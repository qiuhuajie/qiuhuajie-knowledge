---
name: my-markdown
description: Personal Obsidian markdown style for qiuhuajie. Load together with obsidian-markdown whenever creating, editing, or rewriting any note in this vault. obsidian-markdown defines valid Obsidian syntax; my-markdown defines the user's preferred layout and has higher priority for formatting decisions.
---

# My Markdown Style

This skill defines qiuhuajie's personal note layout style for Obsidian notes.

Use this skill together with `obsidian-markdown` for every markdown note task in this vault:
- creating a new note
- editing an existing note
- rewriting or polishing a note
- reorganizing note structure
- converting raw material into a formal note

Role split:
- `obsidian-markdown` is the base syntax skill. It defines valid Obsidian Flavored Markdown, such as wikilinks, embeds, callouts, properties, comments, tags, math, and Mermaid.
- `my-markdown` is the personal formatting skill. It defines the user's preferred writing and layout style.
- If there is any formatting conflict, follow `my-markdown` first and keep `obsidian-markdown` as the syntax baseline.

## Priority Rule

1. Always load `obsidian-markdown` when working on Obsidian `.md` files.
2. Always load `my-markdown` when the note is in qiuhuajie's Obsidian vault.
3. On formatting, structure, paragraph layout, numbering, and indentation, `my-markdown` has higher priority.
4. On Obsidian syntax correctness, rely on `obsidian-markdown`.

## Core Style Rules

### 1. Use headings for hierarchy

1. Use `#`, `##`, `###` and deeper headings to organize document structure.
2. Headings should reflect clear topic hierarchy.
3. Do not flatten everything into bullet lists when heading structure is more appropriate.
4. Do not repeat the note filename as a top-level heading. The note title is the filename; the first `#` heading should directly begin the chapter content.
5. Level-1 headings should use Chinese section numbering in the form `# 一、`, `# 二、`, `# 三、` and so on.
6. Level-2 headings should use Arabic numbering with an English period, such as `## 1.`, `## 2.`, `## 3.`.
7. Level-3 headings should inherit the current level-2 section number, such as `### 3.1`, `### 3.2`, `### 3.3` under `## 3.`.
8. Level-4 headings and deeper do not need numbering.
9. Keep heading numbering internally consistent throughout the note.

### 2. Every paragraph must be numbered

1. Every text paragraph under a heading must use markdown list numbering.
2. Allowed paragraph markers:
    1. `1.` `2.` `3.` for ordered progression
    2. `*` for unordered parallel points
3. Do not leave normal body paragraphs unnumbered.
4. Tables are not text paragraphs and do not need numbering of their own.

### 3. How to choose `1.`/`2.` versus `*`

1. If a heading contains only one paragraph, use `*`.
2. If a heading contains multiple paragraphs, decide the relation between them:
    1. Use `1.` `2.` `3.` when the paragraphs are progressive, sequential, causal, or step-by-step.
    2. Use `*` when the paragraphs are parallel, side-by-side, or are simply multiple points in the same category.
3. Within the same local section, numbering style should be internally consistent.

### 4. Restart numbering under each new heading

1. Each new heading level starts numbering again from `1.` when ordered numbering is used.
2. Do not continue numbering across different headings.

### 5. Indentation and sizing for images, indentation for code blocks

1. Images do not need paragraph numbering of their own.
2. Decide image indentation based on whether there is explanatory text immediately above the image.
3. If there is text above the image, indent the entire image by 4 spaces so it visually belongs under that paragraph/list item.
4. If the image stands alone without preceding text, keep it unindented.
5. Set image size to an appropriate width for readability; avoid images that are unnecessarily huge or too small to read.
6. When using Obsidian image sizing, prefer a moderate display width such as `|500`, and adjust up or down based on content density.

### 6. Indentation for code blocks

1. Decide indentation based on whether there is explanatory text immediately above the code block.
2. If there is text above it, indent the entire code block by 4 spaces so it belongs to the paragraph/list context.
3. If there is no text above it, keep the code block unindented.
4. For fenced code blocks, indent not only the code lines, but also the fence lines themselves when indentation is required.

### 7. Table spacing and numbering

