---
title: "Pod 调度配置"
tags:
  - "云原生"
  - "云原生/Kubernetes"
  - "云原生/Kubernetes/Pod"
  - "Pod 调度配置"
  - "yaml 配置文件操作 Pod"
  - "Kubernetes"
updated: 2026-04-16
---
# 一、Pod 调度介绍
1. 在默认情况下，一个Pod在哪个Node节点上运行，是**由Scheduler组件采用相应的算法计算出来**的，这个过程是不受人工控制的
2. 但是在实际使用中，这并不满足的需求，很多情况下，我们==想控制某些Pod到达某些指定的节点上，那么应该怎么做？==
3. kubernetes提供了**四大类调度方式**：
    - 自动调度：运行在哪个节点上完全由Scheduler经过一系列的算法计算得出
    - 定向调度：NodeName、NodeSelector
    - 亲和性调度：NodeAffinity、PodAffinity、PodAntiAffinity
    - 污点（容忍）调度：Taints、Toleration

# 二、四类调度方式
## 1. 自动 调度

由 **Scheduler 组件**采用相应的调度算法计算出来

## 2. 定向 调度
- **强制约束**
- 两种声明方式：以此==将 Pod 调度到==**==期望的 node 节点上==**
    - 在pod上声明 nodeName
    - 在pod上声明 nodeSelector

### 2.1 pod.spec.nodeName
1. `pod.spec.nodeName` 用于**强制约束**将Pod调度到**指定的Name的**Node节点上
    1. 这就意味着即使要调度的目标Node不存在，也会向上面进行调度，只不过pod运行失败而已
    2. 其实是直接跳过Scheduler的调度逻辑，直接将Pod调度到指定名称的节点
2. 示例：
    1. 创建pod-nodename.yaml文件

        ```Plain
        apiVersion: v1
        kind: Pod
        metadata:
          name: pod-nodename
          namespace: dev
        spec:
          containers:
          - name: nginx
            image: nginx:1.17.1
          nodeName: node01 # 指定调度到node01节点上
        ```
    2. 创建Pod

        ```Plain
        [root@master ~]# kubectl create -f pod-nodename.yaml -n dev
        pod/pod-nodename created
        ```
    3. 查看Pod调度到NODE属性，确实是调度到了node01节点上

        ```Plain
        [root@master ~]# kubectl get pods pod-nodename -n dev -o wide
        NAME           READY   STATUS    RESTARTS   AGE   IP               NODE     NOMINATED NODE   READINESS GATES
        pod-nodename   1/1     Running   0          7s    10.244.196.159   node01   <none>           <none>
        ```
    4. 接下来，删除pod，修改nodeName的值为node03（并没有node03节点）

        ```Plain
        [root@master ~]# kubectl delete -f pod-nodename.yaml
        pod "pod-nodename" deleted
        [root@master ~]# vim pod-nodename.yaml
        [root@master ~]# kubectl create -f pod-nodename.yaml -n dev
        pod/pod-nodename created
        ```
    5. 再次查看，发现已经向Node3节点调度，但是由于不存在node3节点，所以pod无法正常运行

        ```Plain
        [root@master ~]# kubectl get pods pod-nodename -n dev -o wide
        NAME           READY   STATUS    RESTARTS   AGE   IP       NODE     NOMINATED NODE   READINESS GATES
        pod-nodename   0/1     Pending   0          3s    <none>   node03   <none>           <none>
        ```
### 2.2 pod.spec.nodeSelector
1. `pod.spec.nodeSelector`用于将pod调度到**添加了指定标签的**node节点上
2. 它是通过kubernetes的label-selector机制实现的
    1. 在pod创建之前，会由scheduler使用MatchNodeSelector调度策略进行label匹配，找出目标node
    2. 然后将pod调度到目标节点
