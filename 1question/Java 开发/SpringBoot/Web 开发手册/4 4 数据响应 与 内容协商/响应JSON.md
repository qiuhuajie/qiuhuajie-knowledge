---
title: "响应JSON"
tags:
  - "内容协商"
  - "JSON"
  - "Spring_Boot"
  - "响应JSON"
  - "请求头"
  - "HttpMessageConverter"
updated: 2026-04-16
---

# 一、示例
1. 需要引入的依赖：web场景自动引入了json场景

    ```XML
     <!--spring-boot-starter-web中-->
     <dependency>
       <groupId>org.springframework.boot</groupId>
       <artifactId>spring-boot-starter-json</artifactId>
       <version>2.3.4.RELEASE</version>
       <scope>compile</scope>
     </dependency>
     <!--spring-boot-starter-json中-->
     <dependency>
         <groupId>com.fasterxml.jackson.core</groupId>
         <artifactId>jackson-databind</artifactId>
         <version>2.11.2</version>
         <scope>compile</scope>
     </dependency>
     <dependency>
         <groupId>com.fasterxml.jackson.datatype</groupId>
         <artifactId>jackson-datatype-jdk8</artifactId>
         <version>2.11.2</version>
         <scope>compile</scope>
     </dependency>
     <dependency>
         <groupId>com.fasterxml.jackson.datatype</groupId>
         <artifactId>jackson-datatype-jsr310</artifactId>
         <version>2.11.2</version>
         <scope>compile</scope>
     </dependency>
     <dependency>
         <groupId>com.fasterxml.jackson.module</groupId>
         <artifactId>jackson-module-parameter-names</artifactId>
         <version>2.11.2</version>
         <scope>compile</scope>
     </dependency>
     </dependencies>
    ```
2. 如何给前端返回一个JSON数据：**==@ResponseBody + @Controller = @RestController==**

    ```Java
     @Controller
     public class responseTestController {
         @ResponseBody
         @GetMapping("/test/person")
         public Person getPerson(){
             Person person = new Person();
             person.setUserName("zhangsan");
             person.setAge(18);
             person.setBirth(new Date());
             return person;
         }
     }
    ```
    ![[Attachment/1question/大数据/Java 开发/SpringBoot/4 Web 开发手册/4 4 数据响应 与 内容协商/IMG-20260405035413998.png|684]]
# 二、原码解析
1. 返回值解析器

    ![[IMG-20260404031832947.png|800]]
2. 返回值解析器支持的返回值类型

    ```Java
     ModelAndView //正常情况下响应的返回值 要走 视图解析器，即controller返回一个 MAV，使用的 返回值处理器是：ModelAndViewMethodReturnValueHandler
     Model
     View
     ResponseEntity
     ResponseBodyEmitter
     StreamingResponseBody
     HttpEntity
     HttpHeaders
     Callable
     DeferredResult
     ListenableFuture
     CompletionStage
     WebAsyncTask
     标注了@ModelAttribute 且为对象类型的
     标注了@ResponseBody 上面例子就是使用的这种返回值类型，故使用的返回值处理器就是：RequestResponseBodyMethodProcessor；
    ```
3. 搜索合适的返回值解析器

    ```Java
     public void handleReturnValue(@Nullable Object returnValue, MethodParameter returnType, ModelAndViewContainer mavContainer, NativeWebRequest webRequest) throws Exception {
         //selectHandler()搜索合适的返回值解析器
         HandlerMethodReturnValueHandler handler = this.selectHandler(returnValue, returnType);
         if (handler == null) {
             throw new IllegalArgumentException("Unknown return value type: " + returnType.getParameterType().getName());
         } else {
             //找到的返回值解析器调用自己的 handleReturnValue()来处理
             handler.handleReturnValue(returnValue, returnType, mavContainer, webRequest);
         }
     }
    ```
4. 找到 **RequestResponseBodyMethodProcessor** 处理器

    ```Java
     //RequestResponseBodyMethodProcessor.class
     @Override
     public void handleReturnValue(@Nullable Object returnValue, MethodParameter returnType,ModelAndViewContainer mavContainer, NativeWebRequest webRequest) throws IOException, HttpMediaTypeNotAcceptableException, HttpMessageNotWritableException {
         mavContainer.setRequestHandled(true);
         ServletServerHttpRequest inputMessage = createInputMessage(webRequest);
         ServletServerHttpResponse outputMessage = createOutputMessage(webRequest);
         //将要返回的数据、返回的数据类型、封装过的请求和响应传入
         //使用消息转换器 writeWithMessageConverters() 进行写出操作
         writeWithMessageConverters(returnValue, returnType, inputMessage, outputMessage);
     }
    ```
5. ⭐利用消息转换器 writeWithMessageConverters() 将返回的数据转换为JSON类型的过程
    1. **内容协商：**[[内容协商]]
        1. 浏览器默认会以**请求头**（Accept字段）的方式告诉服务器他**能接受什么样的内容数据类型**
        2. 服务器最终根据自己自身的能力，决定服务器**能生产出什么样内容数据类型**
        3. 将这两个可接受和可产出的类型做**匹配**：最终确定返回什么类型数据，存在MediaType变量中（上例中就是JSON类型）
    2. SpringMVC会挨个遍历所有容器底层的消息转换器 **HttpMessageConverter** ，看谁能处理 MediaType
    3. 搜索找到 **MappingJackson2HttpMessageConverter** 可以将对象写为 JSON
    4. 最后利用 MappingJackson2HttpMessageConverter将对象转为JSON，再写出去
        > 利用底层的jackson的objectMapper转换的
        >
        > 手动使用 objectMapper 将自定义对象转换为 JSON 字符串的写法 ，**详见 前端笔记： 6.JSON**
6. **HttpMessageConverter** 原理
    1. 接口里面的方法

    ```Java
     public interface HttpMessageConverter<T> {
         boolean canRead(Class<?> var1, @Nullable MediaType var2);
         boolean canWrite(Class<?> var1, @Nullable MediaType var2);
         List<MediaType> getSupportedMediaTypes();
         T read(Class<? extends T> var1, HttpInputMessage var2) throws IOException, HttpMessageNotReadableException;
         void write(T var1, @Nullable MediaType var2, HttpOutputMessage var3) throws IOException, HttpMessageNotWritableException;
     }
    ```
    2. 功能：看是否支持将 此 Class类型的对象，转为目标 MediaType 类型的数据

        例子：Person对象转为JSON，或者 JSON转为Person
    3. 所有的 MessageConverter：

    ![[Attachment/1question/Java 开发/SpringBoot/4 Web 开发手册/4 4 数据响应 与 内容协商/IMG-20260405035420374.png|588]]
    ```Java
     0 - 只支持Byte类型的
     1 - String
     2 - String
     3 - Resource
     4 - ResourceRegion
     5 - DOMSource.class \ SAXSource.class) \ StAXSource.class \StreamSource.class \Source.class
     6 - MultiValueMap
     7 - true
     8 - true
     9 - 支持注解方式xml处理的。
    ```
