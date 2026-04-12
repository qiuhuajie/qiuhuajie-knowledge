---
title: "PromptTemplate 提示词模板"
author: "崔亮的博客"
tags:
  - LangChain
  - Prompt
  - PromptTemplate
  - ChatPromptTemplate
  - FewShot
  - notes/article
aliases:
  - "PromptTemplate提示词模板-崔亮的博客"
  - "PromptTemplate 提示词模板"
source_name: "崔亮的博客"
source_notes:
  - "原始笔记为网页抓取版，本文为整理稿"
---


> [!abstract] 核心摘要
> * PromptTemplate 的本质不是“写一段字符串”，而是<mark style="background: #FFF3A3A6;">把提示词变成可复用、可参数化、可组合的结构</mark>。
> * 在 LangChain 里，文本场景常用 `PromptTemplate`，对话场景常用 `ChatPromptTemplate`，少样本场景常用 `FewShotPromptTemplate` 或 `FewShotChatMessagePromptTemplate`，多轮历史注入则常用 `MessagesPlaceholder`。
> * 真正需要记住的不是类名数量，而是每种模板解决什么问题、输出什么类型，以及它们怎样组合进入后续链路。
# 一、为什么需要 PromptTemplate

1. 在和大模型交互时，通常不会把用户原始输入直接裸传给模型，而是会先做一层结构化包装：
	- 明确角色
	- 组织上下文
	- 约束输出格式
	- 预留变量位置
2. 这套结构化包装方式，就是提示词模板。它解决的核心问题有三个：
	1. **复用：** 同一类 Prompt 不用每次手写。
	2. **参数化：** 把角色、问题、上下文等变量动态注入。
	3. **组合：** 把多个 Prompt 片段拼成更复杂的输入结构。

# 二、模板家族怎么区分

| 类型                                 | 适用场景    | 核心特点                         |
| ---------------------------------- | ------- | ---------------------------- |
| `PromptTemplate`                   | 文本生成模型  | 字符串模板，适合单段文本 Prompt          |
| `ChatPromptTemplate`               | 聊天模型    | 多消息结构，区分 system / human / ai |
| `FewShotPromptTemplate`            | 文本少样本   | 在文本 Prompt 中插入若干示例           |
| `FewShotChatMessagePromptTemplate` | 对话少样本   | 在聊天消息结构中插入示例                 |
| `PipelinePrompt`                   | 管道提示词模板 | 用于把几个提示词组合在一起使用。             |

* 类继承关系
	![[IMG-20260407202431691.png|784]]

> [!info] 可以粗略理解为两条主线：
> - 文本提示模板：围绕字符串模板展开 `StringPromptTemplate`
> - 对话提示模板：围绕消息列表模板展开 `BaseChatPromptTemplate`

# 三、⌨️ **文本提示词模板**：`PromptTemplate`

* `PromptTemplate` 是最基础的文本模板，适合“**生成一段完整字符串再喂给模型**”的场景。

## 1. 常见参数

- `template`：模板字符串，包含固定文本和变量占位符。
- `input_variables`：运行时必须提供的变量名。
- `partial_variables`：预先固定的变量，不需要每次传。

## 2. 两种常见创建方式

### 2.1 构造方法

```python
from langchain_core.prompts import PromptTemplate

# 创建一个PromptTemplate对象，用于生成格式化的提示词模板
# 该模板包含两个变量：role（角色）和question（问题）
template = PromptTemplate(template="你是一个专业的{role}工程师，请回答我的问题给出回答，我的问题是：{question}",
                        input_variables=['role', 'question'])

# 使用模板格式化具体的提示词内容
# 将role替换为"python开发"，question替换为"冒泡排序怎么写？"
prompt = template.format(role="python开发",question="冒泡排序怎么写？")

# 输出格式化后的提示词内容
print(prompt)
```

### 2.2 from_template() 更常用

```python
from langchain_core.prompts import PromptTemplate

# 创建一个PromptTemplate对象，用于生成格式化的提示词模板
# 模板包含两个占位符：{role}表示角色，{question}表示问题
template = PromptTemplate.from_template("你是一个专业的{role}工程师，请回答我的问题给出回答，我的问题是：{question}")

# 使用指定的角色和问题参数来格式化模板，生成最终的提示词字符串
# role: 工程师角色描述
# question: 具体的技术问题
prompt = template.format(role="python开发",question="冒泡排序怎么写？")

# 输出生成的提示词
print(prompt)
```

