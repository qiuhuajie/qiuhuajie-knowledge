# 关于 CLAUDE.md、自定义命令、技能、代理和权限的完整指南，以及如何正确配置它们

1. 大多数 Claude Code 用户把 **.claude 文件夹**当作一个黑箱。他们知道它的存在，看到过它出现在项目根目录中。但他们从未打开过它，更不用说理解里面每个文件的作用了。
2. 这是一个错失的机会。
3. **.claude 文件夹是控制 Claude 在项目中行为的中枢。** 它存放着你的指令、自定义命令、权限规则，甚至还有跨会话的 Claude 记忆。一旦你理解了每个文件的用途和位置，你就可以将 Claude Code 配置成完全符合团队需求的方式。
4. 本指南将带你深入了解整个文件夹的结构，从日常使用的文件到一次性设置后就无需再管的配置。

# 两个文件夹，而不是一个

1. 在深入了解之前，有一点值得提前知道：实际上有两个 .claude 目录，而不是一个。
2. 第一个位于项目内部，第二个位于你的主目录：
    ![[IMG-20260405214031444.jpg|500]]

3. **项目级别的文件夹存放团队配置。** 你将其提交到 git。团队中的每个人都遵循相同的规则、相同的自定义命令、相同的权限策略。

4. 全局的 **~/.claude/** 文件夹存放你的个人偏好和机器本地的状态，如会话历史和自动记忆。

# CLAUDE.md：Claude 的使用手册

1. 这是整个系统中最重要的文件。当你启动 Claude Code 会话时，它首先读取的就是 **CLAUDE.md**。它会将其直接加载到系统提示词中，并在整个对话过程中始终记住。

2. 简单来说：**你在 CLAUDE.md 中写什么，Claude 就会遵循什么。**

3. 如果你告诉 Claude 始终在实现之前写测试，它就会这样做。如果你说"不要使用 console.log 来处理错误，要始终使用自定义日志模块"，它每次都会遵守。

4. 项目根目录下的 **CLAUDE.md** 是最常见的配置方式。但你也可以在 **~/.claude/CLAUDE.md** 中放置适用于所有项目的全局偏好设置，甚至可以在子目录中放置一个用于特定文件夹规则的 CLAUDE.md。Claude 会读取所有这些文件并合并它们。

## CLAUDE.md 中真正应该放什么

* 大多数人要么写得太多，要么写得太少。以下是有效的内容。

## 应该写

- 构建、测试和代码检查命令（npm run test、make build 等）
- **关键的架构决策**（"我们使用 Turborepo 构建 monorepo"）
- **不明显的陷阱**（"TypeScript 严格模式已开启，未使用的变量会报错"）
- 导入约定、命名模式、错误处理风格
- 主要模块的文件和文件夹结构

## 不应该写

* 任何属于 linter 或格式化配置的内容
- 你已经可以链接到的完整文档
- 解释理论的长段落

5. 保持 CLAUDE.md 在 200 行以内。超过这个长度的文件会占用太多上下文空间，而且 Claude 对指令的遵循度实际上会下降。

6. 这是一个最小但有效的示例：
	```plaintext
	# 项目：Acme API
	## 命令
	npm run dev          # 启动开发服务器
	npm run test         # 运行测试（Jest）
	npm run lint         # ESLint + Prettier 检查
	npm run build        # 生产构建
	## 架构
	- Express REST API，Node 20
	- 通过 Prisma ORM 连接 PostgreSQL
	- 所有处理器位于 src/handlers/
	- 共享类型位于 src/types/

	## 约定
	- 每个处理器使用 zod 进行请求验证
	- 返回格式始终为 { data, error }
	- 永远不要向客户端暴露堆栈跟踪
	- 使用 logger 模块，不要用 console.log

	## 注意
	- 测试使用真实的本地数据库，不是 mock。先运行 \`npm run db:test:reset\`
	- 严格 TypeScript：不允许未使用的导入
	```

7. 这大约 20 行代码。它让 Claude 获得了在这个代码库中高效工作所需的一切，而无需不断澄清。

# CLAUDE.local.md 用于个人覆盖

1. 有时你有一个只属于你而不属于整个团队的偏好。也许你更喜欢不同的测试运行器，或者你希望 Claude 始终使用特定模式打开文件。

2. 在项目根目录创建 CLAUDE.local.md。Claude 会与主 CLAUDE.md 一起读取它，它会自动被 gitignore��这样你的个人调整永远不会进入代码仓库。

    ![[IMG-20260405214031463.jpg|500]]

# rules/ 文件夹：可扩展的模块化指令

1. CLAUDE.md 在单个项目中效果很好。但一旦团队扩大，你就会得到一份 300 行的 CLAUDE.md，没人维护，也没人理会。

2. rules/ 文件夹解决了这个问题。

3. **.claude/rules/ 中的每个 markdown 文件都会自动与你的 CLAUDE.md 一起加载。** 不是一个大文件，而是按关注点拆分指令：
	```plaintext
	.claude/rules/
	├── code-style.md
	├── testing.md
	├── api-conventions.md
	└── security.md
	```

4. 每个文件保持专注且易于更新。负责 API 约定的团队成员编辑 api-conventions.md。负责测试标准的人编辑 testing.md。每个人不会互相干扰。

5. **真正的强大之处来自于路径作用域规则。** 给规则文件添加 YAML frontmatter 块，它只会在 Claude 处理匹配文件时激活：
	```markdown
	    ---
	    paths:
	      - "src/api/**/*.ts"
	      - "src/handlers/**/*.ts"
	    ---
	    # API 设计规则
	    - 所有处理器返回 { data, error } 格式
	    - 使用 zod 进行请求体验证
	    - 永远不要向客户端暴露内部错误���情
	```

6. 当 Claude 编辑 React 组件时不会加载这个文件。只有在处理 src/api/ 或 src/handlers/ 中的文件时才会加载。没有 paths 字段的规则会无条件加载，每个会话都会加载。

7. 这是当你的 CLAUDE.md 开始变得拥挤时的正确模式。

# commands/ 文件夹：你的自定义斜杠命令

1. 开箱即用，Claude Code 有内置的斜杠命令如 **/help** 和 **/compact**。**commands/** 文件夹让你可以添加自己的命令。

2. **你放入 .claude/commands/ 的每个 markdown 文件都会变成一个斜杠命令。**

3. 名为 **review.md** 的文件创建 **/project:review**。名为 fix-issue.md 的文件创建 **/project:fix-issue**。文件名就是命令名。

![[IMG-20260405214031568.jpg|500]]

4. 这是一个简单的例子。创建 **.claude/commands/review.md**：
```markdown
---
description: 在合并前审查当前分支差异的问题
---
## 需要审查的变更
!\`git diff --name-only main...HEAD\`
## 详细差异
!\`git diff main...HEAD\`
审查上述变更的：
1. 代码质量问题
2. 安全漏洞
3. 缺失的测试覆盖
4. 性能问题

对每个文件给出具体、可操作的反馈。
```

