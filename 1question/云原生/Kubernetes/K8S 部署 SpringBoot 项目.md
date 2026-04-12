- [[#1. 构建镜像]]
- [[#2. 构建镜像仓库]]
- [[#3. 修改镜像源]]
- [[#4. 推送镜像]]
- [[#5. 使用 deplpyment 启动 Pod]]
- [[#6. 使用 NodePort 暴露端口]]
- [[#7. 测试访问]]
# 1. **构建镜像**
1. 原来的部署方式：将java应用打成 jar 包，再使用 java 命令启动应用
    
    ```Plain
     java -jar springBootAdmin-0.0.1-SNAPSHOT.jar
    ```
    
1. **存在的问题：需要服务器已经安装了相应版本的java环境、mysql环境等等**
1. 解决方法：
    
    1. 容器化部署
    
    1. 所有机器都安装Docker，任何应用都是镜像，所有机器都可以运行
    
1. 创建一个 SpringBoot 程序
    
    ```Java
     @RestController
     public class testController {
         private int count = 0;
         @RequestMapping("/test")
         public String test(){
             return "有【"+ count++ +"】 人访问了这个页面";
         }
     }
    ```
    
1. 编写 Dockerfile
    
    ```Docker
     FROM openjdk:8-jdk-slim
     
     COPY target/*.jar /app.jar
     ENTRYPOINT ["java","-jar","app.jar"]
    ```
    
    - 去 DockerHub 上找想要的镜像
        
        ![[IMG-20260404031955006.png|Untitled 136.png]]
        
    
1. 使用 maven 打包，只保留 Dockerfile 与 jar包 dockerSpringBootDemo-0.0.1-SNAPSHOT.jar
1. 传到服务器上：
    
    ```Plain
     [root@master DockerSpringBootDemo]# ls
     Dockerfile  target
     
     [root@master DockerSpringBootDemo]# cd target/
     
     [root@master target]# ls
     dockerSpringBootDemo-0.0.1-SNAPSHOT.jar
     
     [root@master target]# cd ..
     [root@master DockerSpringBootDemo]# pwd
     /root/springBootDemo/DockerSpringBootDemo
    ```
    
1. 构建镜像
    
    ```Plain
     [root@master DockerSpringBootDemo]# docker build -t srping_boot_demo:v1.0 .
     Sending build context to Docker daemon  17.56MB
     Step 1/3 : FROM openjdk:8-jdk-slim
     8-jdk-slim: Pulling from library/openjdk
     a2abf6c4d29d: Pull complete
     2bbde5250315: Pull complete
     115191490c27: Pull complete
     61b680ac8083: Pull complete
     Digest: sha256:25efb6e0609b95af243b4e3ce2c27dbc1022ef2a4db2164b7afa066c0db18137
     Status: Downloaded newer image for openjdk:8-jdk-slim
      ---&gt; 9afd0fe33df7
     Step 2/3 : COPY target/*.jar /app.jar
      ---&gt; 37304d0eb2ec
     Step 3/3 : ENTRYPOINT [&quot;java&quot;,&quot;-jar&quot;,&quot;app.jar&quot;]
      ---&gt; Running in 549652c11e1d
     Removing intermediate container 549652c11e1d
      ---&gt; 0d2fd9fd3003
     Successfully built 0d2fd9fd3003
     Successfully tagged srping_boot_demo:v1.0
    ```
    
    - 镜像的名字不能带有大写字母！
        
        ```Plain
         [root@master DockerSpringBootDemo]# docker build -t srpingBootDemo:v1.0 .
         invalid argument "srpingBootDemo:v1.0" for "-t, --tag" flag: invalid reference format: repository name must be lowercase
         See 'docker build --help'.
        ```
        
    
1. 查看镜像
    
    ```Plain
     [root@master DockerSpringBootDemo]# docker images
     REPOSITORY                                              TAG          IMAGE ID       CREATED          SIZE
     srping_boot_demo                                        v1.0         0d2fd9fd3003   11 seconds ago   313MB
    ```
    
1. 启动容器**（这里启动容器只是想测试一下镜像是否正常）**
    
    ```Plain
     [root@master DockerSpringBootDemo]# docker run -d -p 8080:8080 srping_boot_demo:v1.0
     e50243abeadc4ab1f51edc7929db3296774d2a5ee8369d9d52fc557c53cecd49
    ```
    
1. 查看容器
    
    ```Plain
     [root@master DockerSpringBootDemo]# docker ps
     CONTAINER ID   IMAGE                                               COMMAND                  CREATED         STATUS         PORTS                                       NAMES
     e50243abeadc   srping_boot_demo:v1.0                               "java -jar app.jar"      7 seconds ago   Up 6 seconds   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   kind_yalow
    ```
    
1. [http://192.168.10.171:8080/test](http://192.168.10.171:8080/test)
    
    ![[IMG-20260404031955056.png|Untitled 1 85.png]]
    
# 2. **构建镜像仓库**
1. 新建一台机器：
    
    ```Plain
     [root@registry ~]# cat /etc/sysconfig/network-scripts/ifcfg-ens32
     TYPE="Ethernet"
     PROXY_METHOD="none"
     BROWSER_ONLY="no"
     BOOTPROTO="static"
     DEFROUTE="yes"
     IPV4_FAILURE_FATAL="no"
     IPV6INIT="yes"
     IPV6_AUTOCONF="yes"
     IPV6_DEFROUTE="yes"
     IPV6_FAILURE_FATAL="no"
     IPV6_ADDR_GEN_MODE="stable-privacy"
     NAME="ens32"
     UUID="9be4c57a-42b1-4fdb-b940-b1b6770e9a20"
     DEVICE="ens32"
     ONBOOT="yes"
     IPADDR=192.168.10.174
     GATEWAY=192.168.10.2
     DNS1=192.168.10.2
     
     [root@registry ~]# cat /etc/hostname
     registry
     
     [root@registry ~]# cat /etc/hosts
     192.168.10.171 master
     192.168.10.174 registry
    ```
    
    > 在本地镜像服务器上操作
    
1. 安装 Docker
    
    1. 安装 wget
        
        ```Plain
         yum install wget
        ```
        
    
    1. 安装 Docker
        
        ```Plain
         wget https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo -O /etc/yum.repos.d/docker-ce.repo
         
         yum -y install docker-ce-18.06.1.ce-3.el7
         
         systemctl enable docker && systemctl start docker
         
         docker --version
        ```
        
    
    1. 给 Docker 配置阿里云加速
        
        ```Plain
         cat > /etc/docker/daemon.json << EOF
         {
         "registry-mirrors": ["https://b9pmyelo.mirror.aliyuncs.com"]
         }
         EOF
        ```
        
    
    1. 重启docker 服务
        
        ```Plain
         systemctl daemon-reload
         
         systemctl restart docker
        ```
        
    
    1. 验证阿里云仓库是否配置成功
        
        ```Plain
         docker info
         
         ...
         Registry Mirrors:
          https://b9pmyelo.mirror.aliyuncs.com/
         ...
        ```
        
    
1. pull 一个官方给的registry 的模板镜像，用于在镜像仓库服务器上构建仓库
    
    ```Plain
     [root@registry ~]# docker run -d -v /opt/registry:/var/lib/registry -p 5000:5000 --restart=always registry
    ```
    
# 3. **修改镜像源**

> [!important] 在 K8S 集群的 master 节点、node01节点、node02节点上操作
1. 修改端口配置文件，将上面的阿里云仓库改成 自建的本地镜像仓库
    
    ```Plain
     [root@registry ~]# vim /etc/docker/daemon.json
    ```
    
    ```Plain
     {
             "insecure-registries": ["192.168.10.110:5000"]
     }
    ```
    
    > 注意这里是：insecure-registries
    
1. 重启docker
    
    ```Plain
     [root@registry ~]# systemctl daemon-reload
     [root@registry ~]# systemctl restart docker
    ```
    
1. 查看此时使用的 Docker 镜像仓库
    
    ```Plain
     [root@registry ~]# docker info
     
     ...
     Insecure Registries:
      192.168.10.174:5000
      127.0.0.0/8
     ...
    ```
    

> [!important] **一定记得将集群中所有的 node 节点也修改镜像仓库源！**
> 
> - 镜像的拉取是在Pod 调度之后的
> 
> - 也就是说==真正 Pull 镜像的是 node 节点==
> 
> - 踩坑：由于只改了 master 节点的镜像仓库源，会导致镜像一直下载失败
> 
> ```Plain
>  [root@master DockerSpringBootDemo]# kubectl get pod
>  NAME             READY   STATUS              RESTARTS   AGE
>  springbootdemo   0/1     ContainerCreating   0          5s
>  
>  [root@master DockerSpringBootDemo]# kubectl describe pod springbootdemo
>  ...
>  Events:
>  Type     Reason     Age                  From               Message
>  ----     ------     ----                 ----               -------
>  Normal   Scheduled  2m38s                default-scheduler  Successfully assigned default/springbootdemo to node02      # ⭐ pod 被调度给 node02，node02开始下载镜像
>  Warning  Failed     63s (x2 over 114s)   kubelet            Failed to pull image "springbootdemo:v1.0": rpc error: code = Unknown desc = Error response from daemon: http: server gave HTTP response to HTTPS client
>  Warning  Failed     63s (x2 over 114s)   kubelet            Error: ErrImagePull
>  Normal   BackOff    49s (x2 over 114s)   kubelet            Back-off pulling image "springbootdemo:v1.0"
>  Warning  Failed     49s (x2 over 114s)   kubelet            Error: ImagePullBackOff
>  Normal   Pulling    34s (x3 over 2m37s)  kubelet            Pulling image "springbootdemo:v1.0"
> ```
# 4. **推送镜像**

> [!important] 在 K8S 集群的 master 节点上操作
1. 向本地镜像仓库 push 镜像
    
    1. 修改要上传的镜像的名字：
        
        > 上传镜像需要的镜像标识符：仓库地址/userName/imageName:tag
        
        ```Plain
         [root@master DockerSpringBootDemo]# docker tag springbootdemo:v1.0 192.168.10.174:5000/springbootdemo:v1.0
        ```
        
    
    1. push 镜像
        
        ```Plain
         [root@master DockerSpringBootDemo]# docker push 192.168.10.174:5000/springbootdemo:v1.0
         The push refers to repository [192.168.10.174:5000/springbootdemo]
         773f14f8f38a: Pushed
         c8fa2e981776: Pushed
         3341e899db61: Pushed
         afda989d53ee: Pushed
         2edcec3590a4: Pushed
         v1.0: digest: sha256:0a9303110e485a3ac6bcd9e21e07124eaea97b05447204b05ceaf8e8f53c28dc size: 1372
        ```
        
    
    1. 查看本地镜像仓库上的镜像
        
        ```Plain
         [root@master DockerSpringBootDemo]# curl -XGET http://192.168.10.174:5000/v2/_catalog
         {"repositories":["springbootdemo"]}
        ```
        
    
1. 测试本地自建镜像仓库上的镜像是否可用
    
    1. 使用远程镜像启动容器
        
        ```Plain
         [root@master DockerSpringBootDemo]# docker run --name springbootdemo -p 8080:8080 192.168.10.174:5000/springbootdemo:v1.0
         Unable to find image '192.168.10.174:5000/springbootdemo:v1.0' locally      # 本地没有找到镜像
         v1.0: Pulling from springbootdemo                                           # 去自建镜像仓库下载
         a2abf6c4d29d: Already exists
         2bbde5250315: Already exists
         115191490c27: Already exists
         61b680ac8083: Already exists
         587148c8979a: Already exists
         Digest: sha256:0a9303110e485a3ac6bcd9e21e07124eaea97b05447204b05ceaf8e8f53c28dc
         Status: Downloaded newer image for 192.168.10.174:5000/springbootdemo:v1.0
        ```
        
        ![[IMG-20260404031955109.png|Untitled 2 67.png]]
        
    
    1. 访问：[http://192.168.10.171:8080/test](http://192.168.10.171:8080/test)
    
# 5. **使用 deplpyment 启动 Pod**
1. 使用命令获取 yaml 文件模板
    
    ```Plain
     [root@master ~]# kubectl create deployment springbootdemo --image=192.168.10.174:5000/springbootdemo:v1.0 --dry-run=client -o yaml > springbootdemo.yaml
     
     [root@master ~]# ls
     ... springbootdemo.yaml ...
     
     [root@master ~]# vi springbootdemo.yaml
    ```
    
1. 对 yaml 配置做需求修改
    
    ```Plain
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       creationTimestamp: null
       labels:
         app: springbootdemo
       name: springbootdemo
     spec:
       replicas: 3           # 启动三个高可用的服务
       selector:
         matchLabels:
           app: springbootdemo
       strategy: {}
       template:
         metadata:
           creationTimestamp: null
           labels:
             app: springbootdemo
         spec:
           containers:
           - image: 192.168.10.174:5000/springbootdemo:v1.0      # 本地自建镜像仓库的镜像
             name: springbootdemo
             resources: {}
     status: {}
    ```
    
1. 启动 deployment
    
    ```Plain
     [root@master ~]# kubectl create -f springbootdemo.yaml
     deployment.apps/springbootdemo created
    ```
    
1. 查看 deployment
    
    ```Plain
     [root@master ~]# kubectl get deployment
     NAME             READY   UP-TO-DATE   AVAILABLE   AGE
     springbootdemo   3/3     3            3           13s
    ```
    
1. 产看 pod
    
    ```Plain
     [root@master ~]# kubectl get pod
     NAME                              READY   STATUS    RESTARTS   AGE
     springbootdemo-75f458f7fc-65c64   1/1     Running   0          21s
     springbootdemo-75f458f7fc-9n6r7   1/1     Running   0          21s
     springbootdemo-75f458f7fc-djgjf   1/1     Running   0          21s
    ```
    
# 6. **使用 NodePort 暴露端口**
1. 创建 service yaml 文件
    
    ```Plain
     apiVersion: v1
     kind: Service
     metadata:
       name: springbootdemo-service
     spec:
       selector:
         app: springbootdemo     # ⭐ 这里标签选择器一定要写，不然service不知道给哪个deploy暴露端口！且要与deploy的标签对应
       type: NodePort            # sevice 类型是 nodeport
       ports:
       - port: 8080              # service 的端口
         nodePort: 30000         # node 节点的端口
         targetPort: 8080        # 应用程序的端口（在代码里已经写好了）
    ```
    
    > [!important] nodePort 的指定由范围要求：
    > 
    > ```Plain
    >  The Service "service-nodeport" is invalid: spec.ports[0].nodePort: Invalid value: 3000: provided port is not in the valid range. The range of valid ports is 30000-32767
    > ```
    
1. 创建 service ，给deployment 暴露对外的服务
    
    ```Plain
     [root@master ~]# kubectl create -f springbootdemoservice.yaml
     service/springbootdemo-service created
    ```
    
1. 查看 service
    
    ```Plain
     [root@master ~]# kubectl get svc -o wide
     NAME                     TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE   SELECTOR
     kubernetes               ClusterIP   10.96.0.1        <none>        443/TCP          11d   <none>
     springbootdemo-service   NodePort    10.100.146.163   <none>        8080:30000/TCP   4s    app=springbootdemo
    ```
    
1. 也可以使用`**expose**`命令直接对外暴露服务
    
    ```Plain
     [root@master ~]# kubectl expose deployment springbootdemo --port=8080 --type=NodePort
     service/nginx exposed
    ```
    
# 7. **测试访问**
访问：[http://192.168.10.171:30000/test](http://192.168.10.171:30000/test)
![[IMG-20260404031955056.png|Untitled 1 85.png]]