### 2.3 部分变量：partial

当某些变量在多次调用中是固定的，可以先预填，再把模板继续传下去。

```python
from datetime import datetime
from langchain_core.prompts import PromptTemplate

# 创建一个包含时间变量的模板，时间变量使用partial_variables预设为当前时间
# 然后格式化问题生成最终提示词
template1 = PromptTemplate.from_template("现在时间是：{time},请对我的问题给出答案，我的问题是：{question}",
                                         partial_variables={"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
prompt1 = template1.format(question="今天是几号？")
print(prompt1)

# 创建一个包含时间变量的模板，通过partial方法预设时间变量为当前时间
# 然后格式化问题生成最终提示词
template2 = PromptTemplate.from_template("现在时间是：{time},请对我的问题给出答案，我的问题是：{question}")
partial = template2.partial(time = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
prompt2 = partial.format(question = "今天是几号？")
print(prompt2)
```

### 2.4 模板组合

多个文本模板可以拼接，用于构造更复杂的 Prompt。

```python
from langchain_core.prompts import PromptTemplatefrom langchain_core.prompts import PromptTemplate

# 创建一个PromptTemplate模板，用于生成介绍某个主题的提示词
# 该模板包含两个占位符：topic（主题）和length（字数限制）
template1 = PromptTemplate.from_template("请用一句话介绍{topic}，要求通俗易懂\n") + "内容不超过{length}个字"
# 使用format方法填充模板中的占位符，生成具体的提示词
prompt1 = template1.format(topic="LangChain", length=20)
print(prompt1)

# 分别创建两个独立的PromptTemplate模板
prompt_a = PromptTemplate.from_template("请用一句话介绍{topic}，要求通俗易懂\n")
prompt_b = PromptTemplate.from_template("内容不超过{length}个字")
# 将两个模板进行拼接组合
prompt_all = prompt_a + prompt_b
# 填充组合后模板的占位符，生成最终的提示词
prompt2 = prompt_all.format(topic="LangChain", length=20)
print(prompt2)
```

### 2.5 三个核心方法

| 方法          | 返回值           | 适合场景                     |
| ----------- | ------------- | ------------------------ |
| `format()`  | `str`         | 想直接看最终文本                 |
| `invoke()`  | `PromptValue` | 要接入 LCEL 或统一 Runnable 接口 |
| `partial()` | 新模板对象         | 先固定一部分变量，再继续传递           |

#### `format()`

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template(
    "你是一个专业的{role}工程师，请回答我的问题：{question}"
)

prompt = template.format(role="Python 开发", question="冒泡排序怎么写？")
print(prompt)
print(type(prompt))
```

#### `invoke()`

`invoke()` 返回的不是字符串，而是 `PromptValue`。

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template(
    "你是一个专业的{role}工程师，请回答我的问题：{question}"
)

prompt_value = template.invoke(
    {"role": "Python 开发", "question": "冒泡排序怎么写？"}
)

print(prompt_value)
print(prompt_value.to_string())
```
#### `partial()`

`partial()` 可以格式化部分变量，并且继续返回一个模板，可以继续进行格式化。通常在部分提示词模板场景下使用。

```python
from langchain_core.prompts import PromptTemplate

# 创建模板对象，定义提示词模板格式
# 模板包含两个占位符：role（角色）和 question（问题）
template = PromptTemplate.from_template("你是一个专业的{role}工程师，请回答我的问题给出回答，我的问题是：{question}")

# 使用partial方法固定role参数为"python开发"
# 返回一个新的模板对象，其中role参数已被绑定
partial = template.partial(role="python开发")

# 打印partial对象及其类型信息
print(partial)
print(type(partial))

# 使用format方法填充question参数，生成最终的提示词字符串
# 此时所有占位符都已填充完毕，返回完整的提示词文本
prompt = partial.format(question="冒泡排序怎么写？")

# 输出生成的提示词
print(prompt)
print(type(prompt))
```

---

# 四、💬 对话提示词模板：ChatPromptTemplate

`ChatPromptTemplate` 适合聊天模型，因为它构造的不是一整段文本，而是一组有角色的消息。

