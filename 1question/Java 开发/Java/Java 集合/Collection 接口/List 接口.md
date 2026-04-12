- [[#1. List 接口介绍]]
- [[#2. ArrayList 和 LinkedList 的区别]]
- [[#3. ArrayList 的扩容机制]]
    - [[#速记版⭐️]]
    - [[#3.1 ArrayList 简介]]
    - [[#3.2 几个私有属性]]
    - [[#3.3 三个构造方法]]
    - [[#3.4 add(E e)方法]]
    - [[#3.5 ensureCapacityInternal() 方法]]
    - [[#3.6 ensureExplicitCapacity() 方法]]
    - [[#3.7 grow() 方法]]
    - [[#3.8 hugeCapacity() 方法]]
- [[#4. 笔试题]]
# 1. List 接口介绍
List 接口有三个实现类：
1. ==**ArrayList**====：==
    
    - 是 List 的主要实现类
    
    - 底层：`Object[]` 数组
    
    - 适用于频繁的查找工作，效率高
    
    - 线程不安全的（如果需要是线程安全的，则使 `collections`工具类中的 `synchronized(List<T> list)` 来实现线程安全）
    
    - 只要用到数组都可以使用 ArrayList
    
1. ==**LinkedList**====：==
    
    - 对于频繁的插入和删除操作，使用此类效率更高
    
    - 底层：双向链表
    
    - 线程不安全的
    
1. ==**Vector**====：==
    
    - 底层：`Object[]` 数组
    
    - List 的古老实现类
    
    - 线程安全的，效率低
    
![[IMG-20260405035413937.png|Untitled 451.png]]
# 2. ArrayList 和 LinkedList 的区别
- ==**是否保证线程安全**==**：** `ArrayList` 和 `LinkedList` 都是不同步的，也就是不保证线程安全
- ==**底层数据结构**==**：**
    
    - `ArrayList` 底层使用的是 `Object` 数组
    
    - `LinkedList` 底层使用的是 双向链表 数据结构（JDK1.6 之前为循环链表，JDK1.7 取消了循环）
    
- ==**插入和删除是否受元素位置的影响：**==
    
    - `ArrayList` 采用数组存储
        
        - 插入和删除元素的时间复杂度受元素位置的影响，比如：执行`add(E e)`方法的时候， `ArrayList` 会默认在将指定的元素追加到此列表的末尾，这种情况时间复杂度就是 $O(1)$
        
        - 但是如果要在指定位置 i 插入和删除元素的话（`add(int index, E element)`）时间复杂度就为 $O(n-i)$。因为在进行上述操作的时候集合中第 i 和第 i 个元素之后的(n-i)个元素都要执行向后位/向前移一位的操作
        
    
    - `LinkedList` 采用链表存储
        
        - 如果是在头尾插入或者删除元素不受元素位置的影响，`add(E e)`、`addFirst(E e)`、`addLast(E e)`、`removeFirst()` 、 `removeLast()`，时间复杂度为 $O(1)$
        
        - 如果是要在指定位置 `i` 插入和删除元素的话（`add(int index, E element)`，`remove(Object o)`）， 时间复杂度为 $O(n)$ ，因为需要先移动到指定位置再插入
        
    
- ==**内存空间占用：**==
    
    - `ArrayList` 的空 间浪费主要体现在在 list 列表的结尾会预留一定的容量空间
    
    - `LinkedList` 的空间花费则体现在它的每一个元素都需要消耗比 `ArrayList` 更多的空间（因为要存放直接后继和直接前驱以及数据）
    
- ==**是否支持快速随机访问：**==
    
    - `LinkedList` 不支持高效的随机元素访问
    
    - `ArrayList`（实现了RandomAccess接口）支持。快速随机访问就是通过元素的序号快速获取元素对象(对应于`get(int index)`方法
        
        > [!important] **`RandomAccess` 接口**
        > 
        > 1. 接口中什么都没有定义。所以 `RandomAccess`接口只是一个标识，标识实现这个接口的类具有随机访问功能
        >     
        >     ![[IMG-20260404031804192.png|Untitled 1 331.png]]
        >     
        > 
        > 1. 在 `binarySearch()` 方法中，它要判断传入的 list 是否是 `RandomAccess` 的实例，如果是，调用 `indexedBinarySearch()` 方法，如果不是，那么调用 `iteratorBinarySearch()` 方法
        >     
        >     ![[IMG-20260405035420344.png|Untitled 2 270.png]]
        >     
        
    
# 3. ArrayList 的扩容机制
## 速记版⭐️
1. 以无参数构造方法创建 `ArrayList` 时，实际上初始化赋值的是一个**空数组**
1. 当真正对数组进行添加元素操作时，才真正分配容量。即**向数组中添加第一个元素时，数组容量扩为 10**
1. **`add()`** 时，根据传入的最低容量需求 `minCapacity`，**判断是否需要扩容**
    
    1. 如果需要扩容，**调用 `grow()` 方法扩容**
    
    1. 每次扩容之后容量都会**变为原来的 1.5 倍左右**
    
    1. 在 `grow()` 方法中，确定 ArrayList 扩容后的新存储能力后，调用的 **`Arrays.copyOf()` 方法进行对新数组的赋值**
    
## 3.1 ArrayList 简介
1. `ArrayList` 的底层是数组队列，相当于动态数组
    
    1. 与 Java 中的数组相比，它的容量能动态增长
    
    1. 在添加大量元素前，应用程序可以使用`ensureCapacity`操作来增加 `ArrayList` 实例的容量。这可以减少递增式再分配的数量
    
1. `ArrayList` 继承于 `**AbstractList**` ，实现了 `**List**`, `**RandomAccess**`, `**Cloneable**`, `**java.io.Serializable**` 这些接口。
    
    ```Java
    public class ArrayList<E> extends AbstractList<E> implements List<E>, RandomAccess, Cloneable, java.io.Serializable{
    }
    ```
    
    - `RandomAccess` 是一个标志接口，表明实现这个接口的 List 集合是支持**快速随机访问**的。在 `ArrayList` 中，我们即可以通过元素的序号快速获取元素对象，这就是快速随机访问
    
    - `ArrayList` 实现了 `**Cloneable**` **接口** ，即覆盖了函数`clone()`，能被克隆
    
    - `ArrayList` 实现了 `java.io.Serializable`接口，这意味着`ArrayList`**支持序列化**，能通过序列化去传输
    
## 3.2 几个私有属性
```Java
// 默认初始容量是10
private static final int DEFAULT_CAPACITY = 10;
// 如果容量为0时候，就返回这个数组
private static final Object[] EMPTY_ELEMENTDATA = {};
// 使用默认容量为10的时候，返回这个数组
private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};
// 元素存放的数组
transient Object[] elementData;
// 元素的个数
private int size;
```
## 3.3 **三个构造方法**
1. 如果**不传入初始容量**
    
    - 就使用默认容量，并设置 `elementData` 为 `DEFAULTCAPACITY_EMPTY_ELEMENTDATA`
    
    - ⭐**以无参数构造方法创建 `ArrayList` 时，==实际上初始化赋值的是一个空数组==**
    
    - **当真正对数组进行添加元素操作时，才真正分配容量。即向==数组中添加第一个元素时，数组容量扩为 10==**
        
        ![[IMG-20260405035422063.png|Untitled 3 202.png]]
        
    
1. 如果**传入初始容量**
    
    - 会判断这个传入的值，如果大于 `0`，就 new 一个新的 object 数组
    
    - 如果等于 `0`，就直接设置 `elementData` 为 `EMPTY_ELEMENTDATA`
        
        ![[IMG-20260405035433729.png|Untitled 4 157.png]]
        
    
1. 如果**传入一个Collection**
    
    - 则会调用 `toArray()` 方法把它变成一个数组
    
    - 同样会判断它的长度是否为 `0`，如果为 `0`，设置 `elementData` 为 `EMPTY_ELEMENTDATA`，否则将数组赋值给 `elementData`
        
        ![[IMG-20260405035445362.png|Untitled 5 128.png]]
        
    
## 3.4 `add(E e)`方法
1. 每次在 `add()` 一个元素时，都需要通过 `ensureCapacityInternal(size + 1)` 方法**确保当前 Arraylist 维护的数组**==**具有存储新元素的能力**==
1. 经过处理后将元素存储在 `elementData` 的尾部
    
    ```Java
    public boolean add(E e) {
         //判断是否可以容納 e，若能，则直接添加在末尾，若不能，则进行扩容，然后再把e添加在末尾
         ensureCapacityInternal(size + 1);  // Increments modCount!!
    
         //把e添加到数组末尾
         elementData[size++] = e;
         return true;
     }
    ```
    
## 3.5 `ensureCapacityInternal()` 方法
1. 确保内部容量具有存储新元素的能力
1. ==**判断传入的 最低容量需求**== ==**`minCapacity`**== ==**，与默认容量**== ==**`DEFAULTCAPACITY_EMPTY_ELEMENTDATA`**== ==**的大小**==**（通过取最大值来实现）**
    
    - 如果小于，则将最低容量需求 `minCapacity` 赋值为 **`10`**
    
    - 如果大于，则对最低容量需求 `minCapacity` 不做任何处理
    
    - 验证了上面：**当真正对数组进行添加元素操作时，才真正分配容量。即向==数组中添加第一个元素时，数组容量扩为==** `**==10==**`
    
1. 然后调用 **`ensureExplicitCapacity()`** 方法，来**判断**==**为了满足这个最低容量需求**== ==**`minCapacity`**== ==**的存储能力，是否需要扩容**==
    
    ```Java
    private void ensureCapacityInternal(int minCapacity) {
         ensureExplicitCapacity(calculateCapacity(elementData, minCapacity));
     }
     
     private static int calculateCapacity(Object[] elementData, int minCapacity) {
         if (elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
             return Math.max(DEFAULT_CAPACITY, minCapacity);
         }
         return minCapacity;
     }
    ```
    
## 3.6 `ensureExplicitCapacity()` 方法
1. 判断是否需要扩容
1. 判断 ==**最低容量需求**== `**minCapacity**` **与 当前 ArrayList** ==**已有的存储能力**== **`elementData.length` 的大小**
    
    1. 如果小于，表示 ArrayList 已有的存储能力满足最低容量需求，则无需扩容
    
    1. 如过大于，表示 ArrayList 的存储能力**不足**，因此需要==**调用**== ==**`grow()`**== ==**方法扩容**==
    
```Java
private void ensureExplicitCapacity(int minCapacity) {
     modCount++;
 
     // overflow-conscious code
     if (minCapacity - elementData.length > 0)
         grow(minCapacity);
 }
```
## 3.7 `grow()` 方法
1. 如何扩容
    
    1. ⭐**`int newCapacity = oldCapacity + (oldCapacity >> 1);`**：**==ArrayList 每次扩容之后容量都会变为原来的 1.5 倍左右==**（oldCapacity 为偶数就是 1.5 倍，奇数会丢掉小数，是 1.5 倍左右）
    
    1. ==**在**== ==**`grow()`**== ==**方法中，确定 ArrayList 扩容后的新存储能力后，调用的**== ==**`Arrays.copyOf()`**== ==**方法进行对原数组的赋值**==
    
    ```Java
    //根据期望容量minCapacity计算实际需要扩容的容量
    private void grow(int minCapacity) {
    
        // overflow-conscious code //得到旧容量
        int oldCapacity = elementData.length;
    
        //设置新容量为旧容量的1.5倍【oldCapacity >> 1相当于oldCapacity除以2】,用位运算提高效率
        int newCapacity = oldCapacity + (oldCapacity >> 1);
    
        //如果新容量仍然小于期望容量，则取值为minCapacity【最低容量需求】
        //一般情况下，如果扩容1.5倍后就大于期望容量，就返回这个1.5倍旧容量的值，而如果小于期望容量，就返回期望容量
        //使用1.5倍这个数值而不是直接使用期望容量，是为了防止频繁扩容影响性能
        if (newCapacity - minCapacity < 0)
            newCapacity = minCapacity;
    
        //当新的容量大于MAX_ARRAY_SIZE，则取值为Integer.MAX_VALUE
        if (newCapacity - MAX_ARRAY_SIZE > 0)
            newCapacity = hugeCapacity(minCapacity);
    
        // minCapacity is usually close to size, so this is a win:
        elementData = Arrays.copyOf(elementData, newCapacity);
    }
    ```
    
1. **`Arrays.copyOf()` 通过调用 `System.arraycopy()` 方法（native修饰）进行复制，以达到扩容的目的**
1. `arraycopy()` 标识为 `native` 意味 JDK 本地库，不可避免地进行 IO 操作，如果频繁扩容，会降低 ArrayList 的使用性能
    
    ![[IMG-20260405035505211.png|Untitled 6 105.png]]
    
    1. 因此当我们确定添加元素的个数的时候，可以事先指定 ArrayList 的可存储元素的个数
    
    1. 这样当加入元素的时候，就可以避免自动扩容，从而提高性能
    
## 3.8 `hugeCapacity()` 方法
1. 从 `hugeCapacity()` 可以看出 **ArrayList 最大存储能力：存储的元素个数为**==**整形范围**==
1. 当ArrayList中的当前容量已经为 Integer.MAX_VALUE，仍向ArrayList中添加元素，抛出异常
    
    ```Java
    private static int hugeCapacity(int minCapacity) {
         if (minCapacity < 0) // overflow
             throw new OutOfMemoryError();
         return (minCapacity > MAX_ARRAY_SIZE) ?
             Integer.MAX_VALUE :
         MAX_ARRAY_SIZE;
     }
    ```
    
# 4. 笔试题
1. 机场购买机票， 客户输入： 出发地， 结束地， 上机时间， 给出最低价的机票
    
    ```Java
    public class Ticket{
        public String from;
        public String to;
        public String time;
        public double price;
    }
    
    public class TicketManager{
    
        private List<Ticket> tickets;
    
        public void Ticket search(String from, String to, String time){
            return null;
        }
    }
    ```
    
1. 实现 search 方法：