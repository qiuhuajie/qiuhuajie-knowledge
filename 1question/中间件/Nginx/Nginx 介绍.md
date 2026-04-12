- [[#1. nginx 的目录结构]]
- [[#2. 基本运行原理]]
- [[#3. Nginx 企业架构案例]]
# 1. **nginx 的目录结构**
```Plain
 [root@nginx ~]# cd /usr/local/nginx/
 [root@nginx nginx]# ls
 client_body_temp  conf  fastcgi_temp  html  logs  proxy_temp  sbin  scgi_temp  uwsgi_temp
 [root@nginx nginx]#
```
- `**conf**`：配置文件
- `**html**`：默认情况下的首页，和一些静态资源
- `**logs**`：记录日志
    
    - access.log：用户访问记录
    
    - error.log：当系统出错时会记录到此日志
    
    - nginx.pid：记录 nginx 主进程的 ID 号
        
        ```Plain
         [root@nginx logs]# cat nginx.pid
         1509
        ```
        
    
- `**sbin**`：nginx 主程序
- `**xxx_temp**`：运行产生的临时文件
# 2. **基本运行原理**
![[Attachment/1question/中间件/Nginx/IMG-20260405035438278.png|Untitled 66.png]]
# 3. **Nginx 企业架构案例**
![[IMG-20260405035401484.png|Untitled 1 37.png]]

> [!important] **Gateway Server**
> 
> - 把业务服务器统一的管理起来，在中间起查找和寻找（**路由**）的作用，和一定的鉴权（**断言、过滤器**）功能
> 
> - 详见 SpringCloud 10.3 Gateway 三大核心概念