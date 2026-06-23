---
title: "AI应用流式输出研究笔记"
tags:
  - "人工智能"
  - "人工智能/AI Studio"
  - "人工智能/AI Studio/Agent"
  - "流式输出"
  - "SSE"
  - "AI应用工程"
updated: 2026-06-23
aliases:
  - "大模型流式输出"
  - "SSE 流式输出"
  - "AI 对话打字机效果"
---
# 一、流式输出是什么
1. AI 应用里的流式输出，本质上是把一次完整回答拆成连续的增量事件，让用户在模型尚未生成完整答案前，就能看到首个 token、阶段进度、工具执行结果或动态 UI 片段。
2. 它优化的第一目标不是模型真实推理速度，而是用户感知速度。非流式模式要求用户等待完整结果，流式模式则让用户先看到系统已经开始工作，把等待过程变成阅读过程。
3. 打字机效果只是流式输出在前端的可见表现，真正的工程链路包括模型 token 生成、框架 chunk 封装、服务端事件推送、网关代理传输、客户端增量解析和 UI 状态合并。只要中间任意一层发生缓冲、阻塞或批处理，用户看到的仍然会是“等很久后突然出现一大段”。
4. 普通聊天里，流式输出主要承载模型文本；在 [[签证Agent]]、ReAct Agent、Coding Agent 这类复杂系统里，流式输出还会承载规划阶段、工具调用、执行日志、中间结果和最终回答。但这些都应该围绕“把当前回答过程展示给用户”展开，不需要把完整 Agent 异步架构混进来。

# 二、为什么通常选择 SSE
1. SSE，即 Server-Sent Events，是基于 HTTP 的服务器到客户端单向事件流协议。浏览器通过 `EventSource` 或 `fetch + ReadableStream` 建立连接，服务端以 `text/event-stream` 持续推送文本事件。
2. 大模型对话的主链路通常是“一次用户请求，服务端持续返回”，它不是客户端和服务端高频互相发消息，所以 SSE 比 [[WebSocket]] 更贴合默认场景。SSE 可以复用 HTTP 的认证、网关、限流、日志和监控体系，实现成本也更低。
3. WebSocket 更适合双向实时协作、游戏、强交互控制台这类场景；长轮询可以做兼容兜底，但本质还是客户端主动查询；WebTransport 技术上更先进，但浏览器、网关和服务端生态还不如 SSE 成熟。

| 协议 | 通信方向 | 优势 | 主要限制 | 适合场景 |
| --- | --- | --- | --- | --- |
| SSE | 服务端到客户端单向 | 简单、HTTP 友好、自动重连 | 仅文本、主要单向 | AI 对话、进度流、通知流 |
| WebSocket | 双向全双工 | 双向实时、支持二进制 | 连接管理和重连复杂 | 协作、游戏、强交互 Agent |
| 长轮询 | 客户端主动请求 | 兼容性好 | 延迟和请求开销较高 | 简单状态查询兜底 |
| WebTransport | 双向、多路复用 | 低延迟、无 TCP 队头阻塞 | 生态和部署未完全成熟 | 未来低延迟多媒体或复杂流 |

4. SSE 响应头的关键约定是 `Content-Type: text/event-stream`、`Cache-Control: no-cache` 和长连接保持。每条消息由若干字段组成，以空行结束，常用字段包括 `data`、`event`、`id` 和 `retry`。

| 字段 | 含义 | AI 应用中的用法 |
| --- | --- | --- |
| `data` | 事件内容 | token、阶段状态、工具结果、错误对象 |
| `event` | 自定义事件类型 | `message`、`progress`、`tool_result`、`done` |
| `id` | 事件编号 | 支持 `Last-Event-ID`、去重和断点恢复 |
| `retry` | 重连间隔 | 控制浏览器自动重连策略 |