5. 现在在 Claude Code 中运行 **/project:review**，它会自动将真实的 git diff 注入到提示词中，然后 Claude 才会看到。**!** 反引号语法运行 shell 命令并嵌入输出。这就是这些命令真正有用的原因，而不仅仅保存的文本。

## 向命令传递参数

6. 使用 $ARGUMENTS 传递命令名后的文本：
```markdown
---
description: 调查并修复 GitHub issue
argument-hint: [issue-number]
---
查看本仓库中的 issue #$ARGUMENTS。
!\`gh issue view $ARGUMENTS\`
理解这个 bug，追踪到根本原因，修复它，并编写一个能够捕获它的测试。
```

7. 运行 /project:fix-issue 234 会将 issue 234 的内容直接输入到提示词中。

## 个人命令 Vs 项目命令

8. **.claude/commands/** 中的项目命令会被提交并与团队共享。对于你希望在任何地方都能使用的命令，不管项目如何，将它们放在 **~/.claude/commands/** 中。这些会显示为 **/user:命令名** 而不是。

9. 一个有用的个人命令：每日站会助手、按照你的约定生成提交消息的命令，或快速安全扫描。

# skills/ 文件夹：按需使用的可复用工作流

1. 现在你知道了命令是如何工作的。技能表面上看很相似，但触发方式有根本区别。在继续之前先理解这个区别：

  ![[IMG-20260405214107513.jpg|500]]

2. **技能是 Claude 可以自动调用自己的工作流，** 无需你输入斜杠命令，当任务匹配技能的描述时。命令等待你。技能则监视对话并在合适的时机行动。

