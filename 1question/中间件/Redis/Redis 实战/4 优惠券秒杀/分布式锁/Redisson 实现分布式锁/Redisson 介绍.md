1. 🚨上面 基于 `setnx` 实现的**自定义分布式锁**存在下面的**问题**：
    
    - **不可重入**：同一个线程无法多次获取同一把锁
    
    - **没有重试机制**：获取锁只尝试一次就返回false，没有重试机制
    
    - **超时释放**：锁超时释放虽然可以避免死锁，但如果是业务执行耗时较长，也会导致锁释放，存在安全隐患
    
    - **主从一致性**：如果Redis提供了主从集群，主从同步存在延迟，当主宕机时，如果从并同步主中的锁数据，则会出现锁实现
    
1. **Redisson**
    
    - 是一个在 Redis 的基础上实现的 Java 驻内存数据网格（In-Memory Data Grid）
    
    - 它不仅提供了一系列的分布式的 Java 常用对象，**还提供了许多分布式服务，其中就包含了各种**==**分布式锁的实现**==
        
        ![[IMG-20260405035438405.png|Untitled 568.png]]
        
    
1. 官网地址：
    
    > [!info] Redisson: Redis Java client with features of In-Memory Data Grid  
    > Redis Java client with features of In-Memory Data Grid.  
    > [https://redisson.org/](https://redisson.org/)  
    
1. GitHub地址：
    
    > [!info] GitHub - redisson/redisson: Redisson - Redis Java client with features of In-Memory Data Grid. Over 50 Redis based Java objects and services: Set, Multimap, SortedSet, Map, List, Queue, Deque, Semaphore, Lock, AtomicLong, Map Reduce, Publish / Subscribe, Bloom filter, Spring Cache, Tomcat, Scheduler, JCache API, Hibernate, MyBatis, RPC, local cache ...  
    > Redisson - Redis Java client with features of In-Memory Data Grid.  
    > [https://github.com/redisson/redisson](https://github.com/redisson/redisson)  
    
1. ==**实际开发中，并不需要自定义分布式锁，直接调用 Redisson 即可**==