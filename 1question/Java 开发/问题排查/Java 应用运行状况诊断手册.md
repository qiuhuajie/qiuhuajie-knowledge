---
title: Java 应用运行状况诊断手册
aliases:
  - Java 运行状况诊断手册
  - Java 应用排障手册
tags:
  - Java
  - Java/问题排查
  - Java/JVM
  - Linux
  - 性能诊断
updated: 2026-06-16
---
> 1. Java 应用排障最怕的不是命令不会背，而是没有排查顺序。这个手册的核心目标不是罗列命令，而是建立一个统一判断框架：先判断问题属于 CPU 忙、IO 慢、线程阻塞、GC 异常、连接池耗尽还是内存泄漏，再选择对应的系统命令和 JDK 工具。
> 2. 当问题已经发展成全局 504、Full GC 频繁、CPU 飙高或 Metaspace 使用率异常时，这个手册可以作为总入口；而更具体的主题则分别落到线程池、数据库连接池、GC 和 JVM 内存结构等专题笔记中。

# 一、我的整理
## 1. 一句话结论
* 排障效率高低，不取决于会不会 `top`、`jstack`、`jmap`，而取决于你能不能先判断“系统是忙死了，还是卡死了”。

## 2. 这份手册的使用方式
1. 先用系统指标判断大方向，例如 CPU、Load、内存、IO、网络是否异常。
2. 再进入 Java 进程内部，用 `top -Hp`、`jstack`、`jstat`、`jmap` 去验证线程、GC、堆、类加载器是否异常。
3. 如果故障已经表现为全局 504，还要把 [[4.1 反向代理|反向代理]]、[[ThreadPoolExecutor|线程池]]、[[5.2 数据库连接池|连接池]] 和数据库慢 SQL 一起纳入排查链路。

# 二、关联笔记
* [[应用机器核心指标详解]]
* [[线程池打满全局 504]]
* [[ThreadPoolExecutor]]
* [[5.2 数据库连接池]]
* [[13.1 SQL 性能分析]]
* [[13.4 连接配置优化]]
* [[G1 垃圾回收器]]
* [[3.6 垃圾回收调优]]
* [[2.4 堆]]
* [[2.2 虚拟机栈]]
* [[2 5 方法区/方法区介绍]]
* [[4.1 反向代理]]

# 三、先建立总判断框架
## 1. 为什么排障不能一上来就抓 Jstack
* 很多排障动作本身就有成本，比如线上频繁抓线程快照、导出堆、做 `jmap -histo:live` 都会影响业务。
* 因此最好的顺序是：先用低成本指标判断方向，再用高成本工具做验证。

## 2. 先把问题分成哪几类
* 常见故障大致可以分成下面几类：

| 故障类型 | 典型表现 | 先看什么 |
|------|------|------|
| CPU 忙死型 | CPU 高、Load 高 | `top`、`top -Hp`、`vmstat` |
| IO / 网络等待型 | CPU 不高、Load 可能高、`wa` 升高 | `vmstat`、`pidstat -d`、网络指标 |
| 线程阻塞型 | CPU 不高、吞吐掉到接近 0、全局超时 | `jstack`、线程池状态 |
| GC 异常型 | RT 抖动、停顿长、FGC 增长 | `jstat -gcutil`、GC 日志 |
| 内存异常型 | RSS 高、堆高、Metaspace 高 | `free -h`、`jmap -heap`、`jstat` |
| 数据库瓶颈型 | RT 上升、连接池等待、慢 SQL 多 | 连接池指标、慢日志、`EXPLAIN` |

## 3. 最值得先问的四个问题
1. CPU 是高还是低。
2. 吞吐量是“变慢了”还是“几乎没了”。
3. 线程是在跑代码，还是在等资源。
4. 问题发生在系统层、JVM 层，还是数据库 / 网络 / 反向代理层。

# 四、系统层诊断
## 1. `top`：先看全局健康度
* `top` 是排障的第一入口，用来快速判断 CPU、Load、内存是否在健康区间。

```bash
top
top -bn1 | head -5
```
* 输出里最该先看的字段是：

| 字段 | 含义 | 判断重点 |
|------|------|------|
| `us` | 用户态 CPU | 业务代码是否在吃 CPU |
| `sy` | 内核态 CPU | 系统调用、锁争抢、上下文切换是否高 |
| `id` | 空闲率 | 是否还有 CPU 裕量 |
| `wa` | IO 等待 | 是否在等磁盘或网络 |
| `avail Mem` | 可用内存 | 比 `free` 更有价值 |
![[IMG-20260617205537011.png|621]]

