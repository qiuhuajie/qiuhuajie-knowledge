---
title: "工作流的 Skill 怎么写？从 7 个顶级 Skill 中提炼的模式与最佳实践"
tags:
  - "人工智能"
  - "人工智能/AI_Studio"
  - "人工智能/AI_Studio/Skills"
  - "Skills"
  - "Skill_Design"
  - "Workflow"
  - "Prompt_Engineering"
updated: 2026-04-16
author: 陈润青（青斧）
date: 2026-04-07
aliases:
  - 工作流的 Skill 怎么写？从 7 个顶级 Skill 中提炼的模式与最佳实践
  - 工作流的 Skill 怎么写 - ATA
  - Skill 怎么写
source_name: ATA / 阿里云基础设施
---
# 工作流的 Skill 怎么写？从 7 个顶级 Skill 中提炼的模式与最佳实践
> [!info] 原文信息
> 作者：陈润青（青斧）
> 来源：ATA / 阿里云基础设施
> 发表：2026-04-07
> 更新：2026-04-11（原页面显示“4月11日更新”，此处按当前归档时间推定年份）
> 说明：本整理稿保留了原文中的模式拆解、模板、链接和对比表，移除了网页 chrome、活动入口、文末重复目录和推广残留，并将 HTML 表格整理为 Markdown 表格。
> [!abstract] 核心摘要
> 这篇文章最有价值的地方，不是再解释一遍 Skill 是什么，而是把 7 个高质量生产级 Skill 拆成可复用的设计模式：线性流程、决策树、循环迭代、跨 Session 接力棒、多阶段编排，以及更偏“控制思维质量”的思维框架。
> 真正决定 Skill 好不好用的，不只是正文写得多细，而是 frontmatter 的触发描述、主文件的信息密度、按需加载的 references，以及是否提前堵住 LLM 偷懒、误判和越界的路径。
> 如果把 Skill 当作“工作流压缩包”，那这篇文章给出的其实是一套写作和架构方法论：先决定模式，再设计触发条件、执行协议、验证机制和安全边界。

## 我的整理
### 一句话结论

写 Skill 的关键，不是把 SOP 原样贴进去，而是把它压缩成“能被模型正确触发、能稳定执行、能按需扩展”的指令系统。

### 全文主线
1. 先解释 Skill 的本质和目录结构，明确 frontmatter 为什么决定触发率。
2. 再从 7 个顶级 Skill 中归纳 5 种核心模式和 1 种特殊模式。
3. 然后总结一套通用写作技巧，包括防偷懒、教学习惯、安全边界和知识分层。
4. 最后给出模式选择决策树、最小模板和参考资源，方便直接落地。

### 最值得记住的判断
- `description` 不是摘要，而是 Skill 的路由规则；写不好，Skill 要么不触发，要么乱触发。
- 好的 Skill 不等于“内容越多越好”，真正有效的是前台短而密、后台按需展开的三层结构。
- 不同类型的工作流必须用不同结构表达，线性流程、循环、长周期协作和深度分析，不应混用同一种模板。
- 大模型最大的执行风险不是“不会做”，而是偷懒、跳步、自我合理化和越界，因此要显式设计借口反驳、量化阈值、负面指令和人工兜底。

---
## 正文整理

以下正文以原文内容和结构为主，仅做排版整理。

> 本文基于对 7 个来自 OpenAI、Google Labs、obra、Trail of Bits、Dean Peters 等团队的生产级 Skill 的逐行分析，提炼出可复用的设计模式、写作技巧和反面教训。

作者在开头补充提到，这篇文章热度比预期更高，说明很多人把自己的工作流或 SOP 写成 Skill 时，普遍会遇到两个问题：

- 不知道应该怎么组织 Skill。
- 写完后运行效果不符合预期。

## 一、Skill 是什么

Skill 是一个文件夹，核心是 `SKILL.md` 文件，采用 YAML frontmatter + Markdown 正文 的格式。当 LLM 判断需要某个 Skill 时，会调用 `skill` 工具加载它，`SKILL.md` 的全部内容会作为 tool result 注入到对话上下文中，模型读到后再自主决定怎么执行。

标准目录一般长这样：

```text
my-skill/
├── SKILL.md      # 主文件（必须）
├── scripts/      # 可执行脚本（可选）
├── references/   # 详细参考文档（可选，按需加载）
├── resources/    # 模板、清单等资源（可选）
└── examples/     # 示例（可选）
```

