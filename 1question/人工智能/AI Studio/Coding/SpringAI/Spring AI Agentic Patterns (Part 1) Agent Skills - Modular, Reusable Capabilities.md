---
title: "Spring AI Agentic Patterns (Part 1) Agent Skills - Modular, Reusable Capabilities"
tags:
  - "人工智能"
  - "人工智能/AI Studio"
  - "人工智能/AI Studio/Coding"
  - "SpringAI"
  - "AI Studio"
  - "Spring Boot"
updated: 2026-04-16
---
# Spring AI Agentic Patterns (Part 1) Agent Skills - Modular, Reusable Capabilities
## Subtitle: "可在你的环境中运行、与 LLM 无关的 Skills"

![[IMG-20260406023912862.png|495]]

Agent Skills 是由指令、脚本和资源组成的模块化文件夹，AI Agent 可以按需发现并加载它们。与其把知识硬编码进提示词，或者为每个任务都创建专门工具，不如用 skills 这种更灵活的方式来扩展 agent 的能力。

Spring AI 的实现把 Agent Skills 带入了 Java 生态，并确保 LLM 可移植性：定义一次 skills，就可以与 OpenAI、Anthropic、Google Gemini，或任何其他受支持的模型一起使用。

**这是我们的 Spring AI Agentic Patterns 系列的第一篇文章**。本系列将探索 [spring-ai-agent-utils](https://github.com/spring-ai-community/spring-ai-agent-utils) 工具包，这是一套面向 Spring AI 的完整 agentic patterns，灵感来自 [Claude Code](https://code.claude.com/docs/en/overview)。我们会先讲 Agent Skills（本文），接着介绍 Task Management、用于交互式工作流的 AskUserQuestion，以及用于复杂多智能体系统的分层 Sub-Agents。

🚀 **想直接上手？** 可以直接跳到 [Getting Started](#getting-started) 一节。

我们先从 Agent Skills 开始，它是组织 agent 知识的基础。

# 什么是 Agent Skills？

Agent Skills 是以带有 `YAML frontmatter` 的 Markdown 文件形式打包的模块化能力。每个 skill 都是一个文件夹，其中包含一个 `SKILL.md` 文件，里面至少要有元数据（`name` 和 `description`）以及指导 agent 如何执行特定任务的说明。Skills 还可以附带脚本、模板和参考资料。frontmatter 同时支持简单字符串值以及复杂 YAML 结构（列表、嵌套对象），以满足高级用例。

```php
my-skill/
├── SKILL.md          # 必需：说明 + 元数据
├── scripts/          # 可选：可执行代码
├── references/       # 可选：参考文档
└── assets/           # 可选：模板、资源
```

Skills 使用 **渐进式披露（progressive disclosure）** 来高效管理上下文：

1. **发现（Discovery）**：启动时，agent 只加载每个可用 skill 的名称和描述，信息量刚好足以判断它何时可能相关。
2. **激活（Activation）**：当某个任务与 skill 的描述匹配时，agent 才会把完整的 `SKILL.md` 指令读入上下文。
3. **执行（Execution）**：agent 按照说明执行，并在需要时选择性加载引用文件或执行附带代码。

这种方式使你可以注册数百个 skills，同时保持上下文窗口足够精简。

> **💡Tip：** 关于 Agent Skills 的更多信息，请查看[官方规范](https://agentskills.io/specification)。

# 为什么在 Spring AI 中使用 Agent Skills

**无缝集成** - 只需注册几个 tools，就可以把 Agent Skills 加入你现有的 Spring AI 应用中，不需要改动整体架构。

**可移植且与模型无关，不会被供应商锁定** - 与那些绑定到特定 LLM 平台的实现不同，这个 Spring AI 实现可以跨多个 LLM 提供商工作，让你切换模型时不必重写代码或 skills。

**可复用且可组合** - Skills 可以跨项目共享、与代码一起做版本控制、组合起来形成复杂工作流，并通过辅助脚本和参考资料扩展能力。Spring AI Skills 还可以无缝支持任何现有的 Claude Code Skills。

**相关的 Spring AI Tools：** Agent Skills 与其他基于 tool 的 Spring AI 特性配合良好，例如用于高效工具选择的 [Dynamic Tool Discovery](https://spring.io/blog/2025/12/11/spring-ai-tool-search-tools-tzolov)，以及用于在 skill 执行期间捕获 LLM 推理过程的 [Tool Argument Augmentation](https://spring.io/blog/2025/12/23/spring-ai-tool-argument-augmenter-tzolov)。

# Spring AI Skills 的工作原理

Spring AI 使用的是[基于工具的集成方式](https://agentskills.io/integrate-skills#integration-approaches)，它通过实现一组 tools，让任何 LLM 都能触发 skills 并访问打包资源。该实现基本遵循 [Claude Code](https://code.claude.com/docs/en/settings#tools-available-to-claude) 对 `Skills`、`Bash` 和 `Read` 的工具规范。

核心工具集包括：[SkillsTool](https://github.com/spring-ai-community/spring-ai-agent-utils/blob/main/spring-ai-agent-utils/docs/SkillsTool.md)（必需）、[ShellTools](https://github.com/spring-ai-community/spring-ai-agent-utils/blob/main/spring-ai-agent-utils/docs/ShellTools.md)（可选）以及 [FileSystemTools](https://github.com/spring-ai-community/spring-ai-agent-utils/blob/main/spring-ai-agent-utils/docs/FileSystemTools.md)（可选）。SkillsTool 提供了一个 `Skill` 函数，使 AI 模型能够按需发现并加载指定 skill；它与 FileSystemTools（用于读取参考文件）和 ShellTools（用于执行辅助脚本）协同工作。

Skills 通过以下三步运行：

**1\. 发现（启动时）** - 在初始化期间，SkillsTool 会扫描配置的 skills 目录（例如 `.claude/skills/`），并解析每个 `SKILL.md` 文件中的 YAML frontmatter。它会提取 `name` 和 `description` 字段，构建一个轻量级的 skill 注册表，并将其直接嵌入 `Skill` 工具的 description 中。这样，LLM 就能看到这些信息，而不会占用对话上下文。

![[IMG-20260406023912926.png|732]]

**2\. 语义匹配（对话期间）** - 当用户发出请求时，LLM 会检查嵌入在工具定义中的 skill 描述。如果 LLM 判断用户请求在语义上与某个 skill 的描述匹配，它就会调用 `Skill` 工具，并把 skill 名称作为参数传入。

**3\. 执行（调用 skill 时）** - 当 `Skill` 工具被调用后，SkillsTool 会从磁盘加载完整的 `SKILL.md` 内容，并将其连同 skill 的基础目录路径一起返回给 LLM。接着，LLM 按照 skill 内容中的指令执行。如果该 skill 引用了额外文件或辅助脚本，LLM 会在需要时使用 FileSystemTools 的 `Read` 函数或 ShellTools 的 `Bash` 函数按需访问它们。

# Skills 的实际运作

这一节通过真实例子展示 skills 在实践中如何工作。

# 示例：带有 References 和 Scripts 的 Skills

当 skill 打包了额外资源时，第 3 步中的按需加载就会变得非常强大。Skills 可以包含带有补充说明的参考文件，以及用于数据处理的可执行脚本，而且这些内容都只会在需要时才被加载。

下面这个例子来自 `my-skill`，它包含一个用于提取 YouTube 转录文本的辅助脚本，以及一个补充说明文件 `research_methodology.md`：

**Skill 目录结构：**

```markdown
.claude/skills/my-skill/
├── SKILL.md
├── scripts/
│   └── get_youtube_transcript.py
└── research_methodology.md
```

**在 SKILL.md 中：**

```markdown
...
**如果概念不熟悉或需要调研：**
加载 \`research_methodology.md\` 获取详细指导。
**如果用户提供了 YouTube 视频：**
调用 \`uv run scripts/get_youtube_transcript.py <video_url_or_id>\`
获取视频转录文本。
...
```

当用户提出 “Explain the concepts from this video: [https://youtube.com/watch?v=abc123](https://youtube.com/watch?v=abc123). Follow the research methodology” 这样的请求时，AI 会：

1. 调用 `my-skill` skill，并加载它的 `SKILL.md` 内容
2. 识别出需要 research methodology，于是用 `Read` 加载 `research_methodology.md`
3. 识别出 YouTube URL，于是通过 ShellTools 使用 `Bash` 执行辅助脚本
4. 按照 research methodology 的说明，利用视频转录文本来解释其中的概念

![[IMG-20260406023912959.png|763]]

脚本代码本身不会进入上下文窗口，只有输出会进入，因此这种方式在 token 使用上非常高效。

💡 **Demo** 可以查看 [Skills-Demo](https://github.com/spring-ai-community/spring-ai-agent-utils/tree/main/examples/skills-demo)，它实现了这一工作流。

> ⚠️ **安全提示：** 脚本会直接在你的本地机器上执行，而且没有沙箱隔离。你需要预先安装所有必需的运行时（Python、Node.js 等）。如果希望更安全，建议在容器中运行你的 agentic application。

# Getting Started

准备好把 Agent Skills 加入你的 Spring AI 项目了吗？

**1\. 添加依赖：**

```xml
<dependency>
    <groupId>org.springaicommunity</groupId>
    <artifactId>spring-ai-agent-utils</artifactId>
    <version>0.4.2</version>
</dependency>
```

**注意：** 最新稳定版本请查看 [GitHub releases page](https://github.com/spring-ai-community/spring-ai-agent-utils/releases)。

**注意：** 你需要 Spring-AI `2.0.0-M2+`。

**2\. 配置你的 agent：**

```java
@SpringBootApplication
public class Application {
    @Bean
    CommandLineRunner demo(ChatClient.Builder chatClientBuilder) {
        return args -> {
            ChatClient chatClient = chatClientBuilder
                .defaultToolCallbacks(SkillsTool.builder()
                    .addSkillsDirectory(".claude/skills")
                    .build())
                .defaultTools(FileSystemTools.builder().build())
                .defaultTools(ShellTools.builder().build())
                .build();
            String response = chatClient.prompt()
                .user("Your task here")
                .call()
                .content();
        };
    }
}
```
> **💡 生产提示：** 对于打包后的应用，你可以使用 Spring Resources 从 classpath 加载 skills：
> 
> ```java
> .defaultToolCallbacks(SkillsTool.builder()
>     .addSkillsResource(resourceLoader.getResource("classpath:.claude/skills"))
>     .build())
> ```
> 
> 当你把 skills 作为 JAR/WAR 部署的一部分进行分发时，这种方式会特别有用。

**3\. 创建你的第一个 skill：**

```bash
mkdir -p .claude/skills/code-reviewer
cat > .claude/skills/code-reviewer/SKILL.md << 'EOF'
---
name: code-reviewer
description: 审查 Java 代码是否符合最佳实践、安全要求和 Spring Framework 约定。当用户要求 review、analyze 或 audit 代码时使用。
---
# Code Reviewer
## Instructions
When reviewing code:
1. Check for security vulnerabilities (SQL injection, XSS, etc.)
2. Verify Spring Boot best practices (proper use of @Service, @Repository, etc.)
3. Look for potential null pointer exceptions
4. Suggest improvements for readability and maintainability
5. Provide specific line-by-line feedback with code examples
EOF
```

**4\. 结合该 skill 使用你的 agent：**

```java
String response = chatClient.prompt()
    .user("Review this controller class for best practices: " +
          "src/main/java/com/example/UserController.java")
    .call()
    .content();
System.out.println(response);
```

运行后，LLM 将会：

1. 将 “Review this controller” 与 `code-reviewer` skill 的描述进行匹配
2. 调用 `Skill` 工具，从 `SKILL.md` 加载完整说明
3. 使用 `Read` 工具（来自 FileSystemTools）读取 `UserController.java` 文件
4. 按照审查说明执行，并给出详细反馈

skill 中的说明会指导 LLM 的行为，而你不需要把 review 逻辑硬编码进提示词中；如果要改变 review 的方式，只需更新这个 skill 文件即可。

# 当前限制

虽然 Spring AI Agent Skills 的实现已经很强大且灵活，但目前仍有一些限制需要注意：

**脚本执行安全性** - 通过 ShellTools 执行的脚本会直接在你的本地机器上运行，而且没有沙箱隔离。这意味着潜在的不安全代码可能访问你的文件系统、网络或系统资源。使用前务必审查 skill 脚本，尤其是来自第三方来源的脚本。建议在容器化环境（Docker、Kubernetes）中运行你的 agentic application，以限制暴露面。

**没有 Human-in-the-Loop** - 目前没有内建机制要求在执行 skills 或脚本之前先经过人工批准。LLM 可以调用任何已注册的 skill，并自动执行其中附带的任何脚本。对于涉及敏感操作的生产环境，你可能需要基于 Spring AI 的 tool callback 机制实现自定义审批工作流，例如包一层 `ToolCallback` wrapper。

**有限的 Skill 版本管理能力** - 当前没有内建的 skill 版本管理系统。如果你更新了某个 skill 的行为，所有使用该 skill 的应用都会立刻使用新版本。对于生产部署，建议通过目录结构实现你自己的版本策略（例如 `.claude/skills/v1/`、`.claude/skills/v2/`）。

Spring AI 还集成了 Anthropic 的原生 Skills API，它提供了另一种方式：

- Skills 运行在 Anthropic 提供的云端沙箱容器中（无网络访问，仅允许使用预装包）
- 内置文档生成能力：Excel、PowerPoint、Word、PDF
- Skills 会上传到 Anthropic 服务器，并在你的 workspace 中共享
- 需要 Claude 模型（Sonnet 4、Sonnet 4.5、Opus 4）

**关键区别：** Anthropic Skills 运行在 Anthropic 的云基础设施中；Generic Agent Skills 则运行在你的环境里。

当你需要安全的沙箱执行能力，或者需要内置文档生成功能时，使用 Anthropic 的原生 Skills。若你需要 LLM 可移植性、本地资源访问能力，或者希望将 skills 与你的应用一起打包，则使用 Generic Agent Skills。

**两者能一起用吗？** 可以。你可以在同一个应用中，用 Anthropic 的原生 Skills 做文档生成，同时用 Generic Agent Skills 提供其他可移植能力。它们用途不同，而且可以互补。