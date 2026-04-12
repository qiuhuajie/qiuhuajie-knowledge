1. 首先 **`sqlSession.getMapper`**`(EmpMapper.class)`
    
    ```Java
    //DefaultSqlSession.class
    
    public <T> T getMapper(Class<T> type) {
        return this.configuration.getMapper(type, this);
    }
    ```
    
    1. ==在调用====`getMapper`====之后，会去====`Configuration`====对象中获取 Mapper 对象==
    
    1. 因为==在项目启动的时候就会把 Mapper 接口加载并解析存储到== ==`Configuration`====对象==
        
        - `Configuration` 对象中存储的东西：（点击查看）
            
            > [!important] Configuration 对象中存储的东西：
            > 
            > 1. 数据库相关：
            >     
            >     ![[IMG-20260405035413787.jpeg|Untitled 17.jpeg]]
            >     
            > 
            > 1. 存储了当前 **所有mapper接口的代理工厂** 的一个 Map：**knownMappers**：
            >     
            >     ![[IMG-20260404031808210.jpeg|Untitled 1 6.jpeg]]
            >     
            > 
            > 1. 所有 mapper 接口的方法：
            >     
            >     ![[IMG-20260405035420142.jpeg|Untitled 2 5.jpeg]]
            >     
            > 
            > 1. 加载的所有 sql 映射文件：
            >     
            >     ![[IMG-20260405035421962.jpeg|Untitled 3 5.jpeg]]
            >     
            
        
    
1. **`configuration.getMapper`**`(type, this)`
    
    ```Java
     //Configuration.class
     
     public <T> T getMapper(Class<T> type, SqlSession sqlSession) {
         return this.mapperRegistry.getMapper(type, sqlSession);
     }
    ```
    
1. **`mapperRegistry.getMapper`**`(type, sqlSession)`
    
    1. 根据type类型，==从====`MapperRegistry`====对象中的== ==`knownMappers`====获取到==**==当前类型对应的代理工厂类==**
        
        ![[IMG-20260405035430258.png|Untitled 358.png]]
        
        > [!important] MapperRegistry对象内的HashMap属性 knownMappers 中的数据是在加载mybatis-config配置文件的时候存储进去的
        
    
    1. ==然后通过==**==代理工厂类==**==生成对应 Mapper 的==**==代理类==**[[代理模式 ⭐]]
    
    ```Java
     //MapperRegistry.class
     
     public <T> T getMapper(Class<T> type, SqlSession sqlSession) {
    
         //根据type类型，从MapperRegistry对象中的knownMappers获取到当前类型对应的代理工厂类
         MapperProxyFactory<T> mapperProxyFactory = (MapperProxyFactory)this.knownMappers.get(type);
         if (mapperProxyFactory == null) {
             throw new BindingException("Type " + type + " is not known to the MapperRegistry.");
         } else {
             try {
                 // 然后通过代理工厂类生成对应 Mapper 的代理类
                 return mapperProxyFactory.newInstance(sqlSession);
             } catch (Exception var5) {
                 throw new BindingException("Error getting mapper instance. Cause: " + var5, var5);
             }
         }
     }
    ```
    
1. 最终获取到我们接口对应的代理类`MapperProxy`对象 `empMapper`
    
    ![[IMG-20260405035442431.png|Untitled 1 269.png]]
    
1. 实例获取图解
    
    ![[IMG-20260405035442578.png|Untitled 2 225.png]]