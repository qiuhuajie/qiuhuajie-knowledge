1. **归档日志**
    
    1. binlog 是 MySQL 的 ==Server 层==实现的，所有引擎都可以使用
    
    1. binlog 是==逻辑日志==，记录的是这个语句（增删改）的原始逻辑，比如==“给 ID=2 这一行的 c 字段加 1 ”==
    
    1. binlog 是可以==追加写入==的，“追加写”是指 binlog 文件写到一定大小后会切换到下一个，并不会覆盖以前的日志
    
1. **作用：**
    
    1. ==实现主从复制==，从库利用主库上的 binlog 进行重播
    
    1. 用于数据库的基于时间点的还原
    
1. InnoDB 中 redolog 并不是一次性写完的，而是分两阶段
    
    1. 第一阶段：prepare 阶段，将事务操作写入 redo log，将 redo log 设置为 `prepare` 状态
    
    1. 第二阶段：commit 阶段：将事务操作写入 bin log，将 redo log 改成 `commit` 状态
    
1. **有了 bin log 为什么还需要 redo log**❓
    
    1. redo log 是 InnoDB 引擎特有的日志，而 bin log 是 Server 层的日志
    
    1. 如果 MySQL ==只依靠 binlog 等== **==server 层日志是没有 crash-safe （容灾恢复）能力的==**
        
        1. bin log 是**追加日志**，保存的是**==全量的日志==**。==没有标志能让 InnoDB 从 bin log 中判断哪些数据已经刷入磁盘了，哪些数据还没有==
        
        1. 举个例子，bin log 记录了两条日志：
            
            ![[IMG-20260405035438347.png|Untitled 442.png]]
            
            - 假设在记录 1 刷盘后，记录 2 未刷盘时，数据库崩溃
            
            - 重启后，只通过 bin log 数据库是无法判断这两条记录哪条已经写入磁盘，哪条没有写入磁盘，导致没法进行正确的数据恢复
            
        
        1. **但 redo log 不一样，==只要刷入磁盘的数据，都会从 redo log 中被抹掉==，数据库重启后，直接把 redo log 中的数据都恢复至内存就可以了**
        
    

> [!important] **知识点串联：[[面试题汇总]]**