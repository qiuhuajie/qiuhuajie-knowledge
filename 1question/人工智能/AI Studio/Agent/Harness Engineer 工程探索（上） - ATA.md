---
title: 《Harness Engineer 工程探索》上 - ATA
tags:
  - 人工智能
  - Agent
  - Harness
  - Context Engineering
  - Prompt Engineering
updated: 2026-04-19
author: 张医博
nickname: 韩笠
workId: 139717
department: 云智能集团
date: 2026-04-17
aliases:
  - Harness Engineer 工程探索 上
  - Harness Engineering 工程探索
source_name: ATA
source_url: https://ata.atatech.org/articles/11020621211?utm_source=open&utm_medium=hsf&utm_campaign=_OPEN_AONE
articleId: 11020621211
---
> [!info] 原文信息
> 作者：张医博（韩笠）
> 来源：ATA
> 发表：2026-04-17
> 链接：https://ata.atatech.org/articles/11020621211?utm_source=open&utm_medium=hsf&utm_campaign=_OPEN_AONE
> 说明：本文从 Prompt Engineering、Context Engineering 的演进出发，引出 Harness Engineering 这一更外层的工程围栏概念，并结合 LangChain 等视角拆解长任务 agent 所需的关键能力。
> [!abstract] 核心摘要
> 文章把 Harness Engineering 定位为 Prompt Engineering 与 Context Engineering 的外层套壳：前两者主要解决输入侧问题，而 Harness Engineering 进一步解决 agent 在连续执行过程中如何被约束、纠偏、编排与观测。作者用多个比喻说明，真正难的不是“给模型喂更多信息”，而是让模型在长任务、工具调用、人机协作和多阶段执行中持续做对事。这个视角有助于理解为什么现代 agent 系统越来越像一个带规划、记忆、权限、文件系统、子代理和人工介入机制的操作环境，而不仅仅是一段聪明 prompt。

# 一、我的整理
## 1. 一句话结论
* Harness Engineering 的核心不是继续优化提示词，而是为 agent 提供一套可规划、可观测、可回滚、可纠偏的工程围栏，让模型在长任务中具备稳定执行能力。

## 2. 全文主线
1. 作者先从 Prompt Engineering 和 Context Engineering 的局限谈起，说明仅靠输入侧优化无法覆盖长任务 agent 的全过程问题。
2. 然后提出 Harness Engineering，强调它是一层面向过程控制的工程套壳，用来管理记忆、执行、思考、观察与协作。
3. 最后结合案例和业界定义，拆解 agent harness 所需要的若干能力，并说明 skills、memory 等机制如何作为额外上下文支撑长期运行。

## 3. 最值得记住的判断
* Prompt Engineering 更擅长局部输出约束，但无法独立支撑长任务连续执行。
* Context Engineering 虽然缓解了长上下文与记忆腐化问题，但随着任务演化仍会面临 context 爆炸。
* Skill 是对 context 的一种渐进式高级优化，能按需加载工具说明和流程知识，减少冗余上下文。
* Harness Engineering 关注的是过程控制，而不只是信息注入，因此更接近真正可用的 agent 工程基础设施。
* 当业界说“Agent = Harness + LLM”时，本质上是在强调系统能力往往比模型本身更决定长任务表现。

# 二、关联笔记
* [[深度解析 Claude Code 在 Prompt  Context  Harness 的设计与实践 - ATA]]
* [[深度解析 Hermes Agent 如何实现“自进化”及其 Prompt Context Harness 的设计实践 - ATA]]
* [[你不知道的 Agent：原理、架构与工程实践 - ATA]]
* [[工作流的 Skill 怎么写？从 7 个顶级 Skill 中提炼的模式与最佳实践 - ATA]]

# 三、正文整理
## 1. 从 Prompt Engineering 到 Harness Engineering 的演进
### 1.1 Prompt Engineering 的位置与局限
1. 作者先回到最早的 Prompt Engineering 阶段，指出它的核心做法是通过提示词约束模型输出，让模型更好地理解需求、减少局部生成偏差。
2. 这种方式适合解决“当前这一轮对话如何表达得更准确”的问题，但对长任务连续执行帮助有限。
3. 原因在于，单靠 prompt 很难抵抗窗口有限、远距离记忆腐化和执行链条变长之后的信息衰减。