* 这里要注意一个常见误区：`free` 很小不一定危险，Linux 会把空闲内存拿去做缓存，真正该看的是 `available`。

## 2. `uptime`：快速判断 Load 趋势
```bash
uptime  // load 情况
nproc // CPU核心数
```
* `uptime` 里的 `load average` 是 1、5、15 分钟的平均负载。
	![[IMG-20260617205537142.png|650]]
* 负载不是纯 CPU 使用率，而是“正在使用 CPU + 等待 CPU + 等待 IO”的任务数。

| Load 与核数关系 | 状态 |
|------|------|
| Load < 核数 | 正常 |
| Load ≈ 核数 | 满载 |
| Load > 核数 | 开始排队 |
| Load > 核数 * 2 | 严重过载 |

* 如果 `load1 > load5 > load15`，说明压力正在上升。
* 如果 CPU 不高但 Load 偏高，要优先怀疑 IO 等待或资源阻塞。

## 3. `free -h`：判断是不是内存不够
```bash
free -h
```
* 内存相关字段里最重要的是：

| 字段 | 含义 |
|------|------|
| `used` | 已用内存 |
| `free` | 完全空闲内存 |
| `buff/cache` | 可回收缓存 |
| `available` | 实际可用内存 |
![[IMG-20260617205537243.png|625]]

* 判断标准通常更建议看 `available` 占比：

| available 占比 | 状态 |
|------|------|
| > 20% | 正常 |
| 10% ~ 20% | 关注 |
| < 10% | 危险 |

* 如果 Swap 开始被使用，说明物理内存已经明显吃紧。

## 4. `vmstat`：看 CPU、IO、上下文切换是不是异常
```bash
vmstat 2 10
```
* `vmstat` 的几个关键字段：

| 字段 | 含义 | 常见判断 |
|------|------|------|
| `r` | 等待运行的线程数 | 持续大于核数说明 CPU 不够 |
| `b` | 不可中断阻塞线程数 | 持续大于 0 说明 IO 或外部资源在卡 |
| `cs` | 每秒上下文切换数 | 突增常见于线程过多或锁争抢 |
| `wa` | IO 等待 | 高说明磁盘或网络慢 |
![[IMG-20260617205537294.png|603]]

* 如果 `cs` 很高但 CPU 也不高，往往意味着系统在做大量无效切换，而不是有效计算。

## 5. `mpstat` 和 `pidstat`：确认是不是局部热点
```bash
mpstat -P ALL 2
pidstat -u 2
pidstat -r 2
pidstat -d 2
pidstat -t -u 2
```
* `mpstat` 适合看是不是某几个核被单线程任务打满。
* `pidstat` 适合看某个进程的 CPU、内存、IO 使用趋势，比 `top` 更适合持续观察。

## 6. `ps`：看谁占内存最多
```bash
ps -eo pid,rss,comm --sort=-rss | head -10
```

![[IMG-20260617205537360.png|617]]

* `RSS` 表示实际占用的物理内存。
* 当宿主机内存高时，先用它确认到底是不是 Java 进程在吃内存，再决定是否继续做 JVM 内部分析。

# 五、Java 进程与线程诊断
## 1. 先找到正确的 Java PID
```bash
jps -l
```

![[IMG-20260617205537410.png|508]]

* `jps -l` 用来定位 Java 进程 PID 和主类名。
* 注意一些容器或 Pandora Boot 场景里，`top` 看到的 PID 和业务主类不一定一眼对应，要小心过滤。

## 2. `top -Hp` + `jstack`：排查 CPU 高线程
1. 当 Java 进程 CPU 高时，优先这样查：
    ```bash
    top -Hp <pid>
    printf 'nid=0x%x\n' <tid>
    jstack <pid> | grep -A 15 'nid=0x<hex_tid>'
    ```
2. 这个套路的核心是：
    1. 先在系统层定位哪个线程最耗 CPU。
        ![[IMG-20260617205537448.png|618]]
    2. 再把线程 ID 转成 16 进制。
        ![[IMG-20260617205537502.png|641]]
    3. 最后在 `jstack` 里定位这个线程到底在跑什么代码。
        ![[IMG-20260617205537597.png|891]]
