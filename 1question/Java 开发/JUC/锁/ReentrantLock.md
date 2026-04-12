- [[#1. 介绍]]
- [[#2. ReentrantLock 特性]]
    - [[#2.1 可重入]]
    - [[#2.2 可打断]]
    - [[#2.3 锁超时]]
    - [[#2.4 公平锁]]
    - [[#2.5 条件变量]]
- [[#3. 原理]]
    - [[#3.1 非公平锁实现原理]]
        - [[#加锁流程]]
        - [[#解锁流程]]
    - [[#3.2 公平锁实现原理]]
    - [[#3.3 可重入实现原理]]
        - [[#获取锁]]
        - [[#释放锁]]
    - [[#3.4 可打断原理]]
        - [[#不可打断模式]]
        - [[#可打断模式]]
    - [[#3.5 条件变量实现原理]]
        - [[#await 流程]]
        - [[#signal 流程]]
- [[#4. 源码注释]]
    - [[#4.1 Sync 类]]
    - [[#4.2 NonfairSync 类]]
    - [[#4.3 FairSyn 类]]
# 1. 介绍
1. 类结构

    ![[IMG-20260404031743307.png|Untitled 301.png]]

    1. ReentrantLock 实现了 Lock 接口，Lock 接口中定义了 lock 与 unlock 等相关操作
    2. ReentrantLock 类有三个内部类： Sync、NonfairSync、FairSync
    3. Sync 是一个抽象的 AQS 子类，他有两个 子类 NonfairSync、FairSync 分别对应公平锁和非公平锁

        ```Java
        abstract static class Sync extends AbstractQueuedSynchronizer {...}
        ```
2. ReentrantLock 和 Synchronized 的对比❓[[线程的通信]]
# 2. ReentrantLock 特性
## 2.1 可重入
```Java
public class RLDemo2 {
    static ReentrantLock lock = new ReentrantLock();
    public static void main(String[] args) throws InterruptedException {
        m1();
    }
    public static void m1(){
        lock.lock();
        try {
            System.out.println(Thread.currentThread().getName() + " m1() 获取锁成功");
            // 同一线程下的 m1 调用 m2
            m2();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            lock.unlock();
        }
    }
    public static void m2(){
        lock.lock();
        try {
            System.out.println(Thread.currentThread().getName() + " m2() 获取锁成功");
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            lock.unlock();
        }
    }
}
```

运行结果：**m2 也可以顺利获得锁**

```Java
main m1() 获取锁成功
main m2() 获取锁成功
```
## 2.2 可打断
1. **不可打断模式获取锁：`lock.lock()`**

    ```Java
    public class RLDemo1 {
        public static void main(String[] args) throws InterruptedException {
            ReentrantLock lock = new ReentrantLock();
            Thread t = new Thread(() -> {
                try {
                    System.out.println("t 尝试获取锁");
                    // 现在主线程拿着锁，t 拿不到，此时 t 进入阻塞队列
                    lock.lock();
                } finally {
                    lock.unlock();
                }
            });
            // 主线程先拿到锁
            lock.lock();
            // 再启动线程 t
            t.start();
            Thread.sleep(1000);
            System.out.println("主线程尝试打断 t");
            t.interrupt();
        }
    }
    ```

    运行结果：**线程 t 一直被阻塞**

    ![[IMG-20260404031743419.png|Untitled 1 227.png]]

2. **可打断模式获取锁：`lock.lockInterruptibly()`**

    ```Java
    public class RLDemo1 {
        public static void main(String[] args) throws InterruptedException {
            ReentrantLock lock = new ReentrantLock();
            Thread t = new Thread(() -> {
                try {
                    System.out.println("t 尝试获取锁");
                    // 现在主线程拿着锁，t 拿不到，此时 t 进入阻塞队列
                    lock.lockInterruptibly();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                } finally {
                    lock.unlock();
                }
            });
            // 主线程先拿到锁
            lock.lock();
            // 再启动线程 t
            t.start();
            Thread.sleep(1000);
            System.out.println("主线程尝试打断 t");
            t.interrupt();
        }
    }
    ```

    运行结果：**线程 t 直接被打断，抛出** `**InterruptedException**` **异常**

![[IMG-20260404031743523.png|Untitled 2 192.png]]

## 2.3 锁超时
```Java
public class RLDemo3 {
    public static void main(String[] args) throws InterruptedException {
        ReentrantLock lock = new ReentrantLock();
        Thread t = new Thread(() -> {
            System.out.println("t 尝试获取锁");
            try {
                // t 只会尝试获取锁 2s，如果获取不到就直接 return，避免无限制地等待下去
                if (!lock.tryLock(2, TimeUnit.SECONDS)) {
                    System.out.println("t 尝试获取锁失败");
                    return;
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            try {
                System.out.println("t 获取到锁");
            } finally {
                lock.unlock();
            }
        });
        // 主线程先拿到锁
        lock.lock();
        // 再启动线程 t
        t.start();
    }
}
```

运行结果：

```Java
t 尝试获取锁
t 尝试获取锁失败
```
## 2.4 公平锁
## 2.5 条件变量
1. `**synchronized**` **中有条件变量，就是我们讲原理时那个** `**waitSet**` **休息室，当条件不满足时进入** `**waitSet**` **等待**
2. **ReentrantLock 的条件变量比 synchronized 强大之处在于，它是⭐**==**支持多个条件变量的**==
    1. 这就好比 synchronized 是那些不满足条件的线程都在一间休息室等消息
    2. 而 ReentrantLock **支持多间休息室**，有专门等烟的休息室、专门等早餐的休息室、唤醒时也是按休息室来唤醒
3. **条件变量执行流程：**
    1. await 前需要获得锁
    2. await 执行后，会释放锁，进入 conditionObject 等待
    3. await 的线程被唤醒（或打断、或超时）取重新竞争 lock 锁
    4. 竞争 lock 锁成功后，从 await 后继续执行
4. 代码示例

    ```Java
    public class RLDemo4 {
        public static void main(String[] args) throws InterruptedException {
            ReentrantLock lock = new ReentrantLock();
            Condition c1 = lock.newCondition();
            Condition c2 = lock.newCondition();
            Thread t1 = new Thread(() -> {
                try {
                    lock.lock();
                    try {
                        // 1. t1 在 c1 条件上 await()，同时释放锁
                        c1.await();
                        // 5. 被唤醒后，使用 c2 条件唤醒 t2
                        c2.signal();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    System.out.println("t1 执行完毕");
                } finally {
                    lock.unlock();
                }
            });
            Thread t2 = new Thread(() -> {
                try {
                    // 2. t2 此时是可以拿到锁的
                    lock.lock();
                    try {
                        // 3. t2 使用 c1 条件唤醒 t1
                        c1.signal();
                        // 4. t2 在 c2 条件上 await()，同时释放锁
                        c2.await();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    System.out.println("t2 执行完毕");
                } finally {
                    lock.unlock();
                }
            });
            t1.start();
            t2.start();
        }
    }
    ```

    运行结果

    ```Java
    t1 执行完毕
    t2 执行完毕
    ```
# 3. 原理
## 3.1 非公平锁实现原理
### 加锁流程
1. 先从构造器开始看，ReentrantLock 默认为非公平锁实现：NonfairSync 继承自 AQS

    ![[IMG-20260404031743586.png|Untitled 3 147.png]]

2. 没有竞争时，线程 0，获取到锁，通过 CAS 将 state 修改为 1，将持有者线程设置为自己

    ![[IMG-20260404031743707.png|Untitled 4 120.png]]

3. 此时，线程 1 来竞争资源，第一个竞争出现，会使用 CAS 尝试将 state 从 0 修改为 1，但此时 state = 1，修改失败，会进入 acquire(1) 逻辑

    ![[IMG-20260404031743822.png|Untitled 5 99.png]]

4. acquire() 方法中执行 NonfairSync 重写后的 tryAcquire()，调用 nonfairTryAcquire() 方法
5. 这里线程 1 由于线程 0 占着资源，拿不到锁，会直接失败，返回 false，会进入 addWaiter() 逻辑，构造一个 Node 队列
    - 黄色三角为 Node 的 waitStatus 状态，默认为 0
    - **head 指向的第一个节点是一个**==**哨兵节点**==**，用来占位，不关联线程**

    ![[IMG-20260404031743893.png|Untitled 6 84.png]]

6. 接着线程 1 进入 acquireQueued() 逻辑
    1. acquireQueued() 会在一个死循环里不断尝试获得锁，失败后进入 park 阻塞
    2. 如果当前节点的前驱节点是 head，那么再次 tryAcquire() 尝试获取锁，当然这时 state 仍为 1，失败
    3. 接着，进入 shouldParkAfterFailedAcquire 逻辑，**将前驱 Node，即 head 的 waitStatus 改为 -1**，这次返回 false

    ![[IMG-20260404031744007.png|Untitled 7 71.png]]

7. shouldParkAfterFailedAcquire 执行完毕回到 acquireQueued ，再次 tryAcquire 尝试获取锁，当然这时 state 仍为 1，失败
8. 当再次进入 shouldParkAfterFailedAcquire 时，这时因为其前驱 node 的 waitStatus 已经是 -1，这次返回 true
9. 进入 parkAndCheckInterrupt， **Thread-1 park（灰色表示）**

    ![[IMG-20260404031744091.png|Untitled 8 58.png]]

10. **再次有多个线程经历上述过程竞争失败，变成这个样子**

    ![[IMG-20260404031744174.png|Untitled 9 51.png]]

### 解锁流程
1. 此时，线程 0 释放锁，进入 tryRelease() 流程，如果成功
    - 设置持有者线程 exclusiveOwnerThread 为 null
    - 将 state 设置回 0

    ![[IMG-20260404031744292.png|Untitled 10 44.png]]

2. ⭐**如果当前等待队列不为 null，并且 head 的 waitStatus = -1，**==**表示等待队列中 head 节点的后继节点线程 1，万事俱备只等锁的释放就可以执行了**==，接着进入 unparkSuccessor 流程
    1. 找到队列中离 head 最近的一个 Node（没取消的），unpark 恢复其运行，即 线程 1 被唤醒
    2. 此时执行 线程1 进入等待队列时，执行 park 之后的那行代码，也即，acquireQueued 流程
3. 此时，线程 1 会再次尝试获取锁，当前是可以获取到的
    - **将持有者线程 exclusiveOwnerThread 设置为 线程 1，state = 1**
    - ==**将 head 指向刚刚 线程 1 所在的 Node，并将该 Node 清空 ，此时这个新的 null 节点成为哨兵**==
    - **原本的 head 因为从链表断开，而可被垃圾回收**

    ![[IMG-20260404031744365.png|Untitled 11 39.png]]

4. 到此，线程 1 获得锁，可以继续执行
5. 但**由于是**==**非公平锁**==**，也即在 线程 0 刚释放完锁后，来了一个新的线程 4，它刚好直接获取到锁了**
    - 线程 4 将持有者线程 exclusiveOwnerThread 设置为 线程 4，state = 1
    - 而线程 1 再次进入 acquireQueued 流程，获取锁失败，重新进入 park 阻塞

    ![[IMG-20260404031744458.png|Untitled 12 36.png]]

## 3.2 公平锁实现原理
1. 上面的线程 4，在公平锁下根本抢不到锁，因为当前 AQS 等待队列中，线程 4 并不是第一个节点
2. 可以在**构造函数中，传递参数确定采用公平策略或者是非公平策略，参数为 true 表示公平策略，否则，采用非公平策略**

    ![[IMG-20260404031744538.png|Untitled 13 35.png]]

3. **与非公平锁主要区别在于 `tryAcquire()` 方法的实现**

    ![[IMG-20260404031744625.png|Untitled 14 32.png]]

4. ⭐**在方法中会线使用 `hasQueuedPredecessors()`** ==**检查，如果 AQS 队列非空，且 head 没有下一个等待节点，或者第一个等待节点就是当前要获取锁的线程，那么当前线程可以去竞争锁**==

    ![[IMG-20260404031744707.png|Untitled 15 30.png]]

## 3.3 可重入实现原理
- 可重入获取锁和释放锁的逻辑实现，都写在了 ReentrantLock 的 内部 AQS 实现类 Sync 中，由于非公平锁和公平锁都继承了 Sync，所以这两种锁都是可重入锁

    ![[IMG-20260404031744776.png|Untitled 16 23.png]]

### 获取锁
1. 首先 getState() 看看当前锁有没有线程在占着，如果没有占着，直接就可以拿到锁
2. ⭐==**如果有线程占用，则会看当前占用锁的线程是不是当前请求锁的线程**==
    1. 如果不是直接返回 false
    2. **如果是，表示发生了锁的重入，则会将** `**state + 1**` **，返回 true，表示获取锁成功**

### 释放锁
1. **会判断当前线程是不是持有者线程 exclusiveOwnerThread**
    1. 如果不是，抛出异常
    2. **如果是，再判断当前重入数 state 减去 传入的要扣除的重入的差是否等于 0**
        1. 如果等于 0，表示当前线程要释放锁了，会将持有者线程设置为 null
        2. 如果不等于 0，则直接将这个差值赋值给 state，返回 false

## 3.4 可打断原理
### **不可**打断模式
1. 在线程无法获取锁时，会进入 acquireQueued() 方法中，不断尝试
    1. **如果尝试不成功会调用 `LockSupport.park()` 将当前线程阻塞等待**
    2. 在当前线程 park 阻塞的过程中，如果有其他线程将其打断，**在不可打断模式下，只是设置一个标志位：`interrupted = true`**

    ![[IMG-20260404031744843.png|Untitled 17 23.png]]

2. ⭐**不可打断模式下，**==**即使线程被其他线程打断，该线程仍会驻留在 AQS 队列中，一直要等到这个线程获得锁后，才能得知自己被打断了**==
### 可打断模式
1. 以可打断方式获取锁的方法是：**`acquireInterruptibly()`**
2. 调用 doAcquireInterruptibly()，在方法逻辑中**如果发现线程被打断了，不可打断模式下，会直接抛出一个异常** `**throw new InterruptedException()**`

    ![[IMG-20260404031744976.png|Untitled 18 22.png]]

## 3.5 条件变量实现原理
- 当一个拿到锁的线程调用 `await()` 进入阻塞，如何让其在唤醒条件满足时，被唤醒❓
- ⭐==**每个条件变量其实就对应着一个等待队列**==**，这个队列实现类是 ConditionObject**
    - ConditionObject 是 `AbstractQueuedSynchronizer` 提供的一个内部实现类
    - 队列中的节点和 Sync 队列中的节点一样，都是 Node 类节点

### Await 流程
1. 开始 线程 0 持有锁，调用 await，进入 ConditionObject 的 addConditionWaiter 流程
2. 创建新的 Node 状态为 -2（Node.CONDITION），关联 线程 0，加入等待队列尾部

    ![[IMG-20260404031745042.png|Untitled 19 21.png]]

3. 接下来进入 AQS 的 fullyRelease 流程，释放同步器上的锁，fullyRelease 中会将当前锁上的所有重入数清零

    ![[IMG-20260404031745142.png|Untitled 20 20.png]]

4. unpark AQS 队列中的下一个节点，竞争锁，假设没有其他竞争线程，那么 线程 1 竞争成功

    ![[IMG-20260404031745215.png|Untitled 21 19.png]]

5. park 阻塞 线程 0

    ![[IMG-20260404031745278.png|Untitled 22 17.png]]

### Signal 流程
1. 假设 线程 1 执行过程中会醒 线程 0

    ![[IMG-20260404031745406.png|Untitled 23 17.png]]

2. 进入 ConditionObject 的 doSignal 流程，取得条件等待队列中第一个 Node，即 线程 0 所在 Node

    ![[IMG-20260404031745472.png|Untitled 24 15.png]]

3. 执行 transferForSignal 流程，将该 Node 加入 AQS 队列尾部，将 线程 0 的 waitStatus 改为 0，Thread-3 的 waitStatus 改为 -1

    ![[IMG-20260404031745559.png|Untitled 25 14.png]]

# 4. 源码注释
## 4.1 Sync 类
```Java
abstract static class Sync extends AbstractQueuedSynchronizer {
    // 序列号
    private static final long serialVersionUID = -5179523762034025860L;
    // 获取锁
    abstract void lock();
    // 非公平方式获取
    final boolean nonfairTryAcquire(int acquires) {
        // 当前线程
        final Thread current = Thread.currentThread();
        // 获取状态
        int c = getState();
        if (c == 0) { // 表示没有线程正在竞争该锁
            if (compareAndSetState(0, acquires)) { // 比较并设置状态成功，状态0表示锁没有被占用
                // 设置当前线程独占
                setExclusiveOwnerThread(current); 
                return true; // 成功
            }
        }
        else if (current == getExclusiveOwnerThread()) { // 当前线程拥有该锁
            int nextc = c + acquires; // 增加重入次数
            if (nextc < 0) // overflow
                throw new Error("Maximum lock count exceeded");
            // 设置状态
            setState(nextc); 
            // 成功
            return true; 
        }
        // 失败
        return false;
    }
    // 试图在共享模式下获取对象状态，此方法应该查询是否允许它在共享模式下获取对象状态，如果允许，则获取它
    protected final boolean tryRelease(int releases) {
        int c = getState() - releases;
        if (Thread.currentThread() != getExclusiveOwnerThread()) // 当前线程不为独占线程
            throw new IllegalMonitorStateException(); // 抛出异常
        // 释放标识
        boolean free = false; 
        if (c == 0) {
            free = true;
            // 已经释放，清空独占
            setExclusiveOwnerThread(null); 
        }
        // 设置标识
        setState(c); 
        return free; 
    }
    // 判断资源是否被当前线程占有
    protected final boolean isHeldExclusively() {
        // While we must in general read state before owner,
        // we don't need to do so to check if current thread is owner
        return getExclusiveOwnerThread() == Thread.currentThread();
    }
    // 新生一个条件
    final ConditionObject newCondition() {
        return new ConditionObject();
    }
    // Methods relayed from outer class
    // 返回资源的占用线程
    final Thread getOwner() {        
        return getState() == 0 ? null : getExclusiveOwnerThread();
    }
    // 返回状态
    final int getHoldCount() {            
        return isHeldExclusively() ? getState() : 0;
    }
    // 资源是否被占用
    final boolean isLocked() {        
        return getState() != 0;
    }
    /**
        * Reconstitutes the instance from a stream (that is, deserializes it).
        */
    // 自定义反序列化逻辑
    private void readObject(java.io.ObjectInputStream s)
        throws java.io.IOException, ClassNotFoundException {
        s.defaultReadObject();
        setState(0); // reset to unlocked state
    }
}
```
## 4.2 NonfairSync 类
- NonfairSync 类继承了 Sync 类，表示采用非公平策略获取锁，其实现了 Sync 类中抽象的 lock 方法，源码如下
```Java
// 非公平锁
static final class NonfairSync extends Sync {
    // 版本号
    private static final long serialVersionUID = 7316153563782823691L;
    // 获得锁
    final void lock() {
        if (compareAndSetState(0, 1)) // 比较并设置状态成功，状态0表示锁没有被占用
            // 把当前线程设置独占了锁
            setExclusiveOwnerThread(Thread.currentThread());
        else // 锁已经被占用，或者set失败
            // 以独占模式获取对象，忽略中断
            acquire(1); 
    }
    protected final boolean tryAcquire(int acquires) {
        return nonfairTryAcquire(acquires);
    }
}
```
## 4.3 FairSyn 类
- FairSync 类也继承了 Sync 类，表示采用公平策略获取锁，其实现了 Sync 类中的抽象 lock 方法，源码如下
```Java
// 公平锁
static final class FairSync extends Sync {
    // 版本序列化
    private static final long serialVersionUID = -3000897897090466540L;
    final void lock() {
        // 以独占模式获取对象，忽略中断
        acquire(1);
    }
    /**
        * Fair version of tryAcquire.  Don't grant access unless
        * recursive call or no waiters or is first.
        */
    // 尝试公平获取锁
    protected final boolean tryAcquire(int acquires) {
        // 获取当前线程
        final Thread current = Thread.currentThread();
        // 获取状态
        int c = getState();
        if (c == 0) { // 状态为0
            if (!hasQueuedPredecessors() &&
                compareAndSetState(0, acquires)) { // 不存在已经等待更久的线程并且比较并且设置状态成功
                // 设置当前线程独占
                setExclusiveOwnerThread(current);
                return true;
            }
        }
        else if (current == getExclusiveOwnerThread()) { // 状态不为0，即资源已经被线程占据
            // 下一个状态
            int nextc = c + acquires;
            if (nextc < 0) // 超过了int的表示范围
                throw new Error("Maximum lock count exceeded");
            // 设置状态
            setState(nextc);
            return true;
        }
        return false;
    }
}
```