#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from collections import defaultdict
from pathlib import Path

import yaml

try:
    from PIL import Image
except Exception:
    Image = None


IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
FRONTMATTER_RE = re.compile(r"^\ufeff?---\n(.*?)\n---\n?", re.S)
OBS_PAT = re.compile(r"!\[\[([^\]]+)\]\]")
MD_PAT = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_ONLY_RE = re.compile(r"^\s*(?:[-*+]\s*)?\[\[[^\]]+\]\]\s*$")
HEADING_RE = re.compile(r"^#+\s*(.+?)\s*$")


class PrettyDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize Obsidian notes without rewriting knowledge content."
    )
    parser.add_argument("--root", required=True, help="Directory containing markdown notes.")
    parser.add_argument(
        "--root-tag",
        help="Top-level tag to use when building hierarchical tags. Defaults to the folder name.",
    )
    parser.add_argument(
        "--mode",
        choices=["all", "notes", "images"],
        default="all",
        help="Process notes, images, or both. Default: all.",
    )
    parser.add_argument(
        "--updated",
        default=dt.date.today().isoformat(),
        help="Value for the updated frontmatter field. Default: today.",
    )
    parser.add_argument(
        "--max-image-width",
        type=int,
        default=800,
        help="Maximum normalized image width. Default: 800.",
    )
    parser.add_argument(
        "--attachments-dir",
        help="Attachment directory. Defaults to <vault>/Attachment.",
    )
    parser.add_argument(
        "--vault-root",
        help="Vault root. Auto-detected when omitted.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing or deleting files.",
    )
    parser.add_argument(
        "--no-delete-link-index",
        action="store_true",
        help="Keep pure-link index notes even if a same-name folder exists.",
    )
    return parser.parse_args()


def detect_vault_root(script_path: Path) -> Path:
    for parent in script_path.resolve().parents:
        if (parent / ".obsidian").exists():
            return parent
        if (parent / ".agents" / "skills").exists():
            return parent
    return script_path.resolve().parents[4]


def normalize_name(value: str) -> str:
    return "".join(
        ch for ch in value if ch.isalnum() or ("\u4e00" <= ch <= "\u9fff")
    ).lower()


