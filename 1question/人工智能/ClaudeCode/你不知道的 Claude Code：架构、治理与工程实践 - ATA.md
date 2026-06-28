---
title: "你不知道的 Claude Code：架构、治理与工程实践"
tags:
  - "人工智能"
  - "人工智能/AI Coding"
  - "人工智能/AI Coding/ClaudeCode"
  - "ClaudeCode"
  - "AI Coding"
  - "堆内存"
updated: 2026-04-16
aliases:
  - Claude Code 架构、治理与工程实践
  - Claude Code 工程治理笔记
author: 汤威（侑夕）
source: ATA 技术社区
status: distilled
---
# 你不知道的 Claude Code：架构、治理与工程实践
> [!abstract]
> 这篇文章真正想讲的，不是 Claude Code 有哪些“炫技功能”，而是如何把它当成一个可治理、可约束、可验证的工程系统来使用。
> 
> 最重要的 5 个结论：
> - 问题常常不在 prompt，而在上下文、工具、约束和验证设计。
> - `CLAUDE.md` 应该是长期契约，不是知识库或团队 wiki。
> - `Skill` 负责“怎么做”，`Hook` 负责“必须这样做”，`Subagent` 负责“隔离着做”。
> - 工具设计的重点不是功能越多越好，而是让模型更少选错。
> - 没有 verifier 的 agent，只是在“自我感觉完成”。

## 文章信息
- 作者：汤威（侑夕）
- 来源：ATA 技术社区
- 原文信息：3 月 12 日发表，3 月 20 日更新
- 主题：Claude Code 的架构、上下文治理、工具设计、Prompt Caching 与工程实践
- 备注：这份笔记是整理版，去掉了网页噪声、站点控件和重复目录，只保留核心观点与可复用片段

## 关联笔记
- [[Claude Code 命令]]
- [[Claude Code 源码深度架构分析 - ATA]]
- [[How We Use Skills]]
- [[Anatomy of the .claude folder]]

## 一页总结

作者建议把 Claude Code 拆成 6 层来看：

| 层 | 作用 | 本质问题 |
| --- | --- | --- |
| `CLAUDE.md` / rules / memory | 长期上下文 | 告诉 Claude“这是什么项目” |
| `Tools` / `MCP` | 动作能力 | 告诉 Claude“能做什么” |
| `Skills` | 按需加载的方法论 | 告诉 Claude“应该怎么做” |
| `Hooks` | 硬约束与审计 | 把不能依赖模型自觉的事收回到确定性流程 |
| `Subagents` | 上下文与权限隔离 | 把重型探索、并行研究和高噪声任务隔离出去 |
| `Verifiers` | 验证闭环 | 判断结果是否可信、可回滚、可审计 |

对应地，排查 Claude Code 问题时可以看 5 个面：

| 面向                     | 核心问题           | 主要载体                                |
| ---------------------- | -------------- | ----------------------------------- |
| `Context surface`      | 什么信息常驻，什么按需加载  | `CLAUDE.md`、rules、memory、skills     |
| `Action surface`       | Claude 到底能做什么  | built-in tools、MCP、plugins          |
| `Control surface`      | 哪些动作必须被限制或记录   | permissions、sandbox、hooks           |
| `Isolation surface`    | 哪些任务需要隔离上下文和权限 | subagents、worktrees、forked sessions |
| `Verification surface` | 怎么知道它真的做对了     | tests、lint、screenshots、logs、CI      |

一句话概括：把 Claude Code 当成一个工程系统，而不是“会写代码的聊天框”。

## 1. 底层运行方式

Claude Code 的核心不是“回答问题”，而是一个代理循环：

```text
收集上下文 -> 采取行动 -> 验证结果 -> [完成 or 回到收集]
     ^                          |
  CLAUDE.md / Skills / Memory   Hooks / 权限 / 沙箱
```

作者的体感非常重要：

