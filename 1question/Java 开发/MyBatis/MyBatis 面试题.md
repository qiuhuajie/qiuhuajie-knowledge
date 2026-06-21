# MyBatis 面试题

## 介绍一下 MyBatis 中的 ${} 和 #{} 🙋‍♂️

1. 在 MyBatis 中，${} 和 #{} 都是用于参数占位符的符号，用于动态生成 SQL 语句中的参数
2. 这两种占位符的使用有些不同：
    1. **`${}`：字符串替换占位符**

        ```sql
         select * from user where name = '${name}'
        ```

        1. 使用 ${} 将参数直接替换成为 SQL 语句中的字符串，不会对参数进行任何处理或转义
        2. 在使用 ${} 时，参数不会被转义，需要注意 SQL 注入的问题
    2. **`#{}`：预编译处理占位符**

        ```sql
         select * from user where name = #{name}
        ```

        1. 使用 #{} 时，MyBatis 会将参数先进行预编译处理，再将预处理后的参数值放入 SQL 语句中
        2. 预编译处理的好处：
            1. **提高代码的可读性和可维护性**
            2. 可以处理**参数类型转换**的问题：会根据参数类型自动将参数转换为合适的 SQL 类型，Integer ➡️ SQL 的整型
            3. **可以防止 SQL 注入问题：**MyBatis 会对字符串参数进行转义，"O'Reilly" ➡️ "O''Reilly"
                - 示例
                    1. 如果有人将 特地设计的恶意字符串传进来，会造成安全风险
                    2. 例如：

                        ```java
                         String sql = “select * from tb_name where name= ‘”+varname+”’ and passwd=’”+varpasswd+”’”;
                        ```

                        如果此时 varpasswd 传进来的是：`任意值’ or ‘1’ = ‘1’`，和sql 语句拼接后会变成：

                        ```java
                         select * from tb_name = ‘任意值’ and passwd = ‘任意值’ or ‘1’ = ‘1’;
                        ```

                        这样输入任意密码，都能登陆成功！如果是加上删除数据库、表的语句呢？！

## 二级缓存，以及默认关闭的原因🙋‍♂️

1. 一级缓存最大的共享范围就是一个 `SqlSession` 内部，如果多个 `SqlSession` 之间需要共享缓存，则需要使用到二级缓存
2. 二级缓存**实现了**`SqlSession`**之间缓存数据的共享**，也即二级缓存开启后，**同一个 `namespace`下的所有操作语句，都影响着同一个 `Cache`**
3. 关闭的原因：
    1. 多表查询下，很大可能出现脏数据
    2. 分布式环境下，基于本地的 MyBatis 缓存存在数据不一致的问题，使用 Redis 等分布式缓存成本更低，安全性也更好

## **Mapper 接口实现类代理对象的获取**🙋‍♂️

[详见 Mapper 接口实现类代理对象的获取](MyBatis%20%E5%8E%9F%E7%90%86/Mapper%20%E6%8E%A5%E5%8F%A3%E5%AE%9E%E7%8E%B0%E7%B1%BB%E4%BB%A3%E7%90%86%E5%AF%B9%E8%B1%A1%E7%9A%84%E8%8E%B7%E5%8F%96%20158759569ea04b0fa7a11e5ba5d4c852.md)

## Mybatis 框架中有哪些类

1. **`SqlSession`**：SqlSession 是 MyBatis 的核心类之一，它**负责管理数据库连接，提供了执行 SQL 语句、获取 Mapper 接口实例等方法**
2. **`Configuration`**：Configuration 类用于**配置 MyBatis 的全局参数**，如数据库连接信息、类型别名、插件等
3. **`SqlSessionFactory`**：SqlSessionFactory 是创建 SqlSession 对象的工厂，它可以通过 Configuration 对象来构建
4. **`Mapper`**：Mapper 接口定义了操作数据库的方法，MyBatis 会自动为这些方法生成对应的 SQL 语句并执行
5. **`ResultMap`**：ResultMap 是 MyBatis 中的一个重要概念，它用于**将数据库查询结果映射到 Java 对象上**
6. **`Executor`**：Executor **负责执行 SQL 语句，并将结果映射到 Java 对象上**。MyBatis 中提供了多种 Executor 实现，包括 SimpleExecutor、ReuseExecutor 和 BatchExecutor
7. **`TypeHandler`**：TypeHandler 用于处理 Java 类型与数据库类型之间的转换，MyBatis 中提供了一些默认的 TypeHandler 实现，也可以自定义实现
8. **`ParameterHandler`**：ParameterHandler 用于将 Java 对象转换为 SQL 语句中的参数，MyBatis 中提供了默认实现

