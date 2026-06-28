---
title: "Agentic AI Framework for Java Developers"
source: "https://java2ai.com/docs/frameworks/agent-framework/tutorials/skills"
author:
  - "[[spring-ai-alibaba-team]]"
published: 2026-02-02
created: 2026-06-28
description: "Spring AI Alibaba 开源项目基于 Spring AI 构建，是阿里云通义系列模型及服务在 Java AI 应用开发领域的最佳实践，提供高层次的 AI API 抽象与云原生基础设施集成方案，帮助开发者快速构建 AI 应用。"
tags:
  - "clippings"
---
# 一、Agentic AI Framework for Java Developers 8

1. Skills 是可复用的指令与上下文包，智能体在相关任务时会自动发现并使用。通过 **SkillRegistry** 管理技能、 **SkillsAgentHook** 注册 `read_skill` 工具并注入技能列表到系统提示，模型在需要时调用 `read_skill(skill_name)` 按需加载完整内容。

## 1. 核心概念

### 1.1 渐进式披露

1. 系统提示中先只注入技能列表（name、description、skillPath）；模型判断需要某技能时调用 `read_skill(skill_name)` 加载完整 SKILL.md；再按需访问技能目录下的资源或使用与该技能绑定的工具。

### 1.2 Skill 目录结构

1. 每个技能一个子目录，必须包含 `SKILL.md` ：

```markdown
skill-name/
├── SKILL.md          # 必需
├── references/       # 可选
├── examples/
└── scripts/
```

### 1.3 SKILL.md 格式规范

```yaml
---
name: skill-name
description: This skill should be used when...
---

# 技能名称
正文：功能说明、使用方法、可用资源列表等。
```

1. **必需字段** ： `name` （建议小写字母、数字、连字符，最长 64 字符）、 `description` （超长会被截断）。

---

## 2. 在 Agent 中使用 Skills

### 2.1 使用 FileSystemSkillRegistry

1. 智能体支持从本地文件系统中加载 skills 技能，以下示例假设 `skills` 在进程工作目录，如：

```markdown
skills/
├── pdf-extractor/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

```java
SkillRegistry registry = FileSystemSkillRegistry.builder()
  .projectSkillsDirectory(System.getProperty("user.dir") + "/skills")
  .build();

SkillsAgentHook hook = SkillsAgentHook.builder()
  .skillRegistry(registry)
  .build();

ReactAgent agent = ReactAgent.builder()
  .name("skills-agent")
  .model(chatModel)
  .saver(new MemorySaver())
  .hooks(List.of(hook))
  .build();

agent.call("请介绍你有哪些技能");
```

2. 目录配置： `userSkillsDirectory(String|Resource)` 、 `projectSkillsDirectory(String|Resource)` ；不设置时用户级默认 `~/saa/skills` ，项目级默认 `./skills` ，同名技能“项目级别”覆盖“用户级别”。

### 2.2 使用 ClasspathSkillRegistry

1. 技能放在 `src/main/resources/skills` 或随 JAR 打包。可选 `.basePath("/tmp")` 指定 JAR 内资源复制到的目录（默认 `/tmp` ）。

```java
SkillRegistry registry = ClasspathSkillRegistry.builder()
  .classpathPath("skills")
  .build();

SkillsAgentHook hook = SkillsAgentHook.builder()
  .skillRegistry(registry)
  .build();

ReactAgent agent = ReactAgent.builder()
  .name("skills-agent")
  .model(chatModel)
  .hooks(List.of(hook))
  .build();
```

### 2.3 完整集成示例（Skills + Python + Shell）

1. 技能常需配合脚本执行（如技能目录下的 Python 脚本）和 Shell 命令。下面示例使用 **ClasspathSkillRegistry** 加载技能、 **SkillsAgentHook** 提供 `read_skill` 、 **ShellToolAgentHook** 提供 Shell 工具、 **PythonTool** 提供 Python 执行能力，Agent 可根据技能说明读取并处理技能目录下的文件。

```java
import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import com.alibaba.cloud.ai.graph.agent.hook.skills.SkillsAgentHook;
import com.alibaba.cloud.ai.graph.agent.hook.shelltool.ShellToolAgentHook;
import com.alibaba.cloud.ai.graph.agent.tools.PythonTool;
import com.alibaba.cloud.ai.graph.agent.tools.ShellTool2;
import com.alibaba.cloud.ai.graph.checkpoint.savers.MemorySaver;
import com.alibaba.cloud.ai.graph.skills.registry.classpath.ClasspathSkillRegistry;
import com.alibaba.cloud.ai.graph.skills.registry.SkillRegistry;

