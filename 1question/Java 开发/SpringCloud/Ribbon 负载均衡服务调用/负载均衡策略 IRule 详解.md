- [[#1. IRule]]
- [[#2. 替换负载均衡算法]]
- [[#3. 轮询算法源码分析]]
- [[#4. 自定义轮询算法]]
# 1. **IRule**
1. IRule：**根据特定算法中从服务列表中选取一个要访问的服务**
1. IRule 接口的各种实现类：
    
    ![[IMG-20260405035413899.png|Untitled 347.png]]
    
    1. **RoundRobinRule：轮询**
    
    1. **RandomRule：随机**
    
    1. **RetryRule：**先按照RoundRobinRule的策略获取服务，如果**获取服务失败**则在指定时间内会进行**重试**，获取可用的服务
    
    1. **WeightedResponseTimeRule：**对RoundRobinRule的扩展，响应速度越快的实例选择**权重**越大，越容易被选择
    
    1. **BestAvailableRule：**会先**过滤掉由于多次访问故障而处于断路器跳闸状态的服务**，然后选择一个并发量最小的服务
    
    1. AvailabilityFilteringRule：先过滤掉故障实例，再选择并发较小的实例
    
    1. ZoneAvoidanceRule：默认规则，复合判断server所在区域的性能和server的可用性选择服务器
    
# 2. **替换负载均衡算法**

> [!important] 之前使用的是轮询的负载均衡算法，现在实现
> 
> **让 cloud-consumer-order80 调用 8001 时，使用随机的负载均衡算法**
1. **新建 com.atguigu.myrule 目录**
1. **新建配置类：com.atguigu.myrule.MySelfRule（配置负载均衡算法组件）**
    
    1. 官方文档明确给出了**警告**：这个自定义配置类不能放在 **@ComponentScan（主启动类MainApp80的@SpringBootApplication的子注解）** 所扫描的当前包下以及子包下
    
    1. 否则我们自定义的这个配置类就会被所有的 Ribbon 客户端所共享，达不到特殊化定制的目的了
        
        ![[IMG-20260404031842690.png|Untitled 1 261.png]]
        
    
1. **MySelfRule.class**
    
    ```Java
     @Configuration
     public class MySelfRule {
         @Bean
         public IRule myRule() {
             //默认的是轮询，现在要定义成随机
             return new RandomRule();
         }
     }
    ```
    
1. **主启动类中添加注解：@RibbonClient**
    
    ```Java
     @SpringBootApplication
     @EnableEurekaClient
     
     //⭐@RibbonClient注解：标明对"CLOUD-PAYMENT-SERVICE"服务，使用MySelfRule.class定义的负载均衡算法
     @RibbonClient(name = "CLOUD-PAYMENT-SERVICE",configuration= MySelfRule.class)
     public class MainApp80 {
         public static void main(String[] args) {
             SpringApplication.run(MainApp80.class,args);
         }
     }
    ```
    
1. **测试：**
    
    1. 依次启动 7001、7002、8001、8002、80
    
    1. [http://localhost/consumer/payment/get/1](http://localhost/consumer/payment/get/1)
    
    1. 服务端口8001 和 8002 **随机出现**
        
        ![[IMG-20260405035420308.png|Untitled 2 219.png]]
        
    
# 3. **轮询算法源码分析**
1. **轮询算法的原理：**
    
    1. 算法核心：==**rest接口第几次请求数 % 服务器集群总数量 = 实际调用服务器位置下标**== （每次服务重启动后rest接口计数从1开始）
    
    1. **step1：获取服务的所有实例：**
        
        ```Java
         List<ServiceInstance> instances = discoveryClient.getInstances("CLOUD-PAYMENT-SERVICE");
        ```
        
    
    1. **step2：确定调用哪个服务实例：**
        
        1. 当前：List [0] instances = 127.0.0.1:8002  
            List [1] instances = 127.0.0.1:8001
        
        1. 8001+ 8002 组合成为集群，它们共计2台机器，集群总数为2， 按照轮询算法原理：
            
            1. 当总请求数为1时： **1 % 2 =1** 对应下标位置为1 ，则获得服务地址为127.0.0.1:8001
            
            1. 当总请求数位2时： 2 % 2 =0 对应下标位置为0 ，则获得服务地址为127.0.0.1:8002
            
            1. 当总请求数位3时： 3 % 2 =1 对应下标位置为1 ，则获得服务地址为127.0.0.1:8001
            
            1. 当总请求数位4时： 4 % 2 =0 对应下标位置为0 ，则获得服务地址为127.0.0.1:8002
            
            1. 如此类推......
            
        
    
1. 源码：
    
    ```Java
     public class RoundRobinRule extends AbstractLoadBalancerRule {
    
         private AtomicInteger nextServerCyclicCounter;
     
             ...
         //new 一个原子操作类的 AtomicInteger，用于记录当前请求数
         public RoundRobinRule() {
             this.nextServerCyclicCounter = new AtomicInteger(0);
         }
     
         ....
     
         public Server choose(ILoadBalancer lb, Object key) {
             if (lb == null) {
                 log.warn("no load balancer");
                 return null;
             } else {
                 Server server = null;
                 int count = 0;
     
                 while(true) {
                     if (server == null && count++ < 10) {
                         //获取所有可达（活着）服务
                         List<Server> reachableServers = lb.getReachableServers();
                         //获取所有服务（服务器集群的服务总数）
                         List<Server> allServers = lb.getAllServers();
    
                         int upCount = reachableServers.size();
                         int serverCount = allServers.size();
                         //通过大小判断，如果上面两个 list 大小为 0，则报异常
                         if (upCount != 0 && serverCount != 0) {
    
                             //获取提供服务的服务角标（选哪个服务）
                             int nextServerIndex = this.incrementAndGetModulo(serverCount);
    
                             //通过角标获取最终要调用的服务
                             server = (Server)allServers.get(nextServerIndex);
    
                             if (server == null) {
                                 Thread.yield();
                             } else {
                                 if (server.isAlive() && server.isReadyToServe()) {
                                     return server;
                                 }
                                 server = null;
                             }
                             continue;
                         }
     
                         log.warn("No up servers available from load balancer: " + lb);
                         return null;
                     }
     
                     if (count >= 10) {
                         log.warn("No available alive servers after 10 tries from load balancer: " + lb);
                     }
     
                     return server;
                 }
             }
         }
     
         //获取提供服务的服务角标（选哪个服务），将当前服务器集群的服务总数作为参数传入，用于取余，来选服务
         private int incrementAndGetModulo(int modulo) {
             int current;
             int next;
             do {
    
                 //获取当前请求数current
                         //因为 current 唯一做的操作就是自增+1
                         //ServerCyclicCounter是一个原子操作类的integer：AtomicInteger（线程安全的）
                 current = this.nextServerCyclicCounter.get();
    
                 //取余
                 next = (current + 1) % modulo;
    
             } while(!this.nextServerCyclicCounter.compareAndSet(current, next));
             //将当前值current与next值作比较，如果不同则交换？（看不懂：需要看JUC-->CAS+自旋锁）
             //自旋锁：判断当前如果只有一个人操作 next， 则将 next 返回
     
             return next;
         }
             ...
     }
    ```
    
# 4. **自定义轮询算法**
1. **服务消费者 80 端**
    
    1. 首先**让 Ribbon 自带的负载均衡算法失效**：在配置RestTemplate的配置类ApplicationContextBean中，==**注释掉注解 @LoadBalanced**==
        
        ```Java
         @Configuration
         public class ApplicationContextConfig {
             @Bean
             //@LoadBalanced //使用@LoadBalanced注解赋予RestTemplate负载均衡的能力
             public RestTemplate restTemplate(){
                 return new RestTemplate();
             }
         }
        ```
        
    
    1. **业务层：**
        
        1. 定义一个 LoadBalancer接口，向外提供我们自定义的负载均衡算法的使用接口（在controller层调用）
            
            ```Java
             public interface LoadBalancer {
                 //获取 根据当前使用的负载均衡算法确定的要调用的目标服务实例（8001还是8002）
                 ServiceInstance instances(List<ServiceInstance> serviceInstances);
             }
            ```
            
            > [!important] ==**ServiceInstance**==
            > 
            > - 所在包：package org.springframework.cloud.client
            > 
            > - ServiceInstance 代表在服务发现系统中的一个实例，也就是说可以被 ServiceInstanceChooser 选择
            
        
        1. LoadBalancer接口的实现类：（自定义算法的具体实现）
            
            ```Java
             @Component
             public class MyLB implements LoadBalancer {
                 private AtomicInteger atomicInteger = new AtomicInteger(0);
             
                 @Override
                 public ServiceInstance instances(List<ServiceInstance> serviceInstances) {
                     //使用 轮询的负载均衡算法，得到目标服务实例的下标
                     int index = getAndIncrement() % serviceInstances.size();
                     return serviceInstances.get(index);
                 }
             
                 // 取得请求的统计数
                 public final int getAndIncrement() {
                     int current;
                     int next;
                     do {
                         current = this.atomicInteger.get();
                         //请求数大于上限，重新从0取值
                         next = current >= 2147483647 ? 0 : current + 1;
                     } while(!this.atomicInteger.compareAndSet(current, next));
                     System.out.println("调用的服务在服务列表中的下标："+next);
                     return next;
                 }
             }
            ```
            
        
        > [!important]
        > 
        > 可以看到，具体使用哪种 负载均衡算法（业务层） 都是在服务消费者端定义的，⭐进一步验证了 Ribbon 是一套客户端（服务消费端）负载均衡的工具
        
    
    1. **Controller 层：**用于调用自定义的算法，验证是否是遵循自定义的轮询方式，调用服务
        
        ```Java
         @RestController
         public class OrderController {
         
             ...
         
             @Resource
             private LoadBalancer loadBalancer;
             @Resource
             private DiscoveryClient discoveryClient;
         
             @GetMapping("/consumer/payment/lb")
             public String getPaymentLB() {
         
                 //获取"CLOUD-PAYMENT-SERVICE"服务的全部实例
                 List<ServiceInstance> instances = discoveryClient.getInstances("CLOUD-PAYMENT-SERVICE");
         
                 //判空处理
                 if(instances == null || instances.size()<=0) {
                     return null;
                 }
         
                 //将全部实例的List 传入自定义的loadBalancer算法接口，返回要调用的具体实例（8001 or 8002）
                 ServiceInstance serviceInstance = loadBalancer.instances(instances);
         
                 //得到目标实例的URI
                 URI uri = serviceInstance.getUri();
         
                 //使用 URI 拼接请求，远程调用 目标服务实例提供的服务
                 return restTemplate.getForObject(uri+"/payment/lb",String.class);
             }
         }
        ```
        
    
1. **服务提供者 8001 8002 端**
    
    修改Controller，方便测试：在请求服务后，返回调用的请求的端口号，以验证当前调用的是哪个端口
    
    ```Java
     @GetMapping(value = "/payment/lb")
     public String getPaymentLB() {
         return serverPort;
     }
    ```
    
1. **测试**
    
    1. 启动 7001 7002
    
    1. 启动 8001 8002
    
    1. 启动 80 ：[http://localhost/consumer/payment/lb](http://localhost/consumer/payment/lb)**（8001、8002 交替出现，自定义轮询实现）**
        
        ![[IMG-20260405035422021.png|Untitled 3 168.png]]