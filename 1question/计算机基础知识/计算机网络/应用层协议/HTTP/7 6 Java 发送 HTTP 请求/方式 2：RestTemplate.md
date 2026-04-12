# 1. 介绍
1. RestTemplate提供了多种便捷访问远程Http服务的方法， 如 GET 请求、POST 请求、PUT 请求、DELETE 请求以及一些通用的请求执行方法 exchange 以及 execute
1. 是一种简单便捷的访问restful服务模板类，是Spring提供的用于访问Rest服务的客户端模板工具集
1. 官网地址：
    
    > [!info] RestTemplate (Spring Framework 5.2.2.RELEASE API)  
    > NOTE: As of 5.  
    > [https://docs.spring.io/spring-framework/docs/5.2.2.RELEASE/javadoc-api/org/springframework/web/client/RestTemplate.html](https://docs.spring.io/spring-framework/docs/5.2.2.RELEASE/javadoc-api/org/springframework/web/client/RestTemplate.html)  
    
1. 使用：
    
    1. 使用restTemplate访问restful接口非常的简单粗暴无脑
    
    1. `(url, requestMap, ResponseBean.class)`这三个参数分别代表 REST请求地址、请求参数、HTTP响应转换被转换成的对象类型
    
1. **RestTemplate 提供的方法接口：**
    
    1. **getForObject()：（常用）**
        
        返回对象为响应体中数据转化成的对象，基本上**可以理解为Json串**
        
        ![[IMG-20260405035535187.png|Untitled 531.png]]
        
    
    1. **getForEntity()：**
        
        返回对象为ResponseEntity对象，**包含了响应中的一些更详细的重要信息**，比如响应头、响应状态码、响应体等
        
        ![[IMG-20260405035539963.png|Untitled 1 394.png]]
        
    
    1. **postForObject()：**
    
    1. **postForEntity()：**
        
        ![[IMG-20260405035540014.png|Untitled 2 320.png]]
        
    
# 2. 参考资料

> [!info] RestTemplate 用法详解_决战灬的博客-CSDN博客_resttemplate方法介绍  
> 基本的微服务环境搭建，由 provider 提供服务， consumer 通过 DiscoveryClient 先去 eureka 上获取 provider 的服务的地址，获取到地址之后再去调用相关的服务。在服务的调用过程中，使用到了一个工具，叫做 RestTemplate，RestTemplate 是由 Spring 提供的一个 HTTP 请求工具。在上文的案例中，开发者也可以不使用 RestTemplate ，使用 Java 自带的 HttpUrlConnection 或者经典的网络访问框架 HttpClient 也可以完成上文的案例，只是在 Spring 项目中，使用 RestTemplate 显然更方便一些。在传统的项目架构中，因为不涉及到服务之间的调用，大家对 RestTemplate 的使用可能比较少，因此，本文我们就先来带领大家来学习下 RestTemplate 的各种不同用法，只有掌握了这些用法，才能在微服务调用中随心所欲地发送请求。 RestTemplate 是从 Spring3.  
> [https://blog.csdn.net/weixin_38987366/article/details/109701339](https://blog.csdn.net/weixin_38987366/article/details/109701339)  
# 3. Demo
```Java
@Configuration
public class RestTemplateConfig {
 
    @Bean
    public RestTemplate restTemplate(ClientHttpRequestFactory factory){
        return new RestTemplate(factory);
    }
 
    @Bean
    public ClientHttpRequestFactory simpleClientHttpRequestFactory(){
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(15000);
        factory.setReadTimeout(5000);
        return factory;
    }
}
```
```Java
@Autowired
RestTemplate restTemplate;
 
@Test
public void postTest() throws Exception {
    MultiValueMap<String, String> requestEntity = new LinkedMultiValueMap<>();
    Map paraMap = new HashMap();
    paraMap.put("type", "wx");
    paraMap.put("mchid", "10101");
    requestEntity.add("consumerAppId", "test");
    requestEntity.add("serviceName", "queryMerchant");
    requestEntity.add("params", JSON.toJSONString(paraMap));
    RestTemplate restTemplate = new RestTemplate();
    restTemplate.postForObject("http://10.30.10.151:8012/gateway.do", requestEntity, String.class);
}
```