3. 该匹配规则是**强制约束**
4. 示例：
    1. 首先分别为node节点添加标签

        ```Plain
        [root@k8s-master01 ~]# kubectl label nodes node1 nodeenv=pro
        node/node2 labeled
        [root@k8s-master01 ~]# kubectl label nodes node2 nodeenv=test
        node/node2 labeled
        ```
    2. 创建一个pod-nodeselector.yaml文件，并使用它创建Pod

        ```Plain
        apiVersion: v1
        kind: Pod
        metadata:
          name: pod-nodeselector
          namespace: dev
        spec:
          containers:
          - name: nginx
            image: nginx:1.17.1
          nodeSelector:
            nodeenv: pro # 指定调度到具有nodeenv=pro标签的节点上
        ```
    3. 创建Pod

        ```Plain
        [root@master ~]# kubectl create -f pod-nodeselector.yaml -n dev
        pod/pod-nodeselector created
        ```
    4. 查看Pod调度到NODE属性，确实是调度到了node1节点上

        ```Plain
        [root@master ~]# kubectl get pods pod-nodeselector -n dev -o wide
        NAME               READY   STATUS    RESTARTS   AGE   IP               NODE     NOMINATED NODE   READINESS GATES
        pod-nodeselector   1/1     Running   0          11s   10.244.196.160   node01   <none>           <none>
        ```
    5. 接下来删除pod

        ```Plain
        [root@master ~]# kubectl delete -f pod-nodeselector.yaml -n dev
        pod "pod-nodeselector" deleted
        ```
    6. 修改nodeSelector的值为nodeenv: xxxx（不存在打有此标签的节点）

        ```Plain
        [root@master ~]# vim pod-nodeselector.yaml
        [root@master ~]# kubectl create -f pod-nodeselector.yaml -n dev
        pod/pod-nodeselector created
        ```
    7. 再次查看，发现pod无法正常运行（挂起状态），Node的值为none

        ```Plain
        [root@master ~]# kubectl get pods pod-nodeselector -n dev -o wide
        NAME               READY   STATUS    RESTARTS   AGE   IP       NODE     NOMINATED NODE   READINESS GATES
        pod-nodeselector   0/1     Pending   0          3s    <none>   <none>   <none>           <none>
        ```
    8. 查看详情，发现node selector匹配失败的提示

        ```Plain
        [root@master ~]# kubectl describe pods pod-nodeselector -n dev
        Events:
          Type     Reason            Age   From               Message
          ----     ------            ----  ----               -------
          Warning  FailedScheduling  19s   default-scheduler  0/3 nodes are available: 1 node(s) had taint {node-role.kubernetes.io/master: }, that the pod didn't tolerate, 2 node(s) didn't match Pod's node affinity.
          Warning  FailedScheduling  19s   default-scheduler  0/3 nodes are available: 1 node(s) had taint {node-role.kubernetes.io/master: }, that the pod didn't tolerate, 2 node(s) didn't match Pod's node affinity.
        ```
## 3. 亲和性 调度
> 💡 在 Pod 上设置
1. 定向调度存在的问题
    1. 两种定向调度的方式，使用起来非常方便
    2. 但是也有一定的问题，那就是**如果没有满足条件（node名字匹配和node标签匹配）的Node，那么Pod将不会被运行**
    3. 即使在集群中还有可用 Node 列表也不行，这就限制了它的使用场景
2. 解决方法：
    1. 基于上面的问题，kubernetes还提供了一种亲和性调度（Affinity）
    2. 它在NodeSelector的基础之上的进行了扩展，使调度更加灵活
    3. 可以通过配置的形式，实现：
        - **优先选择满足条件的Node进行调度**
        - **如果没有，也可以调度到不满足条件的节点上**
3. **`Affinity`主要分为三类：**
    - **`nodeAffinity`**（node亲和性）： 以node为目标，解决pod可以调度到哪些node的问题
    - **`podAffinity`**（pod亲和性）：以pod为目标，解决pod可以和哪些已存在的pod部署在同一个拓扑域中的问题
    - **`podAntiAffinity`**（pod反亲和性）：以pod为目标，解决pod不能和哪些已存在pod部署在同一个拓扑域中的问题
