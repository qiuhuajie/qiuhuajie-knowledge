# MyBatis 介绍

# 1. **MyBatis 历史**

1. MyBatis最初是Apache的一个开源项目iBatis，2010年6月这个项目由Apache Software Foundation迁移到了Google Code。随着开发团队转投Google Code旗下， iBatis3.x正式更名为MyBatis。代码于2013年11月迁移到Github
2. iBatis一词来源于“internet”和“abatis”的组合，是一个基于Java的持久层框架。 iBatis提供的持久层框架包括SQL Maps和Data Access Objects（DAO）

# 2. **MyBatis 特性**

1. MyBatis 是支持定制化 SQL、存储过程以及高级映射的优秀的持久层框架（**对JDBC 进行了封装**）
2. MyBatis **避免**了几乎所有的 **JDBC 代码**和**手动设置参数（预编译拼接参数）**以及**获取结果集**
3. MyBatis可以使用简单的XML或注解用于配置和原始映射，将接口和Java的POJO（Plain Old Java Objects，普通的Java对象）映射成数据库中的记录
4. MyBatis 是一个 半自动的ORM（`Object Relation Mapping`）框架

    > JDBC ：自动 ，Hibernate：全自动
    >

# 3. **MyBatis 下载**

MyBatis下载地址：

[https://github.com/mybatis/mybatis-3](https://github.com/mybatis/mybatis-3)

# 4. **和其它持久化层技术对比**

1. **JDBC**
    1. **SQL 夹杂在Java代码中耦合度高**，导致硬编码内伤
    2. 维护不易且实际开发需求中 SQL 有变化，频繁修改的情况多见
    3. 代码冗长，开发效率低
2. **Hibernate 和 JPA**
    1. 操作简便，开发效率高
    2. 程序中的长难复杂 SQL 需要绕过框架
    3. **内部自动生产的 SQL，不容易做特殊优化**
    4. 基于全映射的全自动框架，大量字段的 POJO 进行部分映射时比较困难。
    5. 反射操作太多，导致数据库性能下降
3. **MyBatis**
    1. 轻量级，性能出色
    2. SQL 和 Java 编码分开，功能边界清晰（**Java代码专注业务、SQL语句专注数据**）
    3. 开发效率稍逊于HIbernate，但是完全能够接受