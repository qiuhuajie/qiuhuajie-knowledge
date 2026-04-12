- [[#1. 消息队列 介绍]]
- [[#2. 基于List结构模拟消息队列]]
- [[#3. 基于PubSub的消息队列]]
- [[#4. 基于Stream的消息队列 ✅]]
# 1. 消息队列 介绍
（Message Queue）
1. 字面意思就是存放消息的队列，类比：**快递柜，**解除耦合，提高效率
1. 最简单的消息队列模型包括3个角色：
    
    1. 消息队列：存储和管理消息，也被称为消息代理（Message Broker）
    
    1. 生产者：发送消息到消息队列
    
    1. 消费者：从消息队列获取消息并处理消息
        
        ![[Attachment/1question/中间件/Redis/Redis 实战/4 优惠券秒杀/异步秒杀/Redis 消息队列实现异步秒杀/IMG-20260405035438407.png|Untitled 571.png]]
        
    
1. **Redis 提供了三种不同的方式来实现消息队列：**
    
    1. `List` 结构：基于List结构模拟消息队列
    
    1. `PubSub`：基本的点对点消息模型
    
    1. `Stream`：比较完善的消息队列模型
    
# 2. **基于**`**List**`**结构模拟消息队列**
1. Redis的list数据结构是一个双向链表，很容易模拟出队列效果
1. 队列是入口和出口不在一边，因此我们可以利用：`LPUSH` 结合 `RPOP`、或者 `RPUSH` 结合 `LPOP` 来实现
    
    > 注意：
    > 
    > 1. 当队列中没有消息时RPOP或LPOP操作会返回null，并不像JVM的阻塞队列那样会阻塞并等待消息
    > 
    > 1. 因此这里如果要实现阻塞式队列，在取出消息时应该使用`BRPOP`或者`BLPOP`
    
    ![[IMG-20260405035500909.png|Untitled 1 423.png]]
    
1. 优点：
    
    1. 利用Redis存储，不受限于JVM内存上限
    
    1. 基于Redis的持久化机制，数据安全性有保证
    
    1. 可以满足消息有序性
    
1. ==缺点：==
    
    1. 无法避免消息丢失：pop 是 remove and get，拿到了没处理，自己挂了，还给从队列里删除了
    
    1. 只支持单消费者
    
# 3. **基于**`**PubSub**`**的消息队列**
1. PubSub（发布订阅）是Redis2.0版本引入的消息传递模型
1. 消费者可以订阅一个或多个channel，生产者向对应channel发送消息后，所有订阅者都能收到相关消息
1. 相关命令：
    
    1. `SUBSCRIBE channel [channel]` ：订阅一个或多个频道
    
    1. `PUBLISH channel msg` ：向一个频道发送消息
    
    1. `PSUBSCRIBE pattern[pattern]` ：订阅与pattern格式匹配的所有频道（通配符匹配）
    
    ![[IMG-20260405035509610.png|Untitled 2 344.png]]
    
1. 优点：
    
    1. 采用发布订阅模型
    
    1. 支持多生产、多消费
    
1. ==缺点：==
    
    1. 不支持数据持久化
    
    1. 无法避免消息丢失，不可靠
    
    1. 消息堆积有上限，超出时数据丢失
    
# 4. **基于**`**Stream**`**的消息队列** ✅
1. Stream 是 Redis 5.0 引入的一种新**数据类型**（即可以持久化数据），可以实现一个功能非常完善的消息队列
1. ==**发送消息：**====`**XADD**`==
    
    ```Bash
    127.0.0.1:6379> help xadd2
      XADD key [NOMKSTREAM] [MAXLEN|MINID [=|~] threshold [LIMIT count]] *|ID field value [field value ...]4
      summary: Appends a new entry to a stream5
      since: 5.0.06
      group: stream
    ```
    
    - 语法格式：
        
        ![[IMG-20260405035517528.png|Untitled 3 260.png]]
        
    
    - 示例：创建名为 users 的队列，并向其中发送一个消息，内容是：**{name=jack,age=21}**，并且使用Redis**自动生成ID**
        
        ```Bash
        127.0.0.1:6379> XADD users * name jack age 212
        "1651845988438-0"
        ```
        
    
1. ==**读取消息：**====`**XREAD**`== ==**单消费者模式**==
    
    ```Bash
    127.0.0.1:6379> help XREAD2
    	XREAD [COUNT count] [BLOCK milliseconds] STREAMS key [key ...] ID [ID ...]4
      summary: Return never seen elements in multiple streams, with IDs greater than the ones reported by the caller for each stream. Can block.5
      since: 5.0.06
      group: stream
    ```
    
    - 语法格式：
        
        ![[IMG-20260405035525082.png|Untitled 4 200.png]]
        
    
    - 示例：使用XREAD读取 users 队列的第一个消息
        
        ```Bash
        # 读取队列中的第一条消息
        127.0.0.1:6379> XREAD COUNT 1 STREAMS users 0
        1) 1) "users"
           2) 1) 1) "1651845988438-0"
                 2) 1) "name"
                    2) "jack"
                    3) "age"
                    4) "21"
                    
        # 读取一次之后，可以重复读取
        127.0.0.1:6379> XREAD COUNT 1 STREAMS users 0
        1) 1) "users"
           2) 1) 1) "1651845988438-0"
                 2) 1) "name"
                    2) "jack"
                    3) "age"
                    4) "21"
                    
        # 但如果使用 $ 读的时候，会读不到已经读过的数据
        127.0.0.1:6379> XREAD COUNT 1 STREAMS users $
        (nil)
        
        # 阻塞式读取：0 代表一直等待
        127.0.0.1:6379> XREAD COUNT 1 BLOCK 0 STREAMS users $
        
        # 再开一个窗口，发送消息 XADD users * name qhj age 22
        # 阻塞被唤醒，读取到数据
        127.0.0.1:6379> XREAD COUNT 1 BLOCK 0 STREAMS users $
        1) 1) "users"
           2) 1) 1) "1651846567942-0"
                 2) 1) "name"
                    2) "qhj"
                    3) "age"
                    4) "22"
        (17.97s)
        ```
        
    
    - 注意：`XREAD` **存在漏读消息**的问题：
        
        1. 当我们指定起始ID为$时，代表读取最新的消息
        
        1. 如果**在我们处理一条消息的过程中，又有超过1条以上的消息到达队列，则下次获取时也只能获取到最新的一条**
        
        1. 会出现漏读消息的问题
            
            ```Bash
            # 阻塞式读取：0 代表一直等待
            127.0.0.1:6379> XREAD COUNT 1 BLOCK 0 STREAMS users $
            
            # 再开一个窗口2，发送消息 XADD users * name qhj age 22
            # 阻塞被唤醒，读取到数据
            127.0.0.1:6379> XREAD COUNT 1 BLOCK 0 STREAMS users $
            1) 1) "users"
               2) 1) 1) "1651846567942-0"
                     2) 1) "name"
                        2) "qhj"
                        3) "age"
                        4) "22"
            (17.97s)
            
            # 在窗口2，发送消息 XADD users * name cool age 23
            # 在窗口2，发送消息 XADD users * name zhangsan age 25
            
            # 在窗口1，阻塞式读取：
            127.0.0.1:6379> XREAD COUNT 1 BLOCK 0 STREAMS users $
            
            # 在窗口2，发送消息 XADD users * name lisi age 24
            
            # ⭐在窗口1，阻塞被唤醒，读取到数据，且只能读到最新的一条，中间的消息漏读了
            127.0.0.1:6379> XREAD COUNT 1 BLOCK 0 STREAMS users $
            1) 1) "users"
               2) 1) 1) "1651846567942-5"
                     2) 1) "name"
                        2) "lisi"
                        3) "age"
                        4) "24"
            ```
            
        
    
    - STREAM类型消息队列的`XREAD`命令特点：
        
        1. 消息可回溯
        
        1. 一个消息可以被多个消费者读取
        
        1. 可以阻塞读取
        
        1. 有消息漏读的风险
        
    
1. ==**读取消息：**====`**XREADGROUP**`== ==**消费者组模式**== ==✔==
    
    1. 引入一个新的概念：
        
        **消费者组**（Consumer Group）：将多个消费者划分到一个组中，监听同一个队列
        
    
    1. 消费者组具备的特点
        
        - **消息分流：**
            
            1. 队列中的消息会分发到组，而组内的消费者之间是竞争关系
            
            1. 每个消息被同一组内的消费者竞争得到后，只会被消费一次，而不是重复消费，从而加快消息处理的速度
            
        
        - **消息标识：**
            
            1. 消费者组会维护一个标示，记录最后一个被处理的消息（书签，看到哪里了）
            
            1. 哪怕消费者宕机重启，还会从标示之后读取消息。确保每一个消息都会被消费，这样可以解决消息漏读的问题
            
        
        - **消息确认：**
            
            1. 消费者获取消息后，消息处于`pending` 状态，并存入一个`pending-list`
            
            1. 当处理完成后需要通过`XACK`来确认消息，标记消息为已处理，才会从pending-list移除
            
            1. 解决消息丢失问题：拿到了没消费，却把消息pop删除了的情况
            
        
    
    1. 操作消费组的命令：
        
        1. 创建消费组：
            
            ![[IMG-20260405035525149.png|Untitled 5 163.png]]
            
            - `key`：队列名称
            
            - `groupName`：消费者组名称
            
            - `ID`：起始ID标示，`$` 代表队列中最后一个消息，`0` 则代表队列中第一个消息
            
            - `MKSTREAM`：队列不存在时自动创建队列
                
                ```Bash
                # 为users队列创建一个组 group012
                127.0.0.1:6379> XGROUP CREATE users group01 03
                OK
                ```
                
            
        
        1. 从消费者组读取消息：
            
            ![[IMG-20260405035530781.png|Untitled 6 133.png]]
            
            - `group`：消费组名称
            
            - `consumer`：消费者名称，如果消费者不存在，会自动创建一个消费者
            
            - `count`：本次查询的最大数量
            
            - `BLOCK milliseconds`：当没有消息时最长等待时间
            
            - `NOACK`：无需手动ACK，获取到消息后自动确认
            
            - `STREAMS key`：指定队列名称
            
            - `ID`：获取消息的起始ID：
                
                - `>`：
                    
                    - 正常情况下的读取从队列下一个未消费的消息开始
                    
                    - 相当于从书签后紧接的一个读
                    
                
                - `number`：
                    
                    - 如果出现异常，拿到消息却未确认，就需要去`pending-list`中读取异常处理的消息
                    
                    - 根据指定`number`从`pending-list`（回收站）中获取已消费但未确认的消息，例如`0`，是从`pending-list`中的第一个消息开始
                    
                
                > 示例：
                
                消费消息
                
                ```Bash
                # 使用消费者1读取消息
                127.0.0.1:6379> XREADGROUP GROUP group01 comsumer01 COUNT 1 BLOCK 2000 STREAMS users >
                1) 1) "users"
                   2) 1) 1) "1651845988438-0"
                         2) 1) "name"
                            2) "jack"
                            3) "age"
                            4) "21"
                
                # 使用消费者2读取消息
                127.0.0.1:6379> XREADGROUP GROUP group01 comsumer02 COUNT 1 BLOCK 2000 STREAMS users >
                1) 1) "users"
                   2) 1) 1) "1651905918792-0"
                         2) 1) "name"
                            2) "qhj"
                            3) "age"
                            4) "22"
                            
                # 使用消费者1读取消息，可以看到组内消费者是竞争状态，每个信息只会被同一个组的成员消费一次
                127.0.0.1:6379> XREADGROUP GROUP group01 comsumer01 COUNT 1 BLOCK 2000 STREAMS users >
                1) 1) "users"
                   2) 1) 1) "1651905931671-0"
                         2) 1) "name"
                            2) "zhangsan"
                            3) "age"
                            4) "23"
                ```
                
                确认消息
                
                ```Bash
                127.0.0.1:6379> XACK users group01 1651845988438-0 1651905918792-0 1651905931671-02
                (integer) 3
                ```
                
                查看 `pending-list` 中的消息
                
                ```Bash
                # 由于之前读到的三个消息都被确认过了，所以先在pending-list中没有消息
                127.0.0.1:6379> XPENDING users group01 - + 10
                (empty array)
                
                # 重新读取一个消息
                127.0.0.1:6379> XREADGROUP GROUP group01 comsumer01 COUNT 1 BLOCK 2000 STREAMS users >
                1) 1) "users"
                   2) 1) 1) "1651905943649-0"
                         2) 1) "name"
                            2) "lisi"
                            3) "age"
                            4) "23"
                            
                # 再次查看pending-list中的消息
                127.0.0.1:6379> XPENDING users group01 - + 10
                1) 1) "1651905943649-0"
                   2) "comsumer01"
                   3) (integer) 2943
                   4) (integer) 1
                   
                # 也可以读取pending-list中的消息
                127.0.0.1:6379> XREADGROUP GROUP group01 comsumer01 COUNT 1 BLOCK 2000 STREAMS users 0
                1) 1) "users"
                   2) 1) 1) "1651905943649-0"
                         2) 1) "name"
                            2) "lisi"
                            3) "age"
                            4) "23"
                            
                # 将pending-list中消息确认
                127.0.0.1:6379> XACK users group01 1651905943649-0
                (integer) 1
                
                # 再次查看，pending-list中为空
                127.0.0.1:6379> XPENDING users group01 - + 10
                (empty array)
                ```
                
            
        
        1. 其他命令
            
            ![[IMG-20260405035534042.png|Untitled 7 103.png]]
            
        
    
1. redis 的三种消息队列的比较
    
    ![[IMG-20260405035534072.png|Untitled 8 82.png]]