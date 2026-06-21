---
title: "Redisson 原理浅析"
tags:
  - "中间件"
  - "中间件/Redis"
  - "中间件/Redis/Redis"
  - "Redisson 原理浅析"
  - "Redisson 实现分布式锁"
  - "Redis"
updated: 2026-04-16
---

- Redisson 可以实现可重入的原理：
    ![[IMG-20260620224127760.png|623]]
- 如此多的 Redis 操作不能使用 Java 来实现了
- **Redisson 直接将** Lua 脚本字符串编写在代码中，保证原子性
    - **获取锁的脚本：**

    ```Lua
     local key = KEYS[1]; -- 锁的key
     local threadId = ARGV[1]; -- 线程唯一标识
     local releaseTime = ARGV[2]; -- 锁的自动释放时间
     -- 判断是否存在
     if(redis.call('exists', key) == 0) then
         -- 不存在, 获取锁
         redis.call('hset', key, threadId, '1');
         -- 设置有效期
         redis.call('expire', key, releaseTime);
         return 1; -- 返回结果
     end;
     -- 锁已经存在，判断threadId是否是自己
     if(redis.call('hexists', key, threadId) == 1) then
         -- 不存在, 获取锁，重入次数+1
         redis.call('hincrby', key, threadId, '1');
         -- 设置有效期
         redis.call('expire', key, releaseTime);
         return 1; -- 返回结果
     end;
     return 0; -- 代码走到这里,说明获取锁的不是自己，获取锁失败
    ```
    - **释放锁的脚本：**

    ```Lua
     local key = KEYS[1]; -- 锁的key
     local threadId = ARGV[1]; -- 线程唯一标识
     local releaseTime = ARGV[2]; -- 锁的自动释放时间
     -- 判断当前锁是否还是被自己持有
     if (redis.call('HEXISTS', key, threadId) == 0) then
         return nil; -- 如果已经不是自己，则直接返回
     end;
     -- 是自己的锁，则重入次数-1
     local count = redis.call('HINCRBY', key, threadId, -1);
     -- 判断是否重入次数是否已经为0
     if (count > 0) then
         -- 大于0说明不能释放锁，重置有效期然后返回
         redis.call('EXPIRE', key, releaseTime);
         return nil;
     else  -- 等于0说明可以释放锁，直接删除
         redis.call('DEL', key);
         return nil;
     end;
    ```
