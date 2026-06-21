---
title: "synchronized"
tags:
  - "字节码指令"
  - "Java源代码"
  - "synchronized关键字"
  - "JVM"
  - "字节码"
  - "Java底层"
updated: 2026-04-16
---
# 一、Synchronized
## 1. Java源代码
```Java
 public class Demo {
     public static void main(String[] args) {
         Object lock = new Object();
         synchronized (lock) {
             System.out.println("ok");
         }
     }
 }
```
## 2. 字节码指令
- `dup` 指令会将 在操作数栈中的 lock 对象的引用复制一份，一份存到 slot 2另一份会被`monitorenter`指令执行消耗掉
- `monitorenter`：==会将对象引用加锁==，12 行后的指令就是加锁保护后的指令
- `monitorexit`：==会将对象解锁==
- 25 行至 27 行的指令，**可以保证在代码执行过程中如果出现异常，仍然可以保证被加锁的对象引用解锁**

    ![[IMG-20260620013634359.png|510]]