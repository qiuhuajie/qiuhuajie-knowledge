---
title: "Flyai-skill"
tags:
  - "人工智能"
  - "人工智能/AI Studio"
  - "人工智能/AI Studio/Skills"
  - "Flyai-skill"
  - "Skills"
  - "AI Studio"
updated: 2026-04-16
---
# Flyai-skill
## 核心判断
1. **Agent 会成为新的分发入口，应用要主动把自己的能力暴露给 Agent，现在不占坑就晚了。**
2. 飞猪上线全品类旅行 skill，飞书开源 200+ 命令的 CLI 工具，背后指向同一个趋势。
3. 更值得想清楚的是：MCP、Skill、Terminal CLI 这三条路各自的本质是什么。

## 飞猪 Flyai-skill
1. 飞猪发布的旅行搜索 skill，覆盖机票、酒店、景点、演出、邮轮、签证等全品类。

    ![[IMG-20260405104600227.webp|788]]

2. **flyai-skill 的结构是两层**：一个 SKILL.md 文件 + 一个 flyai-cli。
    * 安装步骤：先把 SKILL.md 拷进 `~/.claude/skills/flyai`，再全局装 `@fly-ai/flyai-cli` 这个 npm 包。
    * 两层分工明确：SKILL.md 负责让 Agent 知道能力存在、什么时候激活；flyai-cli 负责实际执行。
3. **SKILL.md 的触发机制**：定义了触发意图和正则 pattern，比如检测到 "search hotels near West Lake" 或 "find direct flights from Beijing"，skill 就以 priority 90 的优先级激活。

    ![[IMG-20260405104600250.webp|451]]

4. **激活后 Agent 调用四个 CLI 命令**：
    * `fliggy-fast-search`：全品类自然语言搜索
    * `search-flight`：精细化机票查询
    * `search-hotels`：酒店筛选
    * `search-poi`：景点发现
5. 每个命令接受结构化参数，返回 JSON 到 stdout，错误打 stderr。
6. **架构价值在于分层解耦**：Agent 不需要理解 Fliggy 的 API 参数细节，只需要决定调哪条命令、传什么参数。命令层自己处理参数校验、错误格式化、分页和重试。**LLM 做决策，CLI 做执行，两件事分开。**

## 飞书 CLI
1. 飞书 CLI（larksuite/cli）走的是完全相同的路，只是规模更大。
2. 包含 **19 个独立 skill**，对应消息、日历、任务、文档、审批等不同场景；下面是 **200+ 个 CLI 命令**，覆盖飞书全量 OpenAPI。
3. README 里专门说"每条命令经过 Agent 实测验证"，用 Agent 跑每条命令，根据失败案例反过来改参数设计。
4. Quick Start 拆了两个章节，一个给人类，一个给 AI Agent，连认证交互流程都不一样。**这不是包装 API，是重建接口。**

    ![[IMG-20260405104600299.webp|641]]

## MCP Vs Skill Vs CLI 三条路对比
### MCP 的问题：能力发现导致 Context 膨胀
1. MCP 协议本身没问题，**问题出在能力发现机制上**。

    ![[IMG-20260405104600369.webp|719]]

2. 按照 MCP 规范，client 建立连接后立即发送 `list_tools` 请求，server 把所有工具定义一次性返回（包括名称、描述、完整 inputSchema），**全部进入 LLM context，常驻不消失**。
3. 以腾讯云 CODING DevOps MCP server 为例：光 code 模块就有 3 个工具，issue + project 模块再加，总计 11 个工具，`list_commits` 单个工具就有 9 个字段的 inputSchema。11 个工具全量注入 context，**常驻约 3300 tokens**。

    ![[IMG-20260405104600410.webp|636]]

4. 这是协议设计决定的，不是实现不好。企业级服务如果把所有 OpenAPI 都包成 MCP 工具，200+ 接口全量注入，context 直接爆掉。

### Skill 的核心机制：懒加载
1. **Skill 的核心机制是懒加载**：每个 skill 是一个独立文件，只有用户触发对应功能，这个文件才被读入 context。
2. flyai 有 4 个命令，但 context 里只在旅行相关问题出现时才有这份 SKILL.md。
3. 飞书的 19 个 skill 同样如此，发消息用 lark-im，查日历用 lark-calendar，不同时发生，context 里就只有当前需要的那一份。

    ![[IMG-20260405104600460.webp|797]]

### CLI 的作用：执行确定性
1. SKILL.md 里写的是步骤和规则，LLM 读完自己决定怎么做。API 参数怎么填、时间格式用什么、分页怎么处理，靠 LLM 理解。**理解偏了，调用就失败了。**
2. **这就是为什么飞猪和飞书都在 Skill 下面接了 CLI：把不确定的执行层变成确定性的 bash 调用。**

### 三条路的本质分工
1. ==MCP 做协议标准化，Skill 做能力发现，CLI 做执行确定性。==
2. 飞猪和飞书选的是 Skill + CLI，腾讯云选的是纯 MCP。选哪条取决于约束，不是非此即彼：
    * 如果工具要在多个 Agent 平台上跑 → **MCP 兼容性最好**
    * 如果工具数量多、需要按需激活 → **Skill 懒加载更合适**
    * 如果要保证执行准确率 → **CLI 是执行层的正确答案**
3. 纯 MCP 的解法是控制工具数量在 10 个以内，或者按场景拆多个轻量 server，而不是把所有能力全注册进去。

## 参考链接
* GitHub: [flyai-skill](https://github.com/alibaba-flyai/flyai-skill)
* GitHub: [larksuite/cli](https://github.com/larksuite/cli)
* GitHub: [TencentCloudCommunity/mcp-server](https://github.com/TencentCloudCommunity/mcp-server)