> [!important] 引言：
- [[#1. CompletableFuture 简介]]
- [[#2. CompletableFuture 的使用]]
    - [[#2.1 创建 CompletableFuture 对象]]
    - [[#2.2 使用 CompletableFuture 的优点]]
# 1. CompletableFuture 简介
1. ==**FutureTask 存在的缺陷：**==
    
    1. 随然可以达到 **多线程 ➕ 有返回 ➕ 异步执行** 的目的，简单的业务场景使用 Future 完全 OK
    
    1. 但 `get()` 方法在 Future 计算完成之前一直会处于阻塞状态，而 `isDone()` 方法会一直轮询查询执行结果容易耗费 CPU 资源
    
1. ==**CompletableFuture 做的改进：**==
    
    - **回调通知：**
        
        - 提供了一种观察者模式类似的机制，可以让任务执行完成后通知监听的一方
        
        - 任务完成了可以通知主线程
        
    
    - **多个任务前后依赖可以组合处理**
        
        - 将两个或多个异步计算合成一个异步计算，这几个异步计算相互独立，同时后面的计算又依赖前一个处理的结果
        
    
    - **选择计算速度最快的任务**
        
        - 当 Future 集合中某个任务最快结束时，返回执行最快任务的结果
        
    
1. CompletableFuture 类架构说明：CompletableFuture 同时实现了 `Future`接口和 `CompletionStage` 接口
    

    ![[IMG-20260405035413912.png|Untitled 471.png]]

    
    > [!important] **`CompletionStage` 接口说明：**
    > 
    > 1. `CompletionStage` 代表异步计算过程中的某个阶段，一个阶段完成以后可能会触发另外一个阶段
    > 
    > 1. 其中，一个阶段的执行可以是一个 Function，Consumer 或者 Runable
    > 
    > 1. 类似于 Linux 系统的管道分隔符传参数 `ps -aux | grep nignx`
    > 
    > 1. 一个阶段的执行可能是被单个阶段的完成触发，也可能是由多个阶段一起触发
    
# 2. CompletableFuture 的使用
## 2.1 创建 CompletableFuture 对象
1. 一般不使用 `new` 关键字来创建 CompletableFuture 对象，**因为这样创建的对象是功能不完整的（raw use：原始用法）**
    

    ![[IMG-20260404031741441.png|Untitled 1 342.png]]

    
1. **⭐而是使用 4 个静态方法来创建 CompletableFuture 对象：**
    
    1. ==**runAsync**==
        
        1. `public static CompletableFuture<Void> runAsync(Runnable runnable)`
        
        1. `public staticCompletableFuture<Void> runAsync(Runnable runnable, Executor executor)`
        
    
    1. ==**supplyAsync**==
        
        1. `public static <U> CompletableFuture<U> supplyAsync(Supplier<U> supplier)`
        
        1. `public static<U> CompletableFuture<U> supplyAsync(Supplier<U> supplier, Executor executor)`
        
    
    > [!important] 参数说明：
    > 
    > 1. `[[Export-e8249ac1-4ae1-42cd-83d5-041a266841fe/1question/Java 开发/Java/Java 8 新特性/Supplier|Supplier]]`[[Export-e8249ac1-4ae1-42cd-83d5-041a266841fe/1question/Java 开发/Java/Java 8 新特性/Supplier|Supplier]]
    > 
    > 1. `Executor executor`
    > 
    >     1. 如果没有指定 `Executor` 的方法，直接使用默认的 `ForkJoinPool.commonPool()` 作为它的线程池执行异步代码
    > 
    > > 为什么要这样设计？
    > 
    > 
    >     1. 如果指定线程池，则使用自定义的或者特别指定的线程池执行异步代码
    >  
    
    > [!important]
    > 
    > Supplier 表示结果的提供者，即在实例化后一定会有一个返回结果，因此 ==**runAsync 和 supplyAsync 的区别：**==
    > 
    > - **结果返回**:
    > 
    >     - `**supplyAsync**`: 返回一个包含结果的 `CompletableFuture<T>`，可以通过 `thenApply`、`thenAccept` 等方法来处理其结果。
    > 
    >     - `**runAsync**`: 返回一个 `CompletableFuture<Void>`，不返回任何结果，仅用于执行任务。
    > 
    > 
    > - **适用场景**:
    > 
    >     - `**supplyAsync**`: 用于需要计算并返回结果的异步任务。
    > 
    >     - `**runAsync**`: 用于只需执行某些操作而不需要结果的场景。
    >  
    
- **创建 CompletableFuture 对象代码示例**
    
    1. **runAsync**
        
        1. 不传 `Executor` 默认使用 `ForkJoinPool.commonPool()`
            
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
            

            ![[IMG-20260405035420321.png|Untitled 2 280.png]]

            
        
        1. 传入 `Executor`
            
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
            

            ![[Attachment/1question/Java 开发/JUC/线程池/CompletableFuture/IMG-20260405035422029.png|Untitled 3 211.png]]

            
        
    
    1. **supplyAsync**
        
        1. 不传 `Executor`
            
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
            

            ![[IMG-20260405035432940.png|Untitled 4 163.png]]

            
        
        1. 传入 `Executor`
            
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
            

            ![[IMG-20260405035433025.png|Untitled 5 132.png]]

            
        
    
## 2.2 使用 CompletableFuture 的优点
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
    

    ![[IMG-20260405035444832.png|Untitled 6 109.png]]

    
1. 其次，CompletableFuture ⭐==**可以传入回调对象，当异步任务完成或者发生异常时，自动调用回调对象的回调方法**==
    
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
        

        ![[IMG-20260405035505008.png|Untitled 7 87.png]]

        
    
    - 异常执行的情况：
        

        ![[IMG-20260405035511845.png|Untitled 8 69.png]]