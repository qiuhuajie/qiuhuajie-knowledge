- [[#1. 原生 NIO 存在的问题]]
- [[#2. Netty 介绍⭐]]
    - [[#2.1 Netty 简介]]
    - [[#2.2 ⭐为什么选择 Netty❓]]
    - [[#2.3 Netty 的使用场景]]
    - [[#2.4 组件]]
    - [[#2.5 Netty 版本说明]]
# 1. 原生 NIO 存在的问题
1. **Java NIO 的类库和 API 繁杂，使用麻烦：**
    
    1. 需要熟练掌握 Selector、ServerSocketChannel、SocketChannel、ByteBuffer 等
    
    1. 需要具备其他的额外技能：要熟悉 Java 多线程编程，因为 NIO 编程涉及到 Reactor 模式，你必须对多线程和网络编程非常熟悉，才能编写出高质量的 NIO 程序
    
    1. 开发工作量和难度都非常大：例如客户端面临断连重连、网络闪断、半包读写、失败缓存、网络拥塞和异常流的处理等等
    
1. J**DK NIO 的 Bug：**
    
    1. 例如臭名昭著的 **`Epoll Bug`**，它会导致 Selector 空轮询，最终导致 CPU 100%
    
    1. 直到 JDK 1.7 版本该问题仍旧存在，没有被根本解决
    
# 2. Netty 介绍⭐
## 2.1 Netty 简介
1. **Netty is an asynchronous event-driven network application framework for rapid development of maintainable high performance protocol servers & clients**
1. ==**Netty**====是 一个====**异步、非阻塞、事件驱动**====的网络应用程序框架==，用于**快速开发可维护的高性能协议服务器和客户端**
1. 官网
    
    > [!info] Netty: Home  
    > Netty is an asynchronous event-driven network application framework for rapid development of maintainable high performance protocol servers & clients.  
    > [https://netty.io/index.html](https://netty.io/index.html)  
    
## 2.2 ⭐**为什么选择 Netty❓**
1. **简化 NIO 编程模型**：Java NIO 编程模型相对复杂，Netty 提供了一些现成的组件和 API，让开发人员更专注于业务逻辑的实现
1. **支持多种协议和编解码方式**：Netty 内置了多种常见的协议和编解码方式
    
    1. 例如 HTTP、WebSocket、TLS、SSL、JSON、Protobuf 等等，同时可以自定义解码器解决 TCP 粘包、拆包问题
    
    1. 这些协议和编解码方式可以直接使用，也可以进行自定义扩展
    
1. Netty 的架构设计具有良好的**可扩展性**
1. 社区活跃
1. **==性能上的优化：==**
    
    1. Netty 的**线程模型**采用了**主从 Reactor 模式**，实现了高效的事件处理和线程调度，提高了性能
    
    1. Netty 使用**零拷贝技术**，减少了由于系统调用和数据拷贝带来的 CPU 和内存的开销
    
    1. Netty 采用了**异步和事件驱动编程模型**，使得应用程序可以同时处理多个连接和请求，并且不会出现阻塞或死锁等问题
    
## 2.3 **Netty 的使用场景**
1. 作为 **RPC 框架的网络通信工具**
    
    1. 我们在分布式系统中，不同服务节点之间经常需要相互调用，这个时候就需要 RPC 框架了，可以使用 Netty 来实现
    
    1. 比如我调用另外一个节点的方法的话，至少是要让对方知道我调用的是哪个类中的哪个方法以及相关参数吧
    
1. 实现一个**即时通讯系统**：使用 Netty 我们可以实现一个可以聊天类似微信的即时通讯系统，这方面的开源项目还蛮多的，可以自行去 Github 找一找
1. 实现**消息推送系统**：市面上有很多消息推送系统都是基于 Netty 来做的
## 2.4 组件

![[IMG-20260404031811713.png]]

- 绿色的部分**Core**核心模块，包括零拷贝、API库、可扩展的事件模型
- 橙色部分**Protocol Support**协议支持，包括Http协议、webSocket、SSL(安全套接字协议)、谷歌Protobuf协议、zlib/gzip压缩与解压缩、Large File Transfer大文件传输等等
- 红色的部分**Transport Services**传输服务，包括Socket、Datagram、Http Tunnel等等
- 以上可看出Netty的功能、协议、传输方式都比较全，比较强大
## 2.5 Netty 版本说明
1. netty 版本分为 netty 3.x 和 netty 4.x、netty 5.x
1. 因为Netty5出现重大bug，已经被官网废弃了，目前**推荐使用的是 Netty 4.x 的稳定版本**
1. 目前在官网可下载的版本 netty 3.x netty 4.0.x 和 netty 4.1.x