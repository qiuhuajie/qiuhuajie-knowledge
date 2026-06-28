---
title: "阿里千问 AI Agent 三轮技术面试题答案"
tags:
  - "面试"
  - "AI Agent"
  - "RAG"
  - "Java"
  - "LangGraph"
  - "LangChain4j"
  - "系统设计"
created: 2026-06-28
source: "用户整理的阿里千问 AI Agent 三轮技术面试题"
---
# 一、一面
## 1. 自我介绍
1. 可以按“业务背景 -> 技术栈 -> 个人职责 -> 结果指标”的结构讲。示例：我主要做 Java 后端和 AI 应用工程，最近项目集中在 AI Agent、RAG、流式输出和工具调用编排上。我负责服务端链路设计，包括请求接入、意图识别、RAG 检索、工具调用、SSE/MTOP 流式输出、Redis/Tair 断点续接、任务状态落库和可观测性建设。核心难点是把大模型从“文本生成能力”工程化成“可恢复、可追踪、可降级的业务链路”。

## 2. AI Agent 或 RAG 项目介绍
1. 项目架构可以讲四层：入口层负责鉴权、限流和 trace；编排层负责意图识别、规划和工具路由；知识层负责文档解析、切分、向量化、混合检索和 rerank；执行层负责业务工具调用、证据拼装、流式返回和落库。
2. 个人职责可以强调 Agent 编排、RAG 检索链路、缓存、异步任务、流式输出、稳定性和监控。不要硬说自己训练模型，可以说负责模型能力的工程化落地。
3. 核心难点可以讲三个：检索质量不稳定，需要 chunk 策略、metadata、BM25 + 向量混合检索、rerank 和召回评估；工具调用不可控，需要 schema 校验、超时、重试、幂等和 fallback；长耗时体验差，需要流式输出、心跳、断点续接和任务状态管理。
4. 指标建议用首 token 延迟、P95/P99、工具调用成功率、RAG 命中率、人工兜底率、幻觉拦截率和 token 成本来描述。

## 3. JVM 内存模型，G1 与 ZGC 在长连接流式 Agent 服务中的差异
1. 面试里先区分 JMM 和 JVM 运行时内存。JMM 解决线程可见性、有序性和原子性；运行时内存包括堆、方法区、虚拟机栈、本地方法栈和程序计数器。Agent 服务里更常见的问题是堆对象、线程栈、直接内存和连接缓冲。
2. 长连接流式服务的特点是连接生命周期长、活跃对象多、响应链路对暂停敏感。GC 停顿会体现为心跳延迟、客户端超时和 P99 抖动。
3. G1 面向服务端吞吐和可预测停顿，适合大多数 Java 服务；它通过 region、并发标记和混合回收降低长停顿，但在高分配速率、大量老年代对象和 humongous 对象多时仍可能抖动。
4. ZGC 面向低延迟，大部分标记和转移工作并发执行，适合大堆、长连接和低 P99 场景；代价是读屏障、并发线程和额外内存开销，对 CPU 和内存余量更敏感。
5. 结论可以这样说：常规 Agent 网关优先 G1；如果是强实时长连接、大量流式会话且 P99 对 GC 极其敏感，可以压测 ZGC，并用 GC 日志、JFR、对象分配速率、老年代增长和连接延迟曲线验证。

## 4. ThreadPoolExecutor 核心参数与 Agent 工具并发线程池
1. 核心参数包括 `corePoolSize`、`maximumPoolSize`、`keepAliveTime`、`workQueue`、`threadFactory` 和 `RejectedExecutionHandler`。
2. Agent 并发调工具时不要所有工具共用一个无限队列线程池，否则慢工具会拖垮快工具。更合理的方式是按工具类型隔离线程池，例如 IO 工具池、CPU 后处理池、模型调用池、低优先级异步落库池。
3. IO 型线程数可以按 `目标 QPS × 平均 RT 秒 × 冗余系数` 估算；CPU 型任务接近 `CPU 核数` 或 `CPU 核数 + 1`。
4. 队列必须有界。用户在线链路的拒绝策略通常是快速失败或降级；后台任务可以转 MQ。还要配单工具超时、全局 deadline、bulkhead 隔离、熔断和 traceId。

