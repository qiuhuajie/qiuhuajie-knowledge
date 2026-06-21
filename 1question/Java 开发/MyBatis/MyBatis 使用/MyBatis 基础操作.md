# MyBatis 基础操作

# 1. **基础 CRUD**

1. **添加**

    ```xml
     <insert id="insertUser">
             insert into t_user values(null,'admin','123456',23,'男')
     </insert>
    ```

2. **删除**

    ```xml
     <delete id="deleteUser">
             delete from t_user where id = 7
     </delete>
    ```

3. **修改**

    ```xml
     <update id="updateUser">
             update t_user set username='ybc',password='123' where id = 6
     </update>
    ```

4. **查询一个实体类**

    ```xml
     <!--User getUserById()-->
     
     <select id="getUserById" resultType="com.atguigu.mybatis.bean.User">
                 select * from t_user where id = 2
     </select>
    ```

    <aside>
    📌

    ⭐查询的标签 select 必须设置属性resultType或resultMap，用于设置实体类和数据库表的映射关系

    1. `resultType`：自动映射，用于属性名和表中字段名一致的情况
    2. `resultMap`：自定义映射，用于一对多或多对一或字段名和属性名不一致的情况[（详见 8. 自定义映射 resultMap）](%E8%87%AA%E5%AE%9A%E4%B9%89%E6%98%A0%E5%B0%84%20resultMap%2025174f8b5df54feeb2aa0ac6433696a6.md)
    </aside>

5. **查询多条数据**

    ```xml
     <!--List<User> getUserList()-->
     
     <select id="getUserList" resultType="com.atguigu.mybatis.bean.User">
             select * from t_user
     </select>
    ```

    - 当查询的数据为多条时，不能使用实体类作为返回值，只能使用集合，否则会抛出异常`TooManyResultsException`
    - 但是若查询的数据只有一条，可以使用实体类或集合作为返回值

# 2. **各种查询功能**

## 2.1 **查询一个实体类对象**

```java
 public interface UserMapper {
     User selectUser(@Param("param_name") String name);
 }
```

```xml
 <mapper namespace="com.qhj.mapper.UserMapper">
      <select id="selectUser" resultType="com.qhj.pojo.User">
         select * from user where name = #{param_name}
     </select>
 </mapper>
```

<aside>
📌 **`@Param`**：可以给入参起一个别名

</aside>

## 2.2 **查询一个 List 集合**

```java
 public interface UserMapper {
     List<User> selectUsers();
 }
```

```xml
 <mapper namespace="com.qhj.mapper.UserMapper">
     <select id="selectUsers" resultType="com.qhj.pojo.User">
         select * from user
     </select>
 </mapper>
```

## 2.3 **查询单个数据**

```java
 public interface UserMapper {
     Integer selectCount();
 }
```

```xml
 <mapper namespace="com.qhj.mapper.UserMapper">
     <select id="selectCount" resultType="integer">
         select count(*) from user
     </select>
 </mapper>
```

## 2.4 **查询一条数据为 Map 集合**

1. 实际开发中，大部分情况都需要从两个表分别查出数据，合并成一个页面的数据，发送至前端
2. 但**后台的实体类中并没有这个实体，故就需要将这些各个表零碎的数据，放在一个Map 中发给前端**，且传到前端就是一个 JSON 数据

```java
 public interface UserMapper {
     Map<String,Object> selectUserAsMap(@Param("name") String name);
 }
```

```xml
 <mapper namespace="com.qhj.mapper.UserMapper">
     <select id="selectUserAsMap" resultType="map">
         select * from user where name = #{name}
     </select>
 </mapper>
```

## 2.5 **查询多条数据为 Map 集合**

```java
 public interface UserMapper {
     Map<String,Object> selectUserAsMap(@Param("name") String name);
 }
```

```xml
 <mapper namespace="com.qhj.mapper.UserMapper">
     <select id="selectUserAsMap" resultType="map">
         select * from user where name = #{name}
     </select>
 </mapper>
```