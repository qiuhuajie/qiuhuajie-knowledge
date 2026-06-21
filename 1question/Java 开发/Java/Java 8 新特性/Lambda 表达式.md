---
title: "Lambda 表达式"
tags:
  - "Lambda_表达式"
  - "参数列表"
  - "一个参数"
  - "内存泄漏"
  - "线程"
  - "JVM"
updated: 2026-04-16
---

# 一、Lambda 表达式简介
1. Lambda 表达式
    1. 是在 Java 8 语言中引入的一种新的语法元素和操作符
    2. ==Lambda的本质：====**一个接口的实例**====，且该接口只能是一个函数式接口==
        > 💡 函数式接口：只有一个抽象方法，因此实例化时，不需要写方法名，唯一没有歧义
2. **Lambda 操作符 `->` ，它将 Lambda 分为两个部分：**
    1. ==左侧指定了 Lambda 表达式需要的====**参数列表**==
    2. ==右侧指定了 Lambda 体，是====**抽象方法的实现逻辑**====，也即 Lambda 表达式要执行的功能==
3. 从匿名类到 Lambda 的转换举例：
    1. 匿名类

    ```Java
    Comparator<Integer> comparator1 = new Comparator<>() {
        @Override
        public int compare(Integer o1, Integer o2) {
            return Integer.compare(o1,o2);
        }
    };
    int compare1 = comparator1.compare(12, 31);
    System.out.println(compare1);
    ```
    2. Lambda 表达式写法

    ```Java
    Comparator<Integer> comparator2 =(o1,o2) -> Integer.compare(o1,o2);
    int compare2 = comparator2.compare(51, 31);
    System.out.println(compare2);
    ```
        > 例子：[[5.1 生产者消息确认]]
    3. 方法引用写法

    ```Java
    Comparator<Integer> comparator3 = Integer :: compare;
    int compare3 = comparator3.compare(12, 31);
    System.out.println(compare3);
    ```
# 二、Lambda 表达式的使用（6种情况）
1. 无参，无返回值

    ```Java
     Runnable r1 = new Runnable() {
         @Override
         public void run() {
             System.out.println("hh");
         }
     };
     r1.run();
    ==================================================================
     Runnable r2 = () -> System.out.println("hh");
     r2.run();
    ```
2. Lambda 需要一个参数，但是没有返回值

    ```Java
     Consumer<String> consumer1 = new Consumer<String>() {
         @Override
         public void accept(String s) {
             System.out.println(s);
         }
     };
     consumer1.accept("hh");
    ==================================================================
     Consumer<String> consumer2 = (String s) -> System.out.println(s);
     consumer2.accept("hh");
    ```
3. **数据类型可以省略**，因为可由编译器推断得出，称为“类型推断”

    ```Java
     Consumer<String> consumer2 = (s) -> System.out.println(s);
    ```
4. Lambda 若只需要**一个参数**时， 参数的小括号可以省略

    ```Java
     Consumer<String> consumer2 = s -> System.out.println(s);
    ```
5. Lambda 需要**两个或以上的参数**，**多条执行语句**，**并且有返回值**

    ```Java
     Comparator<Integer> comparator2 =(o1, o2) ->{
         System.out.println(o1);
         System.out.println(o2);
         return o1.compareTo(o2);
     };
     int compare2 = comparator2.compare(51, 31);
     System.out.println(compare2);
    ```
6. 当 Lambda 体只有一条语句时， return与大括号若有，都可以省略
# 三、为什么 Lambdas 中使用的局部变量必须是 Final

![[IMG-20260620221658082.png|407]]

1. 如果 lambda 中需要访问 lambda 的外部类或外部对象中的变量，则该 lambda 成为**捕获 lambda（Capturing Lambdas）**
    1. 此时 lambda 需要保留对 lambda 外部环境的引用，lambda 捕获的变量在 lambda 表达式中是不可以修改的
    2. 因此为了代码编写的正确性，lambda 表达式不能访问非 final 的局部变量
2. 原因一：
    1. lambda 对变量的**操作是原变量的副本**
    2. 如果不加 final 的话菜鸟会认为传入的值可变，但是实际上又不可能（JVM 中 变量和 lambda 的变量不是一个栈），所以设计的时候要加个 final
3. 原因二：
    1. 放开 final 限制，**会引入局部变量的多线程 bug**
    2. 如果lambda中可以修改外部变量，一旦将一个 lambda 从一个线程传递给另一个线程，也必须将lambda捕获的变量也传递过去，一旦变量被修改，则会导致多线程问题
4. 原因三：
    1. lambda 的生命周期可能会比调用它的方法还要长，如果lambda中修改了其捕获的变量，很可能会导致**内存泄漏**
    2. 如果在一个方法中定义了 lambda，并将这个 lambda 通过 return 返回出去，这个 lambda 是个捕获 lambda，且捕获的变量能够被修改，则会导致方法的方法栈不能被回收，且有可能内存泄漏
