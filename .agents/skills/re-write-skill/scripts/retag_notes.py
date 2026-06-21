#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
from collections import defaultdict
from pathlib import Path

import yaml


FRONTMATTER_RE = re.compile(r"^\ufeff?---\n(.*?)\n---\n?", re.S)
HEADING_RE = re.compile(r"^#+\s*(.+?)\s*$", re.M)
BOLD_RE = re.compile(r"\*\*([^*\n]{1,80})\*\*")
INLINE_CODE_RE = re.compile(r"`([^`\n]{1,80})`")
ANNOTATION_RE = re.compile(r"@\w+")
CAMEL_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:[A-Z][A-Za-z0-9]*)+\b")
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}(?:/[A-Z]+)?\b")
CONFIG_RE = re.compile(r"\b[a-z]+(?:[.-][a-z0-9]+){1,5}\b")
ASCII_RE = re.compile(r"^[A-Za-z0-9 .+\-_/&]+$")
PACKAGE_LIKE_RE = re.compile(r"\b[a-z]+(?:\.[A-Za-z0-9_]+){1,}\b")

GENERIC_LABELS = {
    "",
    "介绍",
    "概述",
    "基础",
    "原理",
    "流程",
    "步骤",
    "方法",
    "场景",
    "特点",
    "特性",
    "规则",
    "说明",
    "总结",
    "应用",
    "实现",
    "需求",
    "作用",
    "源码",
    "优点",
    "缺点",
    "运行结果",
    "比较",
    "使用",
    "使用方式",
    "使用步骤",
    "核心流程",
    "工作机制",
    "前提知识",
    "代码示例",
    "参数配置",
    "处理流程",
    "处理规则",
    "简单功能分析",
    "功能分析",
    "面试题",
    "综合知识",
    "注意点",
    "工具类",
    "习题",
    "常用 API",
    "常用API",
    "代码案例演示",
    "图解",
    "Read",
    "Done",
    "Fields",
    "Untitled",
}

ALLOWED_LOWER_ASCII_TAGS = set()

SENTENCE_HINTS = {
    "为什么",
    "怎么",
    "如何",
    "什么是",
    "什么情况下",
    "可以",
    "需要",
    "必须",
    "是否",
    "原因",
}

LONG_PHRASE_HINTS = {
    "执行",
    "调用",
    "创建",
    "获得",
    "获取",
    "返回",
    "进行",
    "支持",
    "提升",
    "优化",
    "简化",
    "解决",
    "维护",
    "引起",
    "根据",
    "改进",
    "生成",
}

STRUCTURAL_STOP_PARTS = {
    "案例",
    "运行结果",
    "一般做法",
    "在业务中使用",
    "维护的线程池",
    "子任务和汇总任务",
    "两个任务之间",
    "注意点",
    "介绍",
}

TECH_HINTS = (
    "锁",
    "缓存",
    "线程",
    "并发",
    "异步",
    "同步",
    "中断",
    "通信",
    "原子性",
    "可见性",
    "有序性",
    "内存",
    "模型",
    "屏障",
    "参数",
    "配置",
    "内容协商",
    "静态资源",
    "请求",
    "响应",
    "事务",
    "注解",
    "容器",
    "代理",
    "注册",
    "发现",
    "熔断",
    "限流",
    "路由",
    "网关",
    "回收",
    "回收器",
    "GC",
    "类加载",
    "字节码",
    "集合",
    "队列",
    "Future",
    "Latch",
    "Barrier",
    "Semaphore",
    "Lock",
    "Bean",
    "AOP",
    "IOC",
    "SQL",
    "Mapper",
    "API",
)

TOKEN_STOPWORDS = {
    "Java",
    "String",
    "Integer",
    "Long",
    "Object",
    "Class",
    "Map",
    "List",
    "Set",
    "HashMap",
    "ArrayList",
    "LinkedList",
    "System",
    "Override",
    "Autowired",
    "Component",
    "Controller",
    "Request",
    "Response",
    "Server",
    "Builder",
    "Main",
    "SESSION",
    "STATEMENT",
    "CPU",
    "CG",
    "XX",
    "META",
    "INF",
    "resource",
    "resources",
    "static",
    "public",
    "classpath",
    "jpg",
    "jpeg",
    "png",
    "gif",
    "localhost",
    "true",
    "false",
    "null",
    "void",
}

