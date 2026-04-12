- [[#1. Thymeleaf 介绍]]
- [[#2. Thymeleaf 使用]]
- [[#3. 使用示例]]
# 1. **Thymeleaf 介绍**
1. 基本语法
    
    1. 表达式：
        
        |   |   |   |
        |---|---|---|
        |**表达式名字**|**语法**|**用途**|
        |变量取值|${...}|获取请求域、session域、对象等值|
        |选择变量|*{...}|获取上下文对象值|
        |消息|#{...}|获取国际化等值|
        |链接|@{...}|生成链接|
        |片段表达式|~{...}|jsp:include 作用，引入公共页面片段|
        
    
    1. 字面量：
        
        1. 文本值： 'one text' , 'Another one!'
        
        1. 数字: 0 , 34 , 3.0 , 12.3
        
        1. 布尔值: true , false
        
        1. 空值:：null
        
        1. 变量：one，two，.... 变量不能有空格
        
    
    1. 条件运算
        
        1. If-then：(if) ? (then)
        
        1. If-then-else： (if) ? (then) : (else)
        
        1. Default：(value) ?: (defaultvalue)
        
    
    1. 文本操作
        
        1. 字符串拼接: +
        
        1. 变量替换: |The name is ${name}|
        
    
1. 设置属性值：**th:attr**
    
    ```HTML
     <form action="subscribe.html" th:attr="action=@{/subscribe}">
       <fieldset>
         <input type="text" name="email" />
         <input type="submit" value="Subscribe!" th:attr="value=#{subscribe.submit}"/>
       </fieldset>
     </form>
     
     设置多个值
     <img src="../../images/gtvglogo.png"  th:attr="src=@{/images/gtvglogo.png},title=#{logo},alt=#{logo}" />
    ```
    
1. **迭代**
    
    ```HTML
     <tr th:each="prod : ${prods}">
         <td th:text="${prod.name}">Onions</td>
         <td th:text="${prod.price}">2.41</td>
         <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
     </tr>
    ```
    
    ```HTML
     如果需要获取当前遍历到第几个
     
     <tr th:each="prod,iterStat : ${prods}" th:class="${iterStat.odd}? 'odd'">
       <td th:text="${prod.name}">Onions</td>
       <td th:text="${prod.price}">2.41</td>
       <td th:text="${prod.inStock}? #{true} : #{false}">yes</td>
     </tr>
    ```
    
1. **条件运算**
    
    ```HTML
     <a href="comments.html"
     th:href="@{/product/comments(prodId=${prod.id})}"
     th:if="${not \#lists.isEmpty(prod.comments)}">view</a>
    ```
    
# 2. **Thymeleaf 使用**
1. 引入Thymeleaf 场景启动器
    
    ```XML
     <dependency>
         <groupId>org.springframework.boot</groupId>
         <artifactId>spring-boot-starter-thymeleaf</artifactId>
     </dependency>
    ```
    
1. Thymeleaf 自动配置
    
    1. 底层都自动配好了
        
        ```Java
         @Configuration(proxyBeanMethods = false)
         
         //所有 thymeleaf 的配置值都在 ThymeleafProperties
         @EnableConfigurationProperties({ThymeleafProperties.class})
         @ConditionalOnClass({TemplateMode.class, SpringTemplateEngine.class})
         @AutoConfigureAfter({WebMvcAutoConfiguration.class, WebFluxAutoConfiguration.class})
         public class ThymeleafAutoConfiguration {
             ...
        
             //配好了 ThymeleafViewResolver
             @Bean
             @ConditionalOnMissingBean(name = {"thymeleafViewResolver"})
             ThymeleafViewResolver thymeleafViewResolver(ThymeleafProperties properties, SpringTemplateEngine templateEngine) {
                 ....
                 return resolver;
             }
        
             //配置好了 SpringTemplateEngine
             @Bean
             @ConditionalOnMissingBean({ISpringTemplateEngine.class})
             SpringTemplateEngine templateEngine(ThymeleafProperties properties, ObjectProvider<ITemplateResolver> templateResolvers, ObjectProvider<IDialect> dialects) {
                 ....
                 return engine;
             }
         }
        ```
        
    
    1. 所有的页面文件都放在类路径下的 templates/中
        
        ```Java
         //ThymeleafProperties.class
         public static final String DEFAULT_PREFIX = "classpath:/templates/";
         public static final String DEFAULT_SUFFIX = ".html";
        ```
        
    
    1. 只需要直接开发页面
    
# 3. 使用**示例**
1. 前端页面
    
    ```HTML
     <!DOCTYPE html>
     <!--引入th名称空间-->
     <html lang="en" xmlns:th="http://www.thymeleaf.org">
     <head>
         <meta charset="UTF-8">
         <title>Title</title>
     </head>
     <body>
     <!--    哈哈是默认值（静态的），在经过SpringTemplateEngine渲染后值就变成了controller中设置的值（动态的）-->
         <h1 th:text="${msg}">哈哈</h1>
         <h2>
    
     <!--        ${...} 表示从request域中取数据-->
             <a href="www.baidu.com" th:href="${link}">去百度1</a>
    
     <!--        @{...} 拼接生成链接，其中的值 是字符串 用于拼接请求链接-->
             <a href="www.baidu.com" th:href="@{link}">去百度2</a>
         </h2>
     </body>
     </html>
    ```
    
1. controller
    
    ```Java
     @Controller
     public class ViewTestController {
         @GetMapping("/coolcool")
         public String coolcool(Model model){
             //model中的数据会被放在request请求域中：request.setAttribute("x","xx");
             //再设置model的值
             model.addAttribute("msg","你好coolcool");
             model.addAttribute("link","http://www.baidu.com");
     
             //跳转页面不需要写后缀：ThymeleafProperties 中默认会有
             //会去 temlate/下找success.html
             return "success";
         }
     }
    ```
    
1. 访问
    
    ![[IMG-20260405035414004.png|Untitled 491.png]]
    
1. 查看网页源代码
    
    ![[IMG-20260404031833376.png|Untitled 1 361.png]]