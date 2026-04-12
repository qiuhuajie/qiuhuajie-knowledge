# 1. 介绍
1. 若mapper接口中的方法需要的参数为多个时，此时可以**手动创建**`**map**`集合，将这些数据放在`map`中
1. 只需要通过`${}`和`#{}`访问`map`集合的键就可以获取相对应的值，注意`${}`需要手动加单引号
# 2. 示例
mapper接口：
```Java
 public interface UserMapper {
     User selectUser(Map<String,Object> map);
 }
```
sql 映射文件：

> [!important] ⭐传入的参数本身就是一个
> 
> `map`，直接使用参数本身的键就可以获取到值
```XML
 <mapper namespace="com.qhj.mapper.UserMapper">
     <!--User selectUser(String name,int age)-->
     <select id="selectUser" resultType="com.qhj.pojo.User">
         select * from user where name = #{MapName} and age = #{MapAge}
     </select>
 </mapper>
```
测试：
```Java
 Map<String, Object> map = new HashMap<>();
 map.put("MapName","Tom");
 map.put("MapAge",28);
 User tom = userMapper.selectUser(map);
 System.out.println(tom.toString());
 //User{id=3, name='Tom', age=28, email='test3@baomidou.com'}
```