## 5. CompletableFuture 实现多个工具调用的并行与串行编排
1. 并行编排用 `supplyAsync` 发起多个工具调用，用 `allOf` 聚合，用 `orTimeout` 或 `completeOnTimeout` 控制超时，用 `exceptionally` 转换失败结果。
2. 串行编排用 `thenCompose`，前一个工具结果作为后一个工具输入；结果转换用 `thenApply`；互不依赖的分支用 `thenCombine` 合并。
3. 工程上要传递 `traceId`、用户上下文和统一 deadline，不要让每个 future 自己决定超时时间。超过全局 deadline 后不要继续发起新工具调用。

## 6. ReAct 执行流程与防无限循环
1. ReAct 的核心是让模型交替产生 reasoning 和 action：理解问题，决定是否调用工具，拿到 observation，再继续推理，直到输出 final answer。
2. 典型状态包括 `Thought`、`Action`、`Action Input`、`Observation` 和 `Final Answer`。工程实现时可以把推理链映射成步骤状态或可观测日志，不一定完整暴露给用户。
3. 防无限循环的手段包括最大迭代次数、最大工具调用次数、全局超时、重复 action 检测、相同 observation 检测、工具失败次数上限、强制 final answer 和人工接管。
4. 高确定性业务要限制工具白名单、限制参数范围、关键动作加确认节点，不能让 LLM 自主决定下单、退款、删数据等动作。

## 7. 意图识别：LLM Router 与规则分类
1. 规则分类适合边界清晰、关键词强、合规要求高、低延迟和低成本的场景，例如退款、查订单、查物流、人工客服。
2. LLM Router 适合语义复杂、多意图、口语化表达强、需要结合上下文判断的场景，例如“我上次买的东西怎么还没到，能不能催一下”。
3. 推荐混合路由：规则处理高置信度和高风险意图，embedding 或轻量分类模型召回候选意图，LLM 只处理低置信度和语义复杂 case。
4. 工程上必须输出置信度、候选意图、拒识结果和兜底策略。低置信度不要强行路由，要澄清或转人工。

## 8. LangChain4j Chain 与 LangGraph4j StateGraph
1. LangChain4j 的 Chain 或 AI Service 更偏向把 prompt、memory、model、tool、RAG 组合成一次调用接口，适合简单问答、普通 RAG 和轻量多轮业务。
2. StateGraph 更像状态机和工作流编排，核心是共享 State、节点、边、条件路由、循环、持久化和中断恢复。
3. 必须用 Graph 的场景包括多步骤工具调用、循环反思、Human-in-the-loop、失败恢复、并行分支、状态持久化和可视化执行路径。
4. 总结：Chain 适合“把能力串起来”，Graph 适合“把过程管起来”。只要出现条件分支、循环、人工审批、checkpoint、长任务恢复，就应该考虑 Graph。

## 9. RAG 全流程、Chunking、混合检索和 Re-rank
1. RAG 分离线索引和在线检索生成。离线阶段包括文档采集、解析、清洗、元数据抽取、切分、向量化、入库；在线阶段包括 query 改写、召回、rerank、上下文压缩、提示词拼装、生成和引用溯源。
2. Chunking 要按文档类型设计：FAQ 一问一答切；说明文档按标题层级切；代码按类和方法切；表格要保留行列语义；规则文档要保留条款编号。
3. 固定长度切分适合快速落地，常见做法是 300 到 800 tokens 一个 chunk，并保留 10% 到 20% overlap；语义切分效果更好，但要识别标题、段落、句子和实体边界。
4. 混合检索一般是 BM25/关键词召回 + 向量召回。BM25 擅长精确词、编号、专有名词；向量检索擅长语义相似和口语化问题。
5. Re-rank 对 topK 候选做交叉编码器或 LLM rerank，提高最终上下文相关性。工程上要限制 rerank 数量和超时，否则 P99 会明显变差。

