# 线上故障排查：Metaspace 触发 Full GC 风暴导致 504
> 2026-06-17 故障排查实录。全局 504 再次出现，这次根因是 Metaspace 达到 512MB 上限，反复触发 Full GC，VM Thread 独占 99.9% CPU，业务线程完全无法执行。

## 一、故障现象

2026-06-17 10:11 左右，用户反馈后台接口 504：

```java
Request URL:    https://xiaoer.admin.alitrip.com/scenicLibrary/scenicList
Request Method: POST
Status Code:    504 Gateway Timeout
```

与 2026-06-15 的故障表现一致（全局 504），但根因不同。

---
## 二、排查过程
### 机器 1：travel-xiaoer033102194110
#### 2.1 系统概览
```bash
# top: 实时查看系统资源使用情况
#   -b: batch 模式（非交互，适合脚本/管道）
#   -n1: 只刷新 1 次就退出
# head -5: 只取前 5 行（CPU/Load/内存概要）
$ top -bn1 | head -5
top - 10:11:21 up 1 day, 17:19,  0 users,  load average: 1.40, 1.49, 1.46
Tasks:  25 total,   1 running,  24 sleeping,   0 stopped,   0 zombie
%Cpu(s):  1.1 us,  0.0 sy,  0.0 ni, 98.8 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 16777216 total,  1445140 free, 11272944 used,  4059132 buff/cache
KiB Swap:        0 total,        0 free,        0 used.  4657364 avail Mem
# 输出解读：
#   load average: 1分钟/5分钟/15分钟 平均负载（< CPU核数为正常）
#   us=用户态CPU  sy=内核态CPU  id=空闲  wa=IO等待
```

整机 CPU idle 98.8%，看起来不忙。但 Java 进程单独看很不正常。

#### 2.2 定位 Java 进程 PID
```bash
# jps: JDK 自带工具，列出当前用户的 Java 进程
#   -l: 显示主类的完整包名（便于区分多个 Java 进程）
$ jps -l
2174 com.taobao.pandora.boot.loader.SarLauncher
```

Java 主进程 PID 为 **2174**，后续命令均使用此 PID。

> 注意：`top` 显示的 Java 进程 PID 和 `jps` 的结果可能不同——`top` 显示的可能是子线程的 PID，`jps` 显示的才是主进程 PID。实际排查中曾用 `top -Hp 7797` 但 jstack 连不上，后通过 `jps -l` 发现真正的 PID 是 3769。

#### 2.3 线程级 CPU 分析
```bash
# top -Hp: 查看指定进程内每个线程的 CPU 占用
#   -H: 显示线程（默认只显示进程级）
#   -p 2174: 只看 PID=2174 的进程
#   -b -n1: batch 模式，只刷新 1 次
# head -20: 取前 20 行（最耗 CPU 的线程排在前面）
$ top -bn1 -Hp 2174 | head -20
top - 10:11:49 up 1 day, 17:20,  0 users,  load average: 1.79, 1.58, 1.49
Threads: 2050 total,   1 running, 2049 sleeping,   0 stopped,   0 zombie
    PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND
   2208 admin     20   0   59.0g  10.5g  40084 R 99.9 65.7   1216:37 java
   2174 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7   0:00.00 java
   2179 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7   3:39.48 java
   2187 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7  88:07.95 java
   2188 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7  88:08.20 java
   2189 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7  88:09.54 java
   2190 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7  88:06.90 java
   2191 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7  88:06.77 java
   2192 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7  88:07.67 java
   2193 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7  88:07.67 java
   2194 admin     20   0   59.0g  10.5g  40084 S  0.0 65.7  88:07.16 java
# 输出解读：
#   PID=线程ID  S=状态(R=Running S=Sleeping)  %CPU=CPU占用  TIME+=累计CPU时间
```

关键发现：

- **线程 2208 独占 99.9% CPU，已持续运行 1216 分钟（约 20 小时）**
- 线程 2187~2194（8 个线程）各运行约 88 小时——与 G1GC 8 线程配置吻合，是 GC 并行工作线程

