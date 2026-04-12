1. 为什么要学习Shell编程
    
    1. Linux运维工程师在进行服务器集群管理时，需要编写Shell程序来进行服务器管理
    
    1. 对于JavaEE和Python程序员来说，工作的需要，你的老大会要求你编写一些Shell脚本进行程序或者是服务器的维护，比如编写一个定时备份数据库的脚本
    
    1. 对于大数据程序员来说，需要编写Shell程序来管理集群
    
1. **Shell是什么**
    
    Shell是一个命令行解释器，它为用户提供了一个向Linux内核发送请求以便运行程序的界面系统级程序，用户可以用Shell来启动、挂起、停止甚至是编写一些程序
    
    ![[IMG-20260404032001122.png|Untitled 109.png]]
    
1. **Shell脚本的执行方式**
    
    1. 脚本格式要求
        
        1. 脚本以#!/bin/bash开头
        
        1. 脚本需要有可执行权限
        
    
    1. 编写第一个Shell脚本
        
        创建一个Shell脚本，输出hello world!
        
        ```Plain
         [root@hadoop001 /]# mkdir /root/shcode
         [root@hadoop001 /]# cd /root/shcode/
         [root@hadoop001 shcode]# ls
         [root@hadoop001 shcode]# vim hello.sh
         [root@hadoop001 shcode]# cat hello.sh
         #!/bin/bash
         echo "hello world"
        ```
        
    
    1. ==**脚本的常用执行方式**==
        
        1. **方式1：输入脚本的绝对路径或相对路径**
            
            1. 首先要赋予helloworld.sh 脚本的+x权限
            
            1. 执行脚本
                
                ```Plain
                 [root@hadoop001 shcode]# ll
                 总用量 4
                 -rw-r--r--. 1 root root 31 7月   4 09:38 hello.sh
                 [root@hadoop001 shcode]# ./hello.sh
                 -bash: ./hello.sh: 权限不够
                 [root@hadoop001 shcode]# chmod u+x hello.sh
                 [root@hadoop001 shcode]# ll
                 总用量 4
                 -rwxr--r--. 1 root root 31 7月   4 09:38 hello.sh
                 [root@hadoop001 shcode]# ./hello.sh
                 hello world
                ```
                
            
        
        1. **方式2：sh+脚本**
            
            说明：即使此时脚本没有可执行权限，也可以执行
            
            ```Plain
             [root@hadoop001 shcode]# chmod u-x hello.sh
             [root@hadoop001 shcode]# ll
             总用量 4
             -rw-r--r--. 1 root root 31 7月   4 09:38 hello.sh
             [root@hadoop001 shcode]# sh hello.sh
             hello world
            ```