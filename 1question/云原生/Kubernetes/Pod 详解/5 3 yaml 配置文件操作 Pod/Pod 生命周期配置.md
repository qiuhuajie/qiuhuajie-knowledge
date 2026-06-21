---
title: "Pod 生命周期配置"
tags:
  - "云原生"
  - "云原生/Kubernetes"
  - "云原生/Kubernetes/Pod"
  - "Pod 生命周期配置"
  - "yaml 配置文件操作 Pod"
  - "Kubernetes"
updated: 2026-04-16
---
# 一、生命周期介绍
## 1. Pod 生命周期
- 将pod对象从创建至终的这段时间范围称为pod的生命周期，它主要包含下面的过程：

    ![[IMG-20260404031955605.png|800]]

    - pod创建过程
    - 运行初始化容器（init container）过程
    - 运行主容器（main container）
        - 容器启动后钩子（post start）、容器终止前钩子（pre stop）
        - 容器的存活性探测（liveness probe）、就绪性探测（readiness probe）
    - pod终止过程

## 2. Pod 五种状态

![[IMG-20260404031955681.png|800]]

- 挂起（`Pending`）：apiserver已经创建了pod资源对象，但它尚未被调度完成或者仍处于下载镜像的过程中
- 运行中（`Running`）：pod已经被调度至某节点，并且所有容器都已经被kubelet创建完成
- 成功（`Succeeded`）：pod中的所有容器都已经成功终止并且不会被重启
- 失败（`Failed`）：所有容器都已经终止，但至少有一个容器终止失败，即容器返回了非 0 值的退出状态
- 未知（`Unknown`）：apiserver无法正常获取到pod对象的状态信息，通常由网络通信失败所导致
# 二、Pod 的创建过程

![[IMG-20260404031955758.png|800]]

1. 用户通过 kubectl 命名发起 创建一个 Pod 的请求，并提交需要创建的 Pod 信息
2. 进入 API Server 中，将 Pod 相关信息存储到 etcd 中，然后返回确认信息至客户端
3. Scheduler
    1. Scheduler 会监听 API Server 中的 Watch 接口，查看是否有新的 Pod 被创建
    2. 如果有则从 etcd 中读取到新建 Pod 的信息，通过调度算法 把 Pod 调度到某个 node 节点上
    3. 并将 Pod 和对应节点绑定的信息交给 API Server，API Server 将绑定信息写到 etcd
4. 如果 Pod 被调度到 node02 节点上
    1. node02 节点上的 Kubelet 也会监听 API Server ，它监听的是 API Server 中是否有新的 Pod 被绑定到本节点
    2. 如果有，则从 etcd 中读取到 Pod 的绑定信息
        1. 调用 CNI 接口给 Pod 创建 Pod 网络
        2. 调用 CRI 接口去启动容器（通过 Docker 创建容器）
        3. 调用 CSI 进行存储卷的挂载
    3. 并将 Pod 的状态返回给 API Server

# 三、Pod 的终止过程
1. 用户向apiServer发送删除 Pod 对象的命令
2. apiServcer中的 Pod 对象信息会随着时间的推移而更新，在宽限期内（默认30s），pod被视为dead
3. apiServcer将 Pod 标记为 terminating 状态（修改pod在etcd的信息）
4. kubelet在监控（kubelet一直watch着etcd）到 Pod 对象转为terminating状态的同时启动 Pod 关闭过程
5. 端点控制器监控到 Pod 对象的关闭行为时将其从所有匹配到此端点的service资源的端点列表中移除
6. 如果当前 Pod 对象定义了preStop钩子处理器，则在其标记为terminating后即会以同步的方式启动执行
7. Pod 对象中的容器进程收到停止信号
8. 宽限期结束后，若pod中还存在仍在运行的进程，那么 Pod 对象会收到立即终止的信号
9. kubelet请求apiServer将此pod资源的宽限期设置为0从而完成删除操作，此时pod对于用户已不可见
# 四、initContainers
1. **初始化容器是**==**在 Pod 的主容器启动之前要运行的容器**====，主要是做一些====**主容器的前置工作**==
2. 初始化容器有两大特征：
    1. **（必须启动成功）**初始化容器必须运行完成直至结束，若某初始化容器运行失败，那么kubernetes需要重启它直到成功完成
    2. **（串行启动）**初始化容器必须按照定义的顺序执行，当且仅当前一个成功之后，后面的一个才能运行
