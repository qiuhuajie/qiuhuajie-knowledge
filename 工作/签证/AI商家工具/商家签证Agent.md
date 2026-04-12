# 商家签证售前 Agent 技术方案

## 修订记录

- **v2**：引入 ReAct 模式 + 动态决策树，替代静态阶段流转，支持用户任意顺序回答
- **v3**：Skill 实现升级为 MCP + Prompt 混合架构；知识库升级为结构化召回 + RAG 双层混合召回

---

## 一、Agent 定位与目标

**角色**：商家专属的签证售前咨询顾问

**核心价值**：通过多轮对话精准澄清用户办签诉求，推荐最适合的签证套餐与材料清单，并引导用户下单。

**架构模式**：ReAct（Reasoning + Acting）循环 + 澄清决策树，由单一 Agent 驱动全程。

---

## 二、核心架构：ReAct 循环

### 2.1 ReAct 循环原理

```java
┌─────────────────────────────────────────────────────────────┐
│                        ReAct 循环                            │
│                                                             │
│   ┌─────────┐    ┌────────────┐    ┌──────────┐            │
│   │ Observe │ →  │  Reason    │ →  │  Act     │ ───┐       │
│   │ (用户输入)│    │ (决策树推理) │    │ (调用工具/追问)│      │       │
│   └─────────┘    └────────────┘    └──────────┘    │       │
│                                                     │       │
│                              ┌──────────────────────┘       │
│                              │  循环直到 phase=recommending  │
└─────────────────────────────────────────────────────────────┘
```

每个循环包含三个步骤：

1. **Observe**：解析用户输入，提取所有已知字段，更新 `session_state`
2. **Reason**：运行决策树，判断"当前最需要澄清的字段是什么"
3. **Act**：执行对应动作（追问 / 调用工具 / 给出推荐）

### 2.2 决策树：澄清优先级引擎

决策树是 ReAct 中 `Reason` 步骤的核心，负责回答一个问题：

> **"基于当前已知的字段，下一步应该做什么？"**

#### 决策节点定义

```java
resolve_next_action(state) → Action

Action 类型：
  - ask(field)          # 追问某个字段
  - clarify(field)      # 请用户澄清某个已提供但模糊的字段
  - match()              # 调用工具链，生成推荐
  - confirm(field)       # 确认用户已提供的某个字段
  - done()               # 所有必填字段已齐，进入完成态
```

#### 决策规则表

| 当前 state.known_fields | 优先级 | 触发 Action |
|---|---|---|
| country == null | P0（最高） | ask("country") |
| country != null AND visa_type == null | P1 | ask("visa_type") |
| country != null AND visa_type != null AND residence_city == null | P2 | ask("residence_city") |
| country != null AND visa_type != null AND residence_city != null AND consulate == null | P2.5 | match_consulate(country, residence_city) → 自动推进 |
| country != null AND visa_type != null AND consulate != null AND occupation == null | P3 | ask("occupation") |
| country != null AND visa_type != null AND consulate != null AND occupation != null AND departure_date == null | P4 | ask("departure_date") |
| country != null AND visa_type != null AND consulate != null AND occupation != null AND departure_date != null AND traveler_count == null | P5 | ask("traveler_count") |
| 所有必填字段已齐 | — | match() → 进入推荐阶段 |

#### 决策伪代码

```java
function resolve_next_action(state):
    if state.country is null:              return ask("country")
    if state.visa_type is null:            return ask("visa_type")
    if state.residence_city is null:       return ask("residence_city")

    # 尝试自动匹配领区（不需要用户主动回答）
    if state.consulate is null:
        return match_consulate(state.country, state.residence_city)

    if state.occupation is null:           return ask("occupation")
    if state.departure_date is null:       return ask("departure_date")

    # 可选字段，根据业务策略决定是否追问
    if state.traveler_count is null AND state.ask_traveler_count:
        return ask("traveler_count")

    # 到达此处：所有必填字段已齐
    return match()
```

#### 模糊字段二次澄清规则

用户可能给出模糊回答，Agent 需要主动澄清：

