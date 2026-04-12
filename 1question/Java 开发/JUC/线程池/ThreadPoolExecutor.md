- [[#1. 介绍]]
- [[#2. ThreadPoolExecutor 构造方法]]
    - [[#2.1 构造方法参数 🙋‍♂️]]
    - [[#2.2 如何配置线程数]]
- [[#3. Executors 工具类提供的几种线程池 🙋‍♂️]]
- [[#3. 线程池运行原理]]
- [[#4. 线程池的使用]]
    - [[#4.1 线程池的提交]]
    - [[#4.2 线程池的关闭]]
    - [[#4.3 线程池的异常处理]]
    - [[#4.4 如何正确使用线程池❓⭐]]
    - [[#4.5 线程池如何知道一个线程的任务已经执行完成 🙋‍♂️]]
- [[#5. 线程池场景题]]
- [[#6. Tomcat 线程池]]
- [[#7. 手写线程池🙋‍♂️]]
# 1. 介绍
1. 类结构
    

    ![[IMG-20260404031742221.png|Untitled 298.png]]

    
1. **线程池：** 一个管理线程的池子
1. **为什么要有线程池**❓
    
    1. **提前创建好多个线程，放入线程池中，使用时直接获取**，使用完放回池中
    
    1. ==**好处：**==
        
        - 统一分配管理线程
        
        - 提高响应速度（减少了创建新线程的时间）
        
        - 降低资源消耗（重复利用线程池中线程，不需要每次都创建）
        
    
# 2. ThreadPoolExecutor 构造方法
## 2.1 **构造方法参数** 🙋‍♂️

> [!important] **前五个是必要参数**
- `**corePoolSize**` **（主力业务员的数量）**🔑
    
    - 线程池中核心线程数
    
- **`maximumPoolSize` （主力业务员 加 后备业务员的数量）**
    
    - 最大线程数 =（非核心线程数 + 核心线程数）
    
    - 只有当 workQueue 是一个有界队列时，才会有非核心线程（后备业务员）的概念；如果是无界队列，只会使用核心线程来轮流处理任务
    
- **`workQueue` （营业厅的排队区）**🔑
    
    - 线程池等待队列，维护着等待执行的 Runnable 对象
    
    - workQueue 的数据结构是一个**阻塞队列**，不同的线程池会选用不同的阻塞队列
    
    - 这队列**建议应该为有界队列**，否则任务数过大或过多会导致等待队列占用内存过大，造成 **OOM**（见下 线程池异常）
    
- **`keepAliveTime` （后备业务员闲置后的存活时间）**
    
    - 非核心线程闲置下来不干活最多存活时间
    
- `**unit**`
    
    - 线程池中非核心线程保持存活的时间的单位
    
- **`hreadFactory`**
    
    - 创建一个新线程时使用的工厂，可以**用来设定线程名**
    
- **`handler`**
    
    - **等待队列的拒绝策略**
        
        - AbortPolicy ：**直接抛出 RejectedExecutionException 异常，这是线程池默认的拒绝策略**
        
        - CallerRunsPolicy：**让调用者运行当前提交的任务**
        
        - DiscardOldestPolicy：**丢弃最早被放入工作队列的任务，然后再尝试提交新的任务**
        
        - DiscardPolicy ：**当前提交任务直接丢弃**
        
    
    - 你也可以自己实现 **`RejectedExecutionHandler`** 接口来定义自己的拒绝策略
    

![[IMG-20260404031742268.png|Untitled 1 224.png]]

## 2.2 如何配置**线程数**
1. 线程在Java中属于稀缺资源，线程池不是越大越好（线程池数太大，可能会频繁的进行线程上下文切换和任务调度），但也不是越小越好
1. 对于==**计算密集型任务**==（大部分都在用CPU跟内存，加密，逻辑操作业务处理等）
    
    - 一般推荐线程池不要过大，一般是==**CPU数 + 1**==
    
    - 原因：**因为计算中可能存在**==**缺页中断**==**，如果多一个线程就可以将数据读入内存，避免了线程的上下文切换，将 CPU 的利用率最大化**
    
1. 对于==**IO密集型任务**==（数据库链接，网络通讯传输等）
    
    - 线程数要适当大一点，机器的 ==**CPU 数 * 2**==
    
    - 原因：**设置为 CPU 核心数的两倍可以**==**让 CPU 始终有足够的线程可执行**==**，但**==**不会因为过多的线程数**==**造成**==**过多的上下文切换**==**和**==**线程之间的竞争**==
    
# 3. Executors 工具类提供的几种**线程池** 🙋‍♂️
1. `Executors` 工具类中提供了多个不同种类线程池的创建方法，方法内都是使用 `ThreadPoolExecutor` 的构造函数来创建线程池
1. ⭐**为什么线程池不允许使用 `Executors` 去创建❓而是推荐直接通过** `ThreadPoolExecutor` **的方式❓**
    
    1. 这样的处理方式让写的同学更加明确线程池的运行规则，规避资源耗尽的风险
    
    1. **==Executors 各个方法的弊端：==**
        
        - newFixedThreadPool 和 newSingleThreadExecutor：主要问题是**使用**[[BlockingQueue]] **`LinkedBlockingQueue`，造成任务在队列中，耗费非常大的内存，甚至OOM**
        
        - newCachedThreadPool 和 newScheduledThreadPool：主要问题是**线程数最大数是** `**Integer.MAX_VALUE**`**，可能会创建数量非常多的线程，甚至OOM**
        
    
    1. ==**而且从实用性来说：**==
        
        1. 实际使用中需要根据**实际场景**来手动配置线程池的参数，比如核心线程数、使用的任务队列、饱和策略等等
        
        1. 应该显示地给我们的**线程池命名**，这样有助于我们定位问题
        
    
1. **`newFixedThreadPool` ：固定数目线程的线程池**
    

    ![[IMG-20260404031742304.png|Untitled 2 189.png]]

    
    - ==核心线程数 == 最大线程数（没有救急线程被创建），因此也无需超时时间==
    
    - 阻塞队列是无界的，可以放任意数量的任务
    
    - 适用于任务量已知，相对耗时的任务
    
    - **缺点：**使用的是无界的阻塞队列 `LinkedBlockingQueue`，存在隐患：如果任务太多，处理不过来，可能会导致队列的任务越积越多，导致机器内存 OOM
    
1. **`newSingleThreadExecutor` ：单线程线程池**
    

    ![[IMG-20260405035421952.png|Untitled 3 144.png]]

    
    - 线程池中始终只有一个线程，依次执行队列中的任务
    
    - **缺点：**和固定线程池一样，使用的是无界的阻塞队列 `LinkedBlockingQueue`，存在隐患，会导致机器内存 OOM
    
    - 🙋‍♂️适用于==串行执行任务==的场景，一个任务一个任务地执行
    
    - ==自己创建一个单线程串行执行任务，如果任务执行失败而终止那么没有任何补救措施，而线程池还会新建一个线程，保证池的正常工作==
    
1. **`newCachedThreadPool` ：缓存线程池**
    

    ![[IMG-20260405035429049.png|Untitled 4 117.png]]

    
    - 核心线程数是 0，最大线程数是 `Integer.MAX_VALUE`，救急线程可以无限创建，救急线程的空闲生存时间是 60s
    
    - 也即，线程池线程数会根据任务量不断增长，没有上限，当任务执行完毕，空闲 1 分钟后释放线程
    
    - 适合任务数比较密集，且每个任务执行时间较短的情况
    
    - 队列==采用了== `SynchronousQueue` ==实现特点是，它没有容量，没有线程来取是放不进去的（一手交钱、一手交货）==
    
1. **`newScheduledThreadPool` ：调度线程池**
    

    ![[IMG-20260405035441947.png|Untitled 5 96.png]]

    

    ![[IMG-20260405035503453.png|Untitled 6 82.png]]

    
    - 最大线程数是 `Integer.MAX_VALUE`，救急线程可以无限创建，救急线程的空闲生存时间是 0s
    
    - 返回一个用来==在给定的延迟后运行任务==或者==定期执行任务==的线程池
    
    - 周期性执行任务的场景，且需要限制线程数量的场景
    
    - 队列采用了 `DelayedWorkQueue` ：每个元素都有一个过期时间，只有在过期时才能被消费
    
# 3. 线程池运行原理

> [!important] 为什么要这么设计❓
> 
> 1. ==减少线程创建和销毁的开销==：线程的创建和销毁是一个相对昂贵的操作，涉及到内存分配、资源绑定等操作。通过预先创建一定数量的线程，并将它们保存在线程池中，减少了系统的开销
> 
> 1. ==控制并发线程数量==：过多的线程会导致系统资源的竞争和浪费。线程池通过设置线程池大小，可以控制并发线程的数量
> 
> 1. ==根据实际需求合理分配系统资源，提高资源利用率==：通过复用线程、线程的异步执行以及任务队列等机制，线程池可以根据系统负载情况==动态调整线程数量==
> 
> 1. 通过合理的任务排队和调度机制，==可以根据系统负载情况和优先级，来调度任务的执行顺序==，比如当线程池中的线程全部繁忙时，新的任务可以被放入任务队列中等待执行
🙋‍♂️
![[IMG-20260405035510734.png|Untitled 7 69.png]]
1. ==线程池刚创建时，里面没有一个线程==
1. 任务队列是作为参数传进来的。不过，就算队列里面有任务，线程池也不会马上执行它们
1. 当调用 `execute()` 方法添加一个任务时，线程池会做如下判断：
    
    - 如果正在运行的线程数量小于 `corePoolSize`，那么马上创建线程运行这个任务
    
    - 如果正在运行的线程数量大于或等于 `corePoolSize`，那么将==尝试将这个任务放入队列==
        
        - 如果这时候队列未满，则将==任务放进队列等待==
        
        - 如果这时候队列满了
            
            - 如果正在运行的线程数量小于 `maximumPoolSize`，那么还是要创建==非核心线程运行这个任务==
            
            - 如果正在运行的线程数量大于或等于 `maximumPoolSize`，那么线程池会==根据拒绝策略来对应处理==
            
        
    
1. 当一个线程完成任务时，它会从队列中取下一个任务来执行
1. 当一个线程无事可做，超过一定的时间（`keepAliveTime`）时，线程池会判断
    
    - 如果当前运行的线程数大于 corePoolSize，那么这个线程就被停掉
    
    - 所以线程池的所有任务完成后，它最终会收缩到 corePoolSize 的大小
    
1. 类比银行办理业务
    

    ![[IMG-20260405035518800.png|Untitled 8 56.png]]

    
1. 示例：
    

    ![[IMG-20260405035526241.png|Untitled 9 49.png]]

    
# 4. 线程池的使用
## 4.1 线程池的提交
1. `**execute()**` 用于提交==**不需要返回值的任务**==
    
    ```Java
    ExecutorService executorService = Executors.newCachedThreadPool();
    
    executorService.execute(() -> {
        System.out.println("run");
    });
    
    executorService.shutdown();
    ```
    
1. **`submit()`** 方法用于提交**==需要返回值的任务==**
    
    - 线程池会返回一个 **`Future`** 类型的对象，通过这个 **`Future`** 对象可以判断任务是否执行成功
    
    - 并且可以通过 **`Future`** 的 **`get()`** 方法来获取返回值
    
    ```Java
    Future<Object> future = executorService.submit(() -> {
    		System.out.println("hello");
    }); 
    
    try { 
    		Object s = future.get(); 
    } catch (InterruptedException e) { 
        // 处理中断异常 
    } catch (ExecutionException e) { 
        // 处理无法执行任务异常 
    } finally { 
        // 关闭线程池 executor.shutdown();
    }
    ```
    
1. 其他方法
    
    ```Java
    // 提交 tasks 中所有任务
    <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks) throws InterruptedException;
    
    // 提交 tasks 中所有任务，带超时时间
    <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks, long timeout, TimeUnit unit) throws InterruptedException;
    
    // 提交 tasks 中所有任务，哪个任务先成功执行完毕，返回此任务执行结果，其它任务取消
    <T> T invokeAny(Collection<? extends Callable<T>> tasks) throws InterruptedException, ExecutionException;
    ```
    
## 4.2 线程池的关闭
1. 关闭线程池
    
    1. `shutdownNow()` ：**==能立即停止线程池，正在跑的和正在等待的任务都停下了==**
    
    1. `shutdown()` ：**==只是关闭了提交通道，即让==** `submit()` **==无效；但内部的任务还会继续跑，跑完再彻底停止线程池==**
    
1. 它们的原理是遍历线程池中的工作线程，然后逐个调用线程的 `interrupt()` 方法来中断线程
    

    ![[IMG-20260405035531939.png|Untitled 10 42.png]]

    
## 4.3 线程池的异常处理

> [!important] 在Java中，线程池执行任务时产生的异常默认
> 
> **不会直接抛出到上层**
1. 在使用线程池处理任务的时候，可能会抛出一些异常
    
    - 线程池本身导致的异常，例如：不断地新建线程，导致线程消耗完成了服务器的所有资源
    
    - 提交任务到任务队列已满异常
    
    - 业务异常
    
1. **如何避免**
    
    1. 线程池一定要==设置====**最大线程数**====，防止不停的创建线程==，导致消耗掉服务器所有的资源
    
    1. 线程池的==阻塞队列尽量设置为====**有界队列**====，防止不停的添加任务==，可能把服务器的资源消耗完成
    
    1. ==对于==**==可预见的异常==**==尽量进行捕获处理==
    
1. 🙋‍♂️**处理方式**
    
    1. **主动捕获**
        
        ```Java
        ExecutorService pool = Executors.newFixedThreadPool(1);
        
        pool.submit(() -> {
        		try {
        				log.debug("task1");
        				int i = 1 / 0;
        		} catch (Exception e) {
        				log.error("error:", e);
        		}
        });
        ```
        
    
    1. **借助 Future，发生的异常会封装在返回的 Future 对象中**
        
        ```Java
        ExecutorService pool = Executors.newFixedThreadPool(1);
        Future<Boolean> f = pool.submit(() -> {
        		log.debug("task1");
        		int i = 1 / 0;
        		return true;
        });
        log.debug("result:{}", f.get());
        ```
        
    
## 4.4 如何正确使用线程池❓⭐
1. **正确**==**声明**==**一个线程池**，线程池必须手动通过 `ThreadPoolExecutor` 的构造函数来声明，不使用 `Executors`
1. **正确的**==**配置**==**线程池的各个**==**参数**==，如核心线程数
1. **在线程池和** ==**Threadlocal**== **同时使用时，会有**==**内存泄露**==**的风险[[Threadlocal]]**
1. **建议**==**不同类别的业务**==**用**==**不同的线程池**==**，根据业务的自身情况配置线程池**
1. **初始化线程池的时候需要**==**显示命名**==**（设置线程池名称前缀），**==**有利于定位问题**==
## 4.5 线程池如何知道一个线程的任务已经执行完成 🙋‍♂️
1. **方式一：使用 `submit()` 提交任务**
    
    - 线程池会返回一个 `Future` 类型的对象，通过这个 `Future` 对象可以判断任务是否执行成功
    
    - 并且可以通过 `Future` 的 `get()` 方法来获取返回值，当线程中的任务没有执行完之前，`get()` 方法会一直阻塞
    
1. **方式二：使用** `**CountDownLatch**` **计数器**
    
    - 计数器初始化为 1，主线程调用 `await()` 去阻塞等待计数器减至 0
    
    - 在任务的 `run()` 中，当任务执行完成，调用 `countDown()`，让计数器减一，从而唤醒主线程
    
# 5. 线程池场景题
1. 🙋‍♂️**现在有一个任务提交到了线程池，这个任务本来应该执行3秒就返回结果，但是等了50秒才得到结果，等待的期间系统一直没有日志输出，是为什么，怎么改进？**
    
    - 可能有几种原因导致这种情况发生：
        
        1. **线程池中的线程数量不足：**
            
            1. 如果线程池中的线程数量不足，可能会导致任务等待较长时间才能得到执行
            
            1. 可以通过==增加线程池中的线程数量==来改进这个问题
            
        
        1. **任务中存在耗时的操作：**
            
            1. 任务本身的实现可能存在一些耗时的操作，比如I/O操作、网络请求等。这些操作会阻塞线程的执行，导致任务等待的时间变长
            
            1. 可以通过==异步方式执行这些耗时操作==，或者将这些操作放在单独的线程中执行，以避免阻塞线程池中的线程
            
        
        1. **优化代码逻辑：**如果任务执行时间长的原因是代码逻辑的问题，你可以==对代码进行优化==，提高执行效率
        
        1. **日志输出被阻塞：**
            
            1. 如果日志输出被阻塞，可能会导致无法及时记录任务的执行情况
            
            1. 可以通过==异步方式记录日志==，或者将日志输出放在单独的线程中执行，以避免阻塞线程池中的线程
            
        
    
# 6. Tomcat 线程池

![[IMG-20260405035532039.png|Untitled 11 37.png]]

# 7. 手写线程池🙋‍♂️
1. 线程池把线程和任务进行解耦，线程归线程，任务归任务，摆脱了通过 Thread 创建线程时“一个线程必须对应一个任务”的限制
1. 在线程池中，同一个线程可以从 BlockingQueue 中不断提取新任务来执行
    
    1. 其核心原理在于线程池==对 Thread 进行了==**==封装==（**`**WorkerThread**`**）**，==并不是每次执行任务都会调用 Thread.start() 来创建新线程==
    
    1. 🙋‍♂️而是**让每个线程去执行一个==“循环任务”==，在这个“循环任务”中，**==**不停地检查是否还有任务等待被执行，如果有则直接去执行这个任务，也就是调用任务的 run 方法**==
    
    1. 把 run 方法当作和普通方法一样的地位去调用，相当于把每个任务的 run 方法串联了起来，所以线程数量并不增加
    

![[IMG-20260405035534552.png|Untitled 12 34.png]]

> [!info]  
> 
> [https://mp.weixin.qq.com/s?search_click_id=10789442690320761556-1683422470395-5704438496&__biz=MzkxNzIyMTM1NQ==&mid=2247491473&idx=1&sn=4faebe245817a8f04a3d526a912c1749&chksm=c142a515f6352c03646bce4c664cefeb4ddc537379592eca8b7475941625c7b6c0369983493d&key=c869eb3d99c172287c6db98f0c13a86d419e80b1c839395ad0f97a6d18bc2389a6261480347d26b6b56b06e391b79693f5b0e5bb4739865ff56b1d5cd266b638fbd705be9f197bf0af81eefac1ebcd7554b61349e72b8afd70d156c570334c8ce403ece850f75df9b02024ed62902e0c6b715caaf3574d4f6b6df273218a6114&ascene=0&uin=MzkwMTI3NDcw&devicetype=Windows+10+x64&version=6309021a&lang=zh_CN&countrycode=CN&exportkey=n_ChQIAhIQryfRO0BQaJS0IA+CVN7rNxLgAQIE97dBBAEAAAAAAD6gI3fF1lQAAAAOpnltbLcz9gKNyK89dVj07IArXpi9ImIYkU3v8nHKD2GqNrNc0JBI3qgprKpDLyzuHp0wFSv1dniDm7KwbQWhS2ECq/p06eZUn3wWFfE6smzb93M3n6oN/HwfbutRkbcRASPm/L08TYOuP0tOrKDbFRggjAqgKD12634HrBph4cvqNC3MO8BL6DHA0U7bCLIGU1cOVTY2L179SfdR4tQPRjr19R3sthLQONzdjV2+5gYE4QftLcaqPMxEtgxT5N3cHRbg37Oz8ZlH&acctmode=0&pass_ticket=kbV5j3p32BpR9HBV/OFWOGsDCzSlNLohy1L7so8uRQN/fwiXyf30uBZM6Bd4QiHsqoiAN8v4VNkgHKMCGu5eCA==&wx_header=1](https://mp.weixin.qq.com/s?search_click_id=10789442690320761556-1683422470395-5704438496&__biz=MzkxNzIyMTM1NQ==&mid=2247491473&idx=1&sn=4faebe245817a8f04a3d526a912c1749&chksm=c142a515f6352c03646bce4c664cefeb4ddc537379592eca8b7475941625c7b6c0369983493d&key=c869eb3d99c172287c6db98f0c13a86d419e80b1c839395ad0f97a6d18bc2389a6261480347d26b6b56b06e391b79693f5b0e5bb4739865ff56b1d5cd266b638fbd705be9f197bf0af81eefac1ebcd7554b61349e72b8afd70d156c570334c8ce403ece850f75df9b02024ed62902e0c6b715caaf3574d4f6b6df273218a6114&ascene=0&uin=MzkwMTI3NDcw&devicetype=Windows+10+x64&version=6309021a&lang=zh_CN&countrycode=CN&exportkey=n_ChQIAhIQryfRO0BQaJS0IA+CVN7rNxLgAQIE97dBBAEAAAAAAD6gI3fF1lQAAAAOpnltbLcz9gKNyK89dVj07IArXpi9ImIYkU3v8nHKD2GqNrNc0JBI3qgprKpDLyzuHp0wFSv1dniDm7KwbQWhS2ECq/p06eZUn3wWFfE6smzb93M3n6oN/HwfbutRkbcRASPm/L08TYOuP0tOrKDbFRggjAqgKD12634HrBph4cvqNC3MO8BL6DHA0U7bCLIGU1cOVTY2L179SfdR4tQPRjr19R3sthLQONzdjV2+5gYE4QftLcaqPMxEtgxT5N3cHRbg37Oz8ZlH&acctmode=0&pass_ticket=kbV5j3p32BpR9HBV/OFWOGsDCzSlNLohy1L7so8uRQN/fwiXyf30uBZM6Bd4QiHsqoiAN8v4VNkgHKMCGu5eCA==&wx_header=1)  
1. 线程池是一个典型的生产者-消费者模型
    
    - 调用方不断向线程池中提交任务（生产者）
    
    - 线程池中有一组线程（`threads`），不断地从队列中取任务（消费者）
    
    - 线程池管理一个任务队列（`taskQueue`），对异步任务进行缓冲 （缓冲区）
        

        ![[IMG-20260405035534599.png|Untitled 13 33.png]]

        
    
1. 🟡 **自定义线程池类 `SimpleThreadPool`**
    
    1. 线程池中维护两个集合资源
        
        - `BlockingQueue<Runnable> taskQueue` ：任务队列，直接使用并发包下的集合类，保证线程安全，同时提供了阻塞/唤醒机制
        
        - `List<WorkerThread> threads` ：用于存放和管理工作线程的集合
        
    
    1. 同时还需要一些字段设置：初始化时的线程数量、核心线程数、最大线程数、空闲线程的存活时间、是否已经被停止的标志位 `isShutdown` 、拒绝策略
    
    1. `SimpleThreadPool()`：构造方法，对线程池中的字段进行初始化；同时，还需要创建一定数量的工作线程，并启动它们
    
    1. `execute()`：提交任务到线程池
        
        1. 首先判断，线程池是否被关闭（停止提交）
        
        1. 接着比较当前线程池的线程数与设置的核心线程数大小
            
            1. 小于：表示当前核心线程数还没打满，可以直接向工作线程的集合 `threads` 中添加一个新的线程，并 `start()` 启动；同时将传入的任务添加到任务队列 `taskQueue` 中
            
            1. 大于：需要再判断任务对了是否已满
                
                1. 如果任务队列没满，则直接将提交的任务添加到任务队列中，`taskQueue.offer(task)`
                
                1. 如果队列满（`taskQueue.offer(task)` 返回失败），判断当前线程数是否超过了最大线程数
                    
                    1. 如果超过：则采取设置的拒绝策略，来处理当前提交的任务
                    
                    1. 如果没超过：则向工作线程的集合 `threads` 中添加一个新的线程，并 `start()` 启动；同时将传入的任务添加到任务队列 `taskQueue` 中
                    
                
            
        
    
    1. `shutdown()`：
        
        1. 将标志位 `isShutdown` 设置为 `true`
        
        1. 遍历工作线程的集合 `threads` ，将所有线程中断
        
    
    1. `shutdownNow()`：
        
        1. 将标志位 `isShutdown` 设置为 `true`
        
        1. 遍历工作线程的集合 `threads` ，将所有线程中断
        
        1. 将当前任务队列 `taskQueue` 中的剩余任务保存下来，并以列表的形式返回
        
    
1. 🟡 **工作线程类 `WorkerThread`**
    
    1. 维护空闲线程的存活时间、任务队列 `taskQueue`、工作线程的集合 `threads`
    
    1. 实现 `Thread` 类，重写 `run` 方法，在方法中
        
        1. 一直循环从任务队列中取出任务来执行，如果队列为空，则阻塞等待。直接利用集合的 `taskQueue.poll(阻塞等待时间)`
        
        1. 如果可以取出任务，将取出的任务直接执行，如果取不出则一直阻塞等待（空闲），同时判断线程的存活时间，如果超出了存活时间，则将当前线程从 `threads` 中移除，并结束循环
        
        1. 如果执行期间，发生异常也需要将当前线程从 `threads` 中移除，并结束循环
        
    
1. 代码实现
    
    1. `ThreadPool`
        
        ```Java
        public interface ThreadPool {
        
            // 提交任务到线程池
            void execute(Runnable task);
        
            // 优雅关闭
            void shutdown();
        
            //立即关闭
            List<Runnable> shutdownNow();
        }
        ```
        
    
    1. `SimpleThreadPool`
        
        ```Java
        public class SimpleThreadPool implements ThreadPool {
            // 线程池初始化时的线程数量
            private int initialSize;
            // 线程池最大线程数量
            private int maxSize;
            // 线程池核心线程数量
            private int coreSize;
            // 任务队列
            private BlockingQueue<Runnable> taskQueue;
            // 用于存放和管理工作线程的集合
            private List<WorkerThread> threads;
            // 是否已经被shutdown标志
            private volatile boolean isShutdown = false;
            // 默认的拒绝策略
            private final static RejectedExecutionHandler DEFAULT_REJECT_HANDLER = new DiscardPolicy();
            // 拒绝策略成员变量
            private final RejectedExecutionHandler rejectHandler;
            // 线程空闲时长
            private long keepAliveTime;
        
            public SimpleThreadPool(int initialSize, int maxSize, int coreSize, int queueSize, long keepAliveTime) {
                this(initialSize, maxSize, coreSize, queueSize, keepAliveTime, DEFAULT_REJECT_HANDLER);
            }
        
            public SimpleThreadPool(int initialSize, int maxSize, int coreSize, int queueSize, long keepAliveTime, RejectedExecutionHandler rejectHandler) {
                System.out.printf("初始化线程池: initialSize: %d, maxSize: %d, coreSize: %d%n", initialSize, maxSize, coreSize);
                // 初始化参数
                this.initialSize = initialSize;
                this.maxSize = maxSize;
                this.coreSize = coreSize;
                taskQueue = new LinkedBlockingQueue<>(queueSize);
                threads = new ArrayList<>(initialSize);
                this.rejectHandler = rejectHandler;
                this.keepAliveTime = keepAliveTime;
        
                // 初始化方法，创建一定数量的工作线程，并启动它们
                for (int i = 0; i < initialSize; i++) {
                    WorkerThread workerThread = new WorkerThread(keepAliveTime, taskQueue, threads);
                    workerThread.start();
                    threads.add(workerThread);
                }
            }
        
            @Override
            public void execute(Runnable task) {
                // 线程池是否被关闭（停止提交）
                if (isShutdown) {
                    throw new IllegalStateException("ThreadPool is shutdown");
                }
        
                // 获取到参数传入的的任务
                RunnableWrapper wrapper = (RunnableWrapper) task;
                System.out.printf("put task: %s %n" , wrapper.getTaskId());
        
                // 当线程数量小于核心线程数时，创建新的线程
                if (threads.size() < coreSize) {
                    addWorkerThread(task);
                    System.out.printf("小于核心线程数，创建新的线程: thread count: %d, queue remainingCapacity : %d%n", threads.size(), taskQueue.remainingCapacity());
                } else if (!taskQueue.offer(task)) {
                    // 当队列已满时，且线程数量小于最大线程数量时，创建新的线程
                    if (threads.size() < maxSize) {
                        addWorkerThread(task);
                        System.out.printf("队列已满, 创建新的线程: thread count: %d, queue remainingCapacity : %d%n", threads.size(), taskQueue.remainingCapacity());
                    } else {
                        rejectHandler.rejectedExecution(task, this);
                    }
                } else {
                    System.out.printf("任务放入队列: thread count: %d, queue remainingCapacity : %d%n", threads.size(), taskQueue.remainingCapacity());
                }
            }
        
        
            // 创建新的线程，并执行任务
            private void addWorkerThread(Runnable task) {
                WorkerThread workerThread = new WorkerThread(keepAliveTime, taskQueue, threads);
                workerThread.start();
                threads.add(workerThread);
                // 任务放入队列
                try {
                    taskQueue.put(task);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
        
        
            // 关闭线程池, 等待所有线程执行完毕
            @Override
            public void shutdown() {
                System.out.printf("shutdown thread, count: %d, queue remainingCapacity : %d%n", threads.size(), taskQueue.remainingCapacity());
                // 修改状态
                isShutdown = true;
                for (WorkerThread thread : threads) {
                    // 中断线程
                    thread.interrupt();
                }
            }
        
            @Override
            public List<Runnable> shutdownNow() {
                System.out.printf("shutdown thread now, count: %d, queue remainingCapacity : %d%n", threads.size(), taskQueue.remainingCapacity());
        
                // 修改状态
                isShutdown = true;
                // 清空队列
                List<Runnable> remainingTasks = new ArrayList<>();
                taskQueue.drainTo(remainingTasks);
        
                // 中断所有线程
                for (WorkerThread thread : threads) {
                    thread.interrupt();
                }
                // 返回未执行任务集合
                return remainingTasks;
            }
        }
        ```
        
    
    1. `WorkerThread`
        
        ```Java
        // 定义一个工作线程类
        public class WorkerThread extends Thread {
            private List<WorkerThread> threads;
            // 空闲时长
            private long keepAliveTime;
            // 用于从任务队列中取出并执行任务
            private BlockingQueue<Runnable> taskQueue;
        
            // 构造方法，传入任务队列
            public WorkerThread(long keepAliveTime, BlockingQueue<Runnable> taskQueue, List<WorkerThread> threads) {
                this.keepAliveTime = keepAliveTime;
                this.taskQueue = taskQueue;
                this.threads = threads;
            }
        
            // 重写run方法
            @Override
            public void run() {
                long lastActiveTime = System.currentTimeMillis();
                Runnable task;
                // 循环执行，直到线程被中断（线程池中线程可以被复用的原因）
                while (!Thread.currentThread().isInterrupted() || !taskQueue.isEmpty()) {
                    try {
                        // 从任务队列中取出一个任务，如果队列为空，则阻塞等待
                        task = taskQueue.poll(keepAliveTime, TimeUnit.MILLISECONDS);
        
                        RunnableWrapper wrapper = (RunnableWrapper) task;
                        if (task != null) {
                            System.out.printf("WorkerThread %s, poll current task: %s%n", Thread.currentThread().getName(), wrapper.getTaskId());
                            task.run();
                            lastActiveTime = System.currentTimeMillis();
                        } else if (System.currentTimeMillis() - lastActiveTime >= keepAliveTime) {
                            // 队列里没任务了，计算从线程池中移除
                            threads.remove(this);
                            System.out.printf("WorkerThread %s exit %n", Thread.currentThread().getName());
                            break;
                        }
                    } catch (Exception e) {
                        // 从线程池中移除
                        System.out.printf("WorkerThread %s occur exception%n", Thread.currentThread().getName());
                        threads.remove(this);
                        e.printStackTrace();
                        // 如果线程被中断，则退出循环
                        break;
                    }
                }
            }
        }
        ```
        
    
    1. `RunnableWrapper`
        
        ```Java
        public class RunnableWrapper implements Runnable{
            private final Integer taskId;
        
            public RunnableWrapper(Integer taskId) {
                this.taskId = taskId;
            }
        
            public Integer getTaskId() {
                return this.taskId;
            }
        
            @Override
            public void run() {
                System.out.println("Task " + taskId + " is running.");
                try {
                    Thread.sleep(100);
                } catch (Exception e) {
                    e.printStackTrace();
                    // ignore
                }
                System.out.println("Task " + taskId + " is completed.");
            }
        }
        ```
        
    
    1. `RejectedExecutionHandler`
        
        ```Java
        // 拒绝策略接口
        public interface RejectedExecutionHandler {
            // 参数：r 代表被拒绝的任务，executor 代表线程池对象
            void rejectedExecution(Runnable r, ThreadPool executor);
        }
        ```
        
    
    1. `DiscardPolicy`
        
        ```Java
        // 忽略任务的拒绝策略
        public class DiscardPolicy implements RejectedExecutionHandler {
            public void rejectedExecution(Runnable r, ThreadPool executor) {
                // do nothing
                RunnableWrapper wrapper = (RunnableWrapper) r;
                System.out.println("Task rejected: " + wrapper.getTaskId());
            }
        }
        ```
        
    
    1. `AbortPolicy`
        
        ```Java
        // 直接抛出异常的拒绝策略
        public class AbortPolicy implements RejectedExecutionHandler {
            public void rejectedExecution(Runnable r, ThreadPool executor) {
                throw new RuntimeException("The thread pool is full and the task queue is full.");
            }
        }
        ```
        
    
    1. `SimpleThreadPoolTest`
        
        ```Java
        // 定义一个测试用例类
        public class SimpleThreadPoolTest {
            public static void main(String[] args) throws InterruptedException {
        
                SimpleThreadPool threadPool = new SimpleThreadPool(1, 4, 2, 3, 2000, new AbortPolicy());
        
                for (int i = 0; i < 10; i++) {
                    threadPool.execute(new RunnableWrapper(i));
                }
        
                Thread.sleep(10_000);
        
                threadPool.shutdown();
            }
        }
        ```