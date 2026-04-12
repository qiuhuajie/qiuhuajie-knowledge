- [[#OpenFeign 的核心流程]]
# **OpenFeign 的核心流程**
1. **动态代理对象的生成**
    
    1. OpenFeign 会扫描带有 **`@FeignClient`** 注解的接口，然后为其生成一个动态代理
    
    1. 动态代理对象中使用一个 `Map` 保存接口中每个方法，以及其对应的 **`MethodHandle`**
    
1. **服务调用**
    
    1. ==获取 URL：==当发起一个请求时，从动态代理对象中找到对应的 `MethodHandler` 实例，生成一个 `Request`，包含有目标服务接口的请求 URL
    
    1. ==获取 IP：==再通过负载均衡器 Ribbon 会从服务列表中选取一个 Server，拿到对应的 IP 地址（[[Ribbon 原理 ⭐]]）
    
    1. URL 和 IP 拼接成最后的 URL，就可以发起远程服务调用了
    
![[IMG-20260405035413897.png|640_(9) 2.png]]