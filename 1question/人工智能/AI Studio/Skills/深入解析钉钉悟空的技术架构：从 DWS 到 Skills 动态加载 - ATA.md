# 深入解析钉钉悟空的技术架构：从 DWS 到 Skills 动态加载

> 本文基于对 Wukong v0.9.2（macOS 版本）的逆向分析，还原其核心技术架构。悟空（Wukong）是钉钉推出的 AI Agent 桌面应用，定位为"AI 原生操作系统"，能够通过自然语言驱动钉钉全产品能力。

---

## 1 从一个问题开始：悟空是怎么"什么都能干"的？

1.0.1 打开悟空，你可以对它说："帮我查一下明天的日程"、"帮我建一个项目管理表格"、"查一下《劳动合同法》第四十七条"、"帮我做一份季度汇报 PPT"。

1.0.2 一个桌面应用，怎么做到覆盖日历、表格、法律、文档等 25+ 个业务领域？答案藏在三层架构里：

```java
┌─────────────────────────────────────────┐
│           Skills 技能层                  │  ← AI 的"使用手册"
│     告诉 AI 什么场景用什么工具            │
├─────────────────────────────────────────┤
│           DWS CLI 工具层                 │  ← 统一的命令行入口
│     将 25+ 业务模块聚合为一个 CLI         │
├─────────────────────────────────────────┤
│           MCP 协议层                     │  ← 底层通信协议
│     动态发现、动态调用钉钉云端能力         │
└─────────────────────────────────────────┘
```

1.0.3 接下来，我们自底向上，逐层拆解。

---

## 2 MCP 协议层：一切能力的通信基础

### 2.1 什么是 MCP

2.1.1 MCP（Model Context Protocol）是一种标准化协议，用于 AI Agent 与外部工具之间的通信。它定义了两个核心操作：

| 操作 | 作用 | 类比 |
| --- | --- | --- |
| `tools/list` | 获取所有可用工具的定义 | 查看菜单 |
| `tools/call` | 调用某个具体工具 | 点菜下单 |

2.1.2 悟空的整个能力体系，就建立在 MCP 协议之上。

### 2.2 悟空中的 MCP 配置

2.2.1 悟空的 MCP 配置存储在 `~/.real/.mcp/mcpServerConfig.json` 中：

```json
{
  "mcpServers": {
    "builtin-system-permissions": {
      "isActive": true,
      "name": "system_capabilities",
      "type": "internal",
      "description": "System capabilities MCP server (built-in)",
      "isBuiltin": true,
      "isRemovable": false,
      "baseUrl": "internal://system_capabilities"
    },
    "builtin-agent-model": {
      "isActive": true,
      "name": "dingtalk-real-agent-model",
      "type": "internal",
      "description": "供 Agent 调用文本与图片理解能力",
      "timeout": 3600,
      "isBuiltin": true,
      "isRemovable": false,
      "baseUrl": "internal://dingtalk-real-agent-model"
    }
  }
}
```

2.2.2 内置了两个 MCP Server：一个提供系统权限能力，一个提供模型调用能力。除此之外，用户还可以添加自定义的外部 MCP Server。

### 2.3 MCP 的工作流程

2.3.1 悟空的 MCP 工作流遵循严格的 **discover-then-call**（先发现再调用）模式：

```java
Step 1: mcp tools --json '{"id":"<server_id>"}'
        → 获取该 Server 暴露的所有工具名称和参数定义

Step 2: mcp call --json '{"id":"<server_id>","toolName":"<tool>","arguments":{...}}'
        → 使用精确的工具名称进行调用
```

2.3.2 这个模式有一条铁律：**toolName 必须来自 `tools/list` 的返回结果，禁止编造**。如果调用失败返回 `Unknown tool`，需要重新执行 `tools/list` 刷新后再重试。

---

## 3 DWS：MCP 动态聚合的 CLI 实现

### 3.1 DWS 是什么

3.1.1 DWS（DingTalk Workspace）是悟空的核心 CLI 工具，用 Go 语言编写，约 9.9MB。它的版本信息揭示了其架构理念：

```java
Version:        0.2.20
Build:          2026-03-17T20:50:27+08:00
Architecture:   MCP Dynamic Aggregation
Go:             1.22+
```

3.1.2 **MCP Dynamic Aggregation（MCP 动态聚合）**——这是 DWS 架构的精髓。它不是一个传统的、命令写死在代码里的 CLI 工具，而是一个**动态的 MCP 客户端**。

### 3.2 动态聚合的核心机制

3.2.1 传统 CLI 工具的命令在编译时就已经固定。而 DWS 的 25 个子命令，是从钉钉云端的 MCP Server **动态发现**的：

