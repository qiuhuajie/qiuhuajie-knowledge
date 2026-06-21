---
title: "方案 2：HTTP + JDK 动态代理 + SpringBoot"
tags:
  - "Spring_Boot"
  - "Result"
  - "HttpUtil"
  - "MainController"
  - "ServiceProxy"
  - "UserService"
updated: 2026-04-16
---
- [[#一、服务消费端]]
    - [[#1. `RemoteClass`]]
    - [[#2. `UserService`]]
    - [[#3. `MainController`]]
    - [[#4. `ServiceBeanDefinitionRegistry`]]
    - [[#5. `ServiceFactory`]]
    - [[#6. `ServiceProxy`]]
    - [[#7. `HttpUtil`]]
    - [[#8. `Result`]]
- [[#二、服务提供端]]
    - [[#1. `MainController`]]
    - [[#2. `ServiceGetter`]]
    - [[#3. `Result`]]
    - [[#4. `UserService`]]

# 一、服务消费端

* https://github.com/yeecode/EasyRPC
    ![[IMG-20260621000641999.png|351]]
## 1. `RemoteClass`
```Java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface RemoteClass {
    String value();
}
```
## 2. `UserService`
```Java
@Service
@RemoteClass("com.github.yeecode.easyrpc.server.service.UserService")
public interface UserService {
    Integer getUserCount();
}
```
## 3. `MainController`
```Java
@RestController
public class MainController {
    @Autowired
    private UserService userService;
    @RequestMapping("/getUserCount")
    public String getUserCount() {
        Integer userCount = userService.getUserCount();
        return userCount.toString();
    }
}
```

> **如何实现让 `userService.getUserCount()` 这行代码去执行代理对象中的网络调用代码逻辑**
> 1. 可以将 代理对象在 Spring 初始化 Bean 时就交给 Spring 容器管理，具体代码在 `ServiceBeanDefinitionRegistry` 中的`postProcessBeanDefinitionRegistry()` 方法中
> 2. 初始化好代理对象的 bean 后，debug 查看：这里依赖注入的 UserService 就是一个 `ServiceProxy`对象，并不是像之前的 SpringBoot 项目一样，是一个 UserService 的实现类对象
> 3. 里面维护的 `target` 对象就是被代理接口类的一个代理对象
> ![[IMG-20260621000642106.png|735]]
> 4. 然后，`userService.getUserCount()` 执行会直接进入 JDK 动态代理的钩子函数中，即 `ServiceProxy` 的 `invoke()`
## 4. `ServiceBeanDefinitionRegistry`
```Java
@Component
public class ServiceBeanDefinitionRegistry implements BeanDefinitionRegistryPostProcessor, ResourceLoaderAware, ApplicationContextAware {
    private static final String DEFAULT_RESOURCE_PATTERN = "**/*.class";
    private static ApplicationContext applicationContext;
    private MetadataReaderFactory metadataReaderFactory;
    private ResourcePatternResolver resourcePatternResolver;
    @Override
    public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) throws BeansException {
				// 将所有接口的类扫描到
        Set<Class<?>> clazzSet = scannerPackages("com.github.yeecode.easyrpc.client.remoteservice");
				// 使用 stream 流将所有接口类的代理对象Bean注册到 Spring 容器中
        clazzSet.stream().filter(Class::isInterface).forEach(x -> registerBean(registry, x));
    }
    /**
     * 注册Bean
     */
    private void registerBean(BeanDefinitionRegistry registry, Class clazz) {
        BeanDefinitionBuilder builder = BeanDefinitionBuilder.genericBeanDefinition(clazz);
        GenericBeanDefinition definition = (GenericBeanDefinition) builder.getRawBeanDefinition();
        definition.getConstructorArgumentValues().addGenericArgumentValue(clazz);
				// 设值代理工厂
        definition.setBeanClass(ServiceFactory.class);
        definition.setAutowireMode(GenericBeanDefinition.AUTOWIRE_BY_TYPE);
        registry.registerBeanDefinition(clazz.getSimpleName(), definition);
    }
    /**
     * 扫描获取指定路径及子路径下的所有类
     */
    private Set<Class<?>> scannerPackages(String basePackage) {
        Set<Class<?>> set = new LinkedHashSet<>();
        String basePackageName = ClassUtils.convertClassNameToResourcePath(applicationContext.getEnvironment().resolveRequiredPlaceholders(basePackage));
        String packageSearchPath = ResourcePatternResolver.CLASSPATH_ALL_URL_PREFIX +
                basePackageName + '/' + DEFAULT_RESOURCE_PATTERN;
        try {
            Resource[] resources = this.resourcePatternResolver.getResources(packageSearchPath);
            for (Resource resource : resources) {
                if (resource.isReadable()) {
                    MetadataReader metadataReader = this.metadataReaderFactory.getMetadataReader(resource);
                    String className = metadataReader.getClassMetadata().getClassName();
                    Class<?> clazz;
                    try {
                        clazz = Class.forName(className);
                        set.add(clazz);
                    } catch (ClassNotFoundException e) {
                        e.printStackTrace();
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return set;
    }
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
    }
    @Override
    public void setResourceLoader(ResourceLoader resourceLoader) {
        this.resourcePatternResolver = ResourcePatternUtils.getResourcePatternResolver(resourceLoader);
        this.metadataReaderFactory = new CachingMetadataReaderFactory(resourceLoader);
    }
    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        this.applicationContext = applicationContext;
    }
}
```
## 5. `ServiceFactory`
1. **实现** **`FactoryBean`** **的类是Spring Bean的一种：工厂 Bean， `getObject()` 可以定义bean返回的对象类型**[[2.2 IOC 相关概念]]
2. 这里我们需要的是一个特殊的 Bean，即一个根据 RPC 案例需求**代理扩展**后的 Bean
    ```Java
    // 代理类工厂
    public class ServiceFactory<T> implements FactoryBean<T> {
        private Class<T> interfaceType;
        public ServiceFactory(Class<T> interfaceType) {
            this.interfaceType = interfaceType;
        }
        @Override
        public T getObject() {
            InvocationHandler handler = new ServiceProxy<>(interfaceType);
    				// 返回代理对象
            return (T) Proxy.newProxyInstance(interfaceType.getClassLoader(),
                    new Class[]{interfaceType}, handler);
        }
        @Override
        public Class<T> getObjectType() {
            return interfaceType;
        }
        @Override
        public boolean isSingleton() {
            return true;
        }
    }
    ```
## 6. `ServiceProxy`
```Java
// JDK 动态代理所需要的 InvocationHandler
public class ServiceProxy<T> implements InvocationHandler {
    private T target;
    public ServiceProxy(T target) {
        this.target = target;
    }
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        RemoteClass remoteClass = method.getDeclaringClass().getAnnotation(RemoteClass.class);
        if (remoteClass == null) {
            throw new Exception("远程类标志未指定");
        }
        List<String> argTypeList = new ArrayList<>();
        if (args != null) {
            for (Object obj : args) {
                argTypeList.add(obj.getClass().getName());
            }
        }
        String argTypes = JSON.toJSONString(argTypeList);
        String argValues = JSON.toJSONString(args);
				// 将 RPC 请求所需要的参数数据（方法名、参数类型、参数值等）获取到，传入到 HTTP 请求发起的方法中
        Result result = HttpUtil.callRemoteService(remoteClass.value(), method.getName(), argTypes, argValues);
        if (result.isSuccess()) {
            return JSON.parseObject(result.getResultValue(), Class.forName(result.getResultType()));
        } else {
            throw new Exception("远程调用异常：" + result.getMessage());
        }
    }
}
```
## 7. `HttpUtil`
```Java
public class HttpUtil {
		// 将 RPC 调用请求需要的数据（方法名、参数类型、参数值等）封装在一个 List 中
    public static synchronized Result callRemoteService(String identifier, String methodName, String argTypes, String argValues) {
        try {
            List<NameValuePair> paramsList = new ArrayList<>();
            paramsList.add(new BasicNameValuePair("identifier", identifier));
            paramsList.add(new BasicNameValuePair("methodName", methodName));
            paramsList.add(new BasicNameValuePair("argTypes", argTypes));
            paramsList.add(new BasicNameValuePair("argValues", argValues));
            String result = sendPost("http://127.0.0.1:12311/", paramsList);
            return JSON.parseObject(result, Result.class);
        } catch (Exception ex) {
            return Result.getFailResult("触发远程调用失败");
        }
    }
		// 发送 HTTP 请求
    private static synchronized String sendPost(String url, List<NameValuePair> nameValuePairList) throws Exception {
        CloseableHttpResponse response = null;
        try (CloseableHttpClient client = HttpClients.createDefault()) {
            HttpPost post = new HttpPost(url);
            StringEntity entity = new UrlEncodedFormEntity(nameValuePairList, "UTF-8");
            post.setEntity(entity);
            response = client.execute(post);
            int statusCode = response.getStatusLine().getStatusCode();
            if (200 == statusCode) {
                return EntityUtils.toString(response.getEntity(), "UTF-8");
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (response != null) {
                response.close();
            }
        }
        return null;
    }
}
```
## 8. `Result`
```Java
// 请求返回结果的封装
public class Result {
    private Boolean success;
    private String message;
    private String resultType;
    private String resultValue;
    public Result(Boolean success, String message, String resultType, String resultValue) {
        this.success = success;
        this.message = message;
        this.resultType = resultType;
        this.resultValue = resultValue;
    }
    public static Result getSuccessResult(String resultType, String resultValue) {
        return new Result(true, "成功", resultType, resultValue);
    }
    public static Result getFailResult(String reason) {
        return new Result(false, reason, null, null);
    }
}
```
# 二、服务提供端
## 1. `MainController`
```Java
@RestController
public class MainController {
		// 所有由服务消费端发来的请求都是 "http://127.0.0.1:12311/" 这个url，要看是调用的哪个方法，需要解析传来的参数
    @RequestMapping("/")
    public Result rpcMain(String identifier, String methodName, String argTypes, String argValues) {
        try {
            Class clazz = Class.forName(identifier);
            if (clazz == null) {
                return Result.getFailResult("目标类不存在");
            }
            List<String> argTypeList = JSON.parseArray(argTypes, String.class);
            List<Class> argClassList = new ArrayList<>();
            for (String argType : argTypeList) {
                argClassList.add(Class.forName(argType));
            }
            Class[] argClassArray = new Class[argClassList.size()];
            argClassList.toArray(argClassArray);
            List<String> argValueStringList = JSON.parseArray(argValues, String.class);
            List<Object> argValueList = new ArrayList<>();
            for (int i = 0; i < argTypeList.size(); i++) {
                if (argClassList.get(i).equals(String.class)) {
                    argValueList.add(argValueStringList.get(i));
                } else {
                    argValueList.add(JSON.parseObject(argValueStringList.get(i), argClassList.get(i)));
                }
            }
            Object[] args = new Object[argValueList.size()];
            argValueList.toArray(args);
            Method method = clazz.getMethod(methodName, argClassArray);
            if (method == null) {
                return Result.getFailResult("目标方法不存在");
            }
            Object obj = ServiceGetter.getServiceByClazz(clazz);
            if (obj == null) {
                return Result.getFailResult("目标类的实例无法生成");
            }
						// ⭐服务提供端是由接口的具体实现类的，因此直接调用对应的方法即可
            Object result = method.invoke(obj, args);
            return Result.getSuccessResult(method.getReturnType().getName(), JSON.toJSONString(result));
        } catch (Exception ex) {
            ex.printStackTrace();
            return Result.getFailResult("服务端解析异常");
        }
    }
}
```
## 2. `ServiceGetter`
```Java
public class ServiceGetter {
		// 服务端可以用户一个 Map 来实现 Service对象 的注册与管理
    private static Map<Class, Object> serviceMap = new HashMap<>();
    public static <T> T getServiceByClazz(Class<T> clazz) {
        try {
            if (serviceMap.containsKey(clazz)) {
                return (T) serviceMap.get(clazz);
            } else {
                T bean = clazz.newInstance();
                serviceMap.put(clazz, bean);
                return bean;
            }
        } catch (Exception ex) {
            ex.printStackTrace();
            return null;
        }
    }
}
```
## 3. `Result`
```Java
同上
```
## 4. `UserService`
```Java
// 方法的具体实现类
public class UserService {
    public Integer getUserCount() {
        System.out.println("Method getUserCount called:");
        System.out.println("*************************");
        return 18;
    }
}
```