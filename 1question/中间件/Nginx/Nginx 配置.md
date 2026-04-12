- [[#1. nginx 的配置文件]]
- [[#2. 配置字段解释]]
# 1. **nginx 的配置文件**
```Plain
 [root@nginx logs]# cat /usr/local/nginx/conf/nginx.conf
```
```JSON
 worker_processes  1;
 
 events {
     worker_connections  1024;
 }
 
 
 http {
 
     # include可以把另外的配置文件引入
     include       mime.types;
     default_type  application/octet-stream;
 
		 # 是否开启零拷贝
     sendfile        on;
     # 设置连接超时
     keepalive_timeout  65;
 
     # 主机（一个nginx可以开启多个虚拟主机）
     server {
         listen       80;
         # 域名或主机名
         server_name  localhost;
 
         # 匹配访问的资源请求
         # URI
         location / {
             # 从哪个目录下开始匹配 URI
             root   html;
             # 默认页
             index  index.html index.htm;
         }
 
         # 错误页设置
         error_page   500 502 503 504  /50x.html;
         location = /50x.html {
             root   html;
         }
     }
 }
 # 这是一个最简化的 nginx 配置文件（）把注释都删了
```
# 2. **配置字段解释**
- `**worker_processes**`：配置开启多少个子进程
- `**include**`：mime.types
    
    - MIME(Multipurpose Internet Mail Extensions)多用途互联网邮件扩展类型
        
        - 用于设定**某种扩展名的文件用一种应用程序来打开的方式类型**：当该扩展名文件被访问的时候，浏览器会自动使用指定应用程序来打开
        
        - 多用于指定一些客户端自定义的文件名，以及一些媒体文件打开方式
        
    
    - 查看一下 mime.types
        
        ```Plain
         [root@nginx conf]# cat  mime.types
         
         types {
             text/html                                        html htm shtml;
             text/css                                         css;
             text/xml                                         xml;
             image/gif                                        gif;
             ...
         }
        ```
        
    
- `**default_type application/octet-stream**`：如果当前文件格式不包含在mime.types中，则默认使用application/octet-stream处理
- `**sendfile**` [[6.3 零拷贝]]
    
    - 如果开启后`**on**`，当用户访问服务器上的资源时，应用程序不会读取静态资源，而是告诉Linux 系统直接去读取相应的静态资源，再由操作系统读到操作系统的网络接口缓存中，再发送给用户
    
    - 如果是关闭状态，应用程序会先把静态资源先加载到自己的内存中，再将资源复制到网络接口缓存，最后网络接口将资源推送给用户
    
    ![[IMG-20260404031924513.png|Untitled 67.png]]
    
- `**server.listen**`：配置虚拟主机监听的端口
- `**server.server_name**`：配置寻主机的主机名或域名
- `**server.location.root**`：从哪个目录下开始匹配 URI
- `**server.location.index**`：配置默认页
    
    - 先创建虚拟主机挂载的目录 以及 各自的默认页
        
        ```Plain
         [root@nginx testNginx]# tree /testNginx/
         /testNginx/
         ├── mail
         │   └── qhjqhj
         │       └── index.html
         └── www
             └── qhjqhj
                 └── index.html
         
         4 directories, 2 files
        ```
        
    
    - 修改 nginx 的配置文件
        
        ```Plain
         [root@nginx testNginx]# cd /usr/local/nginx/conf/
         [root@nginx conf]# vi nginx.conf
        ```
        
        ```JSON
         worker_processes  1;
         pid        logs/nginx.pid;
         events {
             worker_connections  1024;
         }
         http {
             include       mime.types;
             default_type  application/octet-stream;
             sendfile        on;
             keepalive_timeout  65;
        
             # 配置两个虚拟主机，对应不同的资源目录，并监听不同的端口
             server {
                 listen       80;
                 server_name  localhost;
                 location / {
                     root   /testNginx/www/qhjqhj;
                     index  index.html index.htm;
                 }
                 error_page   500 502 503 504  /50x.html;
                 location = /50x.html {
                     root   html;
                 }
             }
             server {
                 listen       88;
                 server_name  localhost;
                 location / {
                     root   /testNginx/mail/qhjqhj;
                     index  index.html index.htm;
                 }
                 error_page   500 502 503 504  /50x.html;
                 location = /50x.html {
                     root   html;
                 }
             }
         }
        ```
        
        修改配置文件后，要重新加载服务
        
        ```Plain
         [root@nginx conf]# systemctl reload nginx
        ```
        
        访问：[http://192.168.10.191:88/](http://192.168.10.191:88/)、[http://192.168.10.191:80/](http://192.168.10.191/)
        
        ![[IMG-20260404031924565.png|Untitled 1 38.png]]
        
        ![[IMG-20260404031924602.png|Untitled 2 28.png]]