## 3. `jstack`：看线程到底是在跑还是在等
```bash
jstack <pid>
jstack -l <pid>
jstack -F <pid>
jcmd <pid> Thread.print
kill -3 <pid>
```

![[IMG-20260617205537671.png|754]]

* `jstack` 是线程问题排查的核心工具。
* 常见线程状态需要这样理解：

| 状态 | 含义 | 常见场景 |
|------|------|------|
| `RUNNABLE` | 正在运行或可运行 | 在执行业务代码、GC、网络 IO |
| `WAITING` | 无限等待 | 线程池空闲、等待条件唤醒 |
| `TIMED_WAITING` | 限时等待 | sleep、超时等待、连接等待 |
| `BLOCKED` | 等待进入同步块 | 锁竞争严重 |

* 这里有一个很重要的判断：
    1. 如果 CPU 高且大量线程 `RUNNABLE`，系统大概率在忙。
    2. 如果 CPU 不高但大量线程 `WAITING` 或 `BLOCKED`，系统大概率在卡。
* 但是 jstack 直接输出的线程信息很多
	1. 第一步：看线程池分布——哪类线程最多
		```bash
		jstack <pid> | grep -oP '"[^"]*"' | sed 's/-[0-9]*"/"/g' | sort | uniq -c | sort -rn | head -20
		```

		![[IMG-20260617205537704.png|723]]

	2. 第二步：看线程状态分布——大部分在干嘛
		```bash
		jstack <pid> | grep 'java.lang.Thread.State' | sort | uniq -c | sort -rn
		```

		![[IMG-20260617205537793.png|656]]

		输出示例及含义：

		![[IMG-20260617205537837.png|592]]

	3. 第三步：定向看有问题的线程
		1. 看 BLOCKED 的线程都在等什么锁
			```bash
			jstack  <pid> | grep -B 1 -A 15 'BLOCKED'
			```
		2. 看某个线程池都在干什么
			```bash
			jstack <pid> | grep -A 15 'HSFBizProcessor'
			```
		3. 检查有没有死锁（jstack 会自动检测，在输出末尾）
			```bash
			jstack <pid> | tail -20
			```
## 4. 用线程池视角看问题
* 在 Java Web / RPC 应用里，线程问题往往不是“某个线程有问题”，而是“某个线程池被占满了”。
* 因此除了看单线程，还要看线程池分布和状态：

```bash
# 按线程池名分组计数，看哪类线程最多
jstack <pid> | grep -oP '"[^"]*"' | sed 's/-[0-9]*"/"/g' | sort | uniq -c | sort -rn | head -20

# 统计所有线程的状态分布，看整体在干嘛（WAITING/BLOCKED/RUNNABLE
jstack <pid> | grep 'java.lang.Thread.State' | sort | uniq -c | sort -rn

# 单看 Tomcat HTTP 线程池的状态分布
jstack <pid> | grep -A 3 'http-nio-7001-exec' | grep 'State' | sort | uniq -c

# 单看 HSF RPC 线程池的状态分布
jstack <pid> | grep -A 3 'HSFBizProcessor-DEFAULT' | grep 'State' | sort | uniq -c
```
* 这些结果通常和 [[ThreadPoolExecutor]]、Tomcat 公共线程池、RPC 公共线程池的配置一起看才有意义。

# 六、JVM 与 GC 诊断
## 1. `jstat -gcutil`：最适合看 GC 趋势
```bash
jstat -gcutil <pid> 1000 10
```
* 常见字段含义：

| 字段           | 含义                | 重点关注       |
| ------------ | ----------------- | ---------- |
| `E`          | Eden 使用率          | 是否很快打满     |
| `O`          | Old 使用率           | 是否长期高位     |
| `M`          | Metaspace 使用率     | 是否接近上限     |
| `YGC / YGCT` | Young GC 次数 / 总耗时 | 平均单次耗时是否偏高 |
| `FGC / FGCT` | Full GC 次数 / 总耗时  | 是否在持续增长    |

* 这里最实用的判断是：
    1. Young GC 多不一定有问题，要看单次耗时。
    2. Full GC 持续增长，基本一定有问题。
    3. G1 在 JDK 8 下的 Full GC 尤其要警惕，因为停顿通常很长，这部分可以结合 [[G1 垃圾回收器]] 和 [[3.6 垃圾回收调优]] 一起看。

