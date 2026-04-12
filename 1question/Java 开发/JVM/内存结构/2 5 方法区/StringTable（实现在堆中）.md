- [[#1. 串池简介]]
- [[#2. StringTable 的特性]]
    - [[#2.1 字符串字面量在第一次被用到时，才会成为对象⭐]]
    - [[#2.3 StringTable 可以保证避免重复创建字符串对象⭐]]
    - [[#2.4 字符串拼接原理]]
    - [[#2.5 intern() 方法⭐]]
- [[#3. StringTable 的垃圾回收]]
- [[#4. StringTable 的性能调优⭐]]
    - [[#4.1 StringTable 的大小，相当于扩大了底层哈希数组的大小]]
    - [[#4.2 使用 intern() 方法将所有字符串加入 StringTable，避免重复字符串的内存占用]]
- [[#5. 使用案例⭐]]
- [[#6. 面试题]]
    - [[#6.1 面试题一]]
    - [[#6.2 面试题二]]
    - [[#6.3 面试题三]]
# 1. **串池简介**
1. StringTable 也叫串池
    
    1. 可以用于==存放字符串对象==，应用程序中大量的字符串常量都会被分配到 StringTable 中
    
    1. 可以==避免重复创建字符串对象==
    
1. ==底层是一个 hashtable== 结构的数据结构（数组 + 链表），不能扩容
1. StringTable 的位置
    
    1. jdk 1.6 及之前，StringTable 是常量池的一部分，随着常量池存储在永久代（堆的一部分）中
    
    1. j==dk 1.7 及以后，StringTable 被留在堆中，因为永久代的内存回收效率很低，而堆里的垃圾回收效率较高==
    
# 2. **StringTable 的特性**
## 2.1 **字符串字面量在第一次被用到时，才会成为对象**⭐
1. 常量池中的信息在类被加载之后，都会被放入到运行时常量池中
1. 但这时常量池中的字符串仅是符号，如 ”a” “b” “ab” 都是常量池中的符号，还没有变为 java 字符串对象，等到第一次用到时才会变为对象
1. 示例验证：
    
    1. 当运行到断点时，内存里有 2216 个字符串对象
        
        ![[Attachment/1question/大数据/Java 开发/JVM/内存结构/2 5 方法区/IMG-20260405035413906.png|Untitled 459.png]]
        
        ![[IMG-20260404031748994.png|Untitled 1 335.png]]
        
    
    1. 再往下运行两行，此时内存里有 2218 个字符串对象，新增了 "1" "2" 两个字符串对象，因此验证了字符串字面量只有在被用到时，才会成为字符串对象
        
        ![[IMG-20260405035420317.png|Untitled 2 274.png]]
        
        ![[IMG-20260405035422028.png|Untitled 3 205.png]]
        
    
## 2.3 **StringTable 可以保证避免重复创建字符串对象**⭐
1. 当第一次用到一个字符串时，==首先会查看串池中是否已经存在相同值得字符串==
    
    1. **如果存在，就会沿用串池中已有得字符串对象**
    
    1. 如果没有，则会新创建一个该值得字符串，并添加到串池中
    
    ```Java
    String s = "hello";
    String s2 = new String("hello");
    ```
    
    ![[IMG-20260405035432772.png|Untitled 4 159.png]]
    
1. 示例验证：
    
    1. 当运行到断点时，内存里有 2226 个字符串对象
        
        ![[IMG-20260405035444773.png|Untitled 5 129.png]]
        
        ![[IMG-20260405035504969.png|Untitled 6 106.png]]
        
    
    1. 再往下运行两行，此时内存里仍然有 2226 个字符串对象，并没有新增，因为串池里已经存在了相同值的字符串对象，执行到这行代码时，可以串池中找到，故不再会创建新的字符串对象
        
        ![[IMG-20260405035511787.png|Untitled 7 85.png]]
        
        ![[IMG-20260405035511812.png|Untitled 8 68.png]]
        
    
## 2.4 **字符串拼接原理**
[**（详见面试题一）**](https://www.notion.so/StringTable-df202ee339ca445eb2ee73ff9b5ed6ce?pvs=21)
1. 字符串**变量**拼接的原理是 **StringBuilder** 的 `append()` 方法（1.8）
    
    ```Java
     String s1 = "a";
     String s2 = "b";
     String s3 = s1 + s2;    //new StringBuilder().append("a").append("b").toString()
    ```
    
1. 字符串**常量**拼接的原理是**编译期优化**
    
    ```Java
     String s5 = "a" + "b";
    ```
    
## 2.5 `**intern()**` **方法**⭐
[**（详见面试题二、面试题三）**](https://www.notion.so/StringTable-df202ee339ca445eb2ee73ff9b5ed6ce?pvs=21)
1. ==可以使用== `==intern==` ==方法，====**主动将串池中还没有的字符串对象放入串池**==
1. 不同的 jdk 版本 intern 方法的操作会有不同
    
    1. 1.8 将这个字符串对象尝试放入串池
        
        - 如果有则并不会放入
        
        - 如果没有则放入串池， 会把串池中的对象返回
        
    
    1. 1.6 将这个字符串对象尝试放入串池
        
        - 如果有则并不会放入
        
        - 如果没有会把此对象复制一份放入串池（也就是说最后放入的不是这个对象自己，而是他的一个新的副本对象），会把串池中的对象返回，返回的就是那个新的副本对象
        
    
# 3. **StringTable 的垃圾回收**
1. jdk 1.7 及以后，StringTable 被留在堆中，因为永久代的内存回收效率很低，而堆里的垃圾回收效率较高
1. ==当 StringTable 中的字符串对象过多时，会触发垃圾回收机制==
1. 演示 StringTable 垃圾回收：
    
    1. 代码：
        
        ```Java
         public class stringTableDemo4 {
             public static void main(String[] args) throws InterruptedException {
                 int i = 0;
                 try {
                     for (int j = 0; j < 100000; j++) { // j=100, j=10000
                         String.valueOf(j).intern();
                         i++;
                     }
                 } catch (Throwable e) {
                     e.printStackTrace();
                 } finally {
                     System.out.println(i);
                 }
             }
         }
        ```
        
    
    1. 虚拟机参数设置：因为是 jdk 1.8 ，所以这里对堆内存的大小做了限制，以展示 StringTable 的垃圾回收机制；并打印垃圾回收的细节
        
        - `Xmx10m -XX:+PrintStringTableStatistics -XX:+PrintGCDetails -verbose:gc`
        
    
    1. 运行结果分析：发生了垃圾回收
        
        ![[IMG-20260405035520314.png|Untitled 9 60.png]]
        
    
# 4. **StringTable 的性能调优⭐**
## 4.1 **StringTable 的大小，相当于扩大了底层哈希数组的**大小
1. 由扩大于 StringTable 是一个 `hashtable` 结构的数据结构（数组 + 链表）
1. ⭐ 而哈希表的性能是和他的大小密切相关的，如果哈希表的桶的个数比较多（数组比较大），那么元素就会比较分散，从而发生**哈希碰撞的几率就会少，链表的长度会较短，这样查找的速度也会更快**
1. 优化演示：演示==**串池大小**====对性能的影响==
    
    1. 代码：读取文件里的字符串，并使用 `intern()` 方法将所有字符串加入 StringTable
        
        ```Java
         public class stringTableDemo5 {
             public static void main(String[] args) throws IOException {
                 try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream("C:/linux.words"), "utf-8"))) {
                     String line = null;
                     long start = System.nanoTime();
                     while (true) {
                         line = reader.readLine();
                         if (line == null) {
                             break;
                         }
                         //将每一个字符串都入池
                         line.intern();
                     }
                     //打印耗时
                     System.out.println("cost:" + (System.nanoTime() - start) / 1000000);
                 }
             }
         }
        ```
        
    
    1. 未优化执行：
        
        运行参数：`-Xms500m -XX:+PrintStringTableStatistics -XX:StringTableSize=1009`
        
        花费了 4581 毫秒
        
        ![[IMG-20260405035527355.png|Untitled 10 51.png]]
        
    
    1. 优化==（扩大串池大小）==后执行：
        
        运行参数：`-Xms500m -XX:+PrintStringTableStatistics -XX:StringTableSize=200000`
        
        花费了 221 毫秒（可以看到有显著的性能提升）
        
        ![[IMG-20260405035532779.png|Untitled 11 43.png]]
        
    
## 4.2 使用 `intern()` 方法将所有字符串加入 StringTable，避免重复字符串的内存占用
1. 在应用程序中有==大量的重复的字符串数据==
    
    - 例如用户的地址，大量用户的地址都是同样值的字符串
    
    - 如果每个字符串都创建一个字符串对象，会造成大量的内存占用
    
1. 因此如果将每个字符串放入 StringTable 可以避免重复字符串对象的创建，从而节省大量的内存空间
1. 优化演示：演示**是否使用串池**对性能的影响
    
    1. **未优化的代码：**读取文件里的字符串，并添加到 list 中
        
        ```Java
         public class stringTableDemo6 {
             public static void main(String[] args) throws IOException {
         
                 List<String> address = new ArrayList<>();
                 System.in.read();
                 for (int i = 0; i < 10; i++) {
                     try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream("C:/linux.words"), "utf-8"))) {
                         String line = null;
                         long start = System.nanoTime();
                         while (true) {
                             line = reader.readLine();
                             if(line == null) {
                                 break;
                             }
                             address.add(line);  //⭐
                         }
                         System.out.println("cost:" +(System.nanoTime()-start)/1000000);
                     }
                 }
                 System.in.read();
             }
         }
        ```
        
        执行后查看内存监控结果：
        
        可以看到 `char[]` 和 `String` 对象一共占了内存的 `90%` 左右，大约 `300M`
        
        ![[IMG-20260405035535647.png|Untitled 12 39.png]]
        
    
    1. **优化后的代码：**
        
        1. 读取文件里的字符串，并添加到 list 中
        
        1. ⭐同时在`add()` 前使用 `intern()` 方法将所有字符串加入 StringTable
        
        ```Java
         public class stringTableDemo6 {
             public static void main(String[] args) throws IOException {
         
                 List<String> address = new ArrayList<>();
                 System.in.read();
                 for (int i = 0; i < 10; i++) {
                     try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream("C:/linux.words"), "utf-8"))) {
                         String line = null;
                         long start = System.nanoTime();
                         while (true) {
                             line = reader.readLine();
                             if(line == null) {
                                 break;
                             }
                             address.add(line.intern()); //⭐
                         }
                         System.out.println("cost:" +(System.nanoTime()-start)/1000000);
                     }
                 }
                 System.in.read();
             }
         }
        ```
        
        执行后查看内存监控结果：
        
        可以看到 `char[]` 和 `String` 对象一共只占了内存的`50%`左右，大约 `32M`，巨大提升
        
        ![[IMG-20260405035541296.png|Untitled 13 37.png]]
        
    
# 5. 使用案例⭐
- [[一人限购一单（悲观锁）]]
# 6. **面试题**
## 6.1 **面试题一**
1. 题目：
    
    ```Java
     public class stringTableDemo1 {
         public static void main(String[] args) {
             String s1 = "a";
             String s2 = "b";
             String s3 = "ab";
    
             String s4 = s1 + s2;
             String s5 = "a" + "b";
         }
     }
    ```
    
    问以下语句的输出结果：
    
    1. `System.out.println(s3 == s4);`
    
    1. `System.out.println(s3 == s5);`
    
1. 将代码编译后，使用 `javap -v` 读出 class 文件内容，再分析：
    
    1. 1️⃣先看 `s1`， `s2`， `s3` 三个对象的生成过程：
        
        ![[IMG-20260405035545361.png|Untitled 14 34.png]]
        
        - 常量池中的信息，都会被加载到运行时常量池中， 这时 a b ab 都是常量池中的符号，还没有变为 java 字符串对象
        
        - `ldc #2` ：会查看StringTable[]中是否有值为 "a" 的字符串对象，如果有，则使用串池中已有的对象；如果没有，则新创建一个 "a" 字符串对象，并将其加入StringTable[]，此时 `StringTable [ "a" ]`
        
        - `astore_1` ：会将创建好的字符串对象 ”a“，存入局部变量表的 `s1` 变量中
        
        - `ldc #3` ：会查看StringTable[]中是否有值为 "b" 的字符串对象，如果有，则使用串池中已有的对象；如果没有，则新创建一个 "b" 字符串对象，并将其加入StringTable[]，此时 `StringTable [ "a","b" ]`
        
        - `astore_2` ：会将创建好的字符串对象 ”b“，存入局部变量表的 `s2` 变量中
        
        - `ldc #4` ：会查看StringTable[]中是否有值为 "ab" 的字符串对象，如果有，则使用串池中已有的对象；如果没有，则新创建一个 "ab" 字符串对象，并将其加入StringTable[]，此时 `StringTable [ "a","b","ab" ]`
        
        - `astore_3` ：会将创建好的字符串对象 ”ab“，存入局部变量表的 `s3` 变量中
        
    
    1. 2️⃣看 `s4` 对象的生成过程：
        
        ![[IMG-20260405035548224.png|Untitled 15 32.png]]
        
        - `invokespecial #6` ：调用 `StringBuilder`的无参构造函数
        
        - `aload_1`：将局部变量表中 `1` 号的位置的变量取出
            
            ![[IMG-20260405035551008.png|Untitled 16 25.png]]
            
        
        - `invokevirtual #7` ：调用 `StringBuilder` 的 `append()` 方法，并将 `aload_1` 取出的变量，作为参数传入
        
        - `aload_2` ： 将局部变量表中 `2` 号的位置的变量取出
        
        - `invokevirtual #7`：再次调用 `StringBuilder` 的 `append()` 方法，并将 `aload_2` 取出的变量，作为参数传入
        
        - `invokevirtual #8`：调用 `StringBuilder` 的 `toString()` 方法，而`toString()` 方法会将拼接好的字符串，新创建为一个字符串对象 `“ab”`
            
            ![[IMG-20260405035551073.png|Untitled 17 25.png]]
            
        
        - `astore 4`：将新创建的 `ab` 字符串对象存入局部变量表的 `s4` 变量中
        
        到此可以确定 `System.out.println(s3 == s4);` 的输出结果为 `false`
        
        > 注意：本行代码新创建的对象是使用动态拼接方式创建的，并不会放入串池（如果要放入串池，需要主动使用 intern() 方法），而是存放在堆中（堆是存放new 出来的对象的内存空间）
        
    
    1. 3️⃣看 `s5` 对象的生成过程：
        
        ![[IMG-20260405035553713.png|Untitled 18 24.png]]
        
        - `ldc #4` ：会查看StringTable[]中是否有值为 "ab" 的字符串对象，发现有（之前 `s3` 变量创建并存入的对象），所以不会创建新的字符串 对象了，而是沿用串池中已有的对象
        
        - `astore 5` ：会串池中原有的字符串对象存入局部变量表的 `S5` 变量中
        
        ==到此可以确定== ==`System.out.println(s3 == s5);`== ==的输出结果为== ==`true`==
        
        > ⭐s4 对象与 s5 对象生成时，差异产生的原因：
        > 
        > 1. `s5` 对象生成时，javac 会在编译期间优化，因为在编译期已经可以确定`s5` 对象拼接后的结果为：ab，于是就可以直接去 StringTable[] 中看有没有
        > 
        > 1. 而`s4` 对象是由两个变量 `s1` 和 `s2` 通过 `+` 拼接的，编译期间并不知道两个变量 `s1` 和 `s2` 的值，只能在运行期间用 `StringBuilder`的方式动态的拼接
        
    
## 6.2 **面试题二**
1. 题目：
    
    ```Java
     public class stringTableDemo3 {
         public static void main(String[] args) {
             String s = new String("a") + new String("b");
             String s2 = s.intern();
         }
     }
    ```
    
    - 问以下语句的输出结果：
        
        1. `System.out.println(s2 == s);`
        
        1. `System.out.println(s2 == "ab");`
        
    
1. 分析：
    
    1. 开始串池中为空：`StringTable[ ]`
    
    1. 第一行代码中的 `"a"` `"b"`，是两个常量（这里和 `s1 = "a" ; s2 = "b"`是一样的），此时会查看串池中有没有值相同的字符串对象，发现没有，则会创建对应值的字符串对象，并放入串池，此时 `StringTable[ "a" "b" ]`
    
    1. 而第一行代码中的 `new String("a")，new String("b")`，因为是 `new` 关键字，故会在堆空间中创建两个字符串对象，此时查看串池中已经有了这两个值得字符串对象，故不会将这两个对象放入串池
    
    1. 又因为 `new String("a")` 和 `new String("b")` 使用 `+` 拼接，这种动态拼接方式会在堆中 `new` 一个值为 `ab` 的字符串对象 `s`，且不会放入串池中，此时 `StringTable[ "a" "b" ]`
    
    1. 第二行代码中的 `s.intern();` 会将堆中的对象 `s` 尝试放入串池中，此时串池中没有值为 `"ab"` 的字符串对象，所以会将 `s` 对象放入串池，并将放入的对象返回，因此返回的对象 `s2` 就是存入串池的对象 `s`，此时 `StringTable[ "a" "b" "ab" ]`
        
        到此可以确定 `System.out.println(s2 == s);` 的输出结果为 `true`
        
        > jdk 1.6 因为存入的是副本对象，返回的对象 s2 就是存入串池的副本对象 s'，故这里的结果是 false
        
    
    1. 第二个输出语句中的 `"ab"` 是一个常量，遇到时会去串池中找有没有值为 `"ab"` 的字符串对象，发现有，则返回串池中已有的对象，也就是上面的对象 `s`，也是对象 `s2`
        
        到此可以确定 `System.out.println(s2 == "ab");` 的输出结果为 `true`
        
        > jdk 1.6 因为存入的是副本对象，返回的对象 s2 就是存入串池的副本对象 s'，而 "ab" 用的也是串池的副本对象 s'，故这里的结果也是 true
        
    
## 6.3 **面试题三**
1. 题目：
    
    ```Java
     public class stringTableDemo3 {
         public static void main(String[] args) {
             String x = "ab";
             String s = new String("a") + new String("b");
             String s2 = s.intern();
         }
     }
    ```
    
    问以下语句的输出结果：
    
    1. `System.out.println( s2 == x);`
    
    1. `System.out.println( s == x );`
    
1. 分析：
    
    1. 开始串池中为空：`StringTable[ ]`
    
    1. 第一行代码中的 `"ab"` 一个常量，此时会查看串池中有没有值相同的字符串对象，发现没有，则会创建对应值的字符串对象，并将创建的对象 `x` 放入串池，此时 `StringTable[ "ab" ]`
    
    1. 第二行代码和面试题二一样，最后 `StringTable[ "ab" "a" "b" ]`
    
    1. 第三行代码中的 `s.intern();` 会将堆中的对象 `s` 尝试放入串池中，此时串池中已经有了值为 `"ab"` 的字符串对象，所以不会将 对象 `s` 放入串池，而是会返回串池中的对象，因此返回的对象 `s2` 就是 对象 `x`，此时 `StringTable[ "ab" "a" "b" ]`
        
        到此可以确定 `System.out.println(s2 == x);` 的输出结果为 `true`
        
        到此可以确定 `System.out.println(s == x);` 的输出结果为 `false`