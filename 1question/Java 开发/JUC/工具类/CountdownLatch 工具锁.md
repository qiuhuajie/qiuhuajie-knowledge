---
title: "CountdownLatch 工具锁"
tags:
  - "CountDownLatch"
  - "并发编程"
  - "线程"
  - "线程池"
  - "同步"
  - "AQS"
updated: 2026-04-16
---
- [[#一、介绍]]
- [[#二、代码示例]]
    - [[#1. 子任务和汇总任务的通讯]]
    - [[#2. 两个任务之间通讯]]

# 一、介绍
1. CountdownLatch 其底层是由 AQS 提供支持的一个同步器锁，相对简单，更像是一个工具锁，用来简化实现线程间的通讯

    ![[IMG-20260619224229529.png|631]]

2. 使用 CountDownLatch 的好处
    1. **CountDownLatch 代替 `wait()` `notify()` 好处是通讯方式简单，不涉及锁**
3. ==**使用场景：**==
    1. 用在**子任务和结果汇总任务之间的通讯**
        1. 将一个程序分为 n 个互相独立的可解决任务，并创建值为 n 的 CountDownLatch
        2. 当每一个任务完成时，都会在这个锁存器上**调用 `countDown()`，让计数器 `-1`**
        3. 汇总 n 个子任务的代码**调用这个锁存器的 `await()`，将他们自己拦住**
        4. **直至锁存器计数减至 `0`，这个汇总任务会被唤醒，即可开始结果汇总**
    2. **在使用线程池时，线程会被复用，使用 CountDownLatch 可以用来判断提交的任务是否已经执行完成**[[ThreadPoolExecutor]]

# 二、代码示例
## 1. 子任务和汇总任务的通讯
1. t4 线程需要在前三个线程完成任务后，进行汇总工作

    ```Java
    public class CountDownLatchTest2 {
        public static void main(String[] args) throws InterruptedException {
            CountDownLatch latch = new CountDownLatch(3);
            ExecutorService service = Executors.newFixedThreadPool(4);
            service.submit(() -> {
                System.out.println("t1 begin...");
                try { Thread.sleep(1); } catch (InterruptedException e) { e.printStackTrace(); }
    						// 子任务每次执行完，都调用 countDown() 将计数器 -1
                latch.countDown();
                System.out.println("t1 end... " + latch.getCount());
            });
            service.submit(() -> {
                System.out.println("t2 begin...");
                try { Thread.sleep(2); } catch (InterruptedException e) { e.printStackTrace(); }
                latch.countDown();
                System.out.println("t2 end... " + latch.getCount());
            });
            service.submit(() -> {
                System.out.println("t3 begin...");
                try { Thread.sleep(3); } catch (InterruptedException e) { e.printStackTrace(); }
                latch.countDown();
                System.out.println("t3 end... " + latch.getCount());
            });
            service.submit(()->{
                try {
                    System.out.println("t4 waiting...");
                    // t4 调用 await() 等待计数器被减为 0
                    latch.await();
                    System.out.println("t4 wait end...");
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            });
        }
    }
    ```
2. 运行结果

    ```Java
    t1 begin...
    t2 begin...
    t3 begin...
    t1 end... 2
    t4 waiting...
    t2 end... 1
    t3 end... 0
    t4 wait end...
    ```
## 2. 两个任务之间通讯
- 实现一个容器
    - 提供两个方法：add，size
    - 写两个线程，线程 1 添加 10 个元素到容器中，线程 2 实现监控元素的个数，当个数到 5 个时，线程 2 给出提示并结束

    ```Java
    import java.util.ArrayList;
    import java.util.List;
    import java.util.concurrent.CountDownLatch;
    public class T3 {
       volatile List list = new ArrayList();
        public void add(int i){
            list.add(i);
        }
        public int getSize(){
            return list.size();
        }
        public static void main(String[] args) {
            T3 t = new T3();
            CountDownLatch countDownLatch = new CountDownLatch(1);
            new Thread(() -> {
                System.out.println("t2 start");
               if(t.getSize() != 5){
                   try {
                       // 线程 2 等待
                       countDownLatch.await();
                       System.out.println("t2 end");
                   } catch (InterruptedException e) {
                       e.printStackTrace();
                   }
               }
            },"t2").start();
            new Thread(()->{
                System.out.println("t1 start");
               for (int i = 0;i<9;i++){
                   t.add(i);
                   System.out.println("add"+ i);
                   if(t.getSize() == 5){
                       System.out.println("countdown is open");
                       // 线程 1 发现容器大小为 5 时，通知线程 2
                       countDownLatch.countDown();
                   }
               }
                System.out.println("t1 end");
            },"t1").start();
        }
    }
    ```