## 2. `jmap -heap`：看堆配置和各区占用
```bash
jmap -heap <pid>
```
* `jmap -heap` 可以回答两个问题：
    1. JVM 实际跑起来的堆、Metaspace、Region 参数到底是什么。
    2. 当前各内存区域到底用了多少。
* 在概念上可以和这些笔记互相参照：
    * 堆的结构看 [[2.4 堆]]
    * 线程栈看 [[2.2 虚拟机栈]]
    * Metaspace / 方法区看 [[2 5 方法区/方法区介绍]]

## 3. `jstat -gcmetacapacity` + `jstat -class`：判断 Metaspace 是高还是泄漏
```bash
jstat -gcmetacapacity <pid> 2000 10
jstat -class <pid>
```
* Metaspace 使用率高，不能直接等于泄漏。
* 正确判断方式是：
    1. 看 `MC` 是否持续增长。
    2. 看 `Loaded` 是否持续增长、`Unloaded` 是否很少。
    3. 再决定是否继续查类加载器。

## 4. `jmap -clstats`：查哪个类加载器在吃 Metaspace
```bash
jmap -clstats <pid>
```
* 如果某个 `ClassLoader` 加载了异常多的类，才有泄漏嫌疑。
* 常见的大量 `DelegatingClassLoader` 如果是零散、短命、可卸载的，不一定有问题。

## 5. `jmap -histo` 和 `jmap -dump`：内存泄漏才继续往下走
```bash
jmap -histo <pid> | head -30
jmap -dump:format=b,file=/tmp/heap.hprof <pid>
```
* `jmap -histo:live` 会触发 Full GC，线上慎用。
* 如果只是想看运行趋势，优先用 `jstat` 和 `jmap -heap`；只有当你已经高度怀疑内存泄漏时，才值得导出堆。

## 6. `jcmd`：辅助工具位
```bash
jcmd <pid> help
jcmd <pid> Thread.print
jcmd <pid> VM.flags
jcmd <pid> VM.native_memory summary
```
* `jcmd` 可以作为 `jstack` 和 `jmap` 的补充。
* 其中 `VM.native_memory summary` 只有在启动时加了 `-XX:NativeMemoryTracking=summary` 才能用。

# 七、线程池、连接池与 504 的联动诊断
## 1. 为什么这一类问题要单独拎出来
* Java 应用很多“看起来像 CPU 或 GC 的问题”，最后其实都落在共享资源争抢上。
* 最常见的两个共享资源就是：
    1. [[ThreadPoolExecutor|线程池]]
    2. [[5.2 数据库连接池|数据库连接池]]

## 2. 一个通用判断链路
* 当你看到“CPU 不高，但全局 RT 上升 / 504 激增”时，可以按下面这条链路查：

```text
入口超时 / 504
-> 公共线程池是否被占满
-> 线程是否卡在 getConnection
-> 数据库连接池是否等待
-> 是否存在慢 SQL
-> 是否触发上游重试放大
```
## 3. 线程池和连接池为什么要一起看
* 线程池控制“能同时处理多少请求”。
* 连接池控制“能同时做多少数据库访问”。
* 如果线程池远大于连接池，而慢 SQL 又持续存在，就会出现大量线程排队等待连接，最终把入口线程池也拖死。
* 这在 [[线程池打满全局 504]] 里已经是一个完整案例。

## 4. 数据库排查动作应该怎么接
* 当确认线程卡在连接获取或数据库访问后，后续动作要转到数据库方向：
    * [[13.1 SQL 性能分析]]
    * [[13.4 连接配置优化]]
    * 具体 SQL 优化或索引问题再继续看相关 MySQL 笔记

# 八、故障现场保留
## 1. 为什么重启前一定要先留现场
* 一旦重启，进程态线程信息、`/proc` 状态、当时的线程堆栈都会消失。
* 重启可以恢复业务，但会让排障证据大幅丢失。

## 2. 最小现场保留命令集
```bash
pid=$(jps -l | grep -v Jps | awk '{print $1}')
ts=$(date +%s)
jstack $pid > /tmp/jstack_${ts}.log
jstat -gcutil $pid 1000 10 > /tmp/jstat_${ts}.log
top -bn1 -Hp $pid > /tmp/top_threads_${ts}.log
```
## 3. 重启后还能补看的内容
* GC 日志
* 监控平台历史数据
* 系统日志
* 数据库慢日志和执行计划

