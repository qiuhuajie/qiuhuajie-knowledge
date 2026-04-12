- [[#1. 介绍]]
- [[#2. Threadlocal 原理⭐]]
- [[#3. ThreadLocal 内存泄露问题 ⭐]]
- [[#4. Threadlocal 在项目中的使用]]
- [[#5. InheritableThreadLocal🙋‍♂️]]
    - [[#5.1 Threadlocal 的缺点]]
    - [[#5.2 InheritableThreadLocal]]
    - [[#5.3 InheritableThreadLocal 缺陷]]
# 1. 介绍
1. 通常情况下，创建的变量是可以被任何一个线程访问并修改的
1. **如何实现**==**每一个线程都有自己的专属本地变量副本**==**，避免两个线程之间竞争数据，从而**==**避免了线程安全**==**问题**
    
    1. ThreadLocal 类主要解决的就是让每个线程绑定自己的值
    
    1. 可以将 ThreadLocal 类形象的比喻成存放数据的盒子，盒子中可以存储每个线程的私有数据
        
        1. 创建一个 Threadlocal 变量，那么访问这个变量的==每个线程都会有这个变量的本地副本==
        
        1. 各个线程可以使用 **`get()`** 和 **`set()`** 方法来获取默认值或将其值更改为当前线程自己的值
        
        ![[IMG-20260404031737603.png|Untitled 306.png]]
        
    
    > [!important] **ThreadLocal 是否会存在另一个线程修改当前线程数据的问题**
    
1. 🙋‍♂️ **两台机器如何实现 ThreadLocal 信息共享？**
    
    1. 可以使用分布式缓存来存储 ThreadLocal 变量的值
        
        1. 例如，可以使用 **Redis 等分布式缓存**来存储 ThreadLocal 变量的值，并使用一个**全局唯一的标识符**来标识每个 ThreadLocal 变量
        
        1. 然后，在不同的机器上的线程可以通过该标识符从分布式缓存中获取相应的值，并在需要的时候将其设置为当前线程的 ThreadLocal 变量的值
        
    
    1. 另外一种可能的方法是使用**远程过程调用（RPC）**来实现 ThreadLocal 信息的共享
    
    1. 无论使用哪种方法，都需要考虑到线程安全和性能问题，以及不同机器之间的数据一致性和可靠性
    
1. **ThreadLocal 与 Synchronized 的比较**
    
    1. 同：
        
        - ThreadLocal 和 Synchronized 都用于解决多线程并发访问。可是 ThreadLocal 与 synchronized 有本质的差别
        
    
    1. 异：
        
        - synchronized 是利用锁的机制，使变量或代码块在某一时该仅仅能被一个线程访问，控制线程堆变量的访问顺序
            
            ```Java
            class MovieTicket {
                int number = 50;
                public synchronized void saleTicket() {
                    if (number > 0) {
                        number--;
                    } else {
                        System.out.println("卖完了");
                    }
                }
            }
            ```
            
        
        - 而 ThreadLocal 为每个线程都提供了变量的副本，其它 Thread 不可访问，也就不存在多线程间共享的问题了
            
            ```Java
            class House {
            		// ⭐每个 Thread 有自己的 ThreadLocal 实例副本，且该副本只能由当前线程自己使用
                ThreadLocal<Integer> threadLocal = ThreadLocal.withInitial(() -> 0);
                public void saleHouse() {
                    Integer value = threadLocal.get();
                    value++;
                    threadLocal.set(value);
                }
            }
            ```
            
        
    
# 2. Threadlocal 原理⭐

> [!important] **ThreadLocal 的具体实现**
1. 在 ThreadLocal 中有一个静态内部类 `**ThreadLocalMap**`
    
    ![[IMG-20260404031737642.png|Untitled 1 232.png]]
    
1. ==**每个 Thread 中都具备一个 ThreadLocalMap ，而 ThreadLocalMap 可以存储以 Threadlocal 为 key ，Object 对象为 value 的 Entry 键值对**==
    
    ![[IMG-20260404031737670.png|Untitled 2 196.png]]
    
    1. ThreadLocal 对象的 `set()` 方法在设置值时，会结果把 ThreadLocal 对象自己当做 Key，放进了 ThreadLoalMap中
        
        ![[IMG-20260405035421937.png|Untitled 3 150.png]]
        
    
    1. ThreadLocal 对象的 `get()` 方法在获取值时，会去当前线程的 Map 里面找，Key 为当前 ThreadLocal 对应的 Value
        
        ![[IMG-20260405035428776.png|Untitled 4 123.png]]
        
    
1. **==Entry 键值==**==对就是==**==每个线程==**==根据共享内存中的 ThreadLocal 变量所维护的一个==**==属于线程自己的==** **==ThreadLocal 变量的副本==**
# 3. ThreadLocal 内存泄露问题 ⭐

> [!important] **内存泄漏：不再会被使用的对象或者变量占用的内存不能被回收**
1. ==**首先，要保证 ThreadLocal 对象本身需要被正确回收**==
    
    1. 强引用指向的对象在任何时候，都不会被回收；弱引用只要发生了垃圾回收，弱引用指向的对象就会被回收[[3.2 Java 中的 4 种引用]]
    
    1. ==源码中，ThreadlocalMap 中 key 是 WeakReference 类型==
        
        ![[IMG-20260405035441840.png|Untitled 5 102.png]]
        
    
    1. 图示：
        
        ![[IMG-20260405035503403.png|Untitled 6 85.png]]
        
        - 图中，ThreadLocal 引用 强引用了 ThreadLocal 对象
        
        - 同时 ThreadLocal 对象同时也被 ThreadlocalMap 的 key 引用，这是个弱引用
        
        - ==如果 key 指向 ThreadLocal 对象的引用也是一个强引用的话==
            
            1. 程序中大多情况使用线程都是要是用的线程池，所以线程是可能出现一直复用的情况的
            
            1. 也即可能一直存在一条强引用链：Thread 引用 ➡️ Thread 对象 ➡️ ThreadLocalMap ➡️ Entry 的 Key ➡️ ThreadLocal 对象
            
            1. 这时，即使 ThreadLocal 引用 ➡️ ThreadLocal 对象的强引用被删除，ThreadLocal 对象也永远不会被删除
            
        
        - 所以，==key 指向 ThreadLocal 对象的引用要设置成一个软引用，当 ThreadLocal 引用 ➡️ ThreadLocal 对象的强引用被删除，ThreadLocal 对象就会被删除==
        
    
1. ==**其次，要保证在 ThreadLocal 对象被删除后，ThreadLocalMap 中对应的 Entry 也被正确清理**==
    
    1. 存在的问题：ThreadLocal 对象被删除后，此时 Entry 的 Key 就会变为一个 null，如果不做任何处理，这些 null ↔️ Value 的键值对就永远无法被清理，造成业务数据污染 + 内存泄漏
    
    1. 所以，==必须在代码 try-finally 块中，主动调用== ==`remove()`== ==清理 ThreadLocal 对象==
        
        ![[IMG-20260405035503428.png|Untitled 7 72.png]]
        
    
# 4. Threadlocal 在项目中的使用
1. 将业务的一些==**上下文信息**==，保存在 ThreadLocal 对象中，实现上下文信息和线程的关联关系
    
    1. VisaApiContext
        
        ```Java
        public class VisaApiContext {
        
            private static final ThreadLocal<VisaApplyHandleContext> TL = new ThreadLocal<>();
        
            public static void init() {
                VisaApplyHandleContext cd = new VisaApplyHandleContext();
                TL.set(cd);
            }
        
            public static boolean putContext(VisaApplyHandleContext info) {
                if (info != null) {
                    TL.set(info);
                    return true;
                }
                return false;
            }
        
            public static void remove() {
                TL.remove();
            }
        
            public static VisaApplyHandleContext get() {
                return TL.get();
            }
        }
        ```
        
    
    1. **登录校验：**[[校验登录状态]]
        
        1. 使用拦截器将请求拦截，判断当前用户是否已登录
        
        1. 如果已经登录，将用户信息放在 Threadlocal 中，这样 Controller 就可以拿到当前用户的信息了
        
        1. 不过引入 Redis 可以代替这种方式
        
    
1. 如果有**很多变量**都要塞到 ThreadlocalMap 中，那岂不是要申明很多个Threadlocal 对象？
    
    - 最佳实践：**再封装一下，把 ThreadLocalMap 的value 弄成 Map 就好了，这样只要一个Threadlocal 对象就好了**
    
# 5. InheritableThreadLocal🙋‍♂️
## 5.1 Threadlocal 的缺点
1. **Threadlocal 的缺点：**==**不能在父子线程中线程之间传递**==
    
    1. 演示：
        
        ![[IMG-20260405035510674.png|Untitled 8 59.png]]
        
    
    1. 结果：**子线程无法访问父线程中设置的本地变量**
        
        ![[IMG-20260405035518770.png|Untitled 9 52.png]]
        
    
## 5.2 InheritableThreadLocal
1. 为了解决上述问题，JDK引入了`InheritableThreadLocal` ：子线程可以访问父线程中的线程本地变量，更严谨的说法是子线程可以访问在创建子线程时父线程当时的本地线程变量
1. 实现原理：
    
    1. ==**在创建子线程的时候，将父线程当前存在的本地线程变量拷贝到子线程的本地线程变量中**==
    
    1. `InheritableThreadLocal#getMap`
        
        ![[IMG-20260405035526182.png|Untitled 10 45.png]]
        
    
    1. `Thread#init` ⭐
        
        ![[IMG-20260405035531799.png|Untitled 11 40.png]]
        
        - 父线程中通过调用`new Thread()`方法来创建子线程，`Thread#init`方法在 Thread 的构造方法中被调用
        
        - **如果父线程的 `inheritableThreadLocals` 不为空并且 `inheritThreadLocals == true`，则将父线程中的本地变量复制到子线程中**
        
    
    1. 子线程默认拷贝父线程的方式是**浅拷贝**，如果需要使用深拷贝，需要使用自定义 ThreadLocal，继承 InheritableThreadLocal 并重写 `childValue` 方法
    
## 5.3 InheritableThreadLocal 缺陷
1. ==**在配合线程池使用时，会出现本地变量混乱的现象**==
    
    - 代码演示：
        
        ```Java
        public class ThreadLocalTest {
            //模拟tomcat线程池
            private static ExecutorService tomcatExecutors = Executors.newFixedThreadPool(10);
            //业务线程池 默认Control中异步任务执行线程池
            private static ExecutorService businessExecutors =Executors.newFixedThreadPool(5);
            //线程上下文环境，模拟在Control这一层，设置环境变量，然后在这里提交一个异步任务，模拟在子线程中，是否可以访问到刚设置的环境变量值。
            private static InheritableThreadLocal<Integer> requestIdThreadLocal = new InheritableThreadLocal<>();
        
            public static void main(String[] args) {
                for (int i = 0; i <10 ; i++) {
                    // 模式10个请求，每个请求执行ControlThread的逻辑，其具体实现就是，先输出父线程的名称，
                    // 然后设置本地环境变量，并将父线程名称传入到子线程中，在子线程中尝试获取在父线程中的设置的环境变量
                    tomcatExecutors.submit(new ControlThread(i));
                }
            }
        
            /**
             * 模拟Control任务
             */
            static class ControlThread implements Runnable {
                private int i;
        
                public ControlThread(int i) {
                    this.i = i;
                }
        
                @Override
                public void run() {
                    System.out.println(Thread.currentThread().getName() + ":" + i);
                    requestIdThreadLocal.set(i);
                    businessExecutors.submit(new BusinessTask(Thread.currentThread().getName()));
                }
            }
        
            /**
             * 业务任务，主要模拟Control控制层，提交任务到线程池执行
             */
            static class BusinessTask implements Runnable {
                private String parentThreadName;
        
                public BusinessTask(String parentThreadName) {
                    this.parentThreadName = parentThreadName;
                }
        
                @Override
                public void run() {
                    System.out.println("parentThreadName:"+parentThreadName+":"+requestIdThreadLocal.get());
                }
            }
        }
        ```
        
    
1. 结果：线程7 的变量值为 6，但其子线程却以为自己的父线程的变量值为 7
    
    ![[IMG-20260405035534474.png|Untitled 12 37.png]]
    
1. 原因：
    
    1. 线程池能够复用线程，减少线程的频繁创建与销毁
    
    1. 如果使用 `InheritableThreadLocal`，那么线程池中的线程拷贝的数据来自于第一个提交任务的外部线程
    
    1. 由于线程池的**复用**机制，“子线程”只会复制一次，即后面的外部线程向线程池中提交任务时，**子线程访问的本地变量始终都来源于第一个外部线程**，造成线程本地变量混乱
    
    1. 在全链路跟踪与压测出现这种情况是致命的
    
1. 解决：
    
    1. **`TransmittableThreadLocal`** 是阿里巴巴开源的专门解决 InheritableThreadLocal 的局限性，实现线程本地变量在线程池的执行过程中，能正常的访问父线程设置的线程变量
    
    1. 官网：
        
        https://github.com/alibaba/transmittable-thread-local
        
    
    1. 依赖：
        
        ```XML
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>transmittable-thread-local</artifactId>
            <version>2.10.2</version>
        </dependency>
        ```
        
    
    1. `TransmittableThreadLocal` 实现原理
        
        1. 在父线程向线程池提交任务时复制父线程的上下环境
        
        1. 那在子线程中就能够如愿访问到父线程中的本地变量，实现本地环境变量在线程池调用中的透传，从而为实现链路跟踪打下坚实的基础