```java
┌──────────────┐
│   dws CLI    │
│  MCP Client  │
└──────┬───────┘
       │
       │ tools/list (发现可用工具)
       │ tools/call (调用具体工具)
       ▼
┌──────────────────────────┐
│  mcp.dingtalk.com        │  钉钉 MCP Server（云端）
│  /mcp/market/servers     │
└──────────┬───────────────┘
           │
           ▼
    ┌──────┴──────┐
    │ 25 个业务模块 │
    └─────────────┘
    aitable │ calendar │ contact │ chat │ todo
    mail │ ding │ law │ oa │ drive │ ...
```

3.2.2 这带来了一个巨大的优势：**钉钉后端新增业务模块时，DWS 不需要重新编译发版，只需要在 MCP Server 上注册新工具，DWS 下次刷新缓存时就能自动发现并使用新能力。**

### 3.3 本地缓存策略

3.3.1 每次都从云端发现工具显然不现实。DWS 采用了本地缓存 + 按需刷新的策略：

```java
首次启动
    │
    ▼
tools/list → 从 MCP Server 获取工具定义
    │
    ▼
缓存到本地（带过期时间）
    │
    ▼
后续调用：优先使用本地缓存
    │
    ├── 缓存有效 → 直接使用
    │
    └── 缓存过期 → "cache miss or stale, discovering from MCP servers"
                   → 重新从云端发现并更新缓存
```

3.3.2 用户也可以通过 `dws cache refresh` 手动强制刷新。

### 3.4 认证体系

3.4.1 DWS 采用 OAuth 2.0 认证，支持多种凭证方式：

```java
凭证优先级（从高到低）：
  --token 参数 > DINGTALK_TOKEN 环境变量 > 凭证文件 > 本地 OAuth token.json
```

3.4.2 Token 类型及有效期：

| Token 类型 | 有效期 | 说明 |
| --- | --- | --- |
| Access Token | 2 小时 | 调用 API 的凭证，过期自动刷新 |
| Refresh Token | 30 天 | 换取新的 Access Token，使用后自动轮转 |

3.4.3 日常使用只需首次 `dws auth login` 扫码登录，之后 Token 自动管理。

### 3.5 完整的命令体系

3.5.1 DWS 覆盖了钉钉 25 个业务模块：

| 模块 | 命令 | 能力 |
| --- | --- | --- |
| AI 表格 | `dws aitable` | Base/数据表/字段/记录 CRUD |
| 日历 | `dws calendar` | 日程/会议室/闲忙查询 |
| 通讯录 | `dws contact` | 用户/部门搜索查询 |
| 群聊 | `dws chat` | 群管理/消息/机器人 |
| 待办 | `dws todo` | 创建/查询/完成任务 |
| 邮箱 | `dws mail` | 收发邮件 |
| 审批 | `dws oa` | 审批流程管理 |
| 法律 | `dws law` | 法律咨询/法规检索/案例检索 |
| AI 设计 | `dws aidesign` | 文生图/图生图/超分/抠图 |
| 财务 | `dws finance` | 发票/凭证/银行流水 |
| ... | ... | 共 25 个模块 |

3.5.2 每个命令都支持两种输出格式：`--format table`（人类可读）和 `--format json`（机器/Agent 可读），这正是"人类与 AI Agent 的统一入口"设计理念的体现。

---

## 4 Skills 动态加载机制：让 AI "知道怎么用工具"

4.0.1 有了 DWS 这把瑞士军刀，还需要一本使用手册告诉 AI 怎么用——这就是 Skills 系统的职责。

### 4.1 Skill 的本质

4.1.1 一个 Skill 本质上就是一个目录，核心文件是 `SKILL.md`：

```java
dingtalk-workspace/
├── SKILL.md                    ← 核心：告诉 AI 怎么使用 DWS
├── references/
│   ├── products/
│   │   ├── aitable.md          ← AI 表格详细命令参考
│   │   ├── calendar.md         ← 日历命令参考
│   │   ├── chat.md             ← 群聊命令参考
│   │   └── ...
│   ├── intent-guide.md         ← 意图路由指南
│   ├── global-reference.md     ← 全局标志和认证说明
│   ├── field-rules.md          ← 字段类型规则
│   └── error-codes.md          ← 错误码和调试流程
└── scripts/
    ├── calendar_today_agenda.py ← 预写的自动化脚本
    ├── todo_daily_summary.py
    ├── mail_send_with_cc.py
    └── ...
```

4.1.2 `SKILL.md` 的 frontmatter 定义了元信息：

```yaml
---
name: dws
description: 管理钉钉产品能力(AI表格/日历/通讯录/文档/...)
cli_version: ">=0.2.14"
---
```

4.1.3 正文包含：意图判断决策树、严格规则约束、核心流程指导、错误处理策略。

