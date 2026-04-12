- [[#1. 介绍]]
- [[#2. 示例]]
# 1. **介绍**
1. **单节点 Nginx 存在的问题**
    
    1. 问题 1：代理服务器需要在用户和目标服务器之间中转数据，造成**网络单点瓶颈**，当流量大的时候，网关服务的带宽不够大，导致整个服务被限制
    
    1. 问题 2：nginx 存在单点故障，当唯一的 nginx 服务器宕机后，对外界则不能提供服务
    
1. 解决：
    
    - 设多台nginx代理服务器，以及多组高可用的业务服务器集群，做负载均衡
    
    - 但是，由于外网所有的访问都要打到 nginx 代理服务器上，如何保证对外总保持唯一的 IP 来提供服务
    
1. **如何实现❓**
    
    1. 设想的解决办法：
        
        1. 若此时有两台 nginx 服务器（192.168.10.191、192.168.10.192），当 191 宕机后，外网访问服务使用的 IP 还是192.168.10.191，此时若想让 192 顶替 191 提供服务
        
        1. **简单的方法就是直接将 192 的 IP 修改为192.168.10.192，但是这样存在很大问题** 🚫
            
            1. 如果突然 191 又恢复了，此时同一个局域网中存在两个相同的 IP ，显然是不可以的
            
            1. 故不能简单的使用 IP 复制的方法来解决 Nginx 高可用的场景
            
        
    
    1. **解决方案** ✅
        
        - ==**配合 keepalived 软件 + VIP（虚拟 IP）漂移**==
        
        ![[Attachment/1question/中间件/Nginx/IMG-20260405035438280.png|Untitled 68.png]]
        
    
# 2. **示例**
1. 新建一个 nginx 的备用机 192.168.10.190 nginx_backup
1. 191 和 190 都安装 ==**keepalived**==
    
    ```Plain
     [root@nginx ~]# yum install keepalived
    ```
    
    ```Plain
     [root@nginx_backup ~]# yum install keepalived
    ```
    
1. 修改 191 的 keepalived 配置文件
    
    ```Plain
     ! Configuration File for keepalived
     global_defs {
         router_id lb191     # 路由id 随便取
     }
     vrrp_instance qhjqhj {
         state MASTER        # 表示 191 是主节点
         interface ens32     # 网卡名字
         virtual_router_id 51
         priority 100        # 会根据 priority 选举当前的主节点
         advert_int 1
         authentication {    # 竞争同一个虚拟IP的节点要处在同一个授权组
             auth_type PASS
             auth_pass 1111
         }
         virtual_ipaddress {
             192.168.10.200  # ⭐配置竞争哪个虚拟IP
         }
     }
    ```
    
1. 修改 190 的 keepalived 配置文件
    
    ```Plain
     ! Configuration File for keepalived
     global_defs {
         router_id lb190
     }
     vrrp_instance qhjqhj {
         state BACKUP    # 表示 190 是备用节点
         interface ens32
         virtual_router_id 51
         priority 50
         advert_int 1
         authentication {
             auth_type PASS
             auth_pass 1111
         }
         virtual_ipaddress {
             192.168.10.200
         }
     }
    ```
    
1. 各自启动 keepalived 服务
1. 此时观察
    
    1. 虚拟 IP 的位置
    
    1. 由于191 当前为 master，故虚拟 IP 在 191 上
    
    ![[IMG-20260405035448697.png|Untitled 1 39.png]]
    
    ![[IMG-20260405035506604.png|Untitled 2 29.png]]
    
1. 测试：
    
    1. 访问 [http://192.168.10.200/](http://192.168.10.200/)
    
    1. 成功访问
    
1. ==**测试两个主机对 虚拟 IP 的竞争过程**==
    
    1. 在主机的 cmd 中 ping 虚拟 IP
        
        ```Plain
         C:\Users\APandaThief>ping 192.168.10.200
        ```
        
        ```Plain
         C:\Users\APandaThief>ping 192.168.10.200 -t                                                                                                                                                 正在 Ping 192.168.10.200 具有 32 字节的数据:
        来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
        来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64来自 192.168.10.200 的回复: 字节=32 时间=1ms TTL=64
        来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
        ```
        
    
    1. **此时将 191 关掉**
        
        ```Plain
         [root@nginx keepalived]# init 0
        ```
        
    
    1. 此时的 cmd 中
        
        ```Plain
         C:\Users\APandaThief>ping 192.168.10.200 -t                                                                                                                                                  正在 Ping 192.168.10.200 具有 32 字节的数据:
        来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
        来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
        来自 192.168.10.200 的回复: 字节=32 时间=1ms TTL=64
        来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
        
         请求超时。                                           # ⭐ 可以看到中断了以下，之后又又恢复了
         来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
         来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
         来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
         来自 192.168.10.200 的回复: 字节=32 时间=1ms TTL=64
         来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
         来自 192.168.10.200 的回复: 字节=32 时间<1ms TTL=64
        ```
        
    
    1. 现在再看 虚拟 IP 的位置：==**已经挪到了备选机 190 上**==
        
        ![[IMG-20260405035513576.png|Untitled 3 23.png]]