## 10. Redis 在 Agent 系统中存什么，对话历史大 Key 如何拆分
1. Redis/Tair 常存会话状态、短期记忆、流式 chunk、工具调用结果缓存、幂等 key、限流计数、分布式锁、RAG 热点查询缓存和任务进度。
2. 对话历史不要用一个超大 list 或 string 一直追加。推荐按 `sessionId + messageId + seq` 拆分，最近 N 轮放热缓存，完整历史落数据库或对象存储。
3. 流式输出可以按 chunk 序号存：`agent:stream:{messageId}:{seq}`，再存 `agent:stream:{messageId}:maxSeq`，续接时从前端已收到的 `seq` 之后继续读。
4. 大 key 风险是阻塞 Redis 单线程、网络传输大、删除慢、复制慢。治理方式是拆 key、设置 TTL、异步删除、控制 value 大小、用 SCAN 替代 KEYS、监控 bigkeys。

## 11. 订单查询、物流查询、优惠计算三个工具的 Agent 编排
1. 先做意图识别，判断是否需要订单、物流、优惠三个工具，然后抽取订单号、用户 ID、商品 ID、收货地等参数。
2. 编排方式是订单查询为根节点；物流查询依赖订单中的物流单号；优惠计算依赖订单商品、用户权益和当前活动。可以先查订单，再并行查物流和优惠。
3. 数据拼装给 LLM 时不要直接塞原始 JSON 全量字段，而是构造成 evidence：订单状态、支付金额、商品名、物流节点、预计到达、可用优惠、不可用原因。
4. 最终提示词要要求 LLM 只基于工具结果回答，不能编造物流状态、优惠金额或履约承诺。

## 12. 手撕算法：LRU 缓存
* 参考实现如下。

```java
import java.util.HashMap;
import java.util.Map;

class LRUCache {
    static class Node {
        int key;
        int value;
        Node prev;
        Node next;
        Node(int key, int value) {
            this.key = key;
            this.value = value;
        }
    }

    private final int capacity;
    private final Map<Integer, Node> map = new HashMap<>();
    private final Node head = new Node(-1, -1);
    private final Node tail = new Node(-1, -1);

    public LRUCache(int capacity) {
        this.capacity = capacity;
        head.next = tail;
        tail.prev = head;
    }

    public int get(int key) {
        Node node = map.get(key);
        if (node == null) {
            return -1;
        }
        moveToHead(node);
        return node.value;
    }

    public void put(int key, int value) {
        Node node = map.get(key);
        if (node != null) {
            node.value = value;
            moveToHead(node);
            return;
        }
        Node newNode = new Node(key, value);
        map.put(key, newNode);
        addAfterHead(newNode);
        if (map.size() > capacity) {
            Node removed = removeTail();
            map.remove(removed.key);
        }
    }

    private void moveToHead(Node node) {
        remove(node);
        addAfterHead(node);
    }

    private void addAfterHead(Node node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }

    private void remove(Node node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private Node removeTail() {
        Node node = tail.prev;
        remove(node);
        return node;
    }
}
```

# 二、二面
## 1. Agent 架构、QPS、P99、GPU 推理成本控制
1. 架构可以讲成网关接入层、Agent 编排层、工具执行层、RAG 知识层、模型服务层、状态存储层、观测与评测层。
2. QPS 控制靠入口限流、用户维度限流、模型 API 并发限流、工具 bulkhead、队列削峰和异步任务拆分。
3. P99 延迟要拆维度看：首 token 延迟、检索耗时、rerank 耗时、工具耗时、模型推理耗时、流式传输间隔、序列化和网络耗时。
4. GPU 成本控制包括模型分级路由、小模型优先、缓存相似问答、prompt 压缩、RAG topK 控制、批处理、量化、限流、降级和离线评测。
5. 监控指标包括 QPS、P50/P95/P99、首 token、tokens/s、模型错误率、工具错误率、重试率、fallback 率、token 成本、GPU 利用率和队列等待时间。

