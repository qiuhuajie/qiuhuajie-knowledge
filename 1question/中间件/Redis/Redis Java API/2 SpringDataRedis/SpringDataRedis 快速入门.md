- [[#1. 介绍]]
- [[#3. 在 SpringBoot 中整合使用 SpringDataRedis]]
# 1. 介绍
1. **SpringDataRedis** 中提供了**==RedisTemplate工具类==**，其中封装了各种对Redis的操作
1. 并且将不同数据类型的操作API封装到了不同的类型中
    
    ![[IMG-20260405035438350.png]]
    
# 3. 在 SpringBoot 中整合使用 SpringDataRedis
1. 引入依赖
    
    ```XML
     <?xml version="1.0" encoding="UTF-8"?>
     <project xmlns="http://maven.apache.org/POM/4.0.0"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
         <parent>
             <artifactId>redis-demo</artifactId>
             <groupId>org.example</groupId>
             <version>1.0-SNAPSHOT</version>
         </parent>
         <modelVersion>4.0.0</modelVersion>
     
         <artifactId>springdataredis-demo</artifactId>
     
         <dependencies>
             <dependency>
                 <groupId>org.springframework.boot</groupId>
                 <artifactId>spring-boot-starter-web</artifactId>
             </dependency>
     
             <dependency>
                 <groupId>org.springframework.boot</groupId>
                 <artifactId>spring-boot-starter-test</artifactId>
             </dependency>
     
             <!--⭐redis-->
             <dependency>
                 <groupId>org.springframework.boot</groupId>
                 <artifactId>spring-boot-starter-data-redis</artifactId>
             </dependency>
     
             <!--commons-pool-->
             <dependency>
                 <groupId>org.apache.commons</groupId>
                 <artifactId>commons-pool2</artifactId>
             </dependency>
     
             <dependency>
                 <groupId>org.junit.jupiter</groupId>
                 <artifactId>junit-jupiter</artifactId>
                 <scope>test</scope>
             </dependency>
     
             <dependency>
                 <groupId>org.projectlombok</groupId>
                 <artifactId>lombok</artifactId>
             </dependency>
         </dependencies>
     </project>
    ```
    
1. 配置文件
    
    ```YAML
     spring:
       redis:
         host: 192.168.10.151
         port: 6379
         password: 111111
         lettuce:
           pool:
             max-active: 8
             max-idle: 8
             min-idle: 0
             max-wait: 1000
    ```
    
1. 编写测试：**RedisTemplate**
    
    ```Java
     @SpringBootTest(classes = springDateRedisRun.class)
     class SpringDataRedisTest {
     
         //注入RedisTemplate
         @Autowired
         private RedisTemplate redisTemplate;
     
         @Test
         void testString(){
     
             redisTemplate.opsForValue().set("name","Jack");
             //⭐这里的字符换被当作对象，默认使用JdkSerializationRedisSerializer来序列化
     
             Object name = redisTemplate.opsForValue().get("name");
             System.out.println(name);   //Jack
         }
    
         @Test
         void testHash(){
             redisTemplate.opsForHash().put("user:400","name","qhj");
             //hash类似于Java中的hashMap，故JavaAPI的方法和操作hashMap的同名：put()、entries()...
             redisTemplate.opsForHash().put("user:400","age","22");
     
             Map<Object, Object> entries = redisTemplate.opsForHash().entries("user:400");
             System.out.println(entries);
         }
     }
    ```
    
1. 在 redis-cli 中查看
    
    ```Bash
     127.0.0.1:6379> get name
     "cool"
    ```
    
    **? 为什么这里name并没有改变**