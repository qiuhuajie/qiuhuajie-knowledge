# 未命名
# 4502174295003000742_4544586204207【护照审核】

![[IMG-20260404032155712.png|1573]]

![[IMG-20260404032155797.png|1532]]

数据库没数据，兜底的结果也没有写上

![[IMG-20260404032155881.png|364]]

但是这单没有告警

# 4502155395046016416_4545061233744【护照审核】

![[IMG-20260404032155993.png|274]]

告警的原因是，触发模型内容风控了：

[[IMG-20260404032155053.png|Open: Pasted image 20260324154330.png]]

![[IMG-20260404032155053.png|1062]]

现象：

![[IMG-20260404032156147.png|1195]]

![[IMG-20260404032156237.png|1232]]

![[IMG-20260404032156320.png|522]]

护照审核四个审核子场景：

![[IMG-20260404032156414.png|553]]

每个子场景都超时报错：

[[IMG-20260404032155131.png|Open: Pasted image 20260323203346.png]]

![[IMG-20260404032155131.png|879]]

# 4502054052003105701_4459686842413【出签结果】

没有告警：

[[IMG-20260404032155245.png|Open: Pasted image 20260324153733.png]]

![[IMG-20260404032155245.png|497]]

因为走了快速返回的兜底，没有触发钉钉告警

[[IMG-20260404032155330.png|Open: Pasted image 20260324153817.png]]

![[IMG-20260404032155330.png|1182]]

[[IMG-20260404032155413.png|Open: Pasted image 20260324153840.png]]

![[IMG-20260404032155413.png|1244]]

[[IMG-20260404032155512.png|Open: Pasted image 20260324153844.png]]

![[IMG-20260404032155512.png|1273]]

# 直接快速返回false结果的原因

[[IMG-20260404032155606.png|Open: Pasted image 20260323204159.png]]

![[IMG-20260404032155606.png|1152]]

hsf 线程数飙升

![[IMG-20260404032156514.png|871]]

![[IMG-20260404032156596.png|865]]

# 原因

## 根因分析：线程持续积累 + `llmSessionCallInSliceParallel` 超时

这是一个**典型的线程池死锁（Thread Pool Deadlock）**，也叫 **"父子任务共用同一线程池"** 导致的饥饿死锁。

---

## 调用链与线程池使用关系

```java
handleEnableSubBizSceneInParallel
  └── 每个 subSceneConfig → CompletableFuture.supplyAsync(passportCheckExecutorPool)  ← 【外层：任务池】
        └── llmSessionCallInSliceParallel
              └── 每个材料分片 → CompletableFuture.supplyAsync(passportCheckSessionExecutorPool)  ← 【内层：会话池】
                    └── llmSessionCall → 真正的 LLM 网络调用（耗时长）
```

看起来外层用 `passportCheckExecutorPool`，内层用 `passportCheckSessionExecutorPool`，是两个独立的池，**理论上不会死锁**。

但问题出在 **`CallerRunsPolicy`** 上 👇

---

## 核心问题：`CallerRunsPolicy` 引发的线程泄漏

两个线程池的配置：

| 线程池 | 核心线程 | 最大线程 | 队列 | 拒绝策略 |
|---|---|---|---|---|
| `passportCheckExecutorPool` | 50 | 200 | `ArrayBlockingQueue(300)` | **`CallerRunsPolicy`** |
| `passportCheckSessionExecutorPool` | 50 | 200 | `ArrayBlockingQueue(300)` | **`CallerRunsPolicy`** |

**`CallerRunsPolicy` 的行为**：当线程池满（200线程全忙 + 队列300满）时，**由调用者线程（即提交任务的那个线程）直接执行任务**。

---

## 死锁/饥饿的完整链路

```java
1. 高并发下，passportCheckSessionExecutorPool 的 200 个线程全部在跑 llmSessionCall（LLM 调用很慢，几秒到几十秒）

2. 队列 300 也满了

3. 新的分片任务触发 CallerRunsPolicy
   → 由 passportCheckExecutorPool 的线程（外层任务线程）直接执行 llmSessionCall

4. 此时 passportCheckExecutorPool 的线程被"借用"去跑 LLM 调用
   → 这些线程本来应该在 llmSessionCallInSliceParallel 里等待 future.get(timeout)
   → 但它们现在被 CallerRunsPolicy 占用，无法返回去 get()

5. 外层 handleEnableSubBizSceneInParallel 的 future.get(timeout) 等不到结果
   → TimeoutException

6. future.cancel(true) 只是设置中断标志，但 LLM 的 HTTP 调用不响应中断
   → 线程继续持有，无法释放

7. 下一批请求进来，又重复上述过程
   → 线程数持续积累升高
```

---

## 为什么线程数一直升高

`future.cancel(true)` **并不能真正终止线程**，它只是：

- 设置 future 的 cancelled 状态
- 向线程发送 interrupt 信号

但 `llmSessionCall` 内部的 HTTP 调用（LLM 网络请求）**不响应 interrupt**，线程会继续阻塞在网络 I/O 上，直到 HTTP 超时或连接断开。

所以每次 `TimeoutException` 后，那些被 cancel 的线程**仍然活着**，继续占用线程池资源，新请求又不断创建新线程，最终线程数持续攀升。

---

## 总结：三个叠加问题

| 问题 | 描述 |
|---|---|
| **① CallerRunsPolicy 借用外层线程** | 内层 session 池满时，外层 task 池的线程被拿去直接跑 LLM 调用，导致外层 `future.get()` 无法及时被执行 |
| **② cancel(true) 无法中断 HTTP I/O** | 超时后 cancel 的线程仍然阻塞在 LLM 网络调用上，线程无法释放 |
| **③ 线程持续积累** | 每批请求都有泄漏的线程，随时间累积，最终压垮线程池 |

---

## 修复建议

**最直接的修复**：将 `passportCheckSessionExecutorPool` 的拒绝策略从 `CallerRunsPolicy` 改为 **`AbortPolicy`**（抛出异常），让 `llmSessionCallInSliceParallel` 里的 catch 块捕获并走兜底逻辑，而不是让外层线程被"借走"：

```java
new ThreadPoolExecutor.AbortPolicy()  // 替换 CallerRunsPolicy
```

同时，LLM HTTP 调用层面应该设置合理的**连接超时 + 读取超时**，确保线程不会无限阻塞在网络 I/O 上，这样 `cancel(true)` 才能真正生效。