## 1. 构造方法
### 1.1 from_messages()

```python
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，请回答我提出的问题"),
    ("human", "请回答：{question}"),
])

prompt_value = chat_prompt.invoke({
    "role": "Python 开发工程师",
    "question": "冒泡排序怎么写？",
})

print(prompt_value.to_string())
```

### 1.2 直接通过列表构造

```python
from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate([
    ("system", "你是一个 AI 助手，你的名字是{name}"),
    ("human", "你能做什么？"),
    ("ai", "我可以陪你聊天、讲笑话、写代码。"),
    ("human", "{user_input}"),
])

print(prompt_template.format(name="小张", user_input="你可以做什么？"))
```

## 2. 常用方法

| 方法 | 返回值 | 说明 |
| --- | --- | --- |
| `invoke()` | `PromptValue` | 统一执行入口 |
| `format_messages()` | `list[BaseMessage]` | 直接拿消息列表 |
| `format_prompt()` | `PromptValue` | 拿到更高层抽象，可转文本或消息 |

### `format_messages()`

```python
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，请回答我提出的问题"),
    ("human", "请回答：{question}"),
])

messages = chat_prompt.format_messages(
    role="Python 开发工程师",
    question="冒泡排序怎么写？",
)

print(messages)
```

### `format_prompt()`

```python
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，请回答我提出的问题"),
    ("human", "请回答：{question}"),
])

prompt_value = chat_prompt.format_prompt(
    role="Python 开发工程师",
    question="冒泡排序怎么写？",
)

print(prompt_value.to_string())
print(prompt_value.to_messages())
```

## 3. 构造方法的参数类型

| 形式                      | 示例                                               | 适合场景        |
| ----------------------- | ------------------------------------------------ | ----------- |
| tuple                   | `("system", "...")`                              | 最常用，最直观     |
| dict                    | `{"role": "system", "content": "..."}`           | 数据化构造消息     |
| `MessagePromptTemplate` | `SystemMessagePromptTemplate.from_template(...)` | 需要模板渲染的消息   |
| 嵌套 `ChatPromptTemplate` | 把小模板拼成大模板                                        | 复杂结构复用      |
| `BaseMessage` 实例        | `SystemMessage(content="...")`                   | 字面消息，不做模板渲染 |

### 3.1 Tuple 形式

```python
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是 AI 助手，你的名字叫{name}。"),
    ("human", "请问：{question}"),
])

messages = chat_prompt.format_messages(name="亮仔", question="什么是 LangChain？")
print(messages)
```

### 3.2 Dict 形式

```python
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate.from_messages([
    {"role": "system", "content": "你是 AI 助手，你的名字叫{name}。"},
    {"role": "user", "content": "请问：{question}"},
])

messages = chat_prompt.format_messages(name="亮仔", question="什么是 LangChain？")
print(messages)
```

### 3.3 使用消息模板类

* 如果你希望系统消息和用户消息都支持变量渲染，应该用消息模板类，而不是直接用消息实例。
	```python
	from langchain_core.prompts import (
	    ChatPromptTemplate,
	    HumanMessagePromptTemplate,
	    SystemMessagePromptTemplate,
	)
	
	system_prompt = SystemMessagePromptTemplate.from_template(
	    "你是 AI 助手，你的名字叫{name}。"
	)
	human_prompt = HumanMessagePromptTemplate.from_template(
	    "请回答：{question}"
	)
	
	chat_prompt = ChatPromptTemplate.from_messages([
	    system_prompt,
	    human_prompt,
	])
	
	messages = chat_prompt.format_messages(name="亮仔", question="什么是 LangChain？")
	print(messages)
	```

### 3.4 嵌套模板
```python
from langchain_core.prompts import ChatPromptTemplate

prompt_template1 = ChatPromptTemplate.from_messages([
    ("system", "你是 AI 助手，你的名字叫{name}。"),
])

prompt_template2 = ChatPromptTemplate.from_messages([
    ("human", "请问：{question}"),
])

chat_prompt = ChatPromptTemplate.from_messages([
    prompt_template1,
    prompt_template2,
])

messages = chat_prompt.format_messages(name="亮仔", question="什么是 LangChain？")
print(messages)
```

