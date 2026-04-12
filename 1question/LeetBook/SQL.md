- [[#📑1141. 查询近30天活跃用户数]]
- [[#📑查询每个用户的最后一次登录记录]]
- [[#📑学号、姓名、科目、成绩4个字段，查找所有科目总成绩大于 10 的学生的学号、姓名和总成绩]]
## **📑1141. 查询近30天活跃用户数**
1. 问题描述：
    
1. 示例：
    
    ```Plain
    输入：
    Activity table:
    +---------+------------+---------------+---------------+
    | user_id | session_id | activity_date | activity_type |
    +---------+------------+---------------+---------------+
    | 1       | 1          | 2019-07-20    | open_session  |
    | 1       | 1          | 2019-07-20    | scroll_down   |
    | 1       | 1          | 2019-07-20    | end_session   |
    | 2       | 4          | 2019-07-20    | open_session  |
    | 2       | 4          | 2019-07-21    | send_message  |
    | 2       | 4          | 2019-07-21    | end_session   |
    | 3       | 2          | 2019-07-21    | open_session  |
    | 3       | 2          | 2019-07-21    | send_message  |
    | 3       | 2          | 2019-07-21    | end_session   |
    | 4       | 3          | 2019-06-25    | open_session  |
    | 4       | 3          | 2019-06-25    | end_session   |
    +---------+------------+---------------+---------------+
    输出：
    +------------+--------------+
    | day        | active_users |
    +------------+--------------+
    | 2019-07-20 | 2            |
    | 2019-07-21 | 2            |
    +------------+--------------+
    解释：注意非活跃用户的记录不需要展示。
    ```
    
1. 代码：
    
    ```SQL
    select activity_date as day, count(DISTINCT(user_id)) as active_users 
    from Activity 
    where activity_date BETWEEN date( '2019-06-28' ) AND date( '2019-07-27' )
    GROUP BY activity_date;
    ```
    
## **📑**查询每个用户的最后一次登录记录
1. 问题描述：
    
1. 示例：
    
1. 代码：
    
    [[2.3 DQL]][[2.3 DQL]][[2.3 DQL]]
    
    ```SQL
    SELECT user_id, MAX(login_time) AS last_login_time
    FROM login_records
    GROUP BY user_id;
    ```
    
## **📑**学号、姓名、科目、成绩4个字段，查找所有科目总成绩大于 10 的学生的学号、姓名和总成绩
1. 问题描述：
    
1. 示例：
    
1. 代码：
    
    [[2.3 DQL]]
    
    ```SQL
    SELECT 学号, 姓名, SUM(成绩) AS 总成绩
    FROM scores
    GROUP BY 学号, 姓名
    HAVING SUM(成绩) > 10;
    ```