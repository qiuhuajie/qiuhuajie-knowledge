- [[#1. 基础 CRUD]]
- [[#2. 各种查询功能]]
    - [[#2.1 查询一个实体类对象]]
    - [[#2.2 查询一个 List 集合]]
    - [[#2.3 查询单个数据]]
    - [[#2.4 查询一条数据为 Map 集合]]
    - [[#2.5 查询多条数据为 Map 集合]]
# 1. **基础 CRUD**
1. **添加**
    
    ```XML
     <insert id="insertUser">
             insert into t_user values(null,'admin','123456',23,'男')
     </insert>
    ```
    
1. **删除**
    
    ```XML
     <delete id="deleteUser">
             delete from t_user where id = 7
     </delete>
    ```
    
1. **修改**
    
    ```XML
     <update id="updateUser">
             update t_user set username='ybc',password='123' where id = 6
     </update>
    ```
    
1. **查询一个实体类**
    
    ```XML
     <!--User getUserById()-->
     
     <select id="getUserById" resultType="com.atguigu.mybatis.bean.User">
                 select * from t_user where id = 2
     </select>
    ```
    
    > [!important]
    > 
    > ⭐查询的标签 select 必须设置属性resultType或resultMap，用于设置实体类和数据库表的映射关系
    > 
    > 1. `resultType`：自动映射，用于属性名和表中字段名一致的情况
    > 
    > 1. `resultMap`：自定义映射，用于一对多或多对一或字段名和属性名不一致的情况[[自定义映射 resultMap]]
    
1. **查询多条数据**
    
    ```XML
     <!--List<User> getUserList()-->
     
     <select id="getUserList" resultType="com.atguigu.mybatis.bean.User">
             select * from t_user
     </select>
    ```
    
    - 当查询的数据为多条时，不能使用实体类作为返回值，只能使用集合，否则会抛出异常`TooManyResultsException`
    
    - 但是若查询的数据只有一条，可以使用实体类或集合作为返回值
    
# 2. **各种查询功能**
## 2.1 **查询一个实体类对象**
```Java
 public interface UserMapper {
     User selectUser(@Param("param_name") String name);
 }
```
```XML
 <mapper namespace="com.qhj.mapper.UserMapper">
      <select id="selectUser" resultType="com.qhj.pojo.User">
         select * from user where name = #{param_name}
     </select>
 </mapper>
```

> [!important] **`@Param`**
> 
> ：可以给入参起一个别名
## 2.2 **查询一个 List 集合**
```Java
 public interface UserMapper {
     List<User> selectUsers();
 }
```
```XML
 <mapper namespace="com.qhj.mapper.UserMapper">
     <select id="selectUsers" resultType="com.qhj.pojo.User">
         select * from user
     </select>
 </mapper>
```
## 2.3 **查询单个数据**
```Java
 public interface UserMapper {
     Integer selectCount();
 }
```
```XML
 <mapper namespace="com.qhj.mapper.UserMapper">
     <select id="selectCount" resultType="integer">
         select count(*) from user
     </select>
 </mapper>
```
## 2.4 **查询一条数据为 Map 集合**
1. 实际开发中，大部分情况都需要从两个表分别查出数据，合并成一个页面的数据，发送至前端
1. 但**后台的实体类中并没有这个实体，故就需要将这些各个表零碎的数据，放在一个Map 中发给前端**，且传到前端就是一个 JSON 数据
```Java
 public interface UserMapper {
     Map<String,Object> selectUserAsMap(@Param("name") String name);
 }
```
```XML
 <mapper namespace="com.qhj.mapper.UserMapper">
     <select id="selectUserAsMap" resultType="map">
         select * from user where name = #{name}
     </select>
 </mapper>
```
## 2.5 **查询多条数据为 Map 集合**
```Java
 public interface UserMapper {
     Map<String,Object> selectUserAsMap(@Param("name") String name);
 }
```
```XML
 <mapper namespace="com.qhj.mapper.UserMapper">
     <select id="selectUserAsMap" resultType="map">
         select * from user where name = #{name}
     </select>
 </mapper>
```