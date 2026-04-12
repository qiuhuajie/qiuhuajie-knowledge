- [[#1. if]]
- [[#2. where]]
- [[#3. trim]]
- [[#4. choose、when、otherwise]]
- [[#5. foreach]]
- [[#6. SQL 片段]]

> [!important] Mybatis框架的动态SQL技术是一种根据特定条件
> 
> **动态拼装SQL语句**的功能，它存在的意义是为了解决拼接SQL语句字符串时的痛点问题
# 1. **if**
1. if 标签可通过**`test`**属性的表达式进行判断
    
    1. 若表达式（`ename != '' and ename != null`）的结果为`true`，则标签中的内容会执行
    
    1. 反之标签中的内容（`and ename = #{ename}`）不会执行
        
        ```XML
         <select id="getEmpListByMoreTJ" resultType="Emp">
             select * from t_emp where
             <if test="ename != '' and ename != null">
                 ename = #{ename}
             </if>
             <if test="age != '' and age != null">
                 and age = #{age}
             </if>
             <if test="sex != '' and sex != null">
                 and sex = #{sex}
             </if>
         </select>
        ```
        
    
1. **存在的问题：**当第一个条件不满足，但第二个条件满足，就会造成 where 关键字，后面直接跟上 and 关键字：
1. 解决方法：
    
    1. 方法一：在 where 关键字后加一个恒成立的条件
        
        ```XML
         <select id="getEmpListByMoreTJ" resultType="Emp">
             select * from t_emp where 1=1
             <if test="ename != '' and ename != null">
                 and ename = #{ename}
             </if>
             <if test="age != '' and age != null">
                 and age = #{age}
             </if>
             <if test="sex != '' and sex != null">
                 and sex = #{sex}
             </if>
         </select>
        ```
        
    
    1. 方法二：使用 where
    
# 2. **where**
1. **where 和 if 一般结合使用：**
    
    1. 若where标签中的if条件都不满足，则where标签没有任何功能，即不会添加where关键字
    
    1. 若where标签中的if条件满足，则where标签会自动添加where关键字，并将条件最前方多余的 and 或 or 去掉
    
1. 示例：
    
    ```XML
     <select id="getEmpListByMoreTJ2" resultType="Emp">
         select * from t_emp
         <where>
             <if test="ename != '' and ename != null">
                 ename = #{ename}
             </if>
             <if test="age != '' and age != null">
                 and age = #{age}
             </if>
             <if test="sex != '' and sex != null">
                 and sex = #{sex}
             </if>
         </where>
     </select>
    ```
    
1. where 标签不能去掉f放在条件最后多余的 and
    
    ```XML
     <if test="ename != '' and ename != null">
         ename = #{ename} and
     </if>
    ```
    
# 3. **trim**
1. **trim 用于去掉或添加标签中的内容**
1. 常用属性：
    
    1. `prefix`：在trim标签中的内容的**前面添加**某些内容
    
    1. `prefixOverrides`：在trim标签中的内容的**前面去掉**某些内容
    
    1. `suffix`：在trim标签中的内容的**后面添加**某些内容
    
    1. `suffixOverrides`：在trim标签中的内容的**后面去掉**某些内容
    
```XML
 <select id="getEmpListByMoreTJ" resultType="Emp">
     select * from t_emp
     <trim prefix="where" suffixOverrides="and">
         <if test="ename != '' and ename != null">
             ename = #{ename} and
         </if>
         <if test="age != '' and age != null">
             age = #{age} and
         </if>
         <if test="sex != '' and sex != null">
             sex = #{sex}
         </if>
     </trim>
 </select>
```
# 4. **choose、when、otherwise**
1. **choose、when、otherwise 相当于** `**if...else if..else**`
1. 只要有一个条件满足，则该条件后边的就不会生效
1. 如果 when 条件都不满足，则会去执行 otherwise
1. otherwise 最多有一个，when 最少有一个
```XML
 <select id="getEmpListByChoose" resultType="Emp">
     select <include refid="empColumns"></include> from t_emp
     <where>
         <choose>
             <when test="ename != '' and ename != null">
                 ename = #{ename}
             </when>
             <when test="age != '' and age != null">
                 age = #{age}
             </when>
             <when test="sex != '' and sex != null">
                 sex = #{sex}
             </when>
             <when test="email != '' and email != null">
                 email = #{email}
             </when>
         </choose>
     </where>
 </select>
```
# 5. **foreach**
1. 属性：
    
    1. `collection`：设置要循环的数组或集合
    
    1. `item`：表示集合或数组中的每一个数据
    
    1. `separator`：设置循环体之间的分隔符
    
    1. `open`：设置foreach标签中的内容的开始符
    
    1. `close`：设置foreach标签中的内容的结束符
    
1. 示例：
    
    1. 将要插入的对象以 List （emps）传入，在将里面的实体对象 emp 遍历出来，逐个插入
        
        ```XML
         <insert id="insertMoreEmp">
             insert into t_emp values
             <foreach collection="emps" item="emp" separator=",">
                 (null,#{emp.ename},#{emp.age},#{emp.sex},#{emp.email},null)
             </foreach>
         </insert>
        ```
        
    
    1. 将要删除的对象的 id 以 List （eids）传入，在将里面的每个 eid 遍历出来，逐个删除
        
        ```XML
         <delete id="deleteMoreByArray">
             delete from t_emp where eid in
             <foreach collection="eids" item="eid" separator="," open="(" close=")">
                 #{eid}
             </foreach>
         </delete>
        ```
        
        拼好的语句：
        
        ```SQL
         delete from t_emp where eid in (eid1,eid2,......)
        ```
        
    
# 6. **SQL 片段**
1. 开发中，搜索一般需要只搜出 一张表的**某几个字段**，不能使用 `*`
1. 可以将这些字段写在一个 sql 片段中
    
    ```XML
     <!--定义 sql 片段-->
     <sql id="empColumns">
         eid,ename,age,sex,did
     </sql>
     
     <!--在搜索语句中 直接引入-->
     select <include refid="empColumns"></include> from t_emp
    ```