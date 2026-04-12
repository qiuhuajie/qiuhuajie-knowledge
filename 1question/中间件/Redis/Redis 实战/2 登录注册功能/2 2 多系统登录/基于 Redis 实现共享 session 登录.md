- [[#1. 业务流程]]
- [[#2. 发送短信验证码]]
- [[#3. 短信验证码登录、注册]]
- [[#4. 校验登陆状态]]
# 1. 业务流程
![[IMG-20260405035438389.png|Untitled 536.png]]
![[IMG-20260405035455941.png|Untitled 1 397.png]]
1. 注入redis依赖
1. 注入`StringRedisTemplate`
    
    ```Java
     @Resource
     private StringRedisTemplate stringRedisTemplate;
    ```
    
# 2. **发送短信验证码**
1. 在发送短信验证码后==将==**==手机号==**==和==**==验证码==** `"login:code:" + phone,codecode` ==作为键值对存入 Redis==
    
    ```Java
     //4. 保存验证码到redis
     //stringRedisTemplate.opsForValue().set("login:code:" + phone,code,2, TimeUnit.MINUTES);
     //设成常量看起来更高级
     stringRedisTemplate.opsForValue().set(LOGIN_CODE_KEY + phone,code,LOGIN_CODE_TTL, TimeUnit.MINUTES);
    ```
    
    - code 是字符串，故存入Redis 时选择的 Value 格式为 String
    
    - **存入 Redis 的 code 需要考虑TTL（time to live）**
    
1. 完整代码：
    
    ```Java
     @Override
     public Result sendCode(String phone, HttpSession session) {
         //1. 校验手机号
         if (RegexUtils.isPhoneInvalid(phone)){
             //2. 如果不符合，返回错误信息
             return Result.fail("手机号格式错误！");
         }
         //3. 符合，生成验证码
         String code = RandomUtil.randomNumbers(6);
     
         //4. 保存验证码到 redis
         //stringRedisTemplate.opsForValue().set("login:code:" + phone,code,2, TimeUnit.MINUTES);
         //设成常量看起来更高级
         stringRedisTemplate.opsForValue().set(LOGIN_CODE_KEY + phone,code,LOGIN_CODE_TTL, TimeUnit.MINUTES);
     
         //5. 发送验证码
         log.debug("发送验证码成功，验证码：{}", code);
         //返回 ok
         return Result.ok();
     }
    ```
    
# 3. **短信验证码登录、注册**
1. 从 redis 获取验证码，并校验验证码
    
    ```Java
     String cacheCode = stringRedisTemplate.opsForValue().get(LOGIN_CODE_KEY + phone);
    ```
    
1. 在保存用户信息时
    
    1. 首先要生成一个 `token` 作为==登陆令牌==
    
    1. 单系统中
        
        1. 是基于 session 的登陆的，**tomcat 会自动维护 session 的信息**
        
        1. **浏览器维护 cookie，请求时携带 cookie，而 cookie 中存着 sessionID（**服务器向用户浏览器发送了一个名为JESSIONID的Cookie，它的值是Session的id值）
        
        1. 因此，如果想要获取 session 中的信息直接：
            
            ```Java
             //1. 获取session
             HttpSession session = request.getSession();
             //2. 获取session中的用户
             Object user = session.getAttribute("user");
            ```
            
        
    
    1. **但是，在多系统中**
        
        1. 使用 Redis 代替 Session，**用户 user 对象是存在 Redis 中的，**==**如何让用户在请求时，拿到属于自己的 user 信息**==❓
        
        1. 故需要在创建用户时生成一个token，==token 的作用就是单系统中的== `cookie.JSESSIONID`
        
        1. 前端代码中获取到token在`axios`拦截器拦截到请求后，会**将token放在请求头的**`**authorization**`**字段中**（项目代码已经实现）
            
            ```Java
             // request拦截器，将用户token放入请求头中
             let token = sessionStorage.getItem("token");
             axios.interceptors.request.use(
               config => {
                 if(token) config.headers['authorization'] = token
                 return config
               },
               error => {
                 console.log(error)
                 return Promise.reject(error)
               }
             )
            ```
            
        
    
    1. 此时要将 user 对象存入 Redis，故 ==value 需要====**选用Hash类型**==
        
        1. 且一个对象要存储多个 hash 键值，就要用到 `stringRedisTemplate` 提供的`putall()`方法，但此方法需要传入一个HashMap
        
        1. 因此还需要先使用hutool工具提供的beanToMap将user对象转成HashMap
        
    
    1. 同时**==对存入 Redis 的对象设置有效期==（**==**session默认的有效期是30分钟**==**，使用 redis 代替session的话，也将其有效期设置成30分钟）**
    
1. 完整代码：
    
    ```Java
     @Override
     public Result login(LoginFormDTO loginForm, HttpSession session) {
         //1. 校验手机号
         String phone = loginForm.getPhone();
         if (RegexUtils.isPhoneInvalid(phone)){
             //2. 如果不符合，返回错误信息
             return Result.fail("手机号格式错误！");
         }
     
         //2. 从redis获取验证码，并校验验证码
         String cacheCode = stringRedisTemplate.opsForValue().get(LOGIN_CODE_KEY + phone);
         String code = loginForm.getCode();
         if (cacheCode == null || !cacheCode.toString().equals(code)){
             //3. 不一致报错
             return Result.fail("验证码错误");
         }
     
         //4. 一致，根据手机号查询用户
         User user = query().eq("phone", phone).one();
         //5. 判断用户是否存在
         if (user == null){
             //6. 不存在，创建新用户并保存
             user = createUserWritePhone(phone);
         }
     
         //7. 保存用户信息到session中
         //7.1 随机生成token，作为登陆令牌
         String token = UUID.randomUUID().toString(true);
         //7.2 将User对象转为HashMap存储
         UserDTO userDTO = BeanUtil.copyProperties(user, UserDTO.class);
         //putAll()需要一个HashMap
         Map<String, Object> map = BeanUtil.beanToMap(userDTO,new HashMap<>(),
                                                      CopyOptions.create()
                                                      .setIgnoreNullValue(true)
                                                      .setFieldValueEditor((fieldName,fieldValue) -> fieldValue + ""));//在Copy对应字段时，将值转成string
         //(这里userDTO各个属性一定不为空，如果操作其他对象转Map时，可能有字段为null，解决办法见 4.3 添加 redis 缓存！)
    
         //7.3 将用户信息存到 Redis 中
         stringRedisTemplate.opsForHash().putAll(LOGIN_USER_KEY + token,map);
         //7.4 设置token键值对的有效期
         stringRedisTemplate.expire(LOGIN_USER_KEY + token,30,TimeUnit.MINUTES);
         //8. ⭐给前端返回token
         return Result.ok(token);
     }
     
     private User createUserWritePhone(String phone) {
         //创建用户
         User user = new User();
         user.setPhone(phone);
         user.setNickName("user_" + RandomUtil.randomString(10));
         //保存用户
         save(user);
         return user;
     }
    ```
    
# 4. **校验登陆状态**
1. 自定义的 LoginInterceptor 登陆拦截器
    
    1. 首先 token 会在前端请求时，放在请求头的 `authorization` 字段中（项目代码已经实现），故后台的登录拦截器拦截到请求后，**先**==**将 token 取出**==
    
    1. token 判空
        
        1. **这里只是对 Token 进行了简单的判空处理，也可以将这个操作放在网关层**
        
        1. **放在网关层可以做的复杂一点，可以**==**对 Token 的合法性进行校验**==[[Gateway 项目实战]]
        
    
    1. **根据 token** ==**去 Redis 中查有没有对应的用户存在**==
    
    1. 并将查出的用户信息存在 ThreadLocal 中
        
        ![[IMG-20260405035456054.png|Untitled 2 322.png]]
        
    
1. 最后，session 在每次有新的请求时，就会刷新有效期，所以基于Redis实现时，**==每次拦截到一个请求，也要将token的有效期刷新==**
1. 完整代码：
    
    ```Java
     public class LoginInterceptor implements HandlerInterceptor {
     
         //这是我们自己写的类，没法直接注入bean
         //技巧：使用构造器来给想要的bean赋值
         //在使用这个自定义拦截器的地方：MvcConfig中传入一个stringRedisTemplate
         //而MvcConfig是标注了@Configuration注解的，它里面可以使用@Resource注入stringRedisTemplate
         //问题就解决了！
         private StringRedisTemplate stringRedisTemplate;
     
         public LoginInterceptor(StringRedisTemplate stringRedisTemplate) {
             this.stringRedisTemplate = stringRedisTemplate;
         }
     
         @Override
         public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
             //1. 从请求头中获取token
             String token = request.getHeader("authorization");
             if (StrUtil.isBlank(token)) {
                 //token为空，拦截
                 response.setStatus(401);
                 return false;
             }
             //2. 基于token获取redis中的用户
             Map<Object, Object> userMap = stringRedisTemplate.opsForHash().entries(RedisConstants.LOGIN_USER_KEY + token);
             //3. 判断用户是否存在
             if (userMap.isEmpty()){
                 //4. Map为空，拦截
                 response.setStatus(401);
                 return false;
             }
             //5. 将查询到的数据转回为UserDTO
             UserDTO userDTO = BeanUtil.fillBeanWithMap(userMap, new UserDTO(), false);
     
             //6. 存在，保存用户信息到ThreadLocal
             UserHolder.saveUser(userDTO);
     
             //7. 刷新token有效期
             stringRedisTemplate.expire(RedisConstants.LOGIN_USER_KEY + token,30, TimeUnit.MINUTES);
     
             //8. 放行
             return true;
         }
     
         @Override
         public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
     
         }
     
         @Override
         public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
             //移除用户
             UserHolder.removeUser();
         }
     }
    ```
    
1. 实现效果：
    
    ![[IMG-20260405035509133.png|Untitled 3 242.png]]
    
    ![[IMG-20260405035516978.png|Untitled 4 185.png]]
    
    ![[IMG-20260405035524408.png|Untitled 5 151.png]]
    
1. **还存在一个小问题：**
    
    1. token 有效期刷新问题，目前刷新是在请求需要校验登录的情况才会刷新，如果用户一直访问的是不需要校验登录的页面，则 token 会失效！
    
    1. 解决方法：再加一个拦截器：
        
        ![[IMG-20260405035524466.png|Untitled 6 126.png]]
        
        - `RefreshTokenIntercepter`：拦截一切请求，刷新 token，查出用户信息，处理完后放行所有请求，不做拦截
        
        - `LoginInterceptor`：只做登陆判断的拦截
        
    
    1. RefreshTokenIntercepter：
        
        ```Java
         public class RefreshTokenIntercepter implements HandlerInterceptor {
         
             private StringRedisTemplate stringRedisTemplate;
         
             public RefreshTokenIntercepter(StringRedisTemplate stringRedisTemplate) {
                 this.stringRedisTemplate = stringRedisTemplate;
             }
         
             @Override
             public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
         
                 //1. 从请求头中获取token
                 String token = request.getHeader("authorization");
                 if (StrUtil.isBlank(token)) {
                     //放行，所有拦截动作全放在LoginInterceptor
                     return true;
                 }
                 //2. 基于token获取redis中的用户
                 Map<Object, Object> userMap = stringRedisTemplate.opsForHash().entries(RedisConstants.LOGIN_USER_KEY + token);
                 //3. 判断用户是否存在
                 if (userMap.isEmpty()){
                     //放行，所有拦截动作全放在LoginInterceptor
                     return true;
                 }
                 //5. 将查询到的数据转回为UserDTO
                 UserDTO userDTO = BeanUtil.fillBeanWithMap(userMap, new UserDTO(), false);
         
                 //6. 存在，保存用户信息到ThreadLocal
                 UserHolder.saveUser(userDTO);
         
                 //7. 刷新token有效期
                 stringRedisTemplate.expire(RedisConstants.LOGIN_USER_KEY + token,30, TimeUnit.MINUTES);
         
                 //8. 放行
                 return true;
             }
         
             @Override
             public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
         
             }
         
             @Override
             public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
                 //移除用户
                 UserHolder.removeUser();
             }
         }
        ```
        
    
    1. LoginInterceptor：
        
        ```Java
         public class LoginInterceptor implements HandlerInterceptor {
         
             @Override
             public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
                 //判断是否需要拦截（ThreadLocal中是否有用户）
                 if (UserHolder.getUser() == null){
                     response.setStatus(401);
                     return false;
                 }
                 //8. 放行
                 return true;
             }
         }
        ```
        
    
    1. 拦截器配置：
        
        - RefreshTokenIntercepter必须在 `LoginInterceptor` 之前执行拦截
        
        - 故使用 `order()` 来设置拦截器执行顺序
        
        ```Java
         @Configuration
         public class MvcConfig implements WebMvcConfigurer {
         
             @Resource
             private StringRedisTemplate stringRedisTemplate;
         
             @Override
             public void addInterceptors(InterceptorRegistry registry) {
                 registry.addInterceptor(new LoginInterceptor()).excludePathPatterns(
                         "/shop/**",
                         "/voucher/**",
                         "/shop-type/**",
                         "/upload/**",
                         "/blog/hot",
                         "/user/code",
                         "/user/login"
                 ).order(1);
         
                 registry.addInterceptor(new RefreshTokenIntercepter(stringRedisTemplate)).addPathPatterns("/**").order(0);
             }
         }
        ```