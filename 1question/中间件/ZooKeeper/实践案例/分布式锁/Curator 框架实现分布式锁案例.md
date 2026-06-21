---
title: "Curator 框架实现分布式锁案例"
tags:
  - "中间件"
  - "中间件/ZooKeeper"
  - "中间件/ZooKeeper/实践案例"
  - "分布式锁"
  - "ZooKeeper"
  - "CountdownLatch"
updated: 2026-04-16
---

1. **原生的 Java API 分布式开发存在的问题**
    1. 会话连接是异步的，需要自己去处理。比如使用 CountDownLatch
    2. Watch 需要重复注册，不然就不能生效
    3. 开发的复杂性还是比较高的
    4. 不支持多节点删除和创建。需要自己去递归
2. Curator 是一个专门解决分布式锁的框架，解决了原生 Java API 开发分布式遇到的问题

    官方文档：
> ℹ️ Apache Curator -
> Curator n ˈkyoor͝ˌātər: a keeper or custodian of a museum or other collection - A ZooKeeper Keeper.
> [https://curator.apache.org/index.html](https://curator.apache.org/index.html)
3. Curator 案例实操
    1. 添加依赖

    ```XML
     <dependency>
         <groupId>org.apache.curator</groupId>
         <artifactId>curator-framework</artifactId>
         <version>4.3.0</version>
     </dependency>
     <dependency>
         <groupId>org.apache.curator</groupId>
         <artifactId>curator-recipes</artifactId>
         <version>4.3.0</version>
     </dependency>
     <dependency>
         <groupId>org.apache.curator</groupId>
         <artifactId>curator-client</artifactId>
         <version>4.3.0</version>
     </dependency>
    ```
    2. 代码实现

    ```Java
     public class CuratorLockTest {
         public static void main(String[] args) {
             new CuratorLockTest().test();
         }
         private void test() {
             final InterProcessMutex lock1 = new InterProcessMutex(getCuratorFramework(), "/locks");
             final InterProcessMutex lock2 = new InterProcessMutex(getCuratorFramework(), "/locks");
             new Thread(new Runnable() {
                 @Override
                 public void run() {
                     try {
                         lock1.acquire();
                         System.out.println("线程1 获取到锁");
                         lock1.acquire();
                         System.out.println("线程1 再次获取到锁");
                         Thread.sleep(5 * 1000);
                         lock1.release();
                         System.out.println("线程1 释放锁");
                         lock1.release();
                         System.out.println("线程1 再次释放锁");
                     } catch (Exception e) {
                         e.printStackTrace();
                     }
                 }
             }).start();
             new Thread(new Runnable() {
                 @Override
                 public void run() {
                     try {
                         lock2.acquire();
                         System.out.println("线程2 获取到锁");
                         lock2.acquire();
                         System.out.println("线程2 再次获取到锁");
                         Thread.sleep(5 * 1000);
                         lock2.release();
                         System.out.println("线程2 释放锁");
                         lock2.release();
                         System.out.println("线程2 再次释放锁");
                     } catch (Exception e) {
                         e.printStackTrace();
                     }
                 }
             }).start();
         }
         private static CuratorFramework getCuratorFramework() {
             //重试策略：初试时间 3 秒，重试 3 次
             ExponentialBackoffRetry policy = new ExponentialBackoffRetry(3000, 3);
             //通过工厂创建 Curator
             CuratorFramework client = CuratorFrameworkFactory.builder().connectString("hadoop102:2181,hadoop103:2181,hadoop104:2181").connectionTimeoutMs(2000).sessionTimeoutMs(2000).retryPolicy(policy).build();
             //开始连接
             client.start();
             System.out.println("zookeeper 启动成功");
             return client;
         }
     }
    ```
    3. 测试结果：

    ![[Attachment/1question/中间件/ZooKeeper/实践案例/分布式锁/IMG-20260405035438371.png|369]]
