1. 可以通过`@Param`注解标识mapper接口中的方法参数
1. 此时，**会将这些参数放在map集合中，以**`**@Param**`**注解的value属性值为键**，以参数为值；以`param1,param2...`为键，以参数为值
1. 只需要通过`${}`和`#{}`访问map集合的键就可以获取相对应的值，注意`${}`需要手动加单引号
mapper接口：
```Java
 public interface UserMapper {
     User selectUser(@Param("param_name") String name, @Param("param_age") int age);
 }
```

> ⭐@Param 就是标注：让 mybatis 自动将参数放入 map 时，使用什么 键
sql 映射文件：
```XML
 <mapper namespace="com.qhj.mapper.UserMapper">
     <!--User selectUser(String name,int age)-->
     <select id="selectUser" resultType="com.qhj.pojo.User">
         select * from user where name = #{param_name} and age = #{param_age}
     </select>
 </mapper>
```
测试：
```Java
 User tom = userMapper.selectUser("Tom",28);
 System.out.println(tom.toString());
 //User{id=3, name='Tom', age=28, email='test3@baomidou.com'}
```