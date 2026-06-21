---
title: "方案 1：Netty + cglib"
tags:
  - "AddService"
  - "Netty"
  - "方案_1：Netty_+_cglib"
  - "NettyServer"
  - "NettyClient"
  - "ServerBootstrap"
updated: 2026-04-16
---
- [[#一、实现思路]]
- [[#二、服务提供端]]
    - [[#1. `AddService` 目标 API 接口]]
    - [[#2. `NettyServer`]]
    - [[#3. `NettyServerHandler`]]
    - [[#4. `ServerBootstrap`]]
- [[#三、服务消费端]]
    - [[#1. `NettyClient`]]
    - [[#2. `NettyClientHandler`]]
    - [[#3. `ClientBootstrap`]]
- [[#四、运行结果]]

# 一、实现思路

![[IMG-20260621000639853.png|795]]

# 二、服务提供端
## 1. `AddService` 目标 API 接口
```Java
public interface AddService {
    Integer add(Integer param1, Integer param2);
}
```
```Java
public class AddServiceImpl implements AddService {
    // 当有消费方调用该方法时，就会返回计算结果
    @Override
    public Integer add(Integer param1, Integer param2) {
        System.out.println("目标方法被调用，参数为：[" + param1 + "，" + param2 + "]，计算中...");
        return param1 + param2;
    }
}
```
## 2. `NettyServer`
```Java
public class NettyServer {
    public static void startServer(String hostName, int port) {
        startServer0(hostName,port);
    }
    // 完成对 NettyServer 的初始化和启动
    private static void startServer0(String hostname, int port) {
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
                              pipeline.addLast(new StringDecoder());
                              pipeline.addLast(new StringEncoder());
                              pipeline.addLast(new NettyServerHandler()); //业务处理器
                          }
                    });
            ChannelFuture channelFuture = serverBootstrap.bind(hostname, port).sync();
            System.out.println("服务提供端启动完成");
            channelFuture.channel().closeFuture().sync();
        }catch (Exception e) {
            e.printStackTrace();
        }
        finally {
            bossGroup.shutdownGracefully();
            workerGroup.shutdownGracefully();
        }
    }
}
```
## 3. `NettyServerHandler`
```Java
public class NettyServerHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
        System.out.println("收到服务消费端发来的参数：" + msg);
        // 进行协议头校验，要求 每次发消息是都必须以字符串开头 "HelloService\#hello#" 开头，后跟参数
        if(msg.toString().startsWith(ClientBootstrap.providerName)) {
            // ⭐调用目标 API 方法，将消费端发来的参数传入
            String substring = msg.toString().substring(msg.toString().lastIndexOf("#") + 1);
            String[] split = substring.split(",");
            Integer result = new AddServiceImpl().add(Integer.valueOf(split[0]), Integer.valueOf(split[1]));
            // 将执行结果写回给服务消费端
            ctx.writeAndFlush(String.valueOf(result));
        }
    }
    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
        ctx.close();
    }
}
```
## 4. `ServerBootstrap`
```Java
public class ServerBootstrap {
    public static void main(String[] args) {
        NettyServer.startServer("127.0.0.1", 7000);
    }
}
```
# 三、服务消费端
## 1. `NettyClient`
```Java
public class NettyClient implements MethodInterceptor {
    //创建线程池
    private static ExecutorService executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
    private static NettyClientHandler clientHandler;
    private String providerName;
    // 编写方法使用 cgLib 代理模式，获取一个代理对象
    public Object getProxyInstance(final Class<?> targetServiceClass, final String providerName){
        this.providerName = providerName;
        //1. 可以通过Enhancer对象的create()方法可以去生成一个类，用于生成代理对象
        Enhancer enhancer = new Enhancer();
        //2. 设置父类(将目标类作为代理类的父类)
        enhancer.setSuperclass(targetServiceClass);
        //3. 设置拦截器(回调对象为本身对象)
        enhancer.setCallback(this);
        //4. 生成一个代理类对象并返回给调用者
        return enhancer.create();
    }
    @Override
    public Object intercept(Object o, Method method, Object[] args, MethodProxy methodProxy) throws Throwable {
        if (clientHandler == null) {
            initClient();
        }
        // 根据协议，为参数添加协议头，并将参数赋给 clientHandler，方便其为服务提供端发送
        clientHandler.setPara(providerName + args[0] + "," + args[1]);
        // 主线程在发起远程调用后，肯定不能阻塞等待调用结果的返回，故需要使用新线程异步来执行
        // 由于 NettyClientHandler 实现了 Callable 接口，故可以将 NettyClientHandler 的一些业务代码放在 call() 方法中
        // 再使用 get() 获取 call() 方法的返回值
        return executor.submit(clientHandler).get();
    }
    // 初始化客户端
    private static void initClient() {
        NioEventLoopGroup group = new NioEventLoopGroup();
        Bootstrap bootstrap = new Bootstrap();
        bootstrap.group(group)
                .channel(NioSocketChannel.class)
                .option(ChannelOption.TCP_NODELAY, true)
                .handler(new ChannelInitializer<SocketChannel>() {
                        @Override
                        protected void initChannel(SocketChannel ch) throws Exception {
                            ChannelPipeline pipeline = ch.pipeline();
                            pipeline.addLast(new StringDecoder());
                            pipeline.addLast(new StringEncoder());
                            pipeline.addLast(clientHandler = new NettyClientHandler());
                        }
                });
        try {
            bootstrap.connect("127.0.0.1", 7000).sync();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```
> **代理的使用说明：**
> 1. **使用 cgLib 代理的原因**
>     1. 被代理的类是 `AddService` ，服务消费者只能获取到目标 API 的接口信息，并不能拿到具体的实现
>     2. 能拿到的话还要 RPC 远程调用干嘛，故被代理对象是一个接口，他自己本身并没有实现任何一个接口
>     3. 故想要获取代理对象的话只能使用 cgLib 代理[[代理模式 ⭐]]
> 2. **代理对象的方法增强实现与之前的代理案例的区别**
>     1. 之前的代理案例都是直接用代理对象通过反射来获取到被代理对象的方法，通过 `invoke()` 来调用
> ![[IMG-20260621000639964.png|766]]
>     2. 但是现在由于 RPC 场景下，消费端并不知道 API 的具体实现，**现在目标被代理对象的代码都不在本地，也就不可能通过反射拿到他的方法实**现
>     3. 因此这里代理对象里的方法使用 Netty 的网络编程来实现参数的传入和执行结果的接收
> （⭐之前的代理是在方法前后做加强，而现在是将方法逻辑做了完全替换，更何况被代理的逻辑都在服务提供端，消费端根本拿不到，谈何加强）
>     4. 可以看到 `intercept()` 方法里 `Object o, Method method, Object[] args, MethodProxy methodProxy` 这些参数都没有用，而是通过 Netty 来实现的方法远程调用
>     5. **这样服务消费端好像在调用本地的 `add()` 方法一样，但方法体内是一系列网络传输的逻辑，这就是 RPC**

## 2. `NettyClientHandler`
```Java
public class NettyClientHandler extends ChannelInboundHandlerAdapter implements Callable {
    // 上下文
    private ChannelHandlerContext context;
    // 保存调用的目标方法返回的结果
    private Integer result;
    // 保存消费端调用方法时，传入的参数
    private String para;
    //(2)
    void setPara(String para) {
        this.para = para;
    }
    // 与服务器的连接创建后，就会被调用, 这个方法是第一个被调用(1)
    @Override
    public void channelActive(ChannelHandlerContext ctx) throws Exception {
        // 在其它方法会使用到 ctx
        context = ctx;
    }
    // 收到服务器的数据后，调用方法 (4)
    @Override
    public synchronized void channelRead(ChannelHandlerContext ctx, Object msg) throws Exception {
        System.out.println(" channelRead 被调用  ");
        // 当收到服务提供端返回的调用结果后，将结果保存在 result 变量中
        result = Integer.valueOf((String) msg);
        // ⭐等到调用结果了，便可以唤醒等待的线程
        notify();
    }
    //被代理对象调用, 发送数据给服务器，-> wait -> 等待被唤醒(channelRead) -> 返回结果 (3)-》5
    @Override
    public synchronized Integer call() {
        try {
            // 将服务消费端设置的参数传给服务提供端
            context.writeAndFlush(para);
            System.out.println("参数已发送，wait...");
            // ⭐将服务消费端设置的参数传给服务提供端后，当前异步线程需要阻塞等待执行结果的返回
            wait();
            // ⭐当服务消费端的 channelRead() 方法读取到从服务提供端发来的执行结果后，会执行 notify()，该方法会唤醒一个在此对象监规器上等待的线程
            // 那么下面的代码就会继续执行
            System.out.println("收到调用结果，notified");
            // 将调用结果返回，这个返回值会由主线程中使用 get() 方法获取
            return  result;
        } catch (InterruptedException e) {
            e.printStackTrace();
            return null;
        }
    }
    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) throws Exception {
        cause.printStackTrace();
        ctx.close();
    }
}
```
> 💡 线程的
> **`get()`**、**`notify()`**、**`call()`** [[线程的创建]]
## 3. `ClientBootstrap`
```Java
public class ClientBootstrap {
    // 定义协议头
    public static final String providerName = "HelloService\#hello#";
    public static void main(String[] args) throws  Exception{
        //创建一个消费者
        NettyClient customer = new NettyClient();
        //创建代理对象
        AddService service = (AddService) customer.getProxyInstance(AddService.class, providerName);
        for (;; ) {
            Thread.sleep(2 * 1000);
            //通过代理对象调用服务提供者的方法(服务)
            Integer res = service.add(22, 11);
            System.out.println("调用的结果 res= " + res);
        }
    }
}
```
# 四、运行结果
1. 依此启动服务提供端和服务消费端
2. 结果打印：
    1. 服务提供端

    ![[IMG-20260621000640053.png|486]]

    2. 服务消费端

    ![[IMG-20260621000640139.png|488]]