### 1.2 Context Engineering 的改进与不足
1. 接着文章讨论 Context Engineering，把 RAG、长文压缩、摘要、跨 agent 信息传递等能力都视为上下文工程的一部分。
2. 这类方法的价值在于为模型补充必要背景，缓解长上下文限制，并尽量让模型在需要时拿到更相关的信息。
3. 但作者指出，随着任务不断演进、角色切换和人工干预叠加，系统仍会出现 context 爆炸，因此仅靠上下文管理仍不足以兜住全过程执行。

### 1.3 Skill 是上下文优化，但还不是 Harness
1. 文章专门提到，skill 可以看作 context 的一种高级优化形式，因为它把工具参数、使用说明和流程经验做成按需分层加载的知识单元。
2. 这样可以减少把所有说明一次性塞进上下文造成的冗余和注意力分散。
3. 但 skill 主要还是在优化“给什么信息、什么时候给”，并不能单独解决连续任务过程中“如何约束和驾驭执行过程”的问题。

### 1.4 Harness Engineering 解决的是过程问题
1. 作者把 Harness Engineering 定义为更外层的工程围栏，强调它不只是继续优化输入，而是围绕 agent 执行过程构建约束、纠偏和观察机制。
2. 它要解决的问题包括记忆如何组织、执行如何分段、思考如何被限制、观察如何回流，以及出现偏差时如何介入和修正。
3. 因此，Harness Engineering 比 Prompt 或 Context 更接近“让 agent 真的能跑长任务”的工程底座。

## 2. 为什么 Harness 更像“操作系统级”套壳
1. 文章通过 TAM 打球、客户护航等类比说明，真正难的不是提前告诉模型一些背景，而是让它在真实执行现场具备随机应变、边做边校准和事后复盘的能力。
2. 这类能力一旦展开，就不再只是“输入信息”问题，而会涉及 checklist、数据播报、应急预案、会议纪要核对、过程纠偏和最终交付等一整套编排动作。
3. 也正因为如此，Harness 往往会演化成接近“操作系统级环境”的东西：它提供文件系统、权限、任务列表、工具执行、人类介入和状态存储，让模型在其中被约束地行动。

## 3. 业界视角下的 Harness 能力拆解
1. 文中引用 LangChain 的认知，强调“如果你不是模型，就是 Harness”，并用“Agent = Harness + LLM”概括这种分工。
2. 从这个视角看，一个可用于长任务的 agent harness 至少需要若干能力组合，例如规划、虚拟文件系统、文件权限、任务委派、上下文与 token 管理、代码执行以及 human-in-the-loop。
3. 这些能力并不是可有可无的附属品，而是让 agent 在复杂环境里稳定运行的结构性条件。

## 4. Skills 与 Memory 在 Harness 中的作用
1. 作者进一步指出，除了基础 harness 能力，skills 与 memory 也是长期运行 agent 的重要补充。
2. Skills 负责在特定任务场景下按需提供流程知识、工具用法和工作规范，减少上下文占用并提高复用率。
3. Memory 则帮助系统跨轮次、跨阶段保留关键经验与状态，使 agent 不必在每次执行时都重新学习同一件事。

## 5. 这篇文章带来的启发
1. 对理解现代 agent 系统来说，这篇文章的最大价值在于把“agent 工程”从提示词技巧拉回到系统设计层面。
2. 当一个团队真正想做长任务 agent 时，最应该投资的往往不是继续堆更多 prompt，而是补齐规划、状态、权限、任务管理、记忆和人工介入这些 harness 能力。
3. 从这个角度再看 Claude Code、Hermes Agent 或各类深度 agent 框架，会更容易理解它们为什么都在围绕 todo、memory、skills、subagents、filesystem 和 human-in-the-loop 持续演化。
