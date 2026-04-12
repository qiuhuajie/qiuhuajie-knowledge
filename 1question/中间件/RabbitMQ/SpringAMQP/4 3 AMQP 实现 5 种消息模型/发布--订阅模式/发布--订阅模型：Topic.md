- [[#1. Topic 模式 概述]]
- [[#2. 代码实现]]
    - [[#2.1 基于注解的 队列、交换机 的声明和绑定]]
    - [[#2.2 消息发送]]
    - [[#2.3 消息接收]]
- [[#3. 测试]]
# 1. **Topic 模式 概述**
1. 使用场景：
    
    1. `TopicExchange`与`DirectExchange`类似，区别在于以下两点：
        
        1. **`TopicExchange` 的 `routingKey` 一般是**==**多个单词的列表**==**，并且以 `.` 分割**
        
        1. **`TopicExchange` 可以在声明 `Bingding key` 的时候使用**==**通配符**==
            
            - 通配符规则：
                
                - `#`：代指0个或多个单词
                
                - `*`：代指一个单词
                
            
        
    
1. 举例：
    
    ![[Attachment/1question/中间件/RabbitMQ/SpringAMQP/4 3 AMQP 实现 5 种消息模型/发布--订阅模式/IMG-20260405035438387.png]]
    
    - 队列1 会收到，所有有关 china 的消息
        
        - Queue1：绑定的是 `**china.#**` ，因此凡是以 china.开头的routing key 都会被匹配到。包括china.news和china.weather
        
    
    - 队列2 会收到，所有有关 japan 的消息
        
        - Queue2：绑定的是 `**#.news**` ，因此凡是以 .news结尾的 routing key 都会被匹配。包括china.news和japan.news
        
    
    - 队列3 会收到，所有有关 天气 的消息
    
    - 队列4 会收到，所有有关 新闻 的消息
    
# 2. **代码实现**
- 示例：TopicExchange的使用
- 实现思路如下：
    
    ![[IMG-20260405035455633.png]]
    
    1. 并利用@RabbitListener声明Exchange、Queue、RoutingKey
    
    1. 在consumer服务中，编写两个消费者方法，分别监听topic.queue1和topic.queue2
    
    1. 在publisher中编写测试方法，向itcast. topic发送消息
    
## 2.1 **基于注解的 队列、交换机 的声明和绑定**
在接受消息的监听类里，在注解`@RabbitListener`上，使用`@QueueBinding`注解来声明 `bingdings` 属性
## 2.2 **消息发送**
```Java
 @RunWith(SpringRunner.class)
 @SpringBootTest
 public class SpringAmqpTest {
     @Autowired
     private RabbitTemplate rabbitTemplate;
 
     @Test
     public void testSendTopicExchange() {
         // 交换机名称
         String exchangeName = "itcast.topic";
         // 消息
         String message = "今天天气不错，我的心情好极了!";
         // 发送消息
         rabbitTemplate.convertAndSend(exchangeName, "china.weather", message);
     }
 }
```
## 2.3 **消息接收**
```Java
 @Component
 public class SpringRabbitListener {
 
     @RabbitListener(bindings = @QueueBinding(
             value = @Queue(name = "topic.queue1"),
             exchange = @Exchange(name = "itcast.topic", type = ExchangeTypes.TOPIC),
             key = "china.#"
     ))
     public void listenTopicQueue1(String msg){
         System.out.println("消费者接收到topic.queue1的消息：【" + msg + "】");
     }
 
     @RabbitListener(bindings = @QueueBinding(
             value = @Queue(name = "topic.queue2"),
             exchange = @Exchange(name = "itcast.topic", type = ExchangeTypes.TOPIC),
             key = "#.news"
     ))
     public void listenTopicQueue2(String msg){
         System.out.println("消费者接收到topic.queue2的消息：【" + msg + "】");
     }
 }
```
# 3. **测试**
1. 启动consumer服务
1. 然后在publisher服务中运行测试代码，发送MQ消息
1. consumer 服务控制台：
    
    ![[IMG-20260405035509045.png]]