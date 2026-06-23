# LangChain 流式输出：这才是实现打字机效果的正确姿势

Jameszyh James的成长日记 *2026年4月3日 20:40*

大家好，我是James。

用过 ChatGPT 的人都记得那种感觉——字一个一个地蹦出来，感觉 AI 在"实时思考"。

但你知道吗？ **90% 的开发者第一次实现流式输出，都踩了同一个坑。**

---

## 01 为什么要流式输出？

先说一个真实的体验差距。

同样一个问题，GPT 回答需要 6 秒：

**❌ 不用流式：**

```java
用户发问 ──────────────────────── 6秒等待 ──────── 整块文字蹦出
    │                                                      │
  发送请求                                             一次性显示
```

**✅ 用了流式：**

```java
用户发问 ── 0.3秒 ── 第1个字 ── 第2个字 ── ... ── 最后一个字
    │          │
  发送请求   立即看到响应（打字机效果）
```

用户等的不是速度，等的是 **反馈** 。

有研究数据表明： **响应时间超过 200ms，用户就会感觉"卡顿"** 。而 LLM 生成一个完整回复，通常需要 3-10 秒。

流式输出本质上是在 **视觉上提前交付** ——让用户感知到"系统在工作"，而不是"系统没反应"。

---

## 02 流式输出的底层原理

在看代码之前，先搞清楚数据是怎么流动的：

```java
┌─────────────┐     token流      ┌─────────────┐     chunk流      ┌─────────────┐
│   LLM模型   │ ──────────────▶  │  LangChain  │ ──────────────▶  │   你的代码  │
│  (逐token   │                  │  (封装成     │                  │  (逐chunk   │
│   生成)     │                  │   chunk)    │                  │   消费)     │
└─────────────┘                  └─────────────┘                  └─────────────┘
```
- **LLM** 每生成一个 token（约1个词/字），就立刻往外推送
- **LangChain** 把 token 封装成 `AIMessageChunk` 对象
- **你的代码** 用 `for await...of` 逐个消费，实时展示

---

## 03 LangChain 流式输出的三种方式

LangChain.js 提供了三种主要的流式 API，用途各不同。

```java
三种流式 API 对比
─────────────────────────────────────────────────────
  .stream()          最基础，拿最终输出的 token 流
  
  chain.stream()     LCEL 链式调用，自动透传流式
  
  streamEvents()     监控每个中间步骤的事件流
─────────────────────────────────────────────────────
  简单场景 ──────────────────────────────▶ 复杂场景
```

### 方式一：.stream() —— 最基础

```java
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4o" });

const stream = await model.stream("用三句话介绍 LangChain");

for await (const chunk of stream) {
  process.stdout.write(chunk.content as string);
}
```

`for await...of` 循环逐 chunk 消费，每个 chunk 是一个 `AIMessageChunk` 。

**适合场景** ：直接调用模型、简单的单步链。

---

### 方式二：Chain 的.stream() —— 配合 LCEL

只要 Chain 用 LCEL（`.pipe()` ）组合，就自动支持流式：

```java
LCEL 流式数据流向
────────────────────────────────────────────────────────
  PromptTemplate  ──pipe──▶  ChatOpenAI  ──pipe──▶  StringOutputParser
       │                          │                        │
   格式化输入                  生成token流             转成纯字符串
                                   │
                           ┌───────▼────────┐
                           │  自动透传流式   │
                           │  每个token     │
                           │  实时向下游传  │
                           └────────────────┘
```
```java
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

const model = new ChatOpenAI({ model: "gpt-4o" });
const prompt = ChatPromptTemplate.fromTemplate("请用中文介绍：{topic}");
const parser = new StringOutputParser();

// 三个组件用 pipe 串联
const chain = prompt.pipe(model).pipe(parser);

// 直接 stream，自动透传
const stream = await chain.stream({ topic: "React 19 的新特性" });

for await (const chunk of stream) {
  process.stdout.write(chunk);
}
```

注意 `StringOutputParser` 的作用：它把 `AIMessageChunk` 对象转成纯字符串，省去手动取 `.content` 。

