---
title: "InputStreamReader 和 OutputStreamWriter"
tags:
  - "InputStreamReader"
  - "OutputStreamWriter"
  - "IO流"
  - "Java基础"
  - "语言特性"
  - "常用处理流"
updated: 2026-04-16
aliases:
  - InputStreamReader/OutputStreamWriter
---

# 一、介绍
1. 转换流：
    1. **OutputStreamWriter**：将一个字节输入流转换为字符输入流
    2. **InputStreamReader**：将一个字符输出流转换成字节输出流
2. 作用：提供字节流与字符流之间的转换

    ![[IMG-20260620222024465.png|446]]

## 1. 代码示例
## 2. 在读入文件时，使用UTF-8字符集；在写出文件时，使用GBK字符集
```Java
public static void main(String[] args) throws IOException {
    //这份文件默认是采用了utf-8编码
    String sourceFile = "C:/Users/lenovo/Desktop/25inputs.txt";
    String destPath = "C:/Users/lenovo/Desktop/2500inputs.txt";
    InputStreamReader isr = null;
    OutputStreamWriter osw = null;
    try {
        isr = new InputStreamReader(new FileInputStream(sourceFile),"utf-8"); //参数1：字节流；参数2：使用系统默认的字符集
        osw = new OutputStreamWriter(new FileOutputStream(destPath),"gbk"); //输出时：使用gbk字符集将字节转化成字符
        char[] chars = new char[1024];
        int len;
        while ((len = isr.read()) != -1){
            osw.write(chars, 0, len);
        }
    } catch (IOException e) {
        e.printStackTrace();
    } finally {
        isr.close();
        osw.close();
    }
}
```
# 二、常见的编码表
1. ASCII： 美国标准信息交换码：用**一个字节的7位**可以表示
2. ISO8859-1：拉丁码表，欧洲码表用一个字节的8位表示
3. GB2312： 最初的中文编码表，最多**两个字节编码**所有字符
4. GBK： 中文编码表升级，融合了更多的中文文字符号。最多两个字节编码
5. Unicode： 国际标准码， 融合了目前**人类使用的所有字符**。为每个字符分配唯一的字符码，所有的文字都用**两个字节**来表示，是对UTF-8、UCS-2/UTF-16等**具体编码方案的统称**而已，并不是具体的编码方案
6. UTF-8： 变长的编码方式，可用**1-4个字节**来表示一个字符，UTF-8就是每次8个位传输数据，而UTF-16就是每次16个位