## 2. MySQL 大表分库分表与跨分片聚合
1. 分片键优先选高频查询条件和高基数字段，例如 `user_id`、`tenant_id`、`order_id`，不要选状态这类低基数字段。
2. 如果主要按用户查订单，用 `user_id` 分片；如果按订单号查详情，可以在订单号里嵌入分片位或维护路由表。
3. 跨分片聚合要尽量避免在线强聚合，常用方案是汇总表、宽表、ES/OLAP 异构索引、按分片并行查询后应用层 merge、限制深分页。
4. 分库分表后必须考虑全局 ID、事务边界、幂等、数据迁移、扩容 re-sharding 和灰度双写校验。

## 3. RocketMQ 事务消息与 Agent 异步长任务
1. RocketMQ 事务消息核心是半消息、本地事务、提交/回滚消息和事务状态回查，解决本地事务与消息发送的一致性。
2. 不丢消息靠 producer 发送确认、broker 持久化、消费重试和死信队列；幂等靠业务唯一键、状态机和去重表。
3. Agent 异步长任务可以设计为：请求入库生成 `taskId`，发送任务消息，worker 消费后执行 Agent/RAG/工具调用，持续更新任务状态和流式 chunk，失败可重试，最终状态为 success/fail/cancel。
4. 幂等关键是 `taskId + executionVersion`。用户重复提交时生成新版本，旧版本结果落库时条件更新失败，避免旧任务覆盖新任务。

## 4. 多级缓存在高并发 RAG 知识查询中的设计
1. 本地 Caffeine 存热点 query、embedding、rerank 结果或知识库元数据，优点是低延迟；Redis 存跨实例共享缓存，优点是容量大、可统一失效。
2. 缓存 key 要包含知识库版本、query 归一化结果、召回参数、embedding 模型版本、rerank 模型版本，否则知识更新后可能命中旧结果。
3. 缓存击穿用互斥锁、singleflight、逻辑过期和后台刷新；缓存穿透用空值缓存、布隆过滤器、参数校验；缓存雪崩用 TTL 随机抖动和分批预热。
4. 问答场景要谨慎缓存最终回答，因为答案可能与用户上下文、权限、时间有关；更推荐缓存检索结果、工具结果和可复用证据。

## 5. Sentinel 对 LLM API 限流降级与 GPU fallback
1. 对 LLM API 要按模型、租户、用户、接口和场景维度限流。限流指标可以是 QPS、并发数、排队时间、token 预算和错误率。
2. 降级策略分层：大模型失败转小模型，小模型失败转 RAG 摘要模板，仍失败转规则 FAQ 或人工客服。
3. GPU 推理服务挂了要先熔断，避免请求继续打满。fallback 时要标记能力降级，避免小模型承担高风险决策。
4. 关键是 deadline 传递：如果用户请求只剩 1 秒，不应该再走一个 5 秒的小模型 fallback。

## 6. LangGraph State、Checkpointer 与 Human-in-the-loop
1. State 是图执行过程的共享状态，节点读取 State 并返回局部更新，边根据 State 决定下一步。State 中应放跨节点需要的信息，例如 messages、toolResults、userProfile、approvalStatus、errorInfo。
2. Reducer 决定同一个字段如何合并更新，例如 messages 追加、score 覆盖、errors 追加。
3. Checkpointer 用来持久化线程级 graph state，适合短期记忆、会话连续性、中断恢复、Human-in-the-loop 和故障恢复。
4. Human-in-the-loop 可以在高风险节点前 interrupt，把当前 State 持久化，等待人工审批后 resume。审批结果写回 State，再继续执行。
5. 要区分 Checkpointer 和长期 Store：Checkpointer 管一次线程/会话的短期状态，Store 更适合跨会话长期记忆，比如用户偏好和事实。

## 7. 多 Agent Orchestrator-Worker、幂等和 Saga 补偿
1. Orchestrator 负责拆任务、分配 Worker、聚合结果和控制全局状态；Worker 负责专门能力，如检索、写作、审核、工具调用。
2. Agent 间幂等靠 `taskId`、`stepId`、`agentId`、`attemptId`、输入 hash 和输出版本。重复执行同一步时，如果输入 hash 不变，可以直接返回已有结果。
3. 超时重试要区分可重试和不可重试：查询类工具可重试，支付、下单、发券类动作必须幂等或走确认。
4. Saga 思路是每个正向动作配一个补偿动作，例如创建工单失败可关闭临时记录，发券失败可回滚权益占用。LLM 只能规划，真正补偿动作必须由确定性代码执行。

