---
title: "CompletableFuture（CF） 介绍"
tags:
  - "CompletableFuture"
  - "runAsync"
  - "CompletionStage"
  - "异步"
  - "FutureTask"
  - "ForkJoinPool"
updated: 2026-04-16
---
- [[#一、CompletableFuture 简介]]
- [[#二、CompletableFuture 的使用]]
    - [[#1. 创建 CompletableFuture 对象]]
        - [[#1.1 参数说明]]
        - [[#1.2 创建 CompletableFuture 对象代码示例]]
    - [[#2. 使用 CompletableFuture 的优点]]

# 一、CompletableFuture 简介
1. ==**FutureTask 存在的缺陷：**==
    1. 随然可以达到 **多线程 ➕ 有返回 ➕ 异步执行** 的目的，简单的业务场景使用 Future 完全 OK
    2. 但 `get()` 方法在 Future 计算完成之前一直会处于阻塞状态，而 `isDone()` 方法会一直轮询查询执行结果容易耗费 CPU 资源
2. ==**CompletableFuture 做的改进：**==
    - **回调通知：**
        - 提供了一种观察者模式类似的机制，可以让任务执行完成后通知监听的一方
        - 任务完成了可以通知主线程
    - **多个任务前后依赖可以组合处理**
        - 将两个或多个异步计算合成一个异步计算，这几个异步计算相互独立，同时后面的计算又依赖前一个处理的结果
    - **选择计算速度最快的任务**
        - 当 Future 集合中某个任务最快结束时，返回执行最快任务的结果
3. CompletableFuture 类架构说明：CompletableFuture 同时实现了 `Future`接口和 `CompletionStage` 接口
    ![[IMG-20260619224416916.png|612]]
    > **`CompletionStage`** 接口说明：
    > 1. `CompletionStage` 代表异步计算过程中的某个阶段，一个阶段完成以后可能会触发另外一个阶段
    > 2. 其中，一个阶段的执行可以是一个 Function，Consumer 或者 Runable
    > 3. 类似于 Linux 系统的管道分隔符传参数 `ps -aux | grep nignx`
    > 4. 一个阶段的执行可能是被单个阶段的完成触发，也可能是由多个阶段一起触发

# 二、CompletableFuture 的使用
## 1. 创建 CompletableFuture 对象
1. 一般不使用 `new` 关键字来创建 CompletableFuture 对象，**因为这样创建的对象是功能不完整的（raw use：原始用法）**
    ![[IMG-20260619224417005.png|588]]
2. **⭐而是使用 4 个静态方法来创建 CompletableFuture 对象：**
    1. ==**`runAsync`**==
        1. `public static CompletableFuture<Void> runAsync(Runnable runnable)`
        2. `public static CompletableFuture<Void> runAsync(Runnable runnable, Executor executor)`
    2. ==**`supplyAsync`**==
        1. `public static <U> CompletableFuture<U> supplyAsync(Supplier<U> supplier)`
        2. `public static <U> CompletableFuture<U> supplyAsync(Supplier<U> supplier, Executor executor)`
### 1.1 参数说明
1. 这 4 个静态方法的核心差异主要看两个维度：任务有没有返回值，以及是否显式指定线程池。

| 参数 / 类型 | 含义 | 用在什么场景 |
| --- | --- | --- |
| `Runnable runnable` | 只执行一段逻辑，不返回结果 | 对应 `runAsync` |
| `Supplier<U> supplier` | 执行一段逻辑，并提供一个返回值 | 对应 `supplyAsync` |
| `Executor executor` | 指定异步任务使用哪个线程池执行 | 用于替换默认线程池 |

2. 如果没有传入 `Executor`，`CompletableFuture` 会默认使用 `ForkJoinPool.commonPool()` 执行异步任务。
3. 如果传入了 `Executor`，异步任务会交给指定线程池执行；线上业务通常更推荐显式传入自定义线程池，避免不同业务共用 `commonPool` 后互相影响。
4. `runAsync` 和 `supplyAsync` 的区别如下：

| 方法 | 返回值 | 适用场景 |
| --- | --- | --- |
| `runAsync` | `CompletableFuture<Void>` | 只需要异步执行任务，不关心任务结果 |
| `supplyAsync` | `CompletableFuture<T>` | 需要异步计算并返回结果，后续可以接 `thenApply`、`thenAccept` 等回调 |

5. `Supplier` 表示结果的提供者，所以 `supplyAsync` 创建出来的是带结果的异步任务；`Runnable` 只表示要执行的动作，所以 `runAsync` 创建出来的是不带业务结果的异步任务。

### 1.2 创建 CompletableFuture 对象代码示例
#### runAsync
1. 不传 `Executor` 时，默认使用 `ForkJoinPool.commonPool()`。
    ```Java
    public class CompletableFutureDemo {
        public static void main(String[] args) throws ExecutionException, InterruptedException {
            CompletableFuture<Void> voidCompletableFuture = CompletableFuture.runAsync(() -> {
                System.out.println(Thread.currentThread().getName()+"\t"+"started");
                try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
            });
            System.out.println(voidCompletableFuture.get());
        }
    }
    ```

    ![[IMG-20260619224417047.png|448]]

2. 传入 `Executor` 时，使用指定线程池执行异步任务。
    ```Java
    public class CompletableFutureDemo {
        public static void main(String[] args) throws ExecutionException, InterruptedException {
            ExecutorService threadPool = Executors.newFixedThreadPool(3);
            CompletableFuture<Void> voidCompletableFuture = CompletableFuture.runAsync(() -> {
                System.out.println(Thread.currentThread().getName()+"\t"+"started");
                try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
            }, threadPool);
            System.out.println(voidCompletableFuture.get());
            threadPool.shutdown();
        }
    }
    ```

    ![[IMG-20260619224417077.png|431]]

#### supplyAsync
1. 不传 `Executor` 时，默认使用 `ForkJoinPool.commonPool()`。
    ```Java
    public class CompletableFutureDemo {
        public static void main(String[] args) throws ExecutionException, InterruptedException {
            ExecutorService threadPool = Executors.newFixedThreadPool(3);
            CompletableFuture<String> stringCompletableFuture = CompletableFuture.supplyAsync(() -> {
                System.out.println(Thread.currentThread().getName() + "\t" + "started");
                try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
                return "supplyAsync task finish";
            });
            System.out.println(stringCompletableFuture.get());
        }
    }
    ```

    ![[IMG-20260619224417122.png|447]]

2. 传入 `Executor` 时，使用指定线程池执行异步任务，并返回计算结果。
    ```Java
    public class CompletableFutureDemo {
        public static void main(String[] args) throws ExecutionException, InterruptedException {
            ExecutorService threadPool = Executors.newFixedThreadPool(3);
            CompletableFuture<String> stringCompletableFuture = CompletableFuture.supplyAsync(() -> {
                System.out.println(Thread.currentThread().getName() + "\t" + "started");
                try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
                return "supplyAsync task finish";
            }, threadPool);
            System.out.println(stringCompletableFuture.get());
            threadPool.shutdown();
        }
    }
    ```

    ![[IMG-20260619224417152.png|449]]

## 2. 使用 CompletableFuture 的优点
1. 首先， CompletableFuture 可以满足 Future 接口的功能：==**异步**==

    ```Java
    public class CompletableFutureDemo {
        public static void main(String[] args) throws ExecutionException, InterruptedException {
            CompletableFuture<String> stringCompletableFuture = CompletableFuture.supplyAsync(() -> {
                System.out.println(Thread.currentThread().getName() + "\t" + "started");
                try { TimeUnit.SECONDS.sleep(2); } catch (InterruptedException e) { e.printStackTrace(); }
                return "supplyAsync task finish";
            });
            System.out.println("main task finish");
            System.out.println(stringCompletableFuture.get());
        }
    }
    ```

    ![[IMG-20260619224417196.png|440]]

2. 其次，CompletableFuture ⭐==**可以传入回调对象，当异步任务完成或者发生异常时，自动调用回调对象的回调方法**==
    - 1️⃣ 异步任务结束时： `whenComplete()` 会自动回调传入的回调对象的回调方法
    - 2️⃣ 异步任务出错时： `exceptionally()` 会自动回调传入的回调对象的回调方法
    - 3️⃣ 主线程设置好回调后，不再关心异步任务的执行，异步任务之间可以顺序执行

    ```Java
    public class CompletableFutureDemo {
        public static void main(String[] args) throws ExecutionException, InterruptedException {
            // 1.创建自定义线程池（如果使用默认的线程池，当主线程结束后，异步任务会立刻关闭）
            ExecutorService threadPool = Executors.newFixedThreadPool(3);
            try {
                // 2.使用有返回的 supplyAsync 静态方法执行异步任务
                CompletableFuture<Integer> integerCompletableFuture = CompletableFuture.supplyAsync(() -> {
                    System.out.println(Thread.currentThread().getName() + "\t" + "started");
                    // 3.使用随机数来模拟任务执行可能出现的情况
                    int result = ThreadLocalRandom.current().nextInt(10);
                    try { TimeUnit.SECONDS.sleep(2); } catch (InterruptedException e) { e.printStackTrace(); }
                    if (result > 6) {
                        // 模拟任务的异常执行
                        int age = 10 / 0;
                    }
                    // 4.返回结果
                    return result;
                }, threadPool).whenComplete((v, e) -> {
                    // 5.1️⃣当没有异常时，任务执行结束
                    if (e == null) {
                        System.out.println("supplyAsync task finish, result = " + v);
                    }
                }).exceptionally(e -> {
                    // 6.2️⃣出现异常则打印异常信息
                    e.printStackTrace();
                    System.out.println("exception: " + e.getCause() + e.getMessage());
                    return -1;
                });
                System.out.println("main task finish");
                // 3️⃣无需再由主线程获取异步任务的执行结果，而是由异步任务利用回调主动向主线程返回结果
                // System.out.println(integerCompletableFuture.get());
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                // 7.关闭资源
                threadPool.shutdown();
            }
        }
    }
    ```
    - 正常执行的情况：
        ![[IMG-20260619224417226.png|435]]
    - 异常执行的情况：
        ![[IMG-20260619224417311.png|749]]