def split_frontmatter(text: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text.lstrip("\ufeff")
    return match.group(1), text[match.end() :]


def normalize_tags(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return [str(value)]


def should_delete_note(path: Path, text: str) -> bool:
    _, body = split_frontmatter(text)
    lines = body.splitlines()
    stem_norm = normalize_name(path.stem)
    kept: list[str] = []
    heading_skipped = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if not heading_skipped:
            match = HEADING_RE.match(stripped)
            if match and normalize_name(match.group(1)) == stem_norm:
                heading_skipped = True
                continue
        kept.append(stripped)

    if not kept or not all(LINK_ONLY_RE.match(line) for line in kept):
        return False

    for sibling in path.parent.iterdir():
        if sibling.is_dir() and normalize_name(sibling.name) == stem_norm:
            return True
    return False


def build_frontmatter(
    path: Path,
    root: Path,
    root_tag: str,
    updated: str,
    existing_raw: str | None,
) -> str:
    existing = {}
    if existing_raw is not None:
        try:
            loaded = yaml.safe_load(existing_raw)
            if isinstance(loaded, dict):
                existing = dict(loaded)
        except Exception:
            existing = {}

    rel_parent = path.parent.relative_to(root)
    hierarchical_tags = [root_tag]
    if rel_parent.parts:
        accum = root_tag
        for part in rel_parent.parts:
            accum = f"{accum}/{part}"
            hierarchical_tags.append(accum)

    title = str(existing.get("title") or path.stem)
    existing_tags = normalize_tags(existing.get("tags"))

    merged_tags: list[str] = []
    seen = set()
    for tag in hierarchical_tags + existing_tags:
        if tag not in seen:
            seen.add(tag)
            merged_tags.append(tag)

    merged = {
        "title": title,
        "tags": merged_tags,
        "updated": updated,
    }
    for key, value in existing.items():
        if key in {"title", "tags", "updated"}:
            continue
        merged[key] = value

    def quote_scalar(value: str) -> str:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'

    lines = [
        "---",
        f"title: {quote_scalar(title)}",
        "tags:",
    ]
    for tag in merged_tags:
        lines.append(f"  - {quote_scalar(tag)}")
    lines.append(f"updated: {updated}")

    extras = {
        key: value for key, value in merged.items() if key not in {"title", "tags", "updated"}
    }
    if extras:
        extras_text = yaml.dump(
            extras,
            Dumper=PrettyDumper,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1000,
        ).strip()
        lines.append(extras_text)

    lines.append("---")
    return "\n".join(lines) + "\n\n"


def build_basename_index(attachments_dir: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = defaultdict(list)
    if not attachments_dir.exists():
        return index
    for path in attachments_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMG_EXTS:
            index[path.name].append(path)
    return index


def get_image_width(path: Path, width_cache: dict[Path, int | None]) -> int | None:
    if path in width_cache:
        return width_cache[path]

    width = None
    try:
        if path.suffix.lower() != ".svg" and Image is not None:
            with Image.open(path) as image:
                width = int(image.width)
        elif path.suffix.lower() != ".svg":
            proc = subprocess.run(
                ["sips", "-g", "pixelWidth", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0:
                match = re.search(r"pixelWidth:\s*(\d+)", proc.stdout)
                if match:
                    width = int(match.group(1))
    except Exception:
        width = None

    width_cache[path] = width
    return width


def candidate_score(
    candidate: Path,
    note: Path,
    root: Path,
    vault_root: Path,
    target: str,
    basename: str,
) -> int:
    score = 0
    try:
        rel = candidate.relative_to(vault_root).as_posix()
    except Exception:
        rel = candidate.as_posix()

    target_norm = target.strip().lstrip("./")
    note_rel = note.parent.relative_to(root).as_posix() if note.parent != root else ""
    root_name = root.name

    if target_norm and (rel == target_norm or rel.endswith("/" + target_norm)):
        score += 100
    if note_rel and f"/{root_name}/{note_rel}/" in ("/" + rel):
        score += 50
    elif f"/{root_name}/" in ("/" + rel):
        score += 20
    if "/Attachment/" in ("/" + rel):
        score += 5
    if candidate.name == basename:
        score += 1
    return score


def resolve_local_image(
    note: Path,
    root: Path,
    vault_root: Path,
    attachments_dir: Path,
    basename_index: dict[str, list[Path]],
    target: str,
) -> Path | None:
    target = target.strip()
    if not target or re.match(r"^[a-z]+://", target, re.I):
        return None

    target = target.split("#", 1)[0].strip()
    basename = Path(target).name
    candidates: list[Path] = []

    direct_candidates = [
        note.parent / target,
        root / target,
        vault_root / target,
        attachments_dir / target,
        note.parent / basename,
        root / basename,
        attachments_dir / basename,
    ]
    for candidate in direct_candidates:
        if candidate.exists() and candidate.is_file():
            candidates.append(candidate)

    candidates.extend(basename_index.get(basename, []))

    deduped: list[Path] = []
    seen = set()
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            deduped.append(candidate)

    if not deduped:
        return None

    deduped.sort(
        key=lambda candidate: (
            -candidate_score(candidate, note, root, vault_root, target, basename),
            str(candidate),
        )
    )
    return deduped[0]


def preferred_width(
    note: Path,
    root: Path,
    vault_root: Path,
    attachments_dir: Path,
    basename_index: dict[str, list[Path]],
    width_cache: dict[Path, int | None],
    target: str,
    max_image_width: int,
) -> int:
    image_path = resolve_local_image(
        note=note,
        root=root,
        vault_root=vault_root,
        attachments_dir=attachments_dir,
        basename_index=basename_index,
        target=target,
    )
    if image_path is None:
        return max_image_width

    width = get_image_width(image_path, width_cache)
    if width is None:
        return max_image_width
    return min(width, max_image_width)


def rewrite_obsidian_images(
    text: str,
    note: Path,
    root: Path,
    vault_root: Path,
    attachments_dir: Path,
    basename_index: dict[str, list[Path]],
    width_cache: dict[Path, int | None],
    max_image_width: int,
) -> tuple[str, int]:
    changed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        inner = match.group(1)
        parts = [part.strip() for part in inner.split("|")]
        target = parts[0]
        if len(parts) >= 2 and parts[-1].isdigit():
            return match.group(0)
        width = preferred_width(
            note=note,
            root=root,
            vault_root=vault_root,
            attachments_dir=attachments_dir,
            basename_index=basename_index,
            width_cache=width_cache,
            target=target,
            max_image_width=max_image_width,
        )
        changed += 1
        return f"![[{target}|{width}]]"

    return OBS_PAT.sub(repl, text), changed


def rewrite_markdown_images(
    text: str,
    note: Path,
    root: Path,
    vault_root: Path,
    attachments_dir: Path,
    basename_index: dict[str, list[Path]],
    width_cache: dict[Path, int | None],
    max_image_width: int,
) -> tuple[str, int]:
    changed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        alt = match.group(1)
        target = match.group(2)
        parts = alt.rsplit("|", 1)
        if len(parts) == 2 and parts[1].isdigit():
            return match.group(0)
        width = preferred_width(
            note=note,
            root=root,
            vault_root=vault_root,
            attachments_dir=attachments_dir,
            basename_index=basename_index,
            width_cache=width_cache,
            target=target,
            max_image_width=max_image_width,
        )
        base_alt = parts[0] if len(parts) == 2 else alt
        new_alt = f"{base_alt}|{width}" if base_alt else f"|{width}"
        changed += 1
        return f"![{new_alt}]({target})"

    return MD_PAT.sub(repl, text), changed


def main() -> int:
    args = parse_args()

    script_path = Path(__file__).resolve()
    vault_root = (
        Path(args.vault_root).expanduser().resolve()
        if args.vault_root
        else detect_vault_root(script_path)
    )
    root = Path(args.root).expanduser().resolve()
    attachments_dir = (
        Path(args.attachments_dir).expanduser().resolve()
        if args.attachments_dir
        else (vault_root / "Attachment").resolve()
    )
    root_tag = args.root_tag or root.name

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root directory not found: {root}")

    md_files = sorted(root.rglob("*.md"))
    basename_index = build_basename_index(attachments_dir)
    width_cache: dict[Path, int | None] = {}

    changed_files = 0
    removed_notes = 0
    frontmatter_written = 0
    obsidian_refs_changed = 0
    markdown_refs_changed = 0
    changed_paths: list[str] = []
    removed_paths: list[str] = []

    for path in md_files:
        original = path.read_text(encoding="utf-8")

        if (
            args.mode in {"all", "notes"}
            and not args.no_delete_link_index
            and should_delete_note(path, original)
        ):
            removed_notes += 1
            removed_paths.append(str(path))
            changed_files += 1
            if not args.dry_run:
                path.unlink()
            continue

        current = original

        if args.mode in {"all", "notes"}:
            existing_raw, body = split_frontmatter(current)
            body = body.lstrip("\n")
            current = build_frontmatter(
                path=path,
                root=root,
                root_tag=root_tag,
                updated=args.updated,
                existing_raw=existing_raw,
            ) + body
            frontmatter_written += 1

        if args.mode in {"all", "images"}:
            current, obs_count = rewrite_obsidian_images(
                text=current,
                note=path,
                root=root,
                vault_root=vault_root,
                attachments_dir=attachments_dir,
                basename_index=basename_index,
                width_cache=width_cache,
                max_image_width=args.max_image_width,
            )
            current, md_count = rewrite_markdown_images(
                text=current,
                note=path,
                root=root,
                vault_root=vault_root,
                attachments_dir=attachments_dir,
                basename_index=basename_index,
                width_cache=width_cache,
                max_image_width=args.max_image_width,
            )
            obsidian_refs_changed += obs_count
            markdown_refs_changed += md_count

        if current != original:
            changed_files += 1
            changed_paths.append(str(path))
            if not args.dry_run:
                path.write_text(current, encoding="utf-8")

    print(f"root={root}")
    print(f"mode={args.mode}")
    print(f"dry_run={str(args.dry_run).lower()}")
    print(f"scanned_md={len(md_files)}")
    print(f"changed_files={changed_files}")
    print(f"removed_notes={removed_notes}")
    print(f"frontmatter_written={frontmatter_written}")
    print(f"obsidian_refs_changed={obsidian_refs_changed}")
    print(f"markdown_refs_changed={markdown_refs_changed}")

    for removed in removed_paths[:20]:
        print(f"removed:{removed}")
    for changed in changed_paths[:20]:
        print(f"changed:{changed}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
