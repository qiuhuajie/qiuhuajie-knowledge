---
title: "如何优雅处理SSE流式输出内容"
source: "https://ata.atatech.org/articles/12020431601?spm=ata.23639746.0.0.20fa11dceffq6U"
author:
published:
created: 2026-06-23
description:
---
# 如何优雅处理SSE流式输出内容

数字马力

粉丝 1影响力 13

** 3

** 5

** 1

发表到圈儿

[ASF前端技术圈](https://ata.atatech.org/community/team/100080) / [技术分享文章](https://ata.atatech.org/community/team/100080?cid=100169) (首发)

**

[李伟(将武)](https://ata.atatech.org/users/12001872712)

2025-06-30发表2025-08-29更新454次浏览

** 朗读

** 字号

** 笔记

** 分享 **

朗读文章08:27

**

## 服务器推送技术和客户端主动请求

### 客户端主动请求包括

1.

轮询（Polling） ：

○

描述：客户端定期向服务器发送请求，检查是否有新数据。如果服务器有新数据，就返回给客户端；如果没有，就返回空或者旧数据。

○

优点：实现简单，不需要特殊的服务器支持。

○

缺点：效率低，因为即使没有新数据，客户端也会频繁发送请求，造成不必要的网络流量和服务器负载。

2.

长轮询（Long Polling） ：

○

描述：客户端发送请求到服务器，服务器保持请求打开，直到有新数据可发送或者超时。

○

优点：比传统轮询更高效，因为只有在有数据时才响应。

○

缺点：仍然有延迟，因为需要等待服务器超时或有数据时才响应。

3.

HTTP/2 Server Push：

○

描述：在HTTP/2协议中，服务器可以在客户端请求一个资源时，主动推送相关的其他资源。

○

优点：减少了额外的请求-响应周期，加快了页面加载速度。

○

缺点：需要客户端和服务器都支持HTTP/2协议。

### 服务器推送技术

服务器推送(Server Push)技术允许客户端和服务端在有新内容可用时主动向客户端推送更新，而不需要用户主动去查询。服务器推送的优点有两个:

1.

用户体验更流畅。用户不需要一直去刷新页面来获取最新内容,系统会在有新的消息出现时自动推送给客户端。

2.

更高效。服务器只在有真正有用的内容时才主动推送,节省了大量不必要的客户端请求。

服务器推送技术：

1.

SSE（Server-Sent Events） ：

○

描述：一种允许服务器向客户端推送事件的技术。客户端通过创建一个到服务器的单向连接来监听事件。

○

优点：实现相对简单，只需要客户端监听一个事件源，适合单向通信（服务器到客户端）。

○

缺点：不支持双向通信，如果需要客户端向服务器发送数据，还需要额外的轮询或WebSocket连接。

2.

WebSocket：

○

描述：一种在单个TCP连接上进行全双工通信的协议。一旦WebSocket连接建立，服务器和客户端就可以通过这个连接发送数据，无需每次建立新的连接。

○

优点：支持全双工通信，延迟低，适用于需要实时双向通信的场景。

○

缺点：实现相对复杂，需要服务器和客户端都支持WebSocket协议。

SSE：

●

单向通信：SSE 是一种单向通信协议，服务器可以向客户端发送数据，但客户端不能向服务器发送数据。

●

简单易用：SSE 的实现相对简单，只需要在服务器端使用 SseEmitter 或类似机制，客户端使用标准的EventSource API 即可。

●

文本数据：SSE 只支持文本数据，不支持二进制数据。

●

自动重连：SSE 支持自动重连，当连接断开时，客户端会自动尝试重新连接。

●

浏览器支持：现代浏览器普遍支持 SSE，无需额外的库或插件。

对比一下我们熟知的Websocket Websocket：

●

双向通信：WebSocket 是一种双向通信协议，服务器和客户端都可以互相发送数据。

●

复杂性：WebSocket 的实现相对复杂，需要处理连接管理、心跳检测、错误处理等。

●

二进制数据：WebSocket 支持二进制数据传输，适用于需要传输大量数据或复杂数据结构的场景。

●

手动重连：WebSocket 需要手动实现重连逻辑，客户端需要在连接断开时主动重新建立连接。

●

广泛支持：WebSocket 在现代浏览器和多种编程语言中都有良好的支持。

WebSocket：

![[Attachment/64b53de5c37bc3d74a66c53fc5e8eeae_MD5.png]]

SSE:

![[Attachment/06c3136dbb6e7c9ee0ea0a671fc5d955_MD5.png]]

SSE返回EventMessage示例，reader读取出来的text文本，交给JSON解析前需去除消息头部的“data:”

例：

![[Attachment/07664044d4e8786a39c42833a48c94fd_MD5.png]]

复制出来其中一个message， 消息格式自定义如下：

data:{"data":{"msgId":"0ffccb9b-4038-4b67-912c-7f831167b838","sessionId":"CHS00020250625000000121746","createTime":1750821895651,"traceId":"0601fc511750821888173171472","turn":0,"roleType":"Agent","msgType":"CHAT","replyCmd":"Continue","contents":\[{"indexId":1,"contentType":"stream","content":{"text":"中的","dataType":"","stageName":"规划","stageId":"规划","status":"RUNNING"},"state":100,"createTime":1750821895651}\]},"traceId":"","success":true,"errorCode":"SUCCESS","errorMsg":"操作成功"}

### 下面是前端如何处理SSE接口返回数据举例

// 定义一个异步函数，用于从接口中获取数据

const streamFetch = async () => {

// 定义接口地址

const url = "接口地址";

// 发送POST请求，并设置请求头和请求体

const response = await fetch(url, {

method: 'POST',

headers: {

'Content-Type': 'application/json',

},

credentials: 'include',

body: JSON.stringify({

query:"你好",

sessionId: '111'

})

}).then(response => {

// 获取响应体

const reader = response.body.getReader();

// 定义解码器和编码器

const decoder = new TextDecoder('utf-8');

const encoder = new TextEncoder();

// 定义缓存、流内容和执行链接内容

let buffer = '';

let streamContent = '';

let execLinkContent = '';

// 返回一个可读流

return new ReadableStream({

// 定义流的开始方法

async start(controller) {

// 定义一个推送函数

function push() {

// 读取响应体中的数据

reader

END

服务器推送技术和客户端主动请求

客户端主动请求包括:

服务器推送技术：

下面是前端如何处理SSE接口返回数据举例：

有什么问题，和我聊聊吧～

**

内部资料

INTERNAL

405832