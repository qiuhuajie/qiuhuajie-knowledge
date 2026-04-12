- [[#1. CopyOnWriteArrayList]]
    - [[#1.1 介绍]]
    - [[#1.2 写操作]]
    - [[#1.3 读操作]]
    - [[#1.4 弱一致性]]
        - [[#get() 一致性]]
        - [[#迭代器一致性]]
- [[#2. CopyOnWriteArraySet]]
# 1. **CopyOnWriteArrayList**
## 1.1 介绍
- CopyOnWriteArrayList 实现了 List 接口，List 接口定义了对列表的基本操作
    
    - 同时实现了 RandomAccess 接口，表示可以随机访问(数组具有随机访问的特性)
    
    - 同时实现了 Cloneable 接口，表示可克隆
    
    - 同时也实现了 Serializable 接口，表示可被序列化
    
    ![[IMG-20260404031738653.png|Untitled 305.png]]
    
- **使用了 `ReentrantLock` 来保证写操作时的同步**
## 1.2 写操作
- ⭐**CopyOnWrite 体现在写操作上**
    
    - **首先会将旧数组拷贝一份，所有的写操作在新数组上进行**
    
    - **并发的读操作，依旧在旧的数组上进行**
    
- 但拷贝的操作会带来性能消耗，所以 CopyOnWriteArrayList **适用于读多写少的场景**
```Java
public boolean add(E e) {
    final ReentrantLock lock = this.lock;
    // 写操作要用锁来保障同步
    lock.lock();
    try {
        // 获取旧的数组
        Object[] elements = getArray();
        int len = elements.length;
        // 拷贝新的数组（这里是比较耗时的操作，但不会影响其他读操作的线程）
        Object[] newElements = Arrays.copyOf(elements, len + 1);
        // 添加新元素
        newElements[len] = e;
        // 替换旧的数组
        setArray(newElements);
        return true;
    } finally {
        lock.unlock();
    }
}
```
## 1.3 读操作
- **==读操作中完全不加锁，可以满足高并发读的场景==**
```Java
public void forEach(Consumer<? super E> action) {
    if (action == null) throw new NullPointerException();
    Object[] elements = getArray();
    int len = elements.length;
    for (int i = 0; i < len; ++i) {
        @SuppressWarnings("unchecked") E e = (E) elements[i];
        action.accept(e);
    }
}
```
## 1.4 弱一致性
1. **一致性**和**高并发**本身就是矛盾的，需要权衡
1. 要求强一致性就要加锁，这样又会降低并发性能
### get() 一致性
- 由于 CopyOnWrite 机制，读操作与写操作并发时，可能会出现读操作读不到写操作最新修改后的数据的情况
    
    ![[IMG-20260404031738681.png|Untitled 1 231.png]]
    
    ![[IMG-20260404031738735.png|Untitled 2 195.png]]
    
### 迭代器一致性
```Java
public class test {
    public static void main(String[] args) throws InterruptedException {
        CopyOnWriteArrayList<Integer> list = new CopyOnWriteArrayList<>();
        list.add(1);
        list.add(2);
        list.add(3);
        // 迭代器此时获取的是旧数组
        Iterator<Integer> iter = list.iterator();
        
        // 使用新线程将元素 1 删除，但是此时操作的是新数组
        new Thread(() -> {
            list.remove(0);
            System.out.println(list);
        }).start();
        
        Thread.sleep(1000);
        
        // 使用迭代器打印看到数据还是旧的
        while (iter.hasNext()) {
            System.out.println(iter.next());
        }
    }
}
```
运行结果
```Java
[2, 3]
1
2
3
```
# 2. **CopyOnWriteArraySet**
1. **CopyOnWriteArraySet 源码完全就是使用 CopyOnWriteArrayList 来实现的**
    
    ![[IMG-20260404031738795.png|Untitled 3 149.png]]
    
1. 读操作
    
    ![[IMG-20260404031738821.png|Untitled 4 122.png]]
    
1. 写操作：Set 要保证数据不重复，底层是调用的 CopyOnWriteArrayList 提供的 `addIfAbsent()` 方法
    
    ![[IMG-20260404031738860.png|Untitled 5 101.png]]