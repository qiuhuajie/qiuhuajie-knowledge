- [[#1. 工作队列 概述]]
- [[#2. 代码实现]]
    - [[#2.1 消息发送]]
    - [[#2.2 消息接收]]
    - [[#2.3 测试]]
    - [[#2.4 消息预取]]
# 1. **工作队列** 概述
1. **简单队列模型存在的问题：**
    1. 当消息处理比较耗时的时候，可能生产消息的速度会远远大于消息的消费速度
    2. 长此以往，消息就会堆积越来越多，无法及时处理
    3. 此时就可以使用 work queues 模型，多个消费者共同处理消息处理，速度就能大大提高了
2. Work queues，也被称为 Task queues，任务模型
3. 简单来说就是**让**==**多个消费者绑定到一个队列，共同消费队列中的消息**==，但是==**消费者之间是竞争关系**==，也就是说**每条消息只能被一个消费者消费**

    ![[IMG-20260404031928833.png]]

# 2. 代码实现
- 示例：模拟WorkQueue，实现一个队列绑定多个消费者
- 基本思路如下：
    1. 在publisher服务中定义测试方法，每秒产生50条消息，发送到simple.queue
    2. 在consumer服务中定义两个消息监听者，都监听simple.queue队列
    3. 消费者1每秒处理50条消息，消费者2每秒处理10条消息

## 2.1 消息发送
- 发送者每 `20 ms` 发送一条消息，一共发送`50`条，相当于一秒内发送了`50`条消息

    ```Java
    @RunWith(SpringRunner.class)
    @SpringBootTest
    public class SpringAmqpTest {
        @Autowired
        private RabbitTemplate rabbitTemplate;
        @Test
        public void testSendMessage2WorkQueue() throws InterruptedException {
            String queueName = "simple.queue";
            String message = "hello, message__";
            for (int i = 1; i <= 50; i++) {
                rabbitTemplate.convertAndSend(queueName, message + i);
                Thread.sleep(20);
            }
        }
    }
    ```
## 2.2 消息接收
```Java
@Component
public class SpringRabbitListener {
    @RabbitListener(queues = "simple.queue")
    public void listenWorkQueue1(String msg) throws InterruptedException {
        System.out.println("消费者1接收到消息：【" + msg + "】" + LocalTime.now());
        Thread.sleep(20);   //每秒50个
    }
    @RabbitListener(queues = "simple.queue")
    public void listenWorkQueue2(String msg) throws InterruptedException {
        System.err.println("消费者2........接收到消息：【" + msg + "】" + LocalTime.now());
        Thread.sleep(200);  //每秒5个
    }
}
```
## 2.3 测试
1. 启动consumer服务
2. 然后在publisher服务中运行测试代码，发送MQ消息
3. consumer 服务控制台

    ![[IMG-20260404031928896.png]]

## 2.4 消息预取
1. rabbitMQ内部有消息预取机制
    1. 比如有两个消费队列，共同去消费50条消息，即便这两台机器有差异，也会因为消息预取机制，每台机器去抢25条消息，从而影响整体效率

    ![[IMG-20260404031928977.png]]

2. 要解决可以在配置中限制消息预取的数量，原来默认是没有上限，**==现在可以限制为1，即每次处理完当前的消息之后再去队列中获取新的消息==**

    ```YAML
    spring:
      rabbitmq:
        host: 192.168.10.120 # rabbitMQ的ip地址
        port: 5672 # 端口
        username: itcast
        password: 123321
        virtual-host: /
        listener:
          simple:
            prefetch: 1  # ⭐每次只能获取一条消息，处理完才能获取下一个消息
    ```