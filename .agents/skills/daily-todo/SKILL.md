---
name: daily-todo
description: Plan and maintain time-ordered daily todos in this Obsidian vault. Use when the user describes what they need to do today, asks to break work into executable blocks, wants dependency-aware sequencing, asks to create or update a daily note under `日程安排/日记`, or asks to insert a new timed todo into the correct slot of an existing day plan.
---

# Daily Todo

Use this skill to turn a rough "what I need to do today" request into an executable day plan, then write it into the vault's daily note.

## Target Note

- Default note path: `日程安排/日记/YYYY-MM-DD.md`
- Default heading format:

```md
# 2026-04-15

# Day Planner

- [ ] 15:00 - 18:00 【📄文档】通讯知识库生成
```

## Supported Modes

1. Build today's plan from a list of tasks, then write the ordered result into the daily note.
2. Insert an additional timed todo into an existing day plan, then keep the timed checklist sorted by start time.

## Category Rules

1. Prefix every task with `【emoji + 两字】`.
   - Example: `【💬会议】`
   - Example: `【💻开发】`
   - Example: `【🧪提测】`
2. Prefer these standard categories when they fit:
   - `【💬会议】`: 会议, 日会, 周会, 同步, 沟通, 讨论
   - `【💻开发】`: 开发, 编码, 实现, 修复, 重构
   - `【🚀发布】`: 发布, 上线, 灰度, 发版
   - `【🔎调研】`: 调研, 研究, 梳理, 分析, 探索
   - `【🏠生活】`: 吃饭, 通勤, 运动, 理发, 医院, 私人安排
   - `【🔗联调】`: 联调, 对接, 联测
   - `【🧪提测】`: 提测, 测试, 验证, 回归
3. When no standard category fits, summarize a custom two-character label and choose a fitting emoji.
   - Example: `【🎫工单】签证工单整理`
   - Example: `【📝评审】AI出签率预测设计稿评审`
   - Example: `【📄文档】通讯知识库生成`
4. Keep the category abstract and the task title concrete.
   - Good: `【🔎调研】通讯知识库目录梳理`
   - Bad: `【通讯】通讯知识库目录梳理`
5. Do not repeat the category words inside the prefix and the title unless the title needs them for clarity.

## Planning Rules

1. Split only when it improves execution.
   - Split work larger than about 2 hours.
   - Split work with obvious phases such as `调研 -> 方案 -> 开发 -> 联调 -> 验收`.
   - Do not split atomic meetings, short follow-ups, or already-specific tasks.
2. Make each block executable.
   - Each block should end with a visible output such as notes, draft, code, review result, sync, or publish.
3. Infer dependency before scheduling.
   - Common chains:
     - `调研 -> 方案 -> 开发 -> 联调 -> 验收 -> 复盘`
     - `收集/拉数 -> 清洗 -> 分析 -> 结论 -> 同步`
     - `准备 -> 会议/沟通 -> 纪要/行动项`
4. Respect hard constraints.
   - Preserve user-provided start and end times.
   - Treat meetings, release windows, and external sync slots as fixed.
5. Estimate duration conservatively when the user gives no time.
   - `30m`: quick admin, brief follow-up, or tiny fix
   - `60m`: reading, review, short document, or simple sync
   - `90m-120m`: focused research, coding, or writing
   - `120m-180m`: deep work only when the task is clearly large
6. Keep the schedule realistic.
   - Avoid overlaps.
   - Prefer contiguous deep-work blocks over fragmented switching.
   - If the requests do not fit into the available day, say so explicitly instead of hiding the conflict.

## Insert Rules

1. If the user gives an exact time, treat it as fixed unless they explicitly ask to reschedule other work.
2. Keep timed checklist items ordered by `start time -> end time`.
3. Preserve existing completed items and indented detail lines under a task.
4. Keep untimed backlog items after timed items.
5. Deduplicate an exact same timed task when the note already contains it.

## Workflow

1. Resolve the target date. Default to today unless the user says otherwise.
2. Read the existing daily note if it exists.
3. Convert rough requests into a concrete plan:
   - Extract fixed-time items first.
   - Break down only the tasks that need breakdown.
   - Classify every task before writing it into the note.
   - Place dependency predecessors earlier in the day.
   - Fill remaining slots with focused work blocks.
4. Write timed tasks with the helper script in this skill:

```bash
python3 .agents/skills/daily-todo/scripts/upsert_daily_todo.py \
  --vault-root "/Users/qiuhuajie/obsidianSpace/knowledge" \
  --date "2026-04-15" \
  --tasks-json '[{"start":"15:00","end":"18:00","category":"文档","title":"通讯知识库生成"}]'
```

5. For a full-day plan, pass the whole ordered timed list in one call.
6. For a single new timed todo, pass only that one item; the script will insert it into the correct position.
7. Re-read the note after writing and report:
   - what was created or inserted
   - any overlap conflicts detected
   - any assumptions made for durations or sequencing

## Task JSON Shape

Pass an array of objects to `--tasks-json`:

```json
[
  {
    "start": "09:00",
    "end": "10:30",
    "category": "调研",
    "details": [
      "梳理现有资料入口",
      "列出缺失专题"
    ],
    "title": "通讯知识库目录梳理 #work"
  }
]
```

Supported fields:

- `start`: required, `HH:MM`
- `end`: required, `HH:MM`
- `category`: optional but strongly preferred; use a standard category or a custom two-character summary
- `emoji`: optional; override the default emoji for this category
- `title`: required; pass the concrete task title without the `【emoji两字】` prefix when possible
- `details`: optional list of strings, rendered as indented child bullets
- `checked`: optional boolean, default `false`

If `category` is omitted, the script will first try to infer a standard category from the task title. If it still cannot decide, it will fall back to `【🗂️待办】`.

## Decision Standard

- Write directly when the user intent is clear enough to schedule safely.
- Ask a follow-up only when a missing constraint would make the plan misleading, such as two fixed meetings with unknown precedence or an obviously impossible total workload.