## Mybatis **连接池**

1. MyBatis 是一个**支持连接池**的数据库持久层框架，它可以通过配置数据源和连接池来自动管理数据库连接的创建、复用和释放，从而提高系统的性能和可靠性
    1. 具体来说，MyBatis 会**为每个线程分配一个 SqlSession 对象，该对象中包含一个 Connection 对象和一个 Transaction 对象**
    2. 当线程需要执行数据库操作时，它会**从 SqlSession 中获取 Connection 对象，并使用该对象执行操作**
    3. 在操作完成后，线程会**将 Connection 对象返回给 SqlSession**
    4. 然后 SqlSession 会**将 Connection 对象放回连接池中**，以便其他线程可以使用它
2. 通过这种方式，MyBatis 可以确保每个线程都有自己的 Connection 对象，并且在操作完成后将其返回给连接池，从而避免了连接泄漏和线程安全问题。

## **Mybatis 工作原理**

![Untitled](IMG-20260621001354339.png)

1. **读取 MyBatis 全局配置文件**
    - **`mybatis-config.xml`** 为 MyBatis 的全局配置文件
    - 包含了 MyBatis 行为的设置和属性信息，例如数据库连接信息和映射文件
2. **加载映射文件 `mapper.xml`**
    - 映射文件即 SQL 映射文件，该文件中配置了操作数据库的 SQL 语句，需要在 MyBatis 配置文件 mybatis-config.xml 中加载
    - mybatis-config.xml 文件可以加载多个映射文件，每个文件对应数据库中的一张表
3. **构造会话工厂 SqlSessionFactory**
    - 通过 MyBatis 的环境等配置信息构建会话工厂 SqlSessionFactory
4. **创建会话对象 SqlSession**
    - 由会话工厂创建 SqlSession 对象，该对象中包含了执行 SQL 语句的所有方法
5. **Executor 执行器**
    - MyBatis 底层定义了一个 Executor 接口来操作数据库
    - 它将根据 SqlSession 传递的参数动态地生成需要执行的 SQL 语句，同时负责查询缓存的维护
6. **MappedStatement 对象**
    - 在 Executor 接口的执行方法中有一个 MappedStatement 类型的参数
    - 该参数是对映射信息的封装，用于存储要映射的 SQL 语句的 id、参数等信息
7. **输入参数映射**
    - 输入参数类型可以是 Map、List 等集合类型，也可以是基本数据类型和 POJO 类型
    - 输入参数映射过程类似于 JDBC 对 preparedStatement 对象设置参数的过程
8. **输出结果映射**
    - 输出结果类型可以是 Map、 List 等集合类型，也可以是基本数据类型和 POJO 类型
    - 输出结果映射过程类似于 JDBC 对结果集的解析过程

## MyBatis 填充 SQL 参数值的两种方式

[（详见 MyBatis 填充 SQL 参数值的两种方式）](MyBatis%20%E4%BD%BF%E7%94%A8/Mapper%20%E6%98%A0%E5%B0%84%E6%96%87%E4%BB%B6%E8%8E%B7%E5%8F%96%E5%8F%82%E6%95%B0/MyBatis%20%E5%A1%AB%E5%85%85%20SQL%20%E5%8F%82%E6%95%B0%E5%80%BC%E7%9A%84%E4%B8%A4%E7%A7%8D%E6%96%B9%E5%BC%8F%209e98485aa85844adb7fb49f733e8773d.md)

## Xml 映射文件中的标签

MyBatis 的 XML 映射文件是描述 SQL 语句和映射关系的重要组成部分，其中包含了许多标签用于实现映射、参数绑定、结果集处理等功能。以下是常用的一些标签：

