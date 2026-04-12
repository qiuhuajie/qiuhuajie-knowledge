- [[#1. 系统设置]]
- [[#2. 安装 nginx]]
- [[#3. systemd 管理 nginx]]
- [[#4. 测试]]
# 1. **系统设置**
1. 防火墙
    
    ```Plain
     systemctl stop firewalld
     systemctl disable firewalld
     systemctl status firewalld
    ```
    
1. SELinux
    
    ```Plain
     # 永久关闭
     sed -i 's/enforcing/disabled/' /etc/selinux/config
     
     # 临时关闭
     setenforce 0
    ```
    
1. yum 源更新
    
    ```Plain
     curl -o /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-7.repo
    ```
    
    ```Plain
     yum -y update
     
     reboot
    ```
    
    ```Plain
     yum clean
    
     yum makecache
    ```
    
# 2. **安装 nginx**
1. 解压 nginx 包
    
    ```Plain
     [root@nginx nginx-1.21.6]# tar -zxvf nginx-1.21.6.tar.gz
    ```
    
1. 进入安装包
    
    ```Plain
     [root@nginx ~]# ls
     anaconda-ks.cfg  nginx-1.21.6  nginx-1.21.6.tar.gz
     
     [root@nginx ~]# cd nginx-1.21.6
     
     [root@nginx nginx-1.21.6]# ls
     auto  CHANGES  CHANGES.ru  conf  configure  contrib  html  LICENSE  Makefile  man  objs  README  src
    ```
    
1. 安装 C 语言编译器
    
    ```Plain
     [root@nginx nginx-1.21.6]# yum install -y gcc
    ```
    
1. 安装 perl 库
    
    ```Plain
     [root@nginx nginx-1.21.6]# yum install -y pcre pcre-devel
    ```
    
1. 安装 zlib 库
    
    ```Plain
     [root@nginx nginx-1.21.6]# yum install -y zlib zlib-devel
    ```
    
1. 编译安装
    
    ```Plain
     [root@nginx nginx-1.21.6]# ./configure --prefix=/usr/local/nginx
    ```
    
    ```Plain
     [root@nginx nginx-1.21.6]# make
     
     [root@nginx nginx-1.21.6]# make install
    ```
    
1. 查看安装好的 nginx
    
    ```Plain
     [root@nginx nginx-1.21.6]# cd /usr/local/nginx/
     [root@nginx nginx]# ls
     conf  html  logs  sbin
    ```
    
1. nginx 的基础命令
    
    ```Plain
     [root@nginx nginx]# cd sbin/
     
     [root@nginx sbin]# pwd
     /usr/local/nginx/sbin
     
     [root@nginx sbin]# ls
     nginx
     
     [root@nginx sbin]# ./nginx
    ```
    
    ```Plain
     ./nginx                 # 启动
     ./nginx -s stop         # 快速停止
     ./nginx -s quit         # 优雅关闭，在退出前完成已经接受的连接请求
     ./nginx -s reload       # 重新加载配置
    ```
    
# 3. **systemd 管理 nginx**
1. 创建 system service 脚本（安装 K8S 时也执行过这些操作 部署K8S）
    
    ```Plain
     vi /usr/lib/systemd/system/nginx.service
    ```
    
    ```Plain
    [Unit]
     Description=nginx - web server
     After=network.target remote-fs.target nss-lookup.target
    [Service]
     Type=forking
     PIDFile=/usr/local/nginx/logs/nginx.pid
     ExecStartPre=/usr/local/nginx/sbin/nginx -t -c /usr/local/nginx/conf/nginx.conf
     ExecStart=/usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
     ExecReload=/usr/local/nginx/sbin/nginx -s reload
     ExecStop=/usr/local/nginx/sbin/nginx -s stop
     ExecQuit=/usr/local/nginx/sbin/nginx -s quit
     PrivateTmp=true
    [Install]
     WantedBy=multi-user.target
    ```
    
    > [!important]
    > 
    > - 相当于把对 nginx 服务的一些操作写成脚本
    > 
    > - 注意：这里的路径要写成自己的安装目录，因为具体执行的程序都是在安装目录的`**sbin**` 下
    
1. 重新加载系统服务
    
    ```Plain
     systemctl daemon-reload
    ```
    
1. 启动服务
    
    ```Plain
     systemctl start nginx.service
    ```
    
1. 设置开机自启
    
    ```Plain
     systemctl enable nginx.service
    ```
    
# 4. **测试**
访问：[http://192.168.10.191/](http://192.168.10.191/)
![[IMG-20260405035438279.png|Untitled 65.png]]