# 三、一条流式链路怎么跑起来
1. 标准链路可以抽象为：模型逐 token 生成 → SDK 或框架封装 chunk → 服务端转换为 SSE 事件 → 反向代理逐块转发 → 客户端解析 `data:` → 前端把增量内容合并到 UI。
2. OpenAI 兼容协议中，流式响应通常由多个 `chat.completion.chunk` 组成。第一个 chunk 可能只包含 `delta.role`，中间 chunk 包含 `delta.content`，最后 chunk 包含 `finish_reason` 和可选 `usage`，最终以 `data: [DONE]` 表示结束。
3. `delta.content` 是增量内容，不是累计内容。前端必须自己维护 `fullContent += delta.content`，并根据 `sessionId`、`messageId`、`stageId` 或 `contentType` 把增量合并到正确位置。
4. 一个普通文本流的事件可以很简单：

    ```text
    data: {"text":"你"}

    data: {"text":"好"}

    data: [DONE]
    ```

5. 一个更适合 AI 应用的事件应显式携带事件类型和业务元数据。这样前端才能区分模型回答、规划阶段、工具结果、错误和完成状态。

    ```text
    event: message
    id: 42
    data: {"sessionId":"s1","messageId":"m1","stageId":"answer","contentType":"text","delta":"你好"}

    event: tool_result
    id: 43
    data: {"sessionId":"s1","messageId":"m1","toolName":"search","status":"succeeded","payload":{"summary":"..."}}

    event: done
    id: 44
    data: {"sessionId":"s1","messageId":"m1","finishReason":"stop"}
    ```

6. 服务端不应该只是把模型厂商的原始 chunk 原样泄漏给前端。更合理的做法是内部保留模型原始事件用于调试，外部暴露一套面向 UI 的稳定事件协议。