## 8. Agent 幻觉原因与缓解
1. 常见原因包括问题超出模型知识、RAG 召回错误、上下文过长、工具返回为空但模型强行补全、prompt 约束弱、缺少引用校验。
2. RAG 约束手段包括只允许基于检索证据回答、引用来源、答案前做 evidence coverage 检查、低置信度时拒答或澄清。
3. Self-Reflection 可以让模型在最终回答前检查“每个事实是否有证据支持”，但它不是强保证，关键事实仍要用规则或工具校验。
4. 工具结果校验包括 schema 校验、枚举值校验、金额/时间范围校验、业务状态机校验和二次查询确认。

## 9. Function Calling / Tool Use 参数校验与失败重试
1. 工具定义要有清晰 name、description、JSON Schema、必填字段、枚举、范围和示例。描述不清会直接影响模型选工具和传参质量。
2. 执行前做参数校验，失败时把可修复错误反馈给模型，让模型重填参数；不可修复错误直接走澄清或 fallback。
3. 重试策略要按错误类型区分：网络超时可指数退避重试，参数错误不应盲目重试，业务状态不允许时要停止。
4. 工具执行异常时 Agent 的 fallback 可以是换工具、降级到规则、要求用户补充信息、转人工或输出部分结果。

## 10. SSE / WebSocket 实现 Agent 流式输出和背压
1. SSE 适合服务端到客户端单向输出，简单、基于 HTTP、天然适合 token 流和进度事件；WebSocket 适合双向交互强、客户端也要频繁发控制消息的场景。
2. Java 后端关键点包括响应头、连接保活、心跳、异常结束、客户端断开感知、超时控制、序号化 chunk、断点续接和最终完成事件。
3. 背压问题来自模型生成太快、客户端消费慢、网络慢或服务端缓冲过大。处理方式是有界队列、按连接限速、丢弃无意义中间进度、心跳独立、慢连接熔断。
4. 生产上建议每个 chunk 带 `seq`、`messageId`、`type` 和 `timestamp`，便于前端去重、续接和观测。

## 11. 手撕算法：固定长度 + 语义 overlap 文本切分
* 参考实现如下。

```java
import java.util.ArrayList;
import java.util.List;

class Chunker {
    public static List<String> chunk(String text, int maxLen, int overlap) {
        List<String> ans = new ArrayList<>();
        if (text == null || text.isEmpty()) {
            return ans;
        }
        int start = 0;
        while (start < text.length()) {
            int end = Math.min(start + maxLen, text.length());
            int cut = findSemanticCut(text, start, end);
            if (cut <= start) {
                cut = end;
            }
            ans.add(text.substring(start, cut).trim());
            if (cut == text.length()) {
                break;
            }
            start = Math.max(cut - overlap, start + 1);
        }
        return ans;
    }

    private static int findSemanticCut(String text, int start, int end) {
        String marks = "。！？；\\n";
        for (int i = end - 1; i > start; i--) {
            if (marks.indexOf(text.charAt(i)) >= 0) {
                return i + 1;
            }
        }
        return end;
    }
}
```

# 三、三面
## 1. 自我介绍
1. 三面自我介绍要更偏“判断力”和“ owner 意识”。可以说：我不只关注模型调用是否成功，更关注 Agent 在业务里是否可控、可评测、可降级。我的优势是把 Java 工程稳定性、分布式系统经验和 AI 应用结合起来，能从 P99、成本、幻觉、工具幂等和用户体验几个维度把 Agent 做成可上线系统。

