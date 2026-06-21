---
title: "CyclicBarrier"
tags:
  - "CyclicBarrier"
  - "CountDownLatch"
  - "并发编程"
  - "线程"
  - "线程协作"
  - "多线程"
updated: 2026-04-16
---
- [[#一、介绍]]
- [[#二、代码示例]]

# 一、介绍
1. CyclicBarrier（循环障碍），**和 CountDownLatch 类似也是用来进行线程协作**
2. 与 CountDownLatch 不同的是
    1. 只有一个方法：**`await()`**
        1. **调用该方法会让计数器 -1，且只有计数器为 0 时，所有调用该方法的线程才能继续执行**
        2. **对比：CountDownLatch 中，子任务调用 `countDown()`，让计数器 `-1` ，之后还能继续执行**
    2. **`CyclicBarrier`** ==**可以被重用**==**，**⭐**当 CyclicBarrier 减为 0 时，再次调用 `await()` 计数器会被重置为初始值**
3. 适用的场景：
    1. CountDownLatch 子任务是独立的，所有子任务做完，用总任务汇总结果
    2. 🙋‍♂️ **CyclicBarrier 子任务之间有限制，比如子任务分好几步，只有**==**所有子任务都执行完第一步**==**，才能开始执行第二步；同样也可以用总任务汇总结果**

# 二、代码示例
```Java
public class CyclicBarrierTest {
    public static void main(String[] args) {
        CyclicBarrier cb = new CyclicBarrier(2, () -> {
            System.out.println("对子任务的汇总，可以通过 Runnable 接口从构造方法传入...");
        });
        // 循环两次，但使用的是同一个 CyclicBarrier
        for (int i = 0; i < 2; i++) {
            new Thread(()->{
                System.out.println("线程1开始.."+new Date());
                try { Thread.sleep(1); } catch (InterruptedException e) { e.printStackTrace(); }
                try {
                    // ⭐await() 会将计数器 -1，但如果 -1 后计数器不为 0，当前线程进入等待
                    cb.await();
                } catch (InterruptedException | BrokenBarrierException e) {
                    e.printStackTrace();
                }
            }).start();
            new Thread(()->{
                System.out.println("线程2开始.."+new Date());
                try { Thread.sleep(2); } catch (InterruptedException e) { e.printStackTrace(); }
                try {
                    // 此时 将计数器 -1，此时计数器减到了 0，此时，线程 1 也会被唤醒，线程 1，2 同时向下运行
                    cb.await();
                } catch (InterruptedException | BrokenBarrierException e) {
                    e.printStackTrace();
                }
            }).start();
        }
    }
}
```

运行结果

```Java
线程2开始..Wed Apr 05 19:01:54 CST 2023
线程2开始..Wed Apr 05 19:01:54 CST 2023
线程1开始..Wed Apr 05 19:01:54 CST 2023
线程1开始..Wed Apr 05 19:01:54 CST 2023
对子任务的汇总，可以通过 Runnable 接口从构造方法传入...
对子任务的汇总，可以通过 Runnable 接口从构造方法传入...
```