关键机制在于：Skill 的本质是“知识注入”，它不会动态生成新工具，而是把指令文本注入到模型上下文中，再由模型去调用已有工具，例如 `bash`、`read`、`edit` 等。

## 二、Frontmatter：决定 Skill 是否被加载的门面
### 2.1 必填字段

最核心的两个字段如下：

| 字段 | 作用 | 示例 |
| --- | --- | --- |
| `name` | 唯一标识符，小写连字符 | `test-driven-development` |
| `description` | 最关键，LLM 通过它决定是否加载 | 见下方对比 |

### 2.2 Description 的写法决定加载率

好的 `description` 要包含触发短语、产品关键词以及触发时机。原文给了几个典型对比：

```yaml
# 好的 description：包含触发短语和关键词
description: Deploy applications and websites to Vercel. Use when the user
requests deployment actions like "deploy my app", "push this live",
or "create a preview deployment".
# 好的 description：定义时序位置
description: Use when implementing any feature or bugfix, before writing
implementation code
# 差的 description：太模糊
description: Helps with deployment stuff
```

作者总结的核心原则是：

- 列举触发短语：把用户可能说的话直接写进去。
- 定义时序位置：说明应该在什么之前或之后使用。
- 包含产品关键词：如果覆盖大平台，把关键产品名也写进去。

### 2.3 可选扩展字段

从 7 个 Skill 中还能看到一些常见扩展字段：

| 字段 | 来源 | 作用 |
| --- | --- | --- |
| `references` | OpenCode `cloudflare` | 声明最重要的参考文档 |
| `allowed-tools` | Google Labs `stitch-loop` | 声明需要的工具权限 |
| `type` | Dean Peters `discovery-process` | 声明 Skill 类型，如 `workflow` / `component` |
| `best_for` | Dean Peters `discovery-process` | 最适合的场景列表 |
| `scenarios` | Dean Peters `discovery-process` | 具体触发场景示例 |
| `estimated_time` | Dean Peters `discovery-process` | 预估执行时间 |

## 三、5 种核心设计模式
### 模式 1：线性流程

适用场景：部署、安装、迁移等有明确步骤的操作。

