---
title: "1. SpringBoot 介绍"
tags:
  - "Spring_Boot"
  - "Spring"
  - "自动配置"
  - "约定优于配置"
  - "Starter"
  - "IOC"
updated: 2026-04-16
---

# 一、Spring 与 SpringBoot

[![|800](https://cdn.nlark.com/yuque/0/2020/png/1354552/1602642309979-eac6fe50-dc84-49cc-8ab9-e45b13b90121.png?x-oss-process=image%2Fwatermark%2Ctype_d3F5LW1pY3JvaGVp%2Csize_27%2Ctext_YXRndWlndS5jb20g5bCa56GF6LC3%2Ccolor_FFFFFF%2Cshadow_50%2Ct_80%2Cg_se%2Cx_10%2Cy_10)](https://cdn.nlark.com/yuque/0/2020/png/1354552/1602642309979-eac6fe50-dc84-49cc-8ab9-e45b13b90121.png?x-oss-process=image%2Fwatermark%2Ctype_d3F5LW1pY3JvaGVp%2Csize_27%2Ctext_YXRndWlndS5jb20g5bCa56GF6LC3%2Ccolor_FFFFFF%2Cshadow_50%2Ct_80%2Cg_se%2Cx_10%2Cy_10)

1. **Spring 存在的问题：**
    1. Spring 基于 IOC 和 AOP 两个特性对 Java 开发本身进行了大大的简化
    2. 但是一个大型的项目需要集成很多其他组件，比如一个 WEB 项目，至少要集成 MVC 框架、Tomcat 这种 WEB 容器、日志框架、ORM框架，连接数据库要选择连接池
    3. 尽管Spring框架提供了强大的功能和灵活性，但在使用Spring时，开发人员需要编写大量的配置文件和样板代码
2. 🙋‍♂️ **SpringBoot 如何让简化 Spring 开发❓**
    1. Spring Boot是一个基于Spring框架的快速开发框架，目的是使Spring应用的开发变得更加简单和快速
    2. Spring Boot通过**==自动配置==**和==**约定优于配置**==的方式，减少了开发人员的工作量，从而提高了开发效率
    3. **内置了 50 多种已经集成好的 starter 依赖启动器，用于简化配置的构建**
        1. 启动器 Starter 就是**一组预先配置好的依赖项**，可以快速引入常用功能和技术栈，例如 Redis、MongoDB、Jpa、kafka，Hakira 等等
        2. 使得应用这些第三方库几乎可以零配置地开箱即用，因此，大部分的 **SpringBoot 应用都只需要非常少量的配置代码，开发者能够更加专注于业务逻辑**
    4. 此外，Spring Boot还**提供了内嵌web服务器、生产级别的监控、健康检查及外部化配置**
3. 🙋‍♂️ **以下是一些常用的 Spring Boot Starter 启动器**
    1. **spring-boot-starter-web**：包含 Spring MVC、Tomcat、Jackson 等常用的 Web 开发相关依赖
    2. **spring-boot-starter-data-redis**：包含 Redis 连接池和 Redis 相关的依赖项
    3. **spring-boot-starter-amqp**：包含 RabbitMQ 相关依赖项，用于消息传递
    4. **spring-boot-starter-test**：包含测试相关的依赖项，如 JUnit、Mockito 等
    5. **spring-boot-starter-security**：包含 Spring Security 相关依赖项，用于身份验证和授权