- 真正卡住的地方，常常不是模型不够聪明，而是上下文错了。
- 很多输出质量问题，不是 prompt 写得不好，而是系统没有告诉模型“怎么判断自己做对了”。
- 长会话失真，往往不是模型退化，而是上下文被工具输出和中间产物污染了。

## 2. 概念边界

文章特别强调不要把几个概念混在一起用。

| 概念 | 运行时角色 | 解决什么问题 | 常见误用 |
| --- | --- | --- | --- |
| `CLAUDE.md` | 项目级持久契约 | 每次会话都必须成立的约束与边界 | 写成团队知识库 |
| `.claude/rules/*` | 局部规则 | 路径、语言、目录级差异 | 所有规则都堆在根 `CLAUDE.md` |
| Built-in Tools | 内置能力 | 读文件、改文件、搜索、执行命令 | 把所有集成都塞进 shell |
| `MCP` | 外部能力接入协议 | 接 GitHub、Sentry、数据库等系统 | 接太多 server 导致 schema 挤爆上下文 |
| `Plugin` | 打包分发层 | 把 Skills / Hooks / MCP 组合分发 | 把 plugin 当成运行时 primitive |
| `Skill` | 按需加载的工作流 | 给 Claude 一套方法包 | 又想当百科，又想当脚本中心 |
| `Hook` | 生命周期拦截层 | 强制执行规则与审计 | 试图用 hook 替代所有模型判断 |
| `Subagent` | 独立工作单元 | 隔离上下文、权限和任务 | 没边界地 fan-out，最后无法治理 |

一个很实用的判断法：

- 给 Claude 新动作能力：用 Tool / MCP
- 给 Claude 一套做事方法：用 Skill
- 需要隔离环境和上下文：用 Subagent
- 需要强制约束或审计：用 Hook
- 需要跨项目复用和分发：用 Plugin

## 3. 上下文工程是第一优先级

这篇文章的核心观点之一：上下文问题往往不是“不够长”，而是“太吵了”。

### 3.1 上下文成本由什么构成

作者给出了一个非常有启发的拆分：

```text
200K 总上下文
├── 固定开销 (~15-20K)
│   ├── 系统指令
│   ├── Skills 描述符
│   ├── MCP Server 工具定义
│   └── LSP 状态
├── 半固定 (~5-10K)
│   ├── CLAUDE.md
│   └── Memory
└── 动态可用 (~160-180K)
    ├── 对话历史
    ├── 文件内容
    └── 工具调用结果
```

作者特别提醒：

- 真正的隐形杀手常常是 `MCP` 的工具 schema。
- 一个大型 MCP Server 可能就吃掉几千 tokens。
- 接了多个 server 之后，还没开始读代码，就已经先损失了一大块上下文。

### 3.2 推荐的上下文分层
```text
始终常驻   -> CLAUDE.md：项目契约 / 构建命令 / 禁止事项
按路径加载 -> rules：语言 / 目录 / 文件类型规则
按需加载   -> Skills：工作流 / 领域知识
隔离加载   -> Subagents：大量探索 / 并行研究
不进上下文 -> Hooks：确定性脚本 / 审计 / 阻断
```

这其实是在做一件事：把不同“生命周期”的信息放到对应层次，而不是全部塞给系统 prompt。

### 3.3 上下文治理最佳实践
- 保持 `CLAUDE.md` 短、硬、可执行，优先写命令、约束和架构边界。
- 大型参考文档不要塞进 `SKILL.md` 正文，拆去 supporting files。
- 用 `.claude/rules/` 承担路径和语言差异，不要让根 `CLAUDE.md` 变成大杂烩。
- 长会话里主动看 `/context`，不要等系统自动压缩以后再补救。
- 任务切换用 `/clear`，同任务进入新阶段用 `/compact`。

### 3.4 Tool Output 是第二个隐形杀手

作者特别提醒，除了工具 schema，真正会拖垮长会话的还有大段工具输出：

- `cargo test`
- `git log`
- `find`
- `grep`
- 各种超长日志

模型并不需要“完整看到”这些输出，它需要的通常只有：

- 成功还是失败
- 失败在哪里
- 下一步该怎么修

