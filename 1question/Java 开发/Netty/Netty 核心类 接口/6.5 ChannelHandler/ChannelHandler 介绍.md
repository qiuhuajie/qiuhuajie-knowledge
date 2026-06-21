---
title: "ChannelHandler 介绍"
tags:
  - "ChannelHandler"
  - "ChannelInboundHandler"
  - "ChannelOutboundHandler"
  - "ChannelPipeline"
  - "自定义Handler"
  - "ReferenceCountUtil"
updated: 2026-04-16
---
- [[#一、ChannelHandler 接口介绍]]
- [[#二、ChannelHandler 接口使用]]
- [[#三、ChannelInboundHandler]]
- [[#四、ChannelOutboundHandler]]

# 一、ChannelHandler 接口介绍
1. `ChannelHandler` 是一个接口
    1. ==**处理 I/O 事件或拦截 I/O 操作，处理完成后，将其转发到其**== ==**`ChannelPipeline`**==**（业务处理链）中的下一个处理程序，充当了处理入站和出站数据的应用程序逻辑的容器**==
    2. ChannelHandler 本身并没有提供很多方法，因为这个接口有许多的方法需要实现，方便使用期间，可以继承它的子类
    3. ChannelHandler 生命周期：

| 类型                | 描述                                              |
| ----------------- | ----------------------------------------------- |
| `handlerAdded`    | 当把 `ChannelHandler` 添加到 `ChannelPipeline` 中时被调用 |
| `handlerRemoved`  | 当把 `ChannelHandler` 从 `ChannelPipeline` 中移除时调用  |
| `exceptionCaught` | 当 `ChannelHandler` 在处理过程中出现异常时调用                |

2. ChannelHandler 及其实现类一览图

    ![[IMG-20260621000553141.png|525]]

![[IMG-20260621000553240.png|568]]

    - `ChannelInboundHandler`：用于处理入站 I/O 事件
    - `ChannelOutboundHandler`：用于处理出站 I/O 操作
    - `ChannelInboundHandlerAdapter`：用于处理入站 I/O 事件，处理入站数据以及各种状态的变化
    - `ChannelOutboundHandlerAdapter`：用于处理出站 I/O 操作，处理出站数据并且允许拦截所有的操作
    - `ChannelDuplexHandler`：用于处理入站和出站事件
3. **⭐`ChannelPipeline` 中维护者一条由 `ChannelHandler` 串起来的链**
4. **但其实 ==逻辑上== 是两条链：**
    - 入站链：由一个或多个 `ChannelInboundHandler` 串起来，用来处理入站事件，调用顺序和加入 `ChannelPipeline` 的顺序**一致**
    - 出站链：由一个或多个 `ChannelOutboundHandler` 串起来，用来处理出站事件，调用顺序和加入 `ChannelPipeline` 的顺序**相反**

    ![[IMG-20260621000555675.png|659]]

![[IMG-20260621000555783.png|743]]

5. 具体的业务逻辑就写在这一个个 `Handler` 中，当前 `Handler` 处理完后，就会将结果**根据当前是出站还是入站**，传给链上的下一个 `ChannelInboundHandler` 或 `ChannelOutboundHandler` 继续处理
# 二、ChannelHandler 接口使用
1. ⭐**在使用过程中不会直接使用这个`ChannelHandler` 接口，而是会使用子类型 `ChannelInboundHandlerAdapter` 和 `ChannelOutboundHandlerAdapter` ，**然后通过重写相应方法实现业务逻辑
2. 通过命名能看出这两个类是一个适配器，它们的父类是 `ChannelInboundHandler` 与 `ChannelOutboundHandler`
3. 例如之前TCP 和 Http 案例中：
    ![[IMG-20260621000553534.png|662]]
![[IMG-20260621000553624.png|743]]
# 三、ChannelInboundHandler
1. 实现 ChannelInboundHandler 接口（或ChannelInboundHandlerAdapter），就可以接收入站事件和数据，这些数据会被业务逻辑处理
2. 业务逻辑通常写在一个或者多个 ChannelInboundHandler 中
3. 在 `ChannelInboundHandler` 中可以获取网络数据并处理各种事件，下面列出了能处理的各种事件
    > 这些事件每一个都是 ChannelInboundHandler 中的方法，也即在
    > **自定义Handler**中需要重写的方法

| 事件 | 说明 |
| --- | --- |
| `channelRegistered` | 当 `Channel` 注册到它的 `EventLoop` 并且能够处理 I/O 时调用 |
| `channelUnregistered` | 当 `Channel` 从它的 `EventLoop` 中注销并且无法处理任何 I/O 时调用 |
| **`channelActive`** | 当 `Channel` 处于活动状态时被调用 |
| `channelInactive` | 当 `Channel` 不再是活动状态且不再连接它的远程节点时被调用 |
| **`channelReadComplete`** | 当 `Channel` 上的一个读操作完成时被调用 |
| **`channelRead`** | 当从 `Channel` 读取数据时被调用 |
| `channelWritabilityChanged` | 当 `Channel` 的可写状态发生改变时被调用 |
| `userEventTriggered` | 当 `ChannelInboundHandler.fireUserEventTriggered()` 方法被调用时触发 |

4. **ByteBuf 实例相关的内存的释放：**
    1. 在应用中可以通过 `channelRead` 方法读取网络数据
    2. 但通过直接继承 `ChannelInboundHandler` 的子类来说，使用 `channelRead` 方法需要注意**需要显示的释放与池化ByteBuf实例相关的内存**，为此Netty提供了一个实用方法：**`ReferenceCountUtil.release()`**方法，示例：

    ```Java
        @Sharable
        //Discradhandler扩展自ChannelInboundHandlerAdapter
        public class DiscardHandler extends ChannelInboundHandlerAdapter{
          @Override
          public void channelRead(ChannelHandlerContext ctx,Object msg){
            //释放msg
            ReferenceCountUtil.release(msg);
          }
        }
    ```
    3. Netty另外还提供了一个类来简化这一过程 `SimpleChannelInboundHandler` 类，这个类通过一个通过的过程**简化**了上面释放内存的操作，使用示例如下：

    ```Java
        public class DiscardHandler extends SimpleChannelInboundHandler<Object>{
          @Override
          public void channelRead0(ChannelHandlerContext ctx,Object msg){
                //在这里不需要显示的对资源msg进行释放
          }
        }
    ```
> **如果使用了继承 `SimpleChannelInboundHandler` 类的方法，还有一个方便之处：**
> 1. 在类继承语句 `SimpleChannelInboundHandler<Object>` 中就填入泛型的类型
> 2. 那么 `channelRead0()` 的 `msg` 入参就为该泛型类型，因此，就不必在 `channelRead0()` 方法中将 `msg` 强转了
> ![[IMG-20260621000553719.png|623]]


# 四、ChannelOutboundHandler
1. ChannelOutboundHandler 原理和 ChannelInboundHandler 一样，只不过它是用来处理出站数据的
2. **出站的数据和操作**由`ChannelOutboundHandler`接口处理，它定义的方法将会被 Channel、ChannelPipeline、ChannelHandlerContext 调用
3. 以客户端应用程序为例
    1. 如果事件的运动方向是从客户端到服务端的，那么我们称这些事件为出站的
    2. 即客户端发送给服务端的数据会通过 pipeline 中的一系列 ChannelOutboundHandler，并被这些 Handler 处理
    3. 反之则称为入站的，由 ChannelInboundHandler 处理
4. ChannelOutBoundHandler的强大之处在于**可以按需要推迟操作或者事件**
    1. 这样就可以处理一些相对复杂的请求
    2. 例如远程节点暂停写入，那么可以通过 ChannelOutboundHandler 的处理推迟冲刷操作并在稍后继续
5. ChannelOutboundHandler定义的处理方法：

| 方法 | 描述 |
| --- | --- |
| `bind` | 当请求将 `Channel` 绑定到本地地址时被调用 |
| `connect` | 当请求将 `Channel` 连接到远程节点时被调用 |
| `disconnect` | 当请求将 `Channel` 从远程节点断开时调用 |
| `close` | 当请求关闭 `Channel` 时调用 |
| `deregister` | 当请求将 `Channel` 从它的 `EventLoop` 注销时调用 |
| `read` | 当请求从 `Channel` 中读取数据时调用 |
| `flush` | 当请求通过 `Channel` 将入队数据冲刷到远程节点时调用 |
| `write` | 当请求通过 `Channel` 将数据写入远程节点时被调用 |