**适合场景** ：绝大多数日常 Chain。

---

### 方式三：streamEvents() —— 监控中间步骤

前两种只能拿到 **最终输出** 的流。但如果你的 Chain 有多个步骤，想知道每一步都发生了什么，就需要 `streamEvents()` ：

```java
streamEvents() 事件流示意
────────────────────────────────────────────────────────────────
  时间轴 ──────────────────────────────────────────────────▶

  on_chain_start     → Chain 开始执行
    on_chat_model_stream → "你" (第1个token)
    on_chat_model_stream → "好" (第2个token)
    on_chat_model_stream → "，" (第3个token)
    on_chat_model_stream → ...
  on_chain_end       → Chain 执行完成

  每个事件包含: event名 + 组件名 + 数据内容
────────────────────────────────────────────────────────────────
```
```java
const eventStream = await chain.streamEvents(
  { topic: "Vue 3 的响应式原理" },
  { version: "v2" }
);

for await (const event of eventStream) {
  if (
    event.event === "on_chat_model_stream" &&
    event.data?.chunk?.content
  ) {
    process.stdout.write(event.data.chunk.content);
  }
}
```

常见事件类型：

| 事件 | 含义 |
| --- | --- |
| `on_chat_model_stream` | 模型输出 token |
| `on_chain_start` | Chain 开始执行 |
| `on_chain_end` | Chain 执行完成 |
| `on_retriever_end` | 检索器返回结果 |
| `on_tool_end` | 工具调用完成 |

**适合场景** ：需要展示"推理过程"、调试复杂 Agent、前端需要区分显示不同步骤的结果。

---

## 04 前端怎么接？—— SSE 完整链路

后端有了流式输出，前端怎么接收？最常见的方案： **Server-Sent Events（SSE）** 。

```java
前后端 SSE 完整流程
─────────────────────────────────────────────────────────────────
  前端 (Vue3)              后端 (Express)              LLM
     │                          │                        │
     │── POST /stream ─────────▶│                        │
     │                          │── chain.stream() ─────▶│
     │                          │◀─ token1 ──────────────│
     │◀─ data: {"text":"你"} ──│                        │
     │ answer += "你"           │◀─ token2 ──────────────│
     │◀─ data: {"text":"好"} ──│                        │
     │ answer += "好"           │         ...            │
     │◀─ data: [DONE] ─────────│◀─ 生成完毕 ────────────│
     │ 显示完整回答              │── res.end() ───────────│
─────────────────────────────────────────────────────────────────
```

### 后端（Node.js / Express）

```java
import express from "express";
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

const app = express();
app.use(express.json());

const model = new ChatOpenAI({ model: "gpt-4o" });
const prompt = ChatPromptTemplate.fromTemplate("请回答：{question}");
const chain = prompt.pipe(model).pipe(new StringOutputParser());

app.post("/stream", async (req, res) => {
  const { question } = req.body;

  // 设置 SSE 必要的 Headers
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const stream = await chain.stream({ question });

  for await (const chunk of stream) {
    // SSE 格式：data: 内容\n\n
    res.write(\`data: ${JSON.stringify({ text: chunk })}\n\n\`);
  }

  res.write("data: [DONE]\n\n");
  res.end();
});
```

### 前端（Vue 3）

```java
const answer = ref("");

async function askQuestion(question: string) {
  answer.value = "";

  const response = await fetch("/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    const lines = text.split("\n").filter((l) => l.startsWith("data: "));

    for (const line of lines) {
      const data = line.replace("data: ", "").trim();
      if (data === "[DONE]") return;

      const parsed = JSON.parse(data);
      answer.value += parsed.text;
    }
  }
}
```

这就是完整的前后端打字机效果链路。

---

## 05 一个让流式"失效"的常见坑

很多人写了这样的 Chain：

