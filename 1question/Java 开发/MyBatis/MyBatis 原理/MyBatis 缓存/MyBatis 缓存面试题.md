# MyBatis 缓存面试题

<aside>
❓

</aside>

<aside>
❓ 只开启了一级缓存，下面代码示例中，开启了一个 SqlSession 会话，调用了一次查询，然后对数据进行了更改，又调用了一次查询，下列关于两次查询的说法，正确的是？

```java
// 打开一个 SqlSession
SqlSession sqlSession = factory.openSession(true);
StudentMapper studentMapper = sqlSession.getMapper(StudentMapper.class); 
// 根据 id=1 查询学生信息
System.out.println(studentMapper.getStudentById(1)); 
// 插入了一条学生数据，改变了数据库
System.out.println("增加了" + studentMapper.addStudent(buildStudent()) + "个学生"); 
// 根据 id=1 查询学生信息
System.out.println(studentMapper.getStudentById(1)); 
sqlSession.close();
```

- 答案：第一次从数据库查询到的数据，第二次从数据库查询的数据
- 解答：第一次从数据库查询后，后续更新（包括增删改）数据库中的数据后，这条 SQL 语句的缓存失效了，后续查询需要重新从数据库获取数据
</aside>

<aside>
❓ 当开启了一级缓存，下面的代码中，开启了两个 SqlSession，请写出最后的查询结果

```java
SqlSession sqlSession1 = factory.openSession(true); 
SqlSession sqlSession2 = factory.openSession(true); 
StudentMapper studentMapper = sqlSession1.getMapper(StudentMapper.class); 
StudentMapper studentMapper2 = sqlSession2.getMapper(StudentMapper.class); 
studentMapper2.updateStudentName("B",1);             // **第二个 SqlSession 更新了一次学生 A 的姓名**
System.out.println(studentMapper.getStudentById(1)); 
System.out.println(studentMapper2.getStudentById(1));
```

- 答案：

    ```java
    A
    B
    ```

- 解答：**只开启一级缓存的情况下，SqlSession 级别是不共享的**。代码示例中，分别创建了两个 SqlSession，在第一个 SqlSession 中查询学生 A 的姓名，第二个 SqlSession 中修改了学生 A 的姓名为 B，**SqlSession2 更新了数据后，不会影响 SqlSession1**，所以 SqlSession1 查到的数据还是 A
</aside>

<aside>
❓ 开启了一级和二级缓存，通过三个SqlSession 查询和更新 学生张三的姓名，判断最后的输出结果是什么？

```java
SqlSession sqlSession1 = factory.openSession(true); 
SqlSession sqlSession2 = factory.openSession(true); 
SqlSession sqlSession3 = factory.openSession(true); 

StudentMapper studentMapper = sqlSession1.getMapper(StudentMapper.class); 
StudentMapper studentMapper2 = sqlSession2.getMapper(StudentMapper.class); 
StudentMapper studentMapper3 = sqlSession3.getMapper(StudentMapper.class); 

System.out.println("studentMapper读取数据: " + studentMapper.getStudentById(1)); 
sqlSession1.commit(); 
System.out.println("studentMapper2读取数据: " + studentMapper2.getStudentById(1)); 
studentMapper3.updateStudentName("李四",1); 
sqlSession3.commit(); 
System.out.println("studentMapper2读取数据: " + studentMapper2.getStudentById(1));
```

- 答案：

    ```java
    张三
    张三
    李四
    ```

- 解答：三个 SqlSession 是共享 MyBatis 缓存，SqlSession2 更新数据后，MyBatis 的 namespace 缓存（StudentMapper） 就失效了，SqlSession2 最后是从数据库查询到的数据
</aside>

<aside>
❓

只开启了一级缓存，下面的代码调用了三次查询操作 getStudentById，请判断，下列说法正确的是？

```java
// 打开一个 SqlSession
SqlSession sqlSession = factory.openSession(true);
StudentMapper studentMapper = sqlSession.getMapper(StudentMapper.class); 
// 根据 id=1 查询学生信息
System.out.println(studentMapper.getStudentById(1)); 
// 根据 id=1 查询学生信息
System.out.println(studentMapper.getStudentById(1)); 
// 根据 id=1 查询学生信息
System.out.println(studentMapper.getStudentById(1));
```

- 答案：第一次从数据库查询到的数据，第二次和第二次从 MyBatis 一级缓存查询的数据
- 解答：第一次从数据库查询后，后续查询走 MyBatis 一级缓存
</aside>