---
title: "ReentrantReadWriteLock"
tags:
  - "ReentrantReadWriteLock"
  - "SHARED"
  - "EXCLUSIVE"
  - "ReentrantLock"
  - "读锁"
  - "写锁"
updated: 2026-04-16
---
- [[#一、介绍]]
- [[#二、流程]]
    - [[#1. T1 w.lock，t2 r.lock]]
    - [[#2. T3 r.lock，t4 w.lock]]
    - [[#3. T1 w.unlock]]
    - [[#4. T2 r.unlock，t3 r.unlock]]

# 一、介绍
1. ReentrantReadWriteLock 底层是**基于 ReentrantLock 和 AbstractQueuedSynchronizer 来实现的**，所以，ReentrantReadWriteLock 的数据结构也依托于 AQS 的数据结构
2. 作用：
    - ==当读操作远远高于写操作时，使用读写锁，可以让==**==读读并发==**==，让==**==读-写、写-写互斥==**==，保证==**==数据安全==**==的同时，==**==提高性能==**
3. 类似于数据库中的当前读：**`select ... lock in share mode`**
    1. 加一个共享锁，读取的是记录的最新版本
    2. 读取时还要保证其他并发事务不能修改当前记录，会对读取的记录进行加锁
4. 注意事项：
    1. 读锁不支持条件变量
    2. 重入时升级不支持：即持有读锁的情况下去获取写锁，会导致获取写锁永久等待
    3. 重入时降级支持：即持有写锁的情况下去获取读锁

# 二、流程
## 1. T1 w.lock，t2 r.lock
1. t1 成功上锁，流程与 ReentrantLock 加锁相比没有特殊之处，不==同是====**写锁状态占了 state 的低 16 位，而读锁使用的是 state 的高 16 位**==

    ![[IMG-20260619222945928.png|442]]

2. t2 执行 r.lock，这时进入读锁的 sync.acquireShared(1) 流程，首先会进入 tryAcquireShared 流程。首先看写锁位置是不是 1，如果是 1，会再看当前占用线程是不是自己（因为写锁在重入时，是可以降级成读锁的），如果上面两个条件不满足，那么 tryAcquireShared 返回 -1 表示获取锁失败

    ![[IMG-20260619222945998.png|457]]

3. 获取锁失败后，会进入 sync.doAcquireShared(1) 流程，首先也是调用 addWaiter 添加节点，不同之处在于==**读锁**==**节点被设置为** **`Node.SHARED`** **模式**
4. t2 会看看自己的节点是不是老二，如果是，还会再次调用 tryAcquireShared(1) 来尝试获取锁
5. 如果没有成功，在 doAcquireShared 内 for (;;) 循环一次，把前驱节点的 waitStatus 改为 -1，再 for (;;) 循环一
6. 次尝试 tryAcquireShared(1) 如果还不成功，那么在 parkAndCheckInterrupt() 处 park

    ![[IMG-20260619222946053.png|621]]

## 2. T3 r.lock，t4 w.lock
1. 这种状态下，假设又有 t3 加读锁和 t4 加写锁，这期间 t1 仍然持有锁，就变成了下面的样子
2. 注意 t2、t3 加的是读锁，它们的 Node 节点是 SHARED 模式，而 **t4 加的是**==**写锁**==**，它的 Node 节点是** **`Node.EXCLUSIVE`** **模式**

    ![[IMG-20260619222946108.png|940]]

## 3. T1 w.unlock
1. 这时会走到写锁的 sync.release(1) 流程，调用 sync.tryRelease(1) 成功，变成下面的样子

    ![[IMG-20260619222946183.png|800]]

2. 接下来执行唤醒流程 sync.unparkSuccessor，即让老二恢复运行，这时 t2 在 doAcquireShared 内 parkAndCheckInterrupt() 处恢复运行
3. 这回 t2 再来一次 for (;;) 执行 tryAcquireShared 成功则让读锁计数加一

    ![[IMG-20260619222946222.png|800]]

4. 这时 t2 已经恢复运行，接下来 t2 调用 setHeadAndPropagate(node, 1)，它原本所在节点被置为头节点

    ![[IMG-20260619222946265.png|666]]

5. **事情还没完，⭐**==**在 setHeadAndPropagate 方法内还会检查下一个节点是否是 shared**==**，如果是则调用 doReleaseShared() 将 head 的状态从 -1 改为 0 并唤醒老二**，这时 t3 在 doAcquireShared 内 parkAndCheckInterrupt() 处恢复运行

    ![[IMG-20260619222946305.png|681]]

6. 这回再来一次 for (;;) 执行 tryAcquireShared 成功则让读锁计数加一，⭐**==此时两个读线程 t2、t3 可以同时获得锁，可以并发执行。读锁计数器此时为 2==**

    ![[IMG-20260619222946346.png|705]]

7. 这时 t3 已经恢复运行，接下来 t3 调用 setHeadAndPropagate(node, 1)，它原本所在节点被置为头节点

    ![[IMG-20260619222946419.png|533]]

8. 由于，==**下一个节点不是 SHARED 了，因此不会继续唤醒 t4 所在节点**==
9. ⭐==**这也是为什么读读可以并发的原因：在唤醒等待节点时，一下子将一串连着的 SHARED 节点都唤醒，直到遇到一个 EXCLUSIVE 模式的节点**==
## 4. T2 r.unlock，t3 r.unlock
1. t2 进入 sync.releaseShared(1) 中，调用 tryReleaseShared(1) 让计数减一，但由于计数还不为零

    ![[IMG-20260619222946483.png|546]]

2. t3 进入 sync.releaseShared(1) 中，调用 tryReleaseShared(1) 让计数减一，这回计数为零了，进入 doReleaseShared() 将头节点从 -1 改为 0 并唤醒老二，即

    ![[IMG-20260619222946549.png|556]]

3. 之后 t4 在 acquireQueued 中 parkAndCheckInterrupt 处恢复运行，再次 for (;;) 这次自己是老二，并且没有其他竞争，tryAcquire(1) 成功，修改头结点，流程结束

    ![[IMG-20260619222946609.png|412]]
