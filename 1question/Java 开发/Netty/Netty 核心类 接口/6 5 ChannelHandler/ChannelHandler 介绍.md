- [[#1. ChannelHandler 接口介绍]]
- [[#2. ChannelHandler 接口使用]]
- [[#3. ChannelInboundHandler]]
- [[#4. ChannelOutboundHandler]]
# 1. ChannelHandler 接口介绍
1. `ChannelHandler` 是一个接口
    
    1. ==**处理 I/O 事件或拦截 I/O 操作，处理完成后，将其转发到其**== ==`**ChannelPipeline**`====**（业务处理链）中的下一个处理程序，充当了处理入站和出站数据的应用程序逻辑的容器**==
    
    1. ChannelHandler 本身并没有提供很多方法，因为这个接口有许多的方法需要实现，方便使用期间，可以继承它的子类
    
    1. ChannelHandler 生命周期：
        
        |   |   |
        |---|---|
        |**类型**|**描述**|
        |handlerAdded|当把ChannelHandler添加到ChannelPipeline中时被调用|
        |handlerRemoved|当把ChannelHandler在ChannelPipeline中移除时调用|
        |exceptionCaught|当ChannelHandler在处理过程中出现异常时调用|
        
    
1. ChannelHandler 及其实现类一览图
    
    ![[IMG-20260405035413941.png|Untitled 516.png]]
    
    ![[IMG-20260404031813807.png|Untitled 1 382.png]]
    
    - `ChannelInboundHandler`：用于处理入站 I/O 事件
    
    - `ChannelOutboundHandler`：用于处理出站 I/O 操作
    
    - `ChannelInboundHandlerAdapter`：用于处理入站 I/O 事件，处理入站数据以及各种状态的变化
    
    - `ChannelOutboundHandlerAdapter`：用于处理出站 I/O 操作，处理出站数据并且允许拦截所有的操作
    
    - `ChannelDuplexHandler`：用于处理入站和出站事件
    
1. **⭐`ChannelPipeline` 中维护者一条由 `ChannelHandler` 串起来的链**
1. **但其实 ==逻辑上== 是两条链：**
    
    - 入站链：由一个或多个 `ChannelInboundHandler` 串起来，用来处理入站事件，调用顺序和加入 `ChannelPipeline` 的顺序**一致**
    
    - 出站链：由一个或多个 `ChannelOutboundHandler` 串起来，用来处理出站事件，调用顺序和加入 `ChannelPipeline` 的顺序**相反**
        
        ![[IMG-20260405035413964.png|Untitled 2 311.png]]
        
        ![[IMG-20260404031813947.png|Untitled 3 233.png]]
        
    
1. 具体的业务逻辑就写在这一个个 `Handler` 中，当前 `Handler` 处理完后，就会将结果**根据当前是出站还是入站**，传给链上的下一个 `ChannelInboundHandler` 或 `ChannelOutboundHandler` 继续处理
# 2. ChannelHandler 接口使用
1. ⭐**在使用过程中不会直接使用这个`ChannelHandler` 接口，而是会使用子类型 `ChannelInboundHandlerAdapter` 和 `ChannelOutboundHandlerAdapter` ，**然后通过重写相应方法实现业务逻辑
1. 通过命名能看出这两个类是一个适配器，它们的父类是 `ChannelInboundHandler` 与 `ChannelOutboundHandler`
1. 例如之前TCP 和 Http 案例中：
![[IMG-20260404031814029.png|Untitled 4 179.png]]
![[IMG-20260404031814063.png|Untitled 5 145.png]]
# 3. **ChannelInboundHandler**
1. 实现 ChannelInboundHandler 接口（或ChannelInboundHandlerAdapter），就可以接收入站事件和数据，这些数据会被业务逻辑处理
1. 业务逻辑通常写在一个或者多个 ChannelInboundHandler 中
1. 在 `ChannelInboundHandler` 中可以获取网络数据并处理各种事件，下面列出了能处理的各种事件
    
    > [!important] 这些事件每一个都是 ChannelInboundHandler 中的方法，也即在
    > 
    > **自定义Handler**中需要重写的方法
    
    |   |   |
    |---|---|
    |**事件**|**说明**|
    |channelRegistered|当Channel注册到它的EventLoop并且能够处理I/O时调用|
    |channelUnregistered|当Channel从它的EventLoop中注销并且无法处理任何I/O时调用|
    |**channelActive**|当Channel处于活动状态时被调用|
    |channelInactive|当Channel不再是活动状态且不再连接它的远程节点时被调用|
    |**channelReadComplete**|当Channel上的一个读操作完成时被调|
    |**channelRead**|当从Channel读取数据时被调用|
    |channelWritabilityChanged|当Channel的可写状态发生改变时被调用|
    |userEventTriggered|当ChannelInboundHandler.fireUserEventTriggered()方法被调用时触发|
    
1. **ByteBuf 实例相关的内存的释放：**
    
    1. 在应用中可以通过 `channelRead` 方法读取网络数据
    
    1. 但通过直接继承 `ChannelInboundHandler` 的子类来说，使用 `channelRead` 方法需要注意**需要显示的释放与池化ByteBuf实例相关的内存**，为此Netty提供了一个实用方法：**`ReferenceCountUtil.release()`**方法，示例：
        
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
        
    
    1. Netty另外还提供了一个类来简化这一过程 `SimpleChannelInboundHandler` 类，这个类通过一个通过的过程**简化**了上面释放内存的操作，使用示例如下：
        
        ```Java
        public class DiscardHandler extends SimpleChannelInboundHandler<Object>{
          @Override
          public void channelRead0(ChannelHandlerContext ctx,Object msg){
                //在这里不需要显示的对资源msg进行释放
          }
        }
        ```
        
        > [!important] **如果使用了继承 `SimpleChannelInboundHandler` 类的方法，还有一个方便之处：**
        > 
        > 1. 在类继承语句 `SimpleChannelInboundHandler<Object>` 中就填入泛型的类型
        > 
        > 1. 那么 `channelRead0()` 的 `msg` 入参就为该泛型类型，因此，就不必在 `channelRead0()` 方法中将 `msg` 强转了
        >     
        >     ![[IMG-20260405035427229.png|Untitled 6 120.png]]
        >     
        
    
# 4. **ChannelOutboundHandler**
1. ChannelOutboundHandler 原理和 ChannelInboundHandler 一样，只不过它是用来处理出站数据的
1. **出站的数据和操作**由`ChannelOutboundHandler`接口处理，它定义的方法将会被 Channel、ChannelPipeline、ChannelHandlerContext 调用
1. 以客户端应用程序为例
    
    1. 如果事件的运动方向是从客户端到服务端的，那么我们称这些事件为出站的
    
    1. 即客户端发送给服务端的数据会通过 pipeline 中的一系列 ChannelOutboundHandler，并被这些 Handler 处理
    
    1. 反之则称为入站的，由 ChannelInboundHandler 处理
    
1. ChannelOutBoundHandler的强大之处在于**可以按需要推迟操作或者事件**
    
    1. 这样就可以处理一些相对复杂的请求
    
    1. 例如远程节点暂停写入，那么可以通过 ChannelOutboundHandler 的处理推迟冲刷操作并在稍后继续
    
1. ChannelOutboundHandler定义的处理方法：
    
    |   |   |
    |---|---|
    |**方法**|**描述**|
    |bind|当请求将Channel绑定到本地地址时被调用|
    |connet|当请求将Channel连接到远程节点时被调用|
    |disconnect|当请求将Channel从远程节点断开时调用|
    |close|当请求关闭Channel时调用|
    |deregister|当请求将Channel从它的EventLoop注销时调用|
    |read|当请求从Channel中读取数据时调用|
    |flush|当请求通过Channel将入队数据冲刷到远程节点时调用|
    |write|当请求通过Channel将数据写入远程节点时被调用|