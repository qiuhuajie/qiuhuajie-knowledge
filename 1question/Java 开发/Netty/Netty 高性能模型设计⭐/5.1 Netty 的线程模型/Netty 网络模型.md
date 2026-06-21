---
title: "Netty 网络模型"
tags:
  - "线程"
  - "Netty_网络模型"
  - "NioEventLoop"
  - "Netty"
  - "两组线程池"
  - "NioEventLoopGroup"
updated: 2026-04-16
---
- [[#一、Netty 的网络模型工作原理]]

# 一、Netty 的网络模型工作原理

> Scalable IO in Java 对 「主从 Reactor 多进程 / 线程」 的原理图解：
> ![[IMG-20260621000528571.png|523]]

![[IMG-20260621000528670.png|1086]]

1. **`NioEventLoopGroup`**：
    1. Netty抽象出**两组线程池**
        - **BossGroup 专门负责接收客户端的连接**
        - **WorkerGroup 专门负责网络的读写**
    2. BossGroup 和 WorkerGroup 类型都是 NioEventLoopGroup
    3. ==NioEventLoopGroup 相当于一个事件循环组，这个组中含有多个事件循环 ，每一个事件循环就是一个 NioEventLoop==
    4. NioEventLoopGroup 可以有多个线程，即可以含有多个 NioEventLoop
2. **`NioEventLoop`**：
    1. ==NioEventLoop 表示一个不断循环的执行处理任务的==**==线程==**
    2. 每个 NioEventLoop 都有一个 selector，用于监听绑定在其上的 socket 的网络通讯；还包含一个 taskQueue
3. **每个 Boss—NioEventLoop 循环执行的步骤：**
    1. 轮询 `accept` 事件
    2. 处理 `accept` 事件，与 client 建立连接 , 生成 NioScocketChannel，并将其注册到某个 worker NIOEventLoop 上的 selector
    3. 处理任务队列的任务，即 runAllTasks
4. **每个 Worker—NIOEventLoop 循环执行的步骤：**
    1. 轮询 `read`，`write` 事件
    2. 处理 `read`，`write` 事件，在对应 NioScocketChannel 处理
    3. 处理任务队列的任务 ，即 runAllTasks
5. 每个 Worker NIOEventLoop 处理业务时，会使用 `pipeline`（管道）
    1. pipeline 中包含了 channel，即通过 pipeline 可以获取到对应通道
    2. 管道中维护了很多的处理器 ChannelHandler
- 每个 NioChannel 只会绑定在唯一的 NioEventLoop 上
- 每个 NioChannel 都绑定有一个自己的 ChannelPipeline