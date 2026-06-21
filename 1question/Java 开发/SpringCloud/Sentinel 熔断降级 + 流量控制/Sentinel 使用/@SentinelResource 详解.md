---
title: "@SentinelResource 详解"
tags:
  - "@SentinelResource"
  - "SentinelResource"
  - "熔断降级"
  - "Spring_Cloud"
  - "流量控制"
  - "Spring"
updated: 2026-04-16
---

# 一、@SentinelResource 详解
```Java
@SentinelResource(value = "",fallback = "",blockHandler = "")
```
## 1. value 属性：规则匹配
1. 使用资源名，将 sentinel 上的配置的规则，与该规则要作用在哪个请求上做匹配）
2. 规则的资源名（这个资源名是指在 sentinel dashboard 上添加规则时输入的资源名）设置有两个方式：

    ![[IMG-20260405035414037.png|800]]

    1. 方式一：`@SentinelResource` 注解的 value 属性（按资源名称）
    2. 方式二：`@GetMapping` 注解的 value 属性（按URL地址）
        > 注意：通过访问的URL来限流，只会返回Sentinel自带默认的限流处理信息

![[IMG-20260404031842942.png|800]]

## 2. fallback 属性：配置熔断降级兜底方法⭐
1. [[熔断降级 + 流量控制 代码示例]][[熔断降级 + 流量控制 代码示例]]
2. **fallback 规定了异常、超时发生后的兜底方法**
3. 代码示例：

    ```Java
    @RestController
    @Slf4j
    public class CircleBreakerController {
        public static final String SERVICE_URL = "http://nacos-payment-provider";
        @Resource
        private RestTemplate restTemplate;
        @RequestMapping("/consumer/fallback/{id}")
        @SentinelResource(value = "fallback",fallback = "handlerFallback")
        public CommonResult<Payment> fallback(@PathVariable Long id) {
            //调用 9003、9004的服务
            CommonResult<Payment> result = restTemplate.getForObject(SERVICE_URL + "/paymentSQL/"+id, CommonResult.class,id);
            //模拟抛出两种异常
                //1. id = 4 ：抛出IllegalArgumentException
                //2. 使用id在9003、9004上查出的数据 = null ：抛出NullPointerException
            if (id == 4) {
                throw new IllegalArgumentException ("IllegalArgumentException,非法参数异常....");
            }else if (result.getData() == null) {
                throw new NullPointerException ("NullPointerException,该ID没有对应记录,空指针异常");
            }
            return result;
        }
        //熔断降级兜底方法
        public CommonResult handlerFallback(@PathVariable  Long id,Throwable e) {
            return new CommonResult<>(444,"当前出现的异常："+e.getMessage()+"，故执行了兜底处理方法");
        }
    }
    ```
4. 测试：

    ![[IMG-20260405035414044.png|800]]

## 3. exceptionsToIgnore 属性
```Java
@SentinelResource(value = "fallback",
                  fallback = "handlerFallback",
                  blockHandler = "blockHandler",
                  exceptionsToIgnore = {IllegalArgumentException.class})
//表示 方法中如果 抛出了 IllegalArgumentException 异常，则不使用规定的 兜底方法处理，而是直接将异常信息返回给前台
```
## 4. blockHandler 属性：配置流量控制兜底方法⭐
1. **blockHandler 规定了限流后的兜底方法**
2. 新增 一个 处理类，在类中写流量控制规则触发后，要执行的兜底方法。兜底方法必须写出 静态方法 `static`

    ```Java
    public class CustomerBlockHandler {
        public static CommonResult handleException(BlockException exception){
            return new CommonResult(2020,"当前执行的是解耦后的兜底方法......");
        }
    }
    ```
3. 在 controller 中添加测试方法 ，并在 **`@SentinelResource`** 注解中配置参数 `blockHandlerClass`

    ```Java
    @GetMapping("/rateLimit/customerBlockHandler")
    @SentinelResource(
            value = "customerBlockHandler",                     //⭐对应规则资源名
            blockHandlerClass = CustomerBlockHandler.class,     //⭐限流后，去哪个处理类找兜底方法
            blockHandler = "handleException")                   //⭐去处理类中找哪个兜底方法
    public CommonResult customerBlockHandler() {
        return new CommonResult(200,"服务正常执行");
    }
    ```

    ![[IMG-20260405035420393.png|800]]

4. 配置：使用 资源名称限流

    ![[IMG-20260405035422117.png|745]]

5. 测试：
    1. [http://localhost:8401/byResource](http://localhost:8401/byResource)
    2. 正常访问：1 秒 1 次

    ![[IMG-20260405035427654.png|621]]

    3. 高并发访问呢：狂点**（可以看到，执行了自定义的限流后的兜底方法）**

    ![[IMG-20260405035427682.png|800]]