1. Tables do not need paragraph numbering of their own.
2. If a sentence or numbered paragraph directly introduces a table, leave exactly one empty line between that text and the table so the table renders correctly.
3. Tables must be written at the left margin with no leading indentation, even when they conceptually belong to a preceding numbered item.
4. Table rows must be continuous with no blank lines between header, separator, and body rows.
5. Use the simple separator style `| --- | --- |`, not `| :--- | :--- |`.
6. Do not use imported empty-header tables such as `|   |   |` followed by a bold header row; put the real column names directly in the first row.
7. If a table appears standalone without preceding explanatory text, keep it unnumbered and unindented.
8. Do not indent table lines with spaces or tabs. Even if the table semantically belongs to a list item, the table itself must start at the left margin.
9. Do not insert blank lines before, inside, or after the table body except the single required blank line between an introducing paragraph and the table.
10. Do not wrap ordinary column names in bold just to simulate a header row. Use plain header cells unless the source explicitly requires emphasis inside a specific cell.
11. When fixing a broken imported table, normalize it into one compact block: one header row, one separator row, then continuous body rows.
12. Preferred table form:

```markdown
| 字段 | 含义 | 说明 |
| --- | --- | --- |
| `load1` | 过去 1 分钟平均负载 | 看当前压力 |
| `load5` | 过去 5 分钟平均负载 | 看短期趋势 |
```

### 8. Preserve existing emphasis and inline code

1. If the original content already contains bold (`** **`) or highlight (`== ==`), preserve it during rewriting.
2. Do not add extra bold, highlight, or other emphasis unless the source content already had it or the user explicitly asked for it.
3. The goal is to preserve the user's emphasis intent, not to decorate the note.
4. When bolding inline code, put bold outside the inline-code backticks: use **`Thread.State`**, not `**Thread.State**`.
5. When fixing imported notes, rewrite malformed bold-code combinations such as `` `**Thread.State**` `` into **`Thread.State`**.
6. Preserve the code text itself while changing only the markdown wrapper order.
7. When a class name, interface name, method name, field name, variable name, constant value, or API identifier is being emphasized, prefer **`identifier`** rather than plain **identifier**.
8. During rewrite, actively scan for malformed identifier emphasis such as:
    1. `**ByteBuffer**`
    2. `` `**ByteBuffer**` ``
    3. mixed broken wrappers like `` `**channel**`** ``
9. Fix these into the normalized form **`ByteBuffer`**, **`channel`**, **`flip()`**, **`SelectionKey`** and similar.

### 9. Do not use Obsidian callouts

1. Do not create Obsidian callouts in this vault. Avoid syntax such as `> [!note]`, `> [!important]`, `> [!warning]`, or any other `> [!type]` form.
2. Use simple markdown blockquotes instead, because nested syntax in Obsidian callouts can render incorrectly.
3. When rewriting an existing note, convert every existing callout into a normal `>` quote block.
4. Preserve the original callout body text exactly. Only remove the callout marker, remove fold markers, and add the emoji prefix; do not summarize, reorder, or rewrite the body text.
5. Convert the callout icon/type into an emoji prefix at the beginning of the first quoted content line.
6. If the callout has a custom title, keep the title text after the emoji on the first quoted line.
7. If the callout has no title, add only the emoji prefix before the first original content line.
8. Remove callout fold markers such as `+` or `-`; simple quotes are not foldable.
9. Use this emoji mapping:
    1. `note`, `info` => `ℹ️`
    2. `tip`, `hint`, `important` => `💡`
    3. `warning`, `caution`, `attention` => `⚠️`
    4. `danger`, `error`, `failure`, `fail`, `missing` => `❌`
    5. `success`, `check`, `done` => `✅`
    6. `question`, `faq`, `help` => `❓`
    7. `bug` => `🐞`
    8. `example` => `🧩`
    9. `quote`, `cite` => `💬`
    10. `todo` => `📌`
    11. `abstract`, `summary`, `tldr` => `📄`
    12. unknown callout types => `💡`
10. If the original callout body contains blank lines, do not preserve those blank lines in the converted blockquote. Delete the empty quoted paragraphs and keep the whole converted quote block compact and continuous.
11. For all multi-line blockquotes in this vault, do not leave empty lines between quoted lines. A quote block should stay visually tight with no quoted blank separator lines.
12. Preferred conversion:

```markdown
> [!warning] 注意
> 不要在 callout 中嵌套复杂的加粗、代码或列表。
```

```markdown
> ⚠️ 注意
> 不要在 callout 中嵌套复杂的加粗、代码或列表。
```

13. Preferred conversion without a title:

```markdown
> [!important]
> 这段内容需要重点看。
```

```markdown
> 💡 这段内容需要重点看。
```

### 10. Concept notes must be organized as systematic explanations, not fragmented Q&A

1. For concept explanation notes, prefer a knowledge-building structure rather than a chat-like Q&A structure.
2. The default organizational order for a concept note should be:
    1. definition
    2. core components or dimensions
    3. key relationships or comparisons
    4. judgment criteria
    5. typical scenarios or examples
    6. commands, indicators, or practical usage when relevant
3. Do not over-fragment concept notes into many micro-headings such as:
    1. "为什么是什么"
    2. "为什么不是那个"
    3. "为什么还要分这个"
    4. repeated "为什么 / 怎么 / 什么时候" style headings
