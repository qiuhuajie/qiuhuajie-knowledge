- [[#1. 实现URL 黑白名单拦截]]
- [[#2. 对 Token 进行校验]]
- [[#3. 对指定 route 限流]]
- [[#4. 解决跨域问题]]
# 1. **实现URL 黑白名单拦截**
- 第一个全局过滤器：
    
    ```Java
    @Component
    public class GlobalAuthFilter implements GlobalFilter, Ordered {
    
        @Autowired
        private JwtTokenConfig jwtTokenConfig;
        @Autowired
        private IgnoreUrlsConfig ignoreUrlsConfig;
        @Autowired
        private JwtConfig jwtConfig;
        @Autowired
        private Logger logger;
        @Autowired
        private SysUserAuth sysUserAuth;
    
    		// 给多个过滤器设置过滤顺序
        @Override
        public int getOrder() {
            return 1;
        }
    
        @Override
        public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
            ServerHttpRequest request = exchange.getRequest();
            ServerHttpResponse response = exchange.getResponse();
            HttpHeaders headers = request.getHeaders();
            List<String> tokenHeaders = headers.get(jwtConfig.getTokenHeader());
            
            // ⭐从 nacos 中获取白名单配置信息，对当前 URL 进行白名单鉴定        
            PathMatcher pathMatcher = new AntPathMatcher();
            for (String path : ignoreUrlsConfig.getUrls()) {
                if (pathMatcher.match(path, request.getURI().getPath())) {
                    return chain.filter(exchange);
                }
            }
    
    				DataBuffer buffer = getDataBuffer(response, "当前 URL 属于黑名单");
            return response.writeWith(Mono.just(buffer));
    
        }
    
        private DataBuffer getDataBuffer(ServerHttpResponse response, String message) {
            Map<String, String> dataMap = new HashMap<>(4);
            dataMap.put("message", message);
            byte[] bits = JSON.toJSONString(CommonResult.unauthorized(dataMap, message)).getBytes(StandardCharsets.UTF_8);
            DataBuffer buffer = response.bufferFactory().wrap(bits);
            response.setStatusCode(HttpStatus.UNAUTHORIZED);
            response.getHeaders().add("Content-Type", "text/json;charset=UTF-8");
            return buffer;
        }
    }
    ```
    
# 2. **对 Token 进行校验**
- 第二个全局过滤器
    
    ```Java
    @Component
    public class GlobalAuthFilter implements GlobalFilter, Ordered {
    
        @Autowired
        private JwtTokenConfig jwtTokenConfig;
        @Autowired
        private IgnoreUrlsConfig ignoreUrlsConfig;
        @Autowired
        private JwtConfig jwtConfig;
        @Autowired
        private Logger logger;
        @Autowired
        private SysUserAuth sysUserAuth;
    
    		// 给多个过滤器设置过滤顺序
        @Override
        public int getOrder() {
            return 2;
        }
    
        @Override
        public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
            ServerHttpRequest request = exchange.getRequest();
            ServerHttpResponse response = exchange.getResponse();
            HttpHeaders headers = request.getHeaders();
            List<String> tokenHeaders = headers.get(jwtConfig.getTokenHeader());
    
            // ⭐对 Token 进行校验（Token 的格式、是否过期）
    	      // 取出 authorization 字段
            String authHeader = null;
            if (!CollectionUtils.isEmpty(tokenHeaders)) {
                authHeader = tokenHeaders.get(0);
            }
    
            if (StringUtils.isNotBlank(authHeader) && authHeader.startsWith(jwtConfig.getTokenHead())) {
                String authToken = authHeader.substring(jwtConfig.getTokenHead().length());
                if (jwtTokenConfig.getClaimsFromToken(authToken) == null) {
                    DataBuffer buffer = getDataBuffer(response, "token错误");
                    return response.writeWith(Mono.just(buffer));
                }
                if (!jwtTokenConfig.validateToken(authToken)) {
                    DataBuffer buffer = getRefreshTokenBuffer(response, "token已过期");
                    return response.writeWith(Mono.just(buffer));
                }
                JwtUserInfo jwtUserInfo = jwtTokenConfig.getUserNameFromToken(authToken);
                if (jwtUserInfo == null) {
                    DataBuffer buffer = getDataBuffer(response, "token无效");
                    return response.writeWith(Mono.just(buffer));
                }
                List<String> platformUid = headers.get("platformUid");
                if (CollectionUtils.isEmpty(platformUid)) {
                    DataBuffer buffer = getDataBuffer(response, "请求头未包含platformUid");
                    return response.writeWith(Mono.just(buffer));
                }
                if (!sysUserAuth.checkUserCanAccess(jwtUserInfo.getRoleId(), platformUid.get(0))) {
                    DataBuffer buffer = getDataBuffer(response, "无该平台访问权限");
                    return response.writeWith(Mono.just(buffer));
                }
                if (!sysUserAuth.checkUserValid(jwtUserInfo.getUid())) {
                    DataBuffer buffer = getDataBuffer(response, "账号不存在或已禁用,请联系管理员");
                    return response.writeWith(Mono.just(buffer));
                }
    
            } else {
                DataBuffer buffer = getDataBuffer(response, "header中无授权信息");
                return response.writeWith(Mono.just(buffer));
            }
            return chain.filter(exchange);
    
        }
    
        private DataBuffer getDataBuffer(ServerHttpResponse response, String message) {
            Map<String, String> dataMap = new HashMap<>(4);
            dataMap.put("message", message);
            byte[] bits = JSON.toJSONString(CommonResult.unauthorized(dataMap, message)).getBytes(StandardCharsets.UTF_8);
            DataBuffer buffer = response.bufferFactory().wrap(bits);
            response.setStatusCode(HttpStatus.UNAUTHORIZED);
            response.getHeaders().add("Content-Type", "text/json;charset=UTF-8");
            return buffer;
        }
    
    
        private DataBuffer getRefreshTokenBuffer(ServerHttpResponse response, String message) {
            Map<String, String> dataMap = new HashMap<>(4);
            dataMap.put("message", message);
            byte[] bits = JSON.toJSONString(CommonResult.refreshToken(dataMap, message)).getBytes(StandardCharsets.UTF_8);
            DataBuffer buffer = response.bufferFactory().wrap(bits);
            response.setStatusCode(HttpStatus.UNAUTHORIZED);
            response.getHeaders().add("Content-Type", "text/json;charset=UTF-8");
            return buffer;
        }
    }
    ```
    
# 3. 对指定 Route 限流
1. gateway 的限流实际使用的是 ==Redis 加 lua 脚本的方式实现的==**==令牌桶==**
1. 对 gateway 进行配置
    
    1. 主要就是配一下令牌的生成速率、令牌桶的存储量上限，以及用于限流的键的解析器
    
    1. 这里设置的桶上限为2，每秒填充1个令牌
    
    ```YAML
    spring:
      application:
        name: gateway-test
      cloud:
        gateway:
          routes:
            - id: limit_route
              uri: lb://sentinel-test
              predicates:
              - Path=/sentinel-test/**
              filters:
                - name: RequestRateLimiter
                  args:
                    # 令牌桶每秒填充平均速率
                    redis-rate-limiter.replenishRate: 1
                    # 令牌桶上限
                    redis-rate-limiter.burstCapacity: 2
                    # 指定解析器，使用spEl表达式按beanName从spring容器中获取
                    key-resolver: "#{@pathKeyResolver}"
                - StripPrefix=1
      redis:
        host: 127.0.0.1
        port: 6379
    ```
    
1. 我们使用请求的路径作为限流的键，编写对应的解析器
    
    ```Java
    @Slf4j
    @Component
    public class PathKeyResolver implements KeyResolver {
        public Mono<String> resolve(ServerWebExchange exchange) {
            String path = exchange.getRequest().getPath().toString();
            log.info("Request path: {}",path);
            return Mono.just(path);
        }
    }
    ```
    
1. gateway 实现限流的关键是 `spring-cloud-gateway-core` 包中的 `RedisRateLimiter` 类，以及 `META-INF/scripts` 中的 `request-rate-limiter.lua` 这个脚本
# 4. **解决跨域问题**
1. **跨域的概念和原理**
    
    1. 跨域：请求位置和被请求位置不同源就会发生跨域
    
    1. 这里的不同源包括两个点：
        
        - 域名不同：www.baidu.com 和 www.taobao.com。（IP不同也是相同道理）
        
        - 端口不同：127.0.0.1:8080和127.0.0.1:8081
        
    
    1. 而==浏览器又会禁止请求的发起者与服务端发生跨域AJAX请求==
    
    1. 如果发生了跨域请求，服务器端是能够正常响应的，但是响应的结果会被浏览器拦截
    
1. **gateway 中解决跨域问题**，配置application.yml文件
    
    ```YAML
    spring:
      cloud:
        gateway:
          globalcors: # 全局的跨域配置
            add-to-simple-url-handler-mapping: true # 解决options请求被拦截问题
                   # options请求 就是一种询问服务器是否浏览器可以跨域的请求
                   # 如果每次跨域都有询问服务器是否浏览器可以跨域对性能也是损耗
                   # 可以配置本次跨域检测的有效期maxAge
                   # 在maxAge设置的时间范围内，不去询问，统统允许跨域
            corsConfigurations:
              '[/**]':
                allowedOrigins:   # 允许哪些网站的跨域请求 
                  - "http://localhost:8090"
                allowedMethods:   # 允许的跨域ajax的请求方式
                  - "GET"
                  - "POST"
                  - "DELETE"
                  - "PUT"
                  - "OPTIONS"
                allowedHeaders: "*"  # 允许在请求中携带的头信息
                allowCredentials: true # 允许在请求中携带cookie
                maxAge: 360000    # 本次跨域检测的有效期(单位毫秒)
                      # 有效期内，跨域请求不会一直发option请求去增大服务器压力
    ```