| 场景 | 用户回答 | Agent 追问 |
|---|---|---|
| 国家模糊 | "欧洲" | "欧洲有很多国家，请问您具体想办哪个国家的签证呢？" |
| 签证类型模糊 | "出去玩" | "您是指出国旅游对吗？还是有商务出差或其他出行目的？" |
| 城市模糊 | "上海周边" | "请问您的常住城市是上海吗？" |
| 日期模糊 | "下个月" | "请问您具体计划几号出发呢？我好帮您算一下办理时间够不够。" |
| 职业模糊 | "上班的" | "是在公司/单位上班对吗？是正式在职员工吗？" |

---

## 三、Session State 设计

```typescript
interface VisaPreSaleState {
  // 上下文
  seller_id: string;
  conversation_id: string;
  created_at: string;

  // 已澄清的字段（用户已明确提供）
  country: CountryInfo | null;       // { code, name }
  visa_type: VisaTypeInfo | null;     // { code, name }
  residence_city: string | null;      // "上海市"
  consulate: ConsulateInfo | null;    // { code, name, jurisdiction }
  occupation: OccupationType | null; // "EMPLOYED" | "SELF_EMPLOYED" | "STUDENT" | "RETIRED" | "UNEMPLOYED"
  departure_date: string | null;      // "2026-05-01"
  return_date: string | null;          // "2026-05-10"
  traveler_count: number | null;
  special_needs: SpecialNeed[];       // ["EXPEDITE", "VIP", "SELF_PICKUP"]

  // 辅助状态
  known_fields: string[];             // 已明确的字段名列表
  pending_fields: string[];           // 待澄清的字段名列表
  ambiguous_fields: string[];         // 需要二次澄清的字段

  // 流程控制
  phase: "CLARIFYING" | "RECOMMENDING" | "CLOSING";
  last_action: Action;
  last_tool_calls: ToolCall[];
  attempts: number;                   // 当前字段的追问次数（防死循环）
}

// OccupationType 枚举
type OccupationType =
  | "EMPLOYED"          // 在职
  | "SELF_EMPLOYED"     // 自由职业
  | "STUDENT"           // 学生
  | "RETIRED"           // 退休
  | "UNEMPLOYED";       // 无业/家庭主妇
```

---

## 四、工具（Tools）设计

### 4.1 MCP 工具：签证标准库

> **接入方式**：通过 MCP Server 接入，Agent 通过 `mcp__visa__*` 工具调用。
> **双重召回**：每个 MCP 工具的调用方（Skill 协调层）先做语义路由，决定是走结构化筛选还是语义召回。

| 工具名                           | 功能         | 入参                             | 召回策略                          |
| ----------------------------- | ---------- | ------------------------------ | ----------------------------- |
| `mcp__visa__get_countries`    | 获取支持国家列表   | `continent?`                   | 结构化筛选（按大洲过滤）+ 语义召回（按国家名/概念匹配） |
| `mcp__visa__get_visa_types`   | 获取某国签证类型列表 | `country_code`                 | 结构化查询（按国家查类型列表）               |
| `mcp__visa__get_consulates`   | 获取某国领区列表   | `country_code`                 | 结构化查询                         |
| `mcp__visa__match_consulate`  | 常住地匹配送签领区  | `country_code, residence_city` | 精确匹配（城市 → 领区映射）               |
| `mcp__visa__get_process_flow` | 获取签证办理标准流程 | `country_code, visa_type_code` | 结构化查询                         |
|                               |            |                                |                               |

### 4.2 API 工具：商品与套餐

> **商品维度**：`sellerId + countryCode + visaTypeCode + consulateCode` 确定一个商品，每个商品下挂多个套餐。
> **Agent 筛选**：套餐数量少（通常 3～10 个），全量返回，由 Agent 根据用户需求筛选并推荐。

| 工具名                       | 功能         | 入参                                                        | 出参                                                           |
| ------------------------- | ---------- | --------------------------------------------------------- | ------------------------------------------------------------ |
| `get_product`             | 获取商品（套餐集合） | `seller_id, country_code, visa_type_code, consulate_code` | `{product_id, product_name, packages: [...]}`                |
| `get_packages_by_product` | 获取商品下的所有套餐 | `product_id`                                              | `[{package_id, name, price, duration_days, features, tags}]` |

### 4.3 MCP 工具：FAI 知识库

> **接入方式**：通过 MCP Server 接入 FAI 平台知识库，所有商家知识召回走此 MCP。
> **召回策略**：结构化结果优先，若结构化无命中则返回 RAG 检索结果。

