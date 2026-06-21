---
title: "Restful 请求风格"
tags:
  - "PUT"
  - "DELETE"
  - "Restful"
  - "REST"
  - "RESTful"
  - "Restful_请求风格"
updated: 2026-04-16
---

# 一、Restful 介绍
## 1. REST 原则
1. `REST` 指的是一组架构约束条件和原则
2. Web 应用程序最重要的 `REST` 原则是：
    1. **客户端和服务器之间的交互在请求之间是无状态的**
        - 如果服务器在请求之间的任何时间点重启，客户端不会得到通知
        - 此外，无状态请求可以由任何可用服务器回答，这十分适合云计算之类的环境
    2. **从客户端到服务器的每个请求都必须包含理解请求所必需的信息**
3. 简单的理解就是：**如果想要访问互联网上的资源，就必须向资源所在的服务器发出请求**
    1. ==请求体中必须包含资源的====**网络资源路径（URL）**==
    2. ==以及====**对资源进行的操作**====（增删改查）==，包括 HTTP `GET`、 `POST`、`PUT`、 `DELETE`，还可能包括 `HEAD` 和 `OPTIONS`

## 2. Restful 请求风格
1. `REST` 指的是一组架构约束条件和原则，满足这些约束条件和原则的应用程序或设计就是 `RESTful`
2. Rest 风格支持 **使用HTTP请求方式动词来表示对资源的操作**
    1. 以前：
        - `/getUser` 获取用户
        - `/deleteUser` 删除用户
        - `/editUser` 修改用户
        - `/saveUser` 保存用户
    2. 项目变大后，起名字也成为困难
    3. 现在：请求都只使用 `/user` ，但不同的**请求方式**对应不同的**操作**：
        - `GET`：获取用户
        - `DELETE`：删除用户
        - `PUT`：修改用户
        - `POST`：保存用户

# 二、使用
1. 需要使用一个Filter：**HiddenHttpMethodFilter**

    ```Java
     @Bean
     @ConditionalOnMissingBean(HiddenHttpMethodFilter.class)
     @ConditionalOnProperty(prefix = "spring.mvc.hiddenmethod.filter", name = "enabled", matchIfMissing = false)
     public OrderedHiddenHttpMethodFilter hiddenHttpMethodFilter() {
         return new OrderedHiddenHttpMethodFilter();
     }
    ```
2. 用法：
    1. 设置表单属性：`method=...`

    ```XML
     <form action="/user" method="get">
         <input value="REST-GET提交" type="submit" />
     </form>
     <form action="/user" method="post">
         <input value="REST-POST提交" type="submit" />
     </form>
     <!--DELETE 和 PUT 要使用POST方式，并设置一个隐藏域 _method=...写自己的方式-->
     <form action="/user" method="post">
         <!--隐藏域-->
         <input name="_method" type="hidden" value="DELETE"/>
         <input value="REST-DELETE 提交" type="submit"/>
     </form>
     <form action="/user" method="post">
         <input name="_method" type="hidden" value="PUT" />
         <input value="REST-PUT提交"type="submit" />
     </form>
    ```
    > 💡 因为表单 method 只能写 POST 所以需要 HiddenHttpMethodFilter 过滤，将 POST 修改为 PUT 或 DELETE
    2. SpringBoot中手动开启

    ```Java
     spring.mvc.hiddenmethod.filter.enabled=true
    ```
    3. conrtoller

    ```Java
     @RestController
     public class HelloController {
         //⭐根据请求提交的方法不同，做出不同的请求处理
         //写法一：
         @RequestMapping(value = "/user",method = RequestMethod.GET)
         //写法二：
         //@GetMapping("/user") 与上面等价
         public String getUser(){
             return "GET-张三";
         }
         //@PostMapping("/user")
         @RequestMapping(value = "/user",method = RequestMethod.POST)
         public String saveUser(){
             return "POST-张三";
         }
         //@PutMapping("/user")
         @RequestMapping(value = "/user",method = RequestMethod.PUT)
         public String putUser(){
             return "PUT-张三";
         }
         //@DeleteMapping("/user")
         @RequestMapping(value = "/user",method = RequestMethod.DELETE)
         public String deleteUser(){
             return "DELETE-张三";
         }
     }
    ```
    4. 访问

    ![[Attachment/1question/大数据/Java 开发/SpringBoot/4 Web 开发手册/4 3 请求 与 参数处理/IMG-20260405035413998.png|684]]

    ![[IMG-20260404031830775.png|800]]

    ![[Attachment/1question/Java 开发/SpringBoot/4 Web 开发手册/4 3 请求 与 参数处理/IMG-20260405035420374.png|588]]

# 三、使用REST提交表单的原理
1. 表单提交会带上**`_method=PUT`**
2. 请求过来被 ⭐ **`HiddenHttpMethodFilter`**拦截
    1. 判断请求是否正常，并且是POST
    2. 获取到**`_method`**的值，判断其值是否为**PUT、DELETE、PATCH**
    3. 使用包装模式 **`requesWrapper`** （HttpServletRequest的实现类，重写了getMethod方法），将原生**request**（POST）包装后返回，其中method 就是传入的值，不再是 POST了（修改为 PUT 或 DELETE）
3. 注意：
    1. **如果使用 PostMan直接发送PUT、DELETE 等方式请求，无需Filter**

    ![[IMG-20260405035422103.png|800]]

    2. 也可以在自定义的配置类中，添加一个 filter，来自定义 `_m` （MethodParam名字）

    ```Java
     //自定义filter
     @Bean
     public HiddenHttpMethodFilter hiddenHttpMethodFilter(){
         HiddenHttpMethodFilter methodFilter = new HiddenHttpMethodFilter();
         methodFilter.setMethodParam("_m");
         return methodFilter;
     }
    ```