3. 初始化容器有很多的应用场景，下面列出的是最常见的几个：
    - 提供主容器镜像中不具备的工具程序或自定义代码
    - 初始化容器要先于应用容器串行启动并运行完成，因此可用于延后应用容器的启动直至其依赖的条件得到满足
4. 示例：假设要以主容器来运行nginx，但是要求在运行nginx之前先要能够连接上mysql和redis所在服务器
    1. 创建pod-initcontainer.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-initcontainer
           namespace: dev
         spec:
           containers:
           - name: main-container
             image: nginx:1.17.1
             ports:
             - name: nginx-port
               containerPort: 80
           initContainers:
           - name: test-mysql
             image: busybox:1.30
             command: ['sh', '-c', 'until ping 192.168.90.14 -c 1 ; do echo waiting for mysql...; sleep 2; done;']
           - name: test-redis
             image: busybox:1.30
             command: ['sh', '-c', 'until ping 192.168.90.15 -c 1 ; do echo waiting for reids...; sleep 2; done;']
        ```
    2. 创建pod

        ```Plain
         [root@master ~]# kubectl create -f pod-initcontainer.yaml
         pod/pod-initcontainer created
        ```
    3. 查看pod状态

        ```Plain
         [root@master ~]# kubectl describe pod  pod-initcontainer -n dev
         Events:
           Type    Reason     Age   From               Message
           ----    ------     ----  ----               -------
           Normal  Scheduled  8s    default-scheduler  Successfully assigned dev/pod-initcontainer to node02
           Normal  Pulled     7s    kubelet            Container image "busybox:1.30" already present on machine
           Normal  Created    7s    kubelet            Created container test-mysql
           Normal  Started    7s    kubelet            Started container test-mysql
           # pod卡在启动第一个初始化容器过程中，后面的容器不会运行
        ```
    4. 动态查看pod：`STATUS`为 Init:0/2，两个初始化容器都没有启动

        ```Plain
         [root@master ~]# kubectl get pods pod-initcontainer -n dev -w
         NAME                READY   STATUS     RESTARTS   AGE
         pod-initcontainer   0/1     Init:0/2   0          2m11s
        ```
    5. 接下来新开一个shell，为当前服务器新增两个ip，观察pod的变化

        ```Plain
        # 安装
        yum install net-tools
        ```
        ```Plain
         [root@master ~]# ifconfig ens32:1 192.168.10.175 netmask 255.255.255.0 up
         [root@master ~]# ifconfig ens32:1 192.168.10.175 netmask 255.255.255.0 up
        ```
    6. 上面动态查看pod的信息有更新：`STATUS` 逐步从 Init:0/2 变为 Running

        ```Plain
         [root@master ~]# kubectl get pods pod-initcontainer -n dev -w
         NAME                READY   STATUS     RESTARTS   AGE
         pod-initcontainer   0/1     Init:0/2   0          2m11s
         pod-initcontainer   0/1     Init:1/2   0          5m37s
         pod-initcontainer   0/1     PodInitializing   0          5m51s
         pod-initcontainer   1/1     Running           0          5m52s
        ```
# 五、钩子函数
1. 钩子函数==能够感知自身生命周期中的事件，并在==**==相应的时刻到来时运行用户指定的程序代码==**（类似于拦截器的前置和后置操作）
2. kubernetes 在主容器的启动之后和停止之前提供了两个钩子函数：
    - **`post start`**：容器创建之后执行，如果失败了会重启容器
    - **`pre stop`** ：容器终止之前执行，执行完成之后容器将成功终止，在其完成之前会阻塞删除容器的操作
3. 钩子处理器支持使用下面三种方式定义动作：
    1. **Exec命令：在容器内执行一次命令**

        ```Plain
         ……
           lifecycle:
             postStart:
               exec:
                 command:
                 - cat
                 - /tmp/healthy
         ……
        ```
    2. **TCPSocket：在当前容器尝试访问指定的socket**

        ```Plain
         ……
           lifecycle:
             postStart:
               tcpSocket:
                 port: 8080
         ……
        ```
    3. **HTTPGet：在当前容器中向某url发起http请求**

        ```Plain
         ……
           lifecycle:
             postStart:
               httpGet:
                 path: / \#URI地址
                 port: 80 \#端口号
                 host: 192.168.5.3 \#主机地址
                 scheme: HTTP \#支持的协议，http或者https
         ……
        ```
4. 示例：以exec方式为例，演示下钩子函数的使用
    1. 创建pod-hook-exec.yaml文件

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-hook-exec
           namespace: dev
         spec:
           containers:
           - name: main-container
             image: nginx:1.17.1
             ports:
             - name: nginx-port
               containerPort: 80
             lifecycle:
               postStart:
                 exec: # 在容器启动的时候执行一个命令，修改掉nginx的默认首页内容
                   command: ["/bin/sh", "-c", "echo postStart... > /usr/share/nginx/html/index.html"]
               preStop:
                 exec: # 在容器停止之前停止nginx服务
                   command: ["/usr/sbin/nginx","-s","quit"]
        ```
    2. 创建 Pod

        ```Plain
         [root@master ~]# kubectl create -f pod-hook-exec.yaml -n dev
         pod/pod-hook-exec created
        ```
    3. 查看 Pod

        ```Plain
         [root@master ~]# kubectl get pods  pod-hook-exec -n dev -o wide
         NAME            READY   STATUS    RESTARTS   AGE   IP              NODE     NOMINATED NODE   READINESS GATES
         pod-hook-exec   1/1     Running   0          9s    10.244.140.92   node02   <none>           <none>
        ```
    4. 访问 nginx 主页：可以看到以及被修改

        ```Plain
         [root@master ~]# curl 10.244.140.92
         postStart...
        ```