```java
❌ 错误写法 — 普通函数破坏流式
────────────────────────────────────────────────────────
  prompt ──pipe──▶ model ──pipe──▶ parser ──pipe──▶ 普通函数
                     │                                  │
                  逐token输出                    必须等全部完成
                                                才能执行函数
                                                       ▼
                                              流式 → 变成批处理 ❌
────────────────────────────────────────────────────────
```
```java
// ❌ 这样会破坏流式！
const extractResult = (output: string) => {
  return output.toUpperCase();
};

const chain = prompt.pipe(model).pipe(parser).pipe(extractResult);
```

**LangChain 遇到普通函数，会等所有 token 都生成完毕，再整体传入函数执行。**

### 正确做法：用 RunnableLambda 包装

```java
✅ 正确写法 — RunnableLambda 保持流式
────────────────────────────────────────────────────────
  prompt ──pipe──▶ model ──pipe──▶ parser ──pipe──▶ RunnableLambda
                     │                                  │
                  逐token输出                      作为Runnable
                                                  参与流式传递 ✅
────────────────────────────────────────────────────────
```
```java
import { RunnableLambda } from "@langchain/core/runnables";

const extractResult = RunnableLambda.from((output: string) => {
  return output.toUpperCase();
});

const chain = prompt.pipe(model).pipe(parser).pipe(extractResult);
```

用 `RunnableLambda` 包装后，函数变成了 Runnable，LangChain 就知道怎么处理它的流式行为了。

---

## 06 LangGraph 中的流式——.stream() 更强

前面是 LangChain Chain 的流式。如果你用的是 LangGraph，`.stream()` 会更强大：

```java
LangGraph stream 两种模式对比
────────────────────────────────────────────────────────────────
  streamMode: "values"（每次输出完整 state）

  Node A 执行完 ──▶ 输出完整 state: { messages: [...], result: "..." }
  Node B 执行完 ──▶ 输出完整 state: { messages: [...], result: "...", summary: "..." }

  streamMode: "updates"（每次只输出变化部分）

  Node A 执行完 ──▶ 输出变更: { result: "..." }          ← 更省流量
  Node B 执行完 ──▶ 输出变更: { summary: "..." }
────────────────────────────────────────────────────────────────
```
```java
import { StateGraph } from "@langchain/langgraph";

const graph = new StateGraph(...)
  .addNode(...)
  .compile();

const stream = await graph.stream(
  { messages: [{ role: "user", content: "你好" }] },
  { streamMode: "updates" } // 推荐用 updates，更高效
);

for await (const chunk of stream) {
  console.log(chunk);
}
```

处理大型 state 时， `"updates"` 更高效。

---

## 07 总结：怎么选？

```java
流式 API 选择决策树
─────────────────────────────────────────────────────────────
  你的场景是什么？
  │
  ├─ 直接调用模型，无需链式 ──────────────▶ model.stream()
  │
  ├─ 用 LCEL pipe 组合的 Chain ──────────▶ chain.stream()
  │
  ├─ 需要监控中间每一步 ─────────────────▶ chain.streamEvents()
  │
  ├─ LangGraph 多节点 Graph ─────────────▶ graph.stream()
  │    │
  │    ├─ 需要完整快照 ─────────────────▶ streamMode: "values"
  │    └─ 只关心变化 ──────────────────▶ streamMode: "updates"
  │
  └─ 前后端联调 ─────────────────────────▶ SSE + for await...of
─────────────────────────────────────────────────────────────
```

| 场景 | 推荐方案 |
| --- | --- |
| 简单模型调用 | `model.stream()` |
| LCEL Chain | `chain.stream()` |
| 需要监控中间步骤 | `chain.streamEvents()` |
| LangGraph 多节点 | `graph.stream()` |
| 前后端联调 | SSE + `for await...of` |

流式输出不是什么高级特性，本质上就是\*\*"别等全部好了再端上来，做好一个端一个"\*\*。

用户等的不是速度，等的是 **反馈** 。

---

关注我，James 的成长日记，持续分享干货，帮你在 AI 时代少走弯路。

**微信扫一扫赞赏作者**

AI Agent 成神路 · 目录

作者提示: 个人观点，仅供参考

继续滑动看下一个

James的成长日记

向上滑动看下一个