#### 2.4 定位耗 CPU 线程
```bash
# printf: 将线程 PID（十进制）转为十六进制
# jstack 中线程 ID 的格式是 nid=0x十六进制，所以需要转换才能匹配
$ printf 'nid=0x%x\n' 2208
nid=0x8a0
# jstack: 抓取 Java 进程的线程快照（所有线程的状态和调用栈）
# grep -A 30: 匹配到 nid=0x8a0 后，再显示后续 30 行（调用栈内容）
$ jstack 2174 | grep -A 30 'nid=0x8a0'
"VM Thread" os_prio=0 tid=0x00007fa774b41000 nid=0x8a0 runnable
"Gang worker#0 (Parallel GC Threads)" os_prio=0 tid=0x00007fa774022000 nid=0x88b runnable
"Gang worker#1 (Parallel GC Threads)" os_prio=0 tid=0x00007fa774023800 nid=0x88c runnable
"Gang worker#2 (Parallel GC Threads)" os_prio=0 tid=0x00007fa774025800 nid=0x88d runnable
"Gang worker#3 (Parallel GC Threads)" os_prio=0 tid=0x00007fa774027800 nid=0x88e runnable
"Gang worker#4 (Parallel GC Threads)" os_prio=0 tid=0x00007fa774029000 nid=0x88f runnable
"Gang worker#5 (Parallel GC Threads)" os_prio=0 tid=0x00007fa77402b000 nid=0x890 runnable
"Gang worker#6 (Parallel GC Threads)" os_prio=0 tid=0x00007fa77402d000 nid=0x891 runnable
"Gang worker#7 (Parallel GC Threads)" os_prio=0 tid=0x00007fa77402e800 nid=0x892 runnable
"G1 Main Concurrent Mark GC Thread" os_prio=0 tid=0x00007fa77404a800 nid=0x89d runnable
"Gang worker#0 (G1 Parallel Marking Threads)" os_prio=0 tid=0x00007fa77404c000 nid=0x89e runnable
"Gang worker#1 (G1 Parallel Marking Threads)" os_prio=0 tid=0x00007fa77404e000 nid=0x89f runnable
"G1 Concurrent Refinement Thread#0" os_prio=0 tid=0x00007fa774040800 nid=0x89c runnable
"G1 Concurrent Refinement Thread#1" os_prio=0 tid=0x00007fa77403e800 nid=0x89b runnable
"G1 Concurrent Refinement Thread#2" os_prio=0 tid=0x00007fa77403c800 nid=0x89a runnable
"G1 Concurrent Refinement Thread#3" os_prio=0 tid=0x00007fa77403b000 nid=0x899 runnable
```

**线程 2208 是 VM Thread**——JVM 内部线程，负责执行 Stop-The-World GC 操作。它占 99.9% CPU 说明 GC 一直在疯狂运行。

#### 2.5 GC 状况
```bash
# jstat -gcutil: 查看 GC 各区域使用率
#   参数：jstat -gcutil <pid> <采样间隔ms> <采样次数>
#   1000 5 = 每 1000ms（1秒）采样一次，共 5 次
# 输出列：S0/S1=Survivor区  E=Eden  O=Old  M=Metaspace  CCS=压缩类空间
#         YGC/YGCT=YoungGC次数/总耗时  FGC/FGCT=FullGC次数/总耗时  GCT=GC总耗时
$ jstat -gcutil 2174 1000 5
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT
  0.00   0.00   0.00  28.85  92.15  90.07   7634  240.438 16596 77903.200 78143.638
  0.00 100.00   0.00  28.76  92.15  90.07   7635  240.481 16597 77907.723 78148.204
  0.00 100.00   0.00  28.76  92.15  90.07   7635  240.481 16597 77907.723 78148.204
  0.00 100.00   0.00  28.76  92.15  90.07   7635  240.481 16597 77907.723 78148.204
  0.00 100.00   0.00  28.76  92.15  90.07   7635  240.481 16597 77907.723 78148.204
```

数据分析：

![[IMG-20260617205530392.png|979]]