# 六、容器探测
1. 强大的自愈能力是 Kubernetes 这类容器编排引擎的一个重要特性，保障业务可用性
2. 自愈的**默认实现方式：**
    1. 默认情况下，容器进程返回值非零，Kubernetes 则认为容器发生故障，将自动重启发生故障的容器（即重启策略）
    2. 每个容器启动时都会执行一个进程，此进程由 Dockerfile 的 CMD 或 ENTRYPOINT 指定
    3. 如果进程退出时返回码非零，则认为容器发生故障，Kubernetes 就会根据 `restartPolicy` 重启容器
        > 💡 **退出状态码：**
        >
        > - 使用echo $? 查看
        >
        >     ```Plain
        >      [root@master opt]# mkdir /opt/test
        >      [root@master opt]# echo $?
        >      0
        >
        >      [root@master opt]# ls
        >      test
        >      [root@master opt]# echo $?
        >      0
        >
        >      [root@master opt]# rmdir /opt/test/
        >      [root@master opt]# echo $?
        >      0
        >
        >      [root@master opt]# cd /opt/test
        >      -bash: cd: /opt/test: No such file or directory
        >      [root@master opt]# echo $?                                  # 确认指令是否成功执行：如果返回值是0，就是执行成功；如果是返回值是0以外的值，就是失败
        >      1
        >     ```
        >
        >     1. 当一个进程执行完毕时，该进程会调用一个名为 _exit 的例程来通知内核它已经做好“消亡”的准备了
        >
        >     2. 该进程会提供一个退出码（一个整数）表明它准备退出的原因。按照惯例，0用来表示正常的或者说“成功”的终止
        >
        >     3. 这个退出码就是 退出状态码
        >
3. ⭐==**但是！有不少情况是发生了故障，但进程并不会退出：**==
    1. 比如访问 Web 服务器时显示 500 内部错误，可能是系统超载，也可能是资源死锁
    2. **此时 httpd 进程并没有异常退出**
    3. 在这种情况下重启容器可能不是最直接最有效的解决方案，如何处理这类场景呢？
4. ==处理方式：====**两种探针**==
    - 用户可以利用 LivenessProbe 和 ReadinessProbe 探测机制设置更精细的健康检查，是在应用层面的健康检查（probe - 探针）
        - **`liveness probes`：**
            - 存活性探针，用于检测应用实例当前是否处于正常运行状态，如果不是，k8s会重启容器
            - 探测失败后的行为：如果检查失败，**直接 kill container，如果当前的重启策略 Restart policy 是 always 会重启 Pod**
        - **`readiness probes`：**
            - 就绪性探针，用于检测应用实例当前是否可以接收请求，如果不能，k8s不会转发流量
            - 探测失败后的行为：如果检查失败，会**把这个pod 的所有 service 的 endpoint 里面的 Pod IP 删掉，意思就这个 Pod 对应的所有 Service 都不会把请求转到这个 Pod 来了**
