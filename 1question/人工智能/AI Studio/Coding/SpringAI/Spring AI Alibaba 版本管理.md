---
title: "Spring AI Alibaba 版本管理"
tags:
  - "人工智能"
  - "人工智能/AI Studio"
  - "人工智能/AI Studio/Coding"
  - "SpringAI"
  - "Spring AI Alibaba"
  - "Maven"
  - "Java"
updated: 2026-05-09
author: "ken.lj"
source_name: "Spring AI Alibaba Docs"
source_url: "https://java2ai.com/docs/versions/"
source_updated: 2026-02-02
aliases:
  - "SAA 版本管理"
  - "Spring AI Alibaba BOM 版本管理"
  - "Spring AI Alibaba 依赖管理"
---
> [!info] 原文信息
> 作者：ken.lj
> 来源：Spring AI Alibaba 文档
> 原文更新时间：2026-02-02
> 链接：https://java2ai.com/docs/versions/
> 补充核对：2026-05-09 额外检查了 Maven Central 上的 `spring-ai-alibaba-bom`、`spring-ai-alibaba-extensions-bom` 与 `spring-ai-alibaba-starter-dashscope`。
> [!abstract] 核心摘要
> Spring AI Alibaba 1.1.2.0 的版本管理不能只看 `spring-ai-alibaba-bom`。如果项目里用了 `spring-ai-alibaba-starter-dashscope`、memory、document reader、tool-calling 等扩展模块，还需要同时关注 `spring-ai-alibaba-extensions-bom`。这次 `industry-ai-core/pom.xml` 报 `spring-ai-alibaba-starter-dashscope` 缺少 `version`，本质上不是 artifact 消失，而是它已经不再由核心 BOM 管理。进一步说，`BOM` 并不是 Maven 之外的新概念，它本质上就是基于 `dependencyManagement` 的版本清单；很多团队虽然平时不把它叫作 `BOM`，但其实一直在做同类的版本统一管理。

# 一、先说结论
* `SAA` 就是 `Spring AI Alibaba` 的缩写。
* `BOM` 是 `Bill of Materials`，在 Maven 里可以理解成“依赖版本清单”。
* 你之前在父 `pom` 里统一管理 `travelvc-client` 这类二方包版本，和 `BOM` 在机制上是同一类事情，核心都是让子模块不必重复写 `<version>`。
* 区别主要不在“有没有新机制”，而在“版本清单是你自己在父 `pom` 里维护，还是导入外部已经整理好的 BOM”。
* Spring AI Alibaba 在 `1.1.x` 阶段已经形成了三层版本关系：`spring-ai-alibaba-bom` 管核心框架，`spring-ai-bom` 管上游 Spring AI，`spring-ai-alibaba-extensions-bom` 管扩展模块。
* 如果项目只导入了 `spring-ai-alibaba-bom`，那么像 `spring-ai-alibaba-starter-dashscope` 这样的扩展 starter 可能拿不到版本管理，最终在业务模块里报 “dependency 缺少 version”。

# 二、SAA 是什么
1. `SAA` 是 `Spring AI Alibaba` 的缩写。
2. 可以先把这几个名字拆开记。

| 缩写或名称 | 含义 | 角色 |
| --- | --- | --- |
| `Spring AI` | Spring 官方的 AI 框架 | 上游基础框架 |
| `Spring AI Alibaba` | 阿里云围绕 `Spring AI` 做的一套增强和适配 | 下游扩展与生态整合 |
| `SAA 1.1.2.0` | `Spring AI Alibaba 1.1.2.0` | 当前讨论的版本号 |
3. 套到这次问题里，`spring-ai-bom` 属于上游 `Spring AI`，而 `spring-ai-alibaba-bom`、`spring-ai-alibaba-extensions-bom` 属于 `SAA` 这一层。
4. 所以 `starter-dashscope` 的报错，并不是 `Spring AI` 本身的问题，而是 `Spring AI Alibaba` 这套版本管理边界发生了变化。