4. **关于 亲和性 和 反亲和性 使用场景的说明：**
    - **亲和性**：
        - ==如果两个应用频繁交互，那就有必要利用亲和性让两个应用的尽可能的靠近，这样可以减少因网络通信而带来的性能损耗==
        - 例如：tomcat 需要调用 mysql，故运行 tomcat 的 Pod 和 运行 mysql 的 Pod 更亲近，需要更偏向调度到同一个 node 节点
    - **反亲和性**：
        - ==当应用的采用多副本部署时，有必要采用反亲和性让各个应用实例打散分在各个node上，这样可以提高服务的高可用性==
        - 例如：运行 4 个tomcat Pod 对外提供高可用的服务，如果4个都分配在同一个node上，如果此node宕机，4个Pod全不能提供服务了；故需要尽量将4个Pod调度到4个不同的node上，以保证服务高可用

### 3.1 nodeAffinity
1. `NodeAffinity`的可配置项：
    1. 硬限制：`requiredDuringSchedulingIgnoredDuringExecution` ，Node节点**必须完全满足指定的所有规则**才可以，相当于硬限制

        ```Plain
         requiredDuringSchedulingIgnoredDuringExecution
             nodeSelectorTerms  节点选择列表
               matchFields   按节点字段列出的节点选择器要求列表
               matchExpressions   按节点标签列出的节点选择器要求列表(推荐)
                 key    键
                 values 值
                 operat or 关系符 支持Exists, DoesNotExist, In, NotIn, Gt, Lt
        ```
        - 关系符的使用说明

        ```Plain
         - matchExpressions:
           - key: nodeenv              # 匹配存在标签的key为nodeenv的节点
             operator: Exists
           - key: nodeenv              # 匹配标签的key为nodeenv,且value是"xxx"或"yyy"的节点
             operator: In
             values: ["xxx","yyy"]
           - key: nodeenv              # 匹配标签的key为nodeenv,且value大于"xxx"的节点
             operator: Gt
             values: "xxx"
        ```
    2. 软限制：`preferredDuringSchedulingIgnoredDuringExecution` ，优先调度到完全满足指定的规则的Node，**如果找不到，调度到别的node也是允许的**。相当于软限制 (倾向)

        ```Plain
         preferredDuringSchedulingIgnoredDuringExecution
             preference   一个节点选择器项，与相应的权重相关联
               matchFields   按节点字段列出的节点选择器要求列表
               matchExpressions   按节点标签列出的节点选择器要求列表(推荐)
                 key    键
                 values 值
                 operator 关系符 支持In, NotIn, Exists, DoesNotExist, Gt, Lt
             weight 倾向权重，在范围1-100。
        ```
        - 软限制多一个 weight 倾向权重：更倾向哪个 node
2. NodeAffinity规则设置的注意事项：
    - 如果同时定义了nodeSelector和nodeAffinity，那么必须两个条件都得到满足，Pod才能运行在指定的Node上
    - 如果nodeAffinity指定了多个nodeSelectorTerms，那么只需要其中一个能够匹配成功即可
    - 如果一个nodeSelectorTerms中有多个matchExpressions ，则一个节点必须满足所有的才能匹配成功
    - 如果一个pod所在的Node在Pod运行期间其标签发生了改变，不再符合该Pod的节点亲和性需求，则系统将忽略此变化
