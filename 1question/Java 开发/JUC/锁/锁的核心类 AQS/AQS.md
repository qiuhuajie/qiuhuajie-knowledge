> [!important] **AQS 框架借助于两个类：Unsafe（提供 CAS 操作）和 LockSupport（提供 park/unpark 操作）**
- [[#1. AQS 介绍]]
- [[#2. AQS 数据结构]]
- [[#3. AQS 源码分析]]
    - [[#3.1 state 标志位]]
    - [[#3.2 虚拟 FIFO 双向队列]]
    - [[#3.3 获取锁方法：acquire() ]]
    - [[#3.4 释放锁方法：release() ]]
- [[#4. 使用 AQS 自定义一个独占锁]]
# 1. AQS 介绍
1. AQS 的全称为 AbstractQueuedSynchronizer ，**抽象队列同步器**
1. 这个类在 java.util.concurrent.locks 包下面，是**整个 JUC 体系的基石**
1. **AQS 是一个**==**用来构建锁和同步器的框架**==
    
    1. 使用 AQS 能简单且高效地构造出应用广泛的大量的同步器，比如 ReentrantLock，Semaphore，ReentrantReadWriteLock，SynchronousQueue，FutureTask 等等皆是基于 AQS 的
    
    1. 也能利用 AQS 非常轻松容易地构造出符合我们自己需求的同步器
    
1. AQS 核心思想是
    
    1. 如果被请求的共享资源空闲，则将当前请求资源的线程设置为有效的工作线程，并且将共享资源设置为锁定状态
    
    1. 如果被请求的共享资源被占用，那么就需要一套线程阻塞等待以及被唤醒时，锁分配的机制
    
    1. 这个机制 AQS 是用一个 CLH 双向队列锁实现的，即将暂时获取不到锁的线程加入到队列中
    
1. **AQS 底层使用了模板模式**[[模板模式 ⭐]]
1. **AQS定义两种资源共享方式**
    
    - Exclusive（独占）：只有一个线程能执行，如 ReentrantLock。又可分为公平锁和非公平锁：
        
        - 公平锁：按照线程在队列中的排队顺序，先到者先拿到锁
        
        - 非公平锁：当线程要获取锁时，无视队列顺序直接去抢锁，谁抢到就是谁的
        
    
    - Share（共享）：多个线程可同时执行，如Semaphore、CountDownLatCh、 CyclicBarrier、ReadWriteLock 我们都会在后面讲到
    
1. 🙋‍♂️ **AQS 和 synchronized 的主要区别在于（都是Java中的同步机制）：**
    
    1. **实现方式：**
        
        1. AQS是一个抽象类，它提供了一个框架来实现同步器，开发人员需要继承AQS并实现其抽象方法来实现自己的同步器
        
        1. 而synchronized是Java语言提供的一种关键字，用于控制多个线程对共享资源的访问
        
    
    1. **粒度：**
        
        1. AQS可以实现更细粒度的同步控制，例如独占锁和共享锁
        
        1. 而synchronized只能实现粗粒度的同步控制，它只能将一个方法或代码块作为同步块
        
    
    1. **性能：**
        
        1. 在高并发情况下，AQS的性能通常比synchronized更好。因为AQS使用基于CAS（Compare-And-Swap）操作的无锁算法来实现同步
        
        1. 而synchronized使用的是重量级锁，它需要进行上下文切换和内核态与用户态之间的切换
        
    
# 2. AQS 数据结构

**状态标志位** `state` **➕ 一个虚拟的 FIFO 双向队列**

![[IMG-20260405035413905.png|Untitled 475.png]]

![[IMG-20260404031748346.png|Untitled 1 346.png]]

# 3. AQS 源码分析
## 3.1 State 标志位
1. **使用一个 `volatile` `int` 成员变量 `state` 来表示共享资源同步状态**
    
    ```Java
    private volatile int state;  //共享变量，使用volatile修饰保证线程可见性
    ```
    
1. **AQS 使用 CAS 对该同步状态进行原子操作实现对其值的修改**：通过 procted 类型的 `getState()`，`setState()`，`compareAndSetState()` 进行操作状态信息
    
    ```Java
    //返回同步状态的当前值
    protected final int getState() {  
            return state;
    }
    
    // 设置同步状态的值
    protected final void setState(int newState) { 
            state = newState;
    }
    
    //如果当前同步状态的值等于expect(期望值)，原子地(CAS操作)将同步状态值设置为给定值update
    protected final boolean compareAndSetState(int expect, int update) {
    				// 调用 Usafe 类提供的 CAS 方法
            return unsafe.compareAndSwapInt(this, stateOffset, expect, update);
    }
    ```
    
## 3.2 虚拟 FIFO 双向队列
1. AQS 类底层的数据结构是使用 CLH（Craig,Landin,and Hagersten）队列，是一个虚拟的 FIFO 双向队列（虚拟的双向队列即不存在队列实例，仅存在结点之间的关联关系）
1. AQS 将**每条请求共享资源的线程**封装成一个 CLH 锁队列的一个结点 **`Node`**，来完成获取资源线程的排队工作，进行锁的分配
1. **head 指向的第一个节点是一个**==**哨兵节点**==**，用来占位，不关联线程**
    
    ```Java
    static final class Node {
        // 模式，分为共享与独占
        // 共享模式
        static final Node SHARED = new Node();
        // 独占模式
        static final Node EXCLUSIVE = null; 
           
        // 当前结点在等待队列中的状态的常量值
        // Node 初始化后该值默认为 0，表示当前节点在sync队列中，等待着获取锁
        static final int CANCELLED =  1;  // CANCELLED，值为1，表示当前的线程被取消
        static final int SIGNAL    = -1;  // SIGNAL，值为-1，表示当前线程节点的 next 线程节点已经准备好了，就等资源释放了
        static final int CONDITION = -2;  // CONDITION，值为-2，表示当前节点在等待condition，也就是在condition队列中
        static final int PROPAGATE = -3;  // PROPAGATE，值为-3，表示当前场景下后续的acquireShared能够得以执行      
    
        // 当前结点在等待队列中的状态
        volatile int waitStatus;
            
        // 前驱结点
        volatile Node prev;    
        // 后继结点
        volatile Node next;        
        // 结点所对应的线程
        volatile Thread thread;        
        // 下一个等待者
        Node nextWaiter;
        
        // 结点是否在共享模式下等待
        final boolean isShared() {
            return nextWaiter == SHARED;
        }
        
        // 获取前驱结点，若前驱结点为空，抛出异常
        final Node predecessor() throws NullPointerException {
            // 保存前驱结点
            Node p = prev; 
            if (p == null) // 前驱结点为空，抛出异常
                throw new NullPointerException();
            else // 前驱结点不为空，返回
                return p;
        }
        
        // 无参构造方法
        Node() {    // Used to establish initial head or SHARED marker
        }
        
        // 构造方法
            Node(Thread thread, Node mode) {    // Used by addWaiter
            this.nextWaiter = mode;
            this.thread = thread;
        }
        
        // 构造方法
        Node(Thread thread, int waitStatus) { // Used by Condition
            this.waitStatus = waitStatus;
            this.thread = thread;
        }
    }
    ```
    
## 3.3 获取锁**方法**：**acquire()**
1. 该方法以独占模式获取(资源)，忽略中断，即线程在aquire过程中，中断此线程是无效的
    
    ```Java
    public final void acquire(int arg) {
        if (!tryAcquire(arg) && acquireQueued(addWaiter(Node.EXCLUSIVE), arg))
            selfInterrupt();
    }
    ```
    
1. 如果执行 `tryAcquire()` 尝试加锁不成功 返回 false，则会执行 `acquireQueued(addWaiter(Node.EXCLUSIVE), arg)` 将当前线程放入等待队列
1. `tryAcquire()` **方法在 AQS 类中是一个空实现，需要继承了 AQS 的同步器子类重写这个方法（详见 下面的 `MySync` ）**
![[IMG-20260405035420315.png|Untitled 2 283.png]]
## 3.4 释放锁**方法**：**release()**
1. 以独占模式释放对象，其源码如下
    
    ```Java
    public final boolean release(int arg) {
        if (tryRelease(arg)) { // 释放成功
            // 保存头节点
            Node h = head; 
            if (h != null && h.waitStatus != 0) // 头节点不为空并且头节点状态不为0
                unparkSuccessor(h); //释放头节点的后继结点（唤醒当前阻塞的第一个线程）
            return true;
        }
        return false;
    }
    ```
    
1. 其中，`tryRelease()` 的默认实现是抛出异常，需要具体的子类实现
1. 如果 `tryRelease()` 成功，那么如果头节点不为空并且头节点的状态不为 0，则**使用 `unparkSuccessor()` 释放头节点的后继结点**
1. `tryRelease()` **方法在 AQS 类中同样是一个空实现，需要继承了 AQS 的同步器子类重写这个方法（详见 下面的 `MySync` ）**
![[IMG-20260405035422025.png|Untitled 3 213.png]]
# 4. 使用 AQS 自定义一个独占锁
1. 实现一个锁需要很多方法，如果自己实现太难了
1. 但是，如果**使用一个继承自 `AbstractQueuedSynchronizer` 的同步器类 `MySync`，同步器里面已经把大部分方法都实现好了**，这样我们实现一个自定义锁就变得很简单了
    
    ```Java
    class MyLock implements Lock {
    
        // 实现一个独占锁（不可重入锁）
        class MySync extends AbstractQueuedSynchronizer {
            @Override
            protected boolean tryAcquire(int arg) {
                // 使用 CAS 方式修改 state 为 1
                if (compareAndSetState(0, 1)) {
                    // 此时已经加上锁，还需要将持有者线程设置为当前线程
                    setExclusiveOwnerThread(Thread.currentThread());
                    return true;
                }
                return false;
            }
    
            @Override
            protected boolean tryRelease(int arg) {
                setExclusiveOwnerThread(null);
                // 将 state 修改回 0，由于 state 是 volatile 修饰的，在其后面会加写屏障
                setState(0);
                return true;
            }
    
            @Override
            protected boolean isHeldExclusively() {
                return getState() == 1;
            }
    
            public Condition newCondition() {
                return new ConditionObject();
            }
        }
    
    	  // new 一个 AQS 对象
        private MySync sync = new MySync();
    
    
        // 加锁（不成功会进入等待队列），这里调用 AQS 中的获取锁：acquire() 方法，里面执行的 tryAcquire(arg) 方法是我们自定义的同步器 MySync 中重写的 tryAcquire(arg)方法
        @Override
        public void lock() {
            sync.acquire(1);
        }
    
        // 加锁，可打断
        @Override
        public void lockInterruptibly() throws InterruptedException {
            sync.acquireInterruptibly(1);
        }
    
        // 尝试加锁（只会尝试一次）
        @Override
        public boolean tryLock() {
            return sync.tryAcquire(1);
        }
    
        // 尝试加锁（带超时时间）
        @Override
        public boolean tryLock(long time, TimeUnit unit) throws InterruptedException {
            return sync.tryAcquireNanos(1, unit.toNanos(time));
        }
    
        // 解锁
        @Override
        public void unlock() {
            sync.release(1);
        }
    
        // 创建条件变量
        @Override
        public Condition newCondition() {
            return sync.newCondition();
        }
    }
    ```
    
1. 测试自定义的锁
    
    ```Java
    public class MyLockTest {
        public static void main(String[] args) {
            MyLock lock = new MyLock();
    
            new Thread(() -> {
                lock.lock();
    
                try {
                    System.out.println("t1 locked");
                    Thread.sleep(1);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                } finally {
                    lock.unlock();
                    System.out.println("t1 unlocked");
                }
            }, "t1").start();
    
            new Thread(() -> {
                lock.lock();
    
                try {
                    System.out.println("t2 locked");
                } finally {
                    lock.unlock();
                    System.out.println("t2 unlocked");
                }
            }, "t2").start();
        }
    }
    ```
    

    运行结果

    
    ```Java
    t1 locked
    t1 unlocked
    t2 locked
    t2 unlocked
    ```