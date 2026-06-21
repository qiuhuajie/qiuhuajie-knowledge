---
title: "IO 文件流"
tags:
  - "IO"
  - "IO_文件流"
  - "IO_流原理"
  - "IO_流体系"
  - "IO_流的分类"
  - "InputStream"
updated: 2026-04-16
aliases:
  - IO文件流
---

# 一、IO 流原理
1. Java程序中，对于数据的输入/输出操作以**“流(stream)”** 的方式进行
    1. 流定义为**代表任何有能力产出数据的数据源对象或者有能力接受数据的接收端对象**
    2. 流的本质其实就是**数据传输**，就是计算机各部件的数据流动；
2. Java IO 原理：
    1. 输入 `input`： 读取外部数据（磁盘、光盘等存储设备的数据）到程序（内存）中
    2. 输出 `output`： 将程序（内存）数据输出到磁盘、光盘等存储设备中
    > 💡 一个汉字占两个字节长度（因为汉字博大精深，所以有些汉字也会占到
    > **「三个字节」**的长度）
# 二、IO 流的分类
## 1. 按操作数据单位分
1. **字节流**
    1. 该类流每次读取数据的时候都会以字节作为基本单位进行数据的读取，通常都会有`InputStream`和`OutputStream`相关字眼
    2. 例如读取数据的时候每次如同下图所示，每次都按照字节**（`8bit-byte`）**进行加载

    ![[IMG-20260620222044292.png|563]]

2. **字符流**
    1. 该类流通常都会以字符的形式去读取数据信息，其读取的效率通常要比字节流更高效。相关的类通常都会带有`Reader`或者`Writer`相关字眼
    2. 例如读取数据的时候每次如同下图所示，每次都按照两个字节**（`16bit-char`）**进行加载
        > 💡 一个汉字占两个字节长度（因为汉字博大精深，所以有些汉字也会占到
        > **「三个字节」**的长度）
![[IMG-20260620222044383.png|514]]

3. ⭐**字符流和字节流的使用场景**
    1. 字符流通常比较适合用于读取一些**文本数据**，例如 txt 格式类型的文本，这类资源通常都是以字符类型数据进行存储，所以使用字符流要比字节流更加高效
    2. 而对于一些**二进制数据**，例如图片，mp4 这类资源比较适合用字节流的方式进行加载

## 2. 按数据流的流向分
1. 输入流：读外部数据比如磁盘等存储设备的数据到程序（内存）
2. 输出流：内存中的程序输出到磁盘、光盘等存储设备
> 💡 **输入是指从外界输入到内存，输出是指从内存输出到外界**
## 3. 按流的角色的不同分为
1. 节点流
    1. **直接对特定的数据源执行读写操作**
2. 处理流
    1. **对一个已经存在的流做一些二次封装操作，其功能更加比原先更加强大**
    2. 已有流的外边包的一层，如加速作用

# 三、IO 流体系

| 分类 | 字节输入流 | 字节输出流 | 字符输入流 | 字符输出流 | 类型 |
| --- | --- | --- | --- | --- | --- |
| 抽象接口（基类） | InputStream | OutputStream | Reader | Writer | 节点流 |
| 访问文件 | FileInputStream | FileOutputStream | FileReader | FileWriter | 节点流 |
| 访问数组 | ByteArrayInputStream | ByteArrayOutputStream | CharArrayReader | CharArrayWriter | 节点流 |
| 访问管道 | PipedInputStream | PipedOutputStream | PipedReader | PipedWriter | 节点流 |
| 访问字符串 |  |  | StringReader | StringWriter | 节点流 |
| 缓冲流 | BufferedInputStream | BufferedOutputStream | BufferedReader | BufferedWriter | 处理流 |
| 打印流 |  | PrintStream |  | PrintWriter | 处理流 |
| 对象流 | ObjectInputStream | ObjectOutputStream |  |  | 处理流 |
| 转换流 |  |  | InputStreamReader | OutputStreamWriter | 处理流 |
> 💡 `InputStream`、`OutputStream`、`Reader`、`Writer` 它们都是一些抽象基类，并不能直接用于创建对象实例
# 四、IO 流的类结构

![[IMG-20260620222044452.png|432]]

- **点击查看完整 Java 的 IO 类结构图**

    [![|578](http://web.deu.edu.tr/doc/oreily/java/fclass/figs/jfc_1101.gif)](http://web.deu.edu.tr/doc/oreily/java/fclass/figs/jfc_1101.gif)

> 💡 Java的IO结构， `FilterInputStream`是一个装饰者角色[[装饰器模式]]
