> [!important] **Ribbon 与 RestTemplate 一起实现**
> 
> ==**远程服务调用**==
- [[#1. 请求 URL 使用注册中心的服务名]]
- [[#2. 赋予 RestTemplate 负载均衡的能力：@LoadBalanced]]
- [[#3. 测试]]
# 1. 请求 URL 使用注册中心的服务名
```Java
 @RestController
 public class OrderController {
     //支付服务提供者的请求地址
     //单个支付服务：
     //public static final String PaymentSrv_URL = "http://localhost:8001";
 
     //多个支付服务：
     //⭐这里改写成 eureka 上的服务名，不能写死，否则只能8001和8002具体的一个
     public static final String PaymentSrv_URL = "http://CLOUD-PAYMENT-SERVICE";
 
     @Autowired
     private RestTemplate restTemplate;
 
     @GetMapping("/consumer/payment/create")
     public CommonResult create(Payment payment) {
         return restTemplate.postForObject(PaymentSrv_URL + "/payment/create",payment,CommonResult.class);
     }
 
 
     @GetMapping("/consumer/payment/get/{id}")
     public CommonResult getPayment(@PathVariable Long id) {
         return restTemplate.getForObject(PaymentSrv_URL + "/payment/get/"+id, CommonResult.class, id);
     }
 }
```
# 2. **赋予 RestTemplate 负载均衡的能力：**`**@LoadBalanced**`
```Java
 @Configuration
 public class ApplicationContextConfig {
     @Bean
     @LoadBalanced //使用@LoadBalanced注解赋予RestTemplate负载均衡的能力
     public RestTemplate restTemplate(){
         return new RestTemplate();
     }
 }
```
# 3. **测试**
1. **先要启动 EurekaServer，7001/7002服务，再要启动服务提供者 provider，8001/8002服务**
1. 测试注册：[http://localhost:7001/](http://localhost:7001/) [http://localhost:7002/](http://localhost:7002/)
    
    ![[IMG-20260404031842389.png|Untitled 345.png]]
    
    ![[IMG-20260404031842458.png|Untitled 1 260.png]]
    
1. 测试服务业务：[http://localhost/consumer/payment/get/1](http://localhost/consumer/payment/get/1)
    
    ![[IMG-20260405035420307.png|Untitled 2 218.png]]
    
    ![[IMG-20260405035422020.png|Untitled 3 167.png]]
    
1. **8001和8002交替访问（轮询算法）：负载均衡配置成功**