---
title: "Sentinel Dashboard"
tags:
  - "Spring_Cloud"
  - "Sentinel_Dashboard"
  - "熔断降级"
  - "Sentinel"
  - "YAML"
  - "Spring"
updated: 2026-04-16
---

# 一、安装 Sentinel
1. 下载：

    https://github.com/alibaba/Sentinel/releases
2. 运行下载好的 jar 包

    ```Plain
     java -jar sentinel-dashboard-1.7.0.jar
    ```
3. 访问 [http://localhost:8080/](http://localhost:8080/) （sentinel dashboard 端口是 8080），登录账号密码均为sentinel

    ![[IMG-20260405035414038.png|800]]
# 二、构建演示服务：8401
1. **新建Moudle：cloudalibaba-sentinel-service8401**
2. **pom.xml**

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
         <artifactId>cloudalibaba-sentinel-service8401</artifactId>
         <dependencies>
             <!--SpringCloud ailibaba nacos -->
             <dependency>
                 <groupId>com.alibaba.cloud</groupId>
                 <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
             </dependency>
             <!--⭐SpringCloud ailibaba sentinel-datasource-nacos 后续做持久化用到-->
             <dependency>
                 <groupId>com.alibaba.csp</groupId>
                 <artifactId>sentinel-datasource-nacos</artifactId>
             </dependency>
             <!--⭐SpringCloud ailibaba sentinel -->
             <dependency>
                 <groupId>com.alibaba.cloud</groupId>
                 <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
             </dependency>
             <!--openfeign-->
             <dependency>
                 <groupId>org.springframework.cloud</groupId>
                 <artifactId>spring-cloud-starter-openfeign</artifactId>
             </dependency>
             <!-- SpringBoot整合Web组件+actuator -->
             <dependency>
                 <groupId>org.springframework.boot</groupId>
                 <artifactId>spring-boot-starter-web</artifactId>
             </dependency>
             <dependency>
                 <groupId>org.springframework.boot</groupId>
                 <artifactId>spring-boot-starter-actuator</artifactId>
             </dependency>
             <!--日常通用jar包配置-->
             <dependency>
                 <groupId>org.springframework.boot</groupId>
                 <artifactId>spring-boot-devtools</artifactId>
                 <scope>runtime</scope>
                 <optional>true</optional>
             </dependency>
             <dependency>
                 <groupId>cn.hutool</groupId>
                 <artifactId>hutool-all</artifactId>
                 <version>4.6.3</version>
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
3. **yaml 配置文件：spring.cloud.sentinel**

    ```YAML
     server:
       port: 8401
     spring:
       application:
         name: cloudalibaba-sentinel-service
       cloud:
         nacos:
           discovery:
             \#Nacos服务注册中心地址
             server-addr: localhost:8848
         sentinel:
           transport:
             \#配置Sentinel dashboard地址
             dashboard: localhost:8080
             \#默认8719端口，假如被占用会自动从8719开始依次+1扫描,直至找到未被占用的端口
             port: 8719
     management:
       endpoints:
         web:
           exposure:
             include: '*'
    ```
4. **主启动类**

    ```Java
     @EnableDiscoveryClient
     @SpringBootApplication
     public class MainApp8401 {
         public static void main(String[] args) {
             SpringApplication.run(MainApp8401.class, args);
         }
     }
    ```
5. **Controller**

    ```Java
     @RestController
     public class FlowLimitController {
         @GetMapping("/testA")
         public String testA() {
             return "------testA";
         }
         @GetMapping("/testB")
         public String testB() {
             return "------testB";
         }
     }
    ```
# 三、测试
1. 启动 Nacos
2. 启动 Sentinel Dashboard
3. 启动 cloudalibaba-sentinel-service8401
4. Sentinel采用的**懒加载**，需要先访问请求，才能监控到
    - [http://localhost:8401/testA](http://localhost:8401/testA)
    - [http://localhost:8401/testB](http://localhost:8401/testB)
5. [http://localhost:8080/](http://localhost:8080/)
    1. ==**簇点链路：**==
        - 簇点链路（单机调用链路）页面实时的去拉取指定客户端资源的运行情况
        - 一共提供两种展示模式：一种用树状结构展示资源的调用链路，另外一种则不区分调用链路展示资源的实时情况
        - **注意:** 簇点链路监控是内存态的信息，它仅展示启动后调用过的资源

    ![[IMG-20260404031843445.png|800]]
    2. ==**实时监控：**==
        - 同时，同一个服务下的所有机器的簇点信息会被汇总，并且秒级地展示在"实时监控"下
        - **注意:** 实时监控仅存储 5 分钟以内的数据，如果需要持久化，需要通过调用实时监控接口来定制

    ![[IMG-20260405035420394.png|800]]