代表：[`openai/skills` 的 `vercel-deploy`](https://github.com/openai/skills/tree/main/skills/.curated/vercel-deploy)（77 行）

典型结构：

- `Prerequisites`：前置条件
- `Quick Start`：主流程，按 Step 1 -> Step 2 -> Step 3 展开
- `Fallback`：降级方案
- `Troubleshooting`：故障排除

关键技巧如下：

| 技巧 | 示例 | 为什么有效 |
| --- | --- | --- |
| 安全默认值 | `Always deploy as preview, not production` | 防止模型做危险操作 |
| 具体命令 | 每步给出可直接执行的 bash 命令 | 模型不需要猜测 |
| 超时提示 | `Use a 10 minute (600000ms) timeout` | 防止超时中断 |
| 降级方案 | CLI 失败时提供 Fallback 脚本 | 给出 B 计划 |
| 负面指令 | `Do not curl the deployed URL to verify` | 明确禁止不该做的事 |

适用判断：如果你的 Skill 可以用“先做 A，再做 B，最后做 C”来描述，就优先用线性模式。

### 模式 2：决策树 + 按需加载

适用场景：大型平台选型、产品导航、问题诊断。

代表：[`openai/skills` 的 `cloudflare-deploy`](https://github.com/openai/skills/tree/main/skills/.curated/cloudflare-deploy)（224 行）

典型结构：

- `Authentication`：认证前置
- `Quick Decision Trees`：快速决策树
- 按用户意图分类，例如 `I need to run code`、`I need to store data`、`I need AI/ML`
- `Product Index`：产品索引表

关键技巧如下：

| 技巧 | 示例 | 为什么有效 |
| --- | --- | --- |
| 用户意图分类 | `I need to run code`，而不是 `Compute products` | 用用户语言而不是技术术语 |
| 树形导航 | `├─ 边缘无服务器函数 -> workers/` | 帮模型快速定位正确产品 |
| 渐进式披露 | 主文件 7KB，references 按需展开到几十万字 | 不浪费上下文窗口 |
| 产品索引表 | `Product -> Reference` 的映射表 | 便于结构化查找 |

适用判断：如果你的 Skill 覆盖的知识域有 10 个以上分支，而且每个分支都有大量详细文档，就用决策树模式。

作者还提到一个很实用的进阶做法：同一个知识域可以拆成两个 Skill。

- 导航型：只负责选型。
- 操作型：负责认证、命令、故障排除等具体动作。

### 模式 3：循环迭代

适用场景：TDD、代码审查、设计评审等需要反复执行的流程。

代表：[`obra/superpowers` 的 `test-driven-development`](https://github.com/obra/superpowers/tree/main/skills/test-driven-development)（371 行）

典型结构：

- `The Iron Law`：不可违反的核心原则
- `Red-Green-Refactor`：循环体
- `RED`：写失败的测试
- `Verify RED`：验证它确实失败
- `GREEN`：写最少的代码
- `Verify GREEN`：验证它确实通过
- `REFACTOR`：清理
- `Repeat`：回到 RED
- `Common Rationalizations`：借口反驳表
- `Verification Checklist`：退出条件

关键技巧如下：

| 技巧 | 示例 | 为什么有效 |
| --- | --- | --- |
| 强硬语气 | `Delete it. Start over.` | 模型容易“灵活变通”，强语气更能提高遵从率 |
| Good / Bad 对比 | 用 `<Good>` 和 `<Bad>` 标签包裹代码示例 | 对比式教学更直接 |
| 借口反驳表 | 预判 12 种偷懒借口并逐一反驳 | 堵死逃避路径 |
| 验证清单 | 8 项 checklist 作为退出条件 | 确保达标才结束 |
| 人类兜底 | `ask your human partner` | 不确定时交给人 |

适用判断：如果你的 Skill 需要模型反复执行“做 -> 验证 -> 改进”的循环，就用迭代模式。

### 模式 4：接力棒循环（跨 Session 持久化）

适用场景：多次迭代的长期项目，需要跨多个 session 持续工作。

代表：[`google-labs-code/stitch-skills` 的 `stitch-loop`](https://github.com/google-labs-code/stitch-skills/tree/main/skills/stitch-loop)（203 行）

典型结构：

- `Overview`：接力棒模式概述
- `The Baton System`：接力棒文件规范
- `Execution Protocol`：6 步执行协议
- `Step 1: Read the Baton`
- `Step 2: Consult Context Files`
- `Step 3: Generate`
- `Step 4: Integrate`
- `Step 5: Update Documentation`
- `Step 6: Prepare the Next Baton`
- `File Structure Reference`
- `Orchestration Options`

关键技巧如下：

| 技巧 | 示例 | 为什么有效 |
| --- | --- | --- |
| 文件即状态 | `next-prompt.md` 作为接力棒 | 不需要模型记住“上次做到哪了” |
| 续命机制 | Step 6 标记为 `Critical` + `MUST` | 忘了写接力棒，循环就断了 |
| 文件协议 | 每个文件有明确职责 | 模型只需按协议读写 |
| 编排无关 | CI/CD、人在回路、Agent 链都能驱动 | 同一个 Skill 适配多种自动化环境 |

适用判断：如果你的 Skill 需要跨多个 session 持续推进，或者需要多个 Agent 协作，就用接力棒模式。

作者还专门对比了它与循环迭代模式的区别：

| 维度 | 循环迭代（TDD） | 接力棒循环（Stitch Loop） |
| --- | --- | --- |
| 状态存储 | LLM 对话上下文 | 外部文件系统 |
| 跨 session | ❌ | ✅ |
| 循环退出 | Checklist 全部打勾 | 路线图清空 |
| 适用时长 | 单次会话（分钟到小时） | 长期项目（天到周） |

### 模式 5：多阶段 + 检查点 + Skill 编排

适用场景：复杂的多周流程，需要在关键节点做 Go / No-Go 决策。

代表：[`deanpeters/Product-Manager-Skills` 的 `discovery-process`](https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/discovery-process)（502 行）

典型结构：

- `Key Concepts`：核心概念与反模式
- `Phase 1: Frame the Problem`
- `Activities`：需要调用哪些子 Skill
- `Outputs`：阶段产出
- `Decision Point 1`：是否通过检查点，以及时间影响
- `Phase 2-6`：按相同模板推进
- `Complete Workflow`
- `Common Pitfalls`
- `References`

关键技巧如下：

| 技巧 | 示例 | 为什么有效 |
| --- | --- | --- |
| 统一阶段模板 | 每个 Phase 都有 `Activities -> Outputs -> Decision Point` | 帮模型快速理解结构 |
| 决策检查点 | `达到饱和了吗？YES -> 下一阶段，NO -> +1 周` | 防止盲目推进 |
| Skill 编排 | 调度 10+ 个子 Skill 完成各阶段 | 形成编排器模式 |
| 时间影响 | 每个 NO 路径标注 `+2-3 days`、`+1 week` | 让用户感知延迟成本 |
| 交互协议分离 | 引用 `workshop-facilitation` 定义交互方式 | 保持关注点分离 |

适用判断：如果你的 Skill 跨越多天或多周，有明确阶段划分和 Go / No-Go 决策点，就用多阶段模式。

### 特殊模式：思维框架

适用场景：安全审计、代码审查、架构分析等需要深度思考的场景。

代表：[`trailofbits/skills` 的 `audit-context-building`](https://github.com/trailofbits/skills/tree/main/plugins/audit-context-building/skills/audit-context-building)（302 行）

这个模式控制的不是“行为步骤”，而是“思维质量”。

典型结构：

- `Purpose`
- `When to Use / When NOT to Use`
- `Rationalizations`
- `Phase 1: Initial Orientation`
- `Phase 2: Ultra-Granular Function Analysis`
- `Per-Function Checklist`
- `Cross-Function Flow Analysis`
- `Output Requirements`
- `Completeness Checklist`
- `Phase 3: Global System Understanding`
- `Stability Rules`
- `Non-Goals`

关键技巧如下：

| 技巧 | 示例 | 为什么有效 |
| --- | --- | --- |
| 思维工具 | 第一性原理、5 Why、5 How | 给模型的是分析框架，而非具体命令 |
| 量化阈值 | `每个函数最少 3 个不变量、5 个假设` | 强迫分析达到足够深度 |
| 非目标约束 | `不要识别漏洞、不要提出修复` | 克制模型先下结论的冲动 |
| 反幻觉规则 | `Never reshape evidence to fit earlier assumptions` | 防止模型自我欺骗 |
| 子 Agent 指导 | 何时以及如何使用 `function-analyzer` Agent | 便于分而治之 |

适用判断：如果你的 Skill 需要模型进行深度分析，而不是快速执行动作，需要控制的是“怎么想”，就用思维框架模式。

## 四、通用写作技巧
### 4.1 防止 LLM 偷懒的 4 种武器

| 武器 | 原理 | 示例来源 |
| --- | --- | --- |
| 强硬语气 | 模型对命令式语气的遵从率更高 | TDD：`Delete it. Start over.` |
| 借口反驳表 | 预判模型的自我合理化路径并堵死 | TDD 的 12 种借口；审计的 6 种借口 |
| 量化阈值 | 给出硬性的最低标准 | 审计：`最少 3 个不变量、5 个假设` |
| 负面指令 | 明确说“不要做 X” | `vercel-deploy`：`Do not curl the URL` |

### 4.2 教学的 3 种有效方式

| 方式 | 原理 | 示例来源 |
| --- | --- | --- |
| Good / Bad 对比 | 对比学习效果最好 | TDD：`<Good>` vs `<Bad>` 代码示例 |
| 具体命令 | 模型擅长执行明确指令 | `vercel-deploy`：每一步都有 bash 命令 |
| 完整示例 | 直接展示期望输出格式 | 审计：引用 `FUNCTION_MICRO_ANALYSIS_EXAMPLE.md` |

### 4.3 安全与边界的 3 条原则

| 原则 | 做法 | 示例来源 |
| --- | --- | --- |
| 安全默认值 | 默认选择最安全的选项 | `vercel-deploy`：`Always deploy as preview` |
| 权限最小化 | 只在必要时提升权限 | `vercel-deploy`：`Do not escalate the installation check` |
| 人类兜底 | 不确定时交给人 | TDD：`ask your human partner` |

### 4.4 知识组织的 3 层架构

作者把 Skill 的知识组织分成三层：

第 1 层：Frontmatter（约 100 tokens）

- 模型扫描所有 Skill 的 `description`，决定是否加载。

第 2 层：`SKILL.md` 正文（建议小于 5K tokens）

- 存放核心指令、决策树和流程步骤。

第 3 层：`references/` 和 `resources/`（按需加载）

- 存放详细文档、示例和清单，通过 `read` 工具按需读取。

Token 预算参考如下：

| 层级 | Token 预算 | 内容 |
| --- | --- | --- |
| Frontmatter | ~100 tokens | `name` + `description` |
| 主文件 | 2K-5K tokens | 核心指令 |
| 参考文档（单个） | 1K-3K tokens | 按需加载 |
| 总上下文占用 | <10K tokens | 主文件 + 1-2 个参考文档 |

## 五、模式选择决策树

作者给了一个很实用的快速选择树：

- 执行一个有明确步骤的操作 -> 模式 1：线性流程
- 在大量选项中帮用户选择正确方向 -> 模式 2：决策树 + 按需加载
- 在单次会话中反复执行“做 -> 验证 -> 改进” -> 模式 3：循环迭代
- 跨多个 session 持续推进一个长期项目 -> 模式 4：接力棒循环
- 跨越多天或多周，有阶段划分和 Go / No-Go 决策 -> 模式 5：多阶段 + 检查点
- 需要模型进行深度分析，而非快速执行 -> 特殊模式：思维框架

## 六、快速上手模板
### 最小可用 Skill（线性模式）
````markdown
---
name: my-skill
description: [一句话描述做什么 + 什么时候触发]
---
# Skill 名称
[一句话核心原则 + 安全默认值]
## Prerequisites
- [前置条件 1]
- [前置条件 2]

## Steps
### Step 1: [动作]
```bash
[具体命令]
```
### Step 2: [动作]
[具体指令]
### Step 3: [动作]
[具体指令]
## Troubleshooting
| Issue | Solution |
| --- | --- |
| [问题 1] | [解决方案] |
````
### 循环迭代 Skill 模板
````markdown
---
name: my-loop-skill
description: [描述 + 触发时机]
---
# Skill 名称
## Core Principle
[不可违反的铁律]
## The Loop
### Phase A - [动作]
[具体指令]
### Verify A
[验证命令]
### Phase B - [动作]
[具体指令]
### Verify B
[验证命令]
### Repeat
回到 Phase A。
## Rationalizations
| Excuse | Reality |
| --- | --- |
| "[借口 1]" | [反驳] |
## Completion Checklist
- [ ] [条件 1]
- [ ] [条件 2]
````
## 七、参考资源
### 官方规范
- [Agent Skills 开放标准](https://agentskills.io/)
- [anthropics/skills - 官方模板](https://github.com/anthropics/skills/tree/main/template)
- [anthropics/skills - 规范文档](https://github.com/anthropics/skills/tree/main/spec)

### 精选仓库
- [openai/skills](https://github.com/openai/skills) - OpenAI Codex 官方 Skill 目录
- [obra/superpowers](https://github.com/obra/superpowers) - 14 个工作流型 Skill
- [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) - 设计到代码的 Skill
- [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills) - 40+ 产品管理 Skill
- [trailofbits/skills](https://github.com/trailofbits/skills) - 安全审计 Skill
- [openclaw/clawhub](https://github.com/openclaw/clawhub) - Skill 注册中心

### 精选列表
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) - 500+ Skill 索引
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) - 精选列表 + Skill vs MCP 对比

## 八、本文分析的 7 个 Skill 速查表

| # | Skill | 来源 | 模式 | 行数 | 一句话精髓 |
| --- | --- | --- | --- | --- | --- |
| 1 | `vercel-deploy` | OpenAI | 线性 | 77 | 最小但完整的 Skill 模板 |
| 2 | `cloudflare-deploy` | OpenAI | 线性 + 决策树 | 224 | 大平台的渐进式披露 |
| 3 | `cloudflare` | OpenCode | 纯决策树 | 211 | 导航型 vs 操作型的区别 |
| 4 | `test-driven-development` | obra | 循环迭代 | 371 | 堵死 LLM 偷懒的所有退路 |
| 5 | `stitch-loop` | Google Labs | 接力棒循环 | 203 | 文件即状态，跨 session 持久化 |
| 6 | `discovery-process` | Dean Peters | 多阶段 + 检查点 | 502 | 编排器模式，调度 10+ 子 Skill |
| 7 | `audit-context-building` | Trail of Bits | 思维框架 | 302 | 控制 LLM “怎么想”而非“做什么” |
