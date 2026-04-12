# 一、LangChain 介绍
## 1. Philosophy
1. LangChain 是一个面向 LLM 应用开发的模块化框架，核心目标是把大模型与提示词、外部数据、工具调用、记忆机制和工作流编排连接起来，让模型从“会聊天”升级为“能完成任务”的应用能力。
	- `Lang` 指大语言模型能力。
	- `Chain` 指把多个步骤串联起来执行，例如：构造提示词 -> 调用模型 -> 解析结果 -> 调用工具 -> 返回答案。
	- 它的价值不在于替代模型 API，而在于为复杂应用提供统一接口、可组合组件和更清晰的工程结构。
2. 为什么需要 LangChain ？
	1. 单独使用模型 API 可以完成基础对话，但在真实业务里通常会遇到三个问题：
		- 信息过时：模型知识受训练数据截止时间限制，无法天然获得最新信息。
		- 无法直接执行操作：模型本身不能主动访问数据库、调用 API、执行命令或处理外部系统。
		- 上下文有限：长文档、多轮对话和复杂任务会受到上下文窗口限制。
	2. LangChain 的作用，就是把模型与“数据、工具、记忆、流程”组合起来，补足这些短板。
3. 使用 LangChain 的主要收益
	- 统一模型调用方式，降低切换不同厂商模型的成本。
	- 通过标准化组件减少重复开发，提高工程可维护性。
	- 支持链式编排、工具调用、检索增强和状态管理，适合构建复杂 AI 应用。
	- 生态较丰富，便于接入向量数据库、搜索工具、文档加载器和调试平台。

## 2. 技术体系

| 分类 | 组件/类型 | 说明 | 常见示例 |
| --- | --- | --- | --- |
| 核心库 | `langchain-core` | 提供基础抽象和通用接口，是整个生态的底层核心。 | Runnable、Prompt、Output Parser 等基础能力 |
| 核心库 | `langchain` | 主功能包，包含模型、链、记忆、代理、工具等能力。 | Model、Chain、Memory、Agent、Tool |
| 核心库 | `langchain-community` | 社区扩展包，提供大量第三方集成。 | 文档加载器、向量库、外部工具 |
| 常见集成 | 模型集成 | 对接不同厂商的大模型和嵌入模型。 | `langchain-openai`、`langchain-huggingface`、`langchain-google-genai` |
| 常见集成 | 向量数据库 | 支持向量存储与相似度检索。 | `langchain-chroma`、`langchain-pinecone`、`langchain-faiss`、`langchain-qdrant` |
| 常见集成 | 外部工具 | 为模型补充搜索、知识检索、计算和自动化能力。 | 搜索、百科、论文检索、数学计算、自动化工作流 |
| 辅助能力 | `langsmith` | 用于调试、监控、链路追踪和评估。 | Trace、Observability、Evaluation |
| 辅助能力 | `langserve` | 用于把 LangChain 应用快速暴露为服务接口。 | REST API 部署 |
| 辅助能力 | `langgraph` | 适合构建更复杂、可控、有状态的图式工作流。 | 多步骤流程、循环任务、状态机式 Agent |

## 3. 核心模块

| 模块 | 说明 | 核心价值 |
| --- | --- | --- |
| Model / LLM 接口 | 对不同模型提供统一封装，开发者可以用相似方式切换 OpenAI、Hugging Face、Gemini 等模型。 | 降低模型切换成本，减少供应商绑定。 |
| PromptTemplate | 把提示词抽象成模板，支持变量注入和结构化管理。 | 避免 Prompt 硬编码，提升复用性和可维护性。 |
| Chain | 将多个步骤按顺序连接起来，使前一步输出自动成为下一步输入。 | 适合构建清晰、可复用的处理流程。 |
| Memory | 保存对话历史或中间上下文，必要时做摘要压缩以降低 token 消耗。 | 让多轮交互更连贯，增强上下文记忆。 |
| Tool / Agent / MCP | Tool 用于封装搜索、数据库、脚本、API 等外部能力；Agent 负责按任务自动决策与编排工具；MCP 提供更规范的模型与外部能力连接方式。 | 解决“模型会想，但不会做”的问题。 |
| RAG | 先读取文档、切分文本、向量化并写入向量数据库，再在提问时检索相关片段交给模型生成答案。 | 提升回答的准确性、时效性，并减少幻觉。 |

# 二、Install LangChain
1. python & pip env
	![[IMG-20260407202401301.png|633]]
	![[IMG-20260407202402465.png]]
