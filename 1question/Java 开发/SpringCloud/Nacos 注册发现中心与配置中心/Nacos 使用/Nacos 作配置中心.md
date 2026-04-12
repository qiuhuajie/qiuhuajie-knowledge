- [[#1. 构建 Nacos 客户端:3377]]
- [[#2. 配置文件的 动态获取]]
- [[#3. Nacos 配置的空间划分]]
    - [[#3.1 存在的问题]]
    - [[#3.2 Nacos 的划分]]
    - [[#3.3 三种方案实现加载配置]]
- [[#4. 配置中心对比]]
- [[#5. Nacos 配置文件持久化]]
# 1. **构建 Nacos 客户端:3377**
1. **新建Moudle：cloudalibaba-config-nacos-client3377（类比 Config + Bus 中的 3344、3355、3366）**
1. **pom.xml**
    
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
     
         <artifactId>cloudalibaba-config-nacos-client3377</artifactId>
     
         <dependencies>
             <!--nacos-config-->
             <dependency>
                 <groupId>com.alibaba.cloud</groupId>
                 <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
             </dependency>
             <!--nacos-discovery-->
             <dependency>
                 <groupId>com.alibaba.cloud</groupId>
                 <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
             </dependency>
             <!--web + actuator-->
             <dependency>
                 <groupId>org.springframework.boot</groupId>
                 <artifactId>spring-boot-starter-web</artifactId>
             </dependency>
             <dependency>
                 <groupId>org.springframework.boot</groupId>
                 <artifactId>spring-boot-starter-actuator</artifactId>
             </dependency>
             <!--一般基础配置-->
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
    
1. **yaml 配置文件**
    
    1. **bootstrap.yml**
        
        ```YAML
         # nacos配置
         server:
           port: 3377
         
         spring:
           application:
             name: nacos-config-client
           cloud:
             nacos:
               discovery:
                 server-addr: localhost:8848 \#Nacos服务注册中心地址
               config:
                 server-addr: localhost:8848 \#Nacos作为配置中心地址
                 file-extension: yaml \#指定yaml格式的配置
         
         # 如何找到想要读取的配置文件？
         
         # ⭐配置文件 DataId 的拼接规则：
         # ${spring.application.name}-${spring.profile.active}.${spring.cloud.nacos.config.file-extension}
        ```
        
    
    1. **application.yml**
        
        ```YAML
         spring:
           profiles:
             active: dev # 表示当前是开发环境
        ```
        
    
1. **主启动类**
    
    ```Java
     @EnableDiscoveryClient
     @SpringBootApplication
     public class NacosConfigClientMain3377 {
         public static void main(String[] args) {
             SpringApplication.run(NacosConfigClientMain3377.class, args);
         }
     }
    ```
    
1. **Controller：**==`**@RefreshScope**`==
    
    ```Java
     @RestController
     @RefreshScope //⭐在控制器类加入@RefreshScope注解使当前类下的配置支持Nacos的动态刷新功能
     public class ConfigClientController {
         @Value("${config.info}")
         private String configInfo;
     
         @GetMapping("/config/info")
         public String getConfigInfo() {
             return configInfo;
         }
     }
    ```
    
1. **测试：**
    
    1. **在Nacos 上添加 配置文件（不再像 SpringCloud Config 中需要 Git 了）**
        
        ![[IMG-20260405035414030.png|Untitled 498.png]]
        
        ![[IMG-20260404031840653.png|Untitled 1 365.png]]
        
        ![[IMG-20260405035420391.png|Untitled 2 295.png]]
        
    
    1. **访问** [**http://localhost:3377/config/info**](http://localhost:3377/config/info)**，3377 获得配置信息：**
        
        ![[IMG-20260405035422116.png|Untitled 3 221.png]]
        
    
    1. **Nacos 配置文件 命名规则**
        
        - `**${spring.application.name}-${spring.profile.active}.${spring.cloud.nacos.config.file-extension}**`
        
        - **微服务注册名`-`开发环境名`.`指定文件后缀**
        
        ![[IMG-20260405035427641.png|Untitled 4 170.png]]
        
    
1. 历史配置：Nacos会记录配置文件的历史版本默认保留30天，此外还有一键回滚功能，回滚操作将会触发配置更新
    
    ![[IMG-20260405035427666.png|Untitled 5 138.png]]
    
# 2. **配置文件的 动态获取**
1. **将 配置文件中的version 改为2**
    
    ![[IMG-20260405035427697.png|Untitled 6 115.png]]
    
1. **刷新** [**http://localhost:3377/config/info**](http://localhost:3377/config/info) **直接就变成了 2**
    
    ![[IMG-20260405035434838.png|Untitled 7 92.png]]
    
1. **结论：**==**Nacos 自带 配置文件的动态刷新**==（无需像 Config 还需要 Bus 的辅助）
# 3. **Nacos 配置的空间划分**
## 3.1 **存在的问题**
1. 问题1：实际开发中，通常一个系统会准备dev开发环境、test测试环境、prod生产环境。如何保证**指定环境启动时服务能正确读取到Nacos上相应环境的配置文件**呢？
1. 问题2：一个大型分布式微服务系统会有很多微服务子项目，每个微服务项目又都会有相应的开发环境、测试环境、预发环境、正式环境...... 那**怎么对这些微服务配置进行管理**呢？
## 3.2 **Nacos 的划分**
![[IMG-20260405035445905.png|Untitled 8 74.png]]
1. **Namespace：**
    
    1. 可以用于区分部署环境，用来实现隔离
    
    1. 默认：public
    
1. **Group：**
    
    1. 逻辑上区分两个目标对象
    
    1. Group可以把不同的微服务划分到同一个分组里面去
    
    1. 默认：DEFAULT_GROUP
    
1. **Service：**
    
    1. 就是一个微服务
    
    1. 一个Service可以包含多个Cluster（集群），Cluster是对指定微服务的一个虚拟划分
        
        > 比方说为了容灾，将Service微服务分别部署在了杭州机房和广州机房，这时就可以给杭州机房的Service微服务起一个集群名称（HZ），给广州机房的Service微服务起一个集群名称（GZ），还可以尽量让同一个机房的微服务互相调用，以提升性能
        
    
    1. Nacos默认Cluster是DEFAULT
    
1. **Instance：**就是微服务的实例
## 3.3 **三种方案实现加载配置**
1. **DataID方案**
    
    1. ==给DataID拼接不同的 profile==，对应不同的环境（哪个环境就activate哪个）
        
        ```YAML
         spring:
           profiles:
             active: dev # 表示开发环境
             # active: test # 表示测试环境
             # active: prod # 表示生产环境
        ```
        
    
    1. Nacos 上的配置文件
        
        ![[IMG-20260405035505470.png|Untitled 9 65.png]]
        
    
1. **Group方案**
    
    1. DataID同名，但==指定给不同的组==，配置的时候指定用哪个组的文件
        
        ```YAML
         spring.cloud.nacos.config.group = TEST_GROUP
         # spring.cloud.nacos.config.group = DEV_GROUP
        ```
        
    
    1. Nacos 上的配置文件
        
        ![[IMG-20260405035512309.png|Untitled 10 55.png]]
        
    
1. **Namespace方案**
    
    1. 在 bootstrap.yml 中配置==使用不同命名空间==中的文件
        
        ```YAML
         spring.cloud.nacos.config.namespace = c0e9bf90-5be2-44e3-94e5-77ae587b72f7
        ```
        
    
    1. Nacos 上的配置文件
        
        ![[IMG-20260405035520914.png|Untitled 11 47.png]]
        
    
# 4. **配置中心对比**
![[IMG-20260405035527740.png|Untitled 12 41.png]]
# 5. **Nacos 配置文件持久化**
1. 为什么要使用 MySQL 做持久化？
    
    1. Nacos默认**自带嵌入式数据库 derby**，默认Nacos使用嵌入式数据库实现数据的存储
    
    1. **如果启动**==**多个默认配置下的Nacos节点**==**，数据存储是存在**==**一致性**==**问题的**
    
    1. 为了解决这个问题，Nacos采用了集中式存储的方式来支持集群化部署，目前只支持MySQL的存储
    
1. **Nacos持久化配置：derby 到 mysql 切换配置**
    
    1. 执行 sql 脚本，先将 mysql 的数据库创建好
        
        1. sql 脚本的位置："E:\nacos\conf\nacos-mysql.sql"
        
        1. 执行脚本（先创建 nacos_config 数据库）
        
        1. 查看本地 mysql
            
            ![[IMG-20260405035532980.png|Untitled 13 38.png]]
            
        
    
    1. 修改 Nacos 的配置文件
        
        1. 配置文件位置："E:\nacos\conf\application.properties"
        
        1. 添加以下内容
            
            ```YAML
             spring.datasource.platform=mysql
             db.num=1
             db.url.0=jdbc:mysql://127.0.0.1:3306/nacos_config?characterEncoding=utf8&connectTimeout=1000&socketTimeout=3000&autoReconnect=true&useUnicode=true&useSSL=false&serverTimezone=UTC
             db.user=root
             db.password=xxxxx
            ```
            
        
    
1. **测试**
    
    1. 重启 Nacos
    
    1. 查看 当前 Nacos 上的配置文件信息**（因为，之前创建的配置文件都没了，之前的是创建在自带嵌入式数据库 derby中，现在是连接的mysql）**
        
        ![[IMG-20260405035534366.png|Untitled 14 35.png]]
        
    
    1. 创建一个新的配置文件
        
        ![[IMG-20260405035537646.png|Untitled 15 33.png]]
        
    
    1. 查看 mysql
        
        ![[IMG-20260405035541532.png|Untitled 16 26.png]]