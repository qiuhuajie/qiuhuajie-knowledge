- [[#Gateway 工作流程]]
- [[#1. 断言]]
- [[#2. 动态路由]]
- [[#3. 过滤器]]
# **Gateway 工作流程**

==**断言判断**== **+** ==**路由转发**== **+** ==**执行过滤器链**==

```YAML
spring:
  cloud:
    gateway:
      routes:
        - id: route_thirdparty # 第三方微服务路由规则
          uri: lb://passjava-thirdparty # 动态路由 & 负载均衡，将请求转发到注册中心注册的 passjava-thirdparty 服务
          predicates: # 断言
            - Path=/api/thirdparty/** # 如果前端请求路径包含 api/thirdparty，则应用这条路由规则
          filters: # 过滤器
            - RewritePath=/api/(?<segment>.*),/$\{segment} # 将跳转路径中包含的api替换成空
```
# 1. **断言**
1. 在启动 cloud-gateway-gateway9527 时，会发现加载了很多的 路由断言工厂
    

    ![[IMG-20260405035413881.png|Untitled 342.png]]

    

    **Spring Cloud Gateway 包括许多内置的 Route Predicate 工厂**

    
1. **工作机制**：==如果客户端发送的请求满足了断言的条件，则映射到指定的路由器，就能转发到指定的服务上进行处理==
    
    1. 这些 Predicate 与HTTP请求的不同属性匹配
    
    1. 多个 Route Predicate 可以进行组合
    
1. 底层在创建 Route 对象时， 使用 RoutePredicateFactory 创建 Predicate 对象，Predicate 对象可以赋值给 Route
1. **断言和路由的匹配规则**：
    
    - ==一对多==：一个路由规则可以包含多个断言
    
    - ==同时满足==：如果一个路由规则中有多个断言，则需要同时满足才能匹配
    
    - ==第一个匹配成功==：如果一个请求可以匹配多个路由，则映射第一个匹配成功的路由
    
1. 常用的 Route Predicate
    
    - 查看
        
        1. After Route Predicate
            
            ```Plain
             predicates:
                 - After=2020-02-05T15:10:03.685+08:00[Asia/Shanghai]
            ```
            
        
        1. Before Route Predicate
            
            ```Plain
             predicates:
                 - Before=2020-02-05T15:10:03.685+08:00[Asia/Shanghai]
            ```
            
        
        1. Between Route Predicate
            
            ```Plain
             predicates:
                 - Between=2020-02-02T17:45:06.206+08:00[Asia/Shanghai],2020-03-25T18:59:06.206+08:00[Asia/Shanghai]
            ```
            
        
        1. Cookie Route Predicate
            
            ```Plain
             predicates:
                 - Cookie=username,zzyy  # 请求中要有{username,zzyy}这个键值对
            ```
            
        
        1. Header Route Predicate
            
            ```Plain
             predicates:
                 - Header=X-Request-Id, \d+  # 请求头要有X-Request-Id属性并且值为整数的正则表达式
            ```
            
        
        1. Host Route Predicate
            
            ```Plain
             predicates:
                 - Host=**.atguigu.com
            ```
            
        
        1. Method Route Predicate
            
            ```Plain
             predicates:
                 - Method=GET
            ```
            
        
        1. Path Route Predicate
            
            ```Plain
             predicates:
                 - Path=/payment/lb/**
            ```
            
        
        1. Query Route Predicate
            
            ```Plain
             predicates:
                 - Query=username, \d+  # 要有参数名username并且值还要是整数才能路由
            ```
            
        
    
# 2. 动态**路由**
1. **动态路由**
    
    1. 当服务集群添加一个微服务，或者 IP 地址更换了，Gateway 都是可以感知到的
    
    1. 但是 Gateway 的配置是不需要更新的
    
    1. 这里的动态指的是==微服务的集群个数、IP 和端口是动态可变的==
    
1. **配置项**：由ID、目标URI、一系列的断言和过滤器组成
1. **动态路由示例**
    
    1. 将 URL 配置为：`uri: lb://cloud-payment-service` ，即 ==lb 协议 + 注册中心上的微服务名==
    
    1. Gateway 会==根据注册中心注册的服务列表，找到对应服务具体的 IP + 端口，进而创建动态路由进行转发==
    
    1. yaml 配置文件
        
        ```YAML
         server:
           port: 9527
         
         spring:
           application:
             name: cloud-gateway
           cloud:
             gateway:
               # 多个路由
               routes:
                 - id: payment_routh
                   # uri: http://localhost:8001
                   uri: lb://cloud-payment-service  # ⭐使用注册中心上微服务名，为Eureka 上注册的所有服务，创建动态路由进行转发
                                                                                 # 格式：uri: 协议名://微服务名
                                                                                 # ⭐当前uri的协议为lb，表示启用Gateway的负载均衡功能，在微服务中自动为我们创建的负载均衡uri
                   predicates:
                     - Path=/payment/get/**          # 断言：（Path）若请求路径与Path的路径相匹配，则路由转发访问 uri 中的地址
         
                 - id: payment_routh2
                   # uri: http://localhost:8001
                   uri: lb://cloud-payment-service
                   predicates:
                     - Path=/payment/lb/**  # 这里的 lb 是 基础8001（没有负载均衡）上的一个controller 请求映射
         
                 - id: payment_routh3
                   uri: https://www.bilibili.com/
                   predicates:
                     - Path=/bilibili
         
         eureka:
           ...\#同上
        ```
        
    
    1. 测试：[http://localhost:9527/payment/lb](http://localhost:9527/payment/lb)
        
        - 8002、8001交替出现
            

            ![[IMG-20260404031837784.png|Untitled 1 258.png]]

            
        
        - 也即==当路由的 uri 使用的是 lb 协议时：Gateway 可以像 Ribbon 一样 实现 负载均衡==
        
    
1. 因此**一个请求的转发过程**
    
    1. 客户端先将请求发送给 Nginx，然后转发到网关，网关经过断言匹配到一个路由后，将请求转发给指定 uri
    
    1. 这个 uri 可以配置成 微服务的名字，比如 passjava-member
    
    1. ==动态路由==：Gateway 从注册中心拉取注册表，就能知道服务名对应具体的 IP + 端口
    
    1. ==负载均衡==：如果一个服务部署了多台机器，则还可以通过负载均衡进行请求的转发
    
    1. 原理如下图所示：
        

        ![[IMG-20260405035420289.png|Untitled 2 216.png]]

        
    
# 3. **过滤器**
1. 过滤器的作用：==规定一些你在 用服务前 和 用服务之后 要执行的操作==
    
    1. 在路由过滤器中可以通过 `ServerWebExchange` 拿到请求的一些属性
        

        ![[IMG-20260405035421998.png|Untitled 3 165.png]]

        
    
    1. 因此可以通过网关过滤器，实现一些逻辑的处理，比如 ip黑白名单拦截、特定地址的拦截、Token 的合法校验等[[Gateway 项目实战]]
    
1. 多个过滤器也是以执行链的方式串起来，执行顺序可以指定
![[IMG-20260405035432325.png|Untitled 4 135.png]]
1. Spring Cloud Gateway 内置了多种路由过滤器，他们都由 GatewayFilter 的工厂类来产生
1. Spring Cloud Gateway 的 Filter 有两种：
    
    1. GatewayFilter
    
    1. GlobalFilter
    
1. **Filter的配置示例：**
    
    ```YAML
     routes:
         - id: payment_routh
             uri: lb://cloud-provider-payment
             filters:
                 - AddRequestParameter=X-Request-Id,1024 \#过滤器工厂会在匹配的请求头加上一对请求头，名称为X-Request-Id值为1024
             predicates:
                 - Path=/paymentInfo/**
                 - Method=GET,POST
    ```
    
1. ==**示例：自定义一个全局过滤器：GlobalFilter**==
    
    1. 在 9527 上写一个 过滤器：MyLogGateWayFilter **（需要实现 `GlobalFilter`、`Ordered` 两个接口）**
        
        ```Java
         @Component //必须加，必须加，必须加
         public class MyLogGateWayFilter implements GlobalFilter, Ordered {
         
             //写过滤器逻辑
             @Override
             public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
         
                 //获取当前请求的 name 参数值
                 String uname = exchange.getRequest().getQueryParams().getFirst("uname");
                 //如果没有输入参数的处理
                 if (uname == null) {
                     System.out.println("****用户名为null，无法登录");
                     //给响应设置状态码
                     exchange.getResponse().setStatusCode(HttpStatus.NOT_ACCEPTABLE);
                     //将 exchange 返回响应，中止过滤器链
                     return exchange.getResponse().setComplete();
                 }
                 //处理完后，交给过滤器链的下一个过滤器处理
                 return chain.filter(exchange);
             }
         
             //设置执行顺序
             @Override
             public int getOrder() {
                 return 0;
             }
         }
        ```
        
    
    1. **测试：**
        
        1. **启动 7001、8001、8002**
        
        1. **请求带参数：正常访问**
            

            ![[IMG-20260405035444596.png|Untitled 5 112.png]]

            
        
        1. **请求不带参数：访问被拒绝**
            

            ![[IMG-20260405035504868.png|Untitled 6 93.png]]