2. To install the LangChain package:
	```bash
	pip3 install -U langchain # Requires Python 3.10+
	```
3. LangChain 提供与数百个 LLM 和其他数千个集成的集成。这些集成以独立提供商软件包的形式存在。
	```bash
	pip3 install -U langchain-openai 	# Installing the OpenAI integration
	pip3 install -U langchain-anthropic	# Installing the Anthropic integration
	```
# 三、Quick Start
1. Python 解释器配置：打开设置，PyCharm → Settings，找到解释器：
	![[IMG-20260407202402579.png|631]]你的包装在了系统 Python 3.13 里，但 PyCharm 可能指向了另一个 Python 环境（比如 venv 或 conda），所以找不到包。把 IDE 的解释器指向正确的 Python 就好了。
2. 系统提示词：系统提示定义您的代理的角色和行为。
	```python
	SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns. You have access to two tools: 
	- get_weather_for_location: use this to get the weather for a specific location 
	- get_user_location: use this to get the user's location If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location."""
	```
3. 创建工具：工具允许模型通过调用定义的函数与外部系统交互。 工具可以依赖于运行时上下文，并与Agent记忆交互。
	```python
	from dataclasses import dataclass
	from langchain.tools import tool, ToolRuntime
	
	@tool # 定义工具
	def get_weather_for_location(city: str) -> str:
	    """Get weather for a given city."""
	    return f"It's always sunny in {city}!"
	
	@dataclass # 定义上下文格式
	class Context:
	    """Custom runtime context schema."""
	    user_id: str
	 
	@tool # 工具如何使用运行时上下文
	def get_user_location(runtime: ToolRuntime[Context]) -> str:
	    """Retrieve user information based on user ID."""
	    user_id = runtime.context.user_id
	    return "Florida" if user_id == "1" else "SF"
	```
4. 配置模型
	```python
	qwen_model = ChatOpenAI(
	    model="qwen-plus",
	    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
	     # DashScope 的 OpenAI 兼容接口地址应该是 `/compatible-mode/v1`，而不是 `/api/v1/services/aigc/text-generation/generation`（那个是 DashScope 原生接口，不兼容 OpenAI 协议）。
	)
	```
5. 定义响应格式：可选地，如果需要Agent响应与特定 Schema，请定义结构化响应格式。
	```python
	from dataclasses import dataclass
	@dataclass
	class ResponseFormat:
	    """Response schema for the agent."""
	    # A punny response (always required)
	    punny_response: str
	    # Any interesting information about the weather if available
	    weather_conditions: str | None = None
	```
6. 添加记忆：向Agent添加记忆，以在交互之间保持状态。 这允许Agent记住以前的对话和上下文。
	```python
	from langgraph.checkpoint.memory import InMemorySaver

	checkpointer = InMemorySaver()
	```
1. 创建并运行Agent
	```python
	from langchain.agents.structured_output import ToolStrategy
	
	agent = create_agent(
	    model=model,
	    system_prompt=SYSTEM_PROMPT,
	    tools=[get_user_location, get_weather_for_location],
	    context_schema=Context,
	    response_format=ToolStrategy(ResponseFormat),
	    checkpointer=checkpointer
	)
	
	# `thread_id` is a unique identifier for a given conversation.
	config = {"configurable": {"thread_id": "1"}}
	
	response = agent.invoke(
	    {"messages": [{"role": "user", "content": "what is the weather outside?"}]},
	    config=config,
	    context=Context(user_id="1")
	)
	
	print(response['structured_response'])
	# ResponseFormat(
	#     punny_response="Florida is still having a 'sun-derful' day! The sunshine is playing 'ray-dio' hits all day long! I'd say it's the perfect weather for some 'solar-bration'! If you were hoping for rain, I'm afraid that idea is all 'washed up' - the forecast remains 'clear-ly' brilliant!",
	#     weather_conditions="It's always sunny in Florida!"
	# )
	
	# Note that we can continue the conversation using the same `thread_id`.
	response = agent.invoke(
	    {"messages": [{"role": "user", "content": "thank you!"}]},
	    config=config,
	    context=Context(user_id="1")
	)
	
	print(response['structured_response'])
	# ResponseFormat(
	#     punny_response="You're 'thund-erfully' welcome! It's always a 'breeze' to help you stay 'current' with the weather. I'm just 'cloud'-ing around waiting to 'shower' you with more forecasts whenever you need them. Have a 'sun-sational' day in the Florida sunshine!",
	#     weather_conditions=None
	# )
	```

	![[IMG-20260407202402721.png]]