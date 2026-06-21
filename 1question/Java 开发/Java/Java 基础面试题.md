---
title: "Java 基础面试题"
tags:
  - "内存地址"
  - "StringBuffer"
  - "StringBuilder"
  - "Java_基础"
  - "AbstractStringBuilder"
  - "泛型"
updated: 2026-04-16
---

# 一、Java 面向对象编程三大特性：封装、继承、多态
1. 封装
    1. 封装把一个对象的属性私有化
    2. 同时提供一些可以被外界访问的属性的方法
2. 继承
    1. 继承是使用已存在的类的定义作为基础建立新类的技术，新类的定义可以增加新的数据或新的功能，也可以用父类的功能，但不能选择性地继承父类
    2. 通过使用继承我们能够非常方便地复用以前的代码
3. 多态
    1. 所谓多态就是指程序中定义的引用变量所指向的具体类型和通过该引用变量发出的方法调用在编程时并不确定，而是在程序运行期间才确定
    2. 即一个引用变量到底会指向哪个类的实例对象，该引用变量发出的方法调用到底是哪个类中实现的方法，必须在由程序运行期间才能决定

# 二、Java 多态是如何实现的🙋‍♂️
1. **多态通常有两种实现方法：**
    1. 子类继承父类（extends）
    2. 类实现接口（implements）
2. 其核心之处就在于
    1. ==**对父类方法的不同改写**==或==**对接口方法的不同实现**==，**以取得在**==**运行时**==**不同的执行效果**
    2. 虚拟机会在执行程序时动态调用实际类的方法，它会通过一种名为**动态绑定机制**自动实现，这个过程对程序员来说是透明的
3. 举例
    1. 假设我们要创建一个ArrayList对象，声明时应该遵循一条法则：声明的总是父类类型或接口类型，创建的是实际类型

    ```Java
    List list =　newArrayList();
    ```

        而不是

```Java
ArrayList list =　newArrayList();
```
    2. 在定义方法参数时也通常总是应该优先使用父类类型或接口类型，例如某方法应该写成：

    ```Java
    public void doSomething(List list);
    ```

        而不是

```Java
public void doSomething(ArrayList list);
```
    3. 这样声明最大的好处在于结构的==**灵活性：**==
        1. 假如某一天我认为 ArrayList 的特性无法满足我的要求，我希望能够用 LinkedList 来代替它
        2. 那么只需要在对象创建的地方把 `new ArrayList()` 改为 `new LinkedList` 即可，其它代码一概不用改动

