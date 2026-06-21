# 整合第三方缓存 EHCache

# 1. **EHCache 的使用**

1. 引入依赖

    ```xml
     <!-- Mybatis EHCache整合包 -->
     <dependency>
         <groupId>org.mybatis.caches</groupId>
         <artifactId>mybatis-ehcache</artifactId>
         <version>1.2.1</version>
     </dependency>
     
     <!-- slf4j日志门面的一个具体实现 -->
     <dependency>
         <groupId>ch.qos.logback</groupId>
         <artifactId>logback-classic</artifactId>
         <version>1.2.3</version>
     </dependency>
    ```

2. 创建EHCache的配置文件 **ehcache.xml**

    ```xml
     <?xml version="1.0" encoding="utf-8" ?>
     <ehcache xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:noNamespaceSchemaLocation="../config/ehcache.xsd">
         <!--🔴 磁盘保存路径 -->
         <diskStore path="D:\atguigu\ehcache"/>
    
         <!--🔴 自定义，service缓存配置 -->
         <defaultCache
                       maxElementsInMemory="1000"
                       maxElementsOnDisk="10000000"
                       eternal="false"
                       overflowToDisk="true"
                       timeToIdleSeconds="120"
                       timeToLiveSeconds="120"
                       diskExpiryThreadIntervalSeconds="120"
                       memoryStoreEvictionPolicy="LRU">
         </defaultCache>
     </ehcache>
    ```

    - `eternal`：缓存是否永远不销毁
    - `maxElementsInMemory`：缓存可以存储的总记录量
    - `overflowToDisk`：当缓存中的数据达到最大值时，是否把缓存数据写入磁盘
    - `diskPersistent`：否启用强制命令将缓存出入磁盘
    - `timeToIdleSeconds`：当缓存闲置时间超过该值，则缓存自动销毁，如果该值是0就意味着元素可以停顿无穷长的时间
    - `timeToLiveSeconds`：缓存数据的生存时间，也就是一个元素从构建到消亡的最大时间间隔值， 这只能在元素不是永久驻留时有效，如果该值是0就意味着元素可以停顿无穷长的时间
    - `memoryStoreEvictionPolicy`：缓存满了之后的淘汰算法
3. 设置二级缓存的类型

    ```xml
     <cache type="org.mybatis.caches.ehcache.EhcacheCache"/>
    ```

4. 加入logback日志：**存在SLF4J时，作为简易日志的log4j将失效**，此时我们需要借助SLF4J的具体实现logback来打印日志
5. 创建 logback 的配置文件 **logback.xml**

    ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <configuration debug="true">
         <!-- 指定日志输出的位置 -->
         <appender name="STDOUT"
                   class="ch.qos.logback.core.ConsoleAppender">
             <encoder>
                 <!-- 日志输出的格式 -->
                 <!-- 按照顺序分别是：时间、日志级别、线程名称、打印日志的类、日志主体内容、换行 -->
                 <pattern>
                     [%d{HH:mm:ss.SSS}] [%-5level] [%thread] [%logger] [%msg]%n
                 </pattern>
             </encoder>
         </appender>
    
         <!-- 设置全局日志级别。日志级别按顺序分别是：DEBUG、INFO、WARN、ERROR -->
         <!-- 指定任何一个日志级别都只打印当前级别和后面级别的日志。 -->
         <root level="DEBUG">
             <!-- 指定打印日志的appender，这里通过“STDOUT”引用了前面配置的appender -->
             <appender-ref ref="STDOUT" />
         </root>
         <!-- 根据特殊需求指定局部日志级别 -->
         <logger name="com.atguigu.crowd.mapper" level="DEBUG"/>
     </configuration>
    ```


# 2. 封装一个 **EHCache** 工具类

包含着插入元素和读取元素操作

```java
public class EncacheTemplete {

    private static CacheManager cacheManager;
    private static Ehcache fileCache;

    static {
        cacheManager = new CacheManager();
        fileCache = cacheManager.getCache("serviceCache");
    }

    public static <T> void put(String key, T value) {
        fileCache.put(new Element(key, value));
    }

    @SuppressWarnings("unchecked")
    public static <T> T get(String key) {
        Element el = fileCache.get(key);
        if (el == null) {
            System.out.println("not found key: " + key);
            return null;
        }

        T t = (T) el.getObjectValue();
        return t;
    }

    /**
     * 根据key删除缓存
     */
    public static boolean remove(String key) {
        System.out.println("remove key:" + key);
        return fileCache.remove(key);
    }

    /**
     * 关闭cacheManager 对象
     */
    public static void shutdown() {
        cacheManager.shutdown();
    }
}
```