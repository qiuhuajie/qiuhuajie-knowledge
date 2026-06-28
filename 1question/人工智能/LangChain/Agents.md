---
title: "Agents"
tags:
  - "人工智能"
  - "人工智能/AI Studio"
  - "人工智能/AI Studio/Coding"
  - "Agents"
  - "LangChain"
  - "AI Studio"
updated: 2026-04-16
aliases:
  - LangChain Agents
---
# 一、核心组件
## 1. Model
* [模型](https://docs.langchain.com/oss/python/langchain/models) 是 agent 的推理引擎。它可以通过多种方式指定，既支持静态模型选择，也支持动态模型选择。

### 1.1 静态模型
1. 静态模型会在创建 agent 时一次性配置，并在整个执行过程中保持不变。这是最常见也最直接的方式。要从如下方式初始化一个静态模型：
	```python
	from langchain.agents import create_agent
	agent = create_agent("openai:gpt-5", tools=tools)
	```
	* 模型标识符字符串支持自动推断，例如 "gpt-5" 会被推断为 "openai:gpt-5"。完整的模型标识符映射列表可参见 [reference](https://reference.langchain.com/python/langchain/chat_models/base/init_chat_model)。
	* [`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) 提供了一个可用于生产环境的 agent 实现。
	* [`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) 会基于 [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) 构建一个基于图（graph）的 agent 运行时。图由节点（步骤）和边（连接）组成，用于定义 agent 如何处理信息。Agent 会在这张图中移动，执行诸如模型节点（调用模型）、工具节点（执行工具）或中间件等节点。更多信息可参见 [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)。
2. 如果希望更精细地控制模型配置，可以直接使用 provider 包初始化模型实例。下面的例子使用的是 [ChatOpenAI](https://reference.langchain.com/python/langchain-openai/chat_models/base/ChatOpenAI)。其他可用的聊天模型类见 [Chat models](https://docs.langchain.com/oss/python/integrations/chat)。
	```python
	from langchain.agents import create_agent
	from langchain_openai import ChatOpenAI
	model = ChatOpenAI(
	    model="gpt-5",
	    temperature=0.1,
	    max_tokens=1000,
	    timeout=30
	    # ... (other params)
	)
	agent = create_agent(model, tools=tools)
	```
> [!info]
> 更多可用参数和方法请参考 [reference](https://docs.langchain.com/oss/python/integrations/providers/all_providers)。

### 2.2 动态模型
1. 动态模型会根据当前状态和上下文在运行时进行选择。
2. 要使用动态模型，可以借助 [`@wrap_model_call`](https://reference.langchain.com/python/langchain/agents/middleware/types/wrap_model_call) 装饰器创建 `middleware`，在请求中修改模型：
	```python
	from langchain_openai import ChatOpenAI
	from langchain.agents import create_agent
	from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
	basic_model = ChatOpenAI(model="gpt-4.1-mini")
	advanced_model = ChatOpenAI(model="gpt-4.1")
	@wrap_model_call
	def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
	    """Choose model based on conversation complexity."""
	    message_count = len(request.state["messages"])
	    if message_count > 10:
	        # Use an advanced model for longer conversations
	        model = advanced_model
	    else:
	        model = basic_model
	    return handler(request.override(model=model))
	agent = create_agent(
	    model=basic_model,  # Default model
	    tools=tools,
	    middleware=[dynamic_model_selection]
	)
	```
> [!info]
> 如果你在使用结构化输出，那么不支持使用已经调用过 [`bind_tools`](https://reference.langchain.com/python/langchain-core/language_models/chat_models/BaseChatModel/bind_tools) 的预绑定模型。如果你既需要动态模型选择，又需要结构化输出，请确保传给 middleware 的模型还没有预先绑定工具。
## 2. Tool
 1. Agents 将语言模型与 [工具](https://docs.langchain.com/oss/python/langchain/tools) 结合起来，构建能够对任务进行推理、决定使用哪些工具，并通过迭代逐步逼近解决方案的系统。
 2. [LLM Agent 会在循环中调用工具来达成目标](https://simonwillison.net/2025/Sep/18/agents/)。Agent 会持续运行，直到满足停止条件，也就是模型输出最终结果，或者达到迭代次数上限。
	 ![[IMG-20260406145725948.png|338]]
3. 工具让 agent 具备执行动作的能力。与仅仅把工具绑定给模型相比，Agent 还能进一步支持：
	- 按顺序进行多次工具调用（由单个提示触发）
	- 在合适时进行并行工具调用
	- 根据前一步结果动态选择工具
	- 工具重试逻辑与错误处理
	- 跨工具调用保持状态

### 2.1 静态工具
1. 静态工具会在创建 agent 时定义好，并在整个执行过程中保持不变。这是最常见也最直接的方式。
2. 要定义带有静态工具的 Agent，只需把工具列表传给 agent。
	1. 工具既可以是普通 Python 函数，也可以使用 [tool decorator @tool](https://docs.langchain.com/oss/python/langchain/tools#create-tools) 来自定义工具名称、描述、参数 schema 以及其他属性。
		```python
		from langchain.tools import tool
		from langchain.agents import create_agent
		@tool
		def search(query: str) -> str:
		    """Search for information."""
		    return f"Results for: {query}"
		@tool
		def get_weather(location: str) -> str:
		    """Get weather information for a location."""
		    return f"Weather in {location}: Sunny, 72°F"
		agent = create_agent(model, tools=[search, get_weather])
		```
	2. 如果传入的是空工具列表，那么该 Agent 将只包含一个 LLM 节点，不具备工具调用能力。

### 2.2 动态工具
1. 在动态工具模式下，Agent 可用的工具集合是在运行时修改的，而不是一开始就全部固定下来。
	1. 并不是每个场景都适合暴露所有工具。工具太多可能会让模型不堪重负（上下文过载）并增加错误率；
	2. 工具太少又会限制能力。
2. 动态工具选择允许你根据认证状态、用户权限、功能开关或对话阶段来调整可用工具集。

#### A. 过滤预注册工具
1. 如果在创建代理时已知所有可能的工具，则可以预先注册它们，并根据状态、权限或上下文动态筛选哪些工具可以公开给模型。
2. 这种方式最适合以下场景：
	- 所有可能的工具在编译/启动阶段就已知
	- 你希望根据权限、功能开关或对话状态进行过滤
	- 工具本身是静态的，但可用性是动态的
3. 常见的筛选依据包括：State、Store、Runtime Context
4. e.g.1：仅在完成特定对话里程碑后才启用高级工具
	```python
	from langchain.agents import create_agent
	from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
	from typing import Callable
	@wrap_model_call
	def state_based_tools(
	    request: ModelRequest,
	    handler: Callable[[ModelRequest], ModelResponse]
	) -> ModelResponse:
	    """Filter tools based on conversation State."""
	    # Read from State: check if user has authenticated
	    state = request.state
	    is_authenticated = state.get("authenticated", False)
	    message_count = len(state["messages"])
	    # Only enable sensitive tools after authentication
	    if not is_authenticated:
	        tools = [t for t in request.tools if t.name.startswith("public_")]
	        request = request.override(tools=tools)
	    elif message_count < 5:
	        # Limit tools early in conversation
	        tools = [t for t in request.tools if t.name != "advanced_search"]
	        request = request.override(tools=tools)
	    return handler(request)
	agent = create_agent(
	    model="gpt-4.1",
	    tools=[public_search, private_search, advanced_search],
	    middleware=[state_based_tools]
	)
	```
5. e.g.2：根据用户偏好或应用商店中的功能标志筛选工具
	```python
	from dataclasses import dataclass
	from langchain.agents import create_agent
	from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
	from typing import Callable
	from langgraph.store.memory import InMemoryStore
	@dataclass
	class Context:
	    user_id: str
	@wrap_model_call
	def store_based_tools(
	    request: ModelRequest,
	    handler: Callable[[ModelRequest], ModelResponse]
	) -> ModelResponse:
	    """Filter tools based on Store preferences."""
	    user_id = request.runtime.context.user_id
	    # Read from Store: get user's enabled features
	    store = request.runtime.store
	    feature_flags = store.get(("features",), user_id)
	    if feature_flags:
	        enabled_features = feature_flags.value.get("enabled_tools", [])
	        # Only include tools that are enabled for this user
	        tools = [t for t in request.tools if t.name in enabled_features]
	        request = request.override(tools=tools)
	    return handler(request)
	agent = create_agent(
	    model="gpt-4.1",
	    tools=[search_tool, analysis_tool, export_tool],
	    middleware=[store_based_tools],
	    context_schema=Context,
	    store=InMemoryStore()
	)
	```
6. e.g.3：根据运行时上下文中的用户权限筛选工具
	```python
	from dataclasses import dataclass
	from langchain.agents import create_agent
	from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
	from typing import Callable
	@dataclass
	class Context:
	    user_role: str
	@wrap_model_call
	def context_based_tools(
	    request: ModelRequest,
	    handler: Callable[[ModelRequest], ModelResponse]
	) -> ModelResponse:
	    """Filter tools based on Runtime Context permissions."""
	    # Read from Runtime Context: get user role
	    if request.runtime is None or request.runtime.context is None:
	        # If no context provided, default to viewer (most restrictive)
	        user_role = "viewer"
	    else:
	        user_role = request.runtime.context.user_role
	    if user_role == "admin":
	        # Admins get all tools
	        pass
	    elif user_role == "editor":
	        # Editors can't delete
	        tools = [t for t in request.tools if t.name != "delete_data"]
	        request = request.override(tools=tools)
	    else:
	        # Viewers get read-only tools
	        tools = [t for t in request.tools if t.name.startswith("read_")]
	        request = request.override(tools=tools)
	    return handler(request)
	agent = create_agent(
	    model="gpt-4.1",
	    tools=[read_data, write_data, delete_data],
	    middleware=[context_based_tools],
	    context_schema=Context
	)
	```
#### B. 运行时工具注册
1. 当在运行时发现或创建工具时（例如，从 MCP 服务器加载、根据用户数据生成或从远程注册表中获取），您需要注册这些工具并动态处理它们的执行。
2. 这种方法最适用于以下情况：
	* 工具在运行时被发现（例如，从 MCP 服务器发现）
	* 工具根据用户数据或配置动态生成
	* 与外部工具注册表集成
3. 这需要两个中间件钩子：
	1. `wrap_model_call` - 将动态工具添加到请求中
	2. `wrap_tool_call` - 处理动态添加的工具的执行
	```python
	from langchain.tools import tool
	from langchain.agents import create_agent
	from langchain.agents.middleware import AgentMiddleware, ModelRequest, ToolCallRequest
	# A tool that will be added dynamically at runtime
	@tool
	def calculate_tip(bill_amount: float, tip_percentage: float = 20.0) -> str:
	    """Calculate the tip amount for a bill."""
	    tip = bill_amount * (tip_percentage / 100)
	    return f"Tip: ${tip:.2f}, Total: ${bill_amount + tip:.2f}"
	class DynamicToolMiddleware(AgentMiddleware):
	    """Middleware that registers and handles dynamic tools."""
	    def wrap_model_call(self, request: ModelRequest, handler):
	        # Add dynamic tool to the request
	        # This could be loaded from an MCP server, database, etc.
	        updated = request.override(tools=[*request.tools, calculate_tip])
	        return handler(updated)
	    def wrap_tool_call(self, request: ToolCallRequest, handler):
	        # Handle execution of the dynamic tool
	        if request.tool_call["name"] == "calculate_tip":
	            return handler(request.override(tool=calculate_tip))
	        return handler(request)
	agent = create_agent(
	    model="gpt-4o",
	    tools=[get_weather],  # Only static tools registered here
	    middleware=[DynamicToolMiddleware()],
	)
	# The agent can now use both get_weather AND calculate_tip
	result = agent.invoke({
	    "messages": [{"role": "user", "content": "Calculate a 20% tip on $85"}]
	})
	```
### 2.3 工具调用错误处理
1. 如果你想自定义工具错误的处理方式，可以使用 [`@wrap_tool_call`](https://reference.langchain.com/python/langchain/agents/middleware/types/wrap_tool_call) 装饰器创建中间件。
2. 当工具失败时，agent 会返回一个带有自定义错误信息的 [`ToolMessage`](https://reference.langchain.com/python/langchain-core/messages/tool/ToolMessage)：
	```python
	from langchain.agents import create_agent
	from langchain.agents.middleware import wrap_tool_call
	from langchain.messages import ToolMessage
	@wrap_tool_call
	def handle_tool_errors(request, handler):
	    """Handle tool execution errors with custom messages."""
	    try:
	        return handler(request)
	    except Exception as e:
	        # Return a custom error message to the model
	        return ToolMessage(
	            content=f"Tool error: Please check your input and try again. ({str(e)})",
	            tool_call_id=request.tool_call["id"]
	        )
	agent = create_agent(
	    model="gpt-4.1",
	    tools=[search, get_weather],
	    middleware=[handle_tool_errors]
	)
	```
### 2.4 在 ReAct 循环中使用工具
1. Agent 遵循 ReAct（“Reasoning + Acting”）模式，在简短推理步骤与有针对性的工具调用之间交替进行，并把得到的观察结果送入后续决策，直到能够给出最终答案。
2. Example of ReAct loop
	1. **Prompt:** Identify the current most popular wireless headphones and verify availability.
	2. **Human Message:** Find the most popular wireless headphones right now and check if they're in stock
	![[IMG-20260406145725999.png|489]]![[IMG-20260406145726072.png|490]]![[IMG-20260406145726121.png|491]]
## 3. System Prompt
1. 你可以通过提供提示词来塑造 agent 处理任务的方式。[`system_prompt`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent\(system_prompt\)) 参数可以直接传入一个字符串：
	```python
	agent = create_agent(
	    model,
	    tools,
	    system_prompt="You are a helpful assistant. Be concise and accurate."
	)
	```
2. 如果没有提供 system_prompt，agent 会直接从消息中推断它的任务。
### 3.1 SystemMessage
1. system_prompt 参数既可以接收 str，也可以接收 [SystemMessage](https://reference.langchain.com/python/langchain-core/messages/system/SystemMessage)。
2. 使用 SystemMessage 可以让你更精细地控制提示词结构，这对某些 provider 特性很有用，比如 [Anthropic 的 prompt caching](https://docs.langchain.com/oss/python/integrations/chat/anthropic#prompt-caching)：
	```python
	from langchain.agents import create_agent
	from langchain.messages import SystemMessage, HumanMessage
	literary_agent = create_agent(
	    model="anthropic:claude-sonnet-4-5",
	    system_prompt=SystemMessage(
	        content=[
	            {
	                "type": "text",
	                "text": "You are an AI assistant tasked with analyzing literary works.",
	            },
	            {
	                "type": "text",
	                "text": "<the entire contents of 'Pride and Prejudice'>",
	                "cache_control": {"type": "ephemeral"}
	            }
	        ]
	    )
	)
	result = literary_agent.invoke(
	    {"messages": [HumanMessage("Analyze the major themes in 'Pride and Prejudice'.")]}
	)
	```
1. 带有 `{"type": "ephemeral"}` 的 `cache_control` 字段会告诉 Anthropic 缓存该内容块，从而在重复请求使用相同系统提示词时降低延迟和成本。
> [!info]
> 关于消息类型和格式的更多细节，参见 [Messages](https://docs.langchain.com/oss/python/langchain/messages)。完整的中间件文档见 [Middleware](https://docs.langchain.com/oss/python/langchain/middleware)。

### 3.2 动态系统提示词
1. 对于更高级的场景，如果你需要根据运行时上下文或 Agent 状态来修改系统提示词，可以使用 [middleware](https://docs.langchain.com/oss/python/langchain/middleware)。
2. [`@dynamic_prompt`](https://reference.langchain.com/python/langchain/agents/middleware/types/dynamic_prompt) 装饰器可以创建基于模型请求生成系统提示词的中间件：
	```python
	from typing import TypedDict
	from langchain.agents import create_agent
	from langchain.agents.middleware import dynamic_prompt, ModelRequest
	class Context(TypedDict):
	    user_role: str
	@dynamic_prompt
	def user_role_prompt(request: ModelRequest) -> str:
	    """Generate system prompt based on user role."""
	    user_role = request.runtime.context.get("user_role", "user")
	    base_prompt = "You are a helpful assistant."
	    if user_role == "expert":
	        return f"{base_prompt} Provide detailed technical responses."
	    elif user_role == "beginner":
	        return f"{base_prompt} Explain concepts simply and avoid jargon."
	    return base_prompt
	agent = create_agent(
	    model="gpt-4.1",
	    tools=[web_search],
	    middleware=[user_role_prompt],
	    context_schema=Context
	)
	# The system prompt will be set dynamically based on context
	result = agent.invoke(
	    {"messages": [{"role": "user", "content": "Explain machine learning"}]},
	    context={"user_role": "expert"}
	)
	```
## 4. Name
1. 你可以为 agent 设置一个可选的 [`name`](https://reference.langchain.com/python/langchain/agents/factory/create_agent)。当你在[多 agent 系统](https://docs.langchain.com/oss/python/langchain/multi-agent)中把该 agent 作为子图加入时，这个名称会被用作节点标识符：
	```python
	agent = create_agent(
	    model,
	    tools,
	    name="research_assistant"
	)
	```
2. Agent 名称应优先使用 `snake_case`，例如 `research_assistant`，而不是 `Research Assistant`。
> [!info]
> 有些模型 provider 会拒绝包含空格或特殊字符的名称并返回错误。只使用字母数字、下划线和连字符可以保证在所有 provider 中兼容。对于[工具名称](https://docs.langchain.com/oss/python/langchain/tools)也是同样的建议。

# 二、Agent Invocation
1. 你可以通过向 Agent 的 [`State`](https://docs.langchain.com/oss/python/langgraph/graph-api#state) 传入更新来调用它。所有 Agent 的状态中都包含一个[消息序列](https://docs.langchain.com/oss/python/langgraph/use-graph-api#messagesstate)；要调用 Agent，只需传入一条新消息：
	```python
	result = agent.invoke(
	    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
	)
	```
2. 如果你想从 Agent 中流式获取步骤和/或 token，请参考 [streaming](https://docs.langchain.com/oss/python/langchain/streaming) 指南。
3. 除此之外，agent 遵循 LangGraph 的 [Graph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api)，并支持 `stream`、`invoke` 等所有相关方法。

# 三、高级概念
## 结构化输出

在某些情况下，你可能希望 agent 以特定格式返回输出。LangChain 通过 [`response_format`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) 参数提供结构化输出策略。

### ToolStrategy

`ToolStrategy` 使用人工工具调用来生成结构化输出。它适用于任何支持工具调用的模型。当 provider 原生结构化输出（通过 [`ProviderStrategy`](#providerstrategy)）不可用或不可靠时，应使用 `ToolStrategy`。

```python
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str
agent = create_agent(
    model="gpt-4.1-mini",
    tools=[search_tool],
    response_format=ToolStrategy(ContactInfo)
)
result = agent.invoke({
    "messages": [{"role": "user", "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"}]
})
result["structured_response"]
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```
### ProviderStrategy

`ProviderStrategy` 使用模型 provider 的原生结构化输出能力。这种方式更可靠，但只适用于支持原生结构化输出的 provider：

```python
from langchain.agents.structured_output import ProviderStrategy
agent = create_agent(
    model="gpt-4.1",
    response_format=ProviderStrategy(ContactInfo)
)
```

从 `langchain 1.0` 开始，如果你只是直接传入一个 schema，例如 `response_format=ContactInfo`，那么当模型支持原生结构化输出时，默认会使用 `ProviderStrategy`；否则会回退到 `ToolStrategy`。

要进一步了解结构化输出，参见 [Structured output](https://docs.langchain.com/oss/python/langchain/structured-output)。

## 记忆

Agent 会通过消息状态自动维护对话历史。你也可以为 agent 配置自定义状态 schema，以便在对话期间记住更多信息。存储在状态中的信息可以视为 agent 的[短期记忆](https://docs.langchain.com/oss/python/langchain/short-term-memory)：自定义状态 schema 必须作为 `TypedDict` 扩展 [`AgentState`](https://reference.langchain.com/python/langchain/agents/middleware/types/AgentState)。定义自定义状态有两种方式：

1. 通过 [middleware](https://docs.langchain.com/oss/python/langchain/middleware)（推荐）
2. 通过 [`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) 上的 [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema)

### 通过 Middleware 定义状态

当你的自定义状态需要被特定的中间件钩子和挂载在该中间件上的工具访问时，应使用 middleware 来定义自定义状态。

```python
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from typing import Any
class CustomState(AgentState):
    user_preferences: dict
class CustomMiddleware(AgentMiddleware):
    state_schema = CustomState
    tools = [tool1, tool2]
    def before_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        ...
agent = create_agent(
    model,
    tools=tools,
    middleware=[CustomMiddleware()]
)
# The agent can now track additional state beyond messages
result = agent.invoke({
    "messages": [{"role": "user", "content": "I prefer technical explanations"}],
    "user_preferences": {"style": "technical", "verbosity": "detailed"},
})
```
### 通过 state_schema 定义状态

如果自定义状态只会在工具中使用，那么可以把 [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema) 参数作为一种简写方式。

```python
from langchain.agents import AgentState
class CustomState(AgentState):
    user_preferences: dict
agent = create_agent(
    model,
    tools=[tool1, tool2],
    state_schema=CustomState
)
# The agent can now track additional state beyond messages
result = agent.invoke({
    "messages": [{"role": "user", "content": "I prefer technical explanations"}],
    "user_preferences": {"style": "technical", "verbosity": "detailed"},
})
```

从 `langchain 1.0` 开始，自定义状态 schema **必须**是 `TypedDict` 类型。不再支持 Pydantic 模型和 dataclass。更多细节见 [v1 migration guide](https://docs.langchain.com/oss/python/migrate/langchain-v1#state-type-restrictions)。

相比直接在 [`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) 上通过 [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema) 定义，优先推荐通过 middleware 定义自定义状态，因为这样可以让状态扩展在概念上更清晰地限定在相关中间件和工具范围内。出于向后兼容考虑，[`create_agent`](https://reference.langchain.com/python/langchain/agents/factory/create_agent) 上的 [`state_schema`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.AgentMiddleware.state_schema) 仍然被支持。

要进一步了解记忆，可参见 [Memory](https://docs.langchain.com/oss/python/concepts/memory)。如果你想了解如何实现跨会话持久化的长期记忆，可参见 [Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)。

## 流式输出

前面我们已经看到，可以通过 `invoke` 调用 agent 并得到最终响应。如果 agent 会执行多个步骤，这可能需要一些时间。为了展示中间进度，我们可以在消息发生时把它们流式返回。

```python
from langchain.messages import AIMessage, HumanMessage
for chunk in agent.stream({
    "messages": [{"role": "user", "content": "Search for AI news and summarize the findings"}]
}, stream_mode="values"):
    # Each chunk contains the full state at that point
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        if isinstance(latest_message, HumanMessage):
            print(f"User: {latest_message.content}")
        elif isinstance(latest_message, AIMessage):
            print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        print(f"Calling tools: {[tc['name'] for tc in latest_message.tool_calls]}")
```

关于流式输出的更多内容，参见 [Streaming](https://docs.langchain.com/oss/python/langchain/streaming)。

## 中间件

[Middleware](https://docs.langchain.com/oss/python/langchain/middleware) 提供了强大的可扩展能力，用于在执行的不同阶段自定义 agent 行为。你可以用中间件来：

- 在调用模型之前处理状态（例如消息裁剪、上下文注入）
- 修改或校验模型响应（例如 guardrails、内容过滤）
- 用自定义逻辑处理工具执行错误
- 基于状态或上下文实现动态模型选择
- 添加自定义日志、监控或分析能力

中间件可以无缝集成到 agent 的执行流程中，让你能够在关键节点拦截并修改数据流，而不必改动 agent 的核心逻辑。

完整的中间件文档，以及 [`@before_model`](https://reference.langchain.com/python/langchain/agents/middleware/types/before_model)、[`@after_model`](https://reference.langchain.com/python/langchain/agents/middleware/types/after_model)、[`@wrap_tool_call`](https://reference.langchain.com/python/langchain/agents/middleware/types/wrap_tool_call) 等装饰器的说明，参见 [Middleware](https://docs.langchain.com/oss/python/langchain/middleware)。