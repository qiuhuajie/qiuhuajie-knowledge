---
title: "Pod 基本配置"
tags:
  - "云原生"
  - "云原生/Kubernetes"
  - "云原生/Kubernetes/Pod"
  - "Pod 基本配置"
  - "yaml 配置文件操作 Pod"
  - "Kubernetes"
updated: 2026-04-16
---
# 一、基本配置
1. 示例：定义一个比较简单 Pod 的配置，里面有两个容器：
    - nginx：用 1.17.1 版本的 nginx 镜像创建，（nginx 是一个轻量级 web 容器）
    - busybox：用 1.30 版本的 busybox 镜像创建，（busybox 是一个小巧的 linux 命令集合）
2. 创建 pod-base.yaml 文件

    ```YAML
     apiVersion: v1
     kind: Pod
     metadata:
       name: pod-base
       namespace: dev
       labels:
         user: heima
     spec:
       containers:
       - name: nginx
         image: nginx:1.17.1
       - name: busybox
         image: busybox:1.30
    ```
3. 创建 Pod

    ```Bash
     [root@master ~]# kubectl apply -f pod-base.yaml -n dev
     pod/pod-base created
    ```
4. 查看 Pod

    ```Bash
     [root@master ~]# kubectl get pod -n dev
     NAME                        READY   STATUS              RESTARTS   AGE
     pod-base                    0/2     ContainerCreating   0          40s
    ```
    - busybox容器一直没有成功运行，是因为busybox并不是一个程序，而是类似于一个工具类的集合，kubernetes集群启动管理后，它会自动关闭
    - 解决方法就是让其一直在运行，需要在启动时使用command配置（见下面）
5. 查看 Pod 详情

    ```Bash
     [root@master ~]# kubectl describe pod -n dev
    ```
# 二、镜像拉取策略
1. **`pod.spec.containers.imagePullPolicy`**：用于设置镜像拉取策略
2. kubernetes支持配置**三种拉取策略：**
    - **`Always`**：每次创建 Pod 都总是去镜像仓库拉取镜像
    - **`IfNotPresent`**：本地有则使用本地镜像，本地没有则从远程仓库拉取镜像（本地有就本地 本地没远程下载）
    - **`Never`**：只使用本地镜像，从不去远程仓库拉取，本地没有就报错 （一直使用本地）
3. **默认值**说明：
    1. 如果省略imagePullPolicy，策略默认为 always
    2. 如果镜像tag为具体版本号， 默认策略为 IfNotPresent
    3. 如果镜像tag为：latest（最终版本） ，默认策略为 always
4. 示例：
    1. 创建pod-imagepullpolicy.yaml文件

        ```YAML
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-imagepullpolicy     # k8s中Pod的name不允许大写
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
             imagePullPolicy: Never # 用于设置镜像拉取策略
           - name: busybox
             image: busybox:1.30
        ```
    2. 创建 Pod

        ```Bash
         [root@master ~]# kubectl apply -f pod-imagepullpolicy.yaml -n dev
         pod/pod-imagepullpolicy created
        ```
    3. 查看 Pod

        ```Bash
         [root@master ~]# kubectl get pod -n dev
         NAME                        READY   STATUS              RESTARTS   AGE
         pod-imagepullpolicy         0/2     ContainerCreating   0          16s
        ```
    4. 查看 Pod 详情

        ```Bash
         [root@master ~]# kubectl describe pod -n dev
         可以看到在拉取nginx镜像时有 Container image "nginx:1.17.1" already present on machine
        ```
# 三、配置启动时命令
1. 在前面的案例中，一直有一个问题没有解决
    1. 就是的busybox容器一直没有成功运行，是因为busybox并不是一个程序，而是类似于一个工具类的集合
    2. kubernetes集群启动管理后，它会自动关闭
