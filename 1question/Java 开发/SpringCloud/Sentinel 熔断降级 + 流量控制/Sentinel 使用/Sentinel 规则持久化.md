- [[#1. 存在的问题]]
- [[#2. 整合 Nacos 对 Sentinel 规则进行持久化]]
# 1. **存在的问题**
一旦我们重启应用，sentinel规则将消失，生产环境需要将配置规则进行持久化
# 2. **整合 Nacos 对 Sentinel 规则进行持久化**
1. 解决方法：
    
    1. 将限流配置规则持久化进Nacos保存，只要刷新被监控服务的某个rest地址
    
    1. sentinel控制台的流控规则就能看到，只要Nacos里面的配置不删除，针对被监控服上sentinel上的流控规则持续有效
    
1. 对 84 模块进行修改
1. 添加依赖
    
    ```XML
    <dependency>
        <groupId>com.alibaba.csp</groupId>
        <artifactId>sentinel-datasource-nacos</artifactId>
    </dependency>
    ```
    
1. 在配置文件中指定 去nacos 上读取哪个 流量控制配置文件
    
    ```YAML
    server:
      port: 84
    
    spring:
      application:
        name: cloudalibaba-sentinel-service
      cloud:
        nacos:
          discovery:
            server-addr: localhost:8848
        sentinel:
          transport:
            dashboard: localhost:8080
            port: 8719
          datasource: # ⭐
            ds1:
              nacos:
                server-addr: localhost:8848
                dataId: cloudalibaba-sentinel-service # ⭐这里的id 要与nacos上的配置文件对应，否则sentinel不知道去nacos上找哪个配置文件
                groupId: DEFAULT_GROUP
                data-type: json
                rule-type: flow
    
    management:
      endpoints:
        web:
          exposure:
            include: '*'
    
    feign:
      sentinel:
        enabled: true
    ```
    
1. 在 nacos 上新建 流控规则
    
    ![[IMG-20260404031843601.png|Untitled 507.png]]
    
    ```Java
    [
        {
            "resource": "/consumer/fallback/1",
            "limitApp": "default",
            "grade": 1,
            "count": 1,
            "strategy": 0,
            "controlBehavior": 0,
            "clusterMode": false
        }
    ]
    ```
    
    - 解析：
        
        1. resource：资源名称
        
        1. limitApp：来源应用
        
        1. grade：阈值类型，0表示线程数，1表示QPS
        
        1. count：单机阈值
        
        1. strategy：流控模式，0表示直接，1表示关联，2表示链路
        
        1. controlBehavior：流控效果，0表示快速失败，1表示Warm Up，2表示排队等待
        
        1. clusterMode：是否集群
        
    
1. 启动 nacos、sentinel、9003、9004、84
1. **需要先正常调用一次 被监控服务的某一个 rest 请求，sentinel 才能加载流控规则配置文件**：[http://localhost:84/consumer/fallback/1](http://localhost:84/consumer/fallback/1)
1. **查看 sentinel 上的流控规则（自动去nacos上读取了流控规则配置文件）**
    
    ![[Attachment/1question/大数据/Java 开发/SpringCloud/Sentinel 熔断降级 + 流量控制/Sentinel 使用/IMG-20260405035414947.png|Untitled 1 374.png]]
    
1. 直接高并发访问：[http://localhost:84/consumer/fallback/1](http://localhost:84/consumer/fallback/1)
    
    **持久化在nacos上的流控规则生效**
    
    ![[IMG-20260405035420395.png|Untitled 2 304.png]]
    
1. 此时将 84 停止，sentinel 上的流控规则就消失了