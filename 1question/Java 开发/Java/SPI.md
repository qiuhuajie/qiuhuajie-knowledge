---
title: "SPI"
tags:
  - "SPI"
  - "SPI接口"
  - "SPI具体实现"
  - "API"
  - "ServiceLoader"
  - "Service类"
updated: 2026-04-16
---

[https://juejin.cn/post/7197070078361387069](https://juejin.cn/post/7197070078361387069)

[https://segmentfault.com/a/1190000041020216](https://segmentfault.com/a/1190000041020216)

[https://pdai.tech/md/java/advanced/java-advanced-spi.html#spi机制-common-logging](https://pdai.tech/md/java/advanced/java-advanced-spi.html#spi%E6%9C%BA%E5%88%B6-common-logging)

# 一、介绍
1. 背景
    1. 在面向对象的设计原则中，一般推荐模块之间基于接口编程，通常情况下调用方模块是不会感知到被调用方模块的内部具体实现。一旦代码里面涉及具体实现类，就违反了开闭原则。如果需要替换一种实现，就需要修改代码
    2. 为了实现在模块装配的时候不用在程序里面动态指明，这就需要一种服务发现机制
2. SPI（Service Provider Interface）是一种服务发现机制，主要用于**在运行时查找和加载可插拔服务的实现**
3. ⭐ ==**实现逻辑：调用方通过调用JDK提供的标准化的服务接口，通过本地服务发现，加载第三方或者自身实现了该接口的类**==
4. 通过这种方式，==**服务规范制定者制定接口规范，服务提供者按照接口进行实现**==

    ![[IMG-20260620222732520.png|515]]

5. ==**优点：**==
    1. Java 中 SPI 机制主要思想是将装配的控制权移到程序之外，在模块化设计中这个机制尤其重要，其核心思想就是解耦
    2. SPI 将服务接口和具体的服务实现分离开来，将服务调用方和服务实现者解耦
    3. 这种机制使得应用程序能够**轻松扩展**，**支持不同的服务提供者**，而无需更改主程序的代码
6. ==**缺点：**==
    1. 不能按需加载，需要遍历所有的实现，并实例化，然后在循环中才能找到我们需要的实现。如果不想用某些实现类，或者某些类实例化很耗时，它也被载入并实例化了，这就造成了浪费
    2. 获取某个实现类的方式不够灵活，只能通过 Iterator 形式获取，不能根据某个参数来获取对应的实现类
    3. 多个并发多线程使用 ServiceLoader 类的实例是不安全的
7. 很多框架都使用了 Java 的 SPI 机制
    1. 比如：数据库加载驱动，日志接口，以及 dubbo 的扩展实现等等
    2. 在JDK中实现数据库驱动按需加载就是利用SPI的方式实现的，JDK规定了 java.sql.Driver 接口，其具体实现可以是MySQL或者PostgreSQL，具体实现是第三方的驱动服务方提供，通过SPI机制加载供调用方使用。

# 二、SPI 和 API 有啥区别
1. 说到 SPI 就不得不说一下 API 了，从广义上来说它们都属于接口，而且很容易混淆。下面先用一张图说明一下：

    ![[IMG-20260620222732573.png|430]]

2. 一般模块之间都是通过通过接口进行通讯，那我们在服务调用方和服务实现方（也称服务提供者）之间引入一个“接口”
3. 当**实现方提供了接口和实现**，我们可以通过调用实现方的接口从而拥有实现方给我们提供的能力，**这就是 API** ，这种接口和实现都是放在实现方的
4. ==**当接口存在于调用方这边时，就是 SPI**==
    1. 由接口调用方确定接口规则，然后由不同的厂商去根绝这个规则对这个接口进行实现，从而提供服务
    2. 举个通俗易懂的例子：公司 H 是一家科技公司，新设计了一款芯片，然后现在需要量产了，而市面上有好几家芯片制造业公司，这个时候，只要 H 公司指定好了这芯片生产的标准（定义好了接口标准），那么这些合作的芯片公司（服务提供者）就按照标准交付自家特色的芯片（提供不同方案的实现，但是给出来的结果是一样的）

# 三、Java SPI 应用实例
- [https://juejin.cn/post/6844903605695152142](https://juejin.cn/post/6844903605695152142)
- 当服务的提供者提供了一种接口的实现之后，需要在classpath下的META-INF/services/目录里创建一个以服务接口命名的文件，这个文件里的内容就是这个接口的具体的实现类。当其他的程序需要这个服务的时候，就可以通过查找这个jar包（一般都是以jar包做依赖）的META-INF/services/中的配置文件，配置文件中有接口的具体实现类名，可以根据这个类名进行加载实例化，就可以使用该服务了。JDK中查找服务实现的工具类是：java.util.ServiceLoader
## 1. SPI接口
- 定义了一个对象序列化接口，内有三个方法：序列化方法、反序列化方法和序列化名称
    ```Java
    public interface ObjectSerializer {
        byte[] serialize(Object obj) throws ObjectSerializerException;
        <T> T deSerialize(byte[] param, Class<T> clazz) throws ObjectSerializerException;
        String getSchemeName();
    }
    ```
## 2. SPI具体实现
1. 实现一：使用Kryo的序列化方式。Kryo 是一个快速高效的Java对象图形序列化框架，它原生支持java，且在java的序列化上甚至优于google著名的序列化框架protobuf。

    ```Java
    public class KryoSerializer implements ObjectSerializer {
        @Override
        public byte[] serialize(Object obj) throws ObjectSerializerException {
            byte[] bytes;
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            try {
                //获取kryo对象
                Kryo kryo = new Kryo();
                Output output = new Output(outputStream);
                kryo.writeObject(output, obj);
                bytes = output.toBytes();
                output.flush();
            } catch (Exception ex) {
                throw new ObjectSerializerException("kryo serialize error" + ex.getMessage());
            } finally {
                try {
                    outputStream.flush();
                    outputStream.close();
                } catch (IOException e) {
                }
            }
            return bytes;
        }
        @Override
        public <T> T deSerialize(byte[] param, Class<T> clazz) throws ObjectSerializerException {
            T object;
            try (ByteArrayInputStream inputStream = new ByteArrayInputStream(param)) {
                Kryo kryo = new Kryo();
                Input input = new Input(inputStream);
                object = kryo.readObject(input, clazz);
                input.close();
            } catch (Exception e) {
                throw new ObjectSerializerException("kryo deSerialize error" + e.getMessage());
            }
            return object;
        }
        @Override
        public String getSchemeName() {
            return "kryoSerializer";
        }
    }
    ```
2. 实现二：Java原生的序列化方式

    ```Java
    public class JavaSerializer implements ObjectSerializer {
        @Override
        public byte[] serialize(Object obj) throws ObjectSerializerException {
            ByteArrayOutputStream arrayOutputStream;
            try {
                arrayOutputStream = new ByteArrayOutputStream();
                ObjectOutput objectOutput = new ObjectOutputStream(arrayOutputStream);
                objectOutput.writeObject(obj);
                objectOutput.flush();
                objectOutput.close();
            } catch (IOException e) {
                throw new ObjectSerializerException("JAVA serialize error " + e.getMessage());
            }
            return arrayOutputStream.toByteArray();
        }
        @Override
        public <T> T deSerialize(byte[] param, Class<T> clazz) throws ObjectSerializerException {
            ByteArrayInputStream arrayInputStream = new ByteArrayInputStream(param);
            try {
                ObjectInput input = new ObjectInputStream(arrayInputStream);
                return (T) input.readObject();
            } catch (IOException | ClassNotFoundException e) {
                throw new ObjectSerializerException("JAVA deSerialize error " + e.getMessage());
            }
        }
        @Override
        public String getSchemeName() {
            return "javaSerializer";
        }
    }
    ```
## 3. 增加META-INF目录文件
- Resource下面创建META-INF/services 目录里创建一个以服务接口命名的文件

    ![[IMG-20260620222732622.png|408]]

- 文件内容【接口的具体实现类名】

    ```Java
    com.blueskykong.javaspi.serializer.KryoSerializer
    com.blueskykong.javaspi.serializer.JavaSerializer
    ```
## 4. Service类
- 获取定义的序列化方式，且只取第一个（我们在配置中写了两个），如果找不到则返回Java原生序列化方式。
    ```Java
    @Service
    public class SerializerService {
        public ObjectSerializer getObjectSerializer() {
            ServiceLoader<ObjectSerializer> serializers = ServiceLoader.load(ObjectSerializer.class); ⭐⭐⭐
            final Optional<ObjectSerializer> serializer = StreamSupport.stream(serializers.spliterator(), false)
                    .findFirst();
            return serializer.orElse(new JavaSerializer());
        }
    }
    ```
## 5. 测试类
- 测试用例通过，且输出`kryoSerializer`
    ```Java
        @Autowired
        private SerializerService serializerService;
        @Test
        public void serializerTest() throws ObjectSerializerException {
            ObjectSerializer objectSerializer = serializerService.getObjectSerializer();
            System.out.println(objectSerializer.getSchemeName());
            byte[] arrays = objectSerializer.serialize(Arrays.asList("1", "2", "3"));
            ArrayList list = objectSerializer.deSerialize(arrays, ArrayList.class);
            Assert.assertArrayEquals(Arrays.asList("1", "2", "3").toArray(), list.toArray());
        }
    ```
# 四、ServiceLoader
- 上面例子中使用了 jdk 提供的 spi 能力，关键代码：==ServiceLoader.load(ObjectSerializer.class)==
- 下面详细解读下 **ServiceLoader 类的源码**
    - [https://segmentfault.com/a/1190000041020216](https://segmentfault.com/a/1190000041020216)

# 五、总结

其实不难发现，SPI 机制的具体实现本质上还是通过反射完成的。即：我们按照规定将要暴露对外使用的具体实现类在 `META-INF/services/` 文件下声明。

![[IMG-20260620222732667.png|673]]