# 三、BOM 是什么
1. `BOM` 全称是 `Bill of Materials`，直译是“物料清单”，放在 Maven 语境里更适合理解成“依赖版本清单”。如果只想先补 Maven 基础背景，可以先看 [[Maven]]。
2. 它通常是一个 `packaging = pom` 的工程，自己不提供业务功能，主要作用是通过 `dependencyManagement` 统一管理一组依赖版本；这一点和 [[2.4 依赖管理]] 里讲的 Spring Boot 自动版本仲裁机制，本质上是同一类思路。
3. 你在项目里导入 BOM 之后，子模块再声明这些依赖时，就可以不写 `<version>`，Maven 会从 BOM 的 `dependencyManagement` 里把版本补出来。
4. 这里最容易混淆的一点是：`BOM` 负责“管版本”，但不会自动“把依赖真正引进来”。
5. 一句话记忆可以写成下面这样。
    ```text
    dependencies 决定“要什么”
    dependencyManagement / BOM 决定“用哪个版本”
    ```
6. 最小关系图如下。
    ```text
    业务模块 pom.xml
    │
    ├─ <parent>
    │   └─ 父 pom.xml
    │
    ├─ <dependencies>
    │   └─ 只声明“我要用哪个依赖”
    │      例如：spring-ai-alibaba-starter-dashscope
    │      可以不写 <version>
    │
    └─ Maven 在解析版本时，会去看：
        1. 当前 pom 的 <dependencyManagement>
        2. 父 pom 的 <dependencyManagement>
        3. 父 pom 里 import 的各个 BOM
        4. 还找不到的话，就报错：缺少 version
    ```
# 四、父 pom、dependencyManagement 和 BOM 的关系
1. `dependencyManagement` 是 Maven 的原生机制，`BOM` 不是一套全新的独立机制，而是 `dependencyManagement` 的一种标准化用法；如果只看 Maven 语义本身，可以和 [[Maven]] 中“DependencyManagement 和 Dependencies”那一节对照着理解。
2. 如果父 `pom` 把依赖写在 `<dependencies>` 里，含义是“父工程自己依赖这个包”，它更偏向依赖继承。
    ```xml
    <dependencies>
        <dependency>
            <groupId>com.xxx</groupId>
            <artifactId>travelvc-client</artifactId>
            <version>1.2.3</version>
        </dependency>
    </dependencies>
    ```
3. 如果父 `pom` 把依赖写在 `<dependencyManagement>` 里，含义是“父工程统一管理版本，但不自动替子模块引入这个依赖”。
    ```xml
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.xxx</groupId>
                <artifactId>travelvc-client</artifactId>
                <version>1.2.3</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
    ```
4. 子模块这时可以只声明依赖，不写版本。
    ```xml
    <dependencies>
        <dependency>
            <groupId>com.xxx</groupId>
            <artifactId>travelvc-client</artifactId>
        </dependency>
    </dependencies>
    ```
5. `BOM` 做的事情，本质上也是把一大批这样的版本定义集中起来，只不过它常常是一个单独的 `pom`，再通过 `import` 的方式引入。
    ```xml
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.alibaba.cloud.ai</groupId>
                <artifactId>spring-ai-alibaba-extensions-bom</artifactId>
                <version>1.1.2.0</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
    ```
6. 所以更准确地说：
    * 你自己在父 `pom` 的 `dependencyManagement` 里一条条写版本，是“自建版本清单”。
    * 你导入别人提供的 BOM，是“复用外部版本清单”。
7. 两者在效果上非常接近，差别主要只在版本清单由谁维护。

# 五、为什么你之前没觉得自己在用 BOM
1. 因为很多团队平时只会说“父 `pom` 统一管版本”或者“`dependencyManagement` 管版本”，不会特意说“这是 BOM”。
2. 但从机制上看，如果你们一直在父 `pom` 里统一管理 `travelvc-client` 这类二方包版本，那其实已经是在做 BOM 同类的事情了。
3. 可以把这几种方式并排看。

| 做法 | 本质 | 子模块是否可省略 `<version>` | 是否一定要叫 BOM |
| --- | --- | --- | --- |
| 父 `pom` 的 `<dependencies>` 直接带版本 | 依赖继承 | 常见情况下可以继承依赖本身 | 否 |
| 父 `pom` 的 `<dependencyManagement>` 管版本 | 版本统一管理 | 可以 | 否 |
| 父 `pom` `import` 一个外部 BOM | 复用外部版本清单 | 可以 | 是更标准的 BOM 用法 |
4. 所以你之前的感觉没有错：`travelvc-client` 这种用法和这次聊的 `BOM` 确实很像，因为底层依然是 Maven 那套版本管理逻辑。
5. 真正导致这次报错的关键，不是你之前“没提过 BOM 这个词”，而是 Maven 最终没有在 `dependencyManagement` 体系里找到 `spring-ai-alibaba-starter-dashscope` 的版本。