1. **`<select>`**：用于执行查询操作，包括查询参数绑定、结果集映射等。
2. **`<insert>`**：用于执行插入操作，包括插入参数绑定和自动生成主键等。
3. **`<update>`**：用于执行更新操作，包括更新参数绑定和更新条件等。
4. **`<delete>`**：用于执行删除操作，包括删除条件绑定等。
5. **`<parameterMap>`**：用于定义参数映射关系，可以为 SQL 语句中的参数命名或设置类型等信息。
6. **`<resultMap>`**：用于定义结果集映射关系，可以将查询结果映射为 Java 对象或基本类型。
7. **`<sql>`**：用于定义可重用的 SQL 片段，可以在其他 SQL 语句中引用。
8. **`<include>`**：用于引用其他 SQL 片段，可以将 **`<sql>`** 中定义的 SQL 片段插入到当前 SQL 语句中
9. 动态 SQL：**`<if>`** 、**`<choose>`** 、**`<trim>`** 、**`<where>`** 、**`<forEach>`**

## **为什么说 Mybatis 是半自动 ORM 映射工具？它与全自动的区别在哪里？**

1. ORM（Object Relational Mapping），对象关系映射，是一种为了**解决 关系型数据库数据 与 简单Java对象（POJO）的映射关系**的技术
2. Hibernate属于全自动ORM映射工具，使用Hibernate查询关联对象或者关联集合对象时，可以根据对象关系模型直接获取，所以它是全自动的
3. **Mybatis在查询关联对象或关联集合对象时，需要手动编写 sql 来完成，所以，称之为半自动ORM映射工具**

## **JDBC 编程有哪些不足之处，MyBatis 是如何解决这些问题的？**

1. 在 JDBC 连接数据库时，则必须按照以下几步完成：
    - 通过 `Class.forName()` 加载数据库的驱动程序 （通过[反射](../Java/%E5%8F%8D%E5%B0%84%20c688a15a980943f886b1496b3f29ba44.md)加载）
    - 通过 `DriverManager` 类连接数据库，参数包含数据库的连接地址、用户名、密码
    - 通过 `Connection` 接口接收连接
    - 关闭连接

    ![Untitled](IMG-20260621001354436.png)

2. **JDBC 编程有哪些不足之处**
    1. **频繁创建、释放数据库连接对象**，容易造成系统资源浪费，影响系统性能。解决：**在`mybatis-config.xml`中配置数据库连接池，使用连接池管理数据库连接**
    2. **Sql语句写在代码中造成代码不易维护**，实际应用sql变化的可能较大，sql变动需要改变java代码。解决：**将Sql语句配置在`XXXXmapper.xml`文件中，与java代码分离**
    3. **向Sql语句传参数麻烦**，因为sql语句的where条件不一定，可能多也可能少，占位符需要和参数一一对应。解决：**Mybatis自动将java对象映射至sql语句**
    4. **对结果集解析麻烦**，sql变化导致解析代码变化，且解析前需要遍历，如果能将数据库记录封装成pojo对象解析比较方便。解决：**Mybatis自动将sql执行结果映射至java对象**

## **模糊查询 like**

[（详见 特殊 SQL）](MyBatis%20%E4%BD%BF%E7%94%A8/%E7%89%B9%E6%AE%8A%20SQL%2025073e452be04d399deaf1feac8cfa2b.md)

## **动态 SQL**

[（详见 动态 SQL）](MyBatis%20%E4%BD%BF%E7%94%A8/%E5%8A%A8%E6%80%81%20SQL%201ca2709950534dcdb441f89c922c1e3c.md)

## **使用 MyBatis 的 Mapper 接口调用时有哪些要求？**

- Mapper.xml 文件中的 namespace 即是 mapper 接口的全限定类名

    ![Untitled](IMG-20260621001354530.png)

- Mapper 接口方法名和 mapper.xml 中定义的 sql 语句 id一一对应

    ![Untitled](IMG-20260621001354629.png)

    ![Untitled](IMG-20260621001354718.png)

- Mapper 接口方法的输入参数类型和 mapper.xml 中定义的每个 sql 语句的 parameterType 的类型相同
- Mapper 接口方法的输出参数类型和 mapper.xml 中定义的每个 sql 语句的 resultType 的类型相同

## Mabatis 一级、二级缓存

[（详见 Mabatis 缓存）](MyBatis%20%E5%8E%9F%E7%90%86/MyBatis%20%E7%BC%93%E5%AD%98%20a699788c3eb2497588a51958f39f9684.md)