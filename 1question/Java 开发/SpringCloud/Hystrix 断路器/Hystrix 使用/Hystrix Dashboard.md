---
title: "Hystrix Dashboard"
tags:
  - "Spring_Cloud"
  - "Hystrix_Dashboard"
  - "Hystrix"
  - "yaml_配置文件"
  - "EnableHystrixDashboard"
  - "@EnableHystrixDashboard"
updated: 2026-04-16
---

# 一、简述
1. 除了隔离依赖服务的调用以外，Hystrix还提供了准实时的调用监控（Hystrix Dashboard）
2. Hystrix会持续地记录所有通过Hystrix发起的请求的执行信息，并以统计报表和图形的形式展示给用户，包括每秒执行多少请求多少成功，多少失败等
3. Netflix通过hystrix-metrics-event-stream项目实现了对以上指标的监控
4. Spring Cloud也提供了Hystrix Dashboard的整合，对监控内容转化成可视化界面
# 二、构建 Hystrix 监控服务 9001
1. **新建Moudle： cloud-consumer-hystrix-dashboard9001**
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
        <artifactId>cloud-consumer-hystrix-dashboard9001</artifactId>
        <dependencies>
            <!--⭐hystrix-dashboard-->
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-starter-netflix-hystrix-dashboard</artifactId>
            </dependency>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-actuator</artifactId>
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
3. **yaml 配置文件**

    ```Java
    server:
      port: 9001
    ```
4. **主启动类：****`@EnableHystrixDashboard`**

    ```Java
    @SpringBootApplication
    @EnableHystrixDashboard //开启监控
    public class HystrixDashboardMain9001 {
        public static void main(String[] args) {
            SpringApplication.run(HystrixDashboardMain9001.class,args);
        }
    }
    ```
5. **注意：所有Provider微服务提供类（8001/8002/8003）都需要监控依赖配置**

    ```XML
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    ```
6. **修改微服务提供类：cloud-provider-hystrix-payment8001**

    ```Java
    @SpringBootApplication
    @EnableEurekaClient
    @EnableCircuitBreaker //开启服务降级
    public class PaymentHystrixMain8001 {
        public static void main(String[] args) {
            SpringApplication.run(PaymentHystrixMain8001.class,args);
        }
        /**
         *⭐此配置是为了服务监控而配置，与服务容错本身无关，springcloud升级后的坑
         *ServletRegistrationBean因为springboot的默认路径不是"/hystrix.stream"，
         *只要在自己的项目里配置上下面的servlet就可以了
         */
        @Bean
        public ServletRegistrationBean getServlet() {
            HystrixMetricsStreamServlet streamServlet = new HystrixMetricsStreamServlet();
            ServletRegistrationBean registrationBean = new ServletRegistrationBean(streamServlet);
            registrationBean.setLoadOnStartup(1);
            registrationBean.addUrlMappings("/hystrix.stream");
            registrationBean.setName("HystrixMetricsStreamServlet");
            return registrationBean;
        }
    }
    ```
# 三、测试使用 Dashboard
1. [http://localhost:9001/hystrix](http://localhost:9001/hystrix)

    ![[IMG-20260405035414006.png|800]]

2. 输入：
    1. 监控地址：[http://localhost:8001/hystrix.stream](http://localhost:8001/hystrix.stream)
    2. delay：200
    3. 标题：cloud-provider-hystrix-payment8001
3. 多次访问：[http://localhost:8001/payment/circuit/1](http://localhost:8001/payment/circuit/1)

    ![[IMG-20260404031838729.png|800]]

4. **如何看这个监控图？**
    1. **实心圆：**
        1. 通过颜色的变化代表了实例的健康程度，它的健康度从绿色<黄色<橙色<红色递减
        2. 除了颜色的变化之外，它的大小也会根据实例的请求流量发生变化，流量越大该实心圆就越大
    2. **7 色：**

    ![[IMG-20260405035420385.png|800]]

    3. **1 线：**曲线：用来记录2分钟内流量的相对变化，可以通过它来观察到流量的上升和下降趋势

    ![[IMG-20260405035422108.png|800]]