**关键矛盾：Old 区只有 28%，堆明明很空，却发生了 16,597 次 Full GC。**

这说明 Full GC 的触发源不在堆内，而在堆外——Metaspace。

### 机器 2：travel-xiaoer033008049028
#### 2.6 系统概览
```bash
# 同机器 1，查看系统 CPU/Load/内存概况
$ top -bn1 | head -5 up 1 day, 17:03,  0 users,  load average: 1.35, 1.49, 1.45
Tasks:  26 total,   1 running,  25 sleeping,   0 stopped,   0 zombie
%Cpu(s):  9.6 us,  0.0 sy,  0.0 ni, 90.4 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 16777216 total,  1427760 free, 11137072 used,  4212384 buff/cache
KiB Swap:        0 total,        0 free,        0 used.  4789636 avail Mem
```

CPU 9.6% user，比机器 1 高一些。

#### 2.7 定位 Java 进程 PID
```bash
# jps 报错，改用 ps 查找 Java 进程
# ps -ef: 显示所有进程的完整信息
# grep java: 过滤出 java 进程
# grep -v grep: 排除 grep 自身这条进程
# awk '{print $2}': 取第 2 列（PID）
# head -1: 只取第一个结果
$ jps -l

OpenJDK 64-Bit Server VM warning: bad AJDK_MAX_PROCESSORS_LIMIT value 8
# ... jps 输出异常（AJDK 已知问题）

# 改用 ps 代替
$ pid=$(ps -ef | grep java | grep -v grep | awk '{print $2}' | head -1) && echo "PID: $pid"

PID: 2019
```
> 踩坑记录：这台机器的 `jps` 命令因 AJDK 版本问题输出异常，无法正确获取 PID。遇到此类情况直接用 `ps -ef | grep java` 代替。

#### 2.8 线程级 CPU 分析
```bash
# 同机器 1，查看 Java 进程内线程级 CPU 占用
$ top -bn1 -Hp 2019 | head -15

top - 10:19:09 up 1 day, 17:04,  0 users,  load average: 1.19, 1.43, 1.43
Threads: 2287 total,   1 running, 2286 sleeping,   0 stopped,   0 zombie
    PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND
   2053 admin     20   0   19.3g  10.4g  37452 R 99.9 64.9 246:19.37 java
   2067 admin     20   0   19.3g  10.4g  37452 S  5.3 64.9   1:54.41 java
   2019 admin     20   0   19.3g  10.4g  37452 S  0.0 64.9   0:00.00 java
   2030 admin     20   0   19.3g  10.4g  37452 S  0.0 64.9   3:46.03 java
   2033 admin     20   0   19.3g  10.4g  37452 S  0.0 64.9  15:37.70 java
   2034 admin     20   0   19.3g  10.4g  37452 S  0.0 64.9  15:31.71 java
   2035 admin     20   0   19.3g  10.4g  37452 S  0.0 64.9  15:22.00 java
   2036 admin     20   0   19.3g  10.4g  37452 S  0.0 64.9  15:25.95 java
```

同样的模式——**线程 2053 独占 99.9% CPU，已运行 246 分钟**。

#### 2.9 Jstat 崩溃
```bash
# jstat -gcutil: 尝试查看 GC 统计，但在这台机器上崩溃了
$ jstat -gcutil 2019 1000 5
OpenJDK 64-Bit Server VM warning: bad AJDK_MAX_PROCESSORS_LIMIT value 8
#
# A fatal error has been detected by the Java Runtime Environment:
#
#  SIGSEGV (0xb) at pc=0x00007f6a7af9b2d0, pid=468656, tid=0x00007f6a7834d700
#
# JRE version: OpenJDK Runtime Environment (8.0_152-b187) (build 1.8.0_152-b187)
# Java VM: OpenJDK 64-Bit Server VM (25.152-b187 mixed mode linux-amd64 compressed oops)
# Problematic frame:
# V  [libjvm.so+0x91b2d0]  ParNewGeneration::collect(bool, bool, unsigned long, bool)+0x80
#
# Core dump written. Default location: /home/admin/travel-xiaoer/bin/core or core.468656
```

