- [[#Maven 安装]]
- [[#Maven 命令]]
- [[#maven 中跳过单元测试]]
- [[#父 POM 和 子 POM]]
- [[#Maven 中的 DependencyManagement 和 Dependencies]]
# Maven 安装
> [!info] Maven安装与配置_mvn version-CSDN博客
> 文章浏览阅读10w+次，点赞683次，收藏2.
> [https://blog.csdn.net/qq_38190185/article/details/115921070?ops_request_misc=%7B%22request%5Fid%22%3A%22171257460416800227456204%22%2C%22scm%22%3A%2220140713.130102334..%22%7D&request_id=171257460416800227456204&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-115921070-null-null.142^v100^control&utm_term=maven安装与配置&spm=1018.2226.3001.4187](https://blog.csdn.net/qq_38190185/article/details/115921070?ops_request_misc=%7B%22request%5Fid%22%3A%22171257460416800227456204%22%2C%22scm%22%3A%2220140713.130102334..%22%7D&request_id=171257460416800227456204&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-115921070-null-null.142^v100^control&utm_term=maven安装与配置&spm=1018.2226.3001.4187)
# **Maven 命令**
1. `**clean install**`
    1. `clean`：执行清理删除已有target目录
    2. `install`：把打包生成的 jar 包和 pom文件安装到本地的仓库中

        `"F:\MavenRepository\com\atguigu\springcloud\cloud-api-commons\1.0-SNAPSHOT\cloud-api-commons-1.0-SNAPSHOT.jar"`

        ![[IMG-20260404032014216.png|Untitled 24.png]]

2. `mvn clean package -DskipTests=true`
# **maven 中跳过单元测试**
1. 方法一：引入依赖

    ```XML
    <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <configuration>
            <skip>true</skip>
        </configuration>
    </plugin>
    ```
2. 方法二：IDEA工具支持（推荐）

    ![[IMG-20260404032014274.png|Untitled 1 5.png]]

# 父 POM 和 子 POM
1. 父 POM
    > [!important] **父工程创建完成执行**
    > 
    > `**mvn clean & install**` **将父工程发布到仓库方便子工程继承**
    - 查看全部内容

        ```XML
        <?xml version="1.0" encoding="UTF-8"?>
        <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
          <modelVersion>4.0.0</modelVersion>
          <groupId>com.atguigu.springcloud</groupId>
          <artifactId>springCloudProject</artifactId>
          <version>1.0-SNAPSHOT</version>
          <modules>
            <module>cloud-provider-payment-8001</module>
          </modules>
          <packaging>pom</packaging>
          <!-- 统一管理jar包版本 -->
          <properties>
            <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
            <maven.compiler.source>1.8</maven.compiler.source>
            <maven.compiler.target>1.8</maven.compiler.target>
            <junit.version>4.12</junit.version>
            <log4j.version>1.2.17</log4j.version>
            <lombok.version>1.16.18</lombok.version>
            <mysql.version>5.1.47</mysql.version>
            <druid.version>1.1.16</druid.version>
            <mybatis.spring.boot.version>1.3.0</mybatis.spring.boot.version>
          </properties>
          <!-- 子模块继承之后，提供作用：锁定版本+子modlue不用写groupId和version  -->
          <dependencyManagement>
            <dependencies>
              <!--spring boot 2.2.2-->
              <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>2.2.2.RELEASE</version>
                <type>pom</type>
                <scope>import</scope>
              </dependency>
              <!--spring cloud Hoxton.SR1-->
              <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>Hoxton.SR1</version>
                <type>pom</type>
                <scope>import</scope>
              </dependency>
              <!--spring cloud alibaba 2.1.0.RELEASE-->
              <dependency>
                <groupId>com.alibaba.cloud</groupId>
                <artifactId>spring-cloud-alibaba-dependencies</artifactId>
                <version>2.1.0.RELEASE</version>
                <type>pom</type>
                <scope>import</scope>
              </dependency>
              <dependency>
                <groupId>mysql</groupId>
                <artifactId>mysql-connector-java</artifactId>
                <version>${mysql.version}</version>
              </dependency>
              <dependency>
                <groupId>com.alibaba</groupId>
                <artifactId>druid</artifactId>
                <version>${druid.version}</version>
              </dependency>
              <dependency>
                <groupId>org.mybatis.spring.boot</groupId>
                <artifactId>mybatis-spring-boot-starter</artifactId>
                <version>${mybatis.spring.boot.version}</version>
              </dependency>
              <dependency>
                <groupId>junit</groupId>
                <artifactId>junit</artifactId>
                <version>${junit.version}</version>
              </dependency>
              <dependency>
                <groupId>log4j</groupId>
                <artifactId>log4j</artifactId>
                <version>${log4j.version}</version>
              </dependency>
              <dependency>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <version>${lombok.version}</version>
                <optional>true</optional>
              </dependency>
            </dependencies>
          </dependencyManagement>
          <build>
            <plugins>
              <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                  <excludes>
                    <exclude>
                      <groupId>org.projectlombok</groupId>
                      <artifactId>lombok</artifactId>
                    </exclude>
                  </excludes>
                </configuration>
              </plugin>
            </plugins>
          </build>
        </project>
        ```
2. 子 POM
    1. 子模块创建完后，父工程的 pom.xml 文件中：

        ```XML
        <modules>
          <module>cloud-provider-payment-8001</module>
        </modules>
        ```
    2. 子模块集成父项目
        - 查看全部内容

            ```XML
            <?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0"
                     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                     xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
                <parent>
                    <artifactId>springCloudProject</artifactId>
                    <groupId>com.atguigu.springcloud</groupId>
                    <version>1.0-SNAPSHOT</version>
                </parent>
                <modelVersion>4.0.0</modelVersion>
                <artifactId>cloud-provider-payment-8001</artifactId>
                <dependencies>
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-web</artifactId>
                    </dependency>
                    <!--
                        每一个微服务在云上部署以后，我们都需要对其进行监控、追踪、审计、控制等
                        SpringBoot 抽取了Actuator场景，使得我们每个微服务快速引用即可获得生产级别的应用监控、审计等功能
                    -->
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-actuator</artifactId>
                    </dependency>
                    <dependency>
                        <groupId>org.mybatis.spring.boot</groupId>
                        <artifactId>mybatis-spring-boot-starter</artifactId>
                    </dependency>
                    <dependency>
                        <groupId>com.alibaba</groupId>
                        <artifactId>druid-spring-boot-starter</artifactId>
                        <version>1.1.10</version>
                    </dependency>
                    <!--mysql-connector-java-->
                    <dependency>
                        <groupId>mysql</groupId>
                        <artifactId>mysql-connector-java</artifactId>
                    </dependency>
                    <!--jdbc-->
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-jdbc</artifactId>
                    </dependency>
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-devtools</artifactId>
                        <scope>runtime</scope>
                        <optional>true</optional>
                    </dependency>
                    <dependency>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok</artifactId>
                        <optional>true</optional>
                    </dependency>
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-test</artifactId>
                        <scope>test</scope>
                    </dependency>
                </dependencies>
            </project>
            ```
# **Maven 中的** `**DependencyManagement**` **和** `**Dependencies**`
1. `DependencyManagement` 提供了一种管理依赖版本号的方式，通常在父 POM 中使用
    1. **如果子项目没有指定依赖的版本：**Maven 会沿着父子层次向上走，直到找到一个拥有 dependencyManagement 元素的项目，然后它就会使用这个dependencyManagement 元素中指定的版本号
    2. **如果子项目中指定了版本号：**那么会使用子项目中指定的依赖版本
    3. **`DependencyManagement` 只是声明依赖，并不实现引入，真正的依赖引入是在 `Dependencies` 中引入的，因此子项目需要显示的声明需要用的依赖**
    4. **只有在子项目中写了该依赖项，并且没有指定具体版本，才会从父项目中继承该项**，并且`version`和`scope`都读取自父 pom
2. 这样做的好处是：
    1. 如果有多个子项目都引用同一样依赖，则可以避免在每个使用的子项目里都声明一个版本号
    2. 这样当想升级或切换到另一个版本时，只需要在顶层父容器里更新，而不需要一个一个子项目的修改
    3. 另外如果某个子项目需要另外的一个版本，只需要声明version就可