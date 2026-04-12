- [[#1. 简介]]
- [[#2. IntSet 的自动升级]]
- [[#3. IntSet 特性总结]]
- [[#4. IntSet 源码]]
# 1. **简介**
1. IntSet是Redis中 set 集合的一种实现方式，**基于整数数组来实现**，并且具备长度可变、有序等特征
1. 源码中定义的结构体如下：
    
    ![[IMG-20260404031936432.png|Untitled 577.png]]
    
1. 其中的encoding包含三种模式，表示存储的整数大小不同：
    
    ![[IMG-20260404031936467.png|Untitled 1 429.png]]
    
1. 为了方便查找，Redis会将 intset 中所有的整数**按照升序**依次保存在`contents`数组中，结构如图：
    
    ![[IMG-20260404031936575.png|Untitled 2 350.png]]
    
    现在，数组中每个数字都在int16_t的范围内，因此采用的编码方式是INTSET_ENC_INT16，每部分占用的字节大小为：
    
    - `encoding`：4字节
    
    - `length`：4字节
    
    - `contents`：2字节 * 3 = 6字节
    
# 2. **IntSet 的自动升级**
如果此时要插入一个新的数字：`50000`，这个数字超出了int16_t的范围，intset会自动 **升级** 编码方式到合适的大小
1. 插入前的元素为`{5,10，20}`，采用的编码是`INTSET_ENC_INT16`，则每个整数占2字节：
    
    ![[IMG-20260404031936602.png|Untitled 3 265.png]]
    
1. 升级编码为`INTSET_ENC_INT32`，每个整数占4字节，并按照新的编码方式及元素个数扩容数组，因此**倒序依次将数组中的元素拷贝到扩容后的正确位置**
    
    ![[IMG-20260404031936675.png|Untitled 4 204.png]]
    
1. 再将待添加的元素放入数组末尾（既然触发了升级，那么要插入的新元素一定是当前元素中最大的，故插在末尾）
    
    ![[IMG-20260404031936747.png|Untitled 5 166.png]]
    
1. 最后，将inset的`encoding`属性改为`INTSET_ENC_INT32`，将`length`属性改为4
    
    ![[IMG-20260404031936819.png|Untitled 6 135.png]]
    
# 3. **IntSet 特性总结**
**IntSet 可以看做是特殊的整数数组，具备一些特点：**
1. Redis会确保Intset中的==元素唯一、有序==
1. 具备类型==自动升级==机制，可以节省内存空间
1. 底层采用==二分查找方式来查询==
1. 可以在数据量不多的时候使用
# 4. **IntSet 源码**
1. intsetAdd
    
    ```C
     intset *intsetAdd(intset *is, int64_t value, uint8_t *success) {
         uint8_t valenc = _intsetValueEncoding(value);// 获取当前值编码
         uint32_t pos; // 要插入的位置
         if (success) *success = 1;
         // ⭐判断编码是不是超过了当前intset的编码
         if (valenc > intrev32ifbe(is->encoding)) {
             // 超出编码，需要升级
             return intsetUpgradeAndAdd(is,value);
         } else {
             // 在当前intset中查找值与value一样的元素的角标pos
             if (intsetSearch(is,value,&pos)) {
                 if (success) *success = 0; //如果找到了，则无需插入，直接结束并返回失败
                 return is;
             }
             // 数组扩容
             is = intsetResize(is,intrev32ifbe(is->length)+1);
             // 移动数组中pos之后的元素到pos+1，给新元素腾出空间
             if (pos < intrev32ifbe(is->length)) intsetMoveTail(is,pos,pos+1);
         }
         // 插入新元素
         _intsetSet(is,pos,value);
         // 重置元素长度
         is->length = intrev32ifbe(intrev32ifbe(is->length)+1);
         return is;
     }
     
    ```
    
1. intsetUpgradeAndAdd
    
    ```C
     static intset *intsetUpgradeAndAdd(intset *is, int64_t value) {
         // 获取当前intset编码
         uint8_t curenc = intrev32ifbe(is->encoding);
         // 获取新编码
         uint8_t newenc = _intsetValueEncoding(value);
         // 获取元素个数
         int length = intrev32ifbe(is->length);
         // ⭐判断新元素是大于0还是小于0 ，小于0插入队首、大于0插入队尾
         int prepend = value < 0 ? 1 : 0;
         // 重置编码为新编码
         is->encoding = intrev32ifbe(newenc);
         // 重置数组大小
         is = intsetResize(is,intrev32ifbe(is->length)+1);
         // 倒序遍历，逐个搬运元素到新的位置，_intsetGetEncoded按照旧编码方式查找旧元素
         while(length--) // _intsetSet按照新编码方式插入新元素
             _intsetSet(is,length+prepend,_intsetGetEncoded(is,length,curenc));
         /* 插入新元素，prepend决定是队首还是队尾*/
         if (prepend)
             _intsetSet(is,0,value);
         else
             _intsetSet(is,intrev32ifbe(is->length),value);
         // 修改数组长度
         is->length = intrev32ifbe(intrev32ifbe(is->length)+1);
         return is;
     }
    ```