# 三、重写 与 重载
1. **重写（Override）**
    1. 是多态的具体表现，它允许子类重新定义父类中已有的方法，且子类中的**方法名**和**参数的类型及个数**都必须与父类保持一致，这就是方法重写
    2. 注意点：
        - 子类方法的**权限控制符**必须大于等于父类方法
            > 如果父类方法的权限控制符是 protected，那么子类的方法权限控制符只能是 protected 或 public
        - 子类方法的**返回类型**必须是父类方法返回类型或为其子类型
            > 如果父类方法返回的是 Number 类型，那么子类方法只能返回 Number 类型或 Number 类的子类 Long 类型，而不能返回 Number 类型的父类类型 Object
    3. 重写的异常抛出限制：
        1. 如果父类抛出的是运行时异常（RuntimeException、[ArithmeticException](https://so.csdn.net/so/search?q=ArithmeticException&spm=1001.2101.3001.7020)），Java编译器不会检查，没有任何限制
        2. 如果父类抛出的是非运行时异常（IOException、CharacterCodingException），重写的方法抛出的异常必须小于等于被重写方法抛出的异常
2. **重载（Overload）**
    1. 方法重载是指在同一个类中，定义了多个同名方法，但**同名方法的参数类型或参数个数不同**就是方法重载
    2. 存在于同一个类中，指一个方法与已经存在的方法名称上相同，但是参数的类型、个数、顺序至少有一个不同
    3. 应该注意的是，返回值不同，其它都相同不算是重载

# 四、== 、 equals() 和 hashCode()🙋‍♂️
## 1. ==
1. 是 Java 中的一个**关系操作符，用于**==**比较两个对象的**====**内存地址**====**是否相同**==
    - 若操作数的类型是**基本数据类型**，则该关系操作符判断的是左右两边操作数的**值**是否相等
    - 若操作数的类型是**引用数据类型**，则该关系操作符判断的是左右两边操作数的**内存地址**是否相同。**也就是说，若此时返回 true，则该操作符作用的一定是同一个对象**
2. 例如：

    ```Java
    String str1 = "hello";
    String str2 = "hello";
    System.out.println(str1 == str2); // 返回 true，因为 str1 和 str2 都指向常量池中的同一个对象
    String str3 = new String("hello");
    String str4 = new String("hello");
    System.out.println(str3 == str4); // 返回 false，因为 str3 和 str4 指向堆中的不同对象
    ```
## 2. equals()
1. 是 Java 中 **Object 类的一个方法，用于比较一个对象是否等于另外一个对象**
    1. ==**默认情况下**==**，Object 类的** **`equals()`** **方法**==**比较的是两个对象的**====**内存地址**====**是否相等**==

    ![[IMG-20260620220610809.png|615]]

    2. 但往往更希望比较的是对象的内容，因此**可以根据需要在子类中重写** **`equals()`** **方法来**==**比较对象的**====**值**====**是否相等**==
    3. 例如，String 就重写了 equals() 方法

    ![[IMG-20260620220610853.png|339]]

    ```Java
    String str1 = "hello";
    String str2 = "hello";
    System.out.println(str1.equals(str2)); // 返回 true，因为 str1 和 str2 的值相等
    String str3 = new String("hello");
    String str4 = new String("hello");
    System.out.println(str3.equals(str4)); // 返回 true，因为 str3 和 str4 的值相
    ```
## 3. hashCode()
1. Object 中的 hashCode 调用了一个 native 本地方法，返回了一个 `int` 类型的整数（可正可负），==hashCode 的值默认是 JVM 使用==**==随机数==**==来生成的==

    ![[IMG-20260620220610896.png|268]]

2. **作用：**hashCode 方法在配合使用散列集合时，==判断元素是否存在时会使用到，可以提高在判断元素是否相同时，降低==调用 `equals()` 的频率，提升性能
    1. 如 HashMap、HashSet，因为这些集合的 `put()` 中会需要判断元素是否存在，如果只有 `equals()` 方法的话，需要一个个比较，效率太低
    2. 但是如果使用 `hashCode` 的话，经过散列函数（取模）就可以得到元素该存的索引下标
        1. 如果得到的索引值没有元素，则直接将当前元素直接放入集合
        2. 如果存在元素，才会进一步调用 `equals()` 比较两个元素的值是否相等

    ![[IMG-20260620220610953.png|648]]

3. 因此，降低了调用 `equals()` 的频率
## 4. 重写 Equals 时为什么一定要重写 hashCode🙋‍♂️
1. ==hashCode 的值默认是 JVM 使用随机数来生成的==
2. ==两个不同的对象生成的 hashCode 可能会相同==，这种情况，一般使用拉链法来解决这类哈希冲突问题
3. 但还会出现==两个相同的对象生成的 hashCode 可能会不同==，那么该类对象在配合使用散列集合时，就会有问题
    1. 例如：`a.equals(b) == ture`
    2. 如果没有重写 equals 方法，默认 equals 比较内存指向，因此这两个对象的内存地址一定是同一个，必然相等
    3. ⭐如果只重写 equals 方法，但没有重写 hashCode 方法，此时这两个对象的地址指向可能不同，但内容相同；==但由于 hashCode 是随机生成的，可能会不同，因此在配合散列集合使用的时候，会直接取模到不同的位置，==**==造成两个相同的对象，插入散列集合的不同位置==**

    ![[IMG-20260620220611029.png|354]]

    4. 因此，约定要重写 `hashCode()` 来保证，相同对象的 hashCode 一定相同！
4. **如何重写❓**
    1. 理想的散列函数应当具有均匀性，即不相等的对象应当均匀分布到所有可能的散列值上
    2. 可以将**每个域（对象属性）都当成 R 进制的某一位**，然后组成一个 R 进制的整数
    3. **R 一般取** **`31`**，因为它是一个奇素数，如果是偶数的话，当出现乘法溢出，信息就会丢失，因为与 2 相乘相当于向左移一位

    ```Java
    @Override
    	public int hashCode() {
    		int result = 17;
    		result = result * 31 + name.hashCode();
    		result = result * 31 + age;
    		return result;
    	}
    ```
# 五、String、StringBuilder 和 StringBuffer
## 1. String
1. **`String` 有**==**不可变**==**的特性**
    1. `String` 类被声明为 `final` ，因此它**不可被继承**
    2. 内部使用 `char` 数组存储数据，该数组被声明为 `final`，因此 **value 数组初始化之后就不能再引用其它数组**，并且 String 内部没有改变 value 数组的方法，因此可以保证 String 不可变

    ![[IMG-20260620220611082.png|520]]

    3. ==这意味着==**==每次对 String 对象进行操作时，都需要创建一个新的 String 对象==**==，因为原来的 String 对象不能更改==
2. **不可变的好处：**
    1. String 不可变性天生具备**==线程安全==**，可以在多个线程中安全地使用
    2. 因为 String 的 hash 值经常被使用，例如 String 用做 HashMap 的 key。**不可变的特性可以使得 hash 值也不可变，因此只需要进行一次计算**
    3. 只有不可变，才支持：如果一个 String 对象已经被创建过了，那么就会从 **String Pool** 中取得引用
3. **坏处：**这样会导致大量的内存分配和垃圾回收操作，特别是在处理大量字符串时会对性能产生负面影响
## 2. StringBuilder
1. **`StringBuilder`** 是一个==**可变**==**的对象，它允许对字符串进行修改而不创建新的对象**
    1. 继承自 `AbstractStringBuilder` ，使用一个非 `final` 的 `char[]`

    ![[IMG-20260620220611216.png|568]]

    2. 它通过**预先分配一段足够大的内存空间**来避免频繁的内存分配和垃圾回收操作
    3. 因此，当需要对字符串进行==**频繁的修改**==**时，应该使用 StringBuilder**；当需要处理不可变字符串时，应该使用String
2. ==**线程不安全**==
## 3. StringBuffer
1. **`StringBuffer`** 也是一个==**可变**==**的对象，它允许对字符串进行修改而不创建新的对象**
    1. 也是继承自 `AbstractStringBuilder` ，使用一个非 `final` 的 `char[]`
2. StringBuffer 还有一个重要的特性是==**线程安全**==
    1. 方法实现中使用 **`_synchronized_`** 关键字来保证线程安全，在多线程环境下使用它可以避免线程冲突的问题

    ![[IMG-20260620220611269.png|316]]

    2. 故性能略低于 StringBuilder

# 六、泛型擦除🙋‍♂️
1. 泛型的==本质是参数化类型（====[[泛型]]====）==，而类型擦除使得类型参数只存在于编译期，在运行时，`jvm` 是并不知道泛型的存在的
2. 什么是**泛型的类型擦除❓**
    1. 下面程序输出 `true`

    ```Java
    public static void main(String[] args) {
        List<String> list1 = new ArrayList<String>();
        List<Integer> list2 = new ArrayList<Integer>();
        System.out.println(list1.getClass()==list2.getClass());
    }
    ```
    2. 虽然 `ArrayList<String>` 和 `ArrayList<Integer>` 在编译时是不同的类型，但是在编译完成后都被编译器简化成了`ArrayList`，这一现象，被称为泛型的**类型擦除**(Type Erasure)
3. **为什么要进行泛型的类型擦除❓**
    1. 主要目的是避免过多的创建类而造成的运行时的过度消耗
    2. 如果用`List<A>`表示一个类型，再用`List<B>`表示另一个类型，以此类推，无疑会引起类型的数量爆炸
4. **反射能获取泛型的类型吗**❓
    1. 如果打印`Map`对象的参数类型：

    ```Java
    Map<String,Integer> map=new HashMap<>();
    System.out.println(Arrays.asList(map.getClass().getTypeParameters()));
    ```
    2. 最终也只能够获取到：

    ```Java
    [K, V]
    ```
    3. 可以看到通过`getTypeParameters`方法==只能获取到泛型的参数占位符==，而不能获得代码中真正的泛型类型
5. **能在指定类型的List中放入其他类型的对象吗**❓
    1. 可以通过反射，绕过编译检查，把一个类型的对象能放进另一类型的 `List`

    ![[IMG-20260620220611360.png|700]]

    2. 不仅在编译期间可以通过语法检查，并且也可以正常地运行，使用`debug`来看一下数组中的内容

    ![[IMG-20260620220611398.png|298]]

    3. 但是，打印会报错，因为`ArrayList`中`get`方法的源码中会进行强制类型转换

    ![[IMG-20260620220611457.png|728]]

    ![[IMG-20260620220611530.png|329]]

# 七、深拷贝与浅拷贝🙋‍♂️
1. **浅拷贝**
    - 是指在拷贝对象时，只拷贝对象本身和其属性的引用，而不是属性本身
    - ==如果原对象中的属性是引用类型，那么浅拷贝得到的对象和原对象会共享同一个属性对象==

    ![[IMG-20260620220611588.png|455]]

    - 可以通过**实现 `Cloneable` 接口**并**重写 `clone` 方法**来实现浅拷贝
2. **深拷贝**
    - 是指在拷贝对象时，不仅拷贝对象本身和其属性的引用，而且==会递归地拷贝对象的属性所指向的对象，直到所有的对象都被拷贝==
    - 深拷贝会复制对象本身以及对象所包含的所有属性和子属性

    ![[IMG-20260620220611662.png|456]]

    - 可以通过**实现 `Serializable` 接口**并使用**序列化**来实现深拷贝：先将对象转为字节序列，再把字节序列恢复成对象

# 八、成员变量 与 局部变量
1. **成员变量**
    1. 是属于**类或对象**的
    2. 可以被 `public` ，`private` ，`static` 等修饰符所修饰
    3. 静态成员变量存在方法区，非静态成员变量存在堆中
    4. 生命周期：是对象的一部分，它随着对象的创建而存在
2. **局部变量**
    1. 是在**方法中**定义的变量或是方法的参数
    2. 局部变量不能被访问控制修饰符及 `static` 所修饰
    3. 如果局部变量类型为基本数据类型，那么存储在栈内存，如果为引用数据类型，那存放的是指向堆内存对象的引用或者是指向常量池中的地址
    4. 生命周期：局部变量随着方法的调用而自动消

# 九、包装类
1. 针对八种基本数据类型定义相应的引用类型——包装类（封装类）
2. **为什么要有包装类❓**
    - ==解决基本数据类型无法做到的事情==，如**泛型类型参数**、**序列化**、**类型转换**、**高频区间数据缓存**等问题
    - 同时，使得基本数据结构有了类的特点，就可以调用类中的方法
    - 且有的方法的形参是引用型，导致基本数据类型放不进去
3. **基本类型、包装类与String类间的转换**

    ![[IMG-20260620220611873.png|704]]

4. 基本数据类型的自动拆箱可能会有空指针异常

    ![[IMG-20260620220611908.png|461]]

    1. 存在的问题：自动拆箱会调用 `xxxValue()`方法

    ```Java
     public boolean booleanValue() {
      return value;
     }
    ```
    2. **如果包装类 Boolean 对象是一个空对象 `NULL` 时，那么在调用 `booleanValue()`方法时便会抛出 `NullPointerException`**
        > 💡 上面代码中，success 对象可能为 null
    3. 故对要自动拆箱的返回值 `success` 做如下处理

    ```Java
     return Boolean.TRUE.equals(success);
    ```
        - `TRUE` 是包装类 `Boolean` 中的一个常量

    ```Java
     public static final Boolean TRUE = new Boolean(true);
    ```
        - 如果 success 为 true，则返回 true
        - 如果 success 为 false 或 NULL，则返回false
    4. PS：也可以使用hutool工具包处理

    ```Java
     return BooleanUtil.isTrue(success);
    ```
# 十、代码块
1. **普通代码块**
    1. 这种用法一般比较少见
    2. 普通代码块就是定义在方法中的代码块，也叫本地代码块

    ![[IMG-20260620220612074.png|380]]

2. **实例代码块**
    1. 定义在类中的代码块（不加修饰符）
    2. 作用：一般**==用于初始化实例成员变量==**

    ![[IMG-20260620220612186.png|245]]

    3. 实例代码块内部也可以初始化静态成员变量，但一般不这么做
    4. ==实例代码块只有在创建对象时才会执行==
3. **静态代码块**
    1. 使用 `static` 定义的代码块称为静态代码块
    2. 作用：一般**==用于初始化静态成员变量==**

    ![[IMG-20260620220612278.png|207]]

    3. ==不管生成多少个对象，静态代码块只会执行一次==
4. 代码的执行顺序为：
    1. **静态代码块 ➡️ 实例代码块 ➡️ 构造方法**
    2. 并且和代码块的定义顺序无关
    3. 如果有多个实例代码块，则根据它们的定义顺序来先后执行
    4. 如果有多个静态代码块，在编译代码时，编译器会按照定义的顺序依次合并

# 十一、迭代器
1. **概述**
    1. Iterator对象称为迭代器[[Export-e8249ac1-4ae1-42cd-83d5-041a266841fe/1question/Java 开发/设计模式/行为型模式/迭代器模式|迭代器模式]]，==主要用于====**遍历 Collection 集合中的元素**==
    2. 迭代器模式：
        1. 提供一种方法访问一个容器(container)对象中各个元素，而又不需暴露该对象的内部细节
        2. 迭代器模式，就是为容器而生
    3. 集合对象每次调用**`iterator()`**方法都得到一个**全新的迭代器对象**，默认游标都在集合的**第一个元素之前**
2. **Iterator 接口的使用**
    1. **`hasNext()`**、**`next()`**

    ```Java
    Iterator iterator = col1.iterator();
    //hasNext():判断是否还有下一个元素
    while (iterator.hasNext()){
        //next():
        //1.只要调用就会使指针下移
        //2.将下移以后集合位置上的元素返回
        System.out.println(iterator.next());
    }
    ```
        1. ⭐==在调用====`it.next()`====方法之前必须要调用====`it.hasNext()`====进行检测==。若不调用，且下一条记录无效，直接调用`it.next()`会抛出`NoSuchElementException`异常
        2. ⭐==一个====`while (iterator.hasNext())`== ==中不能出现两个== ==`.next()`====，否则会报====`NoSuchElementException`====异常（线程越界）==
    2. **`remove()`**

    ```Java
    Iterator iterator = col1.iterator();
    while (iterator.hasNext()){
        Object next = iterator.next();
        if (next.equals("Tom")){
            iterator.remove();
        }
    }
    Iterator iterator1 = col1.iterator();
    while (iterator1.hasNext()){
        System.out.println(iterator1.next());
    }
    ```
        1. Iterator可以删除集合的元素， 但是是遍历过程中通过**迭代器对象的remove方法**， 不是集合对象的remove方法
        2. 如果还未调用next()或在上一次调用 next 方法之后已经调用了 remove 方法，再调用remove都会报IllegalStateException
3. **另一种遍历方式 foreach**
    1. Java 5.0 提供了 foreach **`for (:) { }`**循环迭代访问 Collection 和 数组
    2. 遍历操作不需获取Collection或数组的长度，无需使用索引访问元素
    3. 遍历集合的**底层调用Iterator完成操作**
    4. foreach还可以用来遍历数组

    ```Java
     //for(集合元素的类型 局部变量 : 集合对象)
     for (Object obj:col1) {
         System.out.println(obj);
     }
    ```
    5. foreach并不会修改原集合中的内容

    ```Java
     for (Object obj : col1) {
         obj = new Person("Jack",20);//只是赋值给了对象obj
         System.out.println(obj);
     }
     for (Object obj : col1) {
         System.out.println(obj);//原来的集合并未发生改变
     }
    ```
# 十二、比较器
1. 介绍
    1. 在Java中经常会涉及到对象数组的排序问题，那么就涉及到对象之间的比较问题
    2. Java实现**对象排序**的方式有两种：
        1. 自然排序：**`java.lang.Comparable`**，一旦指定一劳永逸
        2. 定制排序：**`java.util.Comparator`**，临时性的给定比较规则
    3. ⭐==**两者的使用场景不同：**==
        1. 使用 Comparable 必须==**要修改原有的类**==，也就是你要排序那个类
            1. 就要在那个中实现 Comparable 接口并重写 compareTo 方法
            2. 所以 Comparable 更像是**“对内”进行排序的接口**
        2. 而 Comparator 的使用则不相同，Comparator ==**无需修改原有类**==
            1. 也就是在最极端情况下，即使 Person 类是第三方提供的，我们依然可以通过创建新的自定义比较器 Comparator，来**实现对第三方类 Person 的排序功能**
            2. 也就是说通过 Comparator 接口可以实现和原有类的解耦，在不修改原有类的情况下实现排序功能
            3. 所以 Comparator 可以看作是**“对外”提供排序的接口**
2. **自然排序：java.lang.Comparable**
    1. 像 String 包装类等**实现了** **`Comparable`** **接口，重写了** **`compareTo()`** **方法**，给出了比较两个对象大小的方式

    ```Java
     String[] arr = new String[]{"AA","BB","EE","DD"};
     Arrays.sort(arr);//从小到大排的
     System.out.println(Arrays.toString(arr));//[AA, BB, DD, EE]
    ```
    2. **==重写====`compareTo()`====方法的规则：==**
        1. 如果当前对象this大于形参对象obj， 则返回正整数
        2. 如果当前对象this小于形参对象obj， 则返回负整数
        3. 如果当前对象this等于形参对象obj， 则返回零
    3. **对于自定义类，**==**如果需要排序，可以让自定义类实现 Comparable 接口，重写compareTo()方法**==

    ```Java
     public class Goods implements Comparable{//⭐实现接口
         private String name;
         private int price;
         /*get、set、构造器、toString*/
         //⭐指明排序方式
         @Override
         public int compareTo(Object o) {
         if(o instanceof Goods){
             Goods goods = (Goods) o;
             if(this.price > goods.price){
                 return 1;
             }else if(this.price < goods.price){
                 return -1;
             }else {
                 //若价格相同，则比名字，再嵌套一个compareTo()
                 //name是String类型的，已经有重写好的了
                 //返回-负的实现从高到低
                 return -this.name.compareTo(goods.name);
             }
         }
         throw new RuntimeException("传入的数据类型不一致");
     }
    ```
    ```Java
     public class Test {
         public static void main(String[] args) throws ParseException {
             Goods[] goods = new Goods[4];
             goods[0]=new Goods("lenovo",34);
             goods[1]=new Goods("huawei",22);
             goods[2]=new Goods("xiaomi",3);
             goods[3]=new Goods("dell",56);
             Arrays.sort(goods);
             System.out.println(Arrays.toString(goods));
             //[Goods{name='xiaomi', price=3}, Goods{name='huawei', price=22}, Goods{name='lenovo', price=34}, Goods{name='dell', price=56}]
         }
     }
    ```
3. **定制排序：java.util.Comparator**
    1. 使用场景
        1. 当元素的类型**没有实现 java.lang.Comparable 接口，而又不方便修改代码**
        2. 或者**实现了 java.lang.Comparable 接口的排序规则，但是此规则不适合当前的操作**
    2. 那么**==可以考虑使用== ==`Comparator`== ==的对象来排序==**
    3. **==重写====`compare(Object o1,Object o2)`====方法的规则：==**
        1. 如果方法返回正整数，则表示o1大于o2
        2. 如果返回0，表示相等
        3. 返回负整数，表示o1小于o2
    4. 代码示例

    ```Java
    public class StringTest {
        public static void main(String[] args) throws ParseException {
            Goods[] goods = new Goods[4];
            goods[0]=new Goods("lenovo",34);
            goods[1]=new Goods("huawei",22);
            goods[2]=new Goods("xiaomi",3);
            goods[3]=new Goods("dell",56);
            //⭐要排序时，临时给一个排序方法
            //匿名类实现接口Comparator，重写compare()
            Arrays.sort(goods, new Comparator<Goods>() {
                @Override
                public int compare(Goods o1, Goods o2) {
                    if(o1.getPrice() > o2.getPrice()){
                        return 1;
                    }if(o1.getPrice() < o2.getPrice()){
                        return -1;
                    }else{
                        return o1.getName().compareTo(o2.getName());
                    }
                }
            });
            System.out.println(Arrays.toString(goods));
        }
    }
    ```
# 十三、枚举类
- 使用枚举类优化 `if-else`
    - 优化前

    ```Java
    String OrderStatusDes;
    if(orderStatus==0){
        OrderStatusDes ="订单未支付";
    }else if(OrderStatus==1){
        OrderStatusDes ="订单已支付";
    }else if(OrderStatus==2){
       OrderStatusDes ="已发货";
    }
    ```
    - 优化后

    ```Java
    public enum OrderStatusEnum {
        UN_PAID(0,"订单未支付"),PAIDED(1,"订单已支付"),SENDED(2,"已发货"),;
        private int index;
        private String desc;
        public int getIndex() {
            return index;
        }
        public String getDesc() {
            return desc;
        }
        OrderStatusEnum(int index, String desc){
            this.index = index;
            this.desc =desc;
        }
        OrderStatusEnum of(int orderStatus) {
            for (OrderStatusEnum temp : OrderStatusEnum.values()) {
                if (temp.getIndex() == orderStatus) {
                    return temp;
                }
            }
            return null;
        }
    }
    // if-else代码可以优化成一行代码
    String OrderStatusDes = OrderStatusEnum.0f(orderStatus).getDesc();
    ```
