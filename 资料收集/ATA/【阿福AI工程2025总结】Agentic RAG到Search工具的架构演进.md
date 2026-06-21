---
title: "【阿福AI工程2025总结】Agentic RAG到Search工具的架构演进"
source: "https://ata.atatech.org/articles/12020576821"
author:
published:
created: 2026-04-21
description:
---
# 【阿福AI工程2025总结】Agentic RAG到Search工具的架构演进

卧舟

** 275

** 326

** 34

**

**

[周华磊(卧舟)](https://ata.atatech.org/users/12000238777)

1月30日发表1月31日更新5.9k浏览

** 朗读

** 字号

** 笔记

** 分享 **

朗读文章13:48

**

> 本文作者（排名不分先后）：狗卷、方牧、以渊、卧舟

阿福AI工程2025总结系列文章汇总：

1. 【阿福AI工程2025总结】从Agentic RAG到Search工具的架构演进
2. [【阿福AI工程2025总结】从通用到医疗：Benchmark构建的认知升级](https://ata.atatech.org/articles/12020576421)
3. [【阿福AI工程2025总结】DeepSearch Benchmark实践小结](https://ata.atatech.org/articles/12020577608)
4. [【阿福AI工程2025总结】生成式UI架构实践](https://ata.atatech.org/articles/12020576020)
5. 【阿福AI工程2025总结】大模型时代的研发范式探索（敬请期待）

## 前言：2025业界发展

> RAG大势已定、谋事在人、干在业务、干中学、干中发展、做适合做的事情且长期做才是出路。
> —公众号《老刘说NLP》

2025年RAG技术不再追求概念炒作，而是走向了务实的“工业化”阶段，一个明显的指标是论文数量明显变少了。总结这一年，可以从以下几个方面来概括：

1）从“概念炒作”到“工业化”

RAG没有被长上下文（Long Context）取代，而是两者相互配合，达成了“检索前置，长窗口容纳”的共识，RAG负责筛选高质量信息喂给大模型。框架也开始逐步收敛，开源的开发框架从百花齐放收敛为 Dify、RAGFlow 等少数几个主流头部，行业进入优胜劣汰的稳定期。

2）从“暴力分块”到“结构化认知”

标准化PTI：流程升级为 PTI（解析-转换-索引），不再只是简单的切片，而是强调利用大模型进行深度的文档解析和语义增强,。

精细化检索：解决了切片破碎的问题。采用 TreeRAG（树状索引）先定位再展开，或者 Search vs Retrieve（搜索定位线索，检索组装内容）的分离策略。

结构化融合：GraphRAG从“暴力预构建”转向“按需构建”或与树状索引结合，以降低成本并提升跨文档推理能力。此外，TreeRAG或者PageIndex等树状索引结构开始受到业界的关注。

3）从“检索引擎”到“上下文引擎”

RAG 进化为 Context Engine（上下文引擎）。它不仅检索文档，还开始检索记忆和工具。比如，当Agent 面对成百上千个工具时，硬编码已经不再适合，通过RAG动态检索出最合适的工具和使用指南或许成为一种务实的选择。

4）从“文本”到“多模态”

PDF文件已不再单纯依赖 OCR 转文字，而是开始通过多模态索引保留图像和文档的视觉语义，虽然存储成本较高，但已成为处理复杂图表文档的主流方向。

## 一、阿福RAG1.0架构：Agentic RAG

## 在线检索架构

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F40f0944e-dcfa-4a14-bf76-0b7833df7b55.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

## Query路由

场景：用户query复杂，而医疗检索库多样；针对用户复杂query，检索相关且有用的知识。

核心优化：意图规则 转向 模型理解规划；

### V1方案：意图规则

意图tag：医保、医疗、医生、医院、非医疗；根据意图tag规划检索库；

问题：强依赖意图tag准确率；多意图问题的知识检索会有检索不全面问题；

### V2方案：检索Planner

检索planner模型去规划检索的数据库&检索词。

![[IMG-20260531150548293.avif]]

## 召回

持续优化向量检索，提升 标准库建设&抽槽检索 的重要性。

### 1）非结构化召回

离在线链路

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F37e5d2eb-01ab-46d6-b0e9-49e90067d1f9.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

在线迭代方向：快速评测&运用业界最新的向量模型；

早期线上bge-m3 embedding模型存在一些问题，会导致一些badcase，需要进行优化，Qwen3-Embedding在向量检索上表现出较佳的性能；

![[IMG-20260531150548313.avif]]

微调Qwen3-Embedding 相对 bge-m3 效果优化：recall + 1.15%，hit@1 + 9.8%；

### 2）结构化召回

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F230f98ab-754b-448d-8f67-b34e56e7c541.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

- 标准库数据生产；
- 索引构建；
- 在线槽位抽取&标化；
- 数据补全&排序；

## 排序

embedding相似度打分排序 -> 多维度打分&排序；

文献多维度打分&排序：相关性、完整性、有用性、权威性、时效性；

## 1.0架构存在的问题

1）误差累积：整个检索链路依赖了多个小模型：query改写模型、检索planner模型、是否rag模型、时效tag模型等，模型之间相互依赖，且链路的累积误差较大。

2）架构耦合：检索效果和agent回复效果的边界模糊，整个端到端效果强依赖检索，检索变更强依赖端上benchmark正向。检索本身缺少各方达成一致的benchmark，无法更好得指导检索的效果优化。

3）效果天花板：一些复杂问题，缺少推理&多步检索的能力。

## 二、阿福RAG2.0架构之工具化

## 架构升级背景

基于RAG1.0架构中的遇到的种种问题，我们开始推进RAG2.0架构的方案，整套架构从Workflow模式升级为Agent模式，在这套架构中，检索能力以Search工具的形式提供给中枢LLM进行调用，架构变得更加简洁，天花板也会更高。一下就是我们OneModel架构的示例：

- query改写、是否rag、检索plan节点 集成到 planner，减少小模型；
- RAG和Agent卡片里的编排workflow连下线
- planner react方式调用search工具，解决需要多步推理的复杂检索问题；
- search和agent回复解耦，search工具专注search-benchmark；

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F232aeac5-0da9-48c8-8eb7-f01c7d0fe994.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

## 落地场景1：DeepSearch Agent

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F86b98d9e-9242-4e59-bd88-a36ff3fed47f.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

1）持续建设deepSearch场景端到端benchmark 和 search tool benchmark；

2）持续构建医疗权威文献库；

3）持续优化权威检索：

> 权威&时效召回，文献PICO标签使用；
> 权威文献判别过滤能力优化，主要是开源模型 + pe；
> 权威文献排序能力优化，主要是微调模型；

## 落地场景2：阿福主bot

![[IMG-20260531150548371.avif]]

## 三、阿福RAG2.0架构之平台化

## 平台架构

医疗RAG经过1年半的发展，架构已经基本成型，今年开始逐步进行平台化能力建设，力求打造一个更好的检索引擎，从而支撑阿福更快的迭代速度。

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F4cb6f2e3-a9fb-46ca-ac2d-3082bcfbc5f9.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

## 索引构建

RAG 平台能力的核心是统一管理大批量、多源、异构、动态更新的知识库。经过一年的建设，平台沉淀了权威知识 库 5亿条数据，医疗网页垂搜库164w数据，医保网页垂搜库7.8w篇文章。

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2Fadbb20b5-9520-4c71-8f65-68bd48e7da3a.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

产品界面：

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2Fc352257b-f149-4508-b8b9-544095b6b534.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

## 离线ETL

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F30fe8f2f-5ed2-4cda-9dc1-573b7838deb4.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

实时（增量）/离线（全量）数据流程，对于内容数据和索引数据进行分离，相同内存水位下提高存储量：

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F45ff2a4f-49e2-4992-b3bf-aa03fd56c772.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

离线计算流程

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F311e347f-50cf-408b-a4e8-0eec802d0116.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

针对不同来源的数据，我们基于主子任务的离线批处理框架 构建数据加工的pipeline： 非结构化数据引入 -> 数据预处理 -> 分块（Chunking）-> 索引（Indexing） -> 数据资产入库

**分块环节**

我们实现了下述分块方案，并支持不同业务定制和组合分块方案：

- Fixed-size chunking
- Sentence splitting
- Recursive chunking
- Specialized chunking
- Lumber Chunking
- RAPTOR

**索引&** 数据资产入库 **环节**

我们实现了下述索引方案，也支持不同业务定制和组合索引方案：

| **索引方案** | **特点** |
| --- | --- |
| 基于分块全文 | \+ 支持使用q2doc 的Embedding模型进行检索   \+ 支持 BM25 检索   \+ 支持 Sparse 稀疏向量检索 |
| 基于总结或标题 | \+ 概括chunk数据的主旨，便于检索分块主要信息 |
| 基于假设性问题 | \+ 对chunk数据构建假设性问题，便于检索分块内信息细节 |

## 评测中心

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2Fce424b97-d36a-4781-a260-a334de7465e7.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

- GroundTruth构造：通过 扩搜 &大尺寸模型判别 获取并拟合 q2docs 的 groundTruth；根据q2docs groundTruth计算召回模块的指标；
- 漏斗分析：数据库节点、召回节点、判别节点、重排节点；计算每个节点的指标 & 定位goodDoc 在每个节点的流失率；

产品界面：

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2Fdd1c454e-027f-4745-8b80-b078e933bbc1.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

## 调试中心

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F9c412c81-c351-4ea3-8fce-6a2d7f02fd05.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

## 四、未来规划

今年我们也在医学循证检索和多模态检索领域进行了一定的探索，也有了几个落地场景，26年我们将继续打磨相应的技术能力，从而做出一定的技术先进性。

## 医学循证检索

### 概述

医学循证检索是将检索增强生成（RAG）技术与循证医学（EBM）核心理念深度融合，专为医疗健康领域量身打造的智能信息检索与生成范式。其核心目标是打破传统医疗信息检索的碎片化、非标准化困境，基于“证据优先、分级采信、可追溯、可验证”的原则，实现医疗知识的精准召回、科学筛选、层级排序与规范生成，为临床决策、医学研究、药物研发、医患沟通等核心场景提供高质量、高可信度的信息支撑。

循证医学（英语：Evidence-based medicine，缩写为EBM），是一种医学诊疗方法，它将证据依知识论上的强度分类，并要求只有强度最高的证据（如元分析、系统性评论和随机对照试验）才能归纳为有力的建议证据；相对较无力的证据（如专家意见、动物实验、细胞实验、基本原理推论）只能归入有力程度不高的建议。

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F7e794f28-ebc4-4493-aaea-72669e0a86d0.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

### PICO模型

**PICO模型** 是循证医学中规范临床问题、精准定位循证证据的核心工具，也是医疗RAG循证检索实现“检索请求精准解析”的核心依据，其本质是通过结构化拆解临床问题，将模糊的医疗诉求转化为可检索、可验证的标准化问题，确保检索范围精准、证据匹配度高，避免因问题表述模糊导致的检索偏差。

PICO模型：

- **P (Patient/Problem)** ：患者或人群特征
- **I (Intervention)** ：干预措施
- **C (Comparison)** ：对照措施（可选）
- **O (Outcome)** ：希望观察的结果

> 示例：对于患有2型糖尿病的中年患者（P），使用二甲双胍（I）相比磺脲类药物（C），能否更有效降低HbA1c水平并减少低血糖事件（O）？

### EBM（Evidence-based medicine）检索

医学循证检索的全链路闭环的核心，依赖于检索系统的高效运转，而RAG检索系统通常包含两大核心部分： **召回、过滤&重排** 。针对医疗循证场景的精准性需求，本文重点引入基于循证医学（ Evidence-based medicine, EBM）的召回与过滤&重排机制，二者协同发力，为高质量循证证据的精准获取提供核心技术支撑。

#### EBM召回

PICOs-RAG方法旨在解决在循证医学（Evidence-Based Medicine, EBM）中，检索增强生成（Retrieval-Augmented Generation, RAG）模型处理复杂、非专业或信息不完整的用户查询时所面临的挑战。现有的RAG方法在处理此类查询时，常因检索到不相关的证据而导致大型语言模型（LLMs）生成无益或不准确的回答。PICOs-RAG通过查询重写和PICO（Population, Intervention, Comparison, Outcome）信息提取来优化这一过程，从而显著提升了检索效率和响应相关性。核心步骤：

1. 查询分类
2. 查询扩展与规范化
3. PICOS提取
4. 证据检索
5. 答案评估

![[IMG-20260531150548427.avif]]

#### EBM过滤&重排

META-RAG提出了一种面向循证医学（Evidence-Based Medicine, EBM）的检索增强生成（RAG）方法，核心创新在于借鉴Meta-Analysis（荟萃分析）思想，对检索到的医学证据进行再排序与过滤，以提升大模型生成答案的准确性和可靠性。核心步骤：

1. 可靠性分析（Reliability Analysis）：评估每篇证据的研究质量，筛除低质量文献。
2. 异质性分析（Heterogeneity Analysis）： 排除结论不一致或相互矛盾的证据。
3. 外推性分析（Extrapolation Analysis）： 判断证据是否适用于当前患者背景。

![](https://ata.atatech.org/router/file/redirect?url=https%3A%2F%2Foss-ata.alibaba.com%2Farticle%2F2026%2F01%2F7043c010-12f0-43ca-9c8b-e386098345c1.png&kind=ARTICLE&process=image/auto-orient,1/resize,m_lfit,w_1600/quality,Q_80/format,webp)

## 多模态检索

图文并茂已经是大势所趋，今年我们也在健康小目标场景进行了一些探索，并且收获了一致的好评：

![[IMG-20260531150548483.avif]]

2026年，我们将在图片库建设和多模态检索效果上持续发力，把阿福里专业枯燥的医学知识用图文并茂的方式呈现出来。

![[IMG-20260531150548503.avif]]

## 五、招聘帖

蚂蚁阿福AI工程团队持续招聘中~ 对Agent架构、DeepSearch Agent、多模态RAG、生成式UI、Memory等等最前沿的技术有过探索的同学可以私聊我，期待你的加入。

END

前言：2025业界发展

一、阿福RAG1.0架构：Agentic RAG

在线检索架构

Query路由

V1方案：意图规则

V2方案：检索Planner

召回

1）非结构化召回

2）结构化召回

排序

1.0架构存在的问题

二、阿福RAG2.0架构之工具化

架构升级背景

落地场景1：DeepSearch Agent

落地场景2：阿福主bot

三、阿福RAG2.0架构之平台化

平台架构

索引构建

离线ETL

评测中心

调试中心

四、未来规划

医学循证检索

概述

PICO模型

EBM（Evidence-based medicine）检索

EBM召回

EBM过滤&重排

多模态检索

五、招聘帖

**

**

有什么问题，和我聊聊吧～

**

内部资料

INTERNAL

405832