# 1. **简介**
1. ZipList 存在的问题：
    
    1. 问题1：**ZipList虽然节省内存，但申请内存必须是连续空间**，如果内存占用较多，**内存空间中可能没有足够的连续空间**，申请内存效率很低。怎么办？
        
        > 为了缓解这个问题，我们必须限制ZipList的长度和entry大小
        
    
    1. 问题2：但是我们**要存储大量数据，超出了ZipList最佳的上限**该怎么办？
        
        > 我们可以创建多个ZipList来分片存储数据
        
    
    1. 问题3：**数据拆分后比较分散，不方便管理和查找，这多个ZipList如何建立联系**？
        
        > Redis在3.2版本引入了新的数据结构QuickList，它是一个双端链表，只不过QuickList链表中的每个节点都是一个ZipList
        
    
1. QuickList 的结构：`LinkList + ZipList`
    
    ![[IMG-20260405035438404.png|Untitled 8 79.png]]
    
# 2. **QuickList 的特性总结⭐**
1. 是一个==**节点为 ZipList 的双端链表**==
    
    1. **节点采用 ZipList，解决了**==**传统链表的内存占用**==**问题**
    
    1. **创建多个 ZipList 来分片存储数据，**==**控制了 ZipList 大小**==**，解决连续内存空间申请效率问题**
    
1. 中间节点可以压缩，进一步节省了内存
# 3. QuickList 的参数设置
1. `list-max-ziplist-size`：
    
    1. **为了避免QuickList中的每个ZipList中entry过多**，Redis提供了一个配置项：list-max-ziplist-size来限制
        
        1. 如果值为正，则代表ZipList的允许的entry个数的最大值
        
        1. 如果值为负，则代表ZipList的最大内存大小，分5种情况：
            
            1. `1`：每个ZipList的内存占用不能超过4kb
            
            1. `2`：每个ZipList的内存占用不能超过8kb
            
            1. `3`：每个ZipList的内存占用不能超过16kb
            
            1. `4`：每个ZipList的内存占用不能超过32kb
            
            1. `5`：每个ZipList的内存占用不能超过64kb
            
        
    
    1. 默认值为 `2`：
        
        ![[IMG-20260405035500166.png|Untitled 574.png]]
        
    
1. `list-compress-depth`：
    
    1. 除了控制ZipList的大小，QuickList还可以**对节点的ZipList做压缩**，通过配置项list-compress-depth来控制
    
    1. 因为链表一般都是从**首尾访问较多，所以首尾是不压缩的**。这个参数是控制首尾不压缩的节点个数：
        
        1. `0`：特殊值，代表不压缩
        
        1. `1`：标示QuickList的首尾各有1个节点不压缩，中间节点压缩
        
        1. `2`：标示QuickList的首尾各有2个节点不压缩，中间节点压缩
        
        1. 以此类推
        
    
    1. 默认值为 `0`：
        
        ![[IMG-20260405035509555.png|Untitled 1 426.png]]
        
    
# 4. **源码**
以下是QuickList的和QuickListNode的结构源码：
1. quicklist
    
    ```C
     typedef struct quicklist {
         // 头节点指针
         quicklistNode *head;
         // 尾节点指针
         quicklistNode *tail;
         // 所有ziplist的entry的数量
         unsigned long count;
         // ziplists总数量
         unsigned long len;
         // ziplist的entry上限，默认值 -2
         int fill : QL_FILL_BITS;     •    // 首尾不压缩的节点数量
         unsigned int compress : QL_COMP_BITS;
         // 内存重分配时的书签数量及数组，一般用不到
         unsigned int bookmark_count: QL_BM_BITS;
         quicklistBookmark bookmarks[];
     } quicklist;
    ```
    
1. quicklistNode
    
    ```C
     typedef struct quicklistNode {
         // 前一个节点指针
         struct quicklistNode *prev;
         // 下一个节点指针
         struct quicklistNode *next;
         // 当前节点的ZipList指针
         unsigned char *zl;
         // 当前节点的ZipList的字节大小
         unsigned int sz;
         // 当前节点的ZipList的entry个数
         unsigned int count : 16;
         // 编码方式：1，ZipList; 2，lzf压缩模式
         unsigned int encoding : 2;
         // 数据容器类型（预留）：1，其它；2，ZipList
         unsigned int container : 2;
         // 是否被解压缩。1：则说明被解压了，将来要重新压缩
         unsigned int recompress : 1;
         unsigned int attempted_compress : 1; //测试用
         unsigned int extra : 10; /*预留字段*/
     } quicklistNode;
    ```
    
    ![[IMG-20260405035517424.png|Untitled 2 347.png]]