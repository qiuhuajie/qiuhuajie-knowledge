# 1. **Spring框架**

[Home](https://spring.io/)

- Spring是轻量级的、开源的 JavaEE 框架
    - 轻量级：Spring所含的jar包比较少、比较小，需要大量引入
    - 框架：解决企业应用开发的复杂性
- Spring有两个核心部分：**IOC**和**AOP**
    1. IOC：控制反转，之前是new个类创建对象，现在是把创建对象的过程交给spring进行管理
    2. AOP：面向切面，不修改代码的情况下，进行功能增强

    ![Untitled](IMG-20260620232101044.png)

- Spring框架的**特点**
    1. 方便解耦，简化开发
    2. 支持AOP编程
    3. 方便程序的测试
    4. 方便集成各种常见框架，如mybatis
    5. 方便进行事务的操作
    6. 降低API的开发难度，对其中的功能进行封装

# 2. 设计模式在 Spring 中的应用⭐

1. **工厂设计模式：**Spring使用工厂模式通过 `BeanFactory` 和 `ApplicationContext` 对象 创建 bean[（详见 设计模式 工厂模式）](../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E5%88%9B%E5%BB%BA%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E7%AE%80%E5%8D%95%E5%B7%A5%E5%8E%82%E6%A8%A1%E5%BC%8F%20%E2%AD%90%20b4feea09a392434896f11521e8838267.md)
2. **代理设计模式：**Spring AOP 功能的实现[（详见 设计模式 代理模式）](../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E7%BB%93%E6%9E%84%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E4%BB%A3%E7%90%86%E6%A8%A1%E5%BC%8F%20%E2%AD%90%20842740694a744703bae301ee954a103e.md)
3. **单例设计模式：**Spring 中的 Bean 默认都是单例的[（详见 设计模式 单例模式）](../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E5%88%9B%E5%BB%BA%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E5%8D%95%E4%BE%8B%E6%A8%A1%E5%BC%8F%20%E2%AD%90%20f51e94bd1992441288ef067991eb7692.md)
4. **观察者模式：**Spring 事件驱动模型就是观察者模式很经典的一个应用[（详见 设计模式 观察者模式）](../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E8%A1%8C%E4%B8%BA%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E8%A7%82%E5%AF%9F%E8%80%85%E6%A8%A1%E5%BC%8F%E2%AD%90%20d742e966c5f84cf6823908f7d9f40ff5.md)
5. **适配器模式：**
    - Spring AOP 的增强或通知（Advice）使用到了适配器模式[（详见 设计模式 适配器模式）](../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E7%BB%93%E6%9E%84%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E9%80%82%E9%85%8D%E5%99%A8%E6%A8%A1%E5%BC%8F%20%E2%AD%90%202b037a9aa2cd47c59d02cdc4054ad619.md)
    - spring MVC 中也是用到了适配器模式适配 Controller[（详见 设计模式 适配器模式）](../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E7%BB%93%E6%9E%84%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E9%80%82%E9%85%8D%E5%99%A8%E6%A8%A1%E5%BC%8F%20%E2%AD%90%202b037a9aa2cd47c59d02cdc4054ad619.md)
6. **模板模式：**Spring IOC 容器在初始化工程中，使用的 `AbstractApplicationContext` 的 `refresh()` 方法是一个模板方法[（详见 设计模式 模板模式）](../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E8%A1%8C%E4%B8%BA%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E6%A8%A1%E6%9D%BF%E6%A8%A1%E5%BC%8F%20%E2%AD%90%20b96bea7eec194ba69802ece0f40d8449.md)
7. **职责链模式：**
    - Spring AOP 中增强方法与被增强方法则组织[（详见 设计模式 职责链模式）](../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E8%A1%8C%E4%B8%BA%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E8%B4%A3%E4%BB%BB%E9%93%BE%E6%A8%A1%E5%BC%8F%20%E2%AD%90%203512b3bd8cfe4a49a9935baee9352faf.md)
    - Spring MVC 中拦截器与处理器中的业务逻辑方法组织成了一个执行链[（详见 设计模式 职责链模式）](../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E8%A1%8C%E4%B8%BA%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E8%B4%A3%E4%BB%BB%E9%93%BE%E6%A8%A1%E5%BC%8F%20%E2%AD%90%203512b3bd8cfe4a49a9935baee9352faf.md)

# 3. 快速开始

1. 下载Spring5所依赖的jar包
    1. 选取Spring5.x版本
    2. 下载地址：

        [Index of release/org/springframework/spring](https://repo.spring.io/release/org/springframework/spring/)

2. 导入Spring基本包

    ```java
     //4个核心基本包
     spring-beans-5.2.6.RELEASE
     spring-context-5.2.6.RELEASE
     spring-core-5.2.6.RELEASE
     spring-expression-5.2.6.RELEASE
     
     //日志包
     commons-logging-1.1.1
    ```

3. 创建User类

    ```java
     package com.at.spring5;
     
     public class User {
         public void add(){
             System.out.println("add....");
         }
     }
    ```

4. 使用配置文件创建一个User对象：配置bean.xml（不再使用new的方式）

    ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <beans xmlns="http://www.springframework.org/schema/beans"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
     
            <!--配置User对象创建-->
            <bean id="user" class="com.at.spring5.User"></bean>
     </beans>
    ```

5. 创建测试类

    ```java
     package com.test;
     
     import com.at.spring5.User;
     import org.junit.Test;
     import org.springframework.context.ApplicationContext;
     import org.springframework.context.support.ClassPathXmlApplicationContext;
     
     public class testdemo {
         @Test
         public void testadd(){
             //1.加载spring配置文件（ApplicationContext在加载配置文件时，就将对象创建好了）
             ApplicationContext context = new ClassPathXmlApplicationContext("bean1.xml");
     
             //2. 通过id值 获取 配置中已经创建好的对象
             User user = context.getBean("user", User.class);
     
             System.out.println(user);
             user.add();
         }
     }
    ```

6. 测试结果

    ```java
     com.at.spring5.User@4466af20    //打印user对象的地址
     add....                         //执行user对象的方法
    ```