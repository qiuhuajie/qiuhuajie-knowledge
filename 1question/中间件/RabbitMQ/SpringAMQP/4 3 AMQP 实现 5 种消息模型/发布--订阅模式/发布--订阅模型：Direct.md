---
title: "发布--订阅模型：Direct"
tags:
  - "中间件"
  - "中间件/RabbitMQ"
  - "中间件/RabbitMQ/SpringAMQP"
  - "发布--订阅模型：Direct"
  - "发布--订阅模式"
  - "RabbitMQ"
updated: 2026-04-16
---

# 一、路由模式 概述
1. 使用场景：
    1. 在 `Fanout` 模式中，一条消息，会被所有订阅的队列都消费
    2. 但是，在某些场景下，我们**希望**==**不同的消息被不同的队列消费**==
    3. 这时就要用到`Direct`类型的Exchange
2. `Direct Exchange` 会将接收到的消息根据规则路由到指定的`Queue`，因此称为路由模式（`routes`）
3. 路由模式实现流程：

    ![[IMG-20260404031928043.png|800]]

    1. 队列与交换机的绑定时：**不能是任意绑定了，而是要指定一个⭐`BindingKey`**

    ```Java
     @RabbitListener(bindings = @QueueBinding(
         value = @Queue(name = "direct.queue1"),
         exchange = @Exchange(name = "itcast.direct", type = ExchangeTypes.DIRECT),
         key = {"red", "blue"}   //BindingKey
     ))
     public void listenDirectQueue1(String msg){
         ...
     }
    ```
    2. 消息的发送方**在向 `Exchange`发送消息时：**
        1. **也必须指定消息的⭐ `RoutingKey`**

    ```Java
     rabbitTemplate.convertAndSend(exchangeName, "red", message);
    ```
        2. `Exchange`不再把消息交给每一个绑定的队列，而是**根据消息的`Routing Key`进行判断，只有队列的`Routingkey`与消息的 `Routing key`完全一致，才会接收到消息**

# 二、代码实现
- 示例：DirectExchange的使用
- 实现思路如下：

    ![[IMG-20260404031928102.png|800]]

    1. 利用@RabbitListener声明Exchange、Queue、RoutingKey
    2. 在consumer服务中，编写两个消费者方法，分别监听direct.queue1和direct.queue2
    3. 在publisher中编写测试方法，向itcast. direct发送消息

## 1. ⭐基于注解的 队列、交换机 的声明和绑定
1. 基于`@Bean`的方式声明队列和交换机比较麻烦，**==Spring还提供了基于注解方式来声明==**
    - 在接受消息的监听类里，在注解`@RabbitListener`上，使用`@QueueBinding`注解来声明 `bingdings` 属性：

    ```Java
     @RabbitListener(bindings = @QueueBinding(
         value = @Queue(name = "direct.queue1"),
         exchange = @Exchange(name = "itcast.direct", type = ExchangeTypes.DIRECT),
         key = {"red", "blue"}
     ))
     public void listenDirectQueue1(String msg){
         ...
     }
    ```
## 2. 消息接收

在consumer的SpringRabbitListener中添加两个消费者，同时基于注解来声明队列和交换机：

```Java
 @Component
 public class SpringRabbitListener {
     @RabbitListener(bindings = @QueueBinding(
             value = @Queue(name = "direct.queue1"),
             exchange = @Exchange(name = "itcast.direct", type = ExchangeTypes.DIRECT),
             key = {"red", "blue"}
     ))
     public void listenDirectQueue1(String msg){
         System.out.println("消费者接收到direct.queue1的消息：【" + msg + "】");
     }
     @RabbitListener(bindings = @QueueBinding(
             value = @Queue(name = "direct.queue2"),
             exchange = @Exchange(name = "itcast.direct", type = ExchangeTypes.DIRECT),
             key = {"red", "yellow"}
     ))
     public void listenDirectQueue2(String msg){
         System.out.println("消费者接收到direct.queue2的消息：【" + msg + "】");
     }
 }
```
## 3. 消息发送

在publisher服务的SpringAmqpTest类中添加测试方法：

```Java
 @RunWith(SpringRunner.class)
 @SpringBootTest
 public class SpringAmqpTest {
     @Autowired
     private RabbitTemplate rabbitTemplate;
     @Test
     public void testSendDirectExchange() {
         // 交换机名称
         String exchangeName = "itcast.direct";
         // 消息
         String message = "hello, red!";
         // 发送消息
         rabbitTemplate.convertAndSend(exchangeName, "red", message);
     }
 }
```
# 三、测试
1. 启动consumer服务
2. 然后在publisher服务中运行测试代码，发送MQ消息
3. consumer 服务控制台：
    1. 当`rabbitTemplate.convertAndSend();`传入的路由键是 `red` 时，队列 1、2都可以接收到消息

    ![[IMG-20260404031928128.png|683]]

    2. 如果将消息的路由键改成 `blue`时，只有绑定了路由键`blue`的队列1 才能收到消息

    ![[IMG-20260404031928242.png|576]]
