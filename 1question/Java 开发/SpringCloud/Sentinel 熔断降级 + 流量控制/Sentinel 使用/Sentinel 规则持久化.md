---
title: "Sentinel 规则持久化"
tags:
  - "Spring_Cloud"
  - "Sentinel_规则持久化"
  - "熔断降级"
  - "Sentinel"
  - "Nacos"
  - "线程"
updated: 2026-04-16
---

# 一、存在的问题

一旦我们重启应用，sentinel规则将消失，生产环境需要将配置规则进行持久化

# 二、整合 Nacos 对 Sentinel 规则进行持久化
1. 解决方法：
    1. 将限流配置规则持久化进Nacos保存，只要刷新被监控服务的某个rest地址
    2. sentinel控制台的流控规则就能看到，只要Nacos里面的配置不删除，针对被监控服上sentinel上的流控规则持续有效
2. 对 84 模块进行修改
3. 添加依赖

    ```XML
    <dependency>
        <groupId>com.alibaba.csp</groupId>
        <artifactId>sentinel-datasource-nacos</artifactId>
    </dependency>
    ```
4. 在配置文件中指定 去nacos 上读取哪个 流量控制配置文件

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
5. 在 nacos 上新建 流控规则

    ![[IMG-20260404031843601.png|800]]

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
        2. limitApp：来源应用
        3. grade：阈值类型，0表示线程数，1表示QPS
        4. count：单机阈值
        5. strategy：流控模式，0表示直接，1表示关联，2表示链路
        6. controlBehavior：流控效果，0表示快速失败，1表示Warm Up，2表示排队等待
        7. clusterMode：是否集群
6. 启动 nacos、sentinel、9003、9004、84
7. **需要先正常调用一次 被监控服务的某一个 rest 请求，sentinel 才能加载流控规则配置文件**：[http://localhost:84/consumer/fallback/1](http://localhost:84/consumer/fallback/1)
8. **查看 sentinel 上的流控规则（自动去nacos上读取了流控规则配置文件）**

    ![[Attachment/1question/大数据/Java 开发/SpringCloud/Sentinel 熔断降级 + 流量控制/Sentinel 使用/IMG-20260405035414947.png|800]]

9. 直接高并发访问：[http://localhost:84/consumer/fallback/1](http://localhost:84/consumer/fallback/1)

    **持久化在nacos上的流控规则生效**

![[IMG-20260405035420395.png|524]]

10. 此时将 84 停止，sentinel 上的流控规则就消失了