| 工具名 | 功能 | 入参 | 出参 |
|---|---|---|---|
| `mcp__fai__retrieve_knowledge` | 商家知识库混合召回 | `seller_id, query, country_code?, visa_type_code?, occupation?` | `{structured_results: [...], rag_results: [...], total: n}` |

**返回结果结构**：

```json
{
  "structured_results": [
    {
      "type": "MATERIAL_REQUIREMENTS",
      "data": { "materials": [...] },
      "score": 0.95
    }
  ],
  "rag_results": [
    {
      "chunk_text": "日本旅游注意事项：...",
      "source": "日本签证须知.pdf",
      "score": 0.88
    }
  ],
  "total": 5
}
```

> **优先级规则**：结构化结果（`structured_results`）永远优先于 RAG 结果（`rag_results`）。Agent 优先使用结构化材料清单，RAG 结果作为补充说明参考。

### 4.4 内置 Skill 工具（Agent 内部执行）

| 工具名 | 类型 | 功能 | 触发时机 |
|---|---|---|---|
| `resolve_visa_type(user_text, country_code?)` | Prompt 层 | 将口语映射为签证类型 code | 用户回答出行目的时 |
| `resolve_occupation(user_text)` | Prompt 层 | 将口语映射为职业类型 | 用户回答职业时 |
| `detect_ambiguity(user_text, field)` | Prompt 层 | 判断回答是否模糊需澄清 | Observe 步骤 |
| `generate_ask_script(field, attempts)` | Prompt 层 | 生成追问话术 | Act = ask 时 |
| `calculate_timeline(departure_date, duration_days)` | 内置 | 计算时间余量 | 推荐阶段 |
| `format_recommendation(...)` | 内置 | 格式化推荐卡片 | 推荐阶段 |

---

## 五、ReAct Agent 主循环实现

```java
LOOP (ReAct Cycle):

  1. OBSERVE
     ├─ 解析用户输入，提取所有字段
     ├─ 对模糊字段调用 resolve_occupation / resolve_visa_type 做意图解析
     ├─ 若解析置信度低 → clarify(field)
     ├─ 更新 session_state.known_fields
     └─ 若发现新字段 → 立即确认（confirm）

  2. REASON
     ├─ 运行 resolve_next_action(session_state)
     ├─ 判断是追问、澄清、自动匹配还是生成推荐
     └─ 输出 next_action

  3. ACT
     ├─ ask(field):
     │    ├─ 生成针对该字段的个性化追问
     │    ├─ 若该字段之前已问过但用户回避 → 换一种问法
     │    └─ 记录 attempts += 1
     │
     ├─ match_consulate(...):
     │    ├─ 调用 mcp__visa__match_consulate
     │    ├─ 若匹配送签地成功 → 更新 state.consulate
     │    └─ 继续循环（继续 Reason）
     │
     ├─ match():
     │    ├─ 步骤1：调用 get_product，获取商品及套餐列表
     │    │         sellerId + countryCode + visaTypeCode + consulateCode
     │    ├─ 步骤2：并行调用
     │    │    ├─ mcp__fai__retrieve_knowledge（材料清单，FAI MCP）
     │    │    └─ calculate_timeline（办理时间余量）
     │    ├─ 步骤3：Agent 根据用户需求筛选套餐（Top 2～3）
     │    ├─ 聚合结果，调用 format_recommendation 生成推荐
     │    ├─ 更新 phase = "RECOMMENDING"
     │    └─ 输出推荐卡片 + 引导下单
     │
     └─ confirm(field):
          ├─ "您是说您要办理【XX国】的【旅游】签证，对吗？"
          └─ 等待用户确认后继续循环
```

---

## 六、System Prompt 完整设计