4. For concept notes, prefer topic-based section titles such as:
    1. "Load 是什么"
    2. "Load 1 / 5 / 15"
    3. "Load 和 CPU 的关系"
    4. "怎么判断是否正常"
5. The goal is to let the note read like a normal textbook or technical explanation, not like a temporary interactive answer.
6. If a point can be explained continuously under one heading, do not split it into multiple small question headings just for structure.
7. Use tables when the content is inherently comparative, such as:
    1. field meanings
    2. metric comparisons
    3. scenario differences
    4. threshold judgments
8. When writing explanatory paragraphs, prefer complete and continuous explanation with natural transitions.
9. Do not sacrifice readability for structure. Structure should help the reader follow the main line, not interrupt it.
10. Only use heavily question-driven organization when the note is explicitly:
    1. an FAQ
    2. an interview prep note
    3. a troubleshooting SOP
    4. a user explicitly requested Q&A-style explanation

### 11. Do not add front-loaded meta-summary sections by default

1. Do not automatically prepend note bodies with meta-summary sections such as:
    1. `一、我的整理`
    2. `一句话结论`
    3. `这份手册的使用方式`
    4. `全文主线`
    5. `最值得记住的判断`
2. These sections often make the note feel like an AI-generated summary rather than a normal knowledge note.
3. For ordinary concept notes, technical notes, and long-form explanations, begin directly with the actual subject matter instead of adding a synthetic summary layer first.
4. Default to "enter the topic directly" rather than "wrap the topic in a summary shell first".
5. A normal knowledge note should usually open with the concept itself, for example:
    1. `Load 是什么`
    2. `Load 1 / 5 / 15`
    3. `Load 和 CPU 的关系`
    4. `怎么判断是否正常`
6. Avoid layouts that first manufacture an overview frame and only then begin the real content.
7. If the note needs a summary, fold it naturally into the opening explanation or a later consolidation section instead of adding a generic front-matter-like scaffold.
8. If the note truly needs an overview, express it in a more natural structure such as:
    1. a short opening paragraph
    2. a normal first section like `定义` / `背景` / `核心概念`
    3. a compact blockquote only when it clearly improves usability
9. Only add front-loaded summary sections when:
    1. the user explicitly asks for them
    2. the document is a dedicated summary page
    3. the document is a navigation page or index page
    4. the document is a troubleshooting SOP where a top-level checklist is genuinely useful

## Collaboration Rule with obsidian-markdown

1. Use `obsidian-markdown` for syntax features such as:
    1. `[[wikilinks]]`
    2. `![[embeds]]`
    3. frontmatter / properties
    4. tags, comments, math, Mermaid, footnotes
2. After syntax is valid, apply `my-markdown` to normalize structure and layout.
3. If the note uses Obsidian-specific syntax, keep it valid while still conforming to the personal layout rules here.
4. Do not remove useful Obsidian syntax only for visual simplicity.
5. Although `obsidian-markdown` documents callout syntax, do not use callouts in this vault. Convert callouts to simple blockquotes according to the callout rule above.

## Rewrite Checklist

1. Confirm the note structure uses appropriate heading hierarchy.
2. Confirm the note does not repeat the filename as a top-level heading.
3. Confirm level-1 headings use Chinese section numbering like `一、` `二、` `三、`.
4. Confirm level-2 headings use Arabic numbering like `1.` `2.` `3.`.
5. Confirm level-3 headings inherit the current level-2 number, such as `3.1` `3.2` `3.3`.
6. Confirm level-4 headings and deeper do not use numbering.
7. Confirm every text paragraph is numbered with `1.` `2.` or `*`.
8. Confirm standalone images and tables do not need paragraph numbering of their own.
9. Confirm each heading restarts numbering correctly.
10. Confirm paragraph relations use the right marker type:
    1. progressive => `1.` `2.`
    2. parallel => `*`