## 2. 项目最难技术问题与排查
1. 可以讲“流式 Agent 断点续接”或“RAG 召回质量不稳定”。以断点续接为例：问题是 MTOP/SSE 长连接断开后原流不可恢复，用户返回页面只能看到生成中，打字机效果丢失。
2. 排查过程包括确认连接生命周期、服务端 streamWriter 是否绑定旧连接、前端是否保存最大 seq、缓存是否有完整 chunk、结束状态是否可靠。
3. 解决方案是每个 chunk 写出前分配递增 seq，同时写入 Tair/Redis；前端断线后携带最大 seq 调 continue 接口；服务端开新流，从缓存中按 seq 回放并等待新 chunk；通过心跳、超时和 END 状态结束。
4. 结果可以用体验和稳定性描述：弱网恢复后可以续上已有内容，避免重复生成和用户长时间空白等待。

## 3. 为什么选 ReAct 而不是传统规则工作流
1. 规则工作流适合路径固定、状态明确、高确定性的业务，例如订单状态机、退款审核、库存扣减。
2. ReAct 适合用户表达复杂、工具选择动态、需要边观察边决策的任务，例如旅游规划、智能客服、复杂问答、跨系统查询。
3. 高确定性业务里 Agent 的自主性边界必须收紧：LLM 负责理解、规划、解释和候选动作；确定性代码负责权限、校验、状态变更和资金类动作。
4. 面试结论：不是用 ReAct 替代规则，而是用 ReAct 处理自然语言和动态规划，用规则系统兜住安全边界。

## 4. Agent P99 过高的排查思路
1. 模型推理维度看排队时间、首 token、tokens/s、上下文长度、模型规格、是否触发大模型 fallback。
2. 网络维度看客户端到网关、网关到模型、网关到工具的连接池、DNS、TLS、跨机房链路和丢包。
3. 工具超时维度看慢工具排行榜、单工具 P99、重试放大、串行依赖、线程池队列和外部服务限流。
4. 序列化维度看大 JSON、大上下文、大图片、流式 chunk 过细或过大、日志打印过量。
5. 解决上先做 trace 分段，再按耗时大头治理：并行化工具、设置 deadline、压缩 prompt、降低 topK、缓存检索、模型分级、慢工具熔断。

## 5. Hallucination 产生违规或虚假内容怎么拦截
1. 输入侧做敏感词、意图识别、越权检测和风险分级；检索侧做权限过滤、知识库版本控制和引用溯源；生成侧要求只基于证据回答。
2. 输出侧做敏感词、规则引擎、事实一致性二次校验、工具结果对账和高风险内容人工审核。
3. 对金额、政策、物流、签证、医疗、法律等高风险事实，不允许模型自由发挥，必须来自工具或知识库。
4. 低置信度时要拒答、澄清或转人工，而不是“看起来合理地编一个答案”。

## 6. 面试官收集数据用于微调或 Prompt 优化，数据标注闭环怎么设计
1. 数据来源包括线上对话、用户点赞点踩、人工客服改写、工具失败日志、RAG 无命中问题、投诉问题和评测集。
2. 标注维度包括意图、是否解决、是否幻觉、引用是否正确、工具是否选对、参数是否正确、回答是否合规、是否需要人工。
3. 闭环流程是采集、脱敏、抽样、标注、质检、构建 golden set、离线评测、prompt 或模型优化、灰度发布、线上指标回看。
4. 数据治理要注意隐私脱敏、权限隔离、标注一致性、坏样本去重和版本化评测，不能直接把原始用户敏感数据拿去训练。

## 7. 支持图片输入做向量化检索，多模态后端架构改造
1. 接入层要支持图片上传、格式校验、大小限制、病毒扫描、鉴权和对象存储。
2. 解析层增加 OCR、图像 caption、视觉 embedding、多模态 embedding；索引层要支持文本向量、图片向量和 metadata 联合检索。
3. 检索层可以做图片向量召回、OCR 文本召回、caption 文本召回和混合 rerank。
4. 生成层要把图片证据、OCR 文本、相似图片和业务 metadata 拼装给多模态模型或文本模型。
5. 安全侧要增加涉敏图片检测、隐私信息识别、水印和版权风险控制。

## 8. 最近在学什么 AI 新技术
1. 可以回答 MCP、A2A、LangGraph、多 Agent Harness、Agent 评测、上下文工程和多模态 RAG。
2. MCP 解决的是模型和外部工具/资源的标准化连接问题；A2A 关注 Agent 间通信和协作；LangGraph 关注有状态、可恢复、可中断的 Agent 工作流。
3. 快速上手新框架的方法是先跑官方 quick start，再看核心抽象，再做一个小 demo，然后读源码里的 example，最后接入一个真实业务小场景验证边界。