```markdown
# 角色定义

你是一名专业、耐心、友善的签证售前咨询顾问，服务于商家用户。你的唯一目标是：
**通过多轮对话精准澄清用户的办签需求，推荐最适合的签证套餐与材料清单，并引导用户完成下单。**

## 核心原则

1. **每次只做一件事**：每轮对话最多追问 1 个字段，不要一次性问多个问题
2. **用户是主角**：等待用户回答，不催促，不假设
3. **模糊即追问**：用户回答模糊时，先确认再推进，不主观臆断
4. **诚实告知边界**：不支持的国家/签证类型，直接告知并建议转人工
5. **以办成签证为目标**：不是推销套餐，而是帮助用户找到最合适的那一款

## 字段澄清优先级（决策规则）

按以下顺序推进，每步仅处理当前最优先缺失的字段：

P0 → 目的地国家（最重要）
P1 → 签证类型（旅游/商务/探亲/留学等）
P2 → 常住地（用于匹配送签领区，由系统自动匹配）
P3 → 职业身份（在办理材料时必须区分）
P4 → 出行日期（判断办理时间是否充裕）
P5 → 同行人数（可选，影响是否需要单独操作）

> 注意：配送签地（领区）由系统根据常住地自动匹配，不需要用户主动告知。

## Skill 协作规则

每个字段的澄清，由 **Prompt 层 + MCP 层** 协作完成：

### 国家匹配（country_match）

当用户提到目的地时，根据表述类型决定召回策略：

- **洲名**（"欧洲"、"东南亚"、"美洲"）→ MCP `mcp__visa__get_countries` + `continent` 筛选 → 展示该洲国家列表
- **概念**（"申根"、"欧盟"、"发达国家"）→ 语义召回 → 展示匹配的国家列表
- **具体国家**（"日本"、"美国"）→ MCP 精确匹配 → 置信度 1.0，直接确认

### 签证类型匹配（visa_type_match）

1. Prompt 层解析口语 → 签证类型候选列表
2. 若已确定国家 → 调用 MCP `mcp__visa__get_visa_types` 获取该国签证类型
3. 语义匹配用户口语与签证类型列表
4. 置信度 ≥ 0.8 → 直接确认；< 0.8 → 展示签证类型列表请用户选择

### 领区匹配（residence_match）

- 用户提供常住城市 → Prompt 层标准化城市名（"魔都"→"上海市"）
- MCP `mcp__visa__match_consulate` 精确匹配城市 → 返回领区
- 无匹配 → 提示用户可能的替代领区

### 职业解析（occupation_match）

纯 Prompt 层，依赖内部映射表：
- "上班族"/"打工"/"正式员工" → EMPLOYED
- "自由职业"/"个体户"/"SOHO" → SELF_EMPLOYED
- "学生"/"在读" → STUDENT
- "退休" → RETIRED
- "无业"/"家庭主妇" → UNEMPLOYED

置信度 < 1.0 时追问确认。

### 模糊检测（detect_ambiguity）

| 触发场景 | Agent 行为 |
|---|---|
| 用户说"欧洲"、"东南亚" | 展示国家列表 |
| 用户说"出去玩" | 展示签证类型列表 |
| 用户说"尽快出发" | 追问具体日期 |

## 推荐输出格式（phase = RECOMMENDING 时使用）

推荐卡片格式如下：

---
**为您推荐**

- **目的地**：[国家]
- **签证类型**：[类型]
- **送签领区**：[城市]领区
- **推荐套餐**：[套餐名]  价格：[X元]  预计[X]个工作日
- **办理余量**：距出行还有 **X 天**，时间[X充裕/紧张]，建议[X正常办理/加急]
- **所需材料**：
  - [基础材料]（所有人必须提供）
  - [在职材料]（在职人员需额外提供）
  - [资产材料]（在职/自由职业需提供）
  - （[敏感材料] 如需额外准备另行告知）

> ⚠️ 材料仅供参考，具体以商家最终要求为准。

---

**下一步**：如需办理，请点击「立即下单」，或告诉我您还有任何疑问。
---

## 结束语风格

- 推荐完成后：根据用户反馈决定是结束还是继续解答疑问
- 用户确认下单后：感谢信任，告知后续流程（准备材料、邮寄等）
- 用户明确不需要：感谢咨询，欢迎随时回来，保持友好
- 无法满足需求时：「非常抱歉，[XX]类型的签证目前暂不支持办理，建议您联系人工客服获取更详细的帮助。祝您出行顺利！」

## 商家上下文

- sellerId：[由调用方在会话初始化时注入]
- 商家名称：[由调用方注入]
- 商家特色服务：[由调用方注入，用于个性化推荐话术]
```

---

## 七、Skill 架构：MCP + Prompt 混合模式

> **设计原则**：每个 Skill 不是单纯的 Prompt 规则，也不是单纯的 MCP 工具调用，而是**两层协作**：
> - **Prompt 层（决策/理解）**：负责语义理解、意图判断、话术生成
> - **MCP 层（召回/查询）**：负责结构化数据的精确查询和语义相似度召回

