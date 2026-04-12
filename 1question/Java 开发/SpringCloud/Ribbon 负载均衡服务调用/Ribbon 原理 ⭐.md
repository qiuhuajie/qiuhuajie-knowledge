- [[#Ribbon 拦截请求的原理]]
# **Ribbon 拦截请求的原理**

> [!important]
> 
> `**@LoadBalanced**` **注解是如何赋予 RestTemplate 负载均衡的能力的，负载均衡**==**本质就是获取目标服务的 IP**==
1. **获取服务列表：**Ribbon 会从注册中心获取服务列表，然后**存到 Ribbon 中（客户端负载均衡）**
1. **拦截请求：**
    
    1. **`@LoadBalanced`** 会将 Ribbon 默认的**拦截器 `LoadBalancerInterceptor`** 添加到 RestTemplate 的执行逻辑中
    
    1. 这样所有标注 `@loadBalance` 注解的 RestTemplate，都会被 Ribbon 拦截
    
1. **创建负载均衡器：**
    
    1. 拦截后，Ribbon 会创建一个**负载均衡器 `ILoadBalancer`**
    
    1. 这个负载均衡器**会自动初始化要使用的负载均衡算法、心跳检测，以及加载服务列表**
    
1. **负载均衡和路由转发**
    
    1. 负载均衡器会将 RestTemplate 中的服务名解析为具体的 IP
    
    1. 如果一个服务名有对应的多个 IP，则会使用负载均衡算法做负载均衡
    
    1. 确定好 IP 和 PORT 后，再从 feign 的代理对象中拿到 目标接口的 URL（[[OpenFeign 原理 ⭐]]），就会进行 HTTP 调用
    
![[IMG-20260405035413898.png|Untitled 346.png]]