# 五、💡 少样本提示词模板：FewShotPromptTemplate

> [!info]
> 少样本提示的核心目的，是先给模型几个例子，再让模型按同样模式处理新输入。

## 1. `FewShotPromptTemplate`

* 适合文本模板场景，核心组成包括：
	- `examples`：示例列表。
	- `example_prompt`：每个示例的格式化方式。
	- `prefix`：示例前说明。
	- `suffix`：真正要问模型的问题模板。
	- `input_variables`：运行时变量。
```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

examples = [
    {"input": "北京下雨吗", "output": "北京"},
    {"input": "上海热吗", "output": "上海"},
]

example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="输入：{input}\n输出：{output}",
)

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="按下面的格式输出结果：",
    suffix="输入：{input}\n输出：",
    input_variables=["input"],
)

print(few_shot_prompt.format(input="天津今天刮风吗"))
```

![[IMG-20260407202431885.png|623]]

## 2. `FewShotChatMessagePromptTemplate`

当示例本身就是对话格式时，更适合用聊天版 few-shot 模板。

```python
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)

examples = [
    {"input": "1×2", "output": "2"},
    {"input": "2×2", "output": "4"},
]

example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input} 是多少"),
    ("ai", "{output}"),
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一名数学奇才"),
]) + few_shot_prompt + ChatPromptTemplate.from_messages([
    ("human", "{question}"),
])

print(final_prompt.format(question="3×2"))
```

![[IMG-20260407202432050.png|717]]

## 3. Example Selector

1. 前面FewShotPromptTemplate的特点是，无论输入什么问题，都会包含全部示例。在实际开发中，我们可以根据当前输入，使用示例选择器，从大量候选示例中选取最相关的示例子集。
2. 使用的好处：避免盲目传递所有示例，减少 token 消耗的同时，还可以提升输出效果。
3. 示例选择策略：
	- 语义相似选择：通过余弦相似度等度量方式评估语义相关性，选择与输入问题最相似的 k 个示例。
	- 长度选择：根据输入文本的长度，从候选示例中筛选出长度最匹配的示例。增强模型对文本结构的理解。比语义相似度计算更轻量，适合对响应速度要求高的场景。
	- 最大边际相关示例选择：优先选择与输入问题语义相似的示例；同时，通过惩罚机制避免返回同质化的内容。
4. 代码如下
	```python
		import os
	
	from langchain_core.example_selectors import SemanticSimilarityExampleSelector
	from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
	from langchain_openai import OpenAIEmbeddings
	from langchain_community.vectorstores import FAISS
	
	# 通义千问 API Key（DashScope 兼容 OpenAI 接口）
	os.environ["OPENAI_API_KEY"] = "sk-xxxx"
	
	# 创建示例模板，用于格式化输入输出对
	example_prompt = PromptTemplate.from_template(template="Input:{input},Output:{output}")
	
	# 定义示例数据集，包含输入词和对应的反义词
	examples = [
	    {"input": "高", "output": "矮"},
	    {"input": "高兴", "output": "悲伤"},
	    {"input": "高级", "output": "低级"},
	    {"input": "高楼大厦", "output": "低矮茅屋"},
	    {"input": "高瞻远瞩", "output": "鼠目寸光"}
	]
	
	# 使用通义千问的 Embedding 模型（通过 DashScope OpenAI 兼容接口）
	# check_embedding_ctx_length=False 禁用 tokenize，DashScope 接口需要直接接收字符串
	embedding = OpenAIEmbeddings(
	    model="text-embedding-v3",
	    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
	    check_embedding_ctx_length=False,
	)
	
	# 创建语义相似度示例选择器，用于根据输入选择最相似的示例
	# 该选择器使用FAISS向量数据库存储示例嵌入，并返回最相似的k个示例
	example_selector = SemanticSimilarityExampleSelector.from_examples(
	    examples,
	    embedding,
	    FAISS,
	    k=2,
	)
	
	# 创建少样本提示模板，结合示例选择器和提示模板生成最终提示
	# 该模板会根据输入选择相似示例，并按照指定格式组合成完整提示
	similar_prompt = FewShotPromptTemplate(
	    example_selector=example_selector,
	    example_prompt=example_prompt,
	    prefix="给出每个词语的反义词",
	    suffix="输入:{input}",
	    input_variables=["input"]
	)
	
	# 格式化提示模板，将"开心"作为输入生成最终提示字符串
	prompt = similar_prompt.format(input="开心")
	print(prompt)
	```

	执行结果如下

	![[IMG-20260407202432221.png|706]]

