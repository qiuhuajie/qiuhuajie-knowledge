> [!引言]
> 1. Skills 已成为 Claude Code 中使用最广泛的扩展点之一。它们灵活、易于创建，且分发简单。
> 2. 但这种灵活性也让人难以判断什么才是最佳实践。什么样的 Skills 值得创建？写好一个 Skill 的秘诀是什么？什么时候该把它们分享给他人？
# 一、什么是 Skills？
1. 我们经常听到的一个误解是，Skills"只是 markdown 文件"，但 Skills 最有趣的地方在于它们不仅仅是文本文件。它们是文件夹，可以包含脚本、资源、数据等，Agent 可以发现、探索和操作这些内容。
2. 在 Claude Code 中，Skills 还拥有[丰富的配置选项](https://code.claude.com/docs/en/skills#frontmatter-reference)，包括注册动态钩子。
3. 我们发现 Claude Code 中一些最有趣的 Skills 正是创造性地利用了这些配置选项和文件夹结构。
# 二、Skills 的类型
1. 在对我们所有的 Skills 进行分类后，我们发现它们可以归类为几个重复出现的类别。<mark style="background: #FFF3A3A6;">最好的 Skills 能干净地归入某一类；而那些令人困惑的则跨越了多个类别。</mark>
	![[IMG-20260322195849664.jpg|671]]
2. 这不是一份详尽的列表，但这是思考你的组织内部是否缺少某些 Skills 的好方法。
## 1. 库和 API 参考

1. <mark style="background: #FFF3A3A6;">解释如何正确使用库、CLI 或 SDK 的 Skills</mark>。
	1. 这些可以是<u>内部库</u>，也可以是 <u>Claude Code 有时处理不好的常见库</u>。
	2. 这些 Skills 通常包含一个参考代码片段文件夹，以及 Claude 在编写脚本时应避免的坑列表。
2. **示例：**
	- `billing-lib` ：边界情况、易踩的坑等
	- `internal-platform-cli` — 你的内部 CLI 封装的每个子命令，以及使用示例
	- `frontend-design` — 让 Claude 更擅长你的设计系统

## 2. 产品验证

1. <mark style="background: #FFF3A3A6;">描述如何测试或验证代码是否正常工作的 Skills</mark>。
	1. 这些通常与外部工具（如 playwright、tmux 等）配合使用进行验证。
	2. 验证 Skills 对于确保 Claude 的输出正确非常有用。让一位工程师花一周时间把验证 Skills 做得非常出色是值得的。
2. 可以考虑一些技巧：这些通常通过在 Skill 中包含各种脚本来实现。
	* 比如让 Claude 录制其输出的视频，这样你就能确切看到它测试了什么
	* 或者在每一步对状态进行程序化断言。
3. **示例：**
	- `signup-flow-driver` — 在无头浏览器中运行注册 → 邮件验证 → 引导流程，并在每一步提供断言状态的钩子
	- `checkout-verifier` — 使用 Stripe 测试卡驱动结账 UI，验证发票是否确实到达正确的状态
	- `tmux-cli-driver` — 用于交互式 CLI 测试，当你验证的东西需要 TTY 时

## 3. 数据获取与分析

1. <mark style="background: #FFF3A3A6;">连接到你的数据和监控栈的 Skills</mark>。这些 Skills 可能包含带有凭证的库来获取数据、特定的仪表板 ID 等，以及常见工作流或获取数据的方法说明。
2. **示例：**
	- `funnel-query` — "我需要关联哪些事件才能看到注册 → 激活 → 付费"，以及真正包含规范 user_id 的表
	- `cohort-compare` — 比较两个群组的留存率或转化率，标记统计上显著的差异，链接到分群定义
	- `grafana` — 数据源 UID、集群名称、问题 → 仪表板查找表

## 4. 业务流程与团队自动化

1. <mark style="background: #FFF3A3A6;">将重复性工作流自动化为一个命令的 Skills</mark>。
	1. 这些 Skills 通常相当简单，但可能依赖于其他 Skills 或 MCP。
	2. 对于这些 Skills，<u>将之前的结果保存在日志文件中可以帮助模型保持一致</u>，并反思工作流的先前执行情况。
2. **示例：**
	- `standup-post` — 聚合你的工单追踪器、GitHub 活动和之前的 Slack 消息 → 格式化的站会报告，只显示变化
	- `create-<ticket-system>-ticket` — 强制执行模式（有效的枚举值、必填字段）以及创建后的工作流（提醒审核者、在 Slack 中链接）
	- `weekly-recap` — 合并的 PR + 关闭的工单 + 部署 → 格式化的周报

## 5. 代码脚手架（Scaffolding）与模板（Templates）

1. <mark style="background: #FFF3A3A6;">为代码库中的特定功能生成框架样板的 Skills</mark>。
	1. 你可以将这些 Skills 与可组合的脚本结合使用。
	2. 当你的脚手架有无法纯粹用代码覆盖的自然语言需求时，它们特别有用。
2. **示例：**
	- `new-<framework>-workflow` — 用你的注释脚手架一个新的服务/工作流/处理器
	- `new-migration` — 你的迁移文件模板加上常见的坑
	- `create-app` — 新的内部应用，预先配置好你的认证、日志和部署配置

## 6. 代码质量与审查

1. <mark style="background: #FFF3A3A6;">在组织内部强制执行代码质量并帮助审查代码的 Skills</mark>。
	1. 这些可以包括确定性脚本或工具以获得最大的健壮性。
	2. 你可能希望将这些 Skills 作为钩子的一部分自动运行，或在 GitHub Action 中运行。
2. **示例：**
	- `adversarial-review` — 生成一个新的子 Agent 来批评，实施修复，迭代直到发现的问题变成吹毛求疵
	- `code-style` — 强制执行代码风格，特别是 Claude 默认做得不好的风格
	- `testing-practices` — 关于如何编写测试以及测试什么的说明

## 7. CI/CD 与部署

1. <mark style="background: #FFF3A3A6;">帮助你在代码库中获取、推送和部署代码的 Skills</mark>。这些 Skills 可能引用其他 Skills 来收集数据。
2. **示例：**
	- `babysit-pr` — 监控 PR → 重试不稳定的 CI → 解决合并冲突 → 启用自动合并
	- `deploy-<service>` — 构建 → 冒烟测试 → 逐步流量推出并比较错误率 → 检测到回归时自动回滚
	- `cherry-pick-prod` — 隔离的 worktree → cherry-pick → 冲突解决 → 使用模板创建 PR

## 8. 运行手册

1. <mark style="background: #FFF3A3A6;">接收**症状**（如 Slack 线程、警报或错误特征），通过**多工具调查**，并**生成结构化报告**的 Skills</mark>。
2. **示例：**
	- `<service>-debugging` — 为你的高流量服务映射症状 → 工具 → 查询模式
	- `oncall-runner` — 获取警报 → 检查常见问题 → 格式化发现
	- `log-correlator` — 给定一个请求 ID，从可能接触过它的每个系统拉取匹配的日志

## 9. 基础设施运维

1. <mark style="background: #FFF3A3A6;">执行例行维护和操作程序的 Skills</mark>。
	1. 其中一些涉及需要防护措施的危险操作。
	2. 这些使工程师更容易在关键操作中遵循最佳实践。
2. **示例：**
	- `<resource>-orphans` — 查找孤立的 pods/volumes → 发到 Slack → 等待期 → 用户确认 → 级联清理
	- `dependency-management` — 你的组织的依赖审批工作流
	- `cost-investigation` — "为什么我们的存储/出口账单飙升"，包含特定的存储桶和查询模式

# 三、创建 Skills 的技巧

* 一旦你决定要创建什么 Skill，该怎么写呢？以下是我们发现的一些最佳实践、技巧和窍门。
	![[IMG-20260404032004373.jpg|704]]
2. Claude Code 还最近发布了 [Skill Creator](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)，让在 Claude Code 中创建 Skills 变得更加容易。

## 1. 不要陈述显而易见的内容

1. Claude Code 对你的代码库了解很多，而 Claude 对编码也了解很多，包括许多默认偏好。
2. <mark style="background: #FFF3A3A6;">如果你发布的是一个主要关于知识的 Skill，尽量专注于能推动 Claude 跳出常规思维模式的信息</mark>。
3. [frontend design skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) 是一个很好的例子 — 它是由 Anthropic 的一位工程师构建的，通过与客户迭代来改善 Claude 的设计品味，避免像 Inter 字体和紫色渐变这样的经典模式。

## 2. 构建"易错点"部分

* 任何 Skill 中<mark style="background: #FFF3A3A6;">信号最强的内容是"易错点"（Gotchas）部分</mark>。
	1. 这些部分应该从 Claude 使用你的 Skill 时遇到的常见失败点构建。
	2. 理想情况下，你会随着时间的推移更新你的 Skill 来捕获这些易错点。
		![[IMG-20260404032004407.jpg|692]]

## 3. 使用文件系统和渐进式披露

![[IMG-20260404032004522.jpg]]

正如我们之前所说，Skill 是一个文件夹，不仅仅是 markdown 文件。你应该把整个文件系统视为上下文工程和渐进式披露的一种形式。告诉 Claude 你的 Skill 中有哪些文件，它会在适当的时候阅读它们。

最简单的渐进式披露形式是指向其他 markdown 文件供 Claude 使用。例如，你可能会将详细的函数签名和使用示例拆分到 references/api.md 中。

另一个例子：如果你的最终输出是一个 markdown 文件，你可能会在 assets/ 中包含一个模板文件供复制和使用。

你可以有参考、脚本、示例等文件夹，这些都能帮助 Claude 更有效地工作。

## 避免"轨道化"限制 Claude

Claude 通常会尝试遵循你的指令，而由于 Skills 如此可重用，你需要小心在指令中过于具体。给 Claude 它需要的信息，但给它适应情况的灵活性。例如：

![[IMG-20260404032004584.jpg]]

## 仔细考虑设置

![[IMG-20260404032004618.jpg]]

一些 Skills 可能需要用户提供上下文来设置。例如，如果你正在创建一个将站会发布到 Slack 的 Skill，你可能希望 Claude 询问要发布到哪个 Slack 频道。

做这件事的一个好模式是将这些设置信息存储在 Skill 目录中的 config.json 文件中，如上面的示例。如果配置没有设置，Agent 可以向用户询问信息。

如果你希望 Agent 提出结构化的多选问题，你可以指示 Claude 使用 AskUserQuestion 工具。

## Description 字段是给模型看的

当 Claude Code 启动会话时，它会构建所有可用 Skill 及其描述的列表。这个列表是 Claude 扫描以决定"是否有适合这个请求的 Skill？"的内容。这意味着 description 字段不是摘要 — 它是描述何时触发这个 Skill 的说明。

![[IMG-20260404032004670.jpg]]

## 内存与数据存储

![[IMG-20260405214031446.jpg]]

一些 Skills 可以通过在其中存储数据来包含某种形式的内存。你可以将数据存储在简单的仅追加文本日志文件或 JSON 文件中，也可以存储在复杂的 SQLite 数据库中。

例如，standup-post Skill 可能会保留一个 standups.log，记录它写的每篇帖子，这意味着下次运行时，Claude 会读取自己的历史记录，可以知道自昨天以来发生了什么变化。

存储在 Skill 目录中的数据可能会在你升级 Skill 时被删除，所以你应该将其存储在稳定的文件夹中，截至今天我们提供 `${**CLAUDE_PLUGIN_DATA**}` 作为每个插件的稳定文件夹来存储数据。

## 存储脚本与生成代码

你能给 Claude 的最强大的工具之一是代码。给 Claude 脚本和库让 Claude 把它的轮次花在组合上，决定下一步做什么，而不是重构样板代码。

例如，在你的数据科学 Skill 中，你可能有一个函数库来从事件源获取数据。为了让 Claude 进行复杂分析，你可以给它一组辅助函数，如下所示：

![[IMG-20260405214031466.jpg]]

然后 Claude 可以动态生成脚本来组合这些功能，为"周二发生了什么？"这样的提示做更高级的分析。

![[IMG-20260405214031604.jpg]]

## 按需钩子

Skills 可以包含仅在调用 Skill 时激活并持续到会话结束的钩子。用于那些你不想一直运行但有时极其有用的更有主见的钩子。

例如：

- /**careful** — 通过 PreToolUse 匹配 Bash 来阻止 rm -rf、DROP TABLE、force-push、kubectl delete。只有当你知道你在操作生产环境时才需要这个 — 一直开着会让你发疯
- /**freeze** — 阻止任何不在特定目录中的 Edit/Write。在调试时很有用："我想添加日志，但我一直不小心'修复'不相关的东西"

# 分发 Skills

Skills 最大的好处之一是你可以与团队其他成员分享它们。

有两种方式可以与他人分享 Skills：

- 将你的 Skills 提交到仓库（在 ./.claude/skills 下）
- 制作一个 **插件** 并拥有一个 Claude Code 插件市场，用户可以在其中上传和安装插件（在[文档](https://code.claude.com/docs/en/plugin-marketplaces)中了解更多）

对于在相对较少的仓库中工作的较小团队，将 Skills 提交到仓库效果很好。但是每个被提交的 Skill 也会稍微增加模型的上下文。随着规模扩大，内部插件市场允许你分发 Skills 并让你的团队决定安装哪些。

## 管理市场

你如何决定哪些 Skills 进入市场？人们如何提交它们？

我们没有 centralized 团队来做决定；相反，我们尝试有机地找到最有用的 Skills。如果你有一个想让人们试用的 Skill，你可以把它上传到 GitHub 中的沙盒文件夹，并在 Slack 或其他论坛中向人们指出它。

一旦一个 Skill 获得了关注（由 Skill 所有者决定），他们可以提交 PR 将其移入市场。

值得注意的是，创建糟糕或冗余的 Skills 可能很容易，所以确保在发布前有一些筛选方法很重要。

## 组合 Skills

你可能希望有相互依赖的 Skills。例如，你可能有一个上传文件的文件上传 Skill，和一个生成 CSV 并上传的 CSV 生成 Skill。这种依赖管理目前还没有原生内置到市场或 Skills 中，但你可以通过名称引用其他 Skills，如果它们被安装，模型就会调用它们。

## 衡量 Skills

要了解一个 Skill 的表现，我们使用 PreToolUse 钩子，让我们在公司内部记录 Skill 使用情况（[示例代码在这里](https://gist.github.com/ThariqS/24defad423d701746e23dc19aace4de5)）。这意味着我们可以找到受欢迎的或与我们预期相比触发不足的 Skills。

# 结语

Skills 是 Agents 极其强大、灵活的工具，但仍处于早期阶段，我们都在摸索如何最好地使用它们。

把这更多地看作是我们发现有用的技巧集合，而不是确定的指南。理解 Skills 的最好方法是开始使用、实验，看看什么对你有效。我们大多数的 Skills 最初只有几行和一个易错点，然后变得更好是因为人们在 Claude 遇到新的边界情况时不断添加内容。

希望这对你有帮助，如果有任何问题请告诉我。