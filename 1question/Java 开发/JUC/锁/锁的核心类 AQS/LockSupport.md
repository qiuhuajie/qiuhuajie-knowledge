- [[#1. LockSupport 介绍]]
- [[#2. LockSupport API]]
    - [[#2.1 park 函数]]
    - [[#2.2 unpark 函数]]
- [[#3. LockSupport 的使用]]
- [[#4. 比较]]
    - [[#4.1 Thread.sleep() 和 LockSupport.park() 的区别]]
    - [[#4.2 Object.wait() 和 LockSupport.park() 的区别]]
# 1. LockSupport 介绍
1. **LockSupport 是**==**用来创建锁和其他同步类**==**的**==**基本线程阻塞原语**==
    
    1. LockSupport 类使用了一种名为 **Permit（许可）的概念**来做到阻塞和唤醒线程的功能
    
    1. **一个线程最多只会有一个许可**，即许可只有两个值 `1` 和 `0`，默认是 `0`
    
1. **在**==**使用 LockSupport 实现线程的等待和唤醒时，没有限制条件，更加灵活**==（详见 下 LockSupport）
# 2. LockSupport API
## 2.1 park 函数
1. `**park()**`：
    
    1. 调用后阻塞线程，除非许可可用，或 该线程被中断（比如其他线程调用 `interrupt()`）
    
    1. 由于许可默认为 0，**当调用 `park()` 后当前线程就会阻塞，直到别的线程将当前线程的许可设置为 1 时，`park()` 方法会被唤醒，然后会将许可再次设置为 0 并返回**
    
1. **`park(boolean isAbsolute, long time)`**
    
    1. 调用后阻塞线程，并且该线程在下列情况发生之前都会被阻塞：
        
        1. 调用 `unpark()` 函数，释放该线程的许可
        
        1. 该线程被中断
        
        1. 设置的时间到了
        
    
    1. 参数说明：
        
        1. isAbsolute 为 true 时，time 为绝对时间时，否则 time 为相对时间
        
        1. 当 time 为 0 时，表示无限等待，直到 unpark() 发生
        
    
1. **`park(Object blocker)`**
1. **`parkNanos(Object blocker, long nanos)`** ：在许可可用前阻塞当前线程，并最多等待指定的等待时间
1. **`parkUntil(Object blocker, long deadline)`** ：在指定的时限前禁用当前线程，除非许可可用
## 2.2 unpark 函数
1. **`unpark(Thread thread)`**：
    
    1. 如果给定线程尚不可用，则为其提供许可
    
    1. **调用 `unpark(thread)` 方法后，就会将指定的 thread 线程的许可设置成 1，会自动唤醒 thread 线程，即之前阻塞中的 `LockSupport.park()` 方法会立即返回**
    
    1. 注意：多次调用 `unpark()` 方法，**许可数量不会累加**，一个线程的许可数始终为 1
    
# 3. LockSupport 的使用
1. **线程之间的协作：**
    
    - Thread：sleep()
    
    - **Object：**[[线程的通信]]
    
    - **Condition：**[[线程的通信]]
    
1. LockSupport：
    
    1. **`wait()` + `notify()` 、**`**await()**` **+ `signal()` 的方法在实现等待和唤醒时，会有限制条件**
        
        1. 线程先要获得并持有锁，必须在锁块（synchronized 或 lock）中
        
        1. 必须要先等待后唤醒，线程才能够被唤醒
        
        1. 且这些方法在声明时，抛出了 `InterruptedException` 中断异常，所以在使用时需要捕获异常
        
    
    1. ==⭐====**但 LockSupport 实现等待和唤醒时，没有限制条件，更加灵活**==
        
        1. **不需要在锁块中使用**
        
        1. **即使 `unpark(t1)` 在 `park()` 之前执行，线程的等待和唤醒操作依然可以顺利执行**
        
        1. **且不需要捕获异常**
        
        1. **线程被唤醒后，一定会继续执行（被唤醒后不需要再去竞争锁）**
        
    
1. 运行示例：
    
    ```Java
    public class LockSupportDemo3 {
        public static void main(String[] args) {
    
            Thread t1 = new Thread(() -> {
                try { TimeUnit.SECONDS.sleep(3); } catch (InterruptedException e) { e.printStackTrace(); }
                System.out.println(Thread.currentThread().getName() + "等待通知 " + System.currentTimeMillis());
                LockSupport.park();
                System.out.println(Thread.currentThread().getName() + "t1 获得许可被唤醒了");
            }, "t1");
            t1.start();
    
    //        try { TimeUnit.SECONDS.sleep(3); } catch (InterruptedException e) { e.printStackTrace(); }
    
            new Thread(() -> {
                LockSupport.unpark(t1);
                System.out.println(Thread.currentThread().getName() + "给 t1 发出一个许可 " + System.currentTimeMillis());
            }, "t2").start();
    
        }
    }
    ```
    
    - 运行结果：
        
        ```Java
        t2给 t1 发出一个许可 1680439996859
        t1等待通知 1680439999860
        t1t1 获得许可被唤醒了
        ```
        
    
# 4. 比较
## 4.1 Thread.sleep() 和 LockSupport.park() 的区别
- **相同点：都是阻塞当前线程的执行，且**==**都不会释放当前线程占有的锁资源**==
- **唤醒方式不同**
    
    - Thread.sleep() 没法从外部唤醒，只能自己醒过来
    
    - LockSupport.park() 方法可以被另一个线程调用 LockSupport.unpark() 方法唤醒
    
- **使用时是否需要捕获异常**
    
    - Thread.sleep() 方法声明上抛出了 InterruptedException 中断异常，所以调用者需要捕获这个异常或者再抛出
    
    - LockSupport.park() 方法不需要捕获中断异常
    
- **是否是 native 方法**
    
    - Thread.sleep() 本身就是一个 native 方法
    
    - LockSupport.park() 底层是调用的 Unsafe 的 native 方法
    
## 4.2 Object.wait() 和 LockSupport.park() 的区别
- **是否需要在锁块中使用**
    
    - Object.wait() 方法需要在 synchronized 块中执行
    
    - LockSupport.park() 可以在任意地方执行
    
- **使用时是否需要捕获异常**
    
    - Object.wait() 方法声明抛出了中断异常，调用者需要捕获或者再抛出
    
    - LockSupport.park() 不需要捕获中断异常
    
- **唤醒方式后是否继续执行** 🟡
    
    - Object.wait() 不带超时的，需要另一个线程执行 notify() 来唤醒，**==但不一定继续执行后续内容==**
        
        - 这是因为在多线程编程中，==线程调度器==是不可预测的，它负责决定哪个线程可以运行
        
        - 而且，当一个线程被唤醒后，需要==竞争锁==，因为其他线程可能会先获得锁并运行一段时间
        
    
    - LockSupport.park() 不带超时的，需要另一个线程执行 unpark() 来唤醒，一定会继续执行后续内容