# 四、代码实践
## 1. 前端怎么消费流
1. 如果接口需要 POST body、鉴权 Header 或主动取消，优先用 `fetch + ReadableStream`。前端不要假设一次 `reader.read()` 就是一条完整事件，因为网络分片可能把一条 JSON 拆成多段，也可能把多条事件合并到一次读取里。

    ```ts
    type SseMessage = {
      event?: string;
      id?: string;
      data: string;
    };

    function parseSseEvent(raw: string): SseMessage | null {
      const message: SseMessage = { data: "" };

      for (const line of raw.split("\n")) {
        if (!line || line.startsWith(":")) continue;

        const index = line.indexOf(":");
        const field = index === -1 ? line : line.slice(0, index);
        const value = index === -1 ? "" : line.slice(index + 1).trimStart();

        if (field === "event") message.event = value;
        if (field === "id") message.id = value;
        if (field === "data") {
          message.data += message.data ? `\n${value}` : value;
        }
      }

      return message.data ? message : null;
    }

    export async function streamChat(params: {
      url: string;
      body: unknown;
      signal?: AbortSignal;
      onDelta: (text: string) => void;
      onEvent?: (event: SseMessage, json: unknown) => void;
    }) {
      const response = await fetch(params.url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params.body),
        signal: params.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error(`stream request failed: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        while (true) {
          const boundary = buffer.indexOf("\n\n");
          if (boundary === -1) break;

          const rawEvent = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);

          const event = parseSseEvent(rawEvent);
          if (!event) continue;
          if (event.data === "[DONE]") return;

          const json = JSON.parse(event.data) as any;
          params.onEvent?.(event, json);

          const delta = json?.choices?.[0]?.delta?.content ?? json?.delta ?? json?.text;
          if (delta) params.onDelta(delta);
        }
      }
    }
    ```

2. 用户点击停止生成时，前端要中断 HTTP 流，而不是只隐藏加载态。

    ```ts
    const controller = new AbortController();

    streamChat({
      url: "/api/chat/stream",
      body: { question: "解释 SSE 流式输出" },
      signal: controller.signal,
      onDelta: (text) => {
        answer.value += text;
      },
    });

    function stopGenerate() {
      controller.abort();
    }
    ```

3. 如果只是订阅任务进度，`EventSource` 更轻。它适合 Agent Run 进度、异步 Job 状态、通知流，不适合需要 POST body 或复杂 Header 的模型请求。

    ```ts
    const source = new EventSource(`/api/runs/${runId}/events`, {
      withCredentials: true,
    });

    source.addEventListener("message", (event) => {
      const payload = JSON.parse(event.data);
      appendDelta(payload.messageId, payload.delta);
    });

    source.addEventListener("tool_result", (event) => {
      const payload = JSON.parse(event.data);
      renderToolResult(payload.messageId, payload.toolName, payload.payload);
    });

    source.addEventListener("done", () => {
      source.close();
    });
    ```

## 2. 后端怎么吐出流
1. Node.js 后端可以通过 `for await...of` 消费 LangChain 的 `chain.stream()`，再把每个 chunk 包装为 SSE 事件写给浏览器。

    ```ts
    import express from "express";
    import { ChatOpenAI } from "@langchain/openai";
    import { ChatPromptTemplate } from "@langchain/core/prompts";
    import { StringOutputParser } from "@langchain/core/output_parsers";

    const app = express();
    app.use(express.json());

    const model = new ChatOpenAI({ model: "gpt-4o" });
    const prompt = ChatPromptTemplate.fromTemplate("请回答：{question}");
    const chain = prompt.pipe(model).pipe(new StringOutputParser());

    app.post("/api/chat/stream", async (req, res) => {
      res.setHeader("Content-Type", "text/event-stream; charset=utf-8");
      res.setHeader("Cache-Control", "no-cache, no-transform");
      res.setHeader("Connection", "keep-alive");
      res.setHeader("X-Accel-Buffering", "no");
      res.flushHeaders?.();

      const stream = await chain.stream({ question: req.body.question });

      try {
        for await (const chunk of stream) {
          const event = JSON.stringify({
            sessionId: req.body.sessionId,
            messageId: req.body.messageId,
            delta: chunk,
          });
          res.write(`event: message\n`);
          res.write(`data: ${event}\n\n`);
        }

        res.write(`event: done\n`);
        res.write(`data: {"finishReason":"stop"}\n\n`);
        res.write("data: [DONE]\n\n");
      } catch (error) {
        res.write(`event: error\n`);
        res.write(`data: ${JSON.stringify({ message: String(error) })}\n\n`);
      } finally {
        res.end();
      }
    });
    ```

2. FastAPI 的核心写法是异步生成器。每次模型产出 token，就 `yield` 一条符合 SSE 格式的字符串。`request.is_disconnected()` 是取消生成的检查点，真实服务中还应把 `request_id` 传给 vLLM、TGI、自研推理引擎或上游模型 SDK，用于主动释放推理资源。

    ```python
    import json
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse

    app = FastAPI()

    def sse(data: dict, event: str = "message", event_id: str | None = None) -> str:
        lines = []
        if event_id is not None:
            lines.append(f"id: {event_id}")
        lines.append(f"event: {event}")
        lines.append(f"data: {json.dumps(data, ensure_ascii=False)}")
        return "\n".join(lines) + "\n\n"

    async def model_stream(messages):
        yield "你"
        yield "好"

    @app.post("/api/chat/stream")
    async def chat_stream(request: Request):
        body = await request.json()

        async def event_generator():
            yield sse({"role": "assistant"}, event="start")

            async for token in model_stream(body["messages"]):
                if await request.is_disconnected():
                    # 如果底层推理引擎支持 request_id，这里应调用 abort_request。
                    break

                yield sse({
                    "sessionId": body.get("sessionId"),
                    "messageId": body.get("messageId"),
                    "delta": token,
                })

            yield sse({"finishReason": "stop"}, event="done")
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "X-Accel-Buffering": "no",
            },
        )
    ```

3. Spring MVC 项目可以用 `SseEmitter` 渐进接入。它适合连接数不太大、已有 Servlet 体系比较重的应用，重点是连接表和生命周期清理，而不是 `send()` 本身。

    ```java
    @RestController
    @RequestMapping("/api/chat")
    public class SseChatController {

        private final Map<String, SseEmitter> emitters = new ConcurrentHashMap<>();

        @GetMapping("/events")
        public SseEmitter createStream(@RequestParam String sessionId) {
            SseEmitter emitter = new SseEmitter(5 * 60 * 1000L);
            emitters.put(sessionId, emitter);

            emitter.onCompletion(() -> emitters.remove(sessionId));
            emitter.onTimeout(() -> {
                emitters.remove(sessionId);
                emitter.complete();
            });
            emitter.onError(error -> emitters.remove(sessionId));

            return emitter;
        }

        public void sendDelta(String sessionId, String messageId, String delta) {
            SseEmitter emitter = emitters.get(sessionId);
            if (emitter == null) {
                return;
            }

            try {
                emitter.send(SseEmitter.event()
                    .name("message")
                    .id(UUID.randomUUID().toString())
                    .data(Map.of(
                        "sessionId", sessionId,
                        "messageId", messageId,
                        "delta", delta
                    ), MediaType.APPLICATION_JSON));
            } catch (IOException e) {
                emitters.remove(sessionId);
                emitter.completeWithError(e);
            }
        }
    }
    ```

4. Spring WebFlux 更贴近模型流和 Reactive Streams。如果模型调用本身已经返回 `Flux<ChatResponse>`，可以直接把模型流 `map` 成 `ServerSentEvent`，中间插入 `doOnCancel` 做取消清理。

    ```java
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> stream(@RequestParam String query) {
        return chatClient.prompt(query)
            .stream()
            .content()
            .map(text -> ServerSentEvent.<String>builder()
                .event("message")
                .data(text)
                .build())
            .concatWithValues(ServerSentEvent.<String>builder()
                .event("done")
                .data("[DONE]")
                .build())
            .doOnCancel(() -> log.info("client cancelled stream"));
    }
    ```

## 3. 框架怎么保持流式不被破坏
1. [[Model]] 层的 `model.stream()` 适合直接调用模型并拿到最终输出的 token 流。LCEL Chain 的 `chain.stream()` 适合由 Prompt、Model、Parser 组合而成的常规链路，框架会把流式能力向下游透传。

    ```ts
    const stream = await model.stream("用三句话介绍 LangChain");

    for await (const chunk of stream) {
      process.stdout.write(String(chunk.content ?? ""));
    }
    ```

2. 复杂 Chain 或需要观察中间步骤时，可以用 `streamEvents()` 监听事件流。它不仅输出最终 token，还能看到 `on_chain_start`、`on_chat_model_stream`、`on_retriever_end`、`on_tool_end` 等中间事件。

    ```ts
    const events = await chain.streamEvents(
      { topic: "Vue 3 响应式原理" },
      { version: "v2" }
    );

    for await (const event of events) {
      if (event.event === "on_chat_model_stream") {
        const text = event.data?.chunk?.content;
        if (text) process.stdout.write(text);
      }
      if (event.event === "on_tool_end") {
        console.log("tool result:", event.data?.output);
      }
    }
    ```

3. 普通函数可能破坏流式，因为它需要等上游完整输出后才能执行。需要转换时，优先使用框架支持的 Runnable、Transform、流式 Parser 或异步生成器，而不是普通同步函数。

    ```ts
    import { RunnableLambda } from "@langchain/core/runnables";

    const normalize = RunnableLambda.from((output: string) => {
      return output.trim();
    });

    const chain = prompt
      .pipe(model)
      .pipe(new StringOutputParser())
      .pipe(normalize);
    ```

4. Spring AI 构建流式 ReAct Agent 时，可以把 Agent 的 `run()` 暴露为 `Flux<String>`，再把 `FluxSink` 传入 `think()` 和 `act()`。模型文本可以边生成边推给前端，但 tool call 参数必须聚合完整后再执行；工具结果必须作为 observation 写回上下文，否则 ReAct 循环会断。

    ```java
    public abstract class BaseAgent {

        private AgentState state = AgentState.IDLE;
        private int currentStep = 0;
        private final int maxStep;

        public enum AgentState {
            IDLE, RUNNING, FINISHED, ERROR
        }

        public Flux<String> run() {
            return Flux.create(sink -> {
                state = AgentState.RUNNING;
                executeStep(sink);
            });
        }

        private void executeStep(FluxSink<String> sink) {
            if (state != AgentState.RUNNING || currentStep >= maxStep) {
                sink.next("[DONE]");
                sink.complete();
                return;
            }

            sink.next("{\"event\":\"step_start\",\"step\":" + currentStep + "}");

            step(sink)
                .doOnSuccess(shouldContinue -> {
                    currentStep++;
                    executeStep(sink);
                })
                .doOnError(error -> {
                    state = AgentState.ERROR;
                    sink.error(error);
                })
                .subscribe();
        }

        protected abstract Mono<Boolean> step(FluxSink<String> sink);
    }
    ```

    ```java
    public Mono<Boolean> think(FluxSink<String> sink) {
        ChatOptions options = OpenAiChatOptions.builder()
            .internalToolExecutionEnabled(false)
            .build();

        Flux<ChatResponse> responseFlux = chatClient.prompt(buildPrompt())
            .options(options)
            .toolCallbacks(toolCallbacks)
            .stream()
            .chatResponse();

        return responseFlux
            .transform(flux -> new MethodAggregatorWithToolCalls()
                .aggregate(flux, aggregated -> {
                    this.decideTools = aggregated.getResult().getOutput().getToolCalls();
                    chatMemory.add(sessionId, aggregated.getResult().getOutput());
                }))
            .map(response -> response.getResult().getOutput().getText())
            .filter(Objects::nonNull)
            .doOnNext(text -> sink.next(toJson("message", text)))
            .then(Mono.fromSupplier(() -> decideTools != null && !decideTools.isEmpty()));
    }
    ```

# 五、生产可用要处理什么
1. 生产环境最常见的问题是代理缓冲。Nginx、CDN 或内部网关如果默认缓冲后端响应，SSE 事件会被攒成大块再返回，流式效果会失效。Nginx 通常需要关闭缓冲并延长读超时，应用侧也可以补充 `X-Accel-Buffering: no`。

    ```nginx
    location /api/chat/stream {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
        chunked_transfer_encoding on;

        add_header X-Accel-Buffering "no";
    }
    ```

2. 用户主动停止生成时，取消信号必须沿着“前端 abort → 服务端断连感知 → 推理引擎 abort → 资源清理”的链路传递。否则前端虽然不显示了，后端模型仍在继续生成，GPU 或模型 API 成本还在消耗。
3. 断线恢复不要只依赖 SSE 的 `Last-Event-ID`。更稳妥的做法是服务端在每个 chunk 到达时写入 Redis、数据库或事件日志，客户端刷新后先同步已有内容，再决定是否重新接入 SSE。

    ```python
    async def append_stream_chunk(redis, session_id, message_id, event_id, delta):
        stream_key = f"stream:{session_id}:{message_id}"
        await redis.rpush(stream_key, json.dumps({
            "eventId": event_id,
            "delta": delta,
        }, ensure_ascii=False))
        await redis.expire(stream_key, 3600)

    async def sync_stream(redis, session_id, message_id):
        stream_key = f"stream:{session_id}:{message_id}"
        chunks = await redis.lrange(stream_key, 0, -1)
        done = await redis.get(f"{stream_key}:done")

        return {
            "content": "".join(json.loads(item)["delta"] for item in chunks),
            "lastEventId": json.loads(chunks[-1])["eventId"] if chunks else None,
            "isComplete": done == b"1",
            "resumeUrl": None if done else f"/api/messages/{message_id}/stream/resume",
        }
    ```

4. 多模型对比或多 SubAgent 并行时，每条流都应该有独立取消控制器。取消某个模型的回答，不应该影响其他模型；取消当前步骤，也不一定要取消已完成步骤的结果。

    ```ts
    const controllers = new Map<string, AbortController>();

    function startModelStream(modelId: string, question: string) {
      const controller = new AbortController();
      controllers.set(modelId, controller);

      return streamChat({
        url: `/api/models/${modelId}/stream`,
        body: { question },
        signal: controller.signal,
        onDelta: (text) => appendModelAnswer(modelId, text),
      }).finally(() => {
        controllers.delete(modelId);
      });
    }

    function cancelModel(modelId: string) {
      controllers.get(modelId)?.abort();
      controllers.delete(modelId);
    }
    ```

5. 流式输出至少需要监控首字时间、总生成时间、chunk 间隔、连接数、断连率、用户主动取消率、代理缓冲命中、SSE 错误率和重连成功率。如果有 `traceId`，应贯穿用户请求、模型调用、工具执行、SSE 事件和前端日志，便于排查“模型已经生成但前端没看到”的链路问题。

# 六、常见踩坑
1. 后端日志显示 token 持续输出，但浏览器等很久后一次性收到大段内容，优先检查 Nginx、Ingress、API 网关、CDN 和应用响应头，确认没有缓冲、压缩或超时策略破坏事件流。
2. 前端一次读取到的文本不一定是完整事件，直接 `split("\n")` 后 `JSON.parse()` 容易在弱网环境下失败。正确做法是维护 `buffer`，按 SSE 事件边界 `\n\n` 提取完整事件，再解析 `data:`。
3. 如果某一步必须等待完整内容，例如 JSON 校验、结构化输出解析或工具调用参数聚合，应把“可展示文本”和“最终结构化结果”分成不同事件。不要为了一个最终 JSON，牺牲整个回答过程的流式体验。
4. Function calling 或 tool calling 的参数也可能随 chunk 增量到达。如果在参数尚未完整聚合时执行工具，会产生 JSON 不完整、参数缺失或错误调用。正确方式是在模型流结束或 tool call 聚合完成后，再进入工具执行阶段，并把工具结果作为下一轮上下文写回 memory。
5. 并不是所有接口都需要流式。如果后端处理很快，完整结果能在用户感知阈值内返回；或者输出必须作为完整结构校验后才能展示，例如支付结果、风控结论、数据库事务结果，那么非流式接口反而更简单可靠。

# 七、关联笔记
* [[签证Agent]]
* [[如何设计一个AI Agent系统 - ATA]]
* [[LangChain 介绍]]
* [[Model]]
* [[Agents]]
* [[WebSocket]]

# 八、资料来源
* [[资料收集/ATA/AI原生应用实践：实时流式输出与动态渲染方案|AI原生应用实践：实时流式输出与动态渲染方案]]
* [[资料收集/ATA/大模型流式输出原理简析（SSE协议）|大模型流式输出原理简析（SSE协议）]]
* [[资料收集/ATA/如何优雅处理SSE流式输出内容|如何优雅处理SSE流式输出内容]]
* [[资料收集/ATA/Spring AI如何构建流式输出的ReAct Agent|Spring AI如何构建流式输出的ReAct Agent]]
* [[资料收集/WeChat/大模型流式输出实现原理深度解析|大模型流式输出实现原理深度解析]]
* [[资料收集/WeChat/LangChain 流式输出：这才是实现打字机效果的正确姿势|LangChain 流式输出：这才是实现打字机效果的正确姿势]]
* [[资料收集/WeChat/Agent 异步架构原理|Agent 异步架构原理]]
