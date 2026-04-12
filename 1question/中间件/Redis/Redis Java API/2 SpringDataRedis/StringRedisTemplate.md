- [[#1. RedisTemplate 存在的问题]]
- [[#2. StringRedisTemplate]]
- [[#3. StringRedisTemplate 代码示例]]
# 1. **RedisTemplate** 存在的问题
1. 为了在反序列化时知道对象的类型，JSON序列化器会将类的class类型写入json结果中，存入Redis
    
    ![[IMG-20260405035508259.png]]
    
1. 但是，这==**会带来额外的内存开销！**==
    
    1. 为了节省内存空间，我们并不会使用 JSON 序列化器来处理 value
    
    1. 而是 **统一使用 String 序列化器**，要求只能存储 String 类型的 key 和 value
    
1. **不使用 RedisTemplate，而是使用 StringRedisTemplate** ⬇️
# 2. **StringRedisTemplate**
1. **StringRedisTemplate** ==**只有 String 序列化器**==
    
    ![[IMG-20260404031932760.png]]
    
1. **但是使用** `**StringRedisTemplate**` **时，**==**当需要存储Java对象时，需要手动完成对象的序列化和反序列化**==
    
    ![[IMG-20260404031932794.png]]
    
# 3. StringRedisTemplate 代码示例
1. 使用 StringRedisTemplate 来 set 或 get 一个对象
1. 先注入StringRedisTemplate
    
    ```Java
     @Autowired
     private StringRedisTemplate stringRedisTemplate;
    ```
    
1. 创建对象测试
    
    ```Java
     @SpringBootTest(classes = springDateRedisRun.class)
     class SpringDataRedisTest {
     
     //    @Autowired
     //    private RedisTemplate<String,Object> redisTemplate;
     
         @Autowired
         private StringRedisTemplate stringRedisTemplate;
     
         private static final ObjectMapper MAPPER = new ObjectMapper();
         @Test
         void testSaveUser() throws JsonProcessingException {
             User qhj = new User("qhj", "24");
    
             //手动序列化
             String jsonString = MAPPER.writeValueAsString(qhj);
             stringRedisTemplate.opsForValue().set("user:100",jsonString);
    
             String jsonUser = stringRedisTemplate.opsForValue().get("user:100");
    
             //手动反序列化
             User user = MAPPER.readValue(jsonUser, User.class);
             System.out.println(user.toString());
         }
     }
    ```
    
    > [!important] **这里涉及到 对象与 JSON 之间的互相转换：这里使用的是**
    > 
    > `**ObjectMapper**`**（Jackson 提供的对象映射器）**
    
1. 查看结果：
    
    ```Shell
     127.0.0.1:6379> GET user:100
     "{\"name\":\"qhj\",\"age\":\"24\"}"
    ```
    
    ![[IMG-20260404031932841.png]]
    
    - **可以看到不再需要存储类的class类型，节省了存储空间**