SUFFIX_PATTERNS = [
    re.compile(r"(介绍|概述|总结|原理解析|原理分析|说明|详解|实战|面试题|知识点)$"),
    re.compile(r"(工具锁)$"),
]

TOPIC_PREFIX_PATTERNS = [
    re.compile(r"^(什么是|为什么|如何|怎么|哪些|哪几种|什么时候|什么情况下(?:的)?)\s*"),
    re.compile(r"^(特点|条件|方式|步骤)\s*[一二三四五六七八九十0-9]+\s*[：:]\s*"),
]

TOPIC_SUFFIX_PATTERNS = [
    re.compile(r"(的核心流程|的工作机制|的使用步骤|的处理流程|的处理规则|的实现原理|的原理|的配置|的区别|失效的场景)$"),
    re.compile(r"(核心流程|工作机制|前提知识|代码示例|参数配置|处理流程|处理规则)$"),
    re.compile(r"(简介|介绍|概述|总结|详解|说明)$"),
]

CANONICAL_TAG_ALIASES = {
    "cf": "CompletableFuture",
    "volatile": "volatile关键字",
    "synchronized": "synchronized关键字",
    "namespace": "命名空间",
    "jps": "JPS",
    "jconsole": "JConsole",
    "javap": "javap工具",
    "springboot": "Spring Boot",
    "springboot快速开始": "Spring Boot",
    "springcloud": "Spring Cloud",
    "springmvc": "Spring MVC",
    "spring原理解析": "Spring",
    "java8": "Java 8",
    "java8新特性": "Java 8",
    "io流": "IO流",
    "streamapi": "Stream API",
    "lambda表达式": "Lambda 表达式",
    "mybatisplus": "MyBatis-Plus",
    "reentrantlock": "ReentrantLock",
    "reentrantreadwritelock": "ReentrantReadWriteLock",
    "stampedlock": "StampedLock",
    "countdownlatch": "CountDownLatch",
    "cyclicbarrier": "CyclicBarrier",
    "threadlocal": "ThreadLocal",
    "blockingqueue": "BlockingQueue",
    "concurrenthashmap": "ConcurrentHashMap",
    "copyonwritearraylist": "CopyOnWriteArrayList",
    "completablefuture": "CompletableFuture",
    "futuretask": "FutureTask",
    "forkjoin": "ForkJoin",
    "threadpoolexecutor": "ThreadPoolExecutor",
    "classloader": "ClassLoader",
    "stringtable": "StringTable",
    "javap": "javap",
    "localcache": "LocalCache",
    "sqlsession": "SqlSession",
    "mappedstatement": "MappedStatement",
    "beanfactory": "BeanFactory",
    "applicationcontext": "ApplicationContext",
    "dispatcherservlet": "DispatcherServlet",
    "handlermapping": "HandlerMapping",
    "handleradapter": "HandlerAdapter",
    "configurationproperties": "@ConfigurationProperties",
    "feignclient": "FeignClient",
    "methodhandler": "MethodHandler",
    "methodhandle": "MethodHandle",
    "openfeign": "OpenFeign",
    "mybatis一级缓存": "一级缓存",
    "mybatis二级缓存": "二级缓存",
    "一级缓存原理": "一级缓存",
    "二级缓存原理": "二级缓存",
    "g1垃圾回收器": "G1 垃圾回收器",
    "cms垃圾回收器": "CMS",
    "minorgc": "Minor GC",
    "fullgc": "Full GC",
    "mixedgc": "Mixed GC",
    "stw": "STW",
    "juc": "并发编程",
    "jmm": "JMM",
    "jvm": "JVM",
}

