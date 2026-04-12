- [[#1. 算法介绍]]
- [[#2. 算法实现]]
# 1. 算法介绍
1. LRU 算法是一种缓存淘汰策略
1. LRU 的全称是 Least RecentlyUsed，也就是说我们认为最近使用过的数据应该是是[有用的]，很久都没用过的数据应该是无用的，内存满了就优先删那些很久没用过的数据
1. 举个简单的例子，手机都可以把软件放到后台运行
1. **📑146. LRU 缓存**🔥
    
    > [!info] 力扣（LeetCode）官网 - 全球极客挚爱的技术成长平台  
    > 备战技术面试？力扣提供海量技术面试资源，帮助你高效提升编程技能，轻松拿下世界 IT 名企 Dream Offer。  
    > [https://leetcode.cn/problems/lru-cache/solutions/259678/lruhuan-cun-ji-zhi-by-leetcode-solution/?envType=study-plan-v2&envId=top-100-liked](https://leetcode.cn/problems/lru-cache/solutions/259678/lruhuan-cun-ji-zhi-by-leetcode-solution/?envType=study-plan-v2&envId=top-100-liked)  
    
# 2. 算法实现
1. LRU 缓存机制可以通过==**哈希表 + 双向链表**==实现，**用一个哈希表和一个双向链表维护所有在缓存中的键值对**
    
    ![[IMG-20260405035400264.png|Untitled 101.png]]
    
    1. 双向链表按照被使用的顺序存储了这些键值对，靠近头部的键值对是最近使用的，而靠近尾部的键值对是最久未使用的
    
    1. 哈希表即为普通的哈希映射（HashMap），通过缓存数据的键映射到其在双向链表中的位置
    
    1. 这样以来，我们首先使用哈希表进行定位，找出缓存项在双向链表中的位置，随后将其移动到双向链表的头部
    
1. **可在 O(1) 的时间内完成** `**get**` **或者** `**put**` **操作。具体的方法如下：**
    
    1. 对于 `get` 操作，首先判断 key 是否存在：
        
        1. 如果 key 不存在，则返回 −1；
        
        1. 如果 key 存在，则 key 对应的节点是最近被使用的节点。通过哈希表定位到该节点在双向链表中的位置，并将其移动到双向链表的头部，最后返回该节点的值
        
    
    1. 对于 `put` 操作，首先判断 key 是否存在：
        
        1. 如果 key 不存在，使用 key 和 value 创建一个新的节点，在双向链表的头部添加该节点，并将 key 和该节点添加进哈希表中。然后判断双向链表的节点数是否超出容量，如果超出容量，则删除双向链表的尾部节点，并删除哈希表中对应的项
        
        1. 如果 key 存在，则与 get 操作类似，先通过哈希表定位，再将对应的节点的值更新为 value，并将该节点移到双向链表的头部
        
    
1. **原子能力方法：**
    
    1. 删除一个指定的双向链表节点：`removeNode`
    
    1. 将传入的节点添加在链头：`addToHead`
    
    1. 将一个指定的双向链表节点，移动到链头：`moveToHead`（可由上面两个方法实现，先删除再添加到链头）
    
1. 实现
    
    ```Java
    class LRUCache {
    		// 双向链表节点定义
        class DLinkedNode {
            int key;
            int val;
            DLinkedNode pre;
            DLinkedNode next;
            DLinkedNode (){};
            DLinkedNode (int key, int val) {
                this.key = key;
                this.val = val;
            }
        }
    		
    		// 缓存维护的变量：
        HashMap<Integer, DLinkedNode> map;
        int capacity;
        DLinkedNode head;
        DLinkedNode tail;
        int size;
    
    		// 初始化
        public LRUCache(int capacity) {
            this.capacity = capacity;
            map = new HashMap<>(capacity);
            head = new DLinkedNode();
            tail = new DLinkedNode();
            head.next = tail;
            tail.pre = head;
            size = 0;
        }
        
    		// get()
        public int get(int key) {
            if (map.containsKey(key)) {
                moveToHead(map.get(key));
                return map.get(key).val;
            } else {
                return -1;
            }
        }
        
    		// put()
        public void put(int key, int value) {
            if (map.containsKey(key)) {
                moveToHead(map.get(key));
                map.get(key).val = value;
            } else {
                DLinkedNode newNode = new DLinkedNode(key, value);
                map.put(key, newNode);
                addToHead(newNode);
                size++;
                if (size > capacity) {
                    DLinkedNode del = tail.pre;
                    removeNode(del);
                    map.remove(del.key);
                    size--;
                }
            }
        }
    
    		// 将传入的节点添加在链头
        public void addToHead(DLinkedNode newNode) {
            newNode.next = head.next;
            head.next.pre = newNode;
            head.next = newNode;
            newNode.pre = head;
        }
    
    		// 删除一个指定的双向链表节点
        public void removeNode(DLinkedNode delNode) {
            delNode.pre.next = delNode.next;
            delNode.next.pre = delNode.pre;
        }
    
    		// 将一个指定的双向链表节点，移动到链头
        public void moveToHead(DLinkedNode node) {
            removeNode(node);
            addToHead(node);
        }
    }
    ```