jstat 进程自身崩溃（AJDK 已知问题），不影响应用进程。改用 GC 日志获取 GC 数据。

#### 2.10 GC 日志——实锤 Metaspace 触发
```bash
# tail: 查看文件末尾内容
#   -30: 显示最后 30 行
# GC 日志中的触发原因关键字：
#   "Metadata GC Threshold" → Metaspace 达到上限触发
#   "Allocation Failure" → 堆空间不足触发
#   "System.gc()" → 代码中显式调用触发
$ tail -30 /home/admin/travel-xiaoer/logs/middleware/gc.log

2026-06-17T10:19:37.078+0800: 147883.912: [GC concurrent-mark-abort]
2026-06-17T10:19:37.107+0800: 147883.941: [GC pause (Metadata GC Threshold) (young) (initial-mark), 0.0426088 secs]
   [Parallel Time: 31.3 ms, GC Workers: 8]
      [GC Worker Start (ms): Min: 147883945.2, Avg: 147883945.3, Max: 147883945.4, Diff: 0.2]
      [Ext Root Scanning (ms): Min: 18.6, Avg: 20.5, Max: 27.0, Diff: 8.4, Sum: 163.8]
      [Update RS (ms): Min: 0.0, Avg: 0.5, Max: 2.5, Diff: 2.5, Sum: 3.7]
         [Processed Buffers: Min: 0, Avg: 17.2, Max: 35, Diff: 35, Sum: 138]
      [Scan RS (ms): Min: 0.0, Avg: 0.0, Max: 0.0, Diff: 0.0, Sum: 0.0]
      [Code Root Scanning (ms): Min: 0.0, Avg: 0.0, Max: 0.0, Diff: 0.0, Sum: 0.0]
      [Object Copy (ms): Min: 0.6, Avg: 1.8, Max: 3.4, Diff: 2.8, Sum: 14.8]
      [Termination (ms): Min: 0.0, Avg: 5.6, Max: 7.5, Diff: 7.5, Sum: 44.9]
         [Termination Attempts: Min: 1, Avg: 1.0, Max: 1, Diff: 0, Sum: 8]
      [GC Worker Other (ms): Min: 0.0, Avg: 0.0, Max: 0.0, Diff: 0.0, Sum: 0.1]
      [GC Worker Total (ms): Min: 28.3, Avg: 28.4, Max: 28.5, Diff: 0.2, Sum: 227.4]
      [GC Worker End (ms): Min: 147883973.6, Avg: 147883973.7, Max: 147883973.7, Diff: 0.1]
   [Code Root Fixup: 0.3 ms]
   [Code Root Purge: 6.2 ms]
   [Clear CT: 0.4 ms]
   [Other: 4.4 ms]
      [Choose CSet: 0.0 ms]
      [Ref Proc: 0.5 ms]
      [Ref Enq: 0.0 ms]
      [Redirty Cards: 0.4 ms]
      [Humongous Register: 0.0 ms]
      [Humongous Reclaim: 0.0 ms]
      [Free CSet: 0.1 ms]
   [Eden: 8192.0K(408.0M)->0.0B(400.0M) Survivors: 0.0B->8192.0K Heap: 2056.8M(8192.0M)->2051.8M(8192.0M)]
 [Times: user=0.19 sys=0.00, real=0.04 secs]
2026-06-17T10:19:37.150+0800: 147883.985: [GC concurrent-root-region-scan-start]
2026-06-17T10:19:37.150+0800: 147883.985: [Full GC (Metadata GC Threshold)
```

**实锤**：GC 日志明确标注触发原因为 `Metadata GC Threshold`。

---
## 三、根因分析
### 故障链路
```java
Metaspace 使用 481MB / 上限 512MB（94%）
    ↓
微小波动触及上限
    ↓
JVM 触发 Full GC 试图卸载类释放 Metaspace
    ↓
大部分类无法卸载（Spring/HSF/中间件类常驻）
    ↓
Full GC 完成，Metaspace 几乎没释放
    ↓
再次触及上限 → 再次 Full GC → 循环往复
    ↓
每次 Full GC 4.7 秒（JDK 8 单线程），期间应用完全停顿
    ↓
VM Thread 独占 99.9% CPU 持续执行 GC
    ↓
业务线程饿死，所有请求 504
```
### 推断过程：为什么确定是 Metaspace 触发

