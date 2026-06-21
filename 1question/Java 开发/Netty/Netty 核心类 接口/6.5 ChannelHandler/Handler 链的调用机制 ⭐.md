---
title: "Handler 链的调用机制 ⭐"
tags:
  - "ChannelPipeline"
  - "ChannelInboundHandler"
  - "ChannelOutboundHandler"
  - "Netty"
  - "MyServer"
  - "MyClient"
updated: 2026-04-16
---
- [[#一、调用机制介绍]]
- [[#二、代码示例验证]]
    - [[#1. 程序图示]]
    - [[#2. 服务端]]
    - [[#3. 客户端]]
- [[#三、运行结果]]

# 一、调用机制介绍
1. ⭐上面讲到 `ChannelPipeline` 中维护者一条由 `ChannelHandler` 串起来的链
2. **但其实 ==逻辑上== 是两条链：**
    - 入站链：由一个或多个 `ChannelInboundHandler` 串起来，用来处理入站事件，调用顺序和加入 `ChannelPipeline` 的顺序**一致**
    - 出站链：由一个或多个 `ChannelOutboundHandler` 串起来，用来处理出站事件，调用顺序和加入 `ChannelPipeline` 的顺序**相反**

    ![[IMG-20260621000555675.png|653]]

![[IMG-20260621000555783.png|797]]

3. 具体的业务逻辑就写在这一个个 `Handler` 中，当前 `Handler` 处理完后，就会将结果**根据当前是出站还是入站**，传给链上的下一个 `ChannelInboundHandler` 或 `ChannelOutboundHandler` 继续处理
4. debug 验证
    1. 所有的 `Handler` 物理上都是在一个 `head ➡️ tail` 的链上
    2. 但是 `ChannelInboundHandler` 和 `ChannelOutboundHandler` 会用两个标识 `inbound` 和 `outbound` 来区分是出站还是入站的 `Handler`
    3. 进而可以逻辑上分成两个链

    ![[IMG-20260621000555873.png|865]]

# 二、代码示例验证
## 1. 程序图示

![[IMG-20260621000555958.png|591]]

## 2. 服务端
1. `MyServer` 接受数据，加入的两个

    ```Java
    public class MyServer {
        public static void main(String[] args) throws Exception{
            EventLoopGroup bossGroup = new NioEventLoopGroup(1);
            EventLoopGroup workerGroup = new NioEventLoopGroup();
            try {
                ServerBootstrap serverBootstrap = new ServerBootstrap();
                serverBootstrap.group(bossGroup,workerGroup)
                        .channel(NioServerSocketChannel.class)
                        .childHandler(new ChannelInitializer<SocketChannel>() {
                            @Override
                            protected void initChannel(SocketChannel ch) throws Exception {
                                ChannelPipeline pipeline = ch.pipeline();
                                pipeline.addLast(new MyByteToLongDecoder());
                                pipeline.addLast(new MyServerHandler());
                            }
                        }); //自定义一个初始化类
                ChannelFuture channelFuture = serverBootstrap.bind(7000).sync();
                channelFuture.channel().closeFuture().sync();
            }finally {
                bossGroup.shutdownGracefully();
                workerGroup.shutdownGracefully();
            }
        }
    }
    ```
2. `MyByteToLongDecoder`

    ```Java
    public class MyByteToLongDecoder extends ByteToMessageDecoder {
        @Override
        protected void decode(ChannelHandlerContext ctx, ByteBuf in, List<Object> out) throws Exception {
            System.out.println("MyByteToLongDecoder decode() 被调用进行解码");
            // in 里起码还需要剩 8字节 以上才能，从中读出一个 long 来
            if (in.readableBytes() >= 8) {
                out.add(in.readLong());
            }
        }
    }
    ```
3. `MyServerHandler`

    ```Java
    public class MyServerHandler extends SimpleChannelInboundHandler<Long> {
        @Override
        protected void channelRead0(ChannelHandlerContext ctx, Long msg) throws Exception {
            System.out.println("MyServerHandler 接收数据");
            System.out.println("从客户端 " +ctx.channel().remoteAddress() + " 读取到的 Long 型数据：" + msg);
        }
        @Override
        public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
            cause.printStackTrace();
            ctx.close();
        }
    }
    ```
## 3. 客户端
1. `MyClient`

    ```Java
    public class MyClient {
        public static void main(String[] args)  throws  Exception{
            EventLoopGroup group = new NioEventLoopGroup();
            try {
                Bootstrap bootstrap = new Bootstrap();
                bootstrap.group(group).channel(NioSocketChannel.class)
                        .handler(new ChannelInitializer<SocketChannel>() {
                            @Override
                            protected void initChannel(SocketChannel ch) throws Exception {
                                ChannelPipeline pipeline = ch.pipeline();
                                pipeline.addLast(new MyLongToByteEncoder());
                                pipeline.addLast(new MyClientHandler());
                            }
                        });
                ChannelFuture channelFuture = bootstrap.connect("localhost", 7000).sync();
                channelFuture.channel().closeFuture().sync();
            }finally {
                group.shutdownGracefully();
            }
        }
    }
    ```
2. `MyLongToByteEncoder`

    ```Java
    public class MyLongToByteEncoder extends MessageToByteEncoder<Long> {
        @Override
        protected void encode(ChannelHandlerContext ctx, Long msg, ByteBuf out) throws Exception {
            System.out.println("MyLongToByteEncoder encode() 被调用进行编码");
            System.out.println("编码的数据：" + msg);
            out.writeLong(msg);
        }
    }
    ```
    > 💡`Long msg` ：不论解码器 handler 还是编码器 handler ，接收的消息类型必须与待处理的消息类型一致，否则该handler不会被执行
3. `MyClientHandler`

    ```Java
    public class MyClientHandler extends SimpleChannelInboundHandler<Long> {
        @Override
        protected void channelRead0(ChannelHandlerContext ctx, Long msg) throws Exception {
        }
        @Override
        public void channelActive(ChannelHandlerContext ctx) throws Exception {
            System.out.println("MyClientHandler 发送数据");
            // 发送的是一个long
            ctx.writeAndFlush(123456L); 
        }
    }
    ```
# 三、运行结果
1. 观察 `handler` 的执行顺序
2. 服务端输出

    ![[IMG-20260621000556044.png|452]]

3. 客户端输出

    ![[IMG-20260621000556135.png|461]]