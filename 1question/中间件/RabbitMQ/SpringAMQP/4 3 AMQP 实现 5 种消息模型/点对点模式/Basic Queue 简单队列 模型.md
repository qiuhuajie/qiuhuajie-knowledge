---
title: "Basic Queue 简单队列 模型"
tags:
  - "中间件"
  - "中间件/RabbitMQ"
  - "中间件/RabbitMQ/SpringAMQP"
  - "点对点模式"
  - "RabbitMQ"
  - "Spring"
updated: 2026-04-16
---

# 一、简单队列 概述
1. 官方的HelloWorld是基于最基础的消息队列模型（简单队列模型）来实现的，只包括三个角色：
    1. `publisher`：消息发布者，将消息发送到队列queue
    2. `queue`：消息队列，负责接受并缓存消息
    3. `consumer`：订阅队列，处理队列中的消息
2. 简单队列模型图：

    ![[Attachment/1question/中间件/RabbitMQ/SpringAMQP/4 3 AMQP 实现 5 种消息模型/点对点模式/IMG-20260405035438387.png|800]]

# 二、代码实现
## 1. 消息发送
- 在`publisher`服务中编写测试类`SpringAmqpTest`，并利用`RabbitTemplate.convertAndSend()`实现消息发送：

    ```Java
     @RunWith(SpringRunner.class)
     @SpringBootTest
     public class SpringAmqpTest {
         @Autowired
         private RabbitTemplate rabbitTemplate;
         @Test
         public void testSimpleQueue() {
             // 队列名称
             String queueName = "simple.queue";
             // 消息
             String message = "hello, spring amqp!";
             // 发送消息
             rabbitTemplate.convertAndSend(queueName, message);
         }
     }
    ```
## 2. 消息接受
1. 在consumer服务的`cn.itcast.mq.listener`包中新建一个类`SpringRabbitListener`
2. 并使用注解`@RabbitListener()`，监听`simple.queue`队列，当队列中有消息时，消息会以参数 `msg`传入方法内，进而写代码处理消息
3. 代码如下：

    ```Java
     @Component
     public class SpringRabbitListener {
         @RabbitListener(queues = "simple.queue")
         public void listenSimpleQueueMessage(String msg) throws InterruptedException {
             System.out.println("spring 消费者接收到消息：【" + msg + "】");
         }
     }
    ```
# 三、测试
1. 启动consumer服务
2. 然后在publisher服务中运行测试代码，发送MQ消息
3. consumer 服务控制台

    ![[IMG-20260405035455736.png|800]]
