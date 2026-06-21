---
title: "使用 Redisson 分布式锁"
tags:
  - "中间件"
  - "中间件/Redis"
  - "中间件/Redis/Redis"
  - "使用 Redisson 分布式锁"
  - "Redisson 实现分布式锁"
  - "Redis"
updated: 2026-04-16
---

1. 引入依赖

    ```XML
     <dependency>
         <groupId>org.redisson</groupId>
         <artifactId>redisson</artifactId>
         <version>3.16.1</version>
     </dependency>
    ```
2. 配置类中，**添加`RedissonClient`组件**

    ```Java
     @Configuration
     public class RedissonConfig {
         @Bean
         public RedissonClient redissonClient(){
             //配置
             Config config = new Config();
             config.useSingleServer().setAddress("redis://192.168.10.151:6379").setPassword("111111");
             //创建RedissonClient对象，并返回
             return Redisson.create(config);
         }
     }
    ```
3. **调用`redissonClient.getLock()`、`tryLock()`、`unlock()`**

    ```Java
     //注入RedissonClient
     @Resource
     private RedissonClient redissonClient;
     @Transactional
     public Result getResult(Long voucherId) {
         //5. 一人限购一单
         Long userId = UserHolder.getUser().getId();
         //⭐创建锁对象
         RLock redisLock = redissonClient.getLock("lock:order:" + userId);
         //⭐尝试获取锁
         boolean isLock = redisLock.tryLock();   //不传参数则默认为非阻塞式获取锁
         if (!isLock) {
             return Result.fail("不能重复购买！");
         }
         try {
             //5.1 查询订单
             Integer count = query().eq("user_id", userId).eq("voucher_id", voucherId).count();
             //5.2 判断是否存在
             if (count > 0) {
                 return Result.fail("不能重复购买！");
             }
             //6. 扣减库存
             boolean success = SeckillVoucherService.update()
                     .setSql("stock = stock - 1")
                     .eq("voucher_id", voucherId)
                     .gt("stock",0)
                     .update();
             if (!success) {
                 return Result.fail("库存不足！");
             }
             //7. 创建订单
             VoucherOrder voucherOrder = new VoucherOrder();
             //7.1 设置订单Id、
             long voucherOrderId = redisWorker.nextID("voucher_order");
             voucherOrder.setId(voucherOrderId);
             //7.2 设置用户Id
             voucherOrder.setUserId(userId);
             //7.3 设置代金券Id
             voucherOrder.setVoucherId(voucherId);
             //8. 订单写入数据库
             save(voucherOrder);
             //9. 返回订单Id
             return Result.ok(voucherOrderId);
         } finally {
             //⭐释放锁
             redisLock.unlock();
         }
     }
    ```
4. 可以看到 基于Redisson 实现的分布式锁，使用的API，与之前自定义一个分布式锁的基本一致

    ![[IMG-20260620224127761.png|800]]
