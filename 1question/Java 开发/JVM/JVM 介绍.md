---
title: "JVM 介绍"
tags:
  - "JVM"
  - "常见_JVM"
  - "JPS"
  - "PID"
  - "jstack_PID"
  - "线程"
updated: 2026-04-16
---
- [[#一、介绍]]
- [[#二、常见 JVM]]

# 一、介绍
1. 🙋‍♂️ **JVM（Java虚拟机）运行在用户态**
    1. JVM是一个软件程序，它在计算机上运行Java程序，并将Java字节码转换为可执行代码
    2. 当Java程序在JVM中运行时，JVM使用操作系统提供的系统调用来执行需要访问系统资源的任务，例如输入/输出和内存管理等
    3. 这些系统调用是在内核态执行的，但是JVM本身运行在用户态
2. **JVM 线程 和 操作系统线程 之间存在一种映射关系**
    1. 🙋‍♂️ **可以通过JVM提供的一些工具来查找一个 jvm 线程对应的操作系统的线程**
        1. 可以先使用 Java 命令行工具 **`jps`** 来获取Java进程的 PID
        2. 再使用 **`jstack PID`** 命令，可以输出当前Java进程的堆栈信息，包括 Java 线程和操作系统线程的堆栈信息
    2. 🙋‍♂️ **这种映射关系通过操作系统线程ID（Thread ID）和 JVM 线程ID（Java Thread ID）进行对应**
        1. 在大多数操作系统中，每个线程都有一个唯一的线程ID（Thread ID）
        2. 在Java虚拟机中，每个线程也有一个唯一的线程ID，称为Java Thread ID
        3. JVM会将Java Thread ID映射到操作系统线程ID，并在需要的时候将操作系统线程ID传递给操作系统调用

# 二、常见 JVM

![[IMG-20260619235511590.png|642]]

- 参考资料
    - https://www.javainterviewpoint.com/java-virtual-machine-architecture-in-java/
    - http://learnjvm.com/#/jvm/jvm_serial_00_why_learn_jvm
