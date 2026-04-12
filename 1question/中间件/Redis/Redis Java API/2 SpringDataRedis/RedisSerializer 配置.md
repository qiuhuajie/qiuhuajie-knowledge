- [[#1. 当前存在的问题]]
- [[#2. 解决方法]]
- [[#3. 自定义 RedisTemplate 的序列化方式]]
# 1. 当前存在的问题
1. RedisTemplate 可以接收任意 Object 作为值写入 Redis
1. 只不过写入前会把 Object 序列化为字节形式，默认是采用 JDK 序列化，得到的结果是这样的
    
    ```Shell
     127.0.0.1:6379> KEYS *
      1) "user:1"
      2) "coolcool:user:1"
      3) "name"
      4) "coolcool:user:4"
      5) "coolcool:user:3"
      6) "length"
      7) "k4"
      8) "age"
      9) "coolcool:product:1"
     10) "\xac\xed\x00\x05t\x00\x04name" # ⭐这个name才是Jack
     11) "coolcool:user:2"
     12) "coolcool:product:2"
     
     127.0.0.1:6379> get "\xac\xed\x00\x05t\x00\x04name"
     "\xac\xed\x00\x05t\x00\x04Jack"
    ```
    
    ![[Attachment/1question/中间件/Redis/Redis Java API/2 SpringDataRedis/IMG-20260405035438349.png]]
    
1. 缺点：
    
    - 可读性差
    
    - 内存占用较大
    
# 2. **解决方法**
1. redisTemplate 类中定义了可以配置自定义的序列化方式
1. 没有自定义设置的情况下，才会使用 JDK 序列化
    
    ![[IMG-20260405035453597.png]]
    
1. **可以自定义 RedisTemplate 的序列化方式**
# 3. 自定义 RedisTemplate 的序列化方式
1. 新建一个配置类，来自定义RedisTemplate的序列化方式
    
    ```Java
     @SpringBootConfiguration
     public class redisConfig {
     
         @Bean
         public RedisTemplate<String,Object> redisTemplate(RedisConnectionFactory redisConnectionFactory){
             //1. 创建RedisTemplate对象
             RedisTemplate<String, Object> redisTemplate = new RedisTemplate<>();
             //2. 设置连接工厂
             redisTemplate.setConnectionFactory(redisConnectionFactory);
             //3. 设置key的序列化
             redisTemplate.setKeySerializer(RedisSerializer.string());
             redisTemplate.setHashKeySerializer(RedisSerializer.string());
    
             //4. 创建JSON序列化工具
             GenericJackson2JsonRedisSerializer jsonRedisSerializer = new GenericJackson2JsonRedisSerializer();
             //5. 设置value的序列化
             redisTemplate.setValueSerializer(jsonRedisSerializer);
             redisTemplate.setHashValueSerializer(jsonRedisSerializer);
             //6. 返回
             return redisTemplate;
         }
     }
    ```
    
1. POJO
    
    ```Java
     @Data
     @AllArgsConstructor
     @NoArgsConstructor
     public class User {
         private String name;
         private String age;
     }
    ```
    
1. 存入一个 user 对象做测试
    
    ```Java
     @SpringBootTest(classes = springDateRedisRun.class)
     class SpringDataRedisTest {
     
         //⭐这里注入的自定义序列化方式后的RedisTemplate
         @Autowired
         private RedisTemplate<String,Object> redisTemplate;
     
         @Test
         void testSaveUser(){
             User qhj = new User("qhj", "24");
             //设置对象键值对
             redisTemplate.opsForValue().set("user:100",qhj);
             //获取对象键值对
             User o = (User) redisTemplate.opsForValue().get("user:100");
             System.out.println(o);  //User(name=qhj, age=24)
         }
     }
    ```
    
1. redis-cli 中查看
    
    ```Shell
     127.0.0.1:6379> GET user:100
     "{\"@class\":\"com.qhj.pojo.User\",\"name\":\"qhj\",\"age\":\"24\"}"
    ```
    
    ![[IMG-20260405035508259.png]]
    
    - **为了在反序列化时知道对象的类型，JSON 序列化器**==**会将类的 class 类型写入 json 结果中，存入Redis**==
    
    - 这就是 `redisTemplate.opsForValue().get("user:100")` 时，可以返回一个 User 对象的原因