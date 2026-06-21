# 分页插件 Pagehelper

1. **添加依赖** pom.xml

    ```xml
     <dependency>
         <groupId>com.github.pagehelper</groupId>
         <artifactId>pagehelper</artifactId>
         <version>5.2.0</version>
     </dependency>
    ```

2. **配置分页插件（mybatis 全局配置文件中）**

    ```xml
     <plugins>
         <!--设置分页插件-->
         <plugin interceptor="com.github.pagehelper.PageInterceptor"></plugin>
     </plugins>
    ```

3. **分页插件的使用**
    1. 在**查询功能之前**使用 **`PageHelper.startPage(int pageNum, int pageSize)`** 开启分页功能
        1. `pageNum`：当前页的页码
        2. `pageSize`：每页显示的条数
    2. 在**查询获取list集合之后**，使用 **`PageInfo<T> pageInfo = new PageInfo<>(List<T> list, int navigatePages)`** 获取分页相关数据
        1. `list`：分页之后的数据
        2. `navigatePages`：导航分页的页码数
    3. 常用分页相关数据：
        1. `pageNum`：当前页的页码
        2. `pageSize`：每页显示的条数
        3. `size`：当前页显示的真实条数
        4. `total`：总记录数
        5. `pages`：总页数
        6. `prePage`：上一页的页码
        7. `nextPage`：下一页的页码
        8. `isFirstPage`/`isLastPage`：是否为第一页/最后一页
        9. `hasPreviousPage`/`hasNextPage`：是否存在上一页/下一页
        10. `navigatePages`：导航分页的页码数
        11. `navigatepageNums`：导航分页的页码，[1,2,3,4,5]
4. 测试：

    ```java
     @Test
     public void test() throws IOException {
         InputStream is = Resources.getResourceAsStream("mybatis-config.xml");
         SqlSessionFactoryBuilder sqlSessionFactoryBuilder = new SqlSessionFactoryBuilder();
         SqlSessionFactory sqlSessionFactory = sqlSessionFactoryBuilder.build(is);
     
         SqlSession sqlSession = sqlSessionFactory.openSession(true);
         EmpMapper mapper = sqlSession.getMapper(EmpMapper.class);
     
             //不一定要使用这种方式（常规的查询也可以，这里只是懒得改了）
         //还发现只要不给 empExample 创建条件，它就是查询全部
         EmpExample empExample = new EmpExample();
     
         //3 是显示的当前页是第几页，4 是每页放的记录数
         PageHelper.startPage(3,4);
    
         List<Emp> emps = mapper.selectByExample(empExample);
         for (Emp emp : emps) {
             System.out.println(emp);
         }
    
         //查询后，获取 页面信息：
                 //emps 是查询结果
                 //5 表示在 页面信息中的 navigatepageNums=[4, 5, 6, 7, 8]（可以帮助实现前端页面的 页码点击按钮，比如当前在第6页，故只会有 4, 5, 6, 7, 8 按钮的效果 ）
         PageInfo<Emp> empPageInfo = new PageInfo<>(emps, 5);
         System.out.println(empPageInfo);
     
     }
    ```

5. 测试结果：

    ```java
     Emp{eid=9, empName='j', age=null, dept='null'}
     Emp{eid=10, empName='r', age=null, dept='null'}
     Emp{eid=11, empName='d', age=null, dept='null'}
     Emp{eid=12, empName='d', age=null, dept='null'}
     
     PageInfo{pageNum=3, pageSize=4, size=4, startRow=9, endRow=12, total=14, pages=4, list=Page{count=true, pageNum=3, pageSize=4, startRow=8, endRow=12, total=14, pages=4, reasonable=false, pageSizeZero=false}[Emp{eid=9, empName='j', age=null, dept='null'}, Emp{eid=10, empName='r', age=null, dept='null'}, Emp{eid=11, empName='d', age=null, dept='null'}, Emp{eid=12, empName='d', age=null, dept='null'}], prePage=2, nextPage=4, isFirstPage=false, isLastPage=false, hasPreviousPage=true, hasNextPage=true, navigatePages=5, navigateFirstPage=1, navigateLastPage=4, navigatepageNums=[1, 2, 3, 4, 5]}
    ```