通过排除法：

![[IMG-20260617205530443.png|1003]]

堆没满（28%）却发生 16,597 次 Full GC，触发源只可能在堆外。JVM 堆外能触发 Full GC 的只有 Metaspace。GC 日志中的 `Metadata GC Threshold` 标记最终实锤。

## 四、两台机器数据汇总

| 指标          | 机器 1 (033102194110)        | 机器 2 (033008049028)           |
| ----------- | -------------------------- | ----------------------------- |
| 运行时间        | 1 天 17 小时                  | 1 天 17 小时                     |
| 耗 CPU 线程    | TID 2208 (VM Thread) 99.9% | TID 2053 99.9%                |
| 耗 CPU 时长    | 1216 分钟（20 小时）             | 246 分钟（4 小时）                  |
| Full GC 次数  | 16,597                     | 未获取（jstat 崩溃）                 |
| Full GC 总耗时 | 77,903 秒（21.6 小时）          | 未获取                           |
| Old 区       | 28.76%                     | 未获取                           |
| Metaspace   | 92.15%                     | 未获取                           |
| GC 日志触发原因   | 未查看                        | **Metadata GC Threshold**（实锤） |
| 线程总数        | 2050                       | 2287                          |
| 堆大小         | 59.0g VIRT / 10.5g RES     | 19.3g VIRT / 10.4g RES        |

## 五、解决方案
### 立即执行

修改 `setenv.sh` 中的 Metaspace 配置：

```bash
# 原配置
-XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=512m
# 改为
-XX:MetaspaceSize=512m -XX:MaxMetaspaceSize=768m
```

![[IMG-20260617205530528.png|1029]]

副作用分析：

![[IMG-20260617205530578.png|1038]]

调整之后的机器 metaspace利用率水位：

![[IMG-20260617205530641.png|731]]

## 六、排查命令记录
### 本次排查中实际使用的命令
```bash
# 系统概览
top -bn1 | head -5

# 找 Java PID（jps 方式）
jps -l

# 如果 jps 报错（AJDK 已知问题），用 ps 代替
pid=$(ps -ef | grep java | grep -v grep | awk '{print $2}' | head -1)

# 线程级 CPU
top -bn1 -Hp <pid> | head -20

# 最耗 CPU 线程 PID 转 16 进制
printf 'nid=0x%x\n' <tid>

# 查看该线程的调用栈

jstack <pid> | grep -A 30 'nid=0x<hex>'

# GC 统计
jstat -gcutil <pid> 1000 5

# GC 日志——确认触发原因
tail -50 /home/admin/travel-xiaoer/logs/middleware/gc.log

# 如果看到 "Metadata GC Threshold" 就是 Metaspace 触发的
# 线程状态分布
jstack <pid> | grep 'java.lang.Thread.State' | sort | uniq -c | sort -rn

# 线程池分布
jstack <pid> | grep -oP '"[^"]*"' | sed 's/-[0-9]*"/"/g' | sort | uniq -c | sort -rn | head -20

# 保留现场（重启前必做）
jstack $pid > /tmp/jstack_$(date +%s).log
jstat -gcutil $pid 1000 10 > /tmp/jstat_$(date +%s).log
top -bn1 -Hp $pid > /tmp/top_threads_$(date +%s).log
```
### Jstack 连不上时的替代方案
```bash
# 方式 1：jcmd
jcmd <pid> Thread.print

# 方式 2：发信号（不会杀进程，输出到 stdout 日志）
kill -3 <pid>

# 方式 3：强制模式（输出信息较少）
jstack -F <pid>
```
### Jstack 相关命令说明