# 九、排查 SOP
## 1. 场景一：CPU 飙高
1. `top -bn1 | head -5` 先确认整体 CPU 是否异常。
2. `top -Hp <pid>` 找出最耗 CPU 的线程。
3. 把线程 ID 转为 16 进制后，用 `jstack` 看它在跑什么。
4. 如果是 GC 线程，再用 `jstat -gcutil` 看是不是 GC 在吃 CPU。
5. 如果是业务线程，顺着堆栈定位代码热点、死循环、异常重试或锁竞争。

## 2. 场景二：全局 504
1. 先不要被“CPU 不高”迷惑。
2. 看 HTTP 线程池、RPC 公共线程池是否被占满。
3. 看线程是否卡在 `getConnection`、外部 RPC、锁竞争或队列等待上。
4. 如果卡在连接获取，继续排查 [[5.2 数据库连接池]]、[[13.1 SQL 性能分析]] 和慢 SQL。
5. 如果是反向代理层统一超时，也要把 [[4.1 反向代理]] 一并纳入链路判断。

## 3. 场景三：Full GC 频繁
1. `jstat -gcutil <pid> 1000 10` 先确认 FGC 是否在持续增长。
2. `jmap -heap <pid>` 看 Old 区、堆总量、Region 配置。
3. 如果是 G1，再对照 [[G1 垃圾回收器]] 和 [[3.6 垃圾回收调优]] 判断是参数问题、对象晋升问题还是业务分配模式有问题。
4. 如果怀疑对象堆积，再考虑 `jmap -histo` 或堆 dump。

## 4. 场景四：内存使用率高
1. `free -h` 看 `available`。
2. `ps -eo pid,rss,comm --sort=-rss | head -10` 看是不是 Java 进程在吃内存。
3. `jmap -heap <pid>` 看堆是否真的高。
4. 如果堆不高但 RSS 很高，要警惕直接内存、线程栈或 native 内存。

## 5. 场景五：Metaspace 使用率高
1. 先看趋势，不要先下结论。
2. `jstat -gcmetacapacity` 看 `MC` 是否在增长。
3. `jstat -class` 看已加载类和已卸载类的关系。
4. 只有当它持续增长时，才用 `jmap -clstats` 去找可疑类加载器。

# 十、指标参考告警线
## 1. 系统指标

| 指标 | 安全 | 关注 | 危险 |
|------|------|------|------|
| CPU 利用率 | < 60% | 60% ~ 80% | > 80% |
| Load Average | < 核数 | ≈ 核数 | > 核数 * 2 |
| available 内存 | > 20% | 10% ~ 20% | < 10% |
| IO wait | < 5% | 5% ~ 20% | > 20% |
| 网络重传率 | < 0.1% | 0.1% ~ 1% | > 1% |

## 2. JVM 指标

| 指标 | 安全 | 关注 | 危险 |
|------|------|------|------|
| Old 区使用率 | < 60% | 60% ~ 80% | > 80% 持续 |
| Metaspace 使用率 | < 80% | 80% ~ 90% | > 90% |
| Young GC 单次耗时 | < 50ms | 50 ~ 200ms | > 200ms |
| Full GC 单次耗时 | < 1s | 1 ~ 5s | > 5s |
| 线程数 | < 500 | 500 ~ 2000 | > 2000 |

## 3. 线程池与连接池指标

| 指标 | 正常 | 关注 | 危险 |
|------|------|------|------|
| 线程池活跃数占比 | < 50% | 50% ~ 80% | > 80% |
| BLOCKED 线程数 | 0 | 少量偶发 | 持续存在 |
| 数据库连接池等待数 | 0 | 偶发 > 0 | 持续 > 0 |
| 504 / 502 数量 | 0 | 偶发 | 持续上升 |

# 十一、最终落地建议
## 1. 让这份手册承担什么角色
* 这篇笔记更适合作为“总入口”，帮助你快速决定下一步该查哪一条线。
* 具体细节不要都堆在这里，而应该继续分流到线程池、连接池、GC、堆结构、慢 SQL 这些专题笔记中。

## 2. 真正提升排障效率的三个动作
1. 统一保留现场的最小命令集。
2. 给线程池、连接池、慢 SQL、GC 建立前置监控。
3. 把复盘案例持续挂回这份手册，形成“通用框架 + 真实案例”的知识闭环。