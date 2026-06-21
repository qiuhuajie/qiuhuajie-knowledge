# Mapper 接口实现类代理对象的获取

1. 首先 **`sqlSession.getMapper**(EmpMapper.class)`

    ```java
    //DefaultSqlSession.class
    
    public <T> T getMapper(Class<T> type) {
        return this.configuration.getMapper(type, this);
    }
    ```

    1. 在调用`getMapper`之后，会去`Configuration`对象中获取 Mapper 对象
    2. 因为在项目启动的时候就会把 Mapper 接口加载并解析存储到 `Configuration`对象
        - `Configuration` 对象中存储的东西：（点击查看）

            <aside>
            📌 Configuration 对象中存储的东西：

            1. 数据库相关：

                ![Untitled](IMG-20260621001313824.jpeg)

            2. 存储了当前 **所有mapper接口的代理工厂** 的一个 Map：**knownMappers**：

                ![Untitled](IMG-20260621001313931.jpeg)

            3. 所有 mapper 接口的方法：

                ![Untitled](IMG-20260621001314025.jpeg)

            4. 加载的所有 sql 映射文件：

                ![Untitled](IMG-20260621001314122.jpeg)

            </aside>

2. **`configuration.getMapper**(type, this)`

    ```java
     //Configuration.class
     
     public <T> T getMapper(Class<T> type, SqlSession sqlSession) {
         return this.mapperRegistry.getMapper(type, sqlSession);
     }
    ```

3. **`mapperRegistry.getMapper**(type, sqlSession)`
    1. 根据type类型，从`MapperRegistry`对象中的 `knownMappers`获取到**当前类型对应的代理工厂类**

        ![[IMG-20260621001314212.png|931]]

        <aside>
        📌 MapperRegistry对象内的HashMap属性 knownMappers 中的数据是在加载mybatis-config配置文件的时候存储进去的

        </aside>

    2. 然后通过**代理工厂类**生成对应 Mapper 的**代理类**[（cglib 动态代理 详见 设计模式 代理模式）](../../%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F/%E7%BB%93%E6%9E%84%E5%9E%8B%E6%A8%A1%E5%BC%8F/%E4%BB%A3%E7%90%86%E6%A8%A1%E5%BC%8F%20%E2%AD%90%20842740694a744703bae301ee954a103e.md)

    ```java
     //MapperRegistry.class
     
     public <T> T getMapper(Class<T> type, SqlSession sqlSession) {
    
         //根据type类型，从MapperRegistry对象中的knownMappers获取到当前类型对应的代理工厂类
         MapperProxyFactory<T> mapperProxyFactory = (MapperProxyFactory)this.knownMappers.get(type);
         if (mapperProxyFactory == null) {
             throw new BindingException("Type " + type + " is not known to the MapperRegistry.");
         } else {
             try {
                 // **然后通过代理工厂类生成对应 Mapper 的代理类**
                 return mapperProxyFactory.newInstance(sqlSession);
             } catch (Exception var5) {
                 throw new BindingException("Error getting mapper instance. Cause: " + var5, var5);
             }
         }
     }
    ```

4. 最终获取到我们接口对应的代理类`MapperProxy`对象 `empMapper`

    ![Untitled](IMG-20260621001314304.png)

5. 实例获取图解

    ![Untitled](IMG-20260621001314331.png)