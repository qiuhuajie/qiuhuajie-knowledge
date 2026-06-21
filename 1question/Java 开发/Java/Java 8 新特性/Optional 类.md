---
title: "Optional 类"
tags:
  - "Optional_类"
  - "Optional"
  - "容器类"
  - "Java_8"
  - "Supplier"
  - "Consumer"
updated: 2026-04-16
---

# 一、Optional 类
1. **`Optional<T>`** 类(java.util.Optional) 是一个==**容器类**==
    1. 它可以保存类型T的值，代表这个值存在
    2. 或者仅仅保存 null，表示这个值不存在
2. 原来用 null 表示一个值不存在，现在 Optional 可以更好的表达这个概念。并且**可以避免空指针异常**
3. Optional 提供的方法
    1. 创建Optional类对象的方法：
        1. `Optional.of(T t)`: 创建一个 Optional 实例， **t必须非空**

    ```Java
     Person person = new Person();
     //person = null; //NullPointerException不可为空
     Optional<Person> person1 = Optional.of(person);
     System.out.println(person1);
    ```
        2. `Optional.empty()`: 创建一个空的 Optional 实例
        3. `Optional.ofNullable(T t)`： **t 可以为null**

    ```Java
     Person person = new Person();
     person = null;//可以为空
     Optional<Person> person2 = Optional.ofNullable(person);
     System.out.println(person2); //Optional.empty
    ```
    2. 判断 Optional 容器中是否包含对象：
        1. `boolean isPresent()`: 判断是否包含对象
        2. `void ifPresent(Consumer<? super T> consumer)` ： 如果有值，就执行Consumer接口的实现代码，并且该值会作为参数传给它
    3. 获取 Optional 容器的对象：
        1. `T get()`：如果调用对象包含值，返回该值，否则抛异常
        2. `T orElse(T other)`：如果有值则将其返回，否则返回指定的other对象
        3. `T orElseGet(Supplier<? extends T> other)` ： 如果有值则将其返回，否则返回由Supplier接口实现提供的对象
        4. `T orElseThrow(Supplier<? extends X> exceptionSupplier)` ： 如果有值则将其返回，否则抛出由Supplier接口实现提供的异常
4. 示例：

    ```Java
     //避免空指针异常，不再使用之前的多重判断套嵌
     if(xxx != null){
         if(xxx.yy != null){
             ...
         }
     }
    ```
    ```Java
     @Test
     public void test1() {
    		 Boy b = new Boy("张三");
    		 //b.getGrilFriend()可能为null
    		 //故用ofNullable()将b.getGrilFriend()包装成Optional
    		 Optional<Girl> opt = Optional.ofNullable(b.getGrilFriend());
    		 // 如果女朋友存在就打印女朋友的信息
    		 opt.ifPresent(System.out::println);
     }
     @Test
     public void test2() {
    		 Boy b = new Boy("张三");
    		 Optional<Girl> opt = Optional.ofNullable(b.getGrilFriend());
    		 // 如果有女朋友就返回他的女朋友，否则只能欣赏“嫦娥”了
    		 Girl girl = opt.orElse(new Girl("嫦娥"));
    		 System.out.println("他的女朋友是： " + girl.getName());
     }
    ```
