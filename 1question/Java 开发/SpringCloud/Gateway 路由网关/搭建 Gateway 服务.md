---
title: "搭建 Gateway 服务"
tags:
  - "Spring_Cloud"
  - "搭建_Gateway_服务"
  - "Gateway"
  - "路由1"
  - "路由2"
  - "路由3"
updated: 2026-04-16
---

# 一、搭建 Gateway 服务
1. **新建Moudle：cloud-gateway-gateway9527**
2. **pom.xml**
    > 💡 Gateway 不需要：spring-boot-starter-web、spring-boot-starter-actuator，否则启动时会报错

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
         <artifactId>cloud-gateway-gateway9527</artifactId>
         <dependencies>
             <!--⭐gateway-->
             <dependency>
                 <groupId>org.springframework.cloud</groupId>
                 <artifactId>spring-cloud-starter-gateway</artifactId>
             </dependency>
             <!--eureka-client-->
             <dependency>
                 <groupId>org.springframework.cloud</groupId>
                 <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
             </dependency>
             <!-- 引入自己定义的api通用包，可以使用Payment支付Entity -->
             <dependency>
                 <groupId>com.atguigu.springcloud</groupId>
                 <artifactId>cloud-api-commons</artifactId>
                 <version>${project.version}</version>
             </dependency>
             <!--一般基础配置类-->
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
3. **yaml 配置文件： cloud.gateway.routes**

    ```YAML
     server:
       port: 9527
     spring:
       application:
         name: cloud-gateway
       cloud:
         gateway:
           # 设置多个路由
           routes:
             - id: payment_routh               # 路由的ID，没有固定规则但要求唯一，建议配合服务名
               uri: http://localhost:8001      # uri：断言为true 后，路由转发访问的请求地址
               predicates:
                 - Path=/payment/get/**        # 断言：（Path）若请求路径与Path的路径相匹配，则路由转发访问 uri 中的地址
             - id: payment_routh2
               uri: http://localhost:8001
               predicates:
                 - Path=/payment/set/**
             - id: payment_routh3
               uri: https://www.bilibili.com/
               predicates:
                 - Path=/bilibili

     eureka:
       instance:
         hostname: cloud-gateway-service
       client:
         service-url:
           register-with-eureka: true        # 把网关服务注册在 Eureka 中
           fetch-registry: true
           defaultZone: http://eureka7001.com:7001/eureka
    ```
4. **主启动类**

    ```Java
     @SpringBootApplication
     @EnableEurekaClient
     public class GateWayMain9527 {
         public static void main(String[] args) {
             SpringApplication.run(GateWayMain9527.class,args);
         }
     }
    ```
5. **不需要业务类和 controller**
6. **测试：**
    1. **启动 7001、8001、9527**
    2. **Eureka 注册情况：**

    ![[IMG-20260405035413891.png|800]]

    3. **路由1：**不使用网关路由访问：[http://localhost:8001/payment/get/1](http://localhost:8001/payment/get/1)

    ![[IMG-20260404031838359.png|800]]

    4. **路由2：**使用网关路由访问：[http://localhost:9527/payment/get/1](http://localhost:9527/payment/get/1)

    ![[IMG-20260405035420294.png|800]]

    5. **路由3：**[http://localhost:9527/bilibili](http://localhost:9527/bilibili)

    ![[IMG-20260405035422000.png|800]]
