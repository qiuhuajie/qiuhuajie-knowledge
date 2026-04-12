- [[#1. 创建 Maven 工程]]
- [[#2. MyBatis 全局配置文件]]
- [[#3. 创建 mapper 接口]]
- [[#4. 创建映射文件]]
- [[#5. 测试]]
- [[#4. 加入 log4j 日志]]
# 1. **创建 Maven 工程**
pom.xml
```XML
<!--设置打包方式为 jar-->
<packaging>jar</packaging>
<!--引入依赖-->
<dependencies>
    <!-- Mybatis核心 -->
    <dependency>
        <groupId>org.mybatis</groupId>
        <artifactId>mybatis</artifactId>
        <version>3.5.7</version>
    </dependency>
    <!-- junit测试 -->
    <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.12</version>
        <scope>test</scope>
    </dependency>
    <!-- MySQL驱动 -->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>5.1.3</version>
    </dependency>
</dependencies>
```
# 2. **MyBatis 全局配置文件**

> [!important] **整合Spring之后，这个配置文件可以省略**
1. 习惯上命名为 **mybatis-config.xml**，这个文件名仅仅只是建议，并非强制要求
1. 核心配置文件主要**用于配置连接数据库的环境以及MyBatis的全局配置信息**
1. 核心配置文件存放的位置是`src/main/resources`目录下
    
    ```XML
     <?xml version="1.0" encoding="UTF-8" ?>
     <!DOCTYPE configuration
             PUBLIC "-//MyBatis.org//DTD Config 3.0//EN"
             "http://MyBatis.org/dtd/MyBatis-3-config.dtd">
     <configuration>
    
         <!--⭐引入properties文件，此时就可以${属性名}的方式访问属性值-->
         <properties resource="mybatis.properties"></properties>
    
         <settings>
             <!--将表中字段的下划线自动转换为驼峰-->
             <setting name="mapUnderscoreToCamelCase" value="true"/>
             <!--开启延迟加载-->
             <setting name="lazyLoadingEnabled" value="true"/>
         </settings>
    
         <typeAliases>
             <!--
                 typeAlias：设置某个具体的类型的别名
                     属性：
                         type：需要设置别名的类型的全类名
                         alias：设置此类型的别名，若不设置此属性，该类型拥有默认的别名，即类名且不区分大小写，若设置此属性，此时该类型的别名只能使用alias所设置的值
             -->
             <!--<typeAlias type="com.atguigu.mybatis.bean.User"></typeAlias>-->
             <!--<typeAlias type="com.atguigu.mybatis.bean.User" alias="abc"></typeAlias>-->
    
             <!--以包为单位，设置改包下所有的类型都拥有默认的别名，即类名且不区分大小写-->
             <package name="com.atguigu.mybatis.bean"/>
         </typeAliases>
    
         <!--
                   environments：设置多个连接数据库的环境
                 属性：
                                 default：设置默认使用的环境的id
         -->
         <environments default="mysql_test">
             <!--
                 environment：设置具体的连接数据库的环境信息
                 属性：
                     id：设置环境的唯一标识，可通过environments标签中的default设置某一个环境的id，表示默认使用的环境
             -->
             <environment id="mysql_test">
                 <!--
                     transactionManager：设置事务管理方式
                         属性：
                             type：设置事务管理方式，type="JDBC|MANAGED"
                             type="JDBC"：设置当前环境的事务管理都必须手动处理
                             type="MANAGED"：设置事务被管理，例如spring中的AOP
                 -->
                 <transactionManager type="JDBC"/>
                 <!--
                     dataSource：设置数据源
                         属性：
                             type：设置数据源的类型，type="POOLED|UNPOOLED|JNDI"
                             type="POOLED"：使用数据库连接池，即会将创建的连接进行缓存，下次使用可以从
                             缓存中直接获取，不需要重新创建
                             type="UNPOOLED"：不使用数据库连接池，即每次使用连接都需要重新创建
                             type="JNDI"：调用上下文中的数据源
                 -->
                 <dataSource type="POOLED">
                     <!--设置驱动类的全类名-->
                     <property name="driver" value="${jdbc.driver}"/> ⭐
                     <!--设置连接数据库的连接地址-->
                     <property name="url" value="${jdbc.url}"/>
                     <!--设置连接数据库的用户名-->
                     <property name="username" value="${jdbc.username}"/>
                     <!--设置连接数据库的密码-->
                     <property name="password" value="${jdbc.password}"/>
                 </dataSource>
             </environment>
         </environments>
    
         <!--⭐引入映射文件-->
         <mappers>
             <mapper resource="UserMapper.xml"/>
             <!--
                 以包为单位，将包下所有的映射文件引入核心配置文件
                 注意：x此方式必须保证mapper接口和mapper映射文件必须在相同的包下
             -->
             <package name="com.atguigu.mybatis.mapper"/>
         </mappers>
     </configuration>
    ```
    
    > [!important]
    > 
    > `"http://mybatis.org/dtd/mybatis-3-config.dtd"` ：DTD（文档类型定义）的作用是定义 XML 文档的合法构建模块
    
# 3. **创建 mapper 接口**
1. MyBatis中的mapper接口相当于以前的`dao`
1. 但是区别在于，`mapper`仅仅是接口，**不需要提供实现类**
1. **MaBatis中由面向接口编程的功能，每当调用接口中的方法时，会自动匹配一个 SQL 语句，然后执行**
    
    ```Java
     public interface UserMapper {
         int insertUser();
     }
    ```
    
# 4. **创建映射文件**
1. 映射文件介绍
    
    1. 创建 Dao 的 **sql 映射文件 ，绑定**`**mapper**`**接口**
    
    1. 相关概念：==ORM（Object Relationship Mapping）对象关系映射==
        
        1. 对象：Java的实体类对象
        
        1. 关系：关系型数据库
        
        1. 映射：二者之间的对应关系
        
    
    1. **一个映射文件对应一个实体类，对应一张表的操作**
    
    1. MyBatis映射文件==用于编写SQL，访问以及操作表中的数据==
    
    1. MyBatis映射文件存放的位置是 `src/main/resources/mappers` 目录下
    
1. ⭐**映射文件中的需要遵循的规则**
    
    1. 映射文件的命名规则：
        
        1. 表所对应的**实体类的类名+Mapper.xml**
        
        1. 例如：表t_user，映射的实体类为User，所对应的映射文件为UserMapper.xml
        
    
    1. MyBatis中可以面向接口操作数据，要保证两个一致：
        
        1. **mapper接口的全类名** 和 **映射文件的命名空间**（namespace）保持一致
        
        1. **mapper接口中方法的方法名** 和 **映射文件中编写SQL的标签的id属性**保持一致
        
    
    ```XML
     <?xml version="1.0" encoding="UTF-8" ?>
     <!DOCTYPE mapper
             PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
             "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
     <mapper namespace="com.qhj.mapper.UserMapper">
         <!--int insertUser();-->
         <insert id="insertUser">
             insert into user values(100,'张三',23,'1234@qq.com')
         </insert>
     </mapper>
    ```
    
# 5. **测试**
```Java
public class MyBatisTest {
    @Test
    public void Test01() throws IOException {
        //读取 MyBatis 全局配置文件 mybatis-config.xml
        InputStream is = Resources.getResourceAsStream("mybatis-config.xml");
        //创建 SqlSessionFactoryBuilder 用来创建 SqlSessionFactory
        SqlSessionFactoryBuilder sqlSessionFactoryBuilder = new SqlSessionFactoryBuilder();
        //⭐通过全局配置文件所对应的 字节输入流 创建工厂类 SqlSessionFactory ，用来生产 SqlSession 对象
        SqlSessionFactory sqlSessionFactory = sqlSessionFactoryBuilder.build(is);
        //⭐创建 SqlSession 对象
        //当传入一个布尔参数 true 时 ---> 就不需要在最后对事务进行提交了：sqlSession.commit()
        SqlSession sqlSession = sqlSessionFactory.openSession(true);
        //⭐通过 代理模式 创建UserMapper接口的代理实现类对象
        UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
        //调用UserMapper接口中的方法，就可以根据UserMapper的全类名匹配元素文件
        //通过调用的方法名匹配sql映射文件中的sql标签，并执行标签中的SQL语句
        int result = userMapper.insertUser();
        
        System.out.println("结果" + result);//结果1
    }
}
```
1. **SqlSession**：代表**Java程序和数据库之间的会话**（HttpSession是Java程序和浏览器之间的会话）
1. **SqlSessionFactory**：是生产 SqlSession 的工厂
    
    > springBoot 底层自动配置了 SqlSessionFactory 组件
    
    ```Java
     ...
     @ConditionalOnClass({SqlSessionFactory.class, SqlSessionFactoryBean.class})
     ...
     public class MybatisAutoConfiguration implements InitializingBean {...}
    ```
    
1. **工厂模式**：如果创建某一个对象，使用的过程基本固定，那么我们就可以把创建这个对象的相关代码封装到一个“工厂类”中，以后都使用这个工厂类来“生产”我们需要的对象
1. 🔴通过 **代理模式** 创建 UserMapper 接口的代理实现类对象：
    
    - 由于 mapper 接口是没有实现类的，要想获得他的一个实现类对象，可以使用代理模式返回一个接口的实现类（即使该接口并没有实现类）
        
        ```Plain
         <T> T getMapper(Class<T> var1);
        ```
        
    
# 4. **加入 log4j 日志**
1. 引入依赖
    
    ```XML
     <dependency>
         <groupId>log4j</groupId>
         <artifactId>log4j</artifactId>
         <version>1.2.17</version>
     </dependency>
    ```
    
1. 在 resource 目录下添加配置文件：log4j.xml
    
    ```XML
     <?xml version="1.0" encoding="UTF-8" ?>
     <!DOCTYPE log4j:configuration SYSTEM "log4j.dtd">
     <log4j:configuration xmlns:log4j="http://jakarta.apache.org/log4j/">
         <appender name="STDOUT" class="org.apache.log4j.ConsoleAppender">
             <param name="Encoding" value="UTF-8" />
             <layout class="org.apache.log4j.PatternLayout">
                 <param name="ConversionPattern" value="%-5p %d{MM-dd HH:mm:ss,SSS}
     %m (%F:%L) \n" />
             </layout>
         </appender>
         <logger name="java.sql">
             <level value="debug" />
         </logger>
         <logger name="org.apache.ibatis">
             <level value="info" />
         </logger>
         <root>
             <level value="debug" />
             <appender-ref ref="STDOUT" />
         </root>
     </log4j:configuration>
    ```
    
    > [!important] 日志级别：
    > 
    > 1. `FATAL`(致命)>`ERROR`(错误)>`WARN`(警告)>`INFO`(信息)>`DEBUG`(调试)
    > 
    > 1. 从左到右打印的内容越来越详细
    
1. 再次执行 测试方法：
    
    ![[IMG-20260405035413787.png|Untitled 356.png]]