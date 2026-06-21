---
title: "Nacos 作服务注册中心"
tags:
  - "服务注册中心对比"
  - "yaml_配置文件"
  - "Spring_Cloud"
  - "Nacos_作服务注册中心"
  - "服务注册"
  - "Nacos"
updated: 2026-04-16
---

**没必要专门再构建 Nacos 服务注册与发现的服务Module（ 如之前的 Eureka 7001、7002）了，因为后台 Nacos 服务已经启动了**

# 一、构建 Service Provider:9001
1. **新建Moudle：cloudalibaba-provider-payment9001**
2. **pom.xml**
    1. 父工程 pom

    ```XML
     <!--spring cloud alibaba 2.1.0.RELEASE-->
     <dependency>
       <groupId>com.alibaba.cloud</groupId>
       <artifactId>spring-cloud-alibaba-dependencies</artifactId>
       <version>2.1.0.RELEASE</version>
       <type>pom</type>
       <scope>import</scope>
     </dependency>
    ```
    2. 本模块 pom

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
         <artifactId>cloudalibaba-provider-payment9001</artifactId>
         <dependencies>
             <!--⭐SpringCloud ailibaba nacos -->
             <dependency>
                 <groupId>com.alibaba.cloud</groupId>
                 <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
             </dependency>
             <!-- SpringBoot整合Web组件 -->
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
3. **yaml 配置文件**

    ```YAML
     server:
       port: 9001
     spring:
       application:
         name: nacos-payment-provider
       cloud:
         nacos:
           discovery:
             server-addr: localhost:8848 # ⭐配置 Nacos 地址
     management:
       endpoints:
         web:
           exposure:
             include: '*'
    ```
4. **主启动类**

    ```Java
     @EnableDiscoveryClient //开启服务发现
     @SpringBootApplication
     public class PaymentMain9001 {
         public static void main(String[] args) {
             SpringApplication.run(PaymentMain9001.class, args);
         }
     }
    ```
5. **Controller**

    ```Java
     @RestController
     public class PaymentController {
         @Value("${server.port}")
         private String serverPort;
         @GetMapping(value = "/payment/nacos/{id}")
         public String getPayment(@PathVariable("id") Integer id) {
             return "nacos registry, serverPort: "+ serverPort+"\t id"+id;
         }
     }
    ```
6. **测试：**
    1. [http://localhost:9001/payment/nacos/1](http://localhost:9001/payment/nacos/1)
    2. [http://localhost:8848/nacos](http://localhost:8848/nacos)

    ![[IMG-20260405035414029.png|800]]

# 二、构建 Service Provider:9002
1. 按照 9001 将 9002 创建，并注册到 Nacos 服务上

    ![[IMG-20260404031840222.png|800]]

2. [http://localhost:8848/nacos](http://localhost:8848/nacos) **两个端口的支付服务9001、9002都注册在了 Nacos 上**

    ![[IMG-20260405035420390.png|800]]

# 三、构建 Service Consumer:83
1. **新建Moudle：cloudalibaba-consumer-nacos-order83**
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
         <artifactId>cloudalibaba-consumer-nacos-order83</artifactId>
         <dependencies>
             <!--⭐SpringCloud ailibaba nacos -->
             <dependency>
                 <groupId>com.alibaba.cloud</groupId>
                 <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
             </dependency>
             <!-- 引入自己定义的api通用包，可以使用Payment支付Entity -->
             <dependency>
                 <groupId>com.atguigu.springcloud</groupId>
                 <artifactId>cloud-api-commons</artifactId>
                 <version>${project.version}</version>
             </dependency>
             <!-- SpringBoot整合Web组件 -->
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
3. **yaml 配置文件**

    ```YAML
     server:
       port: 83
     spring:
       application:
         name: nacos-order-consumer
       cloud:
         nacos:
           discovery:
             server-addr: localhost:8848
     # ⭐消费者将要去访问的微服务名称
     service-url:
       nacos-user-service: http://nacos-payment-provider
    ```
4. **主启动类**

    ```Java
     @EnableDiscoveryClient
     @SpringBootApplication
     public class OrderNacosMain83 {
         public static void main(String[] args) {
             SpringApplication.run(OrderNacosMain83.class,args);
         }
     }
    ```
5. **配置类：配置用于服务调度的** ==**RestTemplate +**== **`@LoadBalanced`**

    ```Java
     @Configuration
     public class ApplicationContextBean {
         @Bean
         @LoadBalanced   //赋予 RestTemplate 负载均衡的能力
         public RestTemplate getRestTemplate() {
             return new RestTemplate();
         }
     }
    ```
6. **Controller**

    ```Java
     @RestController
     public class OrderNacosController {
         @Resource
         private RestTemplate restTemplate;
         @Value("${service-url.nacos-user-service}")
         private String serverURL;
         @GetMapping("/consumer/payment/nacos/{id}")
         public String paymentInfo(@PathVariable("id") Long id) {
             return restTemplate.getForObject(serverURL+"/payment/nacos/"+id,String.class);
         }
     }
    ```
7. **测试：**
    1. [http://localhost:8848/nacos](http://localhost:8848/nacos) **支付服务提供者9001、9002；支付服务消费者 83 都注册在了 Nacos 上**

    ![[Attachment/1question/Java 开发/SpringCloud/Nacos 注册发现中心与配置中心/Nacos 使用/IMG-20260405035422115.png|794]]

    2. [http://localhost:83/consumer/payment/nacos/1](http://localhost:83/consumer/payment/nacos/1)

    ![[IMG-20260405035427634.png|558]]

        - **可以看到 8001、8002 交替出现：为什么能实现 轮询算法的负载均衡？Nacos 内置了 Rinbbon**

    ![[IMG-20260405035427662.png|718]]

# 四、服务注册中心对比
1. ==**Nacos 支持 AP 和 CP 模式的切换**==

    ![[IMG-20260405035427689.png|800]]

2. **何时选择使用何种模式**
    1. 一般来说，如果**不需要存储服务级别的信息** 且 **服务实例是通过 nacos-client 注册，并能够保持心跳上报**，那么就可以选择AP模式
        1. 前主流的服务如 Spring cloud 和 Dubbo 服务，都适用于AP模式
        2. AP模式为了服务的可能性而减弱了一致性，因此AP模式下只支持注册临时实例
    2. 如果**需要在服务级别 编辑 或者 存储 配置信息**，那么 CP 是必须的
        1. K8S服务和DNS服务则适用于CP模式
        2. CP模式下则支持注册持久化实例，此时则是以 Raft 协议为集群运行模式，该模式下注册实例之前必须先注册服务，如果服务不存在，则会返回错误
3. 如何切换模式：

    ```Bash
     curl -X PUT '$NACOS_SERVER:8848/nacos/v1/ns/operator/switches?entry=serverMode&value=CP'
    ```