3. 示例一：使用matchExpressions，做硬限制，values 中必须有匹配的
    1. 创建pod-nodeaffinity-required.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-nodeaffinity-required
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
           affinity:  \#亲和性设置
             nodeAffinity: \#设置node亲和性
               requiredDuringSchedulingIgnoredDuringExecution: # 硬限制
                 nodeSelectorTerms:
                 - matchExpressions: # 匹配env的值在["xxx","yyy"]中的标签
                   - key: nodeenv
                     operator: In
                     values: ["xxx","yyy"]
        ```
    2. 查看当前 node 的 label（此时 node01 有标签 `nodeenv=pro`）

        ```Plain
         [root@master ~]# kubectl get nodes --show-labels
         NAME     STATUS   ROLES                  AGE   VERSION   LABELS
         master   Ready    control-plane,master   8d    v1.20.9   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=master,kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=,node-role.kubernetes.io/master=
         node01   Ready    <none>                 8d    v1.20.9   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=node01,kubernetes.io/os=linux,nodeenv=pro
         node02   Ready    <none>                 8d    v1.20.9   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=node02,kubernetes.io/os=linux,nodeenv=test
        ```
    3. 创建pod

        ```Plain
         [root@master ~]#  kubectl create -f pod-nodeaffinity-required.yaml -n dev
         pod/pod-nodeaffinity-required created
        ```
    4. 查看pod状态 （运行失败）

        ```Plain
         [root@master ~]# kubectl get pods pod-nodeaffinity-required -n dev -o wide
         NAME                        READY   STATUS    RESTARTS   AGE   IP       NODE     NOMINATED NODE   READINESS GATES
         pod-nodeaffinity-required   0/1     Pending   0          6s    <none>   <none>   <none>           <none>
        ```
    5. 查看Pod的详情（发现调度失败，提示node选择失败）

        ```Plain
         [root@master ~]# kubectl describe pod pod-nodeaffinity-required -n dev
         Events:
           Type     Reason            Age   From               Message
           ----     ------            ----  ----               -------
           Warning  FailedScheduling  14s   default-scheduler  0/3 nodes are available: 1 node(s) had taint {node-role.kubernetes.io/master: }, that the pod didn't tolerate, 2 node(s) didn't match Pod's node affinity.
           Warning  FailedScheduling  13s   default-scheduler  0/3 nodes are available: 1 node(s) had taint {node-role.kubernetes.io/master: }, that the pod didn't tolerate, 2 node(s) didn't match Pod's node affinity.
        ```
    6. 删除pod

        ```Plain
         [root@master ~]# kubectl delete -f pod-nodeaffinity-required.yaml
         pod "pod-nodeaffinity-required" deleted
        ```
    7. 修改文件，将`values: ["xxx","yyy"]`-----> `["pro","yyy"]`

        此时可以匹配标签了

        ```Plain
         [root@master ~]# vim pod-nodeaffinity-required.yaml
        ```
    8. 再次启动pod

        ```Plain
         [root@master ~]#  kubectl create -f pod-nodeaffinity-required.yaml -n dev
         pod/pod-nodeaffinity-required created
        ```
    9. 此时查看，发现调度成功，已经将pod调度到了node1上

        ```Plain
         [root@master ~]# kubectl get pods pod-nodeaffinity-required -n dev -o wide
         NAME                        READY   STATUS    RESTARTS   AGE   IP               NODE     NOMINATED NODE   READINESS GATES
         pod-nodeaffinity-required   1/1     Running   0          2s    10.244.196.161   node01   <none>           <none>
        ```
4. 示例二：使用matchExpressions，做软限制：values中可以不匹配
    1. 创建pod-nodeaffinity-required.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-nodeaffinity-preferred
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
           affinity:  \#亲和性设置
             nodeAffinity: \#设置node亲和性
               preferredDuringSchedulingIgnoredDuringExecution: # 软限制
               - weight: 1
                 preference:
                   matchExpressions: # 匹配env的值在["xxx","yyy"]中的标签(当前环境没有)
                   - key: nodeenv
                     operator: In
                     values: ["xxx","yyy"]
        ```
    2. 创建 Pod

        ```Plain
         [root@master ~]# kubectl create -f pod-nodeaffinity-preferred.yaml -n dev
         pod/pod-nodeaffinity-preferred created
        ```
    3. 查看 Pod（运行成功）

        ```Plain
         [root@master ~]# kubectl get pod pod-nodeaffinity-preferred -n dev
         NAME                         READY   STATUS    RESTARTS   AGE
         pod-nodeaffinity-preferred   1/1     Running   0          7s
        ```
