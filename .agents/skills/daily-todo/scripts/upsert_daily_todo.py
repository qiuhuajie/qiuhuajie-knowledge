#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TIMED_LINE_RE = re.compile(
    r"^- \[(?P<checked>[ xX])\] "
    r"(?P<start>\d{2}:\d{2}) - (?P<end>\d{2}:\d{2}) "
    r"(?P<title>.+?)\s*$"
)
TOP_LEVEL_HEADING_RE = re.compile(r"^# ")
CATEGORY_PREFIX_RE = re.compile(r"^【[^】]+】\s*")

DEFAULT_CATEGORY_LABEL = "待办"
DEFAULT_CATEGORY_EMOJI = "🗂️"

CATEGORY_PRESETS = (
    {"label": "评审", "emoji": "📝", "keywords": ("评审", "review")},
    {"label": "会议", "emoji": "💬", "keywords": ("会议", "日会", "周会", "例会", "同步", "沟通", "讨论", "站会")},
    {"label": "开发", "emoji": "💻", "keywords": ("开发", "编码", "coding", "实现", "修复", "重构")},
    {"label": "发布", "emoji": "🚀", "keywords": ("发布", "上线", "灰度", "发版")},
    {"label": "调研", "emoji": "🔎", "keywords": ("调研", "研究", "梳理", "分析", "探索")},
    {"label": "生活", "emoji": "🏠", "keywords": ("生活", "吃饭", "午休", "通勤", "运动", "羽毛球", "医院", "理发")},
    {"label": "联调", "emoji": "🔗", "keywords": ("联调", "联测", "对接")},
    {"label": "提测", "emoji": "🧪", "keywords": ("提测", "测试", "验证", "回归")},
    {"label": "工单", "emoji": "🎫", "keywords": ("工单",)},
    {"label": "文档", "emoji": "📄", "keywords": ("文档", "wiki", "知识库", "方案", "纪要")},
)


@dataclass
class TaskBlock:
    lines: list[str]
    start: str
    end: str
    title: str
    start_minutes: int
    end_minutes: int
    order: int


@dataclass
class OtherBlock:
    lines: list[str]
    kind: str
    order: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a daily note if needed and insert timed todos in order."
    )
    parser.add_argument("--vault-root", default=".")
    parser.add_argument("--date", help="Target date in YYYY-MM-DD.")
    parser.add_argument(
        "--note-path",
        help="Exact note path. Relative paths are resolved from --vault-root.",
    )
    parser.add_argument(
        "--tasks-json",
        required=True,
        help="JSON array of task objects or an object with a top-level tasks array.",
    )
    parser.add_argument(
        "--fail-on-conflict",
        action="store_true",
        help="Exit with code 2 when the merged timed tasks overlap.",
    )
    return parser.parse_args()


