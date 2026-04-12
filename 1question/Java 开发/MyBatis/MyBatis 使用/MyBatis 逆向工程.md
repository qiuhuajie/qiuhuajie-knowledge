# 1. 介绍
1. **正向工程：**先创建Java实体类，由框架负责根据实体类生成数据库表。Hibernate是支持正向工程的
1. **逆向工程：**先创建数据库表，由框架负责**根据数据库表，反向生成如下资源**：
    
    1. Java实体类
    
    1. Mapper接口
    
    1. Mapper映射文件
    
# 2. **创建逆向工程**
1. 添加依赖和插件
    
    ```XML
    <!-- 依赖MyBatis核心包 -->
    <dependencies>
        <dependency>
            <groupId>org.mybatis</groupId>
            <artifactId>mybatis</artifactId>
            <version>3.5.7</version>
        </dependency>
    </dependencies>
    
    <!-- 控制Maven在构建过程中相关配置 -->
    <build>
        <!-- 构建过程中用到的插件 -->
        <plugins>
            <!-- 具体插件，逆向工程的操作是以构建过程中插件形式出现的 -->
            <plugin>
                <groupId>org.mybatis.generator</groupId>
                <artifactId>mybatis-generator-maven-plugin</artifactId>
                <version>1.3.0</version>
                <!-- 插件的依赖 -->
                <dependencies>
                    <!-- 逆向工程的核心依赖 -->
                    <dependency>
                        <groupId>org.mybatis.generator</groupId>
                        <artifactId>mybatis-generator-core</artifactId>
                        <version>1.3.2</version>
                    </dependency>
                    <!-- 数据库连接池 -->
                    <dependency>
                        <groupId>com.mchange</groupId>
                        <artifactId>c3p0</artifactId>
                        <version>0.9.2</version>
                    </dependency>
                    <!-- MySQL驱动 -->
                    <dependency>
                        <groupId>mysql</groupId>
                        <artifactId>mysql-connector-java</artifactId>
                        <version>5.1.8</version>
                    </dependency>
                </dependencies>
            </plugin>
        </plugins>
    </build>
    ```
    
1. 创建MyBatis的核心配置文件
1. 创建逆向工程的配置文件
    
    ==文件名必须是：====**generatorConfig.xml**==
    
    > 本例中是：`MyBatis3Simple`: 生成基本的CRUD（清新简洁版）
    
    ```XML
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE generatorConfiguration 
    PUBLIC "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN"
    "http://mybatis.org/dtd/mybatis-generator-config_1_0.dtd">
    <generatorConfiguration>
        <!--
            targetRuntime: 执行生成的逆向工程的版本
            MyBatis3Simple: 生成基本的CRUD（清新简洁版）
            MyBatis3: 生成带条件的CRUD（奢华尊享版）
        -->
        <context id="DB2Tables" targetRuntime="MyBatis3Simple">
            
            <!-- 数据库的连接信息 -->
            <jdbcConnection driverClass="com.mysql.jdbc.Driver"
                            connectionURL="jdbc:mysql://localhost:3306/userdb"
                            userId="root"
                            password="ZXT774276296qq..">
            </jdbcConnection>
            
            <!-- javaBean的生成策略-->
            <javaModelGenerator targetPackage="com.atguigu.mybatis.bean"
                                targetProject=".\src\main\java">
                <property name="enableSubPackages" value="true" />
                <property name="trimStrings" value="true" />
            </javaModelGenerator>
            
            <!-- SQL映射文件的生成策略 -->
            <sqlMapGenerator targetPackage="com.atguigu.mybatis.mapper"
                             targetProject=".\src\main\resources">
                <property name="enableSubPackages" value="true" />
            </sqlMapGenerator>
            
            <!-- Mapper接口的生成策略 -->
            <javaClientGenerator type="XMLMAPPER"
                                 targetPackage="com.atguigu.mybatis.mapper" targetProject=".\src\main\java">
                <property name="enableSubPackages" value="true" />
            </javaClientGenerator>
            
            <!-- 逆向分析的表 -->
            <!-- tableName设置为*号，可以对应所有表，此时不写domainObjectName -->
            <!-- domainObjectName属性指定生成出来的实体类的类名 -->
            <table tableName="t_emp" domainObjectName="Emp"/>
            <table tableName="t_dept" domainObjectName="Dept"/>
        </context>
    </generatorConfiguration>
    ```
    
1. 执行 MBG 插件的 generate
    
    ![[Attachment/1question/大数据/Java 开发/MyBatis/MyBatis 使用/IMG-20260405035413786.png|Untitled 357.png]]
    
1. 自动生成的目录结构：
    
    ![[IMG-20260404031807813.png|Untitled 1 268.png]]
    
# 2. Query By Criteria（**QBC） 查询**

> [!important] 前提：需要是
> 
> `MyBatis3`: **生成带条件的 CRUD**（奢华尊享版）
> 
> 1. 需要注意的几点：
>     
>     1. 在先生成了 简洁版的后，想在使用豪华版，需要将之前生成的文件目录全部删除，在执行生成豪华版 才会更新代码
>     
>     1. 在逆向生成的目录文件中 sql 映射文件是写在 `resource` 下的 `com/atguigu/mybatis/mapper/DeptMapper.xml` 中的，所以 mybatis 全局配置文件中的 sql 映射文件位置也要改
>     
> 
> 1. 豪华版生成的目录结构：
>     
>     ![[IMG-20260405035420134.png|Untitled 2 224.png]]
>     
使用HQL 查询需要写 hql 语句，但使用 QBC 查询不需要写语句，直接使用方法实现
```Java
@Test
public void test() throws IOException {
    InputStream is = Resources.getResourceAsStream("mybatis-config.xml");
    SqlSessionFactoryBuilder sqlSessionFactoryBuilder = new SqlSessionFactoryBuilder();
    SqlSessionFactory sqlSessionFactory = sqlSessionFactoryBuilder.build(is);
    SqlSession sqlSession = sqlSessionFactory.openSession(true);
    EmpMapper mapper = sqlSession.getMapper(EmpMapper.class);
    //new 一个 提供 ⭐条件操作 的实体类对象
    EmpExample empExample = new EmpExample();
    //创建 ⭐条件对象 Criteria，通过andXXX方法为SQL添加查询添加，每个条件之间是and关系
    empExample.createCriteria().andEmpNameLike("a").andAgeGreaterThan(20).andEidIsNotNull();
    //将之前添加的条件通过or拼接其他条件
    empExample.or().andDeptEqualTo("c");
    List<Emp> emps = mapper.selectByExample(empExample);
    for (Emp emp : emps) {
        System.out.println(emp);
    }
}
```

> [!important] mapper 接口中的方法，只要是有 example 就是 根据条件来操作
> 
> ![[IMG-20260405035421962.png|Untitled 3 172.png]]