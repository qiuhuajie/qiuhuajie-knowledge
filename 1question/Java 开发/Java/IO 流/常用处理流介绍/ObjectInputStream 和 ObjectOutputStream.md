# 1. 介绍
1. 设计背景：
    
    1. **思考：如果我们从IO输入流中读取到100这个数据的时候，如何判断这项数据的类型是属于数字还是字符串类型呢？**
    
    1. 为了能让开发者在读取数据源的时候同时了解更多数据的属性，人们设计出了对象输入/输出流
    
1. 作用：可以把Java中的对象写入到数据源中，也能把对象从数据源中还原回
    
    - **序列化**：用`ObjectOutputStream`类，**将内存中的Java对象保存到磁盘中，或通过网络传输出去**
    
    - **反序列化**： 用`ObjectInputStream`类，**将磁盘中的对象还原为内存中的Java对象**
    
    > [!important] **对象的序列化机制：**
    > 
    > 1. 允许把内存中的Java对象转换成平台无关的二进制流，从而允许把这种二进制流持久地保存在磁盘上，或通过网络将这种二进制流传输到另一个网络节点；当其它程序获取了这种二进制流，就可以恢复成原来的Java对象
    > 
    > 1. 使用序列化机制需要注意的点：
    >     
    >     1. 不能序列化`static`和`transient`（不想让某属性可序列化时使用）修饰的成员变量
    >     
    >     1. 对象所属的类一定需要是可序列化的：
    >         
    >         1. 需要该类实现`Serializable`接口
    >         
    >         1. 需要该类提供一个常量`serialVersionUID`：若对象序列化后，所属类若类做了修改， 且没有定义`serialVersionUID`，则在反序列化中，对象就找不到自己的所属类了
    >         
    >         1. 该类内部的所有属性也是可序列化的（基本数据类型默认都是可序列化的）
    >         
    >     
    >     ```Java
    >     public class Person implements Serializable {
    >        
    >         public static final long serialVersionUID = 4687687868L;
    >         
    >         private Accont accont;//Accont类也需要是可序列化的
    >         
    >     }
    >     ```
    >     
    
    > [!important] **如果没有设置**
    > 
    > `**serialVersionUid**`**关键字，在进行序列化的过程中可能会遇到什么问题**
    > 
    > 1. 假设我们原先的对象`A`中有`id`，`name`两个字段，该对象在被序列化之后存储到`temp`文件中
    > 
    > 1. 此时对`A`对象进行了升级变成了`A_1`对象，字段变为了`id`，`name`，`age`，此时将`temp`文件夹中存储的内容重新反序列化到`A_1`对象上，就会出现报错异常，例如下边所示：
    >     
    >     ```Java
    >     Exception in thread "main" java.io.InvalidClassException: org.idea.architect.framework.io.节点流.Dog; local class incompatible: stream classdesc serialVersionUID = 198678371, local class serialVersionUID = 4180152316968275835
    >      at java.io.ObjectStreamClass.initNonProxy(ObjectStreamClass.java:699)
    >      at java.io.ObjectInputStream.readNonProxyDesc(ObjectInputStream.java:1885)
    >      at java.io.ObjectInputStream.readClassDesc(ObjectInputStream.java:1751)
    >      at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:2042)
    >      at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1573)
    >      at java.io.ObjectInputStream.readObject(ObjectInputStream.java:431)
    >      at org.idea.architect.framework.io.节点流.ObjectInputStreamDemo.readObj(ObjectInputStreamDemo.java:19)
    >      at org.idea.architect.framework.io.节点流.ObjectInputStreamDemo.main(ObjectInputStreamDemo.java:25)
    >     ```
    >     
    > 
    > 1. **⭐如果一个对象在进行序列化操作的时候没有声明**`serialVersionUid`**关键字，在**==**jdk底层会自动根据字段属性给它生成一个**====`serialVersionUid`====**关键字**==
    >     
    >     1. 这也就意味着当原先对象的字段发生变动的时候，这个`serialVersionUid`字段值也会变动
    >     
    >     1. 这里报错的内容就是因为序列化和反序列化过程中会通过判断`serialVersionUid`来识别是否是对同一种类型的对象操作，如果原先对象的字段属性发生了变动则会导致`serialVersionUid`值发生变化从而抛出异常
    >     
    
    # 2. 代码示例
    
    ## 2.1 序列化
    
    ```Java
    public static void main(String[] args) throws IOException {
        ObjectOutputStream oos = null;
        try {
            oos = new ObjectOutputStream(new FileOutputStream("C:/Users/lenovo/Desktop/25inputs.txt"));
            oos.writeObject(new String("AAA"));
            oos.flush();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                oos.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    ```
    
    ## 2.2 反序列化：
    
    ```Java
    public static void main(String[] args) throws IOException {
        ObjectInputStream ois = null;
        try {
            ois = new ObjectInputStream(new FileInputStream("C:/Users/lenovo/Desktop/25inputs.txt"));
            Object o = ois.readObject();
            String str = (String) o;
            System.out.println(str); //AAA
        } catch (IOException e) {
            e.printStackTrace();
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } finally {
            try {
                ois.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    ```