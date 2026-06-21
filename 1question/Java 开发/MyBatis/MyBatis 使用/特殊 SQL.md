# 特殊 SQL

# **1. 模糊查询 like**

1. sql 中 模糊查询的语句：

    ```sql
     #找出名字中含有O的
     select ename from emp where ename like '%O%';
     
     #找出名字以T结尾的
     select ename from emp where ename like '%T';
    
     #找出名字以K开始的
     select ename from emp where ename like 'K%';
     
     #找出第二个字每是A的
     select ename from emp where ename like '_A%';
    ```

2. 可以看到 `like` 关键字后的模糊查询条件需要使用**单引号** 括起来
3. 由于`#{ }`使用**占位符赋值**的方式拼接`sql`，**自动添加单引号**，故直接将两个 `%` 拼接好就行

    ```java
     public interface UserMapper {
         List<User> testMoHu(@Param("mohu_name") String mohu_name);
     }
    ```

    ```xml
     <mapper namespace="com.qhj.mapper.UserMapper">
         <select id="testMoHu" resultType="com.qhj.pojo.User">
             select * from user where name like "%"#{mohu_name}"%"
         </select>
     </mapper>
    ```


# 2. **批量删除 in**

1. sql 中 批量操作的语句：

    ```sql
     select ename,sal from emp where sal not in(800, 5000, 3000);
    ```

2. 可以看到 `in` 关键字后的查询条件不能使用**单引号** 括起来（**`#{ }` 的方式不能使用**）
3. 由于`${ }`使用**字符串拼接**的方式拼接`sql`，需要手动加单引号（写批量语句时，不添加即可）

    ```java
     public interface UserMapper {
         int deleteMore(@Param("ids") String ids);
     }
    ```

    ```xml
     <mapper namespace="com.qhj.mapper.UserMapper">
         <delete id="deleteMore">
             delete from user where id in (${ids})
         </delete>
     </mapper>
    ```

    ```java
     int i = userMapper.deleteMore("2,3");
     System.out.println(i);
     //2
    ```


# 3. **动态设置表名**

> 在查询前，不能确定从哪个表中搜索数据
>
1. `sql` 语句中的 表名 是不能使用**单引号** 括起来（**`#{ }` 的方式不能使用**）
2. 由于`${` }使用**字符串拼接**的方式拼接`sql`，需要手动加单引号（获取表名时，不添加即可）

    ```java
     public interface UserMapper {
         List<User> getAllUser(@Param("tablename") String tablename);
     }
    ```

    ```xml
     <mapper namespace="com.qhj.mapper.UserMapper">
         <select id="getAllUser" resultType="com.qhj.pojo.User">
             select * from ${tablename}
         </select>
     </mapper>
    ```

    ```java
     List<User> list = userMapper.getAllUser("user");
     for (User user : list) {
         System.out.println(user);
     }
    ```


# 4. **添加自增主键**

1. **`useGeneratedKeys`**：设置使用自增的主键
2. **`keyProperty`**：因为增删改有统一的返回值是受影响的行数，因此只能将获取的自增的主键放在传输的参数`user`对象的某个属性中

    ```java
     int insertUser(User user);
    ```

    ```xml
     <insert id="insertUser" useGeneratedKeys="true" keyProperty="id">
             insert into t_user values(null,#{username},#{password},#{age},#{sex})
     </insert>
    ```