PATH_ALIASES = {
    "Java 开发": ["Java", "后端开发"],
    "JUC": ["并发编程"],
    "JVM": ["JVM"],
    "Java": ["Java基础"],
    "MyBatis": ["MyBatis"],
    "MyBatis-Plus": ["MyBatis-Plus"],
    "Netty": ["Netty"],
    "Spring 原理解析": ["Spring"],
    "SpringBoot": ["Spring Boot"],
    "SpringCloud": ["Spring Cloud"],
    "ElasticSearch": ["Elasticsearch"],
    "MySQL": ["MySQL"],
    "Nginx": ["Nginx"],
    "RabbitMQ": ["RabbitMQ"],
    "Redis": ["Redis"],
    "ZooKeeper": ["ZooKeeper"],
    "Docker": ["Docker"],
    "Kubernetes": ["Kubernetes", "K8s"],
    "Linux": ["Linux"],
    "Shell": ["Shell"],
    "Git": ["Git"],
    "计算机网络": ["计算机网络"],
}

DOMAIN_DEFAULTS = {
    "Java 开发": ["Java", "后端开发", "工程实践"],
    "SpringBoot": ["Spring Boot", "Web开发"],
    "SpringCloud": ["Spring Cloud", "微服务"],
    "MyBatis": ["数据访问", "ORM"],
    "JUC": ["并发编程", "多线程"],
    "JVM": ["JVM", "Java底层"],
    "Java": ["Java基础", "语言特性"],
}

