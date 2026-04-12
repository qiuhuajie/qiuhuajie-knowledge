- [[#1. CAS]]
    - [[#1.1 介绍]]
    - [[#1.2 CAS 使用示例]]
    - [[#1.3 CAS 存在的问题]]
- [[#2. UnSafe 类]]
- [[#3. atomic 包下的原子类]]
    - [[#3.1 AtomicInteger]]
        - [[#使用举例]]
        - [[#源码解析]]
    - [[#3.2 其他原子类]]
        - [[#a. 基本类型原子类]]
        - [[#b. 数组类型原子类]]
        - [[#c. 引用类型原子类]]
        - [[#d. 字段类原子类]]
        - [[#f. 原子累加器 LongAdder]]

> [!important]
> 
> - **原子类由 CAS + volatile 实现，一起保障了 JMM 中的原子性**
> 
> - **CAS 底层能力由 Unsafe 类提供**
# 1. CAS
## 1.1 介绍
1. CAS 的全称为 Compare-And-Swap，直译就是对比交换
    
    1. **JDK 中大量使用了 CAS ，来在**==**多线程并发**==**下，以**==**不加锁（synchronized 重量级锁）**==**的方式**==**原子地更新数据**==
    
    1. CAS 是**靠硬件实现**的
        
        1. **是一条 CPU 的原子指令**（`cmpxchg(void* ptr, int old, int new)`），其作用是让 CPU 先进行比较两个值（`ptr == old`）是否相等，然后原子地更新某个位置的值为 `new`
        
        1. JVM 只是封装了汇编调用，那些原子类，如 `AtomicInteger` 类便是使用了这些封装后的接口
        
    
1. **==CAS 更新操作的流程==**
    
    1. 它包含三个操作数：**内存位置值 V，旧的预期值 A，要修改的更新值 B**
    
    1. 执行 CAS 操作的时候，将内存位置值 V 与旧的预期值 A 比较：
        
        1. 如果相匹配，那么处理器会自动将内存位置值 V 更新为要修改的更新值 B
        
        1. 如果不匹配，处理器不做任何操作，进入自旋操作（`do-while` 重试）
        
        ![[Attachment/1question/大数据/Java 开发/JUC/锁/锁的核心类 AQS/IMG-20260405035413906.png|Untitled 474.png]]
        
    
  
1. **CAS 必须配合 `volatile` ，只有保证可见性，才能在 CAS 比较时拿到最新的值**
## 1.2 **CAS 使用示例**
1. `i++` 分为三步：取出，加一，放回，这样在多线程环境下自增操作存在并发安全问题
1. **如果不使用 CAS**，在高并发下，多线程同时修改一个变量的值我们需要 **`synchronized` 加重量级锁**（可能有人说可以用 Lock 加锁，Lock 底层的 AQS 也是基于 CAS 进行获取锁的）
    
    ```Java
    public class Test {
        private int i=0;
        public synchronized int add(){
            return i++;
        }
    }
    ```
    
1. Java 并发包中提供了 **AtomicInteger 原子类（底层基于 CAS 进行更新数据的）**，**==不需要加锁==**就在多线程并发场景下实现数据的一致性
    
    ```Java
    public class Test {
        private  AtomicInteger i = new AtomicInteger(0);
        public int add(){
            return i.addAndGet(1);
        }
    }
    ```
    
## 1.3 **CAS 存在的问题**

> [!important] CAS 方式为乐观锁，synchronized 为悲观锁。因此使用 CAS 解决并发问题通常情况下性能更优。但使用 CAS 方式也会有几个问题：
1. ==**ABA 问题**== 🙋‍♂️
    
    1. 因为 CAS 需要在操作值的时候，检查值有没有发生变化，比如没有发生变化则更新，但是**如果一个值原来是 A，变成了 B，又变成了 A**，那么使用CAS进行检查时则会发现它的值没有发生变化，但是实际上却变化了
    
    1. 解决方法：
        
        1. ABA 问题的**解决思路就是使用版本号**。在变量前面追加上版本号，每次变量更新的时候把版本号加1，**那么 A->B->A 就会变成 1A->2B->3A**
        
        1. 从Java 1.5开始，**JDK 的 Atomic 包里提供了一个引用类型的原子类** `**AtomicStampedReference**` **来解决 ABA 问题**
        
        1. 这个类的 `compareAndSet()` 方法的作用是
            
            1. 首先检查当前引用是否等于预期引用，**并且检查当前标志是否等于预期标志**
            
            1. 如果全部相等，则以原子方式将该引用和该标志的值设置为给定的更新值
            
        
    
1. ==**重试存在开销**==
    
    1. 如果 CAS 失败，会一直进行尝试
    
    1. 自旋 CAS 如果长时间不成功，会给 CPU 带来非常大的执行开销
    
1. ==**只能保证一个共享变量的原子操作**==
    
    1. 当对一个共享变量执行操作时，我们可以使用循环 CAS 的方式来保证原子操作，但是**对多个共享变量操作时，循环 CAS 就无法保证操作的原子性，这个时候就可以用锁**
    
    1. 解决方法：
        
        1. 从 Java 1.5 开始，**JDK 的 Atomic 包里提供了一个引用类型的原子类** `**AtomicReference**` **类来保证引用对象之间的原子性，就可以把多个变量放在一个对象里来进行 CAS 操作**
        
        1. 还有一个取巧的办法，就是把多个共享变量合并成一个共享变量来操作。比如，有两个共享变量i = 2，j = a，合并一下ij = 2a，然后用CAS来操作ij
        
    
# 2. **UnSafe 类**
1. Unsafe 是位于 sun.misc 包下的一个类
1. Unsafe 作用
    
    1. **主要==提供一些用于执行低级别、不安全操作的方法==**
    
    1. **Unsafe 提供的 API 大致可分为：内存操作、CAS、Class 相关、对象操作、线程调度、系统信息获取、内存屏障、数组操作等几类**
    
    1. 这些方法**可以==提升 Java 运行效率、增强 Java 语言操作底层资源的能力==**
    
    1. 例如：⭐**Unsafe 类源码中提供了三种 CAS 方法，都是** `native` **方法**
        
        ![[IMG-20260404031748614.png|Untitled 1 345.png]]
        
    
1. **Unsafe 使用有安全风险**
    
    1. 但由于 Unsafe 类使 Java 语言拥有了类似 C 语言指针一样操作内存空间的能力，这无疑也增加了程序发生相关指针问题的风险
    
    1. 在程序中过度、不正确使用 Unsafe 类会使得程序出错的概率变大，使得 Java 这种安全的语言变得不再“安全”，因此对 Unsafe 的使用一定要慎重
    
    1. 对于 Unsafe 类的使用都是受限制的，只有授信的代码才能获得该类的实例，当然 JDK 库里面的类是可以随意使用的
    
# 3. atomic 包下的原子类
## 3.1 **AtomicInteger**
### **使用举例**
1. 以 AtomicInteger 为例，常用 API：
    
    ```Java
    public final int get()：获取当前的值
    public final int getAndSet(int newValue)：获取当前的值，并设置新的值
    public final int getAndIncrement()：获取当前的值，并自增
    public final int getAndDecrement()：获取当前的值，并自减
    public final int getAndAdd(int delta)：获取当前的值，并加上预期的值
    void lazySet(int newValue): 最终会设置成newValue,使用lazySet设置值后，可能导致其他线程在之后的一小段时间内还是可以读到旧的值。
    ```
    
1. 相比 Integer 的优势
    
    1. 多线程中让变量自增：
        
        ```Java
        private volatile int count = 0;
        // 若要线程安全执行执行 count++，需要加锁
        public synchronized void increment() {
            count++;
        }
        public int getCount() {
            return count;
        }
        ```
        
    
    1. 使用 AtomicInteger 后：
        
        ```Java
        private AtomicInteger count = new AtomicInteger();
        public void increment() {
            count.incrementAndGet();
        }
        // ⭐使用 AtomicInteger 后，不需要加锁，也可以实现线程安全
        public int getCount() {
            return count.get();
        }
        ```
        
    
### 源码解析
1. ==**AtomicInteger 底层用的是**== `**volatile**` ==**的变量和 CAS 来进行更改数据的**==
    
    - `volatile` 保证线程的可见性，多线程并发时，一个线程修改数据，可以保证其它线程立马看到修改后的值
    
    - CAS 保证数据更新的原子性
    
    ```Java
    public class AtomicInteger extends Number implements java.io.Serializable {
        private static final Unsafe unsafe = Unsafe.getUnsafe();
        private static final long valueOffset;
        static {
            try {
                //用于获取value字段相对当前对象的“起始地址”的偏移量
                valueOffset = unsafe.objectFieldOffset(AtomicInteger.class.getDeclaredField("value"));
            } catch (Exception ex) { throw new Error(ex); }
        }
    
        private volatile int value;  // volatile 保证值的可见性
    
        //返回当前值
        public final int get() {
            return value;
        }
    
        //递增加detla
        public final int getAndAdd(int delta) {
            //三个参数，1、当前的实例 2、value实例变量的偏移量 3、当前value要加上的数(value+delta)。
            return unsafe.getAndAddInt(this, valueOffset, delta);
        }
    
        //递增加1
        public final int incrementAndGet() {
            return unsafe.getAndAddInt(this, valueOffset, 1) + 1;
        }
    ...
    }
    ```
    
1. 以**递增方法 `incrementAndGet()`** 为例，调用 Unsafe 类的 **`getAndAddInt()`** 方法
    
    ![[IMG-20260405035420316.png|Untitled 2 282.png]]
    
1. Unsafe 类的 `getAndAddInt()` 方法中**使用 `do-while` 实现自旋**，如果修改数值失败则通过循环来执行自旋，直至修改成功
1. **而修改更新数据的操作使用的就是 CAS，可以看到调用了 Unsafe 类提供的三个 CAS 方法之一的 `compareAndSwapInt()`**
## 3.2 其他原子类

> [!important] JDK 中提供了 12 个原子操作类
### a. **基本类型原子类**
1. 使用原子的方式更新基本类型，Atomic 包提供了以下 3 个类
    
    - `AtomicBoolean`：原子更新布尔类型
    
    - `AtomicInteger`：原子更新整型
    
    - `AtomicLong`：原子更新长整型
    
1. 以上 3 个类提供的方法几乎一模一样，可以参考上面 AtomicInteger 中的相关方法
### b. 数组类型原子类
1. 通过原子的方式更新数组里的某个元素，Atomic 包提供了以下的 3 个类
    
    - `AtomicIntegerArray`：原子更新整型数组里的元素
    
    - `AtomicLongArray`：原子更新长整型数组里的元素
    
    - `AtomicReferenceArray`：原子更新引用类型数组里的元素
    
1. 这三个类的最常用的方法是如下两个方法：
    
    - `get(int index)`：获取索引为 index 的元素值。
    
    - `compareAndSet(int i,E expect,E update)`：如果当前值等于预期值，则以原子方式将数组位置 i 的元素设置为 update 值
    
1. 举个 AtomicIntegerArray 例子：
    
    ```Java
    import java.util.concurrent.atomic.AtomicIntegerArray;
    
    public class Demo {
        public static void main(String[] args) throws InterruptedException {
    
            AtomicIntegerArray array = new AtomicIntegerArray(new int[] { 0, 0 });
            System.out.println(array);
    
            System.out.println(array.getAndAdd(1, 2));
            System.out.println(array);
    
            System.out.println(array.compareAndSet(1, 2, 3));
            System.out.println(array);
        }
    }
    // 输出结果
    [0, 0]
    0
    [0, 2]
    true
    [0, 3]
    ```
    
### c. 引用类型原子类
1. Atomic 包提供了以下三个类：
    
    - `AtomicReference`：原子更新引用类型**（可以解决 多个共享变量的原子操作问题）**
    
    - `AtomicStampedReference`：原子更新引用类型，内部使用 Pair 来存储元素值及其版本号**（可以解决 ABA 问题）**
    
    - `AtomicMarkableReferce`：原子更新带有标记位的引用类型（简化了 `AtomicStampedReference`，只用一个 boolean 值来标记是否有人修改过）
    
1. 这三个类提供的方法都差不多
    
    1. 首先构造一个引用对象，然后把引用对象 set 进 Atomic 类，然后调用 compareAndSet 等一些方法去进行原子操作，原理都是基于 Unsafe 实现
    
    1. 但 AtomicReferenceFieldUpdater 略有不同，更新的字段必须用 volatile 修饰
    
1. AtomicReference 代码示例：
    
    ```Java
    class Person {
        volatile long id;
    
        public Person(long id) {
            this.id = id;
        }
    
        public String toString() {
            return "id:"+id;
        }
    }
    
    public class Demo {
        public static void main(String[] args) throws InterruptedException {
    
            // 创建两个Person对象，它们的id分别是101和102
            Person p1 = new Person(101);
            Person p2 = new Person(102);
    
            // 新建AtomicReference对象，初始化它的值为p1对象
            AtomicReference ar = new AtomicReference(p1);
    
            // 通过 CAS 设置 ar，如果 ar 的值为 p1 的话，则将其设置为 p2
            ar.compareAndSet(p1, p2);
    
            Person p3 = (Person)ar.get();
            System.out.println("p3 is " + p3);
            System.out.println("p3.equals(p1) = " + p3.equals(p1));
    
        }
    }
    // 输出结果
    p3 is id:102
    p3.equals(p1) = false
    ```
    
1. ==⭐====**AtomicStampedReference 解决 CAS 的 ABA 问题**==
    
    1. AtomicStampedReference 主要维护包含一个对象引用以及一个可以自动更新的整数 "stamp" 的 pair 对象来解决 ABA 问题
        
        ```Java
        public class AtomicStampedReference<V> {
            private static class Pair<T> {
                final T reference;  //维护对象引用
                final int stamp;  //用于标志版本
                private Pair(T reference, int stamp) {
                    this.reference = reference;
                    this.stamp = stamp;
                }
                static <T> Pair<T> of(T reference, int stamp) {
                    return new Pair<T>(reference, stamp);
                }
            }
            private volatile Pair<V> pair;
            ....
            
            /**
              * expectedReference ：更新之前的原始值
              * newReference : 将要更新的新值
              * expectedStamp : 期待更新的标志版本
              * newStamp : 将要更新的标志版本
              */
            public boolean compareAndSet(V   expectedReference,
                                     V   newReference,
                                     int expectedStamp,
                                     int newStamp) {
                // 获取当前的(元素值，版本号)对
                Pair<V> current = pair;
                return
                    // 引用没变
                    expectedReference == current.reference &&
                    // 版本号没变
                    expectedStamp == current.stamp &&
                    // 新引用等于旧引用
                    ((newReference == current.reference &&
                    // 新版本号等于旧版本号
                    newStamp == current.stamp) ||
                    // 构造新的Pair对象并 CAS 更新
                    casPair(current, Pair.of(newReference, newStamp)));
            }
        
            private boolean casPair(Pair<V> cmp, Pair<V> val) {
                // 调用Unsafe的compareAndSwapObject()方法CAS更新pair的引用为新引用
                return UNSAFE.compareAndSwapObject(this, pairOffset, cmp, val);
            }
        ```
        
        - 可以看到，AtomicStampedReference 中解决 ABA 问题就是使用的版本号法
            
            - 首先，使用版本号控制
            
            - 其次，不重复使用节点（Pair）的引用，每次都新建一个新的 Pair 来作为 CAS 比较的对象，而不是复用旧的
            
            - 最后，外部传入元素值及版本号，而不是节点(Pair)的引用
            
        
    
    1. **AtomicStampedReference** 使用示例：
        
        ```Java
        public class AtomicTester {
            private static AtomicStampedReference<Integer> atomicStampedRef = new AtomicStampedReference<>(1, 0);
        
            public static void main(String[] args){
                first().start();
                second().start();
            }
        
            private static Thread first() {
                return new Thread(() -> {
                    //获取当前标识别
                    int stamp = atomicStampedRef.getStamp();
        
                    System.out.println(Thread.currentThread().getName() + "：初始值 a = " + atomicStampedRef.getReference() + "，版本号 = " + stamp);
        
                    //等待1秒 ，以便让干扰线程执行
                    try { Thread.sleep(1000); } catch (InterruptedException e) { e.printStackTrace(); }
        
                    //此时 expectedReference 未发生改变，但是 stamp 已经被修改了,所以 CAS 失败
                    int newStamp = stamp + 1;
                    boolean isCASSuccess = atomicStampedRef.compareAndSet(1, 2, stamp, newStamp);
                    System.out.println(Thread.currentThread().getName() +"：使用期望的版本号 " + newStamp + " 进行 CAS 操作的结果: " + isCASSuccess);
        
                },"主操作线程");
            }
        
            private static Thread second() {
                return new Thread(() -> {
                    // 确保 thread-first 优先执行
                    Thread.yield(); 
                    
                    int stamp = atomicStampedRef.getStamp();
                    atomicStampedRef.compareAndSet(1, 2, stamp, stamp + 1);
                    System.out.println(Thread.currentThread().getName() +"：修改值为：" + atomicStampedRef.getReference() + "，版本号 = " + stamp);
                    System.out.println(Thread.currentThread().getName() +"：修改后的版本号 = " + atomicStampedRef.getStamp());
        
                },"干扰线程");
            }
        }
        ```
        
        运行结果
        
        ```Java
        主操作线程：初始值 a = 1，版本号 = 0
        干扰线程：修改值为：2，版本号 = 0
        干扰线程：修改后的版本号 = 1
        主操作线程：使用期望的版本号 1 进行 CAS 操作的结果: false
        ```
        
    
### d. 字段类原子类
1. ==**以线程安全的方式操作非线程安全对象内的某些字段**==
1. Atomic 包提供了四个类进行原子字段更新：
    
    - `AtomicIntegerFieldUpdater`：原子更新整型的字段的更新器
    
    - `AtomicLongFieldUpdater`：原子更新长整型字段的更新器
    
    - `AtomicReferenceFieldUpdater`：上面已经说过此处不在赘述
    
1. 这四个类的使用方式都差不多，是基于反射的原子更新字段的值。要想原子地更新字段类需要两步：
    
    - 第一步，因为原子更新字段类都是抽象类，**每次使用的时候必须使用静态方法 `newUpdater()` 创建一个更新器，并且需要设置想要更新的类和属性**
    
    - 第二步，**更新类的字段必须使用 `public` 、`volatile` 修饰**
    
1. AtomicIntegerFieldUpdater 代码示例：
    
    ```Java
    public class TestAtomicIntegerFieldUpdater {
        public static void main(String[] args){
            TestAtomicIntegerFieldUpdater tIA = new TestAtomicIntegerFieldUpdater();
            tIA.doIt();
        }
    
        public AtomicIntegerFieldUpdater<DataDemo> updater(String name){
            // 创建一个更新器（传入想要更新的 类名 和 属性名）
            return AtomicIntegerFieldUpdater.newUpdater(DataDemo.class, name);
        }
    
        public void doIt(){
            DataDemo data = new DataDemo();
            System.out.println("publicVar = " + updater("publicVar").getAndAdd(data, 2));  // publicVar = 3
            System.out.println("publicVar = " + updater("publicVar").get(data));           // publicVar = 5		
        }
    
    }
    
    class DataDemo{
        public volatile int publicVar = 3;
        
        protected volatile int protectedVar=4; // 在 TestAtomicIntegerFieldUpdater 中不能访问
        
        private volatile  int privateVar=5;    // 在 TestAtomicIntegerFieldUpdater 中不能访问
    
        public volatile static int staticVar = 10; // 在 TestAtomicIntegerFieldUpdater 中不能访问，报 java.lang.IllegalArgumentException
    
        public volatile Integer integerVar = 19; // 在 TestAtomicIntegerFieldUpdater 中不能访问，报 must be integer
    }
    ```
    
### f. 原子累加器 LongAdder
1. 相比直接使用**基本类型原子类提供的** `incrementAndGet` 方法更高效
1. 性能提升的原因很简单
    
    1. 就是在有竞争时，**设置多个累加单元**，Therad-0 累加 Cell[0]，而 Thread-1 累加 Cell[1]
    
    1. 最后将结果汇总
    
    1. 这样它们在**累加时操作的不同的 Cell 变量，因此减少了 CAS 重试失败，从而提高性能**