- [[#1. Netty 的网络模型工作原理⭐]]

> [!important] Scalable IO in Java 对 「主从 Reactor 多进程 / 线程」 的原理图解：
> 
> ![[IMG-20260405035413967.png|Untitled 4 178.png]]
# 1. Netty 的网络模型工作原理⭐

![[IMG-20260405035413810.png|Untitled 368.png]]

1. `**NioEventLoopGroup**`**：**
    
    1. Netty抽象出**两组线程池**
        
        - **BossGroup 专门负责接收客户端的连接**
        
        - **WorkerGroup 专门负责网络的读写**
        
    
    1. BossGroup 和 WorkerGroup 类型都是 NioEventLoopGroup
    
    1. ==NioEventLoopGroup 相当于一个事件循环组，这个组中含有多个事件循环 ，每一个事件循环就是一个 NioEventLoop==
    
    1. NioEventLoopGroup 可以有多个线程，即可以含有多个 NioEventLoop
    
1. `**NioEventLoop**`**：**
    
    1. ==NioEventLoop 表示一个不断循环的执行处理任务的==**==线程==**
    
    1. 每个 NioEventLoop 都有一个 selector，用于监听绑定在其上的 socket 的网络通讯；还包含一个 taskQueue
    
1. **每个 Boss—NioEventLoop 循环执行的步骤：**
    
    1. 轮询 `accept` 事件
    
    1. 处理 `accept` 事件，与 client 建立连接 , 生成 NioScocketChannel，并将其注册到某个 worker NIOEventLoop 上的 selector
    
    1. 处理任务队列的任务，即 runAllTasks
    
1. **每个 Worker—NIOEventLoop 循环执行的步骤：**
    
    1. 轮询 `read`，`write` 事件
    
    1. 处理 `read`，`write` 事件，在对应 NioScocketChannel 处理
    
    1. 处理任务队列的任务 ，即 runAllTasks
    
1. 每个 Worker NIOEventLoop 处理业务时，会使用 `pipeline`（管道）
    
    1. pipeline 中包含了 channel，即通过 pipeline 可以获取到对应通道
    
    1. 管道中维护了很多的处理器 ChannelHandler
    
- 每个 NioChannel 只会绑定在唯一的 NioEventLoop 上
- 每个 NioChannel 都绑定有一个自己的 ChannelPipeline