3. 每个技能位于自己的子目录中，包含一个 SKILL.md 文件：
```markdown
    .claude/skills/
    ├── security-review/
    │   ├── SKILL.md
    │   └── DETAILED_GUIDE.md
    └── deploy/
        ├── SKILL.md
        └── templates/
            └── release-notes.md
```

4. SKILL.md 使用 YAML frontmatter 来描述何时使用它：
```markdown
---
name: security-review
description: 全面的安全审计。在审查代码漏洞、部署前或用户提及安全时使用。
allowed-tools: Read, Grep, Glob
---
分析代码库中的安全漏洞：
1. SQL 注入和 XSS 风险
2. 暴露的凭证或密钥
3. 不安全的配置
4. 认证和授权缺口

用严重等级和具体修复步骤报告发现。
参考 @DETAILED_GUIDE.md 了解我们的安全标准。
```

5. 当你说"审查这个 PR 的安全问题"时，Claude 读取描述，识别到匹配，然后自动调用技能。你也可以用 **/security-review** 显式调用它。

6. **与命令的关键区别：** 技能可以将支持文件打包到旁边。上面 [@DETAILED_GUIDE](https://x.com/@DETAILED_GUIDE).md 的引用会拉取一个与 SKILL.md 相邻的详细文档。命令是单个文件。技能是包。

7. 个人技能放在 **~/.claude/skills/** 中，在所有项目中可用。

# agents/ 文件夹：专业化的子代理角色

1. 当任务足够复杂，需要一个专门的专家时，你可以在 .claude/agents/ 中定义一个子代理角色。每个代理是一个 markdown 文件，有自己的系统提示词、工具访问权限和模型偏好：
```plaintext
    .claude/agents/
    ├── code-reviewer.md
    └── security-auditor.md
```

2. 这是一个 code-reviewer.md 的示例：
```markdown
---
name: code-reviewer
description: 专家代码审查员。在审查 PR、检查 bug 或合并前验证实现时主动使用。
model: sonnet
tools: Read, Grep, Glob
---
你是一位专注于正确性和可维护性的高级代码审查员。
审查代码时：
- 标记 bug，不仅仅是风格问题
- 提出具体的修复建议，而不是模糊的改进
- 检查边缘情况和错误处理缺口
- 只有在规模化时才关注性能问题
```

3. 当 Claude 需要进行代码审查时，它会在自己的隔离上下文窗口中生成这个代理。代理完成工作，压缩发现内容，然后报告回来。你的主会话不会被数千个中间探索的 token 弄乱。

4. tools 字段限制代理可以做什么。安全审计员只需要 Read、Grep 和 Glob。它没有理由写文件。这种限制是刻意的，值得明确说明。

5. model 字段让你可以使用更便宜、更快的模型来处理专注的任务。Haiku 在大多数只读探索任务上表现出色。把 Sonnet 和 Opus 留给真正需要它们的工作。

6. 个人代理放在 **~/.claude/agents/** 中，在所有项目中可用。

    ![[IMG-20260405214107575.jpg|500]]

# settings.json：权限和项目配置

1. **.claude/** 中的 **settings.json** 文件控制 Claude 允许和不允许做什么。在这里定义 Claude 可以运行哪些工具、可以读取哪些文件，以及在运行某些命令前是否需要询问。

2. 完整的文件如下：
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Read",
      "Write",
      "Edit"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

## 以下是每个部分的作用

3. **[$schema](https://x.com/search?q=%24schema&src=cashtag_click)** 行在 VS Code 或 Cursor 中启用自动补全和内联验证。始终包含它。

4. **允许列表** 包含 Claude 无需询问即可运行的命令。对于大多数项目，一个好的允许列表涵盖：

- Bash(npm run \*) 或 Bash(make \*) 让 Claude 可以自由运行脚本
- Bash(git \*) 用于只读 git 命令
- Read、Write、Edit、Glob、Grep 用于文件操作

5. **拒绝列表** 包含完全阻止的命令，无论如何都不会执行。合理的拒绝列表会阻止：

- 破坏性的 shell 命令如 rm -rf
- 直接的网络命令如 curl
- 敏感文件如 .env 和 secrets/ 中的任何内容

6. **如果某个命令不在任一列表中，Claude 会在继续之前询问。** 这个中间地带是刻意设计的。它给了你一个安全网，而无需预先预测每个可能的命令。

## settings.local.json 用于个人覆盖

7. **CLAUDE.local.md** 相同的理念。为你不想提交的权限更改创建 **.claude/settings.local.json**。它会自动被 gitignore。

# 全局 ~/.claude/ 文件夹

1. 你不经常与这个文件夹交互，但知道里面是什么是有用的。

2. **~/.claude/CLAUDE.md** 加载到每个 Claude Code 会话中，跨所有项目。对于你的个人编码原则、偏好风格，或任何你希望 Claude 记住的内容（无论你在哪个仓库），这是一个好地方。

3. **~/.claude/projects/** 存储每个项目的会话记录和自动记忆。Claude Code 在工作时会自动保存给自己的笔记：它发现的命令、观察到的模式、架构洞察。这些在会话之间持久化。你可以用 /memory 浏览和编辑它们。

4. **~/.claude/commands/** 和 **~/.claude/skills/** 存放跨所有��目可用的个人命令和技能。

5. 你通常不需要手动管理这些。但知道它们的存在很方便，当 Claude 似乎"记住"了某些你从未告诉过它的事情时，或者当你想要清除一个项目的自动记忆重新开始时。

## 全景图

1. 以下是所有内容如何整合在一起：

```plaintext
your-project/
├── CLAUDE.md                  # 团队指令（提交）
├── CLAUDE.local.md            # 你的个人覆盖（gitignore）
│
└── .claude/
    ├── settings.json          # 权限 + 配置（提交）
    ├── settings.local.json    # 个人权限覆盖（gitignore）
    │
    ├── commands/              # 自定义斜杠命令
    │   ├── review.md          # → /project:review
    │   ├── fix-issue.md       # → /project:fix-issue
    │   └── deploy.md          # → /project:deploy
    │
    ├── rules/                 # 模块化指令文件
    │   ├── code-style.md
    │   ├── testing.md
    │   └── api-conventions.md
    │
    ├── skills/                # 自动调用工作流
    │   ├── security-review/
    │   │   └── SKILL.md
    │   └── deploy/
    │       └── SKILL.md
    │
    └── agents/                # 专业化子代理角色
        ├── code-reviewer.md
        └── security-auditor.md
~/.claude/
├── CLAUDE.md                  # 你的全局指令
├── settings.json              # 你的全局设置
├── commands/                  # 你的个人命令（所有项目）
├── skills/                    # 你的个人技能（所有项目）
├── agents/                    # 你的个人代理（所有项目）
└── projects/                  # 会话历史 + 自动记忆
```

# 实用的入门设置

1. 如果你从零开始，以下是一个效果很好的进阶路径。

2. **第 1 步。** 在 Claude Code 中运行 /init。它会通���读取你的项目来生成一个起步 CLAUDE.md。把它精简到要点。

3. **第 2 步。** 添加带有适合你技术栈的 allow/deny 规则的 .claude/settings.json。至少，允许你的运行命令并拒绝 .env 读取。

4. **第 3 步。** 为你最常做的工作流创建一到两个命令。代码审查和 issue 修复是很好的起点。

5. **第 4 步。** 随着项目增长和 CLAUDE.md 变得拥挤，开始将指令拆分为 .claude/rules/ 文件。在有意义的地方用路径限定它们的作用域。

6. **第 5 步。** 添加一个包含你个人偏好的 ~/.claude/CLAUDE.md。这可能是"始终先写类型再写实现"或"优先使用函数式模式而不是类"之类的东西。

7. 这真的是 95% 项目所需的全部。当你有值得打包的重复复杂工作流时，技能和代理才会派上用场。

## 关键洞察

1. .claude 文件夹 实际上是一个协议，告诉 Claude 你是谁、你的项目做什么、以及它应该遵循什么规则。你定义得越清楚，你花在纠正 Claude 上的时间就越少，它花在真正有用工作上的时间就越多。

2. CLAUDE.md 是你杠杆最高的文件。 先把这个弄对。其他一切都是优化。

3. 从小处着手，边走边完善，把它当作项目中任何其他基础设施一样对待：一旦设置得当，它每天都会产生回报。

4. 到此结束！

5. 如果你喜欢这篇文章。

6. 关注我 → [@akshay_pachaar](https://x.com/@akshay_pachaar) ✔️

7. 我每天分享关于 AI、机器学习和氛围编码最佳实践的教程和见解。