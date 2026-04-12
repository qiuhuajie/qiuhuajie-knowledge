- [[#1. 广播模式 概述]]
- [[#2. 代码实现]]
    - [[#2.1 队列、交换机 的声明和绑定]]
    - [[#2.2 消息发送]]
    - [[#2.3 消息接受]]
- [[#3. 测试]]
# 1. **广播模式 概述**
1. `Fanout`，英文翻译是扇出，在MQ中叫广播更合适
1. `Fanout Exchange` 会将接收到的消息广播到每一个跟其绑定的queue
    
    ![[IMG-20260404031928274.png]]
    
1. 在广播模式下，消息发送流程是这样的：
    
    1. 可以有多个队列
    
    1. 每个队列都要绑定到Exchange（交换机）
    
    1. 生产者发送消息到交换机
    
    1. ==**交换机把消息发送给绑定过的所有队列（广播）**==
    
    1. 订阅队列的消费者都能拿到消息
    
# 2. **代码实现**
- 示例：FanoutExchange的使用
- 实现思路如下：
    
    ![[IMG-20260404031928328.png]]
    
    1. 在consumer服务中，利用代码声明队列、交换机，并将两者绑定
    
    1. 在consumer服务中，编写两个消费者方法，分别监听fanout.queue1和fanout.queue2
    
    1. 在publisher中编写测试方法，向itcast.fanout发送消息
    
## 2.1 **队列、交换机 的声明和绑定**
1. SpringAMQP提供了声明交换机、队列、绑定关系的API，例如：
    
    ![[IMG-20260404031928374.png]]
    
1. ⭐在 `consumer` 服务常见一个类，添加 `@Configuration` 注解，并使用注解 `@Bean` 声明
    
    - **交换机：`FanoutExchange`**
    
    - **队列：`Queue`**
    
    - **绑定关系对象：`Binding`**
    
    ```Java
     @Configuration
     public class FanoutConfig {
         // 声明交换机：itcast.fanout
         @Bean
         public FanoutExchange fanoutExchange(){
             return new FanoutExchange("itcast.fanout");
         }
     
         // 声明队列1：fanout.queue1
         @Bean
         public Queue fanoutQueue1(){
             return new Queue("fanout.queue1");
         }
     
         // 绑定队列1到交换机
         @Bean
         public Binding fanoutBinding1(Queue fanoutQueue1, FanoutExchange fanoutExchange){
             return BindingBuilder
                     .bind(fanoutQueue1)
                     .to(fanoutExchange);
         }
     
         // 声明队列2：fanout.queue2
         @Bean
         public Queue fanoutQueue2(){
             return new Queue("fanout.queue2");
         }
     
         // 绑定队列2到交换机
         @Bean
         public Binding fanoutBinding2(Queue fanoutQueue2, FanoutExchange fanoutExchange){
             return BindingBuilder
                     .bind(fanoutQueue2)
                     .to(fanoutExchange);
         }
     }
    ```
    
## 2.2 **消息发送**
在publisher服务的SpringAmqpTest类中添加测试方法：
```Java
 @RunWith(SpringRunner.class)
 @SpringBootTest
 public class SpringAmqpTest {
     @Autowired
     private RabbitTemplate rabbitTemplate;
 
     @Test
     public void testSendFanoutExchange() {
         // 交换机名称
         String exchangeName = "itcast.fanout";
         // 消息
         String message = "hello, every one!";
         // 发送消息（⭐之前是将消息发送给队列，现在是发送给交换机，再由交换机将消息广播给队列）
         rabbitTemplate.convertAndSend(exchangeName, "", message);
     }
 }
```
## 2.3 **消息接受**
在consumer服务的`SpringRabbitListener`类中，添加两个方法，分别监听`fanout.queue1`和`fanout.queue2`：
```Java
 @Component
 public class SpringRabbitListener {
 
     @RabbitListener(queues = "fanout.queue1")
     public void listenFanoutQueue1(String msg) {
         System.out.println("消费者接收到fanout.queue1的消息：【" + msg + "】");
     }
 
     @RabbitListener(queues = "fanout.queue2")
     public void listenFanoutQueue2(String msg) {
         System.out.println("消费者接收到fanout.queue2的消息：【" + msg + "】");
     }
 }
```
# 3. **测试**
1. 启动consumer服务
1. 然后在publisher服务中运行测试代码，发送MQ消息
1. consumer 服务控制台：
    
    **一个发布者发布消息，**==**所有与交换机**== `**itcast.fanout**` ==**绑定的所以队列中都会有这个消息**==**，而监听队列的消费者就会收到消息**
    
    ![[IMG-20260404031928490.png]]