def normalize_time(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Time must be a string, got {type(value).__name__}")
    value = value.strip()
    match = re.fullmatch(r"(\d{2}):(\d{2})", value)
    if not match:
        raise ValueError(f"Invalid time: {value!r}")
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour > 23 or minute > 59:
        raise ValueError(f"Invalid time: {value!r}")
    return f"{hour:02d}:{minute:02d}"


def to_minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def normalize_title(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Task title must be a string")
    value = value.strip()
    if not value:
        raise ValueError("Task title must not be empty")
    return value


def normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Category and emoji must be strings when provided")
    stripped = value.strip()
    return stripped or None


def strip_category_prefix(title: str) -> str:
    return CATEGORY_PREFIX_RE.sub("", title).strip()


def normalize_category_label(value: str) -> str:
    compact = "".join(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", value))
    if not compact:
        return DEFAULT_CATEGORY_LABEL
    if len(compact) == 1:
        return f"{compact}事"
    return compact[:2]


def infer_preset(text: str) -> dict | None:
    lowered = text.casefold()
    for preset in CATEGORY_PRESETS:
        if any(keyword.casefold() in lowered for keyword in preset["keywords"]):
            return preset
    return None


def format_task_title(title: str, category: str | None, emoji: str | None) -> str:
    normalized_title = normalize_title(title)
    if category is None and emoji is None and CATEGORY_PREFIX_RE.match(normalized_title):
        return normalized_title

    base_title = strip_category_prefix(normalized_title)

    if category is not None:
        preset = infer_preset(category)
        label = normalize_category_label(category)
    else:
        preset = infer_preset(base_title)
        label = preset["label"] if preset else DEFAULT_CATEGORY_LABEL

    resolved_emoji = emoji or (preset["emoji"] if preset else DEFAULT_CATEGORY_EMOJI)
    return f"【{resolved_emoji}{label}】{base_title}"


def parse_task_payload(raw: str) -> list[dict]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for --tasks-json: {exc}") from exc

    if isinstance(payload, dict):
        payload = payload.get("tasks")

    if not isinstance(payload, list):
        raise ValueError("--tasks-json must be a JSON array or an object with a tasks array")

    return payload


def normalize_task(raw: dict, order: int) -> TaskBlock:
    if not isinstance(raw, dict):
        raise ValueError("Each task entry must be an object")

    start = normalize_time(raw.get("start", ""))
    end = normalize_time(raw.get("end", ""))
    start_minutes = to_minutes(start)
    end_minutes = to_minutes(end)
    if end_minutes <= start_minutes:
        raise ValueError(f"Task end must be later than start: {start} - {end}")

    title = format_task_title(
        raw.get("title", ""),
        normalize_optional_text(raw.get("category")),
        normalize_optional_text(raw.get("emoji")),
    )
    details_raw = raw.get("details", [])
    if isinstance(details_raw, str):
        details_raw = [details_raw]
    if not isinstance(details_raw, list):
        raise ValueError("Task details must be a string or a list of strings")

    checked = bool(raw.get("checked", False))
    lines = [f"- [{'x' if checked else ' '}] {start} - {end} {title}"]
    for detail in details_raw:
        if not isinstance(detail, str):
            raise ValueError("Each detail line must be a string")
        stripped = detail.strip()
        if not stripped:
            continue
        if re.match(r"^[-*] ", stripped):
            lines.append(f"\t{stripped}")
        else:
            lines.append(f"\t- {stripped}")

    return TaskBlock(
        lines=lines,
        start=start,
        end=end,
        title=title,
        start_minutes=start_minutes,
        end_minutes=end_minutes,
        order=order,
    )


def block_key(block: TaskBlock) -> tuple[str, str, str]:
    return (block.start, block.end, block.title)


def classify_block(lines: list[str], order: int) -> TaskBlock | OtherBlock:
    match = TIMED_LINE_RE.match(lines[0]) if lines else None
    if not match:
        kind = "untimed" if lines and lines[0].startswith("- ") else "other"
        return OtherBlock(lines=lines, kind=kind, order=order)

    start = normalize_time(match.group("start"))
    end = normalize_time(match.group("end"))
    return TaskBlock(
        lines=lines,
        start=start,
        end=end,
        title=match.group("title").strip(),
        start_minutes=to_minutes(start),
        end_minutes=to_minutes(end),
        order=order,
    )


def parse_day_planner_section(lines: list[str]) -> list[TaskBlock | OtherBlock]:
    blocks: list[TaskBlock | OtherBlock] = []
    index = 0
    order = 0

    while index < len(lines):
        line = lines[index]
        if line.startswith("- "):
            block_lines = [line]
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if next_line.startswith("- ") or TOP_LEVEL_HEADING_RE.match(next_line):
                    break
                if next_line.strip() == "":
                    if index + 1 < len(lines) and (
                        lines[index + 1].startswith(" ")
                        or lines[index + 1].startswith("\t")
                    ):
                        block_lines.append(next_line)
                        index += 1
                        continue
                    break
                if next_line.startswith(" ") or next_line.startswith("\t"):
                    block_lines.append(next_line)
                    index += 1
                    continue
                break
            blocks.append(classify_block(block_lines, order))
            order += 1
            continue

        blocks.append(OtherBlock(lines=[line], kind="other", order=order))
        order += 1
        index += 1

    return blocks


def strip_blank_edges(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and lines[start].strip() == "":
        start += 1
    while end > start and lines[end - 1].strip() == "":
        end -= 1
    return lines[start:end]


def flatten_blocks(blocks: Iterable[TaskBlock | OtherBlock]) -> list[str]:
    lines: list[str] = []
    for block in blocks:
        lines.extend(block.lines)
    return lines


def find_day_planner(lines: list[str]) -> tuple[int | None, int | None]:
    heading_index = None
    section_end = None

    for idx, line in enumerate(lines):
        if line.strip() == "# Day Planner":
            heading_index = idx
            break

    if heading_index is None:
        return None, None

    for idx in range(heading_index + 1, len(lines)):
        if TOP_LEVEL_HEADING_RE.match(lines[idx]) and lines[idx].strip() != "# Day Planner":
            section_end = idx
            break

    if section_end is None:
        section_end = len(lines)

    return heading_index, section_end


def ensure_note_skeleton(note_path: Path, date_text: str | None) -> tuple[list[str], bool]:
    if note_path.exists():
        content = note_path.read_text(encoding="utf-8")
        return content.splitlines(), False

    note_path.parent.mkdir(parents=True, exist_ok=True)
    heading = f"# {date_text}" if date_text else "# Day Planner"
    return [heading, "", "# Day Planner", ""], True


def resolve_note_path(args: argparse.Namespace) -> Path:
    vault_root = Path(args.vault_root).expanduser().resolve()
    if args.note_path:
        note_path = Path(args.note_path).expanduser()
        if not note_path.is_absolute():
            note_path = vault_root / note_path
        return note_path.resolve()

    if not args.date:
        raise ValueError("--date is required when --note-path is not provided")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        raise ValueError("--date must match YYYY-MM-DD")

    return (vault_root / "日程安排" / "日记" / f"{args.date}.md").resolve()


def build_conflicts(tasks: list[TaskBlock]) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    for first, second in zip(tasks, tasks[1:]):
        if first.end_minutes > second.start_minutes:
            conflicts.append(
                {
                    "first": f"{first.start} - {first.end} {first.title}",
                    "second": f"{second.start} - {second.end} {second.title}",
                }
            )
    return conflicts


def main() -> int:
    args = parse_args()

    try:
        note_path = resolve_note_path(args)
        note_lines, created_note = ensure_note_skeleton(note_path, args.date)
        planner_index, planner_end = find_day_planner(note_lines)
        if planner_index is None or planner_end is None:
            if note_lines and note_lines[-1].strip():
                note_lines.append("")
            planner_index = len(note_lines)
            note_lines.extend(["# Day Planner", ""])
            planner_end = len(note_lines)

        existing_section = note_lines[planner_index + 1 : planner_end]
        blocks = parse_day_planner_section(existing_section)

        timed_blocks = [block for block in blocks if isinstance(block, TaskBlock)]
        untimed_blocks = [
            block for block in blocks if isinstance(block, OtherBlock) and block.kind == "untimed"
        ]
        other_blocks = [
            block for block in blocks if isinstance(block, OtherBlock) and block.kind == "other"
        ]

        next_order = len(blocks)
        incoming = [
            normalize_task(raw, next_order + idx)
            for idx, raw in enumerate(parse_task_payload(args.tasks_json))
        ]

        existing_keys = {block_key(block) for block in timed_blocks}
        added = 0
        deduped = 0

        for block in incoming:
            if block_key(block) in existing_keys:
                deduped += 1
                continue
            timed_blocks.append(block)
            existing_keys.add(block_key(block))
            added += 1

        timed_blocks.sort(key=lambda block: (block.start_minutes, block.end_minutes, block.order))
        conflicts = build_conflicts(timed_blocks)

        rebuilt_section: list[str] = []
        rebuilt_section.extend(flatten_blocks(timed_blocks))
        rebuilt_section.extend(flatten_blocks(untimed_blocks))

        other_lines = strip_blank_edges(flatten_blocks(other_blocks))
        if other_lines:
            if rebuilt_section:
                rebuilt_section.append("")
            rebuilt_section.extend(other_lines)

        rebuilt_section = strip_blank_edges(rebuilt_section)

        new_lines = note_lines[: planner_index + 1]
        new_lines.append("")
        new_lines.extend(rebuilt_section)

        suffix = note_lines[planner_end:]
        if suffix:
            if new_lines and new_lines[-1].strip() and suffix[0].strip():
                new_lines.append("")
            new_lines.extend(suffix)

        while len(new_lines) > 1 and new_lines[-1].strip() == "" and new_lines[-2].strip() == "":
            new_lines.pop()

        result = {
            "note_path": str(note_path),
            "created_note": created_note,
            "added_tasks": added,
            "deduped_tasks": deduped,
            "total_timed_tasks": len(timed_blocks),
            "conflicts": conflicts,
        }

        if conflicts and args.fail_on_conflict:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 2

        note_path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