所以作者很认同 RTK 这类“在输出进入模型前先过滤”的思路。

### 3.5 压缩机制的陷阱

默认压缩策略会优先移除“可重新读取”的内容，但这可能把架构决策和约束理由也一起压扁。

文章给出的建议非常实用：把 `Compact Instructions` 明确写进 `CLAUDE.md`。

```markdown
## Compact Instructions
When compressing, preserve in priority order:
1. Architecture decisions (NEVER summarize)
2. Modified files and their key changes
3. Current verification status (pass/fail)
4. Open TODOs and rollback notes
5. Tool outputs (can delete, keep pass/fail only)
```

另外一种更主动的方法：

- 在开新会话前，让 Claude 先写 `HANDOFF.md`
- 写清当前进度、试过什么、哪些有效、哪些是死路、下一步做什么
- 新会话只读 `HANDOFF.md` 就能继续，不再依赖系统摘要质量

### 3.6 Plan Mode 的工程价值

文章对 Plan Mode 的定位很明确：

- 先探索，不急着改文件
- 先澄清目标和边界，再确认方案
- 把“探索”和“执行”拆开，降低错误假设带来的成本

对复杂重构、迁移、跨模块改动尤其有效。

## 4. Skills 设计：不是模板库，而是按需加载的工作流

作者反复强调，Skill 和“保存的 Prompt”不是一回事。

### 4.1 一个好 Skill 应该具备什么
- 描述要告诉模型“什么时候该用我”
- 有完整步骤、输入、输出和停止条件
- 正文只放导航和核心约束
- 大资料拆到 supporting files
- 有副作用的 Skill 要显式限制自动调用

### 4.2 Claude 为何能“按需加载” Skill

这里的设计关键词是 `progressive disclosure`：

- `SKILL.md` 提供任务语义、边界和执行骨架
- supporting files 提供领域细节
- scripts 负责确定性地收集上下文或证据

也就是先给索引，再拉细节，而不是一次性把百科全书塞进上下文。

### 4.3 Skill 的 3 种典型类型
1. 检查清单型
   适合发布前核对、质量门禁、交付前检查。
2. 工作流型
   适合高风险但步骤标准化的操作，例如配置迁移、数据库迁移、回滚流程。
3. 领域专家型
   适合故障诊断、复杂决策、证据收集和固定判断框架。
### 4.4 Skills 的反模式
- 描述过宽，导致什么任务都可能触发
- 正文过长，把 runbook 全塞进 `SKILL.md`
- 一个 Skill 同时承担 review、deploy、debug、docs、incident
- 有副作用的 Skill 允许模型自动调用

### 4.5 很重要的一点：描述符也在偷上下文

作者提醒每个启用的 Skill 描述符都会常驻，因此：

- 高频 Skill：保留自动调用，但把描述符写短
- 低频 Skill：关闭自动调用，改成手动触发
- 极低频 Skill：干脆不要常驻，转成文档

## 5. 工具设计：怎么让 Claude 少选错

文章这一段很值得反复看，因为它强调的是 agent-friendly API，而不是 human-friendly API。

### 5.1 好工具和坏工具的区别

| 维度 | 好工具 | 坏工具 |
| --- | --- | --- |
| 名称 | `jira_issue_get`、`sentry_errors_search` | `query`、`fetch`、`do_action` |
| 参数 | `issue_key`、`project_id`、`response_format` | `id`、`name`、`target` |
| 返回 | 直接服务下一步决策 | 一堆 UUID、内部字段和噪声 |
| 规模 | 单一目标、边界清晰 | 多动作混杂、副作用不透明 |
| 成本 | 默认输出可控 | 默认输出过大 |
| 错误信息 | 告诉模型如何修正 | 只给 opaque error code |

### 5.2 作者总结的工具设计原则
- 按系统和资源分层命名，例如 `github_pr_*`、`jira_issue_*`
- 对大响应提供 `concise / detailed` 等返回级别
- 错误信息要能教模型修正
- 能用高层任务工具时，不要暴露过多底层碎片工具