2. 解决方法就是让其一直在运行，这就用到了 **`pod.spec.containers.command`** 配置
3. 示例：在启动容器时，配置容器启动后要执行的命令
    1. 创建pod-command.yaml文件

        ```YAML
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-command
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
           - name: busybox
             image: busybox:1.30
             command: ["/bin/sh","-c","touch /tmp/hello.txt;while true;do /bin/echo $(date +%T) >> /tmp/hello.txt; sleep 3; done;"]
        ```
        命令说明：
        ```Bash
         /bin/sh -c # 使用sh执行命令
         touch /tmp/hello.txt # 创建一个/tmp/hello.txt 文件
         # 每隔3秒向文件中写入当前时间
         while true;
         do
             /bin/echo $(date +%T) >> /tmp/hello.txt;
             sleep 3
         done;
        ```
    2. 创建 Pod

        ```Bash
         [root@master ~]# kubectl apply -f pod-command.yaml -n dev
         pod/pod-command created
        ```
    3. 查看 Pod：可以看到 Pod 中的两个容器都正常运行

        ```Bash
         [root@master ~]# kubectl get pod -n dev
         NAME                        READY   STATUS             RESTARTS   AGE
         pod-command                 2/2     Running            0          3s
        ```
    4. 进入容器查看 busybox 容器启动命令写入的数据

        ```Bash
         [root@master ~]# kubectl exec pod-command -n dev -it -c busybox /bin/sh
         \kubectl exec [POD] [COMMAND] is DEPRECATED and will be removed in a future version. Use kubectl exec [POD] -- [COMMAND] instead.
         / # tail -f /tmp/hello.txt
         07:15:02
         07:15:05
         07:15:08
         07:15:11
         07:15:14
        ```
4. 还有一个与命令相关的配置 **`pod.spec.containers.args`**
    1. 通过上面发现 command 已经可以完成启动命令和传递参数的功能，为什么这里还要提供一个args选项，用于传递参数呢
    2. 这其实跟 docker 有点关系，kubernetes 中的 `command`、`args` 两项其实是实现覆盖 Dockerfile 中 `ENTRYPOINT` 的功能
        > Dockerfile 中 **`ENTRYPOINT`**：指定这个容器启动的时候要运行的命令，可以追加命令
        ```Bash
         ENTRYPOINT /etc/init.d/tomcat7 start && /usr/sbin/sshd -D
        ```
    3. 覆盖规则：
        1. 如果command和args均没有写，那么用Dockerfile的配置
        2. 如果command写了，但args没有写，那么Dockerfile默认的配置会被忽略，执行输入的command
        3. 如果command没写，但args写了，那么Dockerfile中配置的ENTRYPOINT的命令会被执行，使用当前args的参数
        4. 如果command和args都写了，那么Dockerfile的配置被忽略，执行command并追加上args参数

# 四、配置端口
1. **`pod.spec.containers.ports`** 支持的子选项

    ```YAML
     [root@master ~]# kubectl explain pod.spec.containers.ports
     KIND:     Pod
     VERSION:  v1
     RESOURCE: ports <[]Object>
     FIELDS:
        name         <string>  # 端口名称，如果指定，必须保证name在pod中是唯一的
        containerPort<integer> # 容器要监听的端口(0<x<65536)
        hostPort     <integer> # 容器要在主机上公开的端口，如果设置，主机上只能运行容器的一个副本(一般省略)
        hostIP       <string>  # 要将外部端口绑定到的主机IP(一般省略)
        protocol     <string>  # 端口协议。必须是UDP、TCP或SCTP。默认为“TCP”
    ```
2. 示例：
    1. 创建pod-ports.yaml文件

        ```YAML
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-ports
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
             ports: # 设置容器暴露的端口列表
             - name: nginx-port
               containerPort: 80
               protocol: TCP
        ```
    2. 创建 Pod

        ```Bash
         [root@master ~]# kubectl create -f pod-ports.yaml
         pod/pod-ports created
        ```
    3. 以 yaml 格式 查看 Pod 详细信息

        ```YAML
         [root@master ~]# kubectl get pod pod-ports -n dev -o yaml
         ...
         spec:
           containers:
           - image: nginx:1.17.1
             imagePullPolicy: IfNotPresent
             name: nginx
             ports:
             - containerPort: 80     # nginx容器监听80端口
               name: nginx-port
               protocol: TCP
         ...
         hostIP: 192.168.10.173
           phase: Running
           podIP: 10.244.140.83      # 本Pod中所有容器同时使用此podIP
           podIPs:
           - ip: 10.244.140.83
         ...
        ```
    4. 由于使用的传输协议是 TCP，故使用 **套接字** `PodIP:containerPort`访问容器中的程序

        ```Plain
         [root@master ~]# curl 10.244.140.83:80
         <!DOCTYPE html>
         <html>
         ... NGINX 首页
         </html>
        ```
# 五、资源配额
1. 容器中的程序要运行，肯定是要占用一定资源的，比如 cpu 和内存等，如果不对某个容器的资源做限制，那么它就**可能吃掉大量资源，导致其它容器无法运行**
2. 针对这种情况，kubernetes 提供了对内存和 cpu 的资源进行配额的机制，这种机制主要通过 **`pod.spec.containers.resources`** 选项实现
3. `resources` 有两个子选项：
    - **`limits`**：（上限）用于限制运行时容器的最大占用资源，当容器占用资源超过limits时会被终止，并进行重启
    - **`requests`** ：（下限）用于设置容器需要的最小资源，如果环境资源不够，容器将无法启动
