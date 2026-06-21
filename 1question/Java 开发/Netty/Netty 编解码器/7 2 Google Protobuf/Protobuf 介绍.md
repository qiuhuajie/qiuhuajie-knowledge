---
title: "Protobuf 介绍"
tags:
  - "Protobuf"
  - "Netty"
  - "RPC"
  - "StringEncoder"
  - "ObiectEncoder"
  - "StringDecoder"
updated: 2026-04-16
---
- [[#一、Netty 自带编码解码机制存在的问题]]
- [[#二、Google Protobuf]]

# 一、Netty 自带编码解码机制存在的问题
1. Netty 自身提供了一些 `codec`（编解码器），可以用来实现 POJO 对象或各种业务对象的编码和解码

    ![[IMG-20260621000613632.png|860]]

    1. Netty 提供的编码器
        - `StringEncoder`：对字符串数据进行编码
        - `ObiectEncoder`：对 Java 对象进行编码
    2. Netty 提供的解码器
        - `StringDecoder`：对字符串数据进行解码
        - `ObjectDecoder`：对 Java 对象进行解码
2. ⚠️**在开发场景下，传输的数据大部分情况下是一个** ==**实体对象**==**，但是 Netty 本身自带的** **`objectDecoder`** **和** **`objectEncoder`** **底层使用的仍是 Java 序列化技术，而 Java 序列化技术本身效率就不高，存在如下问题：**
    1. 无法跨语言，如客户端和服务器端不可以是不同的语言编写的
    2. 序列化后的体积太大，是二进制编码的 5 倍多
    3. 序列化性能太低

# 二、Google Protobuf
1. Protobuf 是 Google 发布的开源项目，全称 `Google Protocol Buffers`，是==**一种轻便高效的结构化数据存储格式**==
2. 也可以理解成一种**序列化与反序列化**，或**编码和解码**的一种规范
3. 可以用于结构化数据串行化，或者说序列化，因此，它很**适合做 数据存储 或 RPC**[[RPC 介绍]][[RPC 介绍]][[RPC 介绍]]
4. 参考文档：
    > ℹ️ Language Guide | Protocol Buffers | Google Developers
    > This guide describes how to use the protocol buffer language to structure your protocol buffer data, including .
    > [https://developers.google.com/protocol-buffers/docs/proto](https://developers.google.com/protocol-buffers/docs/proto)
5. Protobuf 特点：
    1. 支持跨平台、跨语言，即（客户端和服务器端可以是不同的语言编写的） (支持目前绝4大多数语言，例如 C++、C\#、Java、python 等)
    2. 高性能，高可靠性
6. 数据交换格式目前很多公司 `http + ison` ➡️ `tcp + protobuf`
7. **Protobuf 的使用：**
    1. Protobuf 是以 **`message`** 的方式来管理数据的
    2. 使用 protobuf 编译器能自动生成代码，Protobuf 是将类的定义使用 `.proto` 文件进行描述
    3. 然后通过 `protoc.exe` 编译器根据 `.proto` 自动生成Java文件
    4. 示意图：

    ![[IMG-20260621000613732.png|881]]