### 5.3 一个很关键的经验

有些能力，不该藏在参数里，也不该依赖 Markdown 约定，而应该做成独立工具。

文章举的例子是“向用户提问”：

- 第一版：往 Bash 等现有工具加 `question` 参数，Claude 会直接忽略
- 第二版：要求模型输出特定 Markdown 格式，外层再解析，太脆弱
- 第三版：做成独立 `AskUserQuestion` 工具，调用即暂停，最稳定

这背后的原则是：

- 如果某个动作必须被稳定触发，就给它一个独立而明确的接口
- 不要把关键行为埋在 flag、注释或文本约定里

### 5.4 什么时候不该再加 Tool
- shell 已经能可靠完成
- 需求本质上是静态知识，不是真实交互
- 更像是工作流约束，适合做成 Skill
- schema、描述和返回格式还没验证过能被模型稳定使用

## 6. Hooks：把不能交给模型自觉的事收回到确定性流程

作者对 Hook 的定义很准确：不是“自动脚本”，而是“控制平面”。

适合放到 Hook 的事情：

- 阻止修改受保护文件
- 编辑后自动格式化 / lint / 轻量校验
- 会话开始时注入动态上下文
- 任务完成后通知

不适合放到 Hook 的事情：

- 需要大量上下文的语义判断
- 长时间运行的复杂业务流程
- 需要多步推理和权衡的决策

可复用示例：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "pattern": "*.rs",
        "hooks": [
          {
            "type": "command",
            "command": "cargo check 2>&1 | head -30",
            "statusMessage": "Running cargo check..."
          }
        ]
      }
    ]
  }
}
```

作者很强调两点：

- 越早发现错误，累计节省的时间越可观
- 一定要限制 Hook 输出长度，否则 Hook 反而会污染上下文

### 6.1 三层叠加很重要
- `CLAUDE.md`：声明必须遵守什么
- `Skill`：告诉模型如何执行
- `Hook`：在关键路径上做硬校验

三层一起用，才比较稳。

## 7. Subagents：并行只是表面，隔离才是核心价值

作者认为 Subagent 的最大价值不是并行，而是“隔离”：

- 重型代码探索
- 大量测试输出
- 审查任务
- 背景调研

这些都容易把主线程上下文污染掉。交给 Subagent 做，主线程只接收摘要。

### 7.1 配置时必须显式约束
- `tools` / `disallowedTools`
- `model`
- `maxTurns`
- `isolation: worktree`

作者的经验很实在：

- 探索任务用便宜模型
- 高价值审查用强模型
- 需要动文件时最好隔离文件系统

### 7.2 常见反模式
- 子代理权限和主线程一样宽
- 输出格式不固定，主线程无法消费
- 子任务之间强依赖，却硬拆成多个 agent

## 8. Prompt Caching：Claude Code 的底层经济学

作者认为 Prompt Caching 是理解 Claude Code 内部架构的关键之一。

### 8.1 缓存按前缀匹配

Prompt 顺序大致如下：

```text
1. System Prompt
2. Tool Definitions
3. Chat History
4. 当前用户输入
```

能保持稳定前缀，就能提高缓存命中率；命中率高，成本和延迟都会更友好。

### 8.2 会破坏缓存的行为
- 在系统 Prompt 里塞时间戳
- 非确定性地打乱工具定义顺序
- 会话中途增删工具

作者给的建议：

- 动态信息不要写进系统 Prompt
- 放到后续消息里传递
- 如果一定要切换模型，尽量通过 Subagent 交接，而不是直接在长会话中途切

### 8.3 为什么中途切模型可能更贵

缓存是模型独占的。

也就是说：

- 你在 Opus 上已经积累了大量缓存
- 中途切到 Haiku，反而要从头重建
- 表面看模型更便宜，实际上整体成本不一定更低

### 8.4 Compaction 的工程意义

文章对压缩的描述很形象：

- 上下文快满时，Claude Code 会 fork 一个总结调用
- 用完整对话做摘要
- 用一段压缩摘要替换几十轮历史
- 保留 system 和 tools，再继续工作

这也解释了为什么压缩前最好自己定义 `Compact Instructions`。

## 9. 验证闭环：没有 verifier，就没有工程上的 Agent

这是全文非常关键的一句：

> “Claude 说完成了”没有工程意义，关键是你能不能验证它做对了、做错了怎么回滚、过程是否可审计。

### 9.1 Verifier 的层级
- 最低层：退出码、lint、typecheck、unit test
- 中间层：集成测试、截图对比、contract test、smoke test
- 更高层：生产日志验证、监控指标、人工审查清单

### 9.2 最好把验证写在 Prompt、Skill 和 CLAUDE.md 里
```markdown
## Verification
For backend changes:
- Run `make test` and `make lint`
- For API changes, update contract tests under `tests/contracts/`