### 3.2 podAffinity
1. PodAffinity 主要实现以运行的Pod为参照，实现让新创建的Pod跟参照pod在一个区域的功能
2. podAffinity 也分为 硬限制 和 软限制
    1. `requiredDuringSchedulingIgnoredDuringExecution`

        ```Plain
         requiredDuringSchedulingIgnoredDuringExecution  硬限制
             namespaces       指定参照pod的namespace
             topologyKey      指定调度作用域
             labelSelector    标签选择器
               matchExpressions  按节点标签列出的节点选择器要求列表(推荐)
                 key    键
                 values 值
                 operator 关系符 支持In, NotIn, Exists, DoesNotExist.
               matchLabels    指多个matchExpressions映射的内容
        ```
    2. `preferredDuringSchedulingIgnoredDuringExecution`

        ```Plain
         preferredDuringSchedulingIgnoredDuringExecution 软限制
             podAffinityTerm  选项
               namespaces
               topologyKey
               labelSelector
                 matchExpressions
                   key    键
                   values 值
                   operator
                 matchLabels
             weight 倾向权重，在范围1-100
        ```
        - topologyKey用于指定调度时作用域，例如:
            1. 如果指定为kubernetes.io/hostname，那就是以Node节点为区分范围
            2. 如果指定为beta.kubernetes.io/os,则以Node节点的操作系统类型来区分
3. 示例：
    1. 使用matchExpressions，做硬限制
    2. 被调度的 pod 会被调度到与本pod规定的 `values[]` 相匹配的 pod 的所在node上
    3. 先创建一个参照Pod，pod-podaffinity-target.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-podaffinity-target
           namespace: dev
           labels:
             podenv: pro # ⭐设置标签
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
           nodeName: node01 # 将目标pod名确指定到node01上
        ```
    4. 启动目标参照Pod

        ```Plain
         [root@master ~]# kubectl create -f pod-podaffinity-target.yaml -n dev
         pod/pod-podaffinity-target created
        ```
    5. 查看参照Pod状况

        ```Plain
         [root@master ~]# kubectl get pods  pod-podaffinity-target -n dev
         NAME                     READY   STATUS    RESTARTS   AGE
         pod-podaffinity-target   1/1     Running   0          4s
        ```
    6. 创建pod-podaffinity-required.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-podaffinity-required
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
           affinity:  \#亲和性设置
             podAffinity: \#设置pod亲和性
               requiredDuringSchedulingIgnoredDuringExecution: # 硬限制
               - labelSelector:
                   matchExpressions: # 匹配env的值在["xxx","yyy"]中的标签
                   - key: podenv
                     operator: In
                     values: ["xxx","yyy"] ⭐
                 topologyKey: kubernetes.io/hostname
        ```
    7. 启动pod

        ```Plain
         [root@master ~]# kubectl create -f pod-podaffinity-required.yaml -n dev
         pod/pod-podaffinity-required created
        ```
    8. 查看pod状态，发现未运行

        ```Plain
         [root@master ~]# kubectl get pods pod-podaffinity-required -n dev
         NAME                       READY   STATUS    RESTARTS   AGE
         pod-podaffinity-required   0/1     Pending   0          45s
        ```
    9. 查看详细信息

        ```Plain
         [root@master ~]# kubectl describe pods pod-podaffinity-required -n dev
         Events:
           Type     Reason            Age   From               Message
           ----     ------            ----  ----               -------
           Warning  FailedScheduling  58s   default-scheduler  0/3 nodes are available: 1 node(s) had taint {node-role.kubernetes.io/master: }, that the pod didn't tolerate, 2 node(s) didn't match pod affinity rules, 2 node(s) didn't match pod affinity/anti-affinity.
           Warning  FailedScheduling  58s   default-scheduler  0/3 nodes are available: 1 node(s) had taint {node-role.kubernetes.io/master: }, that the pod didn't tolerate, 2 node(s) didn't match pod affinity rules, 2 node(s) didn't match pod affinity/anti-affinity.
        ```
    10. 接下来修改 `values: ["xxx","yyy"]----->values:["pro","yyy"]`

        ```Plain
         [root@master ~]# kubectl delete -f pod-podaffinity-required.yaml -n dev
         pod "pod-podaffinity-required" deleted
         [root@master ~]# vim pod-podaffinity-required.yaml
        ```
    11. 然后重新创建pod，查看效果

        ```Plain
         [root@master ~]# kubectl create -f pod-podaffinity-required.yaml -n dev
         pod/pod-podaffinity-required created
        ```
    12. 发现此时Pod运行正常**（被调度到 node 01 所在的 node01 节点上）**

        ```Plain
         [root@master ~]# kubectl get pods pod-podaffinity-required -n dev -o wide
         NAME                       READY   STATUS    RESTARTS   AGE   IP               NODE     NOMINATED NODE   READINESS GATES
         pod-podaffinity-required   1/1     Running   0          15s   10.244.196.163   node01   <none>           <none>
        ```
