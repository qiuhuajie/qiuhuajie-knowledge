# 1. **简介**
1. SkipList（跳表）首先是链表，但与传统链表相比有几点差异：
    
    1. 元素按照升序排列存储
    
    1. 节点可能包含多级指针，不同级指针跨度不同（最多允许32级指针）
    
1. SkipList 的结构：
    
    ![[IMG-20260404031937066.png|Untitled 573.png]]
    
# 2. **SkipList 的特性总结⭐**
1. 跳跃表是一个==**双向链表**==
    
    - 每个节点都包含 `score` 和 `ele` 值
    
    - **节点按照** `score` **值**==**排序**==，`score` 值一样则按照 `ele` 字典排序
    
1. 每个节点都可以包含==**多级指针**==，层数是 `1 ~ 32` 之间的随机数
    
    - 不同层指针到下一个节点的跨度不同，层级越高，跨度越大
    
1. **增删改查效率与红黑树基本一致**，实现却更简单
  
# 3. **源码**
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
    
1. zskiplistNode
    
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
    
1. **一级指针图示：**
    
    ![[IMG-20260404031937129.png|Untitled 1 425.png]]
    
1. **二级指针图示：**
    
    ![[IMG-20260404031937189.png|Untitled 2 346.png]]
    
1. **三级指针图示：**
    
    ![[IMG-20260404031937266.png|Untitled 3 262.png]]