// 1. 技能注册表：从 classpath:skills 加载（如 src/main/resources/skills/）
SkillRegistry registry = ClasspathSkillRegistry.builder()
  .classpathPath("skills")
  .build();

// 2. Skills Hook：注册 read_skill 工具并注入技能列表到系统提示
SkillsAgentHook skillsHook = SkillsAgentHook.builder()
  .skillRegistry(registry)
  .build();

// 3. Shell Hook：提供 Shell 命令执行（工作目录可指定，如当前工程目录）
ShellToolAgentHook shellHook = ShellToolAgentHook.builder()
  .shellTool2(ShellTool2.builder(System.getProperty("user.dir")).build())
  .build();

// 4. 构建 Agent：同时挂载 Skills Hook、Shell Hook 和 Python 工具
ReactAgent agent = ReactAgent.builder()
  .name("skills-integration-agent")
  .model(chatModel)
  .saver(new MemorySaver())
  .tools(PythonTool.createPythonToolCallback(PythonTool.DESCRIPTION))
  .hooks(List.of(skillsHook, shellHook))
  .enableLogging(true)
  .build();

// 5. 调用示例：用户请求处理技能目录下的文件时，模型可先 read_skill 再按技能说明调用 Python/Shell
String skillFilePath = "/path/to/skills/pdf-extractor/saa-roadmap.pdf";  // 实际路径来自技能目录或 hook.listSkills()
AssistantMessage response = agent.call("请从 " + skillFilePath + " 文件中提取关键信息。");
```

* **SkillRegistry** ： `FileSystemSkillRegistry` 用 `projectSkillsDirectory(path)` 或 `ClassPathResource("skills")` ； `ClasspathSkillRegistry` 用 `classpathPath("skills")` 。
* **ShellTool2** ： `ShellTool2.builder(workDir).build()` ， `workDir` 为 Shell 执行的工作目录（如 `System.getProperty("user.dir")` ）。
* **PythonTool** ： `PythonTool.createPythonToolCallback(PythonTool.DESCRIPTION)` 即够用，如需自定义描述可传第二个参数。
* 技能列表中会包含每个技能的 `skillPath` ，模型可用该路径拼出技能目录下文件的绝对路径并交给 Python/Shell 处理。

---

## 3. 高级用法

### 3.1 渐进式工具 Tool 披露

1. 通过将工具与 Skill 技能名绑定，可以做到工具跟随 Skill 实现渐进式披露：仅当模型对该技能调用了 `read_skill` 后，对应工具才会加入当次请求，实现按需暴露。激活后该技能的工具在会话后续轮次中仍可用。

```java
Map<String, List<ToolCallback>> groupedTools = Map.of(
  "my-skill",   // 与 SKILL.md 的 name 一致，如 'pdf-extractor'
  List.of(myTool)
);

SkillsAgentHook hook = SkillsAgentHook.builder()
  .skillRegistry(registry)
  .groupedTools(groupedTools)
  .build();
```

### 3.2 生产环境配置

#### 自动重载技能

```java
SkillsAgentHook hook = SkillsAgentHook.builder()
  .skillRegistry(registry)
  .autoReload(true)
  .build();
```

1. 每次 Agent 执行前会调用 `registry.reload()` （若实现支持；不支持则抛 `UnsupportedOperationException` ，Hook 会捕获并打 debug 日志）。

> 注意，每次 Agent 执行可能包含多次模型推理， `registry.reload()` 仅会在第一次推理时执行并加载最新的 skills，这样能保证同一次 Agent 执行时行为的连续性。

#### 用户级与项目级目录

```java
SkillRegistry registry = FileSystemSkillRegistry.builder()
  .userSkillsDirectory("/home/user/saa/skills")
  .projectSkillsDirectory("/app/project/skills")
  .build();
```

1. 同名技能项目覆盖用户。

#### 自定义系统提示模板

1. SAA 框架内置了 Skill Prompt 模板，用来引导实现 Skill 的渐进式披露。用户可结合自己系统的 Skill 组织方式定制 Prompt 模板。

```java
SystemPromptTemplate customTemplate = SystemPromptTemplate.builder()
  .template("## 可用技能\n{skills_list}\n\n## 加载说明\n{skills_load_instructions}")
  .build();

FileSystemSkillRegistry registry = FileSystemSkillRegistry.builder()
  .projectSkillsDirectory("./skills")
  .systemPromptTemplate(customTemplate)
  .build();
