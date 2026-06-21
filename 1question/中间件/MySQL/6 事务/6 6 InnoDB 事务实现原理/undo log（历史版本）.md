---
title: "undo log（历史版本）"
tags:
  - "中间件"
  - "中间件/MySQL"
  - "中间件/MySQL/事务"
  - "undo log(历史版本)"
  - "InnoDB 事务实现原理"
  - "MySQL"
updated: 2026-04-16
---

# 一、Undo log（历史版本）
1. 介绍
    1. **undo log 和 redo log 记录物理日志不一样，它是**==**逻辑日志**==
        1. **可以认为==当== `delete` ==一条记录时，undo log 中会记录一条对应的== `insert` ==记录==**
        2. 反之亦然，当 update 一条记录时，它记录一条对应相反的 update 记录
    2. **当执行 rollback 时，就可以从 undo log 中的逻辑记录读取到相应的内容并进行回滚，回滚至数据被修改前**的信息
2. **作用包含两个：**
    1. 提供回滚（保证事务的原子性）
    2. MVCC（多版本并发控制）
3. **Undo log 销毁：**
    1. 当 insert 的时候，产生的 undo log 日志只在回滚时需要，在事务提交后，可被立即删除
    2. 而 update、delete 的时候，产生的 undo log 日志不仅在回滚时需要，在快照读时也需要，不会立即被删除
4. Undo log 存储：
    1. undo log采用段的方式进行管理和记录
    2. 存放在前面介绍的 rollback segment 回滚段中，内部包含1024个undo log segment