| 命令 | 作用 |
|------|------|
| `jstack <pid>` | 抓线程快照，显示每个线程的状态和调用栈（首选） |
| `jstack -l <pid>` | 同上 + 显示锁信息，怀疑死锁/锁竞争时用 |
| `jstack -F <pid>` | 强制抓取，jstack 连不上时的备选 |
| `jcmd <pid> Thread.print` | 功能同 jstack，走不同通道，jstack 不可用时用 |

### 线程分析命令说明

| 命令 | 作用 |
|------|------|
| `jstack <pid> \| grep -oP '"[^"]*"' \| sed 's/-[0-9]*"/"/g' \| sort \| uniq -c \| sort -rn \| head -20` | 按线程池名分组计数，看哪类线程最多 |
| `jstack <pid> \| grep 'java.lang.Thread.State' \| sort \| uniq -c \| sort -rn` | 统计所有线程状态分布（WAITING/BLOCKED/RUNNABLE） |
| `jstack <pid> \| grep -A 3 'http-nio-7001-exec' \| grep 'State' \| sort \| uniq -c` | 单看 Tomcat HTTP 线程池的状态分布 |
| `jstack <pid> \| grep -A 3 'HSFBizProcessor-DEFAULT' \| grep 'State' \| sort \| uniq -c` | 单看 HSF RPC 线程池的状态分布 |

### 线程状态速查

| 状态 | 含义 | 大量出现时 |
|------|------|-----------|
| WAITING | 空闲等待任务 | 正常，线程池线程没活干 |
| TIMED_WAITING | 带超时等待 | 正常，定时任务/心跳 |
| RUNNABLE | 正在执行或等 IO | 少量正常，大量说明很忙 |
| BLOCKED | 等锁 | **有问题**——锁竞争 |

## 七、关联 JVM 知识点
### 7.1 Metaspace 和方法区
* 这次故障的直接触发点是 Metaspace 达到 `MaxMetaspaceSize` 上限，关联到 [[方法区介绍#2. 方法区的实现方式|方法区的实现方式]]：JDK 8 中方法区由 Metaspace 实现，类元数据从永久代迁移到本地内存。
* `jstat -gcutil` 中的 `M` 列表示 Metaspace 使用率，`CCS` 表示压缩类空间；当 `M` 接近上限并且 GC 日志出现 `Metadata GC Threshold` 时，应优先按 [[方法区介绍|方法区内存诊断]] 的思路排查。

### 7.2 类元数据和类加载
* Metaspace 保存的是类结构信息、方法字节码、运行时常量池等类元数据，和 [[类的生命周期#2.1 加载 `.class` 文件|类加载阶段]] 中生成并放入方法区的 `instanceKlass` 对应。
* 如果线上持续动态生成类，或者类加载器无法被回收，就可能让 Metaspace 水位持续上涨；这里可以继续关联 [[自定义类加载器]]、[[线程上下文类加载器]]、[[双亲委派模式]] 来排查类由谁加载、是否存在重复加载或类加载器泄漏。

### 7.3 Full GC 触发原因
* 本次 `Old` 区只有约 28%，但 `Full GC` 已经发生 16,597 次，说明不能只按堆内存不足理解 Full GC；应结合 [[3.6 垃圾回收调优|垃圾回收调优案例]] 判断触发源是否来自方法区 / Metaspace。
* GC 日志中的 `Full GC (Metadata GC Threshold)` 是关键证据，含义是 JVM 试图通过 Full GC 卸载无用类来释放 Metaspace；如果类无法卸载，Full GC 结束后 Metaspace 仍然接近上限，就会进入反复触发的循环。

### 7.4 G1 和 STW
* 当前现场看到 `VM Thread` 独占 CPU，说明 JVM 正在执行 STW 相关内部任务；这和 [[G1 垃圾回收器|G1 退化为 Full GC]] 的知识点可以一起理解：一旦进入 Full GC，业务线程会被暂停，接口就可能表现为全局 504。
* 这里的根因不是 G1 正常混合回收不够快，而是 Metaspace 上限过低叠加类无法有效卸载，导致 JVM 持续尝试通过 Full GC 释放类元数据。