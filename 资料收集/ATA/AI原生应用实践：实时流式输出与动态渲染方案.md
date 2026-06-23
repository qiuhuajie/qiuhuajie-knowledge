---
title: "AI原生应用实践：实时流式输出与动态渲染方案"
source: "https://ata.atatech.org/articles/11020606818?spm=ata.23639746.0.0.20fa11dceffq6U"
author:
published:
created: 2026-06-23
description:
---
# AI原生应用实践：实时流式输出与动态渲染方案

中国电商事业群-淘天集团

勋章

粉丝 0影响力 13

**

**

**

** 原创文章

** 内部资料

** AI 辅助创作

**

[赛竞艳(诗乘)](https://ata.atatech.org/users/11002225507)

3月29日发表40次浏览

** 朗读

** 字号

** 笔记

** 分享 **

朗读文章20:02

**

> 摘要：随着大语言模型驱动的对话式智能应用快速普及，传统的请求-响应架构已无法满足实时流式交互的需求。本文基于所在团队的AI原生应用实战经验，分享一套流式输出与动态渲染技术方案并对涉及技术进行介绍，主要围绕 SSE 通信架构、消息路由、前后端数据渲染协议、模型事件处理等核心环节，为后端团队构建高质量的智能应用提供可落地的技术参考。

---

## 一、从请求 - 响应到流式通信

### 1.1 传统 B/S 交互模式的局限

作为后端开发，我们熟悉的技术栈建立在经典的请求 - 响应模型之上：

客户端 → HTTP/HSF 请求 → 服务端处理 → 完整响应 → 客户端渲染

客户端发起一个 HTTP 请求，服务端处理后返回完整的响应体，交互即告结束。这种模式天然适合网页浏览、表单提交等场景，每个请求独立无状态，服务端响应后即完成单次闭环。

然而，随着大语言模型（LLM）驱动的对话式智能应用和AI Agent快速普及，传统模式面临根本性挑战：

<table><colgroup><col width="325"> <col width="325"></colgroup><tbody><tr><td rowspan="1" colspan="1"><p>传统 B/S 架构</p></td><td rowspan="1" colspan="1"><p>对话式智能应用</p></td></tr><tr><td rowspan="1" colspan="1"><p>请求独立无状态</p></td><td rowspan="1" colspan="1"><p>需维护持续性会话状态</p></td></tr><tr><td rowspan="1" colspan="1"><p>单次请求 - 响应闭环</p></td><td rowspan="1" colspan="1"><p>支持动态流式交互</p></td></tr><tr><td rowspan="1" colspan="1"><p>静态内容渲染</p><p>结构化数据为主</p></td><td rowspan="1" colspan="1"><p>动态渲染结构化</p><p>流式文本 + 结构化/非结构化数据</p></td></tr><tr><td rowspan="1" colspan="1"><p>等待完整响应</p></td><td rowspan="1" colspan="1"><p>实时呈现「思考过程」</p></td></tr></tbody></table>

典型场景对比：

●

传统场景：用户提交订单 → 服务端校验 → 写入数据库 → 返回成功/失败

●

AI Agent 场景：用户提问 → 模型逐字生成 → 中途可能调用工具 → 工具异步执行 → 结果合并输出

可以看到，AI Agent 的交互过程是动态的、多阶段的、不可预测时长的，用户期望看到 AI 的「思考过程」逐字呈现，而非等待数秒甚至数十秒后才获得一个完整的答案。

---

### 1.2 技术方案总览

我们的技术方案分为三个核心层次：

┌─────────────────────────────────────────────────────────────┐

│ 前端渲染层 │

│ EventSource 监听 → 消息解析 → 条件渲染（Markdown/Formily） │

└─────────────────────────────────────────────────────────────┘

▲

│ SSE 流式推送

▼

┌─────────────────────────────────────────────────────────────┐

│ 服务端通信层 │

│ 连接管理 → 粘性路由 → 异步消息广播 → 心跳保活 │

└─────────────────────────────────────────────────────────────┘

▲

│ 事件回调

▼

┌─────────────────────────────────────────────────────────────┐

│ 模型交互层 │

│ 事件监听 → 类型转换 → 响应组装 → 持久化 │

└─────────────────────────────────────────────────────────────┘

### 1.3 核心技术选型

<table><colgroup><col width="267"> <col width="267"> <col width="265"></colgroup><tbody><tr><td rowspan="1" colspan="1"><p>模块</p></td><td rowspan="1" colspan="1"><p>技术方案</p></td><td rowspan="1" colspan="1"><p>选型理由</p></td></tr><tr><td rowspan="1" colspan="1"><p>通信协议</p></td><td rowspan="1" colspan="1"><p>SSE（Server-Sent Events）分块流式传输</p></td><td rowspan="1" colspan="1"><p>业界主流方案；单向推送、实现简单、内置重连</p></td></tr><tr><td rowspan="1" colspan="1"><p>路由方案</p></td><td rowspan="1" colspan="1"><p>基于 Token 的粘性路由</p></td><td rowspan="1" colspan="1"><p>解决分布式部署下的连接定位问题</p></td></tr><tr><td rowspan="1" colspan="1"><p>消息广播</p></td><td rowspan="1" colspan="1"><p>会话 ID + 实例 IP 广播</p></td><td rowspan="1" colspan="1"><p>支持异步任务结果跨实例推送</p></td></tr><tr><td rowspan="1" colspan="1"><p>渲染协议</p></td><td rowspan="1" colspan="1"><p>自定义消息类型 + 数据格式</p></td><td rowspan="1" colspan="1"><p>支持文本/Markdown/表单/通知条多形态</p></td></tr><tr><td rowspan="1" colspan="1"><p>事件处理</p></td><td rowspan="1" colspan="1"><p>事件驱动回调</p></td><td rowspan="1" colspan="1"><p>与模型输出事件体系对齐</p></td></tr></tbody></table>

---

## 二、通信协议

### 2.1 为什么选择 SSE（Server-Sent Events）技术？

在技术选型阶段，我们对比了下面几种实时通信协议：

<table><colgroup><col width="97"> <col width="210"> <col width="174"> <col width="160"> <col width="158"></colgroup><tbody><tr><td rowspan="1" colspan="1"><p>对比维度</p></td><td rowspan="1" colspan="1"><p>SSE</p></td><td rowspan="1" colspan="1"><p>WebSocket</p></td><td rowspan="1" colspan="1"><p>HTTP 长轮询</p></td><td rowspan="1" colspan="1"><p>WebTransport</p></td></tr><tr><td rowspan="1" colspan="1"><p>通信方向</p></td><td rowspan="1" colspan="1"><p>服务器→客户端（单向）</p></td><td rowspan="1" colspan="1"><p>双向全双工</p></td><td rowspan="1" colspan="1"><p>客户端轮询服务器响应），服务器有数据时响应，无数据则保持连接直到超时。</p></td><td rowspan="1" colspan="1"><p>双向全双工 + 多流复用</p></td></tr><tr><td rowspan="1" colspan="1"><p>底层协议</p></td><td rowspan="1" colspan="1"><div>基于 HTTP，使用标准文本事件流格式（ <code>text/event-stream</code> ）</div></td><td rowspan="1" colspan="1"><p>WebSocket（独立协议）</p></td><td rowspan="1" colspan="1"><p>基于 HTTP（常规 GET 请求）</p></td><td rowspan="1" colspan="1"><p>HTTP/3 (QUIC)</p></td></tr><tr><td rowspan="1" colspan="1"><p>延迟表现</p></td><td rowspan="1" colspan="1"><p>低延迟，持久化连接</p></td><td rowspan="1" colspan="1"><p>最低延迟</p></td><td rowspan="1" colspan="1"><p>较高，需等待服务器响应，需频繁重建连接</p></td><td rowspan="1" colspan="1"><p>极低延迟，无队头阻塞</p></td></tr><tr><td rowspan="1" colspan="1"><p>资源消耗</p></td><td rowspan="1" colspan="1"><p>低（持久连接）</p></td><td rowspan="1" colspan="1"><p>中高（维护全双工）</p></td><td rowspan="1" colspan="1"><p>高（频繁连接开销）</p></td><td rowspan="1" colspan="1"><p>低（QUIC 多路复用）</p></td></tr><tr><td rowspan="1" colspan="1"><p>实现复杂度</p></td><td rowspan="1" colspan="1"><p>简单（EventSource API）</p></td><td rowspan="1" colspan="1"><p>较复杂（协议升级、帧解析）</p></td><td rowspan="1" colspan="1"><p>中等</p></td><td rowspan="1" colspan="1"><p>较复杂（需 HTTP/3 支持）</p></td></tr><tr><td rowspan="1" colspan="1"><p>浏览器兼容</p></td><td rowspan="1" colspan="1"><p>现代浏览器</p></td><td rowspan="1" colspan="1"><p>主流浏览器</p></td><td rowspan="1" colspan="1"><p>所有浏览器</p></td><td rowspan="1" colspan="1"><p>Chrome/Edge/Firefox/Safari（2025+）</p></td></tr><tr><td rowspan="1" colspan="1"><p>典型场景</p></td><td rowspan="1" colspan="1"><p>LLM 流式输出、通知推送；</p><p>SSE 是当前大模型流式输出的业界主流方案</p></td><td rowspan="1" colspan="1"><p>双向聊天、协同编辑；</p><p>更适合双向高频交互场景，对大模型单向流式输出场景属“过度设计”</p></td><td rowspan="1" colspan="1"><p>兼容性要求高的简单更新；</p><p>效率低已逐步被淘汰</p></td><td rowspan="1" colspan="1"><p>游戏、视频、低延迟双向流；</p><p>WebTransport 作为新技术，尚未被主流应用广泛采用</p></td></tr></tbody></table>

最终选择 SSE 的核心理由：

1.

与 LLM 交互模式天然吻合——大模型对话的模式是：用户发一次问题 → 服务端持续流式返回 token，本质上是"一问，持续答"的单向推送模型；

2.

轻量，实现成本最低——基于 HTTP 协议，无需升级网关配置，可复用现有认证、限流体系

3.

内置重连机制——客户端断线后自动携带 `Last-Event-ID` 重连

4.

浏览器原生支持——浏览器提供了原生的 EventSource API，几乎所有主流浏览器均支持（除 IE）

5.

主流 AI 平台均采用——OpenAI、Anthropic、Google 的 Streaming API 都使用 SSE

### 2.2 SSE实现

![[Attachment/8870b7c9d1d3af9add33419e204f4102_MD5.png]]

SSE 基于 HTTP 协议实现服务器向客户端的单向实时数据推送。客户端通过 `EventSource` API 发起 GET 请求，请求头包含 `Accept: text/event-stream` ，服务器响应时设置 `Content-Type: text/event-stream` 并保持连接开放，形成持久化通道。

SSE 事件流格式

data: 消息内容

event: 自定义事件类型（默认 message）

id: 事件唯一标识（用于断线重连）

retry: 重连时间（毫秒）

在Spring生态中，实现SSE主要有2种技术方案：

●

SseEmitter方案（Spring MVC）

Spring MVC提供的SSE实现，基于Servlet异步处理

代码示例：

@RestController

public class StreamController {

private final Map<String, SseEmitter> emitters = new ConcurrentHashMap<>();

@GetMapping("/stream")

public SseEmitter createStream() {

SseEmitter emitter = new SseEmitter(5 \* 60 \* 1000L);

String connectionId = UUID.randomUUID().toString();

emitters.put(connectionId, emitter);

emitter.onCompletion(() -> emitters.remove(connectionId));

emitter.onError(e -> emitters.remove(connectionId));

return emitter;

}

public void send(String connectionId, Object data) {

SseEmitter emitter = emitters.get(connectionId);

if (emitter!= null) {

emitter.send(SseEmitter.event().data(data));

}

}

}

客户端【JavaScript】

\<script>

const eventSource = new EventSource('http://localhost:8080/api/chat/stream');

eventSource.onmessage = (event) => {

const content = document.getElementById('content');

if (event.data === '\[END\]') {

eventSource.close();

return;

}

content.innerHTML += event.data;

};

eventSource.onerror = (err) => {

console.error('SSE error:', err);

eventSource.close();

};

// 发送问题

function askQuestion() {

const question = document.getElementById('input').value;

fetch('/api/chat/ask', {

method: 'POST',

body: question,

headers: {'Content-Type': 'text/plain'}

});

}

\</script>

技术特点：

<table><colgroup><col width="400"> <col width="399"></colgroup><tbody><tr><td rowspan="1" colspan="1"><p>维度</p></td><td rowspan="1" colspan="1"><p>说明</p></td></tr><tr><td rowspan="1" colspan="1"><p>线程模型</p></td><td rowspan="1" colspan="1"><p>同步阻塞（基于Servlet容器）</p></td></tr><tr><td rowspan="1" colspan="1"><p>依赖</p></td><td rowspan="1" colspan="1"><div><code>spring-boot-starter-web</code></div></td></tr><tr><td rowspan="1" colspan="1"><p>实现复杂度</p></td><td rowspan="1" colspan="1"><p>低</p></td></tr><tr><td rowspan="1" colspan="1"><p>连接管理</p></td><td rowspan="1" colspan="1"><p>手动维护存储</p></td></tr><tr><td rowspan="1" colspan="1"><p>超时控制</p></td><td rowspan="1" colspan="1"><p>构造函数指定超时时间</p></td></tr><tr><td rowspan="1" colspan="1"><p>回调支持</p></td><td rowspan="1" colspan="1"><div><code>onCompletion</code> / <code>onError</code> / <code>onTimeout</code></div></td></tr></tbody></table>

---

●

WebFlux Flux方案（Spring WebFlux）

Spring WebFlux实现的SSE,基于Reactive Streams（响应式流），使用Reactor的Flux推送事件。这是2025-2026年推荐的现代化方案。

代码示例：

@RestController

public class ReactiveStreamController {

private final FluxSinkEmitterRegistry registry = new FluxSinkEmitterRegistry();

@GetMapping(value = "/stream", produces = MediaType.TEXT\_EVENT\_STREAM\_VALUE)

public Flux<ServerSentEvent\<String>> createStream() {

return Flux.<ServerSentEvent\<String>>create(emitter -> {

String connectionId = UUID.randomUUID().toString();

registry.register(connectionId, emitter);

emitter.onDispose(() -> registry.unregister(connectionId));

})

.timeout(Duration.ofMinutes(5))

.doOnCancel(() -> log.info("Client disconnected"));

}

public void send(String connectionId, String data) {

FluxSink<ServerSentEvent\<String>> sink = registry.get(connectionId);

if (sink!= null) {

sink.next(SseEmitter.event().data(data));

}

}

}

技术特点：

<table><colgroup><col width="400"> <col width="399"></colgroup><tbody><tr><td rowspan="1" colspan="1"><p>维度</p></td><td rowspan="1" colspan="1"><p>说明</p></td></tr><tr><td rowspan="1" colspan="1"><p>线程模型</p></td><td rowspan="1" colspan="1"><p>异步非阻塞（基于Reactor+Netty）</p></td></tr><tr><td rowspan="1" colspan="1"><p>依赖</p></td><td rowspan="1" colspan="1"><div><code>spring-boot-starter-webflux</code></div></td></tr><tr><td rowspan="1" colspan="1"><p>实现复杂度</p></td><td rowspan="1" colspan="1"><p>中（需理解响应式编程）</p></td></tr><tr><td rowspan="1" colspan="1"><p>连接管理</p></td><td rowspan="1" colspan="1"><div>使用 <code>FluxSink</code> 注册表</div></td></tr><tr><td rowspan="1" colspan="1"><p>背压支持</p></td><td rowspan="1" colspan="1"><p>✅ 原生支持</p></td></tr><tr><td rowspan="1" colspan="1"><p>操作符丰富</p></td><td rowspan="1" colspan="1"><div>✅ <code>map</code> / <code>filter</code> / <code>timeout</code> 等</div></td></tr></tbody></table>

---

### 2.3 行业标准参考

#### Spring Boot 4.0

Spring Boot 4.0（2025年11月发布）对SSE实现有以下影响：

<table><colgroup><col width="216"> <col width="216"> <col width="216"></colgroup><tbody><tr><td rowspan="1" colspan="1"><p>变化</p></td><td rowspan="1" colspan="1"><p>影响</p></td><td rowspan="1" colspan="1"><p>应对措施</p></td></tr><tr><td rowspan="1" colspan="1"><p>强制JDK 17+</p></td><td rowspan="1" colspan="1"><p>无直接影响</p></td><td rowspan="1" colspan="1"><p>确保JDK版本兼容</p></td></tr><tr><td rowspan="1" colspan="1"><p>Jakarta EE 10</p></td><td rowspan="1" colspan="1"><div>包名从 <code>javax.*</code> 改为 <code>jakarta.*</code></div></td><td rowspan="1" colspan="1"><p>更新导入语句</p></td></tr><tr><td rowspan="1" colspan="1"><p>模块化自动配置</p></td><td rowspan="1" colspan="1"><p>SSE相关配置更精细</p></td><td rowspan="1" colspan="1"><p>按需引入依赖</p></td></tr><tr><td rowspan="1" colspan="1"><p>虚拟线程支持</p></td><td rowspan="1" colspan="1"><p>SseEmitter可结合虚拟线程提升并发</p></td><td rowspan="1" colspan="1"><p>评估虚拟线程收益</p></td></tr></tbody></table>

虚拟线程示例（Spring Boot 4.0 + JDK 21）：

@Configuration

public class VirtualThreadConfig {

@Bean

public Executor virtualTaskExecutor() {

return Executors.newVirtualThreadPerTaskExecutor();

}

}

@RestController

public class VirtualStreamController {

private final Executor virtualExecutor;

public VirtualStreamController(Executor virtualTaskExecutor) {

this.virtualExecutor = virtualTaskExecutor;

}

@GetMapping("/stream")

public SseEmitter createStream() {

SseEmitter emitter = new SseEmitter(5 \* 60 \* 1000L);

// 使用虚拟线程处理发送逻辑

virtualExecutor.execute(() -> {

// 流式发送逻辑

});

return emitter;

}

}

---

#### MCP 协议传输层演进

模型上下文协议（Model Context Protocol，MCP）是 Anthropic 于 2024 年底推出的开放标准，旨在为 AI 应用与外部数据源、工具之间的交互提供统一的协议层。

旧方案：HTTP + SSE 双端点架构

在 MCP 的初始规范（2024-11-05 版本）中，传输层采用 HTTP + SSE 双端点架构：

●

客户端首先通过 GET 请求建立 SSE 连接

●

服务端返回一个 `endpoint` 事件告知客户端后续 POST 请求的目标地址

●

此后，客户端通过 POST 向该地址发送 JSON-RPC 消息，服务端通过 SSE 流返回响应

这种双端点设计在实践中暴露了多个问题：

1.

必须维护长生命周期的 SSE 连接，对高可用基础设施要求较高

2.

不支持流的可恢复性，断线后需要完全重建会话状态

3.

SSE 端点和 POST 端点的分离增加了路由和安全配置的复杂性

4.

纯无状态的 HTTP 服务器无法原生支持此方案

新方案：Streamable HTTP 统一端点

2025 年 3 月 26 日，MCP 发布了协议更新（版本 2025-03-26），正式引入 Streamable HTTP 传输方式并弃用了旧的 HTTP + SSE 方案。

Streamable HTTP 的工作方式：

1.

客户端 → 服务端：所有消息通过 HTTP POST 发送到统一的 MCP 端点，请求体为单个 JSON-RPC 请求、通知或响应

2.

服务端 → 客户端：服务端可以选择以 `application/json` 直接返回（适用于简单请求），或以 `text/event-stream` 开启 SSE 流（适用于需要推送多条消息的场景）

3.

服务端主动推送：客户端可通过 GET 请求打开一个 SSE 流，用于接收服务端主动发起的通知和请求

4.

会话管理：服务端在初始化时可选地分配 `MCP-Session-Id` ，后续请求通过该头部维护会话状态

5.

可恢复流：服务端可为 SSE 事件分配全局唯一 ID，客户端断线后通过 `Last-Event-ID` 头恢复流传输

这种设计的优势是显著的：简单的请求可以完全在无状态 HTTP 中完成，无需建立长连接；只有需要流式传输的场景才升级为 SSE；统一端点大幅简化了路由、认证和安全配置。

---

基于实践经验和业界参考，AI应用（或现有应用的智能化改造）在后端架构设计上可以考虑：

●

渐进式流式：不是所有接口都需要流式，按需升级

●

会话可选：简单场景可无状态，复杂场景再引入会话管理

●

协议标准化：关注行业标准，避免重复造轮子

## 三、 SSE 流式通信架构

### 3.1 连接生命周期管理方案

关键考虑：

<table><colgroup><col width="400"> <col width="399"></colgroup><tbody><tr><td rowspan="1" colspan="1"><p>连接存储</p></td><td rowspan="1" colspan="1"><p>维护连接和会话映射关系</p></td></tr><tr><td rowspan="1" colspan="1"><p>超时控制</p></td><td rowspan="1" colspan="1"><p>防止连接长期占用资源</p></td></tr><tr><td rowspan="1" colspan="1"><p>心跳保活</p></td><td rowspan="1" colspan="1"><p>避免被中间代理超时切断</p></td></tr><tr><td rowspan="1" colspan="1"><p>回调清理</p></td><td rowspan="1" colspan="1"><p>防止内存泄漏</p></td></tr></tbody></table>

代码示例：

@RestController

public class StreamController {

// 存储所有活跃连接的缓存

private final Map<String, SseEmitter> emitters = new ConcurrentHashMap<>();

@CrossOrigin

@GetMapping("/stream")

public SseEmitter createStream() {

SseEmitter emitter = new SseEmitter(5 \* 60 \* 1000L); // 超时 5 分钟

String connectionId = UUID.randomUUID().toString();

emitters.put(connectionId, emitter);

// 心跳保持

sendHeartbeat(emitter);

// 连接关闭处理

emitter.onCompletion(() -> emitters.remove(connectionId));

emitter.onError(e -> {

log.error("SSE error", e);

emitters.remove(connectionId);

});

return emitter;

}

private void sendHeartbeat(SseEmitter emitter) {

ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

scheduler.scheduleAtFixedRate(() -> {

try {

emitter.send(SseEmitter.event().comment("heartbeat"));

} catch (IOException e) {

scheduler.shutdown();

}

}, 0, 30, TimeUnit.SECONDS);

#### 心跳保活机制

SSE 连接在空闲状态下可能被中间代理（如 Nginx、CDN、云负载均衡器）因超时而中断。服务端应以固定间隔发送心跳注释事件。

#### 断线重连与消息恢复

服务端将会话状态持久化 ，以便服务端重启连接丢失时能够重连恢复；针对客户端断线，SSE 协议内置的 `Last-Event-ID` 机制为断线重连提供了基础支持。服务端为每条消息分配递增的 `id` ，客户端断线后自动携带 `Last-Event-ID` 头重新连接，服务端据此从断点位置继续推送。

#### 监控告警

服务端可以对活跃连接数（按实例）、消息推送成功率、心跳超时次数等指标进行监控，以便及时暴露风险。

### 3.2 分布式部署：粘性路由方案

SSE协议本质上是一个长连接的 SSE 和多个短连接的 HTTP POST 一起协作。在分布式部署环境下，如果客户端的后续 POST 请求被负载均衡器路由到与 SSE 连接不同的服务实例，服务端将无法找到对应的 `connectionId` （连接)，导致消息投递失败。

┌─────────────┐ ┌──────────────┐ ┌─────────────┐

│ Client │────▶│ Nginx LB │────▶│ Instance A │

│ │ │ (路由决策) │ │ (持有连接) │

└─────────────┘ └──────────────┘ └─────────────┘

│

▼

┌─────────────┐

│ Instance B │

│ (无连接信息) │

└─────────────┘

❌ connectionId 找不到

我们的解决方案：基于 Token 的粘性路由

1.

SSE 连接建立后，服务端将本机 IP 与 UUID 通过 AES-128 加密，再经 Base64 URL 编码生成 `serverToken`

2.

3.

后续 POST 请求由 Nginx 层的 Lua 脚本拦截，解密 `serverToken` 提取目标 IP

4.

将请求精确转发到对应的后端实例

代码示例：

1.

连接建立时生成路由 Token

private String generateServerToken(String connectionId) {

String serverIp = getLocalIp();

String payload = serverIp + ":" + connectionId;

// AES 加密 + Base64 URL 编码

return encryptAndEncode(payload);

}

2.

.httpOnly(true)

.secure(true)

.path("/")

.build();

response.addCookie(cookie);

3.

应用层提供解密接口

@GetMapping("/mcp/verify")

public String verifyServerToken(@RequestParam String serverToken) {

// 解密 serverToken，提取 IP

String payload = decryptAndDecode(serverToken);

String serverIp = payload.split(":")\[0\];

return serverIp;

}

4.

Nginx 层解析并路由

location /mcp/message {

proxy\_buffering off;

set $target '127.0.0.1';

access\_by\_lua\_block {

if ngx.var.arg\_sessionId then

local verifySessionIdUrl = "/mcp/verify?serverToken=".. ngx.var.arg\_sessionId

local res = ngx.location.capture(verifySessionIdUrl)

if res.status == 200 and res.body and res.body ~= "" then

ngx.var.target = res.body

end

if res.status ~= 200 then

ngx.log(ngx.ERR, "Failed to verify serverToken: ", res.status, " ", res.body)

return ngx.exit(500)

end

end

}

proxy\_pass "http://$target:7001";

add\_header X-Accel-Buffering "no";

}

安全性说明：

●

采用 AES-128 对称加密，应用可自定义密钥

●

即使加密被破解，攻击方构造任意 IP 也只会造成请求转发，不会产生实质危害

---

⚠️ SSE 在生产环境中最常见的问题之一是 Nginx 的代理缓冲。Nginx 默认会缓冲后端响应数据，这会导致 SSE 事件被批量发送而非逐条推送。

location /api/chat {

proxy\_buffering off; # 关闭代理缓冲

add\_header X-Accel-Buffering "no"; # 关闭 FastCGI 缓冲

proxy\_read\_timeout 300s; # 延长超时时间

proxy\_connect\_timeout 60s;

proxy\_send\_timeout 300s;

}

### 3.3 异步消息广播方案

我们的场应用景支持计划的中断和恢复，当其中一个步骤是耗时异步任务时，执行中断，用户可以继续下一个提问。异步任务完成后如果用户依然在线，需要通知前端推送给用户。这里就面临一些问题，接收到任务执行结束消息的实例与原始SSE连接所在实例可能不同，且用户可能刷新页面或在新标签页打开。

我们的解决方案：基于会话 ID 的广播推送

┌─────────────────────────────────────────────────────────┐

│ 任务完成事件 │

└─────────────────────────────────────────────────────────┘

│

▼

┌─────────────────────────────────────────────────────────┐

│ 服务发现获取所有实例 IP 列表 │

│ │

└─────────────────────────────────────────────────────────┘

│

┌───────────────┼───────────────┐

▼ ▼ ▼

┌──────────┐ ┌──────────┐ ┌──────────┐

│ 实例 A │ │ 实例 B │ │ 实例 C │

│ (检查本地) │ │ (检查本地) │ │ (检查本地) │

└──────────┘ └──────────┘ └──────────┘

│ │ │

▼ │ ▼

┌──────────┐ │ ┌──────────┐

│ 推送消息 │ │ │ 推送消息 │

│ 到连接 │ │ │ 到连接 │

└──────────┘ │ └──────────┘

▼

┌──────────┐

│ 无目标连接 │

│ 直接丢弃 │

└──────────┘

1.

服务端维护异步任务与会话 ID 的映射关系，同时记录当前对话位置

2.

任务完成后通过服务发现机制（如 VipServer）获取所有应用实例 IP 列表

3.

向所有实例广播异步消息（包含 `sessionId` / `connectionId` ）

4.

各实例根据本机维护的连接表判断目标连接是否在本机，若在则通过 SSE 通道推送结果；若不在，则向所有同一 `sessionId` 的连接通道推送

5.

异步消息由前端追加到对应对话的回答下方

这种设计确保了跨实例的消息可达性：

●

即使用户刷新页面或在新标签页打开，只要建立了新的 SSE 连接，异步结果就能正确送达。

●

消息自动追加到对应对话的回答下方，不扰乱会话顺序

●

无需轮询，降低服务器开销

## 四、数据渲染协议设计

（待补充）

---

参考资料

1.

MCP 官方规范：Transports — modelcontextprotocol.io

2.

Spring Boot SSE 官方文档

3.

MDN Web Docs：Server-Sent Events API

4.

Formily 官方文档 — formilyjs.org

5.

阿里云百炼 API 文档 — bailian.console.aliyun.com

6.

（待补充）

---

END

一、从请求 - 响应到流式通信

1.1 传统 B/S 交互模式的局限

1.2 技术方案总览

1.3 核心技术选型

二、通信协议

2.1 为什么选择 SSE（Server-Sent Events）技术？

2.2 SSE实现

2.3 行业标准参考

Spring Boot 4.0

MCP 协议传输层演进

三、 SSE 流式通信架构

3.1 连接生命周期管理方案

心跳保活机制

断线重连与消息恢复

监控告警

3.2 分布式部署：粘性路由方案

3.3 异步消息广播方案

四、数据渲染协议设计

有什么问题，和我聊聊吧～

**

内部资料

INTERNAL

405832