### 7.1 Skill 分层总览

```java
┌─────────────────────────────────────────────────────────────┐
│                     Agent / Skill                           │
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  Prompt层   │ ←→ │  Skill协调层  │ ←→ │   MCP层       │  │
│  │  (理解/决策) │    │  (路由/组合)  │    │  (结构化召回)  │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         ↑                  ↑                   ↑            │
│         │                  │                   │            │
│    System Prompt      业务规则路由          签证标准库       │
│    + 对话上下文       + 召回策略组合         MCP Server      │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Skill 1：`country_match` — 国家匹配

**职责**：将用户对目的地的模糊描述，转化为具体的国家代码。

**协作流程**：

```java
用户："我想去欧洲" 或 "申根" 或 "日本"
   │
   ▼
┌────────────────────────────────────────────┐
│         Prompt层：意图分析                  │
│  判断是：洲名/区域/申根概念/具体国家        │
└────────────────────────────────────────────┘
   │
   ├─── "洲名"（"欧洲"、"东南亚"、"美洲"）
   │    │
   │    ▼ MCP：结构化筛选
   │    mcp__visa__get_countries → filter(continent = 'EUROPE')
   │    │
   │    ▼ 展示国家列表请用户选择
   │
   ├─── "申根"/"欧盟" 等概念
   │    │
   │    ▼ MCP：语义召回
   │    semantic_search("申根国家") → 匹配候选列表
   │    │
   │    ▼ 展示申根国列表请用户选择
   │
   └─── 具体国家（"日本"、"美国"）
        │
        ▼ MCP：精确匹配
        mcp__visa__get_countries → exact_match(name)
        │
        ▼ 置信度 1.0，直接确认并推进
```

**MCP 工具**：`mcp__visa__get_countries`（结构化筛选 + 语义召回）

**Prompt 层职责**：判断用户意图类型（洲名/概念/具体），决定走哪条召回路径

**对话示例**：

- 用户："想去欧洲"
  - Agent："欧洲有很多热门签证国家，请问您具体想去哪一个呢？"
  - Agent：[展示欧洲国家列表：法国、德国、意大利、瑞士...]

- 用户："申根怎么办"
  - Agent："好的，申根签证可以通行 27 个欧洲国家，请问您最想去哪个呢？"
  - Agent：[展示申根国家列表]

---

### Skill 2：`visa_type_match` — 签证类型匹配

**职责**：将用户出行目的的口语化描述，转化为该国家下的标准签证类型。

**协作流程**：

```java
用户："出去玩"、"出差"、"看孩子"
   │
   ▼
┌────────────────────────────────────────────┐
│         Prompt层：意图解析                  │
│  提取关键词，生成签证类型候选              │
└────────────────────────────────────────────┘
   │
   ▼ MCP：结构化查询（前提：已确定 country）
   mcp__visa__get_visa_types(country_code)
   │
   ▼ MCP：语义召回（签证类型列表内匹配）
   semantic_search(user_text, visa_types)
   │
   ▼ 输出候选签证类型（置信度排序）
   - { code: "TOURISM", name: "旅游签证", score: 0.92 }
   - { code: "FAMILY_VISIT", name: "探亲签证", score: 0.71 }
```

**若 score ≥ 0.8**：直接确认（"您是去旅游对吗？"）

**若 score < 0.8**：展示该国家支持的签证类型列表请用户选择

**若用户已确定国家** → 直接查该国签证类型列表

**若用户未确定国家** → 等待国家确认后再查（避免展示不相关类型）

**MCP 工具**：`mcp__visa__get_visa_types`

**Prompt 层职责**：口语到签证类型 code 的语义映射（见下方映射表）

**口语→签证类型映射表**：

| 用户口语 | 解析结果 | 置信度说明 |
|---|---|---|
| "旅游"、"出去玩"、"度假"、"旅行" | TOURISM | 精确匹配 |
| "商务"、"出差"、"公干"、"开会" | BUSINESS | 精确匹配 |
| "探亲"、"看家人"、"访友" | FAMILY_VISIT | 精确匹配 |
| "留学"、"读书"、"学习" | STUDY | 精确匹配 |
| "工作"、"务工"、"就业" | WORK | 精确匹配 |
| "移民"、"永居" | IMMIGRATION | 精确匹配 |
| "过境"、"转机" | TRANSIT | 精确匹配 |
| "参加会议" | BUSINESS | 模糊推断，需确认 |
| "陪孩子/配偶出国" | FAMILY_VISIT | 模糊推断，需确认 |

---

### Skill 3：`residence_match` — 常住地匹配送签地

**职责**：将用户提供的常住城市，匹配送签领区。

**协作流程**：

```java
用户："我在上海"、"常住北京"
   │
   ▼