### 4.2 启动同步：从 Zip 包到可用技能

4.2.1 悟空 App 的安装包内预置了 7 个 Skill 的 zip 包：

```java
Wukong.app/Contents/Resources/resources/bundled-skills/
├── dingtalk-workspace.zip
├── docx.zip
├── pdf-document-handler.zip
├── pdf_convert_to_word.zip
├── pptx-presentation-handler.zip
├── skill-creator.zip
└── xlsx-spreadsheet-handler.zip
```

4.2.2 App 启动时，后台任务 `setup_background_tasks` 执行同步流程：

```java
Step 1: 扫描 App 包内 bundled-skills/ 目录
            │
Step 2: 逐个解压 zip → ~/.real/.skills/bundled/<skill-name>/
            │
Step 3: 解析 SKILL.md frontmatter（name, description, cli_version）
            │
Step 4: 写入 SQLite 数据库 (~/.real/.skills/skills.db)
        INSERT INTO skills (id, name, source_type, central_path, enabled, ...)
        VALUES ('dingtalk-workspace', 'dws', 'bundled', '~/.real/.skills/bundled/...', 1, ...)
            │
Step 5: 日志输出：
        "[bundled_skills] startup sync completed: 7 skill(s) imported"
```

4.2.3 整个过程是**幂等**的——如果 Skill 已存在且未更新，不会重复导入。

### 4.3 Skills 的四种安装来源

4.3.1 除了内置 Skill，悟空支持从多种来源动态安装：

| 来源 | 命令 | 场景 |
| --- | --- | --- |
| 内置（bundled） | 启动自动同步 | 官方预置的核心技能 |
| URL 远程安装 | `skills install url` | 从 GitHub 等地址下载安装 |
| 本地安装 | `skills install local` | 从本地目录/zip 导入 |
| Agent 跨平台导入 | `skills scan agent` | 从其他 AI Agent 导入技能 |

4.3.2 **URL 安装流程**特别值得一提：

```java
输入 GitHub URL
    │
    ▼
解析下载候选 URL（尝试 main/master 分支）
    │
    ▼
下载 zip → 写入临时目录
    │
    ▼
解压 → 扫描目录中的 SKILL.md
    │
    ├── 单 Skill 仓库 → 直接安装
    │
    └── 集合仓库（如 github.com/anthropics/skills）
        → 自动扫描所有子目录，发现多个 Skill
        → 列出让用户选择安装
    │
    ▼
复制到 central repo (~/.real/.skills/)
    │
    ▼
注册到 SQLite 数据库
```

### 4.4 跨 Agent 技能共享

4.4.1 悟空的一个亮点设计是能识别 **30+ 种 AI Agent** 的技能目录格式：

```java
Claude Code     → ~/.claude/skills
Cursor          → ~/.cursor/skills
Gemini CLI      → ~/.gemini/skills
GitHub Copilot  → ~/.copilot/skills
Windsurf        → ~/.codeium/windsurf/skills
Cline           → ~/.cline/skills
Trae            → ~/.trae/skills
Goose           → ~/.config/goose/skills
Roo Code        → ~/.roo/skills
OpenHands       → ~/.openhands/skills
Wukong 自己     → ~/.real/skills
... 等 30+ 种
```

4.4.2 这意味着：你在 Cursor 中创建的 Skill，悟空可以通过 `skills scan agent` 扫描发现并导入使用。反之亦然。**技能资产跨 Agent 流通，不被单一平台锁定。**

### 4.5 运行时加载：渐进式披露

4.5.1 Skills 不是一次性全部塞进 AI 的上下文窗口（那会浪费大量 Token）。悟空采用**渐进式披露（Progressive Disclosure）**策略：

```java
┌─────────────────────────────────────────────────────┐
│  Level 0: Skill 快照（Snapshot）                     │
│                                                      │
│  启动时生成精简索引，仅包含 id + 一句话描述            │
│  注入到 System Prompt 中                              │
│  Token 消耗：极少                                     │
│                                                      │
│  示例：                                               │
│  "dws - 管理钉钉产品能力(AI表格/日历/通讯录/...)"      │
│  "pptx - PPT 演示文稿创建、编辑"                      │
└──────────────────────┬──────────────────────────────┘
                       │ 用户提问触发意图匹配
                       ▼
┌─────────────────────────────────────────────────────┐
│  Level 1: search_skills（搜索技能）                   │
│                                                      │
│  快照不够用时，搜索完整技能列表                        │
│  返回匹配的 Skill 元信息                              │
└──────────────────────┬──────────────────────────────┘
                       │ 确定使用某个 Skill
                       ▼
┌─────────────────────────────────────────────────────┐
│  Level 2: use_skill(preview)                         │
│                                                      │
│  加载 SKILL.md 的摘要/预览内容                        │
│  Token 消耗：适中                                     │
└──────────────────────┬──────────────────────────────┘
                       │ 预览不够，需要详细参考
                       ▼
┌─────────────────────────────────────────────────────┐
│  Level 3: use_skill(full)                            │
│                                                      │
│  加载 SKILL.md 全文 + references/ 目录下的参考文档     │
│  Token 消耗：较多，但提供完整操作指导                  │
└─────────────────────────────────────────────────────┘
```