11. Confirm images and code blocks are indented correctly based on preceding text.
12. Confirm standalone images remain unindented when there is no preceding text.
13. Confirm image sizes are set to a readable width and adjusted when too large or too small.
14. Confirm tables are left-aligned and not indented as numbered content.
15. Confirm when text directly introduces a table, there is one empty line between the text and the table.
16. Confirm table rows are continuous with no blank lines inside the table.
17. Confirm table separators use `---`, not `:---`, unless the user explicitly asks for column alignment.
18. Confirm imported empty-header tables have been converted to real header rows.
19. Confirm existing bold/highlight is preserved.
20. Confirm bold inline code uses the correct wrapper order, such as **`Thread.State`**, not `**Thread.State**` or `` `**Thread.State**` ``.
21. Confirm emphasized code identifiers have been normalized to **`...`** when they are class names, methods, fields, variables, constant values, or API names.
22. Confirm no Obsidian callout syntax remains, such as `> [!note]` or `> [!warning]`.
23. Confirm any existing callouts have been converted into simple `>` quotes with the corresponding emoji prefix, while preserving the original body text.
24. Confirm any blank lines that originally existed inside a callout were removed during conversion, so the final blockquote stays continuous and does not contain quoted empty lines.
25. Confirm all multi-line blockquotes in the final note are compact and contain no internal blank lines.
26. Confirm any Obsidian syntax remains valid.
27. Confirm formatting follows the user's tightened rewrite style when normalizing full notes:
    1. remove unnecessary blank lines between headings, numbered items, parallel bullets, and immediately attached explanatory blocks, but do not remove the one empty line required before a table introduced by text
    2. keep one empty line between an introducing paragraph and the table that follows it
    3. when a numbered paragraph directly introduces indented `*` subpoints, keep the subpoints attached without empty lines
    4. if a sentence was manually rewritten by the user as the style reference, prefer matching its numbering, indentation, and paragraph compactness across the rest of the note
25. Confirm headings are not followed by stray unnumbered body lines; convert such lines into `* ` or ordered items based on context.
26. For concept explanation notes, confirm the structure is systematic and topic-based rather than fragmented into excessive micro-questions.
27. For concept explanation notes, confirm the note follows a natural explanatory flow such as:
    1. definition
    2. dimensions
    3. relationships
    4. criteria
    5. examples
28. For concept explanation notes, confirm readability was prioritized over mechanical structure.
29. Confirm the note does not automatically start with front-loaded meta-summary sections like `我的整理` / `一句话结论` / `使用方式` unless the user explicitly requested that structure.

## Examples

### Heading numbering style

```markdown
# 一、背景
## 1. 问题定义
### 1.1 现象
#### 扩展说明
```

### Single paragraph under a heading

```markdown
## 背景

* 这是该标题下唯一的一段内容，因此使用 *。
```

### Multiple progressive paragraphs under a heading

```markdown
## 处理流程

1. 首先收集原始信息并判断主题。
2. 然后整理结构并统一标题层级。
3. 最后补充链接、嵌入或其他 Obsidian 语法。
```

### Multiple parallel paragraphs under a heading

```markdown
## 核心特点

* 支持使用 wikilink 组织知识连接。
* 支持将资料整理成长期可维护的笔记。
* 支持按照个人风格统一排版。
```

### Concept note organization

```markdown
# 一、Load Average
## 1. Load 是什么
* Load 表示系统中正在运行、等待运行，或处于不可中断等待状态的任务平均数。

## 2. Load 1 / 5 / 15

| 指标 | 含义 | 用途 |
| --- | --- | --- |
| load1 | 过去 1 分钟平均负载 | 看当前压力 |
| load5 | 过去 5 分钟平均负载 | 看短期趋势 |
| load15 | 过去 15 分钟平均负载 | 看整体基线 |

## 3. Load 和 CPU 的关系
* Load 高不一定等于 CPU 高，因为一部分 IO 等待也会计入 Load。

## 4. 怎么判断是否正常
* 核心标准是把 Load 和 CPU 核数一起看。
```

### Direct subject entry is preferred

Preferred:

```markdown
# 一、Load Average
## 1. Load 是什么
* 先直接进入主题定义。

## 2. Load 1 / 5 / 15
* 再展开核心维度。
```

### Image indentation when there is text above

```markdown
## 示例

1. 下面这张图说明系统结构。
    ![[system-diagram.png|500]]
```

### Standalone image without preceding text

```markdown
## 系统截图

![[system-diagram.png|500]]
```

### Resize oversized image to a moderate width

```markdown
## 界面预览

1. 原图过大时，应主动缩小到合适宽度。
    ![[dashboard.png|500]]
```

### Code block indentation when there is text above

````markdown
## 示例代码

1. 下面是示例代码。
    ```java
    public void test() {
        run();
    }
    ```
````

### Code block without preceding text

````markdown
## 原始代码

```java
public void test() {
    run();
}
```
````

### Table after introducing text

```markdown
## 示例表格

1. 下表总结奖励函数设计。

| 维度 | 权重 | 说明 |
| --- | --- | --- |
| 正确性 | 2.0 | 最终答案是否正确 |
| 格式规范 | 0.5 | 是否满足格式约束 |
```

## Working Principle

1. Think of `obsidian-markdown` as the grammar and syntax rulebook.
2. Think of `my-markdown` as the user's house style guide.
3. For any note in this vault, both should be applied together.
4. For formatting decisions, follow this skill first.
