- [[#1. HashMap 存在的线程安全问题]]
- [[#2. ConcurrentHashMap]]
- [[#3. 为什么 ConcurrentHashMap 不允许插入 null 值]]
# 1. HashMap 存在的线程安全问题
1. 问题 1：==**数据覆盖问题**==
    
    1. 在两个线程并发 put 时，得到 hash 值最终映射到的位置后，都会判断这个位置上是否存在元素
    
    1. 可能出现两个线程都任务插入位置不存在元素，都生成链表挂上去，导致数据覆盖问题
    
1. 问题 2：由于 **JDK 1.7** 在插入新元素时是使用的头插法，这会使链表在 HashMap 扩容后反转，会产生==**死循环问题**==
    
    1. **死循环是因为并发操作 HashMap 扩容时导致的**
    
    1. 线程 T1 和线程 T2 要对 HashMap 进行扩容操作，此时 T1 和 T2 指向的是链表的头结点元素 A，而 T1 和 T2 的下一个节点，也就是 T1.next 和 T2.next 指向的是 B 节点
        
        ![[IMG-20260404031738392.png|Untitled 303.png]]
        
    
    1. 此时，线程 T2 时间片用完进入休眠状态，而线程 T1 开始执行扩容操作，一直到线程 T1 扩容完成后，线程 T2 才被唤醒
    
    1. 由于线程 T1 **扩容使用的是头插法，所以链表被反转了**，但线程 T2 对于发生的一切是不可知的，所以它的指向元素依然没变，此时，T2 指向的是 A 元素，T2.next 指向的节点是 B 元素
        
        ![[IMG-20260404031738415.png|Untitled 1 229.png]]
        
    
    1. 当线程 T1 执行完，而线程 T2 恢复执行时，A 节点和 B 节点就形成死循环了
        
        ![[IMG-20260404031738453.png|Untitled 2 193.png]]
        
    
# 2. **ConcurrentHashMap**
1. HashMap 存在的线程安全问题
1. 而之前的线程安全 Map 容器是 **HashTable**，但 Hashtable 效率低下，主要是因为其在 put()、get() 等操作中**用了** `**synchronized**` **关键字对整个 Hash 表进行加锁**，使得其效率低下
1. 所以出现了 ConcurrentHashMap，来解决并发安全问题
1. **JDK 1.7 中**
    
    1. ConcurrentHashMap 的底层结构：
        
        1. 使用的是数组加链表的形式实现的，而**数组分为大数组（存放 Segment）和小数组（存放 HashEntry）**
        
        1. Segment 的数量默认为 16，==大数组在初始化完成后，就不能再变了，且大数组不是懒加载，浪费空间==
        
        1. 每个 Segment 中的 HashEntry 对并不是固定分配的，而是根据哈希函数将键值对分散到不同的 Segment 中。因此是动态变化的
        
    
    1. 线程安全的实现：**分段锁**
        
        - ==在 Segment 上加 ReenrantLock 来实现线程安全==
        
        - 可以保证多线程同时访问 ConcurrentHashMap 时，同一时间只有一个线程能操作 Segment
        
        ![[IMG-20260405035421938.png|Untitled 3 148.png]]
        
    
1. **JDK 1.8 中**
    
    1. ConcurrentHashMap 的底层结构：
        
        1. 不允许有空的键或者空的值
        
        1. 数据结构和 HashMap 相同：Node 数组 + 链表 / 红黑树
        
    
    1. ⭐**线程安全的实现：**
        
        1. **put()：**
            
            1. 如果该链表尚未创建，只需要==使用== **==CAS==** ==进行链表初始化==
            
            1. 如果链表已经有了
                
                1. 则**==会用 synchronized 锁住链表头==**==（相比 1.7 锁的粒度降低了，相对分段锁发生加锁的频率更低了，在并发操作下性能有了提升）==
                    
                    ![[IMG-20260405035428804.png|Untitled 4 121.png]]
                    
                
                1. 锁住链头后，再进行后续 put 操作，尾插法
                
            
        
        1. **get()：**
            
            1. 无锁操作，使用 `volatile` 保证可见性
            
            1. ==如果当前线程 get 操作拿到的是 Forwarding（转递）Node，表明有其他线程对这个链表进行了扩容，此时当前线程会让 get 操作在新 table 进行搜索获取==
            
        
        1. **size()**
            
            1. 元素个数保存在 baseCount 中，==在 put() 中==**==使用 CAS 对 baseCount 值进行修改==**
            
            1. 并发时的个数变动保存在 CounterCell[] 数组中，最后将所有线程保存的 size 累加返回
            
        
        1. **table 初始化**🙋‍♂️**：**
            
            1. 懒惰初始化 table，在第一次使用时才会真正创建 table
            
            1. 在初始化过程中，**==使用 CAS 修改初始化标志位==**==，其他线程根据标志位判断当前是否有线程在做初始化操作==，进而保证了并发安全
            
        
        1. **扩容：**
            
            1. 扩容时以链表为单位进行，需要**==对链表进行 synchronized 加锁==**==，每扩容复制完一个链表，就会将原来旧表中的链表头换成 ForwardingNode==
            
            1. 同时，其它扩容竞争线程也会==帮助当前线程，对未扩容复制的链表进行扩容==
            
        
        1. **树化：**同 HashMap。同时，**==树化过程会用 synchronized 锁住链表头==**
        
    
    > [!important] **ConcurrentHashMap 中**
    > 
    > `**CAS**` **和** `**sychronize**` **分别在什么时候使用**
    
# 3. **为什么 ConcurrentHashMap 不允许插入 null 值**
1. HashMap 是==允许 key 或 value 插入 null 值的==
1. 而 ConcurrentHashMap 是==不能插入 null 值的==，程序在运行期间就会报空指针异常
    
    ![[IMG-20260405035428861.png|Untitled 5 100.png]]
    
1. 为什么❓
    
    1. 存在二义性
    
    1. ==HashMap 是不怕二义性问题的，因为 HashMap 的设计是给==**==单线程==**==使用的==
        
        1. 所以如果查询到了 null 值，可以通过 `hashMap.containsKey(key)` 的方法来区分这个 null 值到底是存入的 null，还是压根不存在的 null
        
        1. 这样二义性问题就得到了解决
        
    
    1. ==而 ConcurrentHashMap 使用的场景是==**==多线程==**
        
        1. 假设可以存入 null 值，如果开始时不存在 null 值
            
            1. 线程 A 调用了 `concurrentHashMap.containsKey(key)`，此时返回的 null 是不存在的 nul
            
            1. 但如果在返回结果之前线程B 调用 `put(key,null)`，此时返回的 null 就成了存入的 null
            
        
        1. 所以，==没办法判断某一个时刻 get() 返回的 null，到底是值为 null，还是压根就不存在的 null==
        
        1. 因此，ConcurrentHashMap 源码中直接杜绝 key 或 value 为 null 的歧义问题