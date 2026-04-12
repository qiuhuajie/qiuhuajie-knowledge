- [[#1. 介绍]]
- [[#2. AOF 去重]]
- [[#3. 使用示例]]
![[IMG-20260405035438369.png|Untitled 440.png]]
**AOF 与 RDB 的比较⭐**
- 如果不追求数据的极致完整性，可以容忍短时间内的数据丢失，推荐使用 RDB，恢复速度快
- 但数据完整性要求很高，推荐使用 AOF
# 1. 介绍
1. **AOF全称为 Append Only File (追加文件)。Redis处理的每一个写命令都会记录在AOF文件，可以看做是命令日志文件**
    
    ![[IMG-20260405035454656.png|Untitled 1 326.png]]
    
1. 和 MySQL 的 redo.log 很像[[redo log（操作备份）]][[redo log（操作备份）]][[redo log（操作备份）]]
1. **AOF 默认是关闭的**
# 2. AOF 去重
1. **普通 AOF 的缺陷：**
    
    - 因为是记录命令，AOF 文件会比 RDB 文件大的多
    
    - 而且 AOF **会记录对同一个 key 的多次写操作，但只有最后一次写操作才有意义**
    
1. AOF 去重操作
    
    1. **主动去重**
        
        - 通过执行 **`bgrewriteaof`** 命令，可以让 AOF 文件执行重写功能，用最少的命令达到相同效果
            
            ![[IMG-20260405035508736.png|Untitled 2 265.png]]
            
        
        - **`bgrewriteaof`** 命令也是在后台开启一个异步子进程来执行的
        
    
    1. **在触发阈值时自动去重写 AOF 文件**
        
        - 阈值也可以在 redis.conf 中配置
            
            ![[IMG-20260405035516317.png|Untitled 3 199.png]]
            
        
    
# 3. 使用示例
1. 配置文件 redis.conf
    
    1. 开启AOF
        
        ![[IMG-20260405035516371.png|Untitled 4 155.png]]
        
    
    1. 配置 AOF的命令记录的频率**（刷盘策略）**
        
        ![[IMG-20260405035524073.png|Untitled 5 127.png]]
        
    
    1. 三种频率配置对比**（一般使用 `everysec` 作为刷盘策略）**
        
        ![[IMG-20260405035530148.png|Untitled 6 104.png]]
        
    
1. 查看 AOF 文件
    
    ![[IMG-20260405035533825.png|Untitled 7 84.png]]
    
1. 停机
    
    ![[IMG-20260405035533859.png|Untitled 8 67.png]]
    
1. 重启：可以看到加载了 只允许追加的 AOF 文件
    
    ![[IMG-20260405035536899.png|Untitled 9 59.png]]