┌────────────────────────────────────────────┐
│         Prompt层：城市名标准化              │
│  "魔都" → "上海市" / "帝都" → "北京市"     │
└────────────────────────────────────────────┘
   │
   ▼ MCP：精确匹配
   mcp__visa__match_consulate(country_code, "上海市")
   │
   ├─── 匹配成功 → 更新 state.consulate
   │    "根据您的常住地，系统自动为您匹配【上海领区】"
   │
   └─── 匹配失败（城市不在管辖范围）
        → 提示用户："上海领区目前不受理 XX 国签证，
           您可能需要通过【广州领区】送签，请问您的
           户籍或居住证是在哪个城市？"
```

**注意**：此 Skill 全程由 MCP 主导（精确查询），Prompt 层仅负责城市名方言化（如"魔都"→"上海市"）的预处理。

---

### Skill 4：`occupation_match` — 职业身份解析

**职责**：将用户职业描述，映射为标准职业类型（影响材料清单）。

**协作流程**：纯 Prompt 层技能（无外部查询），内部维护口语→职业类型映射表。

**口语→职业类型映射表**：

| 用户口语 | 解析结果 | 置信度 |
|---|---|---|
| "上班族"、"打工"、"正式员工"、"在公司" | EMPLOYED | 1.0 |
| "自由职业"、"自己干"、"个体户"、"SOHO" | SELF_EMPLOYED | 1.0 |
| "学生"、"在读"、"大学生"、"研究生" | STUDENT | 1.0 |
| "退休"、"已退休"、"退休人员" | RETIRED | 1.0 |
| "无业"、"待业"、"家庭主妇"、"家庭主夫" | UNEMPLOYED | 1.0 |
| "公务员"、"事业单位" | EMPLOYED | 1.0（归入在职） |
| "老板"、"企业主" | SELF_EMPLOYED | 1.0（归入自由职业） |

**Prompt 层职责**：完全由 System Prompt 中的规则表处理，无需 MCP 调用。

**输出**：`{ type: OccupationType, confirmed: boolean }`

**若 confirmed = false**：Agent 追问确认（"您是公司正式员工对吗？"）

---

### Skill 5：`ask_field` — 字段追问话术生成

**职责**：根据当前缺失字段，从候选列表中选取最适合的追问话术。

**协作流程**：纯 Prompt 层技能，依赖对话历史决定话术风格。

**话术策略**：

| 字段 | 首轮问法 | 回避后换法（第2次） | 回避后再换（第3次） |
|---|---|---|---|
| country | "请问您要办理哪个国家的签证呢？" | "您想去哪个国家，我帮您看看？" | "您可以说国家名，比如日本、美国..." |
| visa_type | "您这次出行是旅游、商务还是探亲呢？" | "您的出行目的是什么呢？" | "方便告诉我您出国的原因吗？" |
| residence_city | "请问您的常住城市是哪里呢？" | "您在哪个城市生活？" | "您的户口或居住证是在哪个城市？" |
| occupation | "请问您的职业身份是？" | "您是在职、自由职业还是学生呢？" | "您目前有正式工作吗？" |
| departure_date | "您计划什么时候出行呢？" | "大概几月份出发？" | "出行日期方便告诉我吗？" |

**话术选取规则**：

- `attempts = 0` → 使用首轮问法
- `attempts = 1` → 使用第2种问法（换一种表达方式）
- `attempts ≥ 2` → 使用第3种问法（更具体，降低理解门槛）

---

### Skill 6：`detect_ambiguity` — 模糊意图检测

**职责**：在 Observe 步骤中检测用户回答是否模糊，触发澄清流程。

**协作流程**：Prompt 层判断 + 必要时调用 MCP 辅助召回。

| 检测场景 | 触发条件 | Agent 行为 |
|---|---|---|
| 国家概念模糊 | 回答含洲名/区域/泛概念（"欧洲"、"申根"、"亚洲"） | 调用 `country_match` 召回候选列表，展示给用户 |
| 签证类型模糊 | 回答含"出去"、"出国"等泛指 | 调用 `visa_type_match` 召回候选类型，展示给用户 |
| 城市模糊 | 回答含"周边"、"华东"、"我家在..." | Prompt 标准化城市名，追问确认 |
| 日期模糊 | 回答含"最近"、"尽快"、"下个月" | 追问具体日期 |
| 职业模糊 | 含糊回答 | 调用 `occupation_match` 解析并追问确认 |

---

## 八、对话状态流转图

```java
用户输入
  │
  ▼
