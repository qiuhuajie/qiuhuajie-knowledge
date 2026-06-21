---
title: "Supplier"
tags:
  - "Supplier"
  - "不接受任何参数"
  - "接受单个输入参数"
  - "Consumer"
  - "方法引用"
  - "Java_8"
updated: 2026-04-16
---

# 一、介绍
1. Java Supplier是一**个功能接口，代表结果的提供者**
2. Supplier 在 Java 8 中被引入，属于 java.util.function 包，源代码如下

    ![[IMG-20260620221740706.png|537]]

    1. 可以看到，Supplier 的功能方法是 `get()` ，可以返回通用类型的值
    2. `get()` 方法不接受任何参数，只返回通用类型的值

# 二、实例化
1. 一个 Supplier 可以通过 lambda 表达式、方法引用或默认构造函数来实例化
2. lambda 表达式实例化：

    ```Java
    Supplier<String> s1 = () -> "Hello World!";
    System.out.println(s1.get());
    Random random = new Random();
    Supplier<Integer> s2 = () -> random.nextInt(10);
    System.out.println(s2.get());
    ```
3. 方法引用实例化：

    ```Java
    Supplier<String> s1 = MyUtil::getFavoriteBook;
    System.out.println(s1.get());
    ```
# 三、Java Supplier 与 Consumer 区别
1. `Java` `Supplier` 和 `Consumer` 都是功能接口
    1. `Supplier` 表示结果的提供者，该**结果返回一个对象**且**不接受任何参数**
    2. 而 `Consumer` 表示一个操作，其**接受单个输入参数**且**不返回任何结果**
2. 代码示例：

    ```Java
    public class SupplierConsumerDemo {
    	  public static void main(String[] args) {
    		    Supplier<String> s = Country::getPMName;
    		    Consumer<String> c = Country::printMessage;
    		    c.accept(s.get());
    	  }
    }
    class Country {
    	  public static String getPMName() {
    				return "Narendra Modi";
    	  }
    	  public static void printMessage(String msg) {
    				System.out.println(msg);
    	  }
    }
    ```

    输出：

```Java
Narendra Modi
```
