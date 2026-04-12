1. 当 获得 mapper 接口的代理类对象 empMapper 后
1. empMapper 调用 mapper 接口中的方法，实际是调用了 MapperProxy 的 invoke 方法（动态代理）
    
    ```Java
     //MapperProxy.class
     
     public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
         try {
             //这里是一个三目运算：
                 //1.Mapper接口也继承Object类，拥有Object的方法。判断如果调用的是Object对象的方法（如 toString()方法）直接反射调用就行：method.getDeclaringClass()
                 //2.否则调用 cachedInvoker(method).invoke()
             //这里最后判断执行的就是 ：后面的代码
             return Object.class.equals(method.getDeclaringClass()) ? method.invoke(this, args) : this.cachedInvoker(method).invoke(proxy, method, args, this.sqlSession);
         } catch (Throwable var5) {
             throw ExceptionUtil.unwrapThrowable(var5);
         }
     }
    ```
    
1. `this.cachedInvoker(method)`：调用 MapperProxy 内部类 MapperMethodInvoker 中的方法 cachedInvoker( )
    
    ```Java
     //MapperProxy.class
     
     private MapperProxy.MapperMethodInvoker cachedInvoker(Method method) throws Throwable {
         try {
             return (MapperProxy.MapperMethodInvoker)MapUtil.computeIfAbsent(this.methodCache, method, (m) -> {
                 //这里面会有一个判断，判断一下我们是不是default方法
                 if (m.isDefault()) {
                                 ...
                 } else {
                     //如果不是default方法，会 new 一个 MapperProxy 的内部类 PlainMethodInvoker 的一个对象
                     return new MapperProxy.PlainMethodInvoker(new MapperMethod(this.mapperInterface, method, this.sqlSession.getConfiguration()));
                 }
             });
         } catch (RuntimeException var4) {
             Throwable cause = var4.getCause();
             throw (Throwable)(cause == null ? var4 : cause);
         }
     }
    ```
    
    在 new PlainMethodInvoker 对象时，构造参数需要 new 一个 MapperMethod 对象
    
    > [!important]
    > 
    > - **PlainMethodInvoker**：类是Mapper接口普通方法的调用类，它实现了MethodInvoker接口。其内部封装了MapperMethod实例
    > 
    > - **MapperMethod**：封装了Mapper接口中对应方法的信息，以及对应的SQL语句的信息；它是mapper接口与映射配置文件中SQL语句的桥梁
    >     
    >     ![[Attachment/1question/大数据/Java 开发/MyBatis/MyBatis 原理/IMG-20260405035413788.png|Untitled 359.png]]
    >     
    
    ```Java
     public class MapperMethod {
         //记录了 sql 语句，以及 sql 语句的类型
         private final MapperMethod.SqlCommand command;
         //记录了 Mapper 接口中的方法信息
         private final MapperMethod.MethodSignature method;
     
         public MapperMethod(Class<?> mapperInterface, Method method, Configuration config) {
             this.command = new MapperMethod.SqlCommand(config, mapperInterface, method);
             this.method = new MapperMethod.MethodSignature(config, mapperInterface, method);
         }
         ......
     }
    ```
    
1. 跳出`cachedInvoker()`方法后，该方法返回得到的 PlainMethodInvoker 对象 继续调用其 `invoke()` 方法
    
    ```Java
     //MapperProxy.class（PlainMethodInvoker.class 是 MapperProxy的内部类）
     
     private static class PlainMethodInvoker implements MapperProxy.MapperMethodInvoker {
         private final MapperMethod mapperMethod;
     
         public PlainMethodInvoker(MapperMethod mapperMethod) {
             this.mapperMethod = mapperMethod;
         }
     
         //底层实际是 mapperMethod 对象调用 execute()方法
         public Object invoke(Object proxy, Method method, Object[] args, SqlSession sqlSession) throws Throwable {
             return this.mapperMethod.execute(sqlSession, args);
         }
     }
    ```
    
1. `mapperMethod.execute(sqlSession, args)`：
    
    ```Java
     public Object execute(SqlSession sqlSession, Object[] args) {
         Object result;
         Object param;
         switch(this.command.getType()) {
    
         //会从 MapperMethod 对象的 command 属性中取出当前 sql 语句的类型，不同的类型执行不同的方法
         case INSERT:
             param = this.method.convertArgsToSqlCommandParam(args);
             result = this.rowCountResult(sqlSession.insert(this.command.getName(), param));
             break;
         case UPDATE:
             param = this.method.convertArgsToSqlCommandParam(args);
             result = this.rowCountResult(sqlSession.update(this.command.getName(), param));
             break;
         case DELETE:
             param = this.method.convertArgsToSqlCommandParam(args);
             result = this.rowCountResult(sqlSession.delete(this.command.getName(), param));
             break;
         case SELECT:
             if (this.method.returnsVoid() && this.method.hasResultHandler()) {
                 this.executeWithResultHandler(sqlSession, args);
                 result = null;
             } else if (this.method.returnsMany()) {
                 //查询返回多个实体
                 result = this.executeForMany(sqlSession, args);
             } else if (this.method.returnsMap()) {
                 //查询返回多个Map
                 result = this.executeForMap(sqlSession, args);
             } else if (this.method.returnsCursor()) {
                 result = this.executeForCursor(sqlSession, args);
             } else {
             //查询返回一个实体：
                 //1.解析参数
                 //由于 debug 测试使用的查询方法是用 @Param 标注了参数名，首先会将参数做转换
                 //所以这里需要将Mapper接口方法中的多个参数转化为一个ParamMap
                 param = this.method.convertArgsToSqlCommandParam(args);
    
                 //2.动态代理最后还是使用SqlSession操作数据库的
                 result = sqlSession.selectOne(this.command.getName(), param);
    
                 if (this.method.returnsOptional() && (result == null || !this.method.getReturnType().equals(result.getClass()))) {
                     result = Optional.ofNullable(result);
                 }
             }
             ...
         }
     
         if (result == null && this.method.getReturnType().isPrimitive() && !this.method.returnsVoid()) {
             ...
         } else {
             return result;
         }
     }
    ```
    
1. `sqlSession.selectOne( )`，实际是 DefaultSqlSession.class对象调用 `selectList()` 方法
    
    ```Java
     //DefaultSqlSession.class
     
     public <T> T selectOne(String statement, Object parameter) {
    
         //DefaultSqlSession对象调用selectList( ) 方法
         List<T> list = this.selectList(statement, parameter);
         if (list.size() == 1) {
             //返回结果
             return list.get(0);
         } else if (list.size() > 1) {
             throw new TooManyResultsException("Expected one result (or null) to be returned by selectOne(), but found: " + list.size());
         } else {
             return null;
         }
     }
    ```
    
1. `selectList()` 执行 sql 语句，返回查询结果
    
    ```Java
     //DefaultSqlSession.class
     
     private <E> List<E> selectList(String statement, Object parameter, RowBounds rowBounds, ResultHandler handler) {
         List var6;
         try {
             //获取 MappedStatement
             MappedStatement ms = this.configuration.getMappedStatement(statement);
    
             //执行 sql 语句
             var6 = this.executor.query(ms, this.wrapCollection(parameter), rowBounds, handler);
         } catch (Exception var10) {
             throw ExceptionFactory.wrapException("Error querying database.  Cause: " + var10, var10);
         } finally {
             ErrorContext.instance().reset();
         }
      
         return var6;
     }
    ```
    
    ![[IMG-20260404031809163.png|Untitled 1 270.png]]