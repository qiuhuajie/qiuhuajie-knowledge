---
title: "SkipList"
tags:
  - "中间件"
  - "中间件/Redis"
  - "中间件/Redis/Redis 原理"
  - "SkipList"
  - "详解"
  - "Redis"
updated: 2026-04-16
---

# 一、简介
1. SkipList（跳表）首先是链表，但与传统链表相比有几点差异：
    1. 元素按照升序排列存储
    2. 节点可能包含多级指针，不同级指针跨度不同（最多允许32级指针）
2. SkipList 的结构：

    ![[IMG-20260620224127754.png|800]]

# 二、SkipList 的特性总结⭐
1. 跳跃表是一个==**双向链表**==
    - 每个节点都包含 `score` 和 `ele` 值
    - **节点按照** `score` **值**==**排序**==，`score` 值一样则按照 `ele` 字典排序
2. 每个节点都可以包含==**多级指针**==，层数是 `1 ~ 32` 之间的随机数
    - 不同层指针到下一个节点的跨度不同，层级越高，跨度越大
3. **增删改查效率与红黑树基本一致**，实现却更简单

# 三、源码
1. zskiplist

    ```C
     // t_zset.c
     typedef struct zskiplist {
         // 头尾节点指针
         struct zskiplistNode *header, *tail;
         // 节点数量
         unsigned long length;
         // 最大的索引层级，默认是1
         int level;
     } zskiplist;
    ```
2. zskiplistNode

    ```C
     // t_zset.c
     typedef struct zskiplistNode {
         sds ele; // 节点存储的值
         double score;// 节点分数，排序、查找用
         struct zskiplistNode *backward; // 前一个节点指针
         struct zskiplistLevel {
             struct zskiplistNode *forward; // 下一个节点指针
             unsigned long span; // 索引跨度
         } level[]; // 多级索引数组
     } zskiplistNode;
    ```
3. **一级指针图示：**

    ![[IMG-20260620224133367.png|800]]

4. **二级指针图示：**

    ![[IMG-20260620224139194.png|800]]

5. **三级指针图示：**

    ![[IMG-20260620224144348.png|800]]
