---
title: "Supplier 与 Consumer"
tags:
  - "Supplier"
  - "Consumer"
  - "函数式接口"
  - "方法引用"
  - "Java_8"
updated: 2026-06-26
aliases:
  - "Consumer"
  - "Supplier"
---

# 一、Supplier
## 1. 介绍
1. Java Supplier是一**个功能接口，代表结果的提供者**
2. Supplier 在 Java 8 中被引入，属于 java.util.function 包，源代码如下

    ![[IMG-20260620221740706.png|537]]

    1. 可以看到，Supplier 的功能方法是 `get()` ，可以返回通用类型的值
    2. `get()` 方法不接受任何参数，只返回通用类型的值

## 2. 实例化
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
## 3. Supplier 与 Consumer 区别
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

# 二、Consumer
## 1. 介绍
1. **`Consumer<T>`** 是 `java.util.function` 包中的函数式接口，代表一个==接受单个输入参数且不返回结果的操作==。它和 `Supplier` 刚好相反：`Supplier` 只出不进，`Consumer` 只进不出。
	![[IMG-20260627224637133.png|567]]
2. 源码定义：
    ```java
    @FunctionalInterface
    public interface Consumer<T> {
        void accept(T t);
        default Consumer<T> andThen(Consumer<? super T> after) {
            Objects.requireNonNull(after);
            return (T t) -> { accept(t); after.accept(t); };
        }
    }
    ```
    1. 功能方法是 **`accept(T t)`**，接受一个泛型参数，无返回值。
    2. 默认方法 **`andThen()`** 可以把多个 Consumer 串联，按顺序对同一个输入执行多次操作。

## 2. 实例化
1. 和 Supplier 一样，Consumer 可以通过 [[Lambda 表达式|lambda 表达式]]、方法引用来实例化。
2. lambda 表达式实例化：
    ```java
    Consumer<String> printer = s -> System.out.println(s);
    printer.accept("Hello Consumer!");  // 输出：Hello Consumer!

    Consumer<Integer> doubler = n -> System.out.println(n * 2);
    doubler.accept(5);  // 输出：10
    ```
3. 方法引用实例化：
    ```java
    Consumer<String> printer = System.out::println;
    printer.accept("方法引用");  // 输出：方法引用
    ```

## 3. andThen 链式组合
1. **`andThen()`** 返回一个新的 Consumer，先执行当前操作，再执行参数中的操作，实现对同一个输入的多步处理。
	![[IMG-20260627225507966.png|563]]
2. 代码示例：
    ```java
    Consumer<String> toUpper = s -> System.out.println(s.toUpperCase());
    Consumer<String> printLength = s -> System.out.println("长度: " + s.length());

    Consumer<String> combined = toUpper.andThen(printLength);
    combined.accept("hello");
    // 输出：
    // HELLO
    // 长度: 5
    ```

## 4. 常用场景
### 4.1 集合遍历
* **`Iterable.forEach()`** 的参数就是 `Consumer<T>`，这是最常见的使用场景。
    ```java
    List<String> names = Arrays.asList("Alice", "Bob", "Charlie");
    names.forEach(name -> System.out.println(name));
    // 等价于方法引用
    names.forEach(System.out::println);
    ```
### 4.2 Stream 流操作
1. **`Stream.forEach()`** 和 **`Stream.peek()`** 都接受 Consumer。
2. `forEach` 是终端操作，用于消费流中的元素；`peek` 是中间操作，常用于调试。
    ```java
    List<Integer> nums = Arrays.asList(1, 2, 3, 4, 5);
    nums.stream()
        .filter(n -> n > 2)
        .peek(n -> System.out.println("过滤后: " + n))
        .forEach(n -> System.out.println("最终: " + n));
    ```
### 4.3 回调参数
1. 当一个方法需要"调用方告诉我拿到数据后怎么处理"时，用 `Consumer<T>` 做参数比 `Runnable` 更合适——因为 Consumer 能把数据传进去，而 `Runnable` 拿不到任何入参。
2. 典型例子是[[流式输出|流式输出改造]]中的 `streamWriter`：
    ```java
    // 定义：方法接受一个 Consumer 作为回调
    public void submitAndStreamPredict(Request req, Consumer<PredictStreamChunkVO> streamWriter) {
        // 每产生一个 chunk，就通过 streamWriter 推送
        streamWriter.accept(new PredictStreamChunkVO("增量文本"));
    }

    // 调用：MTOP 层传入具体实现
    appService.submitAndStreamPredict(request, chunk -> mtopStream.write(Result.of(chunk)));
    ```
    1. 调用方通过 lambda 决定"拿到 chunk 后怎么处理"（这里是写入 MTOP 流）。
    2. 被调用方只管调 `accept()`，不关心数据去了哪里——这就是 Consumer 做回调的解耦价值。
### 4.4 CompletableFuture.thenAccept
* **`thenAccept(Consumer<T>)`** 在异步任务完成后消费结果，不产生新的返回值，详见 [[CompletableFuture（CF） 介绍]]。
    ```java
    CompletableFuture.supplyAsync(() -> "异步结果")
        .thenAccept(result -> System.out.println("收到: " + result));
    ```

## 5. Consumer 变体

| 接口 | 参数 | 用途 |
| --- | --- | --- |
| `Consumer<T>` | 1 个泛型 | 通用单参数消费 |
| `BiConsumer<T, U>` | 2 个泛型 | 双参数消费，如 `Map.forEach((k, v) -> ...)` |
| `IntConsumer` | 1 个 int | 避免自动装箱的基本类型特化 |
| `LongConsumer` | 1 个 long | 同上 |
| `DoubleConsumer` | 1 个 double | 同上 |
| `ObjIntConsumer<T>` | 1 个泛型 + 1 个 int | 混合类型消费 |