┌─────────────────────────────────┐
│         OBSERVE 步骤            │
│  提取字段 + 意图解析 + 状态更新  │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│         REASON 步骤             │
│    运行决策树 resolve_next_action │
│    输出：next_action             │
└─────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│          ACT 步骤               │
│  ask / clarify / match / done  │
└─────────────────────────────────┘
  │                                    ▲
  │         循环继续                    │
  └────────────── REACT 循环 ──────────┘

  当 next_action = match() 时：
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤1：get_product                                         │
│  sellerId + countryCode + visaTypeCode + consulateCode    │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤2：并行调用（商品已确定后）                              │
│  ├─ mcp__fai__retrieve_knowledge（材料，FAI MCP）           │
│  └─ calculate_timeline（办理时间余量）                       │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│  步骤3：Agent 筛选套餐（Top 2～3）+ 聚合所有结果             │
│  format_recommendation → 推荐卡片                            │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
  phase = "RECOMMENDING"
  │
  ▼
┌─────────────────────────────────────────┐
│           输出推荐卡片                   │
│  + 引导下单 / 解答疑问                   │
└─────────────────────────────────────────┘
```

---

## 九、知识库架构：FAI 知识库 MCP 接入

> **接入方式**：商家知识统一通过 FAI 平台 MCP 接入，所有召回调用 `mcp__fai__retrieve_knowledge`。
> **召回优先级**：结构化结果 > RAG 结果。Agent 优先使用结构化材料清单，RAG 结果作为补充说明。

### 9.1 召回流程

```java
用户查询（如："日本旅游需要什么材料"）
   │
   ▼
┌─────────────────────────────────────────────────────────┐
│         mcp__fai__retrieve_knowledge                    │
│  seller_id + query + (country_code/visa_type/occupation)│
└─────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────┐
│              FAI 平台内部处理                            │
│  结构化数据语义召回 + RAG 向量检索                      │
│  → 返回 { structured_results, rag_results }           │
└─────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────┐
│              Agent 结果聚合                             │
│                                                         │
│  1. structured_results（非空）→ 直接作为材料清单使用   │
│  2. rag_results → 作为补充说明参考                     │
│  3. 两者均空 → 使用平台通用材料清单，注明以商家为准    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 9.2 知识库来源分层

| 来源 | 存储位置 | 召回方式 | 优先级 |
|---|---|---|---|
| 商家结构化材料配置（表格录入） | FAI 结构化知识库 | 语义召回 + 精确过滤 | 最高 |
| 商家上传文档（PDF/Word/TXT） | FAI RAG 向量库 | 语义向量检索 | 次高 |
| 平台通用材料清单 | FAI 结构化知识库 | 兜底召回 | 保底 |

### 9.3 商品维度设计

> **商品 = sellerId + countryCode + visaTypeCode + consulateCode**
> 一个商品对应多个套餐，Agent 获取商品后根据用户需求（价格、时效、加急等）做筛选推荐。

```java
商品结构：
{
  product_id: "PROD_XXX",
  seller_id: "SELLER_XXX",
  country_code: "JP",
  visa_type_code: "TOURISM",
  consulate_code: "SH",
  product_name: "日本单次旅游签证-上海领区",
  packages: [
    { package_id: "PKG_001", name: "基础套餐", price: 299, duration_days: 10, features: [...] },
    { package_id: "PKG_002", name: "优选套餐", price: 499, duration_days: 8, features: [...] },
    { package_id: "PKG_003", name: "尊享套餐", price: 799, duration_days: 5, features: [...] },
  ]
}
```

**Agent 推荐策略**：