## 9. 如何跟进前沿论文或开源项目
1. 跟进路径可以是 arXiv、Papers with Code、GitHub Trending、LangChain/LlamaIndex/Spring AI Alibaba release notes、技术社区和内部分享。
2. 示例可以讲 ReAct：从论文里学到“推理 + 行动 + 观察”的循环模式，在项目里落成工具调用编排，但工程上增加最大步数、工具白名单、幂等、超时和 fallback。
3. 也可以讲 LangGraph：从开源项目学到 StateGraph、checkpoint 和 interrupt，然后应用到长任务 Agent 的状态持久化和人工审批。

## 10. 带新人做 Agent Harness，Code Review 和技术分享怎么做
1. Agent Harness 可以拆成 SDK、评测、可观测性三块。SDK 统一模型调用、工具 schema、trace、超时、重试和错误码；评测支持 golden set、自动打分、回归对比；可观测性记录 prompt、工具、latency、token、错误和用户反馈。
2. Code Review 重点看接口边界、幂等、超时、线程池、异常处理、日志脱敏、测试覆盖和是否把不确定性留给 LLM。
3. 技术分享按“一个概念 + 一个线上问题 + 一个可运行 demo + 一套 checklist”组织，让新人能直接迁移到工作里。
4. 对新人要设置小而完整的任务，例如实现一个工具 schema 校验器、一个评测 case runner、一个 SSE 心跳 demo，然后逐步扩展。

## 11. 手撕算法：余弦相似度
* 参考实现如下。

```java
class CosineSimilarity {
    public static double cosine(double[] a, double[] b) {
        if (a == null || b == null || a.length != b.length || a.length == 0) {
            throw new IllegalArgumentException("invalid embedding");
        }
        double dot = 0.0;
        double normA = 0.0;
        double normB = 0.0;
        for (int i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        if (normA == 0.0 || normB == 0.0) {
            return 0.0;
        }
        return dot / (Math.sqrt(normA) * Math.sqrt(normB));
    }
}
```

# 四、HR 面
## 1. 自我介绍
1. HR 面自我介绍少讲术语，多讲稳定性、协作和成长。示例：我是一名偏后端和 AI 应用工程的开发，做事比较重视结果闭环和长期可维护性。最近主要参与 AI Agent 和 RAG 方向，把大模型能力接入业务系统，同时关注稳定性、成本、用户体验和团队协作。我比较擅长把复杂问题拆成可落地的工程方案，也愿意做文档、分享和 Code Review，帮助团队一起提升。

## 2. 最有成就感的项目或技术难点
1. 可以选择“AI 预测/Agent 流式输出改造”。回答结构是背景、问题、行动、结果、复盘。
2. 示例：原来用户提交任务后只能轮询等待，模型其实已经在生成，但用户看不到进展。我负责把链路改造成流式输出，后端对接模型流、解析业务标签、按事件推送建议文本和评分结果，同时设计状态落库、异常结束和断点续接。难点是模型 chunk 边界不稳定、长连接会断、旧任务结果可能覆盖新任务。最后通过状态机解析、seq 缓存、executionVersion 乐观锁和心跳机制解决。这个项目让我比较有成就感，因为它既改善了用户体验，也把 AI 能力变成了稳定可上线的工程链路。

# 五、参考资料
1. ReAct 论文：[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
2. RAG 论文：[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
3. LangGraph 文档：[Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
4. LangChain4j 文档：[AI Services](https://docs.langchain4j.dev/tutorials/ai-services/) 和 [RAG](https://docs.langchain4j.dev/tutorials/rag/)
5. MDN 文档：[Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
6. Oracle 文档：[The Z Garbage Collector](https://docs.oracle.com/en/java/javase/24/gctuning/z-garbage-collector.html)
7. Redis 资料：[7 Redis Worst Practices](https://redis.io/blog/7-redis-worst-practices/)

