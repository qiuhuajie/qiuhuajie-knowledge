- [[#1. 二级缓存概述]]
- [[#2. 二级缓存原理]]
- [[#3. 二级缓存查询的顺序]]
- [[#4. 二级缓存配置]]
# 1. **二级缓存概述**
1. MyBatis的二级缓存相对于一级缓存来说，**实现了**`SqlSession`**之间缓存数据的共享**，同时粒度更加的细，能够到 `namespace` 级别，通过`Cache`接口实现类不同的组合，对`Cache`的可控性也更强
1. ==**不推荐使用：**==
    
    1. MyBatis 在多表查询时，极大可能会出现脏数据，有设计上的缺陷，**安全使用二级缓存的条件比较苛刻**
    
    1. **在分布式环境下**
        
        1. 由于默认的MyBatis Cache实现都是基于本地的，分布式环境下必然会出现读取到脏数据，需要使用集中式缓存将 MyBatis的Cache 接口实现，有一定的开发成本
        
        1. 直接使用 Redis、Memcached 等分布式缓存可能成本更低，安全性也更高
        
    
# 2. **二级缓存原理**
1. 一级缓存最大的共享范围就是一个 `SqlSession` 内部，如果多个 `SqlSession` 之间需要共享缓存，则需要使用到二级缓存
1. 开启二级缓存后，会使用 `CachingExecutor` 装饰 `Executor`
1. 二级缓存开启后，**同一个 `namespace`下的所有操作语句，都影响着同一个 `Cache`**
    
    ![[Attachment/1question/大数据/Java 开发/MyBatis/MyBatis 原理/MyBatis 缓存/IMG-20260405035413932.png|Untitled 512.png]]
    
1. **二级缓存被同一个 `namespace` 下的多个 `SqlSession` 共享，是一个全局的变量**
1. 每个 Mapper 映射文件只能配置一个 namespace，用来做 Mapper 文件级别的缓存共享
    
    ```XML
    <mapper namespace="mapper.StudentMapper"></mapper>
    ```
    
    > [!important] **MyBatis 的二级缓存不适应用于映射文件中存在多表查询的情况⭐**
    > 
    > - 通常我们会为每个单表创建单独的映射文件，由于MyBatis的二级缓存是基于`namespace`的
    > 
    > - **多表查询语句所在的`namspace`无法感应到其他`namespace`中的语句对多表查询中涉及的表进行的修改，从而会引发脏数据问题**
    
# 3. 二级**缓存查询的顺序**
![[IMG-20260404031808987.png|Untitled 1 379.png]]
1. **进入一级缓存的查询流程前，先在** `CachingExecutor` **进行二级缓存的查询**
    
    1. **如果二级缓存没有命中，再查询一级缓存**
    
    1. 如果一级缓存也没有命中，则查询数据库
    
1. **SqlSession 关闭之后，一级缓存中的数据会写入二级缓存**
# 4. **二级缓存配置**
1. **全局所有的mapper都开启二级缓存：**开启二级缓存需要在 mybatis-config.xml 中配置
    
    ```XML
    <settingname="cacheEnabled" value="true"/>
    ```
    
1. **单个mapper开启二级缓存：**在 mapper 配置文件中添加的 cache 标签可以设置一些属性：
    
    ![[IMG-20260404031809061.png|Untitled 2 309.png]]
    
    - `**eviction**`**属性**：缓存回收策略，默认的是 LRU
        
        1. `LRU（Least Recently Used）` – 最近最少使用的：移除最长时间不被使用的对象
        
        1. `FIFO（First in First out）` – 先进先出：按对象进入缓存的顺序来移除它们
        
        1. `SOFT – 软引用`：移除基于垃圾回收器状态和软引用规则的对象[[3.2 Java 中的 4 种引用]]
        
        1. `WEAK – 弱引用`：更积极地移除基于垃圾收集器状态和弱引用规则的对象
        
    
    - `**flushInterval**`**属性**：刷新间隔，单位毫秒，默认情况是不设置，也就是没有刷新间隔，缓存仅仅调用语句时刷新
    
    1. `**size**`**属性**：引用数目，正整数代表缓存最多可以存储多少个对象，太大容易导致内存溢出
    
    1. `**readOnly**`**属性**：只读，true/false（默认是false）
        
        1. true：只读缓存；会给所有调用者返回缓存对象的相同实例。因此这些对象不能被修改。这提供了很重要的性能优势。
        
        1. false：读写缓存；**会返回缓存对象的拷贝（通过序列化）**。这会慢一些，但是安全，因此默认是false