# 六、消息占位符：MessagesPlaceholder

1. 如果我们不确定消息何时生成，也不确定要插入几条消息，比如在提示词中添加聊天历史记忆这种场景，可以在ChatPromptTemplate添加`MessagesPlaceholder`占位符，在调用invoke时，在占位符处插入消息。
2. 它最适合这些场景：
	- 注入聊天历史
	- 注入 memory
	- 注入 agent scratchpad
## 1. 显式写法
```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 构建一个 ChatPromptTemplate，包含多种消息类型：
prompt = ChatPromptTemplate.from_messages([
    # 插入 memory 占位符，用于填充历史对话记录（如多轮对话上下文）
    MessagesPlaceholder("memory"),

    # 添加一条系统消息，设定 AI 的角色或行为准则
    SystemMessage("你是一个资深的Python应用开发工程师，请认真回答我提出的Python相关的问题"),

    # 添加一条用户问题消息，用变量 {question} 表示
    ("human", "{question}")
])

# 调用 prompt.invoke 来格式化整个 Prompt 模板
# 传入的参数中：
# - memory：是一组历史消息，表示之前的对话内容（多轮上下文）
# - question：是当前用户的问题
prompt_value = prompt.invoke({
    "memory": [
        # 用户第一轮说的话
        HumanMessage("我的名字叫亮仔，是一名程序员"),
        # AI 第一轮的回应
        AIMessage("好的，亮仔你好")
    ],
    # 当前问题：结合上下文，测试模型是否记住了用户名字
    "question": "请问我的名字叫什么？"
})

# 打印生成的完整 prompt 文本，格式化后的聊天记录
print(prompt_value.to_string())
```

## 2. 隐式写法
* `("placeholder", "{memory}")` 可以理解为 `MessagesPlaceholder("memory")` 的简写。
```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 使用 ChatPromptTemplate 构建一个多角色对话提示模板
prompt = ChatPromptTemplate.from_messages([
    # 占位符，用于插入对话“记忆”内容，即之前的聊天记录（历史上下文）
    ("placeholder", "{memory}"),

    # 系统消息，用于设定 AI 的角色 —— 是一个资深的 Python 应用开发工程师
    SystemMessage("你是一个资深的Python应用开发工程师，请认真回答我提出的Python相关的问题"),

    # 用户当前提问，使用变量 {question} 进行动态填充
    ("human", "{question}")
])

# 使用 invoke 方法传入上下文变量，生成格式化后的对话 prompt 内容
prompt_value = prompt.invoke({
    # memory：是之前的对话上下文，会被插入到 {memory} 的位置
    "memory": [
        # 用户第一轮对话
        HumanMessage("我的名字叫亮仔，是一名程序员"),
        # AI 第一轮回答
        AIMessage("好的，亮仔你好")
    ],

    # 当前的问题，将替换模板中的 {question}
    "question": "请问我的名字叫什么？"
})
# 使用 .to_string() 将格式化后的对话链转换成纯文本字符串，方便查看输出
print(prompt_value.to_string())

```

# 七、LangChain Hub

1. LangChain Hub 是一个公共的 prompt（提示词）仓库，访问地址是[https://smith.langchain.com/hub](https://smith.langchain.com/hub)。
2. 类似 HuggingFace Hub，但是专门存放 LangChain 的 Prompt、Chains、Tools 等。
3. 我们可以在 hub 中搜索通用的提示词模板并使用。代码如下：
	```python
	from langchain import hub
	
	prompt = hub.pull("hwchase17/openai-tools-agent")
	
	# 查看结构（Langchain PromptTemplate 的 repr）
	print(prompt)
	
	# 或者访问具体字段
	print(prompt.messages)
	```
4. 它的实际价值不是“直接拿来就上生产”，而是：
	- 看别人怎么组织 system prompt。
	- 看常见 agent 模板怎样放置 `chat_history`、`agent_scratchpad` 这类变量。
	- 把公开模板当成起点，再改成适合自己业务的版本。