- [[#1. 简介]]
- [[#2. Dict 插入]]
- [[#3. Dict 扩容]]
- [[#4. Dict 缩容]]
- [[#5. Dict 的 rehash]]
- [[#6. Dict 的 渐进式 rehash]]
  
# 1. **简介**
1. Redis是一个键值型（Key-Value Pair）的数据库，我们可以根据键实现快速的增删改查，而键与值的映射关系正是通过Dict来实现的
1. Dict由三部分组成，分别是：哈希表（DictHashTable）、哈希节点（DictEntry）、字典（Dict）
    
    - **哈希表**
        
        ![[IMG-20260405035438403.png|Untitled 576.png]]
        
        > size 的大小规定一顶是一个 2^n，即二进制表示时，有且只有一位为 1
        > 
        > `sizemask` 总是 = `size-1`，即刚好 `+1` 即可进位为 `size`
        
    
    - **哈希节点**
        
        ![[IMG-20260405035459929.png|Untitled 1 428.png]]
        
        > Union：C语言中的联合体，表示v 可以是体中的任意一种，且只能是其中一种
        
    
    - **字典**
        
        ![[IMG-20260405035500047.png|Untitled 2 349.png]]
        
        > 不同的场景需要的hash函数不同，故dict可以定义不同的dicType，来决定使用什么hash函数计算hash值
        > 
        > Dict包含两个 `ht[]`：`ht[0]`平常用，`ht[1]`用来rehash，详见 rehash
        
    
# 2. **Dict 插入**
1. **当向 Dict 中添加键值对时:**
1. ==Redis首先根据key计算出hash值（h），然后利用====`h & sizemask`== ==来计算元素应该存储到数组中的哪个索引位置==
    
    > 这里h & sizemask 的作用其实就是取余
    > 
    > 1. `sizemask`掩码总是 = `size-1`，又因为 `size` 有且只有一位为 `1`，也即掩码刚好是size去掉唯一的`1`，再将后边的位数全用`1`来填充
    > 
    > 1. 如：key计算出的hash值 `h = 0001 0101`， `size = 0000 1000`，那么 `sizemask = 0000 0111`
    > 
    > 1. `h = 0001 0101` 与 `sizemask = 0000 0111` 做与运算，得到 `h & sizemask = 0000 0101`
    > 
    > 1. 刚好是 `h` 与 `size` 取余运算得到的
    
1. 如当存储 k1= v1，假设k1的哈希值 h = 1，则 1 & 3 =1，因此k1=v1要存储到数组角标1位置
    
    ![[IMG-20260405035509504.png|Untitled 3 264.png]]
    
1. 如当存储 k2= v2，假设k2的哈希值也是 h = 1，则 1 & 3 =1，因此k2=v2也要存储到数组角标1位置，则会以**头插法**，插入链表头部
    
    ![[IMG-20260405035517368.png|Untitled 4 203.png]]
    
    > 类似 java 的 HashTable，底层是数组 + 链表来解决哈希冲突
    
# 3. **Dict 扩容**
1. Dict中的HashTable就是数组结合单向链表的实现
1. 存在的问题：当集合中元素较多时，必然导致哈希冲突增多，链表过长，则查询效率会大大降低
1. Dict在每次新增键值对时都会检查**负载因子**（`LoadFactor = used/size`） ，满足以下两种情况时会触发**哈希表扩容**：
    
    - 情况一：哈希表的 `LoadFactor >= 1`，并且服务器没有执行 BGSAVE 或者 BGREWRITEAOF 等后台进程
    
    - 情况二：哈希表的 `LoadFactor > 5`
    
    ```C
     static int _dictExpandIfNeeded(dict *d){
         // 如果正在rehash，则返回ok
         if (dictIsRehashing(d)) return DICT_OK;   // 如果哈希表为空，则初始化哈希表为默认大小：4
         if (d->ht[0].size == 0) return dictExpand(d, DICT_HT_INITIAL_SIZE);
         // 当负载因子（used/size）达到1以上，并且当前没有进行bgrewrite等子进程操作
         // 或者负载因子超过5，则进行 dictExpand ，也就是扩容
         if (d->ht[0].used >= d->ht[0].size &&
             (dict_can_resize || d->ht[0].used/d->ht[0].size > dict_force_resize_ratio){
             // 扩容大小为used + 1，底层会对扩容大小做判断，实际上找的是第一个大于等于 used+1 的 2^n
             return dictExpand(d, d->ht[0].used + 1);
         }
         return DICT_OK;
     }
    ```
    
# 4. **Dict 缩容**
1. Dict除了扩容以外，每次删除元素时，也会对负载因子做检查
1. 当`LoadFactor < 0.1` 时，会做哈希表收缩：
    
    ```C++
     // t_hash.c # hashTypeDeleted()
     ...
     if (dictDelete((dict*)o->ptr, field) == C_OK) {
         deleted = 1;
         // 删除成功后，检查是否需要重置Dict大小，如果需要则调用dictResize重置•    /* Always check if the dictionary needs a resize after a delete. */
         if (htNeedsResize(o->ptr)) dictResize(o->ptr);
     }
     ...
    ```
    
# 5. **Dict 的 rehash**
1. rehash 解决的问题：
    
    1. 不管是扩容还是收缩，必定会创建新的哈希表，==导致哈希表的====`size`====和====`sizemask`====变化，而key的查询与====`sizemask`====有关==
    
    1. 因此，⭐原来旧元素的位置是使用旧掩码计算出来的位置，当再次查询时，使用的是新掩码，会导致找不到元素
    
1. **因此必须对哈希表中的每一个key**==**重新计算索引，插入新的哈希表**==**，这个过程称为rehash**
1. 这里就是为什么 Dict 定义的数据结构中要有两个 `ht[]` 的原因
    
    ![[IMG-20260405035530288.png|Untitled 6 129.png]]
    
    ![[IMG-20260405035524348.png|Untitled 5 157.png]]
    
1. rehash 的过程是这样的：
    
    1. 计算新hash表的 `realeSize`，值取决于当前要做的是扩容还是收缩：
        
        - 如果是扩容，则新size为：第一个大于等于`dict.ht[0].used + 1`的 2n
        
        - 如果是收缩，则新size为：第一个大于等于`dict.ht[0].used`的 2n （不得小于4）
        
    
    1. 按照新的 `realeSize` 申请内存空间，创建 `dictht` ，并赋值给 `dict.ht[1]`
    
    1. 设置`dict.rehashidx = 0`，表示开始rehash
    
    1. 将`dict.ht[0]`中的每一个`dictEntry`都rehash到`dict.ht[1]`
    
    1. 将`dict.ht[1]`赋值给`dict.ht[0]`
    
    1. 再将`dict.ht[1]`初始化为空哈希表，释放原来的`dict.ht[0]`的内存
    
    1. 设置`dict.rehashidx = -1`，表示结束rehash
        
        ![[IMG-20260405035530650.gif|Untitled 2.gif]]
        
    
# 6. **Dict 的 渐进式 rehash**
1. 渐进式 rehash 解决的问题：试想一下，如果Dict中包含==数百万的 entry，要在一次rehash完成，极有可能导致主线程阻塞==
1. ==因此 Dict 的 渐进式 rehash 并====**不是一次性完成的，是分多次、渐进式的完成**==
1. 渐进式 rehash 的流程如下：
    
    1. 计算新hash表的 `realeSize`，值取决于当前要做的是扩容还是收缩：
        
        - 如果是扩容，则新size为：第一个大于等于`dict.ht[0].used + 1`的 2n
        
        - 如果是收缩，则新size为：第一个大于等于`dict.ht[0].used`的 2n （不得小于4）
        
    
    1. 按照新的 `realeSize` 申请内存空间，创建 `dictht` ，并赋值给 `dict.ht[1]`
    
    1. 设置`dict.rehashidx = 0`，表示开始rehash
    
    1. ~~将`dict.ht[0]`中的每一个`dictEntry`都rehash到`dict.ht[1]`~~
        
        > ⭐改为：每次执行新增、查询、修改、删除操作时，都检查一下dict.rehashidx是否大于-1
        > 
        > 1. 如果是，则表示需要 rehash
        > 
        > 1. 故将`dict.ht[0].table[rehashidx]`的`entry`链表rehash到`dict.ht[1]`，即每次只rehash一个`entry`
        > 
        > 1. 并且将`rehashidx++`
        > 
        > 直至多次执行新增、查询、修改、删除操作后，将`dict.ht[0]`的所有数据都rehash到`dict.ht[1]`
        
    
    1. 将`dict.ht[1]`赋值给`dict.ht[0]`
    
    1. 再将`dict.ht[1]`初始化为空哈希表，释放原来的`dict.ht[0]`的内存
    
    1. 设置`dict.rehashidx = -1`，表示结束rehash
    
1. **由于渐进式 rehash 不是一次性将数据做迁移，因此在rehash过程中的操作需要注意：**
    
    - 由于：要确保`dict.ht[0]`的数据只减不增，随着rehash最终为空
        
        所以：==新增操作==，直接写入`dict.ht[1]`
        
    
    - 由于：故会导致`dict.ht[0]`和`dict.ht[1]`中元素的并集才是当前所有元素
        
        所以：==查询、修改和删除== ，会在`dict.ht[0]`和`dict.ht[1]`中依次查找并执行