---
title: "spring-boot-starter"
tags:
  - "编写配置类"
  - "@ConfigurationProperties"
  - "Spring_Boot"
  - "AutoConfiguration"
  - "Spring"
  - "Starter"
updated: 2026-04-16
---

> ℹ️ 如何自定义一个场景启动器springboot-starter，从零开始实现推导。_哔哩哔哩_bilibili
> 如何自定义一个场景启动器springboot-starter，从零开始实现推导。, 视频播放量 3257、弹幕量 18、点赞数 75、投硬币枚数 27、收藏人数 133、转发人数 7, 视频作者 程序员蜗牛哥, 作者简介 ，相关视频：spring事务控制你还在用transactional注解吗？今天给大家分享编程式事务实现方案，springboot一个注解实现接口的加解密\#计算机 \#编程 \#互联网 \#每天跟我涨知识 \#干货分享，被面试官问懵：SpringBoot可以同时处理多少个请求？，分享一个idea插件，写代码神器。，为什么SpringBoot调用一个异步方法都喜欢使用@Async注解？可千万别再这么用了。。，别再重复造轮子了，一个 Spring 注解轻松搞定循环重试功能！，为什么不直接java -jar 启动？多此一举？，还在用策略模式解决if else？map➕函数式接口来帮你搞定，springboot使用aop统一日志管理，mybatis拦截器实现动态sql执行，你一定用过
> [https://www.bilibili.com/video/BV1PA4m1G7wa/?spm_id_from=333.337.search-card.all.click&vd_source=c211fe7b42b0acdb0c6dd7d85cab102c](https://www.bilibili.com/video/BV1PA4m1G7wa/?spm_id_from=333.337.search-card.all.click&vd_source=c211fe7b42b0acdb0c6dd7d85cab102c)
# 一、介绍
## 1. 定义
1. starter会把所有用到的依赖包都包含进来，避免开发者自己去引入依赖所带来的麻烦
2. 虽然不同的starter实现起来各有差异，但是他们基本上都会使用到两个相同的内容：`ConfigurationProperties` 和 `AutoConfiguration`
    ![[Attachment/1question/大数据/Java 开发/SpringBoot/3 SpringBoot 原理分析/3 3 SpringBoot 自动配置原理/IMG-20260405035413988.png|800]]
3. 本质上使用了 SPI 机制 ⭐
    1. **可以理解成 Spring 内部一套类加载机制，读取指定位置的文件配置，进行bean的自动装配**（==SPI机制==）
    2. **你要写一个starter给别人用，首先，要将那些别人在使用你starter时，需要自动注入的 bean 都在starter的自动化配置类里装配好，并要在约定好的位置，将自动化配置类名写入****`spring.factories`** **文件**
    3. 详见[[自动配置原理]]
        1. **`AutoConfigurationImportSelector`** 类则是 Spring Boot 自动装配的核心类
        2. 这个类会通过 ClassLoader 获取 classpath 中的配置文件 `META-INF/spring.factories`

## 2. 命名规则
- 由于SpringBoot官方本身就提供了很多Starter，为了区别那些是官方的，哪些是第三方的，所以SpringBoot官方提出：
    1. 第三方提供的Starter统一用xxx-spring-boot-starter
    2. 而官方提供的Starter统一用spring-boot-starter-xxx

# 二、手写一个 Boot-starter
> 下边我们将以Redisson为例，实现一个简易版的starter组件，通过starter组件将`RedissonClient`所需的jar和bean依赖到我们当前项目
## 1. 创建 Starter

![[IMG-20260404031827995.png|800]]

### 1.1 创建项目
- 首先我们创建一个`redisson-spring-boot-starter`的项目，并添加`redisson`依赖和`spring-boot-starter`依赖，如下

    ```JavaScript
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
      <modelVersion>4.0.0</modelVersion>
      <groupId>com.autu.example.redisson</groupId>
      <artifactId>redisson-spring-boot-starter</artifactId>
      <version>1.0-SNAPSHOT</version>
      <name>redisson-spring-boot-starter</name>
      <!-- FIXME change it to the project's website -->
      <url>http://www.example.com</url>
      <dependencies>
        <dependency>
          <groupId>org.springframework.boot</groupId>
          <artifactId>spring-boot-starter</artifactId>
          <version>2.3.1.RELEASE</version>
          <!-- 禁止传递依赖 -->
          <optional>true</optional>
        </dependency>
        <dependency>
          <groupId>org.redisson</groupId>
          <artifactId>redisson</artifactId>
          <version>3.13.1</version>
        </dependency>
          <!-- 配置提示信息，需加此依赖 -->
        <dependency>
          <groupId>org.springframework.boot</groupId>
          <artifactId>spring-boot-configuration-processor</artifactId>
          <version>2.3.1.RELEASE</version>
        </dependency>
      </dependencies>
    </project>
    ```
- 相关案例：依赖本体存在但传递依赖被裁掉后，可能出现“编译通过、运行时报 `NoClassDefFoundError`”的问题，详见 [[问题记录：编译通过但运行时报 NoClassDefFoundError]]。

### 1.2 编写配置类
- 创建一个ConfigurationProperties用于保存配置信息

    ```Java
    @ConfigurationProperties(prefix = "auto.redisson")
    public class RedissonProperties {
        /** Redis server host */
        private String host = "localhost";
        /** Redis server port */
        private int port = 6379;
        /** 连接超时时间 */
        private int timeout;
        /** 是否启用ssl支持 */
        private boolean ssl;
        ...
    }
    ```
### 1.3 创建自动化配置类⭐
- 创建一个`AutoConfiguration`，引用定义好的配置信息
- 在`AutoConfiguration`中实现bean的注入以及配置信息的读取
- 把这个类加入spring.factories配置文件中进行声明
    ```Java
    @ConditionalOnClass(Redisson.class)
    @EnableConfigurationProperties(RedissonProperties.class)
    @Configuration
    public class RedissonAutoConfiguration {
        @Bean
        RedissonClient redissonClient(RedissonProperties redissonProperties) {
            Config config = new Config();
    		// 判断是否启用ssl
            String prefix = redissonProperties.isSsl() ? "rediss://" : "redis://";
            String host = redissonProperties.getHost();
            int port = redissonProperties.getPort();
            config.useSingleServer()
                    .setAddress(prefix + host + ":" + port)
                    .setConnectTimeout(1000 * 30);
            return Redisson.create(config);
        }
    }
    ```
> ⭐==**可以在在自动化配置类上使用一些注解进行装配的定制**==
>
> ![[IMG-20260405035420368.png|800]]
>
> 1. **@EnableConfigurationProperties({MetaqProperties.class})**:
>
>     - 用途：启用对 `@ConfigurationProperties` 注解的支持，使得指定的类（如 `MetaqProperties`）可以将 Spring Boot 的外部化配置（如 `application.properties` 和 `application.yml` 中的配置）绑定到 Java Bean 上。
>
>     - 作用：简化配置类的属性映射，将应用配置轻松绑定到 POJO 中，从而使其可配置性和可维护性更强。
>
>
> 2. **@ConditionalOnProperty**:
>
>     - 用途：用来根据某个（些）Spring Boot配置属性是否存在，决定一个配置类或者Bean是否应该被加载。
>
>     - 示例中的 `name = {"spring.metaq.enabled"}, matchIfMissing = true` 表示当 `spring.metaq.enabled` 配置属性存在并为 `true` 或者配置属性缺失时（由于 `matchIfMissing = true`），这个配置类将被处理。
>
>     - 作用：允许开发者控制配置的启用或禁用，从而实现条件化的 Bean 注册。
>
>
> 3. **@ConditionalOnClass**:
>
>     - 用途：条件化加载Bean或者配置，只有在类路径中存在指定的类（如这里的 `MetaProducer`）时，才会创建这种条件下的 Bean 或配置。
>
>     - 作用：确保只有在特定环境存在时（例如应用程序依赖于特定库），相关的 Bean 或配置才被创建，避免类路径缺失时出现 `ClassNotFoundException`。
>
>
> 4. **@Import({MetaqProducerRegistrar.class})**:
>
>     - 用途：允许将一个或多个类注入到 Spring 应用上下文中。被导入的类通常是配置类。
>
>     - 作用：通过 `@Import` 可以轻松导入其他配置类或者注册复杂的配置逻辑（而不是直接在当前配置类中定义）。在这种情况下，`MetaqProducerRegistrar` 将成为应用上下文的一部分，参与 Bean 的定义和配置管理。
>
### 1.4 创建`spring.factories`
```Java
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.autu.example.redisson.RedissonAutoConfiguration
```
### 1.5 创建提示信息
- `additional-spring-configuration-metadata.json`的作用：描述配置信息，在其他项目依赖当前starter组件时起到提示的作用
- 效果

    ![[IMG-20260405035422092.png|521]]

    ```XML
    <!-- 配置文件提示需在starter中加入该依赖 -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-configuration-processor</artifactId>
      <version>2.3.1.RELEASE</version>
    </dependency>
    ```
    ```JSON
    {
      "properties": [
        {
          "name": "autu.redissin.host",
          "type": "java.lang.String",
          "description": "redis服务器地址.",
          "defaultValue": "localhost"
        },{
          "name": "autu.redisson.port",
          "type": "java.lang.Integer",
          "description": "redis服务器端口.",
          "defaultValue": 6379
        }
      ]
    }
    ```
## 2. Mvn Install
- 接下来，我们通过运行`mvn install`命令，将这个项目打成jar包

    ![[IMG-20260405035434264.png|800]]

- 部署到本地仓库，提供给另一个服务调用

    ![[IMG-20260405035445574.png|800]]

## 3. 测试
- 创建一个测试项目，依赖`redisson-spring-boot-starter`
### 3.1 `application.properties`配置文件
```Java
auto.redisson.host=127.0.0.1
auto.redisson.port=6379
auto.redisson.timeout=10000
auto.redisson.ssl=false
```
### 3.2 测试类
```Java
@RestController
public class HelloController {
    @Autowired
    RedissonClient redissonClient;
    @GetMapping("/test")
    public String say() {
        RBucket<Object> bucket = redissonClient.getBucket("name");
        if (bucket.get() == null) {
            bucket.set("bucket");
        }
        return bucket.get().toString();
    }
}
```
### 3.3 测试结果
- 从结果中，我们看到starter中定义的`RedissonClient`已成功注入到测试项目中
    ![[IMG-20260405035505333.png|365]]