```

2. 模板变量： `{skills_list}` 、 `{skills_load_instructions}` 。

### 3.3 拓展 SkillRegistry 实现

1. 实现 `SkillRegistry` 接口（ `get` 、 `listAll` 、 `contains` 、 `size` 、 `readSkillContent` 、 `getSkillLoadInstructions` 、 `getRegistryType` 、 `getSystemPromptTemplate` ，可选 `reload()` ）即可接入现有 Skills 体系。 `SkillMetadata` 需包含 `name` 、 `description` 、 `skillPath` （及可选 `source` ）。可参考 `AbstractSkillRegistry` 、 `FileSystemSkillRegistry` 、 `ClasspathSkillRegistry` 。

---

## 4. 在 Graph 中使用 Skills

1. 除在 **ReactAgent** 上通过 **SkillsAgentHook** 使用 Skills 外，在基于 **Graph** 或 **ChatClient** 的链路中，可通过 **ChatClient** 配合 **SkillPromptAugmentAdvisor** （ `spring-ai-alibaba-graph-core` ）将技能列表注入系统提示，实现渐进式披露的「技能发现」部分。

### 4.1 使用 ChatClient + SkillPromptAugmentAdvisor

1. `SkillPromptAugmentAdvisor` 是 Spring AI 的 `Advisor` ，在每次请求的 `before` 阶段将技能元数据（name、description、skillPath）注入系统提示，使模型知晓可用技能及加载说明；模型需要完整 SKILL.md 时，需配合 `read_skill` 工具（可由 SkillsAgentHook 提供或自行注册）。

```java
import org.springframework.ai.chat.client.ChatClient;
import com.alibaba.cloud.ai.graph.advisors.SkillPromptAugmentAdvisor;

// 方式一：指定技能目录（字符串路径），Advisor 内部创建 FileSystemSkillRegistry
SkillPromptAugmentAdvisor skillAdvisor = SkillPromptAugmentAdvisor.builder()
  .projectSkillsDirectory("./skills")       // 或绝对路径 /path/to/skills
  // .userSkillsDirectory("~/saa/skills")  // 可选，默认 ~/saa/skills
  .lazyLoad(false)                          // 可选，true 则首次请求时再加载技能
  .build();

ChatClient chatClient = ChatClient.builder(chatModel)
  .defaultAdvisors(skillAdvisor)
  .build();

// 调用时系统提示中会包含可用技能列表
String response = chatClient.prompt()
  .user("请介绍你有哪些技能")
  .call()
  .content();
```

```java
import com.alibaba.cloud.ai.graph.skills.registry.SkillRegistry;
import com.alibaba.cloud.ai.graph.skills.registry.filesystem.FileSystemSkillRegistry;

SkillRegistry registry = FileSystemSkillRegistry.builder()
  .projectSkillsDirectory("./skills")
  .build();

SkillPromptAugmentAdvisor skillAdvisor = SkillPromptAugmentAdvisor.builder()
  .skillRegistry(registry)
  .build();

ChatClient chatClient = ChatClient.builder(chatModel)
  .defaultAdvisors(skillAdvisor)
  .build();
```

2. **说明** ：
* **SkillPromptAugmentAdvisor** 仅负责在系统提示中注入技能列表与加载说明，不注册 `read_skill` 工具。若需模型按需读取完整 SKILL.md，请在 ChatClient/Graph 中额外注册 `read_skill` （例如使用带 SkillsAgentHook 的 Agent 节点，或单独将 `ReadSkillTool` 注册为工具）。
* **Graph 中的 Agent 节点** ：若节点内部使用 `ChatClient` ，可在构建该 `ChatClient` 时加入 `SkillPromptAugmentAdvisor` ；若节点使用 ReactAgent，则直接使用 **SkillsAgentHook** （会同时注入技能列表并注册 `read_skill` ）。
* 技能通常需配合脚本执行（如技能目录下的 Python 脚本）和 Shell 命令才能在生产环境中正常使用。

---

## 5. 最佳实践与性能建议

* **控制 SKILL.md 大小** ：单文件建议约 1.5k–2k tokens，长内容放 `references/` 并在正文中列路径。
* **技能名称一致** ： `name` 、 `read_skill` 参数、 `groupedTools` 的 key 保持一致。
* **按需使用 groupedTools** ：仅需「随技能激活」的工具用 groupedTools，其余用 Agent 的 `.tools()` 即可。
* **常用 API** ： `hook.listSkills()` 、 `hook.hasSkill(name)` 、 `hook.getSkillCount()` ； `registry.reload()` （ClasspathSkillRegistry 支持）。