- 用户无特殊要求 → 推荐性价比最高（价格适中、时效合理）
- 用户赶时间 → 推荐时效最短
- 用户预算优先 → 推荐价格最低
- 不替用户做绝对判断 → 列出 Top 2～3 套餐并说明差异，由用户选择

### 9.4 商家自设流程（可选）

若商家有特殊流程或话术要求，可通过配置注入到 System Prompt：

```json
{
  "seller_id": "xxx",
  "seller_name": "XX签证专营店",
  "custom_scripts": {
    "greeting": "欢迎来到XX签证！我是您的专属签证顾问，请问有什么可以帮您？",
    "closing": "感谢选择XX签证，我们承诺全程透明、无隐形消费！"
  },
  "supported_countries": ["JP", "KR", "US", "GB"],
  "special_notes": "日本签证目前广州领区办理较慢，建议提前15天咨询"
}
```

---

## 十、异常处理机制

| 场景            | Agent 响应策略                                |
| ------------- | ----------------------------------------- |
| 用户回答超出系统能力    | 「抱歉，[XX]目前暂不支持线上咨询办理，建议您联系人工客服。」          |
| 多次追问同一字段（≥3次） | 换一种问法；若第3次仍回避，降低优先级，后续再择机追问               |
| 出行时间已过        | 「您的出行日期已过，请问是计划改期吗？」                      |
| 出行时间太近，无法办理   | 「按您的出行时间，目前办理时间较为紧张，建议您选择加急服务，或考虑调整出行计划。」 |
| 商家无匹配套餐       | 「目前商家暂未上线该国家的签证套餐，我帮您记录了需求，稍后由客服为您跟进。」    |
| 材料知识库缺失该组合    | 使用平台通用材料清单，注明「具体材料要求以商家审核为准」              |
| 用户表达不满/投诉倾向   | 立即转人工，停止自动回复：「我帮您转接人工客服，请稍等。」             |

---

## 十一、技术实现要点

### 11.1 ReAct 循环实现

```python
# 伪代码：ReAct 主循环

def run_react_loop(user_input: str, state: VisaPreSaleState) -> str:
    while True:
        # 1. OBSERVE：解析用户输入，更新状态
        extracted = extract_fields(user_input, state)
        state.update(extracted)

        # 2. REASON：根据决策树决定下一步
        action = resolve_next_action(state)

        # 3. ACT：根据 action 执行
        if action.type == "ask":
            return generate_ask(action.field, state, action.attempts)

        elif action.type == "clarify":
            return generate_clarify(action.field, extracted)

        elif action.type == "match_consulate":
            result = mcp__visa__match_consulate(state.country.code, state.residence_city)
            state.consulate = result
            continue  # 继续循环，不需要回复用户

        elif action.type == "match":
            # 调用工具链，生成推荐
            packages = get_visa_packages(state)
            materials = get_material_requirements(state)
            timeline = calculate_timeline(state)
            state.phase = "RECOMMENDING"
            return format_recommendation(packages, materials, timeline, state)

        elif action.type == "done":
            return generate_closing(state)
```

### 11.2 MCP Server 部署建议

```java
MCP Server（签证标准库）
├── 数据来源：签证数据中心（MySQL / PostgreSQL）
├── 部署方式：FastMCP / 其他 MCP SDK
├── 接口协议：MCP JSON-RPC 2.0
└── 访问控制：内网 API Key 鉴权
```

### 11.3 会话上下文注入

```java
会话初始化时，调用方需注入：
{
  seller_id: "SELLER_XXX",
  seller_name: "XX签证专营店",
  seller_config: { ... },  // 商家自定义配置
  conversation_id: "xxx",
}
```

---

## 十二、后续迭代方向

- **材料预审 Skill**：用户上传材料后，Agent 调用 OCR + 规则引擎做初步材料检查
- **进度查询 Phase**：下单后 Agent 化身办理进度查询助手，切换 System Prompt
- **多语言 Skill**：支持英文、日文输出（针对使领馆要求）
- **FAI 知识库深化**：商家上传非结构化文档（使领馆公告、FAQ）持续丰富 FAI RAG 库
- **Agent 自学习**：收集用户对推荐结果的反馈（是否下单、是否满意），优化套餐筛选策略
- **多商品对比**：当同一国家有多个商家时，支持跨商家比价推荐（需扩展 sellerId 范围）