1. 查看当前znode中所包含的内容
    
    ```Plain
     [zk: localhost:2181(CONNECTED) 1] ls /
     [zookeeper]
    ```
    
1. 查看当前节点详细数据
    
    ```Bash
     [zk: localhost:2181(CONNECTED) 2] ls -s /
     [zookeeper]cZxid = 0x0
     ctime = Thu Jan 01 08:00:00 CST 1970
     mZxid = 0x0
     mtime = Thu Jan 01 08:00:00 CST 1970
     pZxid = 0x0
     cversion = -1
     dataVersion = 0
     aclVersion = 0
     ephemeralOwner = 0x0
     dataLength = 0
     numChildren = 1
    ```
    
    节点信息描述：
    
    1. `czxid`： 创建节点的事务 zxid
        
        每次修改 ZooKeeper 状态都会产生一个 ZooKeeper 事务 ID。事务ID 是 ZooKeeper 中所有修改总的次序。每次修改都有唯一的 zxid，如果 zxid1 小于 zxid2，那么 zxid1 在 zxid2 之前发生
        
    
    1. ctime： znode 被创建的毫秒数（从 1970 年开始）
    
    1. mzxid： znode 最后更新的事务 zxid
    
    1. mtime： znode 最后修改的毫秒数（从 1970 年开始）
    
    1. pZxid： znode 最后更新的子节点 zxid
    
    1. cversion： znode 子节点变化号， znode 子节点修改次数
    
    1. `dataversion`： znode 数据变化号
    
    1. aclVersion： znode 访问控制列表的变化号
    
    1. ephemeralOwner： 如果是临时节点，这个是 znode 拥有者的session id，如果不是临时节点则是 0
    
    1. `dataLength`： znode 的数据长度
    
    1. `numChildren`： znode 子节点数量