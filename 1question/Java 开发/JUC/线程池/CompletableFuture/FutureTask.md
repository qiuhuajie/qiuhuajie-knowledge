- [[#1. Future 接口]]
- [[#2. FutureTask 简介]]
- [[#3. FutureTask 使用]]
- [[#4. FutureTask 提供的方法]]
- [[#5. FutureTask 优点]]
- [[#6. FutureTask 缺点]]
    - [[#6.1 缺点1：get() 阻塞]]
    - [[#6.1 缺点2：isDone() 轮询]]
# 1. **Future 接口**
1. Future 接口是 Java 5 新加的一个接口，它提供了一种**==异步并行计算==**的功能
1. Future 接口可以为主线程开一个分支任务，专门为主线程处理耗时和费力的复杂业务
    
    1. **如果主线程需要执行一个很耗时的计算任务**
    
    1. **可以通过 Future 接口 把这个任务放到异步线程中，主线程继续处理其他任务或者先行结束，在通过 Future 获取计算结果**
    
1. Future 接口定义了操作异步任务执行一些方法，如
    
    - 获取异步任务的执行结果
    
    - 取消任务的执行
    
    - 判断任务是否被取消
    
    - 判断任务执行是否完毕
    
# 2. **FutureTask 简介**
1. **FutureTask 使用的场景：**
    
    1. 可用于异步获取执行结果或取消执行任务的场景
    
    1. FutureTask 非常适合用于耗时的计算，主线程可以在完成自己的任务后，再去获取结果
    
    1. FutureTask 还可以确保即使调用了多次 `run()` 方法，它都只会执行一次 Runnable 或者 Callable 任务
    
    1. 还可以通过 `cancel()` 取消 FutureTask 的执行等
    
1. 类图结构如下所示：
    

    ![[%E5%9B%BE%E5%83%8F_8 2.png|%E5%9B%BE%E5%83%8F_8 2.png]]

    
# 3. **FutureTask** 使用
- FutureTask 使用步骤：
    
    1. 通过传入 `Runnable` 或者 `Callable` 的任务给 FutureTask
    
    1. **直接调用其 `run()` 方法**或者**放入线程池执行**
    
    1. 之后可以在外部通过 FutureTask 的 `get()` 方法异步获取执行结果
    
```Java
public class Demo {
    public static void main(String[] args) throws ExecutionException, InterruptedException {
        FutureTask<String> futureTask =new FutureTask<>(new MyThread());
        Thread t1 =new Thread(futureTask, "t1");
        t1.start();
        System.out.println(futureTask.get());
    }
}
	
class MyThread implements Callable<String> {
    @Override
    public String call() throws Exception {
        System.out.println("task tarted");
        return"task finish";
    }
}
```

![[IMG-20260404031741834.png|Untitled 470.png]]

# 4. **FutureTask 提供的方法**

![[IMG-20260404031741888.png|Untitled 1 341.png]]

# 5. **FutureTask 优点**
- **FutureTask + 线程池 异步多线程任务配合，能显著提高程序的执行效率**
- 代码示例：
    
    1. **3 个任务，只使用一个 main 线程来处理**
        
        ```Java
        public class Demo {
            public static void main(String[] args) throws ExecutionException, InterruptedException {
                long startTime = System.currentTimeMillis();
                try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
                try { TimeUnit.MILLISECONDS.sleep(300); } catch (InterruptedException e) { e.printStackTrace(); }
                try { TimeUnit.MILLISECONDS.sleep(300); } catch (InterruptedException e) { e.printStackTrace(); }
                long endTime = System.currentTimeMillis();
                System.out.println("执行耗时：" + (endTime - startTime) + "毫秒");
            }
        }
        ```
        
        > [!important] 结果：执行耗时：1123 毫秒
        
    
    1. **3 个任务，开启 2 个异步线程来处理**
        
        ```Java
        public class Demo {
            public static void main(String[] args) throws ExecutionException, InterruptedException {
                long startTime = System.currentTimeMillis();
                // 1.使用线程池
                ExecutorService threadPool = Executors.newFixedThreadPool(3);
        
                // 2. task1 和 task2 使用 FutureTask 异步执行
                FutureTask<String> task1 = new FutureTask<String>(() -> {
                    try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
        
                    return "task1 finish";
                });
                threadPool.submit(task1);
        
                FutureTask<String> task2 = new FutureTask<String>(() -> {
                    try { TimeUnit.MILLISECONDS.sleep(300); } catch (InterruptedException e) { e.printStackTrace(); }
        
                    return "task2 finish";
                });
                threadPool.submit(task2);
        
                // 3. task3 使用 main 线程处理
                try { TimeUnit.MILLISECONDS.sleep(300); } catch (InterruptedException e) { e.printStackTrace(); }
        
                long endTime = System.currentTimeMillis();
                System.out.println("执行耗时：" + (endTime - startTime) + "毫秒");
        				
        				threadPool.shutdown();
            }
        }
        ```
        
        > [!important] 结果：执行耗时：358 毫秒，但这种情况并没有获取到执行结果
        
    
    1. **3 个任务，开启 2 个异步线程来处理，同时使用 `get()` 来获取异步执行的结果**
        
        ```Java
        public class Demo {
            public static void main(String[] args) throws ExecutionException, InterruptedException {
                long startTime = System.currentTimeMillis();
                // 1.使用线程池
                ExecutorService threadPool = Executors.newFixedThreadPool(3);
        
                // 2. task1 和 task2 使用 FutureTask 异步执行
                FutureTask<String> task1 = new FutureTask<String>(() -> {
                    try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
                    return "task1 finish";
                });
                threadPool.submit(task1);
                
                FutureTask<String> task2 = new FutureTask<String>(() -> {
                    try { TimeUnit.MILLISECONDS.sleep(300); } catch (InterruptedException e) { e.printStackTrace(); }
                    return "task2 finish";
                });
                threadPool.submit(task2);
        
        				// 3.获取执行结果
        				System.out.println(task1.get());
                System.out.println(task2.get());
        
                // 4. task3 使用 main 线程处理
                try { TimeUnit.MILLISECONDS.sleep(300); } catch (InterruptedException e) { e.printStackTrace(); }
        
                long endTime = System.currentTimeMillis();
                System.out.println("执行耗时：" + (endTime - startTime) + "毫秒");
        
                threadPool.shutdown();
            }
        }
        ```
        
        > [!important] 结果：
        > 
        > **大约可以节省 1/3 的执行时间**
        > 
        > task1 finish  
        > task2 finish  
        > 执行耗时：876毫秒
        
    
# 6. **FutureTask 缺点**
## 6.1 缺点1：get() 阻塞
1. `get()` 方法
    

    ![[IMG-20260405035420322.png|Untitled 2 279.png]]

    
    1. 一旦调用 `get()` 方法，不管是否计算完成，获取到执行结果才会继续执行，因此容易导致阻塞
    
    1. 一般建议放在程序最后执行
    
1. 代码示例
    
    1. 执行顺序：**task1 执行 ➡️ task2 执行 ➡️ 获取 task1 的执行结果**
        
        ```Java
        public class Demo {
            public static void main(String[] args) throws ExecutionException, InterruptedException {
                long startTime = System.currentTimeMillis();
        
                // 1. task1 使用 FutureTask 异步执行
                FutureTask<String> task1 = new FutureTask<String>(() -> {
                    try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
        
                    return "task1 finish";
                });
                Thread t1 = new Thread(task1, "t1");
                t1.start();
        
                // 2. task2 使用 main 线程处理
                try { TimeUnit.MILLISECONDS.sleep(300); } catch (InterruptedException e) { e.printStackTrace(); }
                System.out.println("task2 finish");
        
                // 3. 获取 task1 的执行结果
                System.out.println(task1.get());
        
                long endTime = System.currentTimeMillis();
                System.out.println("执行耗时：" + (endTime - startTime) + "毫秒");
            }
        }
        ```
        
        > [!important] 结果：
        > 
        > task2 finish  
        > task1 finish  
        > 执行耗时：556 毫秒
        
    
    1. 执行顺序：**task1 执行 ➡️ 获取 task1 的执行结果 ➡️ task2 执行**
        
        ```Java
        public class futureDemo {
            public static void main(String[] args) throws ExecutionException, InterruptedException {
                long startTime = System.currentTimeMillis();
        
                // 1. task1 使用 FutureTask 异步执行
                FutureTask<String> task1 = new FutureTask<String>(() -> {
                    try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
        
                    return "task1 finish";
                });
                Thread t1 = new Thread(task1, "t1");
                t1.start();
        
                // 2. 获取 task1 的执行结果
                System.out.println(task1.get());
        
                // 3. task2 使用 main 线程处理
                try { TimeUnit.MILLISECONDS.sleep(300); } catch (InterruptedException e) { e.printStackTrace(); }
                System.out.println("task2 finish");
                
                long endTime = System.currentTimeMillis();
                System.out.println("执行耗时：" + (endTime - startTime) + "毫秒");
            }
        }
        ```
        
        > [!important] 结果：⭐
        > 
        > **task2 的执行，会被 task1.get() 所阻塞**
        > 
        > task1 finish  
        > task2 finish  
        > 执行耗时：**867 毫秒**
        
    
1. **如果不希望 `get()` 等待太久，可以 传入一个超时时间 主动结束等待**
    

    ![[Attachment/1question/Java 开发/JUC/线程池/CompletableFuture/IMG-20260405035422030.png|Untitled 3 210.png]]

    
    ```Java
    // 获取 task1 的执行结果
    try {
        System.out.println(task1.get(1L, TimeUnit.SECONDS));
    } catch (TimeoutException e) {
        e.printStackTrace();
    }
    ```
    
## 6.1 缺点2：isDone() 轮询
1. `isDone()` 方法：
    

    ![[IMG-20260405035433048.png|Untitled 4 162.png]]

    
    1. 虽然将 `get()` 方法放在程序最后执行会避免阻塞，但是我们可以使用 `isDone()` 来优化获取执行结果的时机，更好的**避免阻塞**
    
    1. `isDone()` 方法可以通过**轮询**的方式，帮助主线程获取异步线程是否执行完成
    
1. 然而：⭐**轮询的方式会耗费无谓的CPU资源，而且也不见得能及时地得到计算结果**
1. 代码示例：
    
    ```Java
    public class futureDemo {
        public static void main(String[] args) throws ExecutionException, InterruptedException, TimeoutException {
    
            // 1. task1 使用 FutureTask 异步执行
            FutureTask<String> task1 = new FutureTask<String>(() -> {
                try { TimeUnit.MILLISECONDS.sleep(1500); } catch (InterruptedException e) { e.printStackTrace(); }
    
                return "task1 finish";
            });
            Thread t1 = new Thread(task1, "t1");
            t1.start();
    
            // 2. task2 使用 main 线程处理
            try { TimeUnit.MILLISECONDS.sleep(300); } catch (InterruptedException e) { e.printStackTrace(); }
            System.out.println("task2 finish");
    
            // 3. 获取 task1 的执行结果
            while (true){
                if (task1.isDone()) {
                    System.out.println(task1.get(1L, TimeUnit.SECONDS));
                    break;
                }else {
                    try { TimeUnit.MILLISECONDS.sleep(500); } catch (InterruptedException e) { e.printStackTrace(); }
                    System.out.println("task1 processing ... please wait");
                }
            }
        }
    }
    ```
    
    > [!important] 结果：
    > 
    > task2 finish  
    > task1 processing ... please wait  
    > task1 processing ... please wait  
    > task1 processing ... please wait  
    > task1 finish