# 六、Spring AI Alibaba 的版本对应关系
1. 官方版本页给出的兼容关系，可以先记成下面这张表。

| SAA 版本 | Spring AI | Spring AI Extensions | Spring Boot | 说明 |
| --- | --- | --- | --- | --- |
| `1.1.2.0` | `1.1.2` | `1.1.2.1` 或 `1.1.2.0` | `3.5.x` | 当前推荐，支持 Agent Skills、Supervisor、Routing 等多智能体能力 |
| `1.1.0.0` | `1.1.0` | `1.1.0.0` | `3.4.x` | `1.1.0` 首个正式版 |
| `1.1.0.0-RC2` | `1.1.0-RC2` | `1.1.0.0-RC2` | `3.4.x` | 候选版，不建议新项目继续使用 |
| `1.1.0.0-RC1` | `1.1.0-RC1` | `1.1.0.0-RC1` | `3.4.x` | 候选版，不建议新项目继续使用 |
2. 这个表里最容易被忽略的是第三列 `Spring AI Extensions`。它不是可有可无的补充项，而是很多扩展 starter 的真正版本来源。
3. 官方文档还特别提醒：具体 Spring Boot 的小版本，以 `spring-ai-alibaba-bom` 和各模块 `pom.xml` 为准，升级前要再核对 Release Notes。这个提醒很重要，因为 SAA 的核心 BOM、扩展 BOM 和上游 Spring AI 并不是完全同步发版。

# 七、Spring AI Alibaba 的三个 BOM 分别管什么
1. 可以把这三个 BOM 理解为三层职责边界。

| BOM | 推荐版本 | 主要职责 | 典型模块 |
| --- | --- | --- | --- |
| `spring-ai-alibaba-bom` | `1.1.2.0` | 管理 Spring AI Alibaba 主仓库里的核心模块 | `spring-ai-alibaba-agent-framework`、`spring-ai-alibaba-graph-core`、`spring-ai-alibaba-studio`、`spring-ai-alibaba-sandbox`、`spring-ai-alibaba-starter-a2a-nacos` |
| `spring-ai-bom` | `1.1.2` | 管理上游 Spring AI 的基础抽象和核心组件 | `ChatModel`、`Prompt`、`Advisor`、`VectorStore` 等上游能力 |
| `spring-ai-alibaba-extensions-bom` | `1.1.2.1` 或 `1.1.2.0` | 管理阿里这边的扩展 starter 与生态模块 | `spring-ai-alibaba-starter-dashscope`、memory、RAG、MCP、tool-calling、document reader、document parser、store 等 |
2. 从 Maven Central 上实际检查 `spring-ai-alibaba-bom:1.1.2.0` 可以看到，它的 `dependencyManagement` 里只有核心模块，并不包含 `spring-ai-alibaba-starter-dashscope`。
3. 再检查 `spring-ai-alibaba-extensions-bom:1.1.2.0`，则可以看到 `spring-ai-alibaba-starter-dashscope`、`spring-ai-alibaba-starter-memory`、`spring-ai-alibaba-starter-rag`、各类 `starter-tool-calling-*`、`starter-document-reader-*` 都在这里统一管理。
4. 这意味着一个经验法则：只要你依赖的是“扩展能力”，就不要假设它还挂在 `spring-ai-alibaba-bom` 下面，最好直接去看 `extensions-bom` 的实际内容。

# 八、推荐的 BOM 写法
1. 如果你按官方当前版本页的推荐来配，可以显式导入这三个 BOM。
    ```xml
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.alibaba.cloud.ai</groupId>
                <artifactId>spring-ai-alibaba-bom</artifactId>
                <version>1.1.2.0</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            <dependency>
                <groupId>org.springframework.ai</groupId>
                <artifactId>spring-ai-bom</artifactId>
                <version>1.1.2</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            <dependency>
                <groupId>com.alibaba.cloud.ai</groupId>
                <artifactId>spring-ai-alibaba-extensions-bom</artifactId>
                <version>1.1.2.1</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
    ```