4.5.2 这个设计的核心思想是：**上下文窗口是公共资源**。只在需要时才加载详细内容，避免无关 Skill 占据宝贵的 Token 空间。

### 4.6 意图路由：从自然语言到精准命令

4.6.1 当用户输入自然语言时，Skill 中的**意图判断决策树**指导 AI 进行路由：

```java
用户说"表格/多维表/记录/数据"     → dws aitable
用户说"日程/日历/会议室/约会"     → dws calendar
用户说"通讯录/同事/部门"         → dws contact
用户说"法律咨询/法规/案例/判例"   → dws law
用户说"考勤/打卡/排班"           → dws attendance
用户说"审批/OA"                  → dws oa
用户说"帮我做/建/生成 应用"       → dws aiapp
```

4.6.2 同时定义了**易混淆场景**的区分规则：

- `aitable`（数据表格）vs `doc`（文档编辑）
- `drive`（钉盘文件存储）vs `doc`（文档内容读写）
- `report`（日志/日报周报）vs `todo`（待办任务）
- `conference`（视频会议预约）vs `calendar`（日历日程管理）

---

## 5 三层协作：一次完整的调用链路

5.0.1 以用户说"帮我查一下《劳动合同法》第四十七条"为例，完整调用链路如下：

```java
用户输入: "帮我查一下《劳动合同法》第四十七条"
    │
    ▼
① Skill 快照匹配
   关键词"法律" → 命中 dws skill 的意图决策树
   路由到: dws law
    │
    ▼
② use_skill 加载
   读取 dingtalk-workspace/SKILL.md
   获取 law 模块的使用规则:
   - 必须加 --format json
   - 禁止编造参数
    │
    ▼
③ DWS CLI 调用
   dws law search --keyword "劳动合同法 第四十七条" --format json
    │
    ▼
④ MCP 协议通信
   DWS 作为 MCP Client → tools/call → mcp.dingtalk.com
   路由到法律咨询业务模块
    │
    ▼
⑤ 返回结果
   云端返回法条内容 → DWS 格式化输出 → AI 整理回复给用户
```

5.0.2 三层各司其职：**MCP 负责通信，DWS 负责聚合调用，Skill 负责指导 AI 如何正确使用。**

---

## 6 技术亮点总结

### 6.1 动态聚合，无需发版

6.1.1 DWS 的 25+ 个业务模块通过 MCP 协议动态发现，钉钉后端新增能力时，客户端无需更新即可获得新功能。

### 6.2 渐进式加载，节约上下文

6.2.1 Skill 的四级加载策略（快照 → 搜索 → 预览 → 全量），将上下文窗口的利用率最大化。

### 6.3 跨 Agent 互通

6.3.1 兼容 30+ 种 AI Agent 的技能格式，打破平台壁垒，实现技能资产的跨生态流通。

### 6.4 统一入口，双模输出

6.4.1 DWS 既服务于人类（`--format table`），也服务于 AI Agent（`--format json`），一套工具链覆盖两种使用场景。

### 6.5 Rust + Go 混合架构

6.5.1 主程序 `DingTalkReal` 用 Rust 编写（基于 Tauri 框架），负责 UI 渲染、进程管理、Skill 生命周期管理；DWS CLI 用 Go 编写，负责与钉钉 MCP Server 通信。两者各取所长：Rust 保证桌面应用的性能和安全性，Go 提供 CLI 工具的快速开发和跨平台编译能力。

---

## 7 写在最后

7.0.1 悟空的技术架构给 AI Agent 领域带来了一些值得思考的设计范式：

- **不要把能力写死在客户端**——通过 MCP 动态发现，让能力跟着后端演进。
- **不要一次性加载所有上下文**——渐进式披露，按需加载，尊重上下文窗口的有限性。
- **不要让技能锁死在单一平台**——标准化的 Skill 格式，让知识和经验可以跨 Agent 流通。

7.0.2 这些设计选择，或许代表了 AI Agent 工具链的一个演进方向：**从静态编译走向动态聚合，从封闭生态走向开放互通。**

---

*本文基于 Wukong v0.9.2 macOS 版本的逆向分析，部分实现细节可能随版本更新而变化。*
