# MTOP 流式-服务端接入方案

注意事项

考虑到流式链路是全新链路，有以下两个改动点：

1

由 HSF 的 HttpServer 变成 MTOP 的 HttpServer（不过两者底层都是 netty）。

（MTOP 已在「测试应用」进行单机性能压测，两者性能（RT、GC、CPU、内存等）基本持平，仅供参考）

2

从原来的单请求-单响应模式，变成单请求-多响应模式，可能会影响应用单机容量和接口限流，具体取决于业务如何使用流式。

因此接入流式的业务最好：

1

性能压测，关注 GC、RT，重新评估单机容量，调整对应接口限流

2

将流式链路加入大促全链路压测。

具体是否需要压测，还以业务评估为准。

ps：强烈不推荐流式和 NextRPC 同时使用！！！

这两个能力本身就是同质的，理论上流式能力是可以覆盖 NextRPC 的场景。两者同时使用，架构复杂度会大大提升，很容易用出问题，排查起来也很困难。

如果非要用一定要保证在写出第一个响应前，NextRPC 逻辑已经执行了。

接入及使用方式

0\. 前置准备

1

流式能力仅去中心化的 MTOP API 支持，因此请先确认 API 已正确做过去中心化，

[

去中心化文档

](https://aliyuque.antfin.com/mtop/doc/mtop-uncenter-intro)

2

如果应用此前是在 Max 控制台操作，请先找 MTOP 管理员

[@雪元](https://aliyuque.antfin.com/xueyuan.yx)

将应用切换到 MTOP 新控制台 UltraMax 操作，只有新控制台支持流式 API。（切换到新控制台后，便不再允许在原 Max 控制台操作应用）

1

升级 Pandora Sar 版本

●

应用需要升级 mtop 去中心化插件至

1.3.2 及以上版本

，对应 Pandora Sar 为

2024-04-release-fix-fastjson 及以后版本

。由于 Pandora Sar 包 升级，可能会涉及到其他插件的升级，请务必做好业务测试！

●

应用还需要升级 mtop 去中心化 sdk 的依赖，以使用开启流式的 API，如下：

2

开启流式能力

config 方式:

API 方式:

3

nginx 配置（按需配置）

如果业务有同机 nginx，需要在 nginx 增加如下配置，关闭 nginx 缓存。

4

将请求路由到流式端口

流式链路为新的请求链路，只有从新端口号 14999 进来的请求才具备流式响应的能力（新端口同时也兼容非流式）。

业务需要判断应用在接入流式前做去中心化接入使用的 VIPServer Key 服务端口是否为 12220 端口：

1

如果应用原本是 12220 端口，则直接升级为 14999 端口即可。升级方式为：在 UltraMax 创建一个流式流量分组并将端口号改为 14999，同时参考后文 「稳定性保障」->「灰度方案」将 API 的「流量分组」改为流式流量分组。（注意：API 修改完流量分组需要重新发布才能生效哦~）

到 UltraMax 的「应用管理」-> 「流量分组」页面按照提示创建一个

流式流量分组，选择端口号为 14999

（如果应用已经有 VIPServer 端口号为 14999 的流量分组，则无需创建）。

1.设置分组名,应用下唯一.

分组名称

MTOP 流式分组

分组号口号

2.设置分组端口号,该端口号会用于初始化VIPSERVER KEY 的端口号.

名文 同时交持单响应利流式响应,击费联务链MTOPAGENT 启用配置ENABIESTREAM 或 STARTIATOP3,详见配置文

自定义&同时

12220

3.确保你的服务端应用的MTOPAGENT 已经正确配置.

预发机器分组

日常机器分组

线上机器分组

日常环境\*

选择分组

PATTON-PREHOSTX

4.透样当的环境下架使用的机器分组.可多活.保存后,平台合自动为该环境创造VPSANORKO)并接起价速连的机器分组.因时使用\[分组转口号\](

取消

图保存

![[Attachment/8d0c93fed62655031d85acac27c9bdc6_MD5.png]]

2

若是其他代理端口（比如 nginx 80 端口）

，

则需要先完成步骤 1

，

然后在代理层配置将流式的 API 转发到 14999 端口。

【MTOP 极其不推荐使用此类中间代理，使用代理导致的任何路由问题 MTOP 无法排查】

5

使用方法

●

mtop 提供

MtopContext.acceptStream()

方法判断当前请求是否支持流式, 并提供

MtopContext.startStream()

方法获取 MtopStream 实例;

●

mtop 通过

com.alibaba.mtop3.invocation.MtopStream

类提供流式响应能力, 共有四个接口:

○

write(Object content)

// 进行一次流式响应

○

writeAndEnd(Object content)

// 进行一次流式响应，并正常结束当前 Stream

○

end()

// 正常结束当前 Stream

○

endExceptionally(Throwable throwable)

// 异常结束当前 Stream

同步使用方式:

异步使用方式:

使用注意点:

●

业务需要先调用

MtopContext.acceptStream()

判断当前请求是否支持流式, 当返回 false 时, 强制调用

MtopContext.startStream()

会抛出异常;

●

一定要保证 MtopStream.end() 方法在 MtopStream.write(object) 方法之后调用;

●

在一次请求里, MtopStream.end() 与 MtopStream.endExceptionally(e) 方法只有一个会生效, 且只有第一次被调用的方法会生效, 后续对这两方法的多次调用会被忽略;

●

在一次请求里, 当 MtopStream.end() 或 MtopStream.endExceptionally(e) 被调用后, MtopStream.write(object) 或 MtopStream.writeAndEnd(object) 方法的调用将被忽略;

稳定性保障

mtop 服务端对流式的支持使用了新的请求链路 (新端口号)，故提供了完善的机制以保障服务稳定性;

1

灰度路由方案

首先，需要确认已经找 MTOP 管理员将你的应用从 Max 迁移到 UltraMax，并在 UltraMax 创建了流式流量分组，即完成上文的步骤

4 将请求路由到流式端口

（迁移仅仅是为了切换到新 MTOP 控制台操作，不影响服务端）

1

在 UltraMax 找到你的API，编辑并修改 API 的流量分组为你创建的流式分组。

2

修改后，重新发布 API，通过分批发布可实现灰度。

2

降级方案

MTOP 流式响应提供了完备的降级能力, 支持 从客户端或服务端 降级单响应:

客户端降级

●

业务客户端通过 MTOP Client SDK 提供的接口，决定本次请求是否接收流式响应。

●

当端侧降级时（不接受流式响应）, 请求会通过相关 header 控制 MtopContext.acceptStream() 方法返回 false, 以控制业务服务端方法降级为普通单响应。

服务端降级

●

业务服务端可以自主控制是否使用流式响应，即是否调用 MTOP Server SDK 提供的 流式 API。

3

回滚方案

当 mtop 服务端的流式新链路出现问题且无法通过降级为普通单响应解决时, 可以通过 Marconi 配置新旧 vipserverKey 的权重, 将后端请求完全回滚到旧的 mtop 链路;

特殊情况处理

1\. 非预期中断

如果流式响应过程中突然发生网络断连等异常中断场景, 端侧会等待直到超时, 业务端侧需要自己处理未接收全部流式响应的情况;

2\. 发生异常提前结束

●

业务在调用 MtopContext.startStream() 前抛出异常, 则认为是普通单响应, mtop 将返回 ret = FAIL\_SYS\_HSF\_THROWN\_EXCEPTION 的单响应;

●

业务在调用 MtopContext.startStream() 后直接抛出异常, mtop 仅记录日志, 而不会处理该异常 (要避免该情况);

●

业务在开启流式后调用 mtopStream.endExceptionally(throwable) 方法显式返回异常, mtop 将直接返回 ret = FAIL\_SYS\_HSF\_THROWN\_EXCEPTION 的响应并结束当前流, 不再接受新的业务响应;

●

业务在开启流式后调用 mtopStream.wirte(object) 方法写回一个 Throwable, mtop 将直接返回 ret = FAIL\_SYS\_HSF\_THROWN\_EXCEPTION 的响应并结束当前流, 不再接受新的业务响应;

业务端侧需要自己处理未接收全部流式响应的情况;

3.以错误状态主动提前结束

●

如果业务调用 mtopStream.wirte() 写回了一个 com.taobao.mtop.common.Result 对象, 并且设置 Result#success 为 false, mtop 将会提前结束当前流, 并将响应置为失败 (业务端侧一定能收到 mtopSDK 的 onError 回调)

●

如果业务调用 mtopStream.wirte() 写回了一个 com.taobao.mtop.common.MtopResult 对象, 并且设置了自定义 msgCode (非 SUCCESS), mtop 将会提前结束当前流, 并将响应置为失败 (业务端侧一定能收到 mtopSDK 的 onError 回调)

4\. 接口超时

当业务正在通过 mtopStream 做流式响应时, MTOP API 响应超时, mtop 将直接返回 ret = FAIL\_SYS\_SERVICE\_TIMEOUT 的响应并结束当前流, 不再接受新的业务响应;

5\. 多段响应的顺序

mtop 流式响应严格按照业务调用的顺序发送响应, 响应包的到达顺序由传输层 TCP / QUIC 来保证;

测试

新版 UltraMax 控制台已经支持流式测试：

[

https://ultramax.alibaba-inc.com/max/test/platform

](https://ultramax.alibaba-inc.com/max/test/platform)

16 人点赞

16