4. 示例：
    1. 创建 pod-resources.yaml 文件

        ```YAML
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-resources
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
             resources: # 资源配额
               limits:  # 限制资源（上限）
                 cpu: "2" # CPU限制，单位是core数
                 memory: "10Gi" # 内存限制
               requests: # 请求资源（下限）
                 cpu: "1"  # CPU限制，单位是core数
                 memory: "10Mi"  # 内存限制
        ```
        - 在这对cpu和memory的单位：
            - cpu：core数，可以为整数或小数
            - memory： 内存大小，可以使用Gi、Mi、G、M等形式
    2. 创建 Pod

        ```Plain
         [root@master ~]# kubectl create  -f pod-resources.yaml
         pod/pod-resources created
        ```
    3. 查看发现pod运行正常

        ```Plain
         [root@master ~]# kubectl get pod pod-resources -n dev
         NAME            READY   STATUS    RESTARTS   AGE
         pod-resources   1/1     Running   0          6s
        ```
    4. 删除 Pod

        ```Plain
         [root@master ~]# kubectl delete  -f pod-resources.yaml
         pod "pod-resources" deleted
        ```
    5. 编辑pod，修改resources.requests.memory的值为10Gi

        ```Plain
               requests: # 请求资源（下限）
                 cpu: "1"
                 memory: "10Gi"
        ```
    6. 再次启动pod

        ```Plain
         [root@master ~]# kubectl create  -f pod-resources.yaml
         pod/pod-resources created
        ```
    7. 查看Pod状态，发现Pod启动失败

        ```Plain
         [root@master ~]# kubectl get pod pod-resources -n dev
         NAME            READY   STATUS    RESTARTS   AGE
         pod-resources   0/1     Pending   0          5s
        ```
    8. 查看pod详情会发现，如下提示

        ```Plain
         [root@master ~]# kubectl describ pod pod-resources -n dev
         nodes are available: 1 node(s) had taint {node-role.kubernetes.io/master: }, that the pod didn't tolerate, 2 Insufficient memory.(内存不足)
        ```
# 六、共享存储配置
1. Pod 需要将日志数据、业务数据等 持久化
    1. 一个 Pod 里的多个容器可以共享存储卷， 这个存储卷会被定义为 Pod 的一部分
    2. 并且 volume 数据卷可以挂载到该 Pod 中所有容器的文件系统上
2. 举例：
    1. 两个容器：一个负责读数据、一个负责写数据
    2. 如果两个容器之间存储相互隔离，读的容器是读不到写容器写入的数据的
    3. **将数据卷挂载到两个容器上，即可实现两个容器的存储共享**

        ![[IMG-20260404031955548.png|546]]
        ```YAML
         # pod_share-storage.yaml
         apiVersion: v1
         kind: Pod
         metadata:
           name: my-pod
         spec:
           containers:
           - name: write         # 写容器
             image: centos
             command: ["bash","-c","for i in {1..100};do echo $i >> /data/hello;sleep 1;done"]
             volumeMounts:   # 挂载 数据卷
             - name: data
               mountPath: /data
           - name: read          # 读容器
             image: centos
             command: ["bash","-c","tail -f /data/hello"]
             volumeMounts:   # 挂载 数据卷
             - name: data
               mountPath: /data
           volumes:                  # 挂载的 volume 数据卷
           - name: data
             emptyDir: {}
        ```
# 七、配置环境变量
1. **了解：**这种方式不是很推荐，推荐将这些配置**单独存储在配置文件中**，（详见 8.数据存储）
2. `pod.spec.containers.env`：用于在pod中的容器设置环境变量
3. 示例
    1. 创建pod-env.yaml文件，内容如下：

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-env
           namespace: dev
         spec:
           containers:
           - name: busybox
             image: busybox:1.30
             command: ["/bin/sh","-c","while true;do /bin/echo $(date +%T);sleep 60; done;"]
             env: # 设置环境变量列表
             - name: "username"
               value: "admin"
             - name: "password"
               value: "123456"
        ```
    2. 创建Pod

        ```Plain
         [root@master ~]# kubectl create -f pod-env.yaml
         pod/pod-env created
        ```
    3. 进入容器，输出环境变量

        ```Plain
         [root@master ~]# kubectl exec pod-env -n dev -c busybox -it /bin/sh
         / # echo $username
         admin
         / # echo $password
         123456
        ```