5. 两种探针的选择：
    - livenessProbe 决定是否重启容器，readinessProbe 决定是否将请求转发给容器
    - Liveness 探测和 Readiness 探测是独立执行的，二者之间没有依赖，所以**可以单独使用**，也**可以同时使用**
    - 用 **Liveness 探测判断容器是否需要重启以实现自愈**
    - 用 **Readiness 探测判断容器是否已经准备好对外提供服务**
6. **探针的配置：**

    ```Plain
     [root@k8s-master01 ~]# kubectl explain pod.spec.containers.livenessProbe
     FIELDS:
        exec <Object>    # 探测方式1
        tcpSocket    <Object>    # 探测方式2
        httpGet      <Object>    # 探测方式3
        initialDelaySeconds  <integer>  # 容器启动后等待多少秒执行第一次探测
        timeoutSeconds       <integer>  # 探测超时时间。默认1秒，最小1秒
        periodSeconds        <integer>  # 执行探测的频率。默认是10秒，最小1秒
        failureThreshold     <integer>  # 连续探测失败多少次才被认定为失败。默认是3。最小值是1
        successThreshold     <integer>  # 连续探测成功多少次才被认定为成功。默认是1
    ```
7. **三种探测方式：**

    上面两种探针目前均支持三种探测方式：

    - **Exec命令：**==**在容器内执行一次命令**==**，如果命令执行的退出码为0，则认为程序正常，否则不正常**

        ```Plain
         ……
           livenessProbe:
             exec:
               command:
               - cat
               - /tmp/healthy
         ……
        ```
    - **TCPSocket：将会**==**尝试访问一个用户容器的端口**==**，如果能够建立这条连接，则认为程序正常，否则不正常**

        ```Plain
         ……
           livenessProbe:
             tcpSocket:
               port: 8080
         ……
        ```
    - **HTTPGet：**==**调用容器内Web应用的URL**==**，如果返回的状态码在200和399之间，则认为程序正常，否则不正常**

        ```Plain
         ……
           livenessProbe:
             httpGet:
               path: / \#URI地址
               port: 80 \#端口号
               host: 127.0.0.1 \#主机地址
               scheme: HTTP \#支持的协议，http或者https
         ……
        ```