KEYWORD_TAGS = [
    ("spring boot", "Spring Boot"),
    ("springboot", "Spring Boot"),
    ("spring cloud", "Spring Cloud"),
    ("springcloud", "Spring Cloud"),
    ("spring mvc", "Spring MVC"),
    ("springmvc", "Spring MVC"),
    ("spring", "Spring"),
    ("mybatis-plus", "MyBatis-Plus"),
    ("mybatis", "MyBatis"),
    ("openfeign", "OpenFeign"),
    ("feignclient", "FeignClient"),
    ("服务调用", "服务调用"),
    ("动态代理", "动态代理"),
    ("远程调用", "远程调用"),
    ("负载均衡", "负载均衡"),
    ("ribbon", "Ribbon"),
    ("nacos", "Nacos"),
    ("注册中心", "服务注册"),
    ("配置中心", "配置中心"),
    ("gateway", "Gateway"),
    ("路由", "路由"),
    ("sentinel", "Sentinel"),
    ("熔断", "熔断降级"),
    ("降级", "熔断降级"),
    ("限流", "流量控制"),
    ("hystrix", "Hystrix"),
    ("断路器", "断路器"),
    ("seata", "Seata"),
    ("静态资源", "静态资源"),
    ("静态映射", "资源映射"),
    ("static-path-pattern", "静态资源路径"),
    ("static-locations", "静态资源目录"),
    ("meta-inf/resources", "静态资源目录"),
    ("欢迎页", "欢迎页"),
    ("favicon", "favicon"),
    ("内容协商", "内容协商"),
    ("文件上传", "文件上传"),
    ("restful", "RESTful"),
    ("json", "JSON"),
    ("yaml", "YAML"),
    ("yml", "YAML"),
    ("@configurationproperties", "@ConfigurationProperties"),
    ("configurationproperties", "@ConfigurationProperties"),
    ("dispatcherServlet", "DispatcherServlet"),
    ("handlermapping", "HandlerMapping"),
    ("handleradapter", "HandlerAdapter"),
    ("ioc", "IOC"),
    ("aop", "AOP"),
    ("事务", "事务"),
    ("循环依赖", "循环依赖"),
    ("三级缓存", "三级缓存"),
    ("beanfactory", "BeanFactory"),
    ("applicationcontext", "ApplicationContext"),
    ("bean 生命周期", "Bean生命周期"),
    ("bean的生命周期", "Bean生命周期"),
    ("自动配置", "自动配置"),
    ("自动装配", "自动装配"),
    ("starter", "Starter"),
    ("一级缓存", "一级缓存"),
    ("二级缓存", "二级缓存"),
    ("sqlsession", "SqlSession"),
    ("mappedstatement", "MappedStatement"),
    ("executor", "Executor"),
    ("namespace", "namespace"),
    ("mapper", "Mapper"),
    ("延迟加载", "延迟加载"),
    ("插件", "插件机制"),
    ("动态 sql", "动态SQL"),
    ("resultmap", "ResultMap"),
    ("juc", "并发编程"),
    ("jmm", "JMM"),
    ("volatile", "volatile"),
    ("线程安全", "线程安全"),
    ("异步", "异步"),
    ("同步", "同步"),
    ("可见性", "可见性"),
    ("原子性", "原子性"),
    ("有序性", "有序性"),
    ("cpu 缓存", "CPU缓存"),
    ("happens-before", "Happens-Before"),
    ("happens before", "Happens-Before"),
    ("内存模型", "内存模型"),
    ("指令重排", "指令重排"),
    ("内存屏障", "内存屏障"),
    ("aqs", "AQS"),
    ("cas", "CAS"),
    ("unsafe", "Unsafe"),
    ("locksupport", "LockSupport"),
    ("reentrantlock", "ReentrantLock"),
    ("公平锁", "公平锁"),
    ("非公平锁", "非公平锁"),
    ("条件变量", "条件变量"),
    ("可重入", "可重入锁"),
    ("可中断", "可中断锁"),
    ("reentrantreadwritelock", "ReentrantReadWriteLock"),
    ("stampedlock", "StampedLock"),
    ("countdownlatch", "CountDownLatch"),
    ("cyclicbarrier", "CyclicBarrier"),
    ("semaphore", "Semaphore"),
    ("线程间的通讯", "线程协作"),
    ("线程间的通信", "线程协作"),
    ("线程协作", "线程协作"),
    ("threadlocal", "ThreadLocal"),
    ("blockingqueue", "BlockingQueue"),
    ("concurrenthashmap", "ConcurrentHashMap"),
    ("copyonwritearraylist", "CopyOnWriteArrayList"),
    ("completablefuture", "CompletableFuture"),
    ("futuretask", "FutureTask"),
    ("fork - join", "ForkJoin"),
    ("fork-join", "ForkJoin"),
    ("threadpoolexecutor", "ThreadPoolExecutor"),
    ("线程池", "线程池"),
    ("拒绝策略", "拒绝策略"),
    ("线程中断", "线程中断"),
    ("线程通信", "线程通信"),
    ("死锁", "死锁"),
    ("进程", "进程"),
    ("线程", "线程"),
    ("jvm", "JVM"),
    ("双亲委派", "双亲委派"),
    ("classloader", "ClassLoader"),
    ("类加载器", "类加载器"),
    ("类加载", "类加载"),
    ("垃圾回收器", "垃圾回收器"),
    ("垃圾回收", "垃圾回收"),
    ("复制算法", "复制算法"),
    ("cms", "CMS"),
    ("g1", "G1"),
    ("zgc", "ZGC"),
    ("minor gc", "Minor GC"),
    ("full gc", "Full GC"),
    ("mixed gc", "Mixed GC"),
    ("混合回收", "混合回收"),
    ("stw", "STW"),
    ("region", "Region"),
    ("eden", "Eden"),
    ("survivor", "Survivor"),
    ("新生代", "新生代"),
    ("老年代", "老年代"),
    ("humongous", "Humongous"),
    ("运行时常量池", "运行时常量池"),
    ("stringtable", "StringTable"),
    ("程序计数器", "程序计数器"),
    ("虚拟机栈", "虚拟机栈"),
    ("堆", "堆内存"),
    ("方法区", "方法区"),
    ("直接内存", "直接内存"),
    ("javap", "javap"),
    ("字节码", "字节码"),
    ("java 8", "Java 8"),
    ("io 流", "IO流"),
    ("stream api", "Stream API"),
    ("lambda 表达式", "Lambda 表达式"),
    ("optional", "Optional"),
    ("supplier", "Supplier"),
    ("consumer", "Consumer"),
    ("predicate", "Predicate"),
    ("function", "Function"),
    ("方法引用", "方法引用"),
    ("构造器引用", "构造器引用"),
    ("函数式接口", "函数式接口"),
    ("反射", "反射"),
    ("泛型", "泛型"),
    ("spi", "SPI"),
    ("netty", "Netty"),
]


class PrettyDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild note tags with 5-6 semantic tags while preserving note bodies."
    )
    parser.add_argument("--root", required=True, help="Root directory containing markdown notes.")
    parser.add_argument(
        "--updated",
        default=dt.date.today().isoformat(),
        help="Value for the updated frontmatter field. Default: today.",
    )
    parser.add_argument(
        "--max-hierarchy-depth",
        type=int,
        default=3,
        help="Maximum number of hierarchy tags to keep. Default: 3.",
    )
    parser.add_argument(
        "--content-priority",
        action="store_true",
        help="Prefer tags summarized from the note content and use path tags only as fallback.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files.",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=20,
        help="How many changed files to print in the summary. Default: 20.",
    )
    return parser.parse_args()


def split_frontmatter(text: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text.lstrip("\ufeff")
    return match.group(1), text[match.end() :]


def load_frontmatter(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        loaded = yaml.safe_load(raw)
        return dict(loaded) if isinstance(loaded, dict) else {}
    except Exception:
        return {}


def quote_scalar(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def alias_key(value: str) -> str:
    return re.sub(r"[\s._/\-+@]+", "", value).lower()


def canonicalize_term(value: str) -> str:
    cleaned = normalize_space(value).strip(" .,:;，。；：!?？/|")
    if not cleaned:
        return ""
    alias = CANONICAL_TAG_ALIASES.get(alias_key(cleaned))
    return alias or cleaned


def format_tag(value: str) -> str:
    segments: list[str] = []
    for part in value.split("/"):
        cleaned = normalize_space(part).strip(" _./")
        if not cleaned:
            continue
        cleaned = re.sub(r"[.\s]+", "_", cleaned)
        cleaned = re.sub(r"_+", "_", cleaned).strip("_")
        if cleaned:
            segments.append(cleaned)
    return "/".join(segments)


def clean_label(value: str) -> str:
    cleaned = normalize_space(value)
    cleaned = re.sub(r"^Export-[^/]+/", "", cleaned)
    cleaned = re.sub(r"^\d+(?:[.\s]+\d+)*\s*[.、\-]?\s*", "", cleaned)
    cleaned = re.sub(r"^[#>*\-\s]+", "", cleaned)
    cleaned = cleaned.replace("`", "")
    cleaned = cleaned.replace("*", "")
    cleaned = cleaned.replace("==", "")
    cleaned = cleaned.replace("（", "(").replace("）", ")")
    cleaned = re.sub(r"[🔥✔️⚔️❓🐮😡⭐🙋‍♂️📑]+", "", cleaned)
    cleaned = normalize_space(cleaned).strip(" .-_/")
    for pattern in SUFFIX_PATTERNS:
        candidate = pattern.sub("", cleaned).strip(" .-_/")
        if candidate:
            cleaned = candidate
    return normalize_space(cleaned)


def normalize_topic(value: str) -> str:
    cleaned = clean_label(value)
    for pattern in TOPIC_PREFIX_PATTERNS:
        cleaned = pattern.sub("", cleaned).strip()
    for pattern in TOPIC_SUFFIX_PATTERNS:
        candidate = pattern.sub("", cleaned).strip(" .-_/")
        if candidate:
            cleaned = candidate
    cleaned = cleaned.strip("：:，,。;；!?？")
    return canonicalize_term(cleaned)


def useful_label(value: str, max_len: int = 24) -> bool:
    if not value or value in GENERIC_LABELS:
        return False
    if alias_key(value) in {alias_key(token) for token in TOKEN_STOPWORDS}:
        return False
    if len(value) < 2:
        return False
    if len(value) > max_len:
        return False
    if re.fullmatch(r"\d+(?:\.\d+)*", value):
        return False
    if re.search(r'[(){}\[\]`\\"]', value):
        return False
    if value.startswith(("/", "\\")):
        return False
    if re.fullmatch(r"[xX]-[A-Za-z0-9-]+", value):
        return False
    if re.fullmatch(r"[a-z]+(?:-[a-z0-9]+)+", value):
        return False
    if PACKAGE_LIKE_RE.search(value):
        return False
    if re.search(r"\.(?:xml|html|properties|factories|exe|conf|class)\b", value, re.I):
        return False
    if re.search(r"\w+\(", value):
        return False
    if re.fullmatch(r"[a-z]+", value) and value.lower() not in ALLOWED_LOWER_ASCII_TAGS:
        return False
    if value.lower() in {"true", "false", "null", "void"}:
        return False
    if re.search(r"[。！？；]", value):
        return False
    if re.search(r"[*=`]", value):
        return False
    if re.match(r"^[)\]}].*", value):
        return False
    if any(hint in value for hint in SENTENCE_HINTS):
        return False
    if len(value) >= 6 and any(hint in value for hint in LONG_PHRASE_HINTS):
        return False
    return True


def is_structural_candidate(value: str, max_len: int = 18) -> bool:
    if not useful_label(value, max_len=max_len):
        return False
    if any(part in value for part in STRUCTURAL_STOP_PARTS):
        return False
    if "：" in value or ":" in value:
        return False
    if "的" in value and len(value) >= 8:
        return False
    if re.search(r"[A-Za-z@]", value):
        return True
    return any(hint in value for hint in TECH_HINTS)


def canonical_path_part(value: str) -> str:
    cleaned = normalize_topic(value)
    if not useful_label(cleaned):
        return ""
    return cleaned


def contains_keyword(corpus: str, keyword: str) -> bool:
    lowered = keyword.lower()
    if ASCII_RE.fullmatch(keyword):
        pattern = r"(?<![A-Za-z0-9])" + re.escape(lowered) + r"(?![A-Za-z0-9])"
        return re.search(pattern, corpus) is not None
    return lowered in corpus


def build_hierarchy_tags(path: Path, root: Path, max_depth: int) -> tuple[list[str], list[str]]:
    rel_parent = path.parent.relative_to(root)
    parts = [canonical_path_part(part) for part in rel_parent.parts]
    parts = [part for part in parts if part]
    accum: list[str] = []
    hierarchy: list[str] = []
    for part in parts[:max_depth]:
        accum.append(part)
        hierarchy.append("/".join(accum))
    return hierarchy, parts


def build_corpus(title: str, body: str, existing_raw: str | None, path: Path) -> str:
    headings = " ".join(HEADING_RE.findall(body))
    emphasis = " ".join(BOLD_RE.findall(body[:12000]))
    inline = " ".join(INLINE_CODE_RE.findall(body[:12000]))
    joined = "\n".join(
        [
            title,
            headings,
            emphasis,
            inline,
            body[:12000],
            existing_raw or "",
            path.as_posix(),
        ]
    )
    joined = re.sub(r"https?://\S+", " ", joined)
    return joined.lower()


def add_tag(bucket: list[str], seen: set[str], tag: str) -> None:
    normalized = canonicalize_term(normalize_space(tag))
    if not useful_label(normalized):
        return
    formatted = format_tag(normalized)
    if not formatted:
        return
    if formatted not in seen:
        seen.add(formatted)
        bucket.append(formatted)


def add_scored(scores: dict[str, float], order: dict[str, int], tag: str, weight: float) -> None:
    normalized = normalize_topic(tag)
    if not useful_label(normalized):
        return
    scores[normalized] += weight
    order.setdefault(normalized, len(order))


def split_topic_parts(value: str) -> list[str]:
    parts: list[str] = []
    for raw in re.split(r"\s+[+\-]\s+|与|和|及|、|/", value):
        candidate = normalize_topic(raw)
        if useful_label(candidate, max_len=18):
            parts.append(candidate)
    return parts


def extract_tech_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in ANNOTATION_RE.findall(text):
        tokens.append(raw)
    for raw in CAMEL_RE.findall(text):
        tokens.append(raw)
    for raw in ACRONYM_RE.findall(text):
        tokens.append(raw)
    for raw in CONFIG_RE.findall(text):
        tokens.append(raw)
    for raw in re.findall(r"\b[a-zA-Z_]+\(\)", text):
        tokens.append(raw)

    normalized: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        canonical = canonicalize_term(token)
        if not canonical or canonical in TOKEN_STOPWORDS:
            continue
        if len(canonical) > 28:
            continue
        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)
    return normalized


def score_structural_content(
    title: str,
    body: str,
    scores: dict[str, float],
    order: dict[str, int],
) -> None:
    headings = [normalize_space(v) for v in HEADING_RE.findall(body)]
    bolds = [normalize_space(v) for v in BOLD_RE.findall(body[:12000])]
    inline = [normalize_space(v) for v in INLINE_CODE_RE.findall(body[:12000])]

    title_tag = normalize_topic(title)
    if useful_label(title_tag, max_len=20):
        add_scored(scores, order, title_tag, 9.0)
    for token in extract_tech_tokens(title):
        add_scored(scores, order, token, 7.0)

    for phrase in headings[:20]:
        topic = normalize_topic(phrase)
        if is_structural_candidate(topic, max_len=10):
            add_scored(scores, order, topic, 4.8)
        for part in split_topic_parts(topic):
            if is_structural_candidate(part, max_len=10):
                add_scored(scores, order, part, 4.0)
        for token in extract_tech_tokens(phrase):
            add_scored(scores, order, token, 4.2)

    for phrase in bolds[:40]:
        topic = normalize_topic(phrase)
        if is_structural_candidate(topic, max_len=10):
            add_scored(scores, order, topic, 3.2)
        for part in split_topic_parts(topic):
            if is_structural_candidate(part, max_len=10):
                add_scored(scores, order, part, 2.8)
        for token in extract_tech_tokens(phrase):
            add_scored(scores, order, token, 3.0)

    for phrase in inline[:50]:
        for token in extract_tech_tokens(phrase):
            add_scored(scores, order, token, 3.0)


def score_keywords(
    path: Path,
    root: Path,
    title: str,
    body: str,
    existing_raw: str | None,
    scores: dict[str, float],
    order: dict[str, int],
) -> None:
    headings = " ".join(HEADING_RE.findall(body)).lower()
    emphasis = " ".join(BOLD_RE.findall(body[:12000])).lower()
    title_lower = title.lower()
    corpus = build_corpus(title, body, existing_raw, path)

    for keyword, tag in KEYWORD_TAGS:
        if contains_keyword(title_lower, keyword):
            add_scored(scores, order, tag, 7.0)
        elif contains_keyword(headings, keyword):
            add_scored(scores, order, tag, 5.5)
        elif contains_keyword(emphasis, keyword):
            add_scored(scores, order, tag, 4.5)
        elif contains_keyword(corpus, keyword):
            add_scored(scores, order, tag, 3.8)

    rel_parent = path.parent.relative_to(root)
    for part in rel_parent.parts:
        aliases = PATH_ALIASES.get(part) or PATH_ALIASES.get(clean_label(part)) or []
        for alias in aliases:
            add_scored(scores, order, alias, 1.1)

    top_level = rel_parent.parts[0] if rel_parent.parts else ""
    for fallback in DOMAIN_DEFAULTS.get(top_level, []):
        add_scored(scores, order, fallback, 0.8)


def sort_candidates(scores: dict[str, float], order: dict[str, int]) -> list[str]:
    return sorted(
        scores,
        key=lambda tag: (-scores[tag], len(tag), order[tag]),
    )


def semantic_candidates(
    path: Path,
    root: Path,
    title: str,
    body: str,
    existing_raw: str | None,
    hierarchy_parts: list[str],
    content_priority: bool,
) -> list[str]:
    scores: dict[str, float] = defaultdict(float)
    order: dict[str, int] = {}

    score_structural_content(title, body, scores, order)
    score_keywords(path, root, title, body, existing_raw, scores, order)

    if not content_priority and hierarchy_parts:
        add_scored(scores, order, hierarchy_parts[-1], 2.2)

    return sort_candidates(scores, order)


def build_tags(
    path: Path,
    root: Path,
    title: str,
    body: str,
    existing_raw: str | None,
    max_hierarchy_depth: int,
    content_priority: bool,
) -> list[str]:
    hierarchy, hierarchy_parts = build_hierarchy_tags(path, root, max_hierarchy_depth)
    tags: list[str] = []
    seen: set[str] = set()

    if not content_priority:
        for tag in hierarchy:
            add_tag(tags, seen, tag)

    for tag in semantic_candidates(
        path=path,
        root=root,
        title=title,
        body=body,
        existing_raw=existing_raw,
        hierarchy_parts=hierarchy_parts,
        content_priority=content_priority,
    ):
        add_tag(tags, seen, tag)
        if len(tags) >= 6:
            return tags[:6]

    if content_priority:
        for part in hierarchy_parts:
            aliases = PATH_ALIASES.get(part) or []
            for alias in aliases:
                add_tag(tags, seen, alias)
                if len(tags) >= 6:
                    return tags[:6]
            add_tag(tags, seen, part)
            if len(tags) >= 6:
                return tags[:6]

    for tag in hierarchy:
        add_tag(tags, seen, tag)
        if len(tags) >= 6:
            return tags[:6]

    rel_parent = path.parent.relative_to(root)
    top_level = rel_parent.parts[0] if rel_parent.parts else ""
    for fallback in DOMAIN_DEFAULTS.get(top_level, []):
        add_tag(tags, seen, fallback)
        if len(tags) >= 6:
            return tags[:6]

    generic_fallbacks = ["学习笔记", "知识梳理", "工程实践"]
    for fallback in generic_fallbacks:
        add_tag(tags, seen, fallback)
        if len(tags) >= 6:
            return tags[:6]

    return tags[:6]


def build_frontmatter(existing: dict, title: str, tags: list[str], updated: str) -> str:
    merged = {"title": title, "tags": tags, "updated": updated}
    for key, value in existing.items():
        if key in {"title", "tags", "updated"}:
            continue
        merged[key] = value

    lines = ["---", f"title: {quote_scalar(title)}", "tags:"]
    for tag in tags:
        lines.append(f"  - {quote_scalar(tag)}")
    lines.append(f"updated: {quote_scalar(updated) if isinstance(updated, str) and ':' in updated else updated}")

    extras = {k: v for k, v in merged.items() if k not in {"title", "tags", "updated"}}
    if extras:
        extras_text = yaml.dump(
            extras,
            Dumper=PrettyDumper,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1000,
        ).strip()
        lines.append(extras_text)

    lines.append("---")
    return "\n".join(lines) + "\n\n"


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root directory not found: {root}")

    changed: list[tuple[str, list[str]]] = []
    counts: dict[int, int] = {}

    for path in sorted(root.rglob("*.md")):
        original = path.read_text(encoding="utf-8")
        existing_raw, body = split_frontmatter(original)
        existing = load_frontmatter(existing_raw)
        title = str(existing.get("title") or path.stem)
        body = body.lstrip("\n")
        tags = build_tags(
            path=path,
            root=root,
            title=title,
            body=body,
            existing_raw=existing_raw,
            max_hierarchy_depth=args.max_hierarchy_depth,
            content_priority=args.content_priority,
        )

        if len(tags) < 5:
            raise SystemExit(f"Failed to build enough tags for {path}: {tags}")

        updated_text = build_frontmatter(existing, title, tags, args.updated) + body
        counts[len(tags)] = counts.get(len(tags), 0) + 1

        if updated_text != original:
            changed.append((str(path.relative_to(root)), tags))
            if not args.dry_run:
                path.write_text(updated_text, encoding="utf-8")

    print(f"root={root}")
    print(f"changed_files={len(changed)}")
    print(f"tag_count_distribution={counts}")
    for rel, tags in changed[: args.sample]:
        print(f"{rel} => {', '.join(tags)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