2. 如果你的项目已经锁在 `1.1.2.0`，而你现在只是要修复 `spring-ai-alibaba-starter-dashscope` 缺少 `version`，那么更稳妥的做法是把 extensions BOM 也先对齐到 `1.1.2.0`。
    ```xml
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.alibaba.cloud.ai</groupId>
                <artifactId>spring-ai-alibaba-bom</artifactId>
                <version>1.1.2.0</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            <dependency>
                <groupId>com.alibaba.cloud.ai</groupId>
                <artifactId>spring-ai-alibaba-extensions-bom</artifactId>
                <version>1.1.2.0</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            <dependency>
                <groupId>org.springframework.ai</groupId>
                <artifactId>spring-ai-bom</artifactId>
                <version>1.1.2</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
    ```
3. 如果你暂时不想引入 `spring-ai-alibaba-extensions-bom`，也可以直接给 `spring-ai-alibaba-starter-dashscope` 显式写版本，但这只适合作为临时补丁，不适合作为长期方案。
    ```xml
    <dependency>
        <groupId>com.alibaba.cloud.ai</groupId>
        <artifactId>spring-ai-alibaba-starter-dashscope</artifactId>
        <version>1.1.2.0</version>
    </dependency>
    ```
# 九、这次编译报错为什么会出现
1. 报错现象是 `industry-ai-core/pom.xml` 第 `35` 行的 `spring-ai-alibaba-starter-dashscope` 没有 `version`，说明当前模块本来预期由父 `pom` 的版本管理体系来统一接管版本。
2. 实际检查后可以确认：`spring-ai-alibaba-bom:1.1.2.0` 的 `dependencyManagement` 已经不再包含 `spring-ai-alibaba-starter-dashscope`。
3. 同时也可以确认：`spring-ai-alibaba-extensions-bom:1.1.2.0` 仍然包含 `spring-ai-alibaba-starter-dashscope`，并且 Maven Central 上 `spring-ai-alibaba-starter-dashscope:1.1.2.0` 的 JAR 依然存在。
4. 所以这次报错不是 “artifactId 失效” 或 “仓库里没有这个包”，而是 “当前项目导入的版本清单不完整，导致 Maven 无法推断这个 dependency 的版本”。
5. 对应的修复思路有两个。
    * 长期方案：在父 `pom.xml` 的 `dependencyManagement` 中补上 `spring-ai-alibaba-extensions-bom`。
    * 临时方案：直接给 `spring-ai-alibaba-starter-dashscope` 写死版本。
6. 如果当前项目整体已经统一在 `1.1.2.0`，那么把 `extensions-bom` 先也定在 `1.1.2.0` 最稳，不要在没有做兼容性回归的前提下，顺手把扩展 BOM 单独升级到 `1.1.2.1`。

# 十、迁移和排查时的 Checklist
1. 新项目不要只照抄一个 `spring-ai-alibaba-bom`，而要先确认自己到底有没有用到 DashScope、memory、RAG、MCP、tool-calling、document reader 这类扩展模块。
2. 老项目升级到 `1.1.x` 时，不要默认认为旧 starter 还由核心 BOM 管理，最好直接翻一下对应版本的 BOM `pom`。
3. 如果 Maven 报某个 dependency 缺少 `version`，第一反应不要只怀疑拼写错误，也要怀疑 “它是不是已经被迁到另一个 BOM 里了”。
4. 遇到版本冲突或 BOM 组合不清楚时，可以先跑这两个命令。
    ```bash
    mvn help:effective-pom
    mvn dependency:tree -Dincludes=com.alibaba.cloud.ai
    ```
5. 官方文档里的版本表适合拿来确定“大版本组合”，而真正落到项目排障时，更可靠的是 Maven Central 上实际发布出去的 BOM `pom` 内容。

# 十一、关联笔记
* [[百炼]]
* [[Spring AI Agentic Patterns (Part 1) Agent Skills - Modular, Reusable Capabilities]]
* [[Maven]]
* [[2.4 依赖管理]]

# 十二、和 Maven 笔记的关系
1. 这篇笔记可以看成 [[Maven]] 的一个实战延伸，重点不是讲 Maven 基础命令，而是把 `dependencyManagement`、父 `pom`、BOM、外部版本清单导入这些机制放到 `Spring AI Alibaba` 的真实排障场景里解释清楚。
2. 如果你只是想先理解 “为什么子模块可以不写 `<version>`”，优先看 [[Maven]] 和 [[2.4 依赖管理]]。
3. 如果你已经懂 Maven 的父子工程和版本仲裁机制，但想看一个“为什么明明没写版本却突然报错”的真实案例，就回到这篇笔记。