8. 示例一：以liveness probes为例，使用Exec方式探测
    1. 创建pod-liveness-exec.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-liveness-exec
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
             ports:
             - name: nginx-port
               containerPort: 80
             livenessProbe:
               exec:
                 command: ["/bin/cat","/tmp/hello.txt"] # 执行一个查看文件的命令（这个文件不存在，所以一定探测失败）
        ```
    2. 创建Pod

        ```Plain
         [root@master ~]# kubectl create -f pod-liveness-exec.yaml -n dev
         pod/pod-liveness-exec created
        ```
    3. 查看 Pod （发现nginx容器启动之后就进行了健康检查）

        ```Plain
         [root@master ~]# kubectl get pod -n dev
         NAME                        READY   STATUS             RESTARTS   AGE
         pod-liveness-exec           0/1     CrashLoopBackOff   0          2m48s
        ```
    4. 查看Pod详情

        ```Plain
         Events:
           Type     Reason     Age                From               Message
           ----     ------     ----               ----               -------
           Normal   Scheduled  95s                default-scheduler  Successfully assigned dev/pod-liveness-exec to node01
           Normal   Killing    14s (x3 over 74s)  kubelet            Container nginx failed liveness probe, will be restarted
           Normal   Pulled     13s (x4 over 94s)  kubelet            Container image "nginx:1.17.1" already present on machine
           Normal   Created    13s (x4 over 94s)  kubelet            Created container nginx
           Normal   Started    13s (x4 over 94s)  kubelet            Started container nginx
           Warning  Unhealthy  4s (x10 over 94s)  kubelet            Liveness probe failed: /bin/cat: /tmp/hello.txt: No such file or directory(存活探针失败：找不到文件)
        ```
    5. 稍等一会之后，再观察Pod 信息，**Pod 在不断重启**

        ```Plain
         [root@master ~]# kubectl get pod -n dev
         NAME                        READY   STATUS             RESTARTS   AGE
         pod-liveness-exec           0/1     CrashLoopBackOff   5          2m48s
        ```
9. 示例二：以liveness probes为例，使用TCPSocket方式探测
    1. 创建pod-liveness-tcpsocket.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-liveness-tcpsocket
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
             ports:
             - name: nginx-port
               containerPort: 80
             livenessProbe:
               tcpSocket:
                 port: 8080 # 尝试访问8080端口
        ```

        创建pod，观察效果

        ```Plain
         # 创建Pod
         [root@k8s-master01 ~]# kubectl create -f pod-liveness-tcpsocket.yaml
         pod/pod-liveness-tcpsocket created
         # 查看Pod详情
         [root@k8s-master01 ~]# kubectl describe pods pod-liveness-tcpsocket -n dev
         ......
           Normal   Scheduled  31s                            default-scheduler  Successfully assigned dev/pod-liveness-tcpsocket to node2
           Normal   Pulled     <invalid>                      kubelet, node2     Container image "nginx:1.17.1" already present on machine
           Normal   Created    <invalid>                      kubelet, node2     Created container nginx
           Normal   Started    <invalid>                      kubelet, node2     Started container nginx
           Warning  Unhealthy  <invalid> (x2 over <invalid>)  kubelet, node2     Liveness probe failed: dial tcp 10.244.2.44:8080: connect: connection refused
         # 观察上面的信息，发现尝试访问8080端口,但是失败了
         # 稍等一会之后，再观察pod信息，就可以看到RESTARTS不再是0，而是一直增长
         [root@k8s-master01 ~]# kubectl get pods pod-liveness-tcpsocket  -n dev
         NAME                     READY   STATUS             RESTARTS   AGE
         pod-liveness-tcpsocket   0/1     CrashLoopBackOff   2          3m19s
         # 当然接下来，可以修改成一个可以访问的端口，比如80，再试，结果就正常了......
        ```
