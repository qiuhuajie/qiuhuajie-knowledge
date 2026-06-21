---
title: "Semaphore 工具锁"
tags:
  - "Semaphore"
  - "加锁解锁流程"
  - "并发编程"
  - "同步"
  - "线程"
  - "AQS"
updated: 2026-04-16
---
- [[#一、介绍]]
- [[#二、代码示例]]
- [[#三、Semaphore 原理]]
    - [[#1. 加锁解锁流程]]
    - [[#2. 源码]]

# 一、介绍
1. Semaphore 其底层也是由 AQS 提供支持的一个同步器锁，相对简单，更像是一个工具锁，用来简化实现线程间的通讯

    ![[IMG-20260619224137192.png|576]]

2. Semaphore 与 ReentrantLock 的内部类的结构相同，类内部总共存在 Sync、NonfairSync、FairSync 三个类，默认是一个 非公平锁
3. **可以用来**==**限制能同时访问共享资源的线程上限**==**，可以理解为停车场门口的空闲车位的数量提示牌**
    1. 和 LockSupport 类似，也是使用 **许可** 的概念来控制线程上限，这个许可数可以在构造方法中传入

        ![[IMG-20260619224137285.png|301]]

    2. 实际就是这个许可数量赋值给了同步器中的 **`state`**

    ![[IMG-20260619224137352.png|197]]

4. API 方法
    1. **`acquire()`**、**`acquire(int permits)`**：此方法从信号量获取一个（多个）许可，在提供一个许可前一直将线程阻塞，或者线程被中断
    2. **`release()`**、**`release(int permits)`**：此方法释放一个（多个）许可，将其返回给信号量

# 二、代码示例
```Java
public class test {
    public static void main(String[] args) throws InterruptedException {
        // 1. 创建 semaphore 对象
        Semaphore semaphore = new Semaphore(3);
        // 2. 10个线程同时运行
        for (int i = 0; i < 10; i++) {
            new Thread(() -> {
        // 3. 获取许可
                try {
                    semaphore.acquire();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                try {
                    System.out.println(Thread.currentThread().getName() + " running...");
                    Thread.sleep(1);
                    System.out.println(Thread.currentThread().getName() + " end...");
                } catch (InterruptedException e) {
                    e.printStackTrace();
                } finally {
                // 4. 释放许可
                    semaphore.release();
                }
            }).start();
        }
    }
}
```

**运行结果：可以看到**==**启动了 10 个线程，但是在同一时刻只能有 3 个线程在执行**==

```Java
Thread-1 running...
Thread-2 running...
Thread-0 running...
Thread-2 end...
Thread-0 end...
Thread-1 end...
Thread-3 running...
Thread-4 running...
Thread-6 running...
Thread-4 end...
Thread-3 end...
Thread-5 running...
Thread-6 end...
Thread-8 running...
Thread-7 running...
Thread-5 end...
Thread-8 end...
Thread-7 end...
Thread-9 running...
Thread-9 end...
```
# 三、Semaphore 原理
## 1. 加锁解锁流程
1. Semaphore 有点像一个停车场，permits 就好像停车位数量，当线程获得了 permits 就像是获得了停车位，然后停车场显示空余车位减一
2. 刚开始，**permits（**`state`**）为 3**，这时 5 个线程来获取资源

    ![[IMG-20260619224137420.png|469]]

3. 假设其中 Thread-1，Thread-2，Thread-4 cas 竞争成功，而 Thread-0 和 Thread-3 竞争失败，进入 AQS 队列park 阻塞

    ![[IMG-20260619224137503.png|873]]

4. 这时 Thread-4 释放了 permits，状态如下

    ![[IMG-20260619224137567.png|864]]

5. 接下来 Thread-0 竞争成功，permits 再次设置为 0，设置自己为 head 节点，断开原来的 head 节点，unpark 接下来的 Thread-3 节点，但由于 permits 是 0，因此 Thread-3 在尝试不成功后再次进入 park 状态

    ![[IMG-20260619224137629.png|720]]

## 2. 源码
```Java
// 内部类，继承自AQS
abstract static class Sync extends AbstractQueuedSynchronizer {
    // 版本号
    private static final long serialVersionUID = 1192457210091910933L;
    // 构造函数
    Sync(int permits) {
        // 设置状态数
        setState(permits);
    }
    // 获取许可
    final int getPermits() {
        return getState();
    }
    // 共享模式下非公平策略获取
    final int nonfairTryAcquireShared(int acquires) {
        for (;;) { // 无限循环
            // 获取许可数
            int available = getState();
            // 剩余的许可
            int remaining = available - acquires;
            if (remaining < 0 ||
                compareAndSetState(available, remaining)) // 许可小于0或者比较并且设置状态成功
                return remaining;
        }
    }
    // 共享模式下进行释放
    protected final boolean tryReleaseShared(int releases) {
        for (;;) { // 无限循环
            // 获取许可
            int current = getState();
            // 可用的许可
            int next = current + releases;
            if (next < current) // overflow
                throw new Error("Maximum permit count exceeded");
            if (compareAndSetState(current, next)) // 比较并进行设置成功
                return true;
        }
    }
    // 根据指定的缩减量减小可用许可的数目
    final void reducePermits(int reductions) {
        for (;;) { // 无限循环
            // 获取许可
            int current = getState();
            // 可用的许可
            int next = current - reductions;
            if (next > current) // underflow
                throw new Error("Permit count underflow");
            if (compareAndSetState(current, next)) // 比较并进行设置成功
                return;
        }
    }
    // 获取并返回立即可用的所有许可
    final int drainPermits() {
        for (;;) { // 无限循环
            // 获取许可
            int current = getState();
            if (current == 0 || compareAndSetState(current, 0)) // 许可为0或者比较并设置成功
                return current;
        }
    }
}
```
