# 1. Shell 的变量的介绍
Linux Shell中的变量分为，系统变量和用户自定义变量
1. 系统变量：
    
    $HOME、 $PWD、 $SHELL、 $USER，比如： echo $HOME 等
    
    显示当前shell中所有变量： set
    
1. 自定义变量：
    
    基本语法
    
    1. 定义变量：变量=值（无空格）
    
    1. 撤销变量： unset 变量
    
    1. 声明静态变量： readonly变量，注意：不能unset
        
        ```Bash
         #!/bin/bash
         \#案例一：定义变量A
         A=100
         \#输出变量需要加上$
         echo $A
         echo A=$A
         echo "A=$A"
         \#案例二：撤销变量A
         unset A
         echo A=$A
         \#案例三：声明静态变量B=2，不能unset
         readonly B=2
         echo B=$B
        ```
        
        ```Shell
         [root@hadoop001 shcode]# sh var.sh
         100
         A=100
         A=100
         A=
         B=2
        ```
        
    
# 2. **shell 变量的定义**
1. 定义变量的规则
    
    1. 变量名称可以由字母、数字和下划线组成，但是不能以数字开头
    
    1. ==等号两侧不能有空格==
    
    1. 变量名称一般习惯为大写
    
1. 将命令的返回值赋给变量
    
    1. A=`ls -la` ==反引号括起来的按照命令运行，并把结果返回给变量A==
    
    1. A=$(ls -la) 等价于反引号
        
        ```Bash
         \#将指令返回的结果赋予变量
         C=`date`
         D=$(date)
         echo C=$C
         echo D=$D
        ```
        
        ```Bash
         [root@hadoop001 shcode]# sh var.sh
         C=2021年 07月 04日 星期日 10:12:11 CST
         D=2021年 07月 04日 星期日 10:12:11 CST
        ```
        
    
# 3. **设置环境变量**
1. 基本语法
    
    1. `export 变量名=变量值` （功能描述：将shell变量输出为环境变量(全局变量)）
    
    1. `source 配置文件` （功能描述：让修改后的配置信息立即生效）
    
    1. `echo $变量名` （功能描述：查询环境变量的值）
        
        ![[IMG-20260404032001147.png|Untitled 110.png]]
        
    
1. 应用实例：
    
    1. 在/etc/profile文件中定义TOMCAT_HOME环境变量
        
        ```Bash
         [root@hadoop001 opt]# vim /etc/profile
        ```
        
        ```Bash
         \#定义一个环境变量
         export TOMCAT_HOME=/opt/tomcat
        ```
        
    
    1. 查看环境变量TOMCAT_HOME的值
        
        ```Bash
         //标准输出刚刚自定义的环境变量
         [root@hadoop001 opt]# echo $TOMCAT_HOME
         
         [root@hadoop001 opt]# source /etc/profile //⭐
         [root@hadoop001 opt]# echo $TOMCAT_HOME
         /opt/tomcat
        ```
        
    
    1. 在另外一个shell程序中使用 TOMCAT_HOME
        
        ```Bash
         \#使用定义的环境变量TOMCAT_HOME
         echo tomcat_home=$TOMCAT_HOME
        ```
        
        ```Bash
         [root@hadoop001 shcode]# sh var.sh
         tomcat_home=/opt/tomcat
        ```
        
        ```Bash
         :<<!
         多行注释
         多行注释
         !
        ```
        
    
# 4. **位置参数变量**（函数形参）
1. 介绍：
    
    1. 当我们执行一个shell脚本时，如果**希望获取到命令行的参数信息**，就可以使用到位置参数变量
    
    1. 比如 `./myshell.sh 100 200` , 这个就是一个执行shell的命令行，可以在myshell 脚本中获取到参数信息
    
1. 基本语法：
    
    1. `$n` （功能描述： n为数字， $0代表命令本身， $1-$9代表第一到第九个参数，十以上的参数，十以上的参数需要用大括号包含，如${10}）
    
    1. `$*` （功能描述：这个变量代表命令行中所有的参数， **$*把所有的参数看成一个整体**）
    
    1. `$@`（功能描述：这个变量也代表命令行中所有的参数， 不过**$@把每个参数区分待**）
    
    1. `$#`（功能描述：这个变量代表命令行中**所有参数的个数**）
    
1. 应用实例：
    
    ```Bash
     #!/bin/bash
     \#依次输出参数
     echo "$0 $1 $2"
     \#所有传入的参数（整体）
     echo "$*"
     \#所有传入的参数（分开）
     echo "$@"
     \#传入参数的个数
     echo "$#"
    ```
    
    ```Bash
     [root@hadoop001 shcode]# sh myshell.sh 100 200 300
     myshell.sh 100 200  //传入的三个参数
     100 200 300
     100 200 300
     3
    ```
    
# 5. **预定义变量**
1. 基本介绍：
    
    就是shell设计者事先**已经定义好的变量**，可以直接在shell脚本中使用
    
1. 基本语法：
    
    1. `$$`：功能描述：当前进程的进程号（PID）
    
    1. `$!`：功能描述：后台运行的最后一个进程的进程号（PID）
    
    1. `$?`：功能描述：最后一次执行的命令的返回状态。如果这个变量的值为0，证明上一个命令正确执行；如果这个变量的值为非0（具体是哪个数，由命令自己来决定），则证明上一个命令执行不正确了
    
1. 应用实例：
    
    在一个shell脚本中简单使用一下预定义变量
    
    ```Bash
     #!/bin/bash
     echo "当前执行的进程号=$$"
     \#以后台的方式运行一个脚本，并获取它的进程号
     /root/shcode/myshell.sh &
     echo "最后一个后台方式运行的进程ID=$!"
     echo "执行的结果是=$?"
    ```
    
    ```Bash
     [root@hadoop001 shcode]# sh prVar.sh
     当前执行的进程号=17613
     最后一个后台方式运行的进程ID=17614
     执行的结果是=0
    ```