10. 示例三：以liveness probes为例，使用HTTPGet方式探测
    1. 创建pod-liveness-httpget.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-liveness-httpget
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
             ports:
             - name: nginx-port
               containerPort: 80
             livenessProbe:
               httpGet:  # 其实就是访问http://127.0.0.1:80/hello
                 scheme: HTTP \#支持的协议，http或者https
                 port: 80 \#端口号
                 path: /hello \#URI地址
        ```

        创建pod，观察效果

        ```Plain
         # 创建Pod
         [root@k8s-master01 ~]# kubectl create -f pod-liveness-httpget.yaml
         pod/pod-liveness-httpget created
         # 查看Pod详情
         [root@k8s-master01 ~]# kubectl describe pod pod-liveness-httpget -n dev
         .......
           Normal   Pulled     6s (x3 over 64s)  kubelet, node1     Container image "nginx:1.17.1" already present on machine
           Normal   Created    6s (x3 over 64s)  kubelet, node1     Created container nginx
           Normal   Started    6s (x3 over 63s)  kubelet, node1     Started container nginx
           Warning  Unhealthy  6s (x6 over 56s)  kubelet, node1     Liveness probe failed: HTTP probe failed with statuscode: 404
           Normal   Killing    6s (x2 over 36s)  kubelet, node1     Container nginx failed liveness probe, will be restarted
         # 观察上面信息，尝试访问路径，但是未找到,出现404错误
         # 稍等一会之后，再观察pod信息，就可以看到RESTARTS不再是0，而是一直增长
         [root@k8s-master01 ~]# kubectl get pod pod-liveness-httpget -n dev
         NAME                   READY   STATUS    RESTARTS   AGE
         pod-liveness-httpget   1/1     Running   5          3m17s
         # 当然接下来，可以修改成一个可以访问的路径path，比如/，再试，结果就正常了......
        ```
# 七、重启策略
1. Pod的重启策略（RestartPolicy）应用于 Pod 内所有容器，并且仅在 Pod 所处的 Node 上由kubelet进行判断和重启操作
2. 当某个容器异常退出或者健康检查失败时，kubelet 将根据 `RestartPolicy` 的设置来进行相应的操作Pod的重启策略包括
    1. **`Always`**：当容器失效时，由 kubelet 自动重启该容器（默认策略）
    2. **`OnFailure`**：当容器异常退出（退出状态码非 0 时），由 kubelet 自动重启该容器
    3. **`Never`**：不论容器运行状态如何，kubelet 都不会重启该容器
3. 示例
    1. 创建pod-restartpolicy.yaml：

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-restartpolicy
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
             ports:
             - name: nginx-port
               containerPort: 80
             livenessProbe:
               httpGet:
                 scheme: HTTP
                 port: 80
                 path: /hello
           restartPolicy: Never # 设置重启策略为Never
        ```
    2. 创建Pod

        ```Plain
         [root@master ~]# kubectl create -f pod-restartpolicy.yaml -n dev
         pod/pod-restartpolicy created
        ```
    3. 查看 Pod

        ```Plain
         [root@master ~]# kubectl  get pods pod-restartpolicy -n dev
         NAME                READY   STATUS    RESTARTS   AGE
         pod-restartpolicy   1/1     Running   0          29s
         [root@master ~]# kubectl  get pods pod-restartpolicy -n dev
         NAME                READY   STATUS      RESTARTS   AGE
         pod-restartpolicy   0/1     Completed   0          47s
        ```
    4. 查看Pod详情，发现nginx容器失败

        ```Plain
         [root@master ~]# kubectl  describe pods pod-restartpolicy  -n dev
         Events:
           Type     Reason     Age   From               Message
           ----     ------     ----  ----               -------
           Normal   Scheduled  7s    default-scheduler  Successfully assigned dev/pod-restartpolicy to node02
           Normal   Pulled     7s    kubelet            Container image "nginx:1.17.1" already present on machine
           Normal   Created    7s    kubelet            Created container nginx
           Normal   Started    7s    kubelet            Started container nginx
           Warning  Unhealthy  0s    kubelet            Liveness probe failed: HTTP probe failed with statuscode: 404
                                                         (存活探针失败)
        ```
    5. 多等一会，再观察pod的重启次数，发现一直是0，并未重启

        ```Plain
         [root@master ~]# kubectl  get pods pod-restartpolicy -n dev
         NAME                READY   STATUS      RESTARTS   AGE
         pod-restartpolicy   0/1     Completed   0          57s
        ```
        ```Java
        try (KubernetesClient client = new DefaultKubernetesClient()) {
            Pod pod = new PodBuilder()
                    .withNewMetadata().withName("compute-pod").addToLabels("app", "compute-app") // 为Pod添加标签
                    .endMetadata().withNewSpec().addNewContainer().withName("container")
                    .withImage("nginx").endContainer().endSpec()
                    .build();
            pod = client.pods().inNamespace("default").create(pod);
            // 创建Service时，使用选择器 "compute-app" 来选择Pod
            Service service = new ServiceBuilder()
                    .withNewMetadata().withName("service").addToLabels("app", "compute-app")
                    .endMetadata().withNewSpec().withSelector(Collections.singletonMap("app", "compute-app"))
                    .addNewPort().withProtocol("TCP").withPort(80) // Service暴露的端口
                    .withTargetPort(new IntOrString(80)) // Pod内部的端口
                    .endPort().withType("ClusterIP") // 指定Service类型
                    .endSpec()
                    .build();
            service = client.services().inNamespace("default").create(service);
        }
        ```
        ```Java
        const Name = "TD3-CecEs-plugin"
        type Args struct {
        	FavoriteColor  string `json:"favorite_color,omitempty"`
        	FavoriteNumber int    `json:"favorite_number,omitempty"`
        	ThanksTo       string `json:"thanks_to,omitempty"`
        }
        type Sample struct {
        	args   *Args
        	handle framework.FrameworkHandle
        }
        func (s *Sample) Name() string {
        	return Name
        }
        func (s *Sample) Bind(pc *framework.PluginContext, pod *v1.Pod, nodeName string) *framework.Status {
        	if nodeInfo, ok := s.handle.NodeInfoSnapshot().NodeInfoMap[nodeName]; !ok {
        		return framework.NewStatus(framework.Error, fmt.Sprintf("prebind get node info error: %+v", nodeName))
        	} else {
        		Bind(pc *PluginContext, p *v1.Pod, getTD3_CecEsResult() string) *Status
        		klog.V(3).Infof("prebind node info: %+v", nodeInfo.Node())
        		return framework.NewStatus(framework.Success, "")
        	}
        }
        ```
