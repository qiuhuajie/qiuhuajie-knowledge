---
title: "PrintStream 和 PrintWriter"
tags:
  - "PrintStream"
  - "PrintWriter"
  - "IO流"
  - "IOException"
  - "Java基础"
  - "语言特性"
updated: 2026-04-16
aliases:
  - PrintStream/PrintWriter
---

# 一、介绍
1. 这两个流分别是基于字节和字符的输出打印流，实现将**基本数据类型的数据格式**转化为**字符串**输出
2. 提供了**一系列重载的** **`print()`** **和** **`println()`** **方法**，用于多种数据类型的输出
3. `PrintStream`和`PrintWriter`的输出不会抛出`IOException`异常
4. `PrintStream`和`PrintWriter`有自动`flush`功能
5. `PrintStream`打印的所有字符都使用平台的默认字符编码转换为字节；因此在需要写入字符而不是写入字节的情况下，应该使用 `PrintWriter`类
6. 其实在日常开发中经常会接触到`PrintStream`这款标准输出字节流，例如刚入门阶段所接触的`helloworld`案例，底层就是基于`PrintStream`去做的

    ```Java
    System.out.printf("hello world");
    ```
# 二、代码示例
## 1. PrintStream
```Java
public static void main(String[] args) throws IOException {
    PrintStream out = null;
    try {
        //重新设置流输出的位置,底层是一个native方法
        System.setOut(new PrintStream("C:/Users/lenovo/Desktop/25inputs.txt"));
        out = System.out;
        out.println("john hello");
        //底层也可以使用字节数组
        out.write("test".getBytes());
    } catch (IOException e) {
        e.printStackTrace();
    } finally {
        out.close();
    }
}
```
- `System.setOut` 可以把标准输出流（控制台输出）改成文件
    ![[IMG-20260404031802407.png|327]]
## 2. PrintWriter
```Java
public static void main(String[] args) throws IOException {
    PrintWriter out = null;
    try {
        //重新设置流输出的位置,底层是一个native方法控制
        out = new PrintWriter("C:/Users/lenovo/Desktop/25inputs.txt");
        out.println("john hello");
        //底层也可以使用字节数组
        out.write("test");
    } catch (IOException e) {
        e.printStackTrace();
    } finally {
        out.close();
    }
}
```

![[IMG-20260404031802407.png|327]]
