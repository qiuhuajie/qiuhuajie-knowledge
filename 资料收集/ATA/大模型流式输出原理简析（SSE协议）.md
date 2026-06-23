---
title: "大模型流式输出原理简析（SSE协议）"
source: "https://ata.atatech.org/articles/12020533240?spm=ata.23639746.0.0.20fa11dceffq6U"
author:
published:
created: 2026-06-23
description:
---
# 大模型流式输出原理简析（SSE协议）

数字马力

勋章

粉丝 3影响力 155

** 8

** 7

**

** 原创文章

** AI 辅助创作

参与征文

[本文正在参加《FY26 不止双11 ATA征文大赛》| 稳定性领域赛道](https://ata.atatech.org/articles/11020509606)

发表到圈儿

[ATA之家](https://ata.atatech.org/community/group/45) (首发)

[数字马力技术团队](https://ata.atatech.org/community/group/1000032)

收录于专题

[Agent应用基础入门](https://ata.atatech.org/specials/10000004322)

**

[武梦琛(辰羊)](https://ata.atatech.org/users/12002363846)

2025-12-25发表303次浏览

** 朗读

** 字号

** 笔记

** 分享 **

朗读文章24:48

**

SSE（Server-Sent Events）是一种基于HTTP的协议，允许服务器向客户端单向推送实时数据。其核心特性包括：

●

单向通信：服务器可以主动向客户端发送数据，而客户端无需发送请求。

●

自动重连：SSE支持断线重连，简化了开发过程。

●

文本流式传输：SSE主要用于传送文本数据，适合流式输出和通知推送等场景。

●

轻量级：与WebSocket相比，SSE更简单，适合轻量级实时应用。

SSE在现代Web应用中提升了实时交互能力，广泛应用于实时通知、数据更新等场景。

目前基本上所有的浏览器（chorme、edge、firefox等）都默认支持该协议。

> 来吧走起～

![[Attachment/9a46b253319da125800cb16f9337772e_MD5.png]]

## SSE本质

类似于单向建立HTTP链接，由服务端向客户端推送消息，传统HTTP链接是一问一答的形式。而SSE，通过服务端向客户端建立“流式连接”，在返回response时，携带一个“流式消息（streaming）”标记，让客户端不要关闭连接，之后连续不断的向客户端发送一个个数据流，而不是一整个完整的数据包。

可以类比为视频播放、下载等场景，客户端源源不断接收服务端传过来的内容。

## SSE与WebSocket

SSE与WebSocket经过简单了解发现功能相似。但是WebSocket是双向通道，C-S之间可以实时交互；而SSE是单向通道，仅由服务端向客户端下发内容。而这个场景是不是很熟悉----“AI对话中的流式回答”。

那么为什么我们AI开发中，这块使用的是SSE协议而不是WebSocket？SSE相比之下有以下优点：

●

SSE 使用 HTTP 协议，现有的服务器软件都支持。WebSocket 是一个独立协议。

●

SSE 属于轻量级，使用简单；WebSocket 协议相对复杂。

●

SSE 默认支持断线重连，WebSocket 需要自己实现。

●

SSE 一般只用来传送文本，二进制数据需要编码后传送，WebSocket 默认支持传送二进制数据。

●

SSE 支持自定义发送的消息类型。

![[Attachment/e7052bae8b7fa446e2c6848b5648c681_MD5.png]]

## 客户端API

## EventSource对象

客户端的SSE部署在 `EventSource` 对象上。

使用SSE时，浏览器创建一个EventSource实例，向服务器发送连接。

var source = new EventSource(url);

var source = new EventSource(url, { withCredentials: true });

EventSource实例的readyState属性，表明连接的当前状态。只读。读取列表：

0：相当于常量EventSource.CONNECTING，表示连接还未建立，或者断线正在重连。

1：相当于常量EventSource.OPEN，表示连接已经建立，可以接受数据。

2：相当于常量EventSource.CLOSED，表示连接已断，且不会重连。

## 基本用法

连接一旦建立，就会触发open事件，可以在onopen属性定义回调函数。

source.onopen = function (event) {

//...

};

// 另一种写法

source.addEventListener('open', function (event) {

//...

}, false);

客户端收到服务器发来的数据，会出发message事件，在onmessage属性设置回调函数。

source.onmessage = function (event) {

var data = event.data;

// handle message

};

// 另一种写法

source.addEventListener('message', function (event) {

var data = event.data;

// handle message

}, false);

上述事件，对象的data属性就是服务器返回的数据（文本格式）。

通信过程中发生错误，会触发error事件，onerror设置回调函数。

source.onerror = function (event) {

// handle error event

};

// 另一种写法

source.addEventListener('error', function (event) {

// handle error event

}, false);

close方法用于关闭SSE连接

source.close();

## 自定义事件

默认情况下，服务器发来的数据，总是触发浏览器 `EventSource` 实例的 `message` 事件。开发者还可以自定义 SSE 事件，这种情况下，发送回来的数据不会触发 `message` 事件。

source.addEventListener('foo', function (event) {

var data = event.data;

// handle message

}, false);

上面代码中，浏览器对 SSE 的 `foo` 事件进行监听。如何实现服务器发送 `foo` 事件，请看下文。

## 服务端如何实现

![[Attachment/9381e623d31cb0fc4a7b638d4eb1d43a_MD5.png]]

## 数据格式

服务器向浏览器发送的 SSE 数据，必须是 UTF-8 编码的文本，具有如下的 HTTP 头信息。

Content-Type: text/event-stream

Cache-Control: no-cache

Connection: keep-alive

上面三行之中，第一行的 `Content-Type` 必须指定 MIME 类型为 `event-steam` 。

每一次发送的信息，由若干个 `message` 组成，每个 `message` 之间用 `\n\n` 分隔。每个 `message` 内部由若干行组成，每一行都是如下格式。

\[field\]: value\\n

上面的 `field` 可以取四个值。

●

data

●

event

●

id

●

retry

此外，还可以有冒号开头的行，表示注释。通常，服务器每隔一段时间就会向浏览器发送一个注释，保持连接不中断。

: This is a comment

下面是一个例子。

: this is a test stream\\n\\n

data: some text\\n\\n

data: another message\\n

data: with two lines \\n\\n

## Data 字段

数据内容用 `data` 字段表示。

data: message\\n\\n

如果数据很长，可以分成多行，最后一行用 `\n\n` 结尾，前面行都用 `\n` 结尾。

data: begin message\\n

data: continue message\\n\\n

下面是一个发送 JSON 数据的例子。

data: {\\n

data: "foo": "bar",\\n

data: "baz", 555\\n

data: }\\n\\n

## Id 字段

数据标识符用 `id` 字段表示，相当于每一条数据的编号。

id: msg1\\n

data: message\\n\\n

浏览器用 `lastEventId` 属性读取这个值。一旦连接断线，浏览器会发送一个 HTTP 头，里面包含一个特殊的 `Last-Event-ID` 头信息，将这个值发送回来，用来帮助服务器端重建连接。因此，这个头信息可以被视为一种同步机制。

## Event 字段

`event` 字段表示自定义的事件类型，默认是 `message` 事件。浏览器可以用 `addEventListener()` 监听该事件。

event: foo\\n

data: a foo event\\n\\n

data: an unnamed event\\n\\n

event: bar\\n

data: a bar event\\n\\n

上面的代码创造了三条信息。第一条的名字是 `foo` ，触发浏览器的 `foo` 事件；第二条未取名，表示默认类型，触发浏览器的 `message` 事件；第三条是 `bar` ，触发浏览器的 `bar` 事件。

下面是另一个例子。

event: userconnect

data: {"username": "bobby", "time": "02:33:48"}

event: usermessage

data: {"username": "bobby", "time": "02:34:11", "text": "Hi everyone."}

event: userdisconnect

data: {"username": "bobby", "time": "02:34:23"}

event: usermessage

data: {"username": "sean", "time": "02:34:36", "text": "Bye, bobby."}

## Retry 字段

服务器可以用 `retry` 字段，指定浏览器重新发起连接的时间间隔。

retry: 10000\\n

两种情况会导致浏览器重新发起连接：一种是时间间隔到期，二是由于网络错误等原因，导致连接出错。

## SpringBoot整合SSE

![[Attachment/f2cb4e14f451031d9385a1cf4037c1f3_MD5.png]]

SpringBoot的Web包整合了SSE

\<dependency>

\<groupId>org.springframework.boot\</groupId>

\<artifactId>spring-boot-starter-web\</artifactId>

\</dependency>

## 实现后端接口

返回类型设置为MediaType.TEXT\_EVENT\_STREAM\_VALUE，即可开启SSE。

package com.example.sse.controller;

import org.springframework.http.MediaType;

import org.springframework.web.bind.annotation.GetMapping;

import org.springframework.web.bind.annotation.RestController;

import java.time.LocalTime;

import java.util.concurrent.Executors;

import java.util.concurrent.TimeUnit;

import java.util.stream.Stream;

@RestController

public class SseController {

@GetMapping(value = "/sse/stream", produces = MediaType.TEXT\_EVENT\_STREAM\_VALUE)

public Stream\<String> stream() {

// 模拟数据流

return Stream.generate(() -> "当前时间：" + LocalTime.now())

.limit(10); // 限制10条消息

}

}

### 实际业务接入

我们实际开发时，返回类型不会是Stream这种粗粒度的，这时候就需要使用到SseEmitter这个类型。

它整合了很多api，相较于Stream更加灵活，不用我们再去额外手动编写。

### SseEmitter 核心 API 详解

#### 1\. 数据发送类 API

##### send(Object data) 方法

emitter.send("Hello World");

emitter.send(responseJson);

用途：向客户端发送普通的文本数据

●

适用于简单的字符串消息

●

自动使用默认的 `MediaType.TEXT_PLAIN`

##### send(Object Data, MediaType mediaType) 方法

// 项目中的实际使用

emitter.send(responseJson, MediaType.APPLICATION\_JSON);

用途：发送指定媒体类型的数据

●

JSON 数据： `MediaType.APPLICATION_JSON` - 最常用

●

纯文本： `MediaType.TEXT_PLAIN` - 默认值

●

HTML： `MediaType.TEXT_HTML`

●

XML： `MediaType.APPLICATION_XML`

实际应用场景：

// 在 SseConsumer.syncSingleData 方法中

JSONObject response = new JSONObject();

response.put("success", true);

response.put("content", "AI回复内容");

emitter.send(response, MediaType.APPLICATION\_JSON);

##### send(SseEventBuilder builder) 方法

emitter.send(SseEmitter.event()

.data("Hello")

.name("message")

.id("123")

.reconnectTime(5000));

用途：发送带有事件元数据的SSE事件

●

event name：事件名称，便于前端区分不同类型的事件

●

event id：事件ID，用于客户端断线重连时的恢复

●

reconnect time：重连间隔时间（毫秒）

●

data：实际数据内容

#### 2\. 连接控制类 API

##### complete() 方法

// 项目中的实际使用

@Override

public void closeFunc() {

emitter.complete();

}

用途：正常完成SSE连接

●

告诉客户端数据流已正常结束

●

不会抛出异常，客户端会正常关闭连接

●

用于正常的业务流程结束

使用场景：

●

AI对话正常完成

●

数据流传输完毕

●

业务逻辑正常结束

##### completeWithError(Throwable throwable) 方法

// 项目中的实际使用

emitter.completeWithError(new RuntimeException("处理失败"));

用途：异常完成SSE连接

●

向客户端报告错误信息

●

客户端会收到错误事件

●

用于异常情况的处理

使用场景：

●

AI模型处理失败

●

系统异常或错误

●

业务逻辑异常终止

#### 3\. 事件回调类 API

##### onCompletion(Runnable callback) 方法

// 项目中的实际使用

emitter.onCompletion(() -> {

try {

AbstractLogContext.set(ctx);

Long timeCost = System.currentTimeMillis() - session.getCreateTime();

LoggerUtil.info(LOGGER, "客户端会话结束,sid:{0},timeCost:{1}", session.getSid(), String.valueOf(timeCost));

sessions.remove(session.getSid());

} finally {

AbstractLogContext.set(null);

}

});

用途：设置连接完成时的回调

●

正常或异常完成都会触发

●

用于清理资源和记录日志

●

统计会话时长和性能指标

##### onTimeout(Runnable callback) 方法

// 项目中的实际使用

emitter.onTimeout(() -> {

AbstractLogContext.set(ctx);

Long timeCost = System.currentTimeMillis() - session.getCreateTime();

LoggerUtil.warn(LOGGER, "客户端会话超时,sid:{0},timeCost:{1}", session.getSid(), String.valueOf(timeCost));

MonitorLogUtil.downstreamMonitorLog(METHOD\_TAG, SCENE\_TAG,false, session.getCreateTime(),params, null);

sessions.remove(session.getSid());

});

用途：设置连接超时时的回调

●

连接超时（默认30秒或指定时间）时触发

●

用于超时监控和资源清理

●

记录超时日志和监控指标

##### onError(Consumer\<Throwable> callback) 方法

// 项目中的实际使用

emitter.onError((e) -> {

try {

AbstractLogContext.set(ctx);

Long timeCost = System.currentTimeMillis() - session.getCreateTime();

LoggerUtil.error(e, LOGGER, "客户端会话报错,sid:{0},timeCost:{1}", session.getSid(), String.valueOf(timeCost));

MonitorLogUtil.downstreamMonitorLog(METHOD\_TAG, SCENE\_TAG,false, session.getCreateTime(),params, null);

sessions.remove(session.getSid());

} finally {

AbstractLogContext.set(null);

}

});

用途：设置连接出错时的回调

●

网络错误、处理异常时触发

●

用于异常监控和错误处理

●

记录错误日志和监控指标

通过自定义返回json字符串内容，由前端解析我们服务端调用模型返回的流式字符段。

## 时间线

> 先有鸡还是先有蛋？

![[Attachment/58b7d984c5080f55516021cd66a94d2d_MD5.svg]]

## SSE协议起源

SSE（Server-Sent Events）协议是先于大模型存在的，它早在2015年就被W3C标准化了，比大模型的爆发早了好几年。

### SSE协议的原始设计

●

2015年：SSE成为W3C推荐标准

●

设计目的：服务器向客户端单向推送数据流

●

典型应用：股票价格推送、新闻更新、社交媒体feed等

## LLM爆火使SSE使用场景光大

2022年底ChatGPT发布，需要使用流式返回来让用户体验良好。

●

传统响应模式：等待模型生成完成之后一次返回，等待时间长

●

流式响应：服务端在收到模型返回首字开始，像打印机一样几个字几个字返回，体验良好

## 大模型SSE流式返回示例

服务端返回到前端的每一个EventSource对象里的data，都有一个id来标识。最终回答结束之后，发送一个结束标记。

// 大模型流式返回示例

data: {"id": "1", "text": "我"}

data: {"id": "2", "text": "认"}

data: {"id": "3", "text": "为"}

data: {"id": "4", "text": "SSE协"}

data: {"id": "5", "text": "议"}

data: {"id": "6", "text": "先于"}

data: {"id": "7", "text": "大模型"}

data: \[DONE\]

## 发展趋势

目前SSE协议仍然是主流的AI对话协议，得益于发布早，兼容性好，成本低，连接建立简单，部署简易等特点，未来很长一段时间仍然会作为主流的大模型对话协议使用。

## 近期眼前一亮的“新范式”——灵光

![[Attachment/bd3c6a1c61a85e336f5aa10e39606f16_MD5.png]]

前段时间公司进行宣传“灵光”，奔着体(can)验(yu)一(chou)下(jiang)的心态，下载下来试了一下，开始发现一些猫腻🐱。

![[Attachment/69c1588875903b9f5b800a01e6babc9c_MD5.png]]

使用过豆包、kimi等ai对话助手，感觉都大差不差，只是换了个logo之类的感觉。而体验了一下灵光，某天后再跟npy介绍的时候，我恍然发现，灵光上对话的字体不是单纯的一种，还有很多大大小小的艺术字，并且嵌入了图片。更有甚query，对话中灵光还能给你根据你的需求制作一个简易的“闪应用”。

这个“闪应用”类似于我们 [oneDay](https://1d.alibaba-inc.com/) 、 [muse](https://muse.antgroup-inc.cn/home) 里大家对话生成的简单网页。这个平时在办公过程中，行政运营同学举办一些小活动，使用这些网站来生成，大家现在想起来是不是十分方便。而现在这份技术下放到用户，并且颠覆了传统流式纯文本输出，这一举措，让人不禁拍手称快。

![[Attachment/b7ccf4a2190d344a73b06a46fa5f856e_MD5.png]]

这里可以给大家看看，我在日常使用过程中，他识别我的意图解答完问题之后，顺手帮我生成了一个小工具。

![[Attachment/440738be59face7dad60c31f68233e31_MD5.png]]

### 使用效果

向灵光提出一个我遇到的需求问题，让他帮我计算优惠地铁乘坐方案。

![[Attachment/034e64a397a6a1d7be7dc41b5909c02f_MD5.png]]

在先给出文字版方案后，又开始制作一个简单的计算器小程序，让人眼前一亮。

![[Attachment/38db6cab9c216480dee0611c74f17734_MD5.png]]

使用之后有一些bug，进行修复一下。

![[Attachment/b3204013bc32359bff2fe699e4f45bfa_MD5.png]] ![[Attachment/742252d91cc48132e647d8655cb996e7_MD5.png]]

而在昨天，我浏览ata的时候，发现志鲲大佬写一篇文章 [《一人手搓复刻蚂蚁灵光》](https://ata.atatech.org/articles/11020532435?spm=ata.23639420.0.0.1552lCYXlCYXyl#MGY2NDc4) ，在拜读完之后，让我想起来刚进入agent项目就听到了有这个sse协议，浏览器已经搜索出来了 但是一直没有时间去阅读一下。遂前往学习了解，记录一下这篇文章。

大佬总结确实是我心中所想，但是苦于水平有限 一直不知道如何表述。

![[Attachment/4242f33b0452ecd75e192a86c5abef5c_MD5.png]]

## WebTransport

WebTransport 是一种新兴的网络协议，旨在为现代 Web 应用提供高效、低延迟的双向通信能力，作为 WebSocket 的现代化替代方案。它基于 HTTP/3（即基于 QUIC 协议）构建，具备更高的性能和更灵活的传输机制。

与 WebSocket 不同，WebTransport 支持多路复用的通信通道，这意味着多个数据流可以并行传输而互不阻塞，避免了传统 TCP 中的队头阻塞问题。它同时提供两种数据传输方式：

1.

可靠传输（类似 TCP）：确保数据按序、完整送达，适用于需要准确性的场景，如聊天消息或控制指令。

2.

不可靠传输（类似 UDP）：以最快速度发送数据，不保证送达或顺序，适用于实时性要求高、可容忍少量丢包的场景，如音视频流、在线游戏中的位置更新。

此外，WebTransport 建立在加密的 QUIC 协议之上，所有通信默认是安全的（即运行在 HTTPS 之上），提升了整体安全性。

典型应用场景包括：

●

多人在线游戏中的实时状态同步

●

互动直播中的低延迟弹幕或观众互动

●

物联网设备与云端的高效数据上报

●

实时音视频通信的辅助控制通道

总之，WebTransport 结合了 TCP 的可靠性与 UDP 的高效性，通过现代网络协议栈的优势，为 Web 提供了更强大、更灵活的实时通信能力，代表了未来 Web 实时交互的发展方向。

### 与SSE相比

<table><colgroup><col width="250"> <col width="250"> <col width="250"></colgroup><tbody><tr><td rowspan="1" colspan="1"><p>维度</p></td><td rowspan="1" colspan="1"><p>SSE（Server-Sent Events）</p></td><td rowspan="1" colspan="1"><p>WebTransport（基于 HTTP/3、QUIC）</p></td></tr><tr><td rowspan="1" colspan="1"><p>数据方向</p></td><td rowspan="1" colspan="1"><p>服务器→浏览器单向流</p></td><td rowspan="1" colspan="1"><p>全双工，可同时上传+下发</p></td></tr><tr><td rowspan="1" colspan="1"><p>传输层</p></td><td rowspan="1" colspan="1"><p>HTTP/1.1 或 HTTP/2 的长连接</p></td><td rowspan="1" colspan="1"><p>QUIC（UDP），0-RTT 建链</p></td></tr><tr><td rowspan="1" colspan="1"><p>每条连接的并发流</p></td><td rowspan="1" colspan="1"><p>1（HTTP/1.1 时串行，HTTP/2 多路复用但服务器推送有限）</p></td><td rowspan="1" colspan="1"><p>独立流（Bidirectional Stream）无队头阻塞</p></td></tr><tr><td rowspan="1" colspan="1"><p>数据格式</p></td><td rowspan="1" colspan="1"><p>纯文本（text/event-stream），自带 retry/event id 语义</p></td><td rowspan="1" colspan="1"><p>任意二进制或文本，需要自己加协议</p></td></tr><tr><td rowspan="1" colspan="1"><p>浏览器支持</p></td><td rowspan="1" colspan="1"><p>全平台</p></td><td rowspan="1" colspan="1"><p>Chrome ≥ 105，Safari 17/Edge 121 开始实验性，Firefox 暂无</p></td></tr><tr><td rowspan="1" colspan="1"><p>网关/防火墙穿透</p></td><td rowspan="1" colspan="1"><p>443 端口即可</p></td><td rowspan="1" colspan="1"><p>443 UDP，部分老旧企业网/运营商 UDP QoS 较差</p></td></tr><tr><td rowspan="1" colspan="1"><p>服务器生态</p></td><td rowspan="1" colspan="1"><p>Nginx/Apache/Node/Go 等开箱即用</p></td><td rowspan="1" colspan="1"><p>目前只有 quiche、quinn、aioquic、wtransport 等实验库，Nginx 官方暂不支持</p></td></tr><tr><td rowspan="1" colspan="1"><p>会话恢复与重连</p></td><td rowspan="1" colspan="1"><p>浏览器自动 retry/Last-Event-ID</p></td><td rowspan="1" colspan="1"><p>需自己在应用层做 token/会话迁移</p></td></tr><tr><td rowspan="1" colspan="1"><p>二进制/压缩效率</p></td><td rowspan="1" colspan="1"><p>无内建压缩，文本冗余大</p></td><td rowspan="1" colspan="1"><p>内建 HPACK/QPACK，可传输 Protobuf/CBOR</p></td></tr><tr><td rowspan="1" colspan="1"><p>服务端推送负载</p></td><td rowspan="1" colspan="1"><p>每个 SSE 连接≈一个 HTTP 长连接，C10K 场景下内存/文件句柄压力大</p></td><td rowspan="1" colspan="1"><p>一个 QUIC 连接可挂几百条流，连接数≈用户量而非消息数</p></td></tr></tbody></table>

WebTransport 技术先进，但目前无法替代 SSE 作为大模型对话的主流传输协议。SSE 因其简单性、兼容性和成熟生态，仍是首选。WebTransport 可能是未来的方向，但需等待生态成熟。

## 结束语

大模型应用开发，不仅仅是对于业务上的理解，在这过程中，去同步学习了解底层的一些知识，可以加深我们在业务场景的思考，判断我们写的地方是否合理，模型答复为何会出现badcase。

这样子，让我们脱离学校里 从底层学起的枯燥，自顶向下来学习，通过Agent实际应用来逐层向下了解对话设计模式、prompt、RAG、向量化、机器学习.......

水平有限，编写偏向基础知识，不足之处谢谢大佬指正～

## 我的相关文章

[我眼中的“普让普特”(Prompt)](https://ata.atatech.org/articles/12020512411?spm=ata.25287382.0.0.3dde7536dmM2jI)

[「CodeFuse」加入这个配置，让开发过程不再枯燥——Prompt简单学习](https://ata.atatech.org/articles/12020458030?spm=ata.25287382.0.0.3dde7536dmM2jI)

## 相关平台

muse： [https://muse.antgroup-inc.cn/home](https://muse.antgroup-inc.cn/home)

ideaTalk： [https://idealab.alibaba-inc.com/chat#/ideaTALK/chat?pageStatus=new](https://idealab.alibaba-inc.com/chat#/ideaTALK/chat?pageStatus=new)

oneday： [https://1d.alibaba-inc.com/?id=020lIFgz](https://1d.alibaba-inc.com/?id=020lIFgz)

codeFuse： [https://codefuse.antgroup-inc.cn/welcome/personal](https://codefuse.antgroup-inc.cn/welcome/personal)

ai广场： [https://aiplayground.antgroup-inc.cn/experience/model/chat](https://aiplayground.antgroup-inc.cn/experience/model/chat)

## 参考资料

[https://ata.atatech.org/articles/11020532435?spm=ata.23639420.0.0.1552lCYXlCYXyl#ODZhOTU0](https://ata.atatech.org/articles/11020532435?spm=ata.23639420.0.0.1552lCYXlCYXyl#ODZhOTU0)

[https://www.ruanyifeng.com/blog/2017/05/server-sent\_events.html](https://www.ruanyifeng.com/blog/2017/05/server-sent_events.html)

[https://www.cnblogs.com/xiondun/p/18828825](https://www.cnblogs.com/xiondun/p/18828825)

[https://juejin.cn/post/7121581378671476773](https://juejin.cn/post/7121581378671476773)

codefuse、ai广场总结问题进行一些文本输出。

END

SSE本质

SSE与WebSocket

客户端API

EventSource对象

基本用法

自定义事件

服务端如何实现

数据格式

data 字段

id 字段

event 字段

retry 字段

SpringBoot整合SSE

实现后端接口

实际业务接入

SseEmitter 核心 API 详解

1\. 数据发送类 API

send(Object data) 方法

send(Object data, MediaType mediaType) 方法

send(SseEventBuilder builder) 方法

2\. 连接控制类 API

complete() 方法

completeWithError(Throwable throwable) 方法

3\. 事件回调类 API

onCompletion(Runnable callback) 方法

onTimeout(Runnable callback) 方法

onError(Consumer\<Throwable> callback) 方法

时间线

SSE协议起源

SSE协议的原始设计

LLM爆火使SSE使用场景光大

大模型SSE流式返回示例

发展趋势

近期眼前一亮的“新范式”——灵光

使用效果

WebTransport

与SSE相比

结束语

我的相关文章：

相关平台

参考资料

有什么问题，和我聊聊吧～

**

内部资料

INTERNAL

405832