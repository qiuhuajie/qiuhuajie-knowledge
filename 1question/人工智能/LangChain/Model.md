---
title: "Model"
tags:
  - "人工智能"
  - "人工智能/AI Studio"
  - "人工智能/AI Studio/Coding"
  - "Model"
  - "LangChain"
  - "AI Studio"
updated: 2026-04-16
---
# 一、Model介绍
- LangChain 的定位是“模型调用与编排框架”，而不是模型提供方。
- 它通过不同的集成包接入 OpenAI、DeepSeek、Ollama、通义千问等模型。
- 统一接口的价值在于：同一套调用方式可以适配不同模型，便于切换和扩展。
- 官方参考文档：[LangChain Language Models](https://reference.langchain.com/python/langchain_core/language_models/)
> [!Info]
> * 理解 Model 层的重点，是搞清楚三件事：模型类型怎么分、参数怎么配、消息怎么传，以及如何以统一方式接入不同厂商模型。

# 二、Model的分类
1. LangChain 中常见的模型能力可以分为三类：

| 模型类型 | 输入形式 | 输出形式 | 主要特点 | 典型场景 |
| --- | --- | --- | --- | --- |
| LLM | 纯文本字符串 | 文本字符串 | 偏单轮文本生成，调用简单 | 摘要、改写、补全、指令执行 |
| ChatModel | 消息列表 | `AIMessage` | 面向对话场景，支持多轮上下文 | 助手、客服、Agent、工具调用 |
| Embeddings | 文本或文本列表 | 向量 | 负责把文本转成语义向量，不直接生成文本 | RAG、检索、聚类、推荐 |

2. 如果是构建智能助手、Agent 或多轮对话系统，通常优先使用 `ChatModel` 。

# 三、Model 继承关系
- LangChain 的顶层抽象是 `BaseLanguageModel` 。
	- 文本生成模型通常继承 `BaseLLM` 。
	- 聊天模型通常继承 `BaseChatModel` 。
		- 常见的 `ChatOpenAI`、`ChatOllama`、`ChatDeepSeek` 这类封装，本质上都是围绕聊天模型接口工作。
	![[IMG-20260407202504833.png|470]]
# 四、Chat Model 主要参数
1. 聊天模型初始化时，最常见的是下面这些参数：

| 参数名           | 作用                  |
| ------------- | ------------------- |
| `model`       | 指定模型名称              |
| `temperature` | 控制输出随机性，越高越发散，越低越稳定 |
| `timeout`     | 请求超时时间              |
| `max_tokens`  | 最大生成 token 数        |
| `stop`        | 生成停止词，用于控制输出边界      |
| `max_retries` | 请求失败后的最大重试次数        |
| `api_key`     | 模型服务商提供的密钥          |
| `base_url`    | 模型服务的接口地址           |

2. 需要注意：

	- 这些属于 LangChain 常见的标准化参数。

	- 不同模型提供方支持程度不同，并不是每个参数都一定生效。

	- 官方集成包通常兼容得更好，社区集成包可能会有差异。

# 五、Message组件
1. 在 Chat Model 中，输入和输出通常都围绕“消息”展开。消息对象常见属性如下：

| 属性名 | 说明 |
| --- | --- |
| `type` | 消息类型，例如 `user`、`ai`、`system`、`tool` |
| `content` | 消息正文，通常是字符串，也可能是多模态结构 |
| `name` | 可选字段，用于区分同类型消息 |
| `response_metadata` | 模型返回的附加信息，例如 token 使用量、模型名等 |
| `tool_calls` | 当模型决定调用工具时，会在 `AIMessage` 中返回工具调用信息 |

2. 常见消息类型：

	- `HumanMessage`：用户消息。

	- `AIMessage`：模型返回消息。

	- `SystemMessage`：系统提示词，用来约束角色、风格和行为。

	- `ToolMessage`：工具执行结果返回给模型时使用。

	- `ChatMessage`：通用消息结构，可自定义角色。

# 六、接入大模型
* LangChain 的模型接入方式大体一致：导入对应封装类，传入模型名、密钥、接口地址等参数，然后调用 `invoke()` 即可。
## 2. 接入 Ollama
```python
from langchain_ollama import ChatOllama
model = ChatOllama(
    base_url="http://localhost:11434",
    model="qwen3:14b",
    reasoning=False,
)
response = model.invoke("什么是 LangChain？")
print(response.content)
```
## 2. 接入 DeepSeek
```python
import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
load_dotenv(override=True)
model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
response = model.invoke("什么是 LangChain？")
print(response.content)
```
## 3. 接入通义千问
```python
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi
load_dotenv(override=True)
model = ChatTongyi(
    model="<qwen-model-name>",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("QWEN_API_KEY"),
)
response = model.invoke("什么是 LangChain？")
print(response.content)
```
## 4. 接入 OpenAI
```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv(override=True)
model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="<openai-model-name>",
    temperature=0.3,
)
response = model.invoke("什么是 LangChain？")
print(response.content)
```
# 七、模型调用方法 ⭐

LangChain 常见的模型调用方式包括普通调用、流式调用、批量调用和异步调用。

## 1. 对话模型 - Invoke

聊天模型既可以直接接收字符串，也可以接收消息列表。推荐在正式应用中使用消息列表，这样更适合加入系统提示词和工具消息。

```python
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
model = ChatOllama(
    base_url="http://localhost:11434",
    model="qwen3:14b",
    reasoning=False,
)
messages = [
    SystemMessage(content="你叫小亮，是一个乐于助人的人工助手"),
    HumanMessage(content="你是谁"),
]
response = model.invoke(messages)
print(response.content)
print(type(response))
```
## 2. 流式输出 - Stream

流式输出适合聊天机器人、写作助手这类强调实时反馈的场景。它不是等完整结果生成后一次性返回，而是边生成边输出。

```python
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
model = ChatOllama(
    base_url="http://localhost:11434",
    model="qwen3:14b",
    reasoning=False,
)
messages = [
    SystemMessage(content="你叫小亮，是一个乐于助人的人工助手"),
    HumanMessage(content="你是谁"),
]
for chunk in model.stream(messages):
    print(chunk.content, end="", flush=True)
```
## 3. 批量调用 - Batch

`batch()` 适合一次处理多条输入，能够减少多次单独请求的开销。

```python
from langchain_ollama import ChatOllama
model = ChatOllama(
    base_url="http://localhost:11434",
    model="qwen3:14b",
    reasoning=False,
)
questions = [
    "什么是 LangChain？",
    "Python 的生成器是做什么的？",
    "解释一下 Docker 和 Kubernetes 的关系",
]
responses = model.batch(questions)
for question, response in zip(questions, responses):
    print(question)
    print(response.content)
```
## 4. 异步调用 - Ainvoke

`ainvoke()` 适合在 `async/await` 环境中并发执行模型请求，例如 FastAPI、异步任务系统等。

```python
import asyncio
from langchain_ollama import ChatOllama
model = ChatOllama(
    base_url="http://localhost:11434",
    model="qwen3:14b",
    reasoning=False,
)
async def main():
    response = await model.ainvoke("解释一下 LangChain 是什么")
    print(response.content)
asyncio.run(main())
```