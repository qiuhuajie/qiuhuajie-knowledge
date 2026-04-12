1. 在 hadoop102 的/home/cool/bin 目录下创建脚本
    
    ```Plain
     [cool@hadoop102 zookeeper-3.5.7]$ cd /home/cool/bin/
     [cool@hadoop102 bin]$ vim zk.sh
    ```
    
1. 在脚本中编写如下内容
    
    ```Shell
     #!/bin/bash
     case $1 in
     "start"){
         for i in hadoop102 hadoop103 hadoop104
         do
             echo ---------- zookeeper $i 启动 ------------
             ssh $i "/opt/module/zookeeper-3.5.7/bin/zkServer.sh
     start"
     done
     };;
     "stop"){
         for i in hadoop102 hadoop103 hadoop104
         do
             echo ---------- zookeeper $i 停止 ------------
             ssh $i "/opt/module/zookeeper-3.5.7/bin/zkServer.sh
     stop"
     done
     };;
     "status"){
         for i in hadoop102 hadoop103 hadoop104
         do
             echo ---------- zookeeper $i 状态 ------------
             ssh $i "/opt/module/zookeeper-3.5.7/bin/zkServer.sh
     status"
     done
     };;
     esac
    ```
    
1. 增加脚本执行权限
    
    ```Plain
     [cool@hadoop102 bin]$ chmod u+x zk.sh
    ```
    
1. Zookeeper 集群启动脚本
    
    ```Plain
     [cool@hadoop102 zookeeper-3.5.7]$ zk.sh start
     ---------- zookeeper hadoop102 启动 ------------
     ZooKeeper JMX enabled by default
     Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
     Starting zookeeper ... STARTED
     ---------- zookeeper hadoop103 启动 ------------
     ZooKeeper JMX enabled by default
     Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
     Starting zookeeper ... STARTED
     ---------- zookeeper hadoop104 启动 ------------
     ZooKeeper JMX enabled by default
     Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
     Starting zookeeper ... STARTED
    ```
    
1. Zookeeper 集群停止脚本
    
    ```Plain
     [cool@hadoop102 bin]$ zk.sh stop
     ---------- zookeeper hadoop102 停止 ------------
     ZooKeeper JMX enabled by default
     Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
     Stopping zookeeper ... STOPPED
     ---------- zookeeper hadoop103 停止 ------------
     ZooKeeper JMX enabled by default
     Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
     Stopping zookeeper ... STOPPED
     ---------- zookeeper hadoop104 停止 ------------
     ZooKeeper JMX enabled by default
     Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
     Stopping zookeeper ... STOPPED
    ```