### 3.3 podAntiAffinity
1. PodAntiAffinity主要实现以运行的Pod为参照，让新创建的Pod跟参照pod不在一个区域中的功能
2. 它的配置方式和选项跟PodAffinty是一样的，只是**效果和PodAffinty完全相反**
3. 示例：
    1. 继续使用上个案例中的参照pod

        ```Plain
         [root@master ~]# kubectl get pods  pod-podaffinity-target -n dev -o wide
         NAME                     READY   STATUS    RESTARTS   AGE     IP               NODE     NOMINATED NODE   READINESS GATES
         pod-podaffinity-target   1/1     Running   0          7m38s   10.244.196.162   node01   <none>           <none>
        ```
    2. 创建pod-podantiaffinity-required.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-podantiaffinity-required
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
           affinity:  \#亲和性设置
             podAntiAffinity: \#设置pod亲和性
               requiredDuringSchedulingIgnoredDuringExecution: # 硬限制
               - labelSelector:
                   matchExpressions: # 匹配podenv的值在["pro"]中的标签
                   - key: podenv
                     operator: In
                     values: ["pro"]  # ⭐与带有podenv:pro 标签的pod排斥
                 topologyKey: kubernetes.io/hostname
        ```
    3. 创建pod

        ```Plain
         [root@master ~]# kubectl create -f pod-podantiaffinity-required.yaml -n dev
         pod/pod-podantiaffinity-required created
        ```
    4. 查看pod**（与参照node排斥，所以被调度到了node2上）**

        ```Plain
         [root@master ~]# kubectl get pods pod-podantiaffinity-required -n dev -o wide
         NAME                           READY   STATUS    RESTARTS   AGE   IP              NODE     NOMINATED NODE   READINESS GATES
         pod-podantiaffinity-required   1/1     Running   0          4s    10.244.140.95   node02   <none>           <none>
        ```
## 4. 污点-容忍 调度
> 💡 在 node 节点上设置
>
> 1. 前面的调度方式都是站在Pod的角度上，通过在Pod上添加属性，来确定Pod是否要调度到指定的Node上
>
> 2. ==也可以站在====**Node的角度上**====，通过在Node上添加====**污点**====属性，来决定是否允许Pod调度过来==
### 4.1 污点
1. Node 被设置上污点之后就和 Pod 之间存在了一种相斥的关系，进而拒绝Pod调度进来，甚至可以将已经存在的Pod驱逐出去
2. 默认就会给 master 节点添加一个污点标记，因此pod就不会调度到master节点上
3. 污点的格式为：`key=value:effect`
    1. key和value是污点的标签
    2. effect描述污点的作用，支持如下三个选项
        1. **`PreferNoSchedule`**：
            1. 尽量不要来，除非没办法
            2. kubernetes将尽量避免把Pod调度到具有该污点的Node上，除非没有其他节点可调度
        2. **`NoSchedule`**：
            1. 新的不要来，在这的就别动了
            2. kubernetes将不会把Pod调度到具有该污点的Node上，但不会影响当前Node上已存在的Pod
        3. **`NoExecute`**：
            1. 新的不要来，在这的也赶紧走
            2. kubernetes将不会把Pod调度到具有该污点的Node上，同时也会将Node上已存在的Pod驱离
    3. 命令示例

        ```Plain
         # 设置污点
         kubectl taint nodes node1 key=value:effect
         # 去除污点
         kubectl taint nodes node1 key:effect-
         # 去除所有污点
         kubectl taint nodes node1 key-
        ```
4. 示例：
    - 准备节点node01（为了演示效果更加明显，暂时停止node02节点）

        ```Plain
         [root@master ~]# kubectl get nodes
         NAME     STATUS     ROLES                  AGE   VERSION
         master   Ready      control-plane,master   8d    v1.20.9
         node01   Ready      <none>                 8d    v1.20.9
         node02   NotReady   <none>                 8d    v1.20.9
        ```
    - 为node1节点设置一个污点： `tag=heima:PreferNoSchedule`；然后创建pod1

        （预计结果：pod1 正常 ）

    - 修改为node1节点设置一个污点： `tag=heima:NoSchedule`；然后创建pod2（预计结果：pod1 正常 pod2 失败 ）
    - 修改为node1节点设置一个污点： `tag=heima:NoExecute`；然后创建pod3 （预计结果：3个pod都失败 ）
    1. 为node1设置污点（PreferNoSchedule）

        ```Plain
         [root@master ~]# kubectl taint nodes node01 tag=heima:PreferNoSchedule
         node/node01 tainted
        ```
    2. 创建pod1

        ```Plain
         [root@master ~]# kubectl run taint1 --image=nginx:1.17.1 -n dev
         pod/taint1 created
        ```
    3. 查看

        ```Plain
         # pod1 正常
         [root@master ~]# kubectl get pods taint1 -n dev -o wide
         NAME     READY   STATUS    RESTARTS   AGE   IP               NODE     NOMINATED NODE   READINESS GATES
         taint1   1/1     Running   0          5s    10.244.196.164   node01   <none>           <none>
        ```
    4. 为node1设置污点（取消PreferNoSchedule，设置NoSchedule）

        ```Plain
         [root@master ~]# kubectl taint nodes node01 tag:PreferNoSchedule-
         node/node01 untainted
         [root@master ~]# kubectl taint nodes node01 tag=heima:NoSchedule
         node/node01 tainted
        ```
    5. 创建pod2

        ```Plain
         [root@master ~]# kubectl run taint2 --image=nginx:1.17.1 -n dev
         pod/taint2 created
        ```
    6. 查看

        ```Plain
         # pod1 正常
         [root@master ~]# kubectl get pods taint1 -n dev -o wide
         NAME     READY   STATUS    RESTARTS   AGE   IP               NODE     NOMINATED NODE   READINESS GATES
         taint1   1/1     Running   0          49s   10.244.196.164   node01   <none>           <none>
         # # pod2 被挂起
         [root@master ~]# kubectl get pods taint2 -n dev -o wide
         NAME     READY   STATUS    RESTARTS   AGE   IP       NODE     NOMINATED NODE   READINESS GATES
         taint2   0/1     Pending   0          4s    <none>   <none>   <none>           <none>
        ```
    7. 为node1设置污点（取消NoSchedule，设置NoExecute）

        ```Plain
         [root@master ~]# kubectl taint nodes node01 tag:NoSchedule-
         node/node01 untainted
         [root@master ~]# kubectl taint nodes node01 tag=heima:NoExecute
         node/node01 tainted
        ```
    8. 创建pod3

        ```Plain
         [root@master ~]# kubectl run taint3 --image=nginx:1.17.1 -n dev
         pod/taint3 created
        ```
    9. 查看

        ```Plain
         # pod1 pod2 被删了。。。
         [root@master ~]# kubectl get pods taint1 -n dev -o wide
         Error from server (NotFound): pods "taint1" not found
         [root@master ~]# kubectl get pods taint2 -n dev -o wide
         Error from server (NotFound): pods "taint2" not found
         # pod3 被挂起
         [root@master ~]# kubectl get pods taint3 -n dev -o wide
         NAME     READY   STATUS    RESTARTS   AGE   IP       NODE     NOMINATED NODE   READINESS GATES
         taint3   0/1     Pending   0          26s   <none>   <none>   <none>           <none>
        ```
### 4.2 容忍
1. 污点的作用：可以在node上添加污点用于拒绝pod调度上来
2. 但是如果==**就是想将一个pod调度到一个有污点的node上去**==，这时候应该怎么做呢
3. 要使用到**容忍**
    1. ==污点就是拒绝，容忍就是忽略==
    2. Node通过污点拒绝pod调度上去，但是 Pod 通过容忍忽略Node的拒绝
4. 容忍的详细配置

    ```Plain
     [root@k8s-master01 ~]# kubectl explain pod.spec.tolerations
     ......
     FIELDS:
        key       # 对应着要容忍的污点的键，空意味着匹配所有的键
        value     # 对应着要容忍的污点的值
        operator  # key-value的运算符，支持Equal和Exists（默认）
        effect    # 对应污点的effect，空意味着匹配所有影响
        tolerationSeconds   # 容忍时间, 当effect为NoExecute时生效，表示pod在Node上的停留时间
    ```
5. 示例：
    - 上面已经在node1节点上打上了`NoExecute`的污点，此时pod是调度不上去的
    - 本示例中，可以通过给pod添加对`NoExecute`污点的容忍，然后将其调度上去
    1. 先不加容忍：创建pod-toleration.yaml

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-toleration
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
        ```
    2. 创建 Pod

        ```Plain
         [root@master ~]# kubectl create -f pod-toleration.yaml -n dev
         pod/pod-toleration created
        ```
    3. 查看 Pod 被挂起

        ```Plain
         [root@master ~]# kubectl get pod pod-toleration -n dev
         NAME             READY   STATUS    RESTARTS   AGE
         pod-toleration   0/1     Pending   0          23s
        ```
    4. 删除 Pod

        ```Plain
         [root@master ~]# kubectl delete pod pod-toleration -n dev
         pod "pod-toleration" deleted
        ```
    5. 修改 yaml 文件，添加容忍

        ```Plain
         apiVersion: v1
         kind: Pod
         metadata:
           name: pod-toleration
           namespace: dev
         spec:
           containers:
           - name: nginx
             image: nginx:1.17.1
           tolerations:      # 添加容忍
           - key: "tag"        # 要容忍的污点的key
             operator: "Equal" # 操作符
             value: "heima"    # 容忍的污点的value
             effect: "NoExecute"   # 添加容忍的规则，这里必须和标记的污点规则相同
        ```
    6. 查看 Pod 运行正常

        ```Plain
         [root@master ~]# kubectl create -f pod-toleration.yaml -n dev
         pod/pod-toleration created
         [root@master ~]# kubectl get pod pod-toleration -n dev
         NAME             READY   STATUS    RESTARTS   AGE
        ```