For UI changes:
- Capture before/after screenshots if visual

Definition of done:
- All tests pass
- Lint passes
- No TODO left behind unless explicitly tracked
```

作者自己的判断标准也很值得记：

- 如果一个任务你都说不清楚“怎样才算做对了”
- 那它大概率不适合直接丢给 Claude 自主完成

## 10. 高频命令的工程意义

这些命令本质上都在帮助你主动管理上下文，而不是等系统自动救火。

### 10.1 上下文管理
```bash
/context
/clear
/compact
/memory
```
### 10.2 能力与治理
```bash
/mcp
/hooks
/permissions
/sandbox
/model
```
### 10.3 会话连续性与并行
```bash
claude --continue
claude --resume
claude --continue --fork
claude --worktree
claude -p "prompt"
claude -p --output-format json
```
### 10.4 作者特别推荐的几个点
- `/simplify`：改完代码后做快速多维审查
- `/rewind`：沿错误路径探索太久时很好用
- `/btw`：问侧问题而不污染主任务上下文
- `/insight`：反向帮助你改进 `CLAUDE.md`
- 双击 `Esc`：修改上一条输入，减少重复解释

## 11. 如何写一个好的 `CLAUDE.md`

作者对 `CLAUDE.md` 的定位很清楚：

- 它是协作契约
- 不是知识库
- 不是团队文档
- 不是大而全的项目说明书

### 11.1 应该放什么
- 如何 build / test / run
- 关键目录结构与模块边界
- 代码风格和命名约束
- 不明显的环境坑
- NEVER 列表
- Compact Instructions

### 11.2 不该放什么
- 大段背景介绍
- 完整 API 文档
- 空泛原则
- Claude 看仓库就能推断出来的显然信息
- 低频任务知识和大量资料

### 11.3 可复用模板
```markdown
# Project Contract
## Build And Test
- Install: `pnpm install`
- Dev: `pnpm dev`
- Test: `pnpm test`
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`

## Architecture Boundaries
- HTTP handlers live in `src/http/handlers/`
- Domain logic lives in `src/domain/`
- Do not put persistence logic in handlers
- Shared types live in `src/contracts/`

## Coding Conventions
- Prefer pure functions in domain layer
- Do not introduce new global state without explicit justification
- Reuse existing error types from `src/errors/`

## Safety Rails
### NEVER
- Modify `.env`, lockfiles, or CI secrets without explicit approval
- Remove feature flags without searching all call sites
- Commit without running tests

### ALWAYS
- Show diff before committing
- Update CHANGELOG for user-facing changes

## Verification
- Backend changes: `make test` + `make lint`
- API changes: update contract tests under `tests/contracts/`
- UI changes: capture before/after screenshots

## Compact Instructions
Preserve:
1. Architecture decisions
2. Modified files and key changes
3. Current verification status
4. Open risks, TODOs, rollback notes
```
### 11.4 一个很实用的习惯

每次纠正 Claude 的错误后，让它顺手更新自己的 `CLAUDE.md`：

> Update your CLAUDE.md so you don't make that mistake again.

这个习惯的本质，是把一次性纠偏变成长期契约。

## 12. 作者自己的新经验
### 12.1 “环境透明”非常重要

