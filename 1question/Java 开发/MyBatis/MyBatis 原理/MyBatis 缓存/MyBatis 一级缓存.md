# MyBatis 一级缓存

<aside>
📌 **MyBatis 缓存中的常用概念**

- **MyBatis 缓存**：它用来优化 SQL 数据库查询的，但是可能会产生脏数据
- **SqlSession**：代表和数据库的一次会话，向用户提供了操作数据库的方法
- **MappedStatement**：代表要发往数据库执行的指令，可以理解为是 SQL 的抽象表示
- **Executor**：代表用来和数据库交互的执行器，接受 MappedStatment 作为参数
- **namespace**：每个 Mapper 文件只能配置一个 namespace，用来做 Mapper 文件级别的缓存共享
- **映射接口**：定义了一个接口，然后里面的接口方法对应要执行 SQL 的操作，具体要执行的 SQL 语句是写在映射文件中
- **映射文件**：MyBatis 编写的 XML 文件，里面有一个或多个 SQL 语句，不同的语句用来映射不同的接口方法。通常来说，每一张单表都对应着一个映射文件
</aside>

# 1. **一级缓存原理⭐**

1. 在一次 `SqlSession`（数据库会话）中，如果程序执行多次查询，且**查询条件完全相同**，**多次查询之间程序没有其他增删改操作**，则第二次及后面的查询可以从缓存中获取数据，避免走数据库

    ![[IMG-20260621001304215.png|455]]

    1. 每个`SqlSession`中持有了`Executor`，每个`Executor`中有一个**`LocalCache`**
    2. 当用户发起查询时，MyBatis根据当前执行的语句生成 `MappedStatement`，在**`Local Cache`**进行查询
    3. 如果缓存命中的话，直接返回结果给用户
    4. 如果缓存没有命中的话，查询数据库，结果写入**`Local Cache`**，最后返回结果给用户
2. **`Local Cache`** 其实是一个 HashMap 的结构

    ```java
    private Map<Object, Object> cache = new HashMap<Object, Object>();
    ```

    - MyBatis一级缓存内部设计简单，只是一个没有容量限定的 HashMap，在缓存的功能性上有所欠缺
    - **HashMap 的 `Key` 由 SQL 语句组成，`Value` 是 Sql 查询结果**

        ```java
        Statement Id + Offset + Limmit + Sql + Params
        ```

    - 如下图所示，有两个 SqlSession，分别为 `SqlSession 01` 和 `SqlSession 02`，每个 SqlSession 中都有自己的缓存，缓存是 HashMap 结构，存放的键值对

        ![Untitled](IMG-20260621001304357.png)

# 2. **一级缓存配置**

在 mybatis-config.xml 文件配置，`name=localCacheScope`，value有两种值：`SESSION`和 `STATEMENT`

- `SESSION`：开启一级缓存功能
- `STATEMENT`：缓存只对当前执行的这一个 SQL 语句有效，也就是没有用到一级缓存功能

```xml
<configuration>
    <settings>
        <setting name="localCacheScope" value="SESSION"/>
    </settings>
<configuration>
```

<aside>
❓

- MyBatis的一级缓存最大范围是`SqlSession`内部，有多个`SqlSession`或者分布式的环境下，数据库写操作会引起脏数据，建议设定缓存级别为`Statement`
- 一级缓存的配置中，默认是 `SESSION`级别，即在一个MyBatis会话中执行的所有语句，都会共享这一个缓存
</aside>

# 3. **一级缓存代码示例**

1. 使用同一个 sqlSession 测试：

    ```java
     InputStream is = Resources.getResourceAsStream("mybatis-config.xml");
     SqlSessionFactoryBuilder sqlSessionFactoryBuilder = new SqlSessionFactoryBuilder();
     SqlSessionFactory sqlSessionFactory = sqlSessionFactoryBuilder.build(is);
     
     SqlSession sqlSession = sqlSessionFactory.openSession(true);
     //使用同一个 sqlSession：
     DeptMapper deptMapper1 = sqlSession.getMapper(DeptMapper.class);
     Dept dept1 = deptMapper1.getDeptByStep("c");
     System.out.println(dept1);
     DeptMapper deptMapper2 = sqlSession.getMapper(DeptMapper.class);
     Dept dept2 = deptMapper2.getDeptByStep("c");
     System.out.println(dept2);
    ```

    ![Untitled](IMG-20260621001304453.png)

2. 使用不同的 sqlSession 测试：

    ```java
     //创建 sqlSession1
     SqlSession sqlSession1 = sqlSessionFactory.openSession(true);
     DeptMapper deptMapper1 = sqlSession1.getMapper(DeptMapper.class);
     Dept dept1 = deptMapper1.getDeptByStep("c");
     System.out.println(dept1);
     
     //创建 sqlSession2
     SqlSession sqlSession2 = sqlSessionFactory.openSession(true);
     DeptMapper deptMapper2 = sqlSession2.getMapper(DeptMapper.class);
     Dept dept2 = deptMapper2.getDeptByStep("c");
     System.out.println(dept2);
    ```

    ![Untitled](IMG-20260621001304545.png)

# 4. **一级缓存失效的场景**

1. 不同的SqlSession对应不同的一级缓存
2. 同一个SqlSession但是查询条件不同
3. 同一个SqlSession两次查询期间执行了任何一次增删改操作（此时数据库里的数据已经发生了变化）
4. 同一个SqlSession两次查询期间手动清空了缓存

    ```java
    sqlSession.clearCache();
    ```