作者在自己做 Rust + Lua 终端工具时发现：

- Claude Code 用的是真实 shell、git、package manager 和本地配置
- 任何一层不透明，模型就只能开始猜
- 一旦开始猜，可靠性就会明显下降

所以一个很好的实践是：

- 提供 `doctor` 命令
- 先收集环境状态、依赖、配置和健康情况
- 再让 Claude 开始干活

### 12.2 混合语言项目特别适合按文件类型挂 Hook

例如：

- 改 `*.rs` 后自动 `cargo check`
- 改 `*.lua` 后自动做语法检查

这样比最后一次性跑全量检查更省时间。

### 12.3 一套比较完整的工程布局
```text
Project/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   ├── skills/
│   ├── agents/
│   └── settings.json
└── docs/
    └── ai/
```

作者主张把不同信息放在对的地方：

- 全局约束进 `CLAUDE.md`
- 路径约束进 `rules`
- 工作流进 `skills`
- 架构细节进文档

## 13. 常见反模式

| 反模式 | 症状 | 修复方向 |
| --- | --- | --- |
| 把 `CLAUDE.md` 当 wiki | 每次都加载大量噪声 | 只保留契约，把资料拆出去 |
| Skill 大杂烩 | 描述无法稳定触发 | 一个 Skill 只做一类事 |
| 工具太多且描述模糊 | 模型频繁选错工具 | 做好 namespacing，合并重叠工具 |
| 没有验证闭环 | 只能“相信模型说完成了” | 给任务绑定 verifier |
| 过度自治 | 多 agent 失控，难止损 | 权限、角色、worktree 最小化 |
| 不切分上下文 | 研究、实现、审查全挤在主线程 | `/clear`、`/compact`、Subagent 分层使用 |
| 自治范围过宽但治理不足 | 工具全开，边界不清 | permissions + sandbox + hooks + subagent |
| 已批准命令长期不清理 | 危险命令残留在白名单 | 定期审查 `.claude/settings.json` |

## 14. 配置健康检查

作者提到一个 `health` skill，可以快速检查：

- `CLAUDE.md`
- `rules`
- `skills`
- `hooks`
- `allowedTools`
- 实际行为模式

安装命令：

```bash
npx skills add hiclaude/health -a claude-code -s health -g -y
```

如果看完文章后想知道自己的配置离“工程化使用 Claude Code”还有多远，跑一次这类健康检查会很值。

## 15. 文章的最终结论

作者把 Claude Code 的使用分成 3 个阶段：

| 阶段 | 关注点 | 效率感知 |
| --- | --- | --- |
| 工具使用者 | 这个功能怎么用 | 有帮助但有限 |
| 流程优化者 | 如何让协作更顺 | 明显提升 |
| 系统设计者 | 如何让 agent 在约束下自主运作 | 质变 |

最值得记住的一句话是：

> 如果你说不清楚“什么叫做完”，那这个任务大概率也不适合直接扔给 Claude 自主完成。

## 我从这篇文章提炼出的行动清单

如果要把文章思想落到自己的项目里，可以先做这几件小事：

1. 把当前项目的 `CLAUDE.md` 缩到只剩“命令、边界、禁令、验证”。
2. 把路径或语言差异拆到 `.claude/rules/`。
3. 把低频、大体量知识从 Skill 正文拆走，只保留导航与流程。
4. 给最关键的编辑路径加 Hook，但严格限制输出长度。
5. 给复杂探索、审查、长测试输出引入 Subagent 隔离。
6. 为每类任务补一个 verifier，不再只听模型口头宣布“完成”。
7. 在长会话里主动用 `/context`、`/clear`、`/compact` 管理上下文。

## 适合反复回看的句子
> 问题常常不在 prompt，而在上下文、能力、约束、隔离和验证的设计。
> Skill 负责方法，Hook 负责强制，Subagent 负责隔离，Verifier 负责兜底。
> Claude Code 不是一个“更聪明的聊天框”，而是一个需要治理的 agent 系统。