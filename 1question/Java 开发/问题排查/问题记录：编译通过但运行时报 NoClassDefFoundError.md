---
title: "编译通过但运行时报 NoClassDefFoundError"
aliases:
  - "为什么编译通过，运行时却报 NoClassDefFoundError"
  - "为什么编译器不报错，运行时才爆"
tags:
  - "JVM"
  - "类加载"
  - "NoClassDefFoundError"
  - "ClassNotFoundException"
  - "Maven"
  - "传递依赖"
updated: 2026-06-05
---

> 一句话结论
> 
> 1. 只要编译期 classpath 中能找到源码里**直接引用**的 `DateUtils.class`，编译器通常就会通过。
> 
> 1. 但 JVM 在运行期第一次真正使用 `DateUtils` 时，才会执行它的 `<clinit>()` 并递归触发静态依赖加载；如果被 `exclusions` 排掉的 `Tracer` 不在 classpath 中，就会在这一步报 `NoClassDefFoundError`。

- [[#一、典型现象]]
- [[#二、为什么编译能通过]]
- [[#三、为什么运行时才报错]]
- [[#四、异常类型怎么区分]]
- [[#五、排查与规避]]

# 一、典型现象
1. 这类问题常见于“业务代码直接调用某个二方包工具类，编译正常，但运行到第一次调用时抛出 `NoClassDefFoundError`”的场景。
2. 它通常伴随下面两个条件同时出现：一是二方包本体仍然在 classpath 中；二是它内部依赖的某个**传递依赖**被 `exclusions`、`optional`、依赖裁剪或打包遗漏移除了。
3. 从现象上看，这不是“源码写错了”，而是“**编译期 classpath** 和 **运行期 classpath** 不一致”叠加 [[类的生命周期]] 中的**懒初始化**共同造成的结果。
4. 这个问题可以用下面这张对照表快速记住。

| 阶段 | JVM / 编译器关注点 | 典型结果 |
| --- | --- | --- |
| 编译期 | 你当前源码直接引用的类、方法、字段能否从编译期 classpath 解析出来 | `DateUtils` 在 jar 中即可编译通过 |
| 运行期首次使用 | 目标类及其静态初始化链上的类能否都在运行期 classpath 中成功加载和初始化 | 缺少 `Tracer` 时抛异常 |

# 二、为什么编译能通过
## 1. 编译器检查的是“当前源码直接用到了什么”
1. Java 编译器在编译你的源码时，核心任务是把当前编译单元里出现的类型、方法、字段解析成可用的符号引用。
2. 只要你的代码里写的是 `DateUtils.stringToDate()`，编译器首先关心的是 `DateUtils.class` 是否存在，以及这个静态方法签名是否可见。
3. 它不会因为你写了 `DateUtils`，就继续把 `DateUtils` 内部所有静态字段、静态代码块，再到它们依赖的 `DigestLogger`、`Tracer` 全部递归验证一遍。
4. 所以从“你的源码是否能编译”这个角度看，`DateUtils` 能被找到就已经满足主要条件了。

## 2. 二方包本体存在，不代表它的运行期依赖完整
1. 假设编译期引入的是 `travelvc-common-1.3.60-AI-SUCCESS-RATE.jar`，并且这个 jar 内确实包含 `DateUtils.class`，那么 `import DateUtils` 就不会报错。
2. 但 `DateUtils` 能被编译器识别，只能说明“**这个类文件在**”；并不能说明“**这个类运行起来需要的所有依赖都在**”。
3. 这也是为什么很多依赖问题会表现为“IDE 不报红、`mvn compile` 也通过，但一跑起来就炸”。

# 三、为什么运行时才报错
## 1. `exclusions` 影响的是传递依赖，而不是当前依赖本体
1. Maven 的 `exclusions` 通常是把某个依赖的**下游传递依赖**挡掉，而不是把当前声明的这个 jar 本身一起删掉。
2. 这就会导致一个典型状态：`travelvc-common.jar` 还在，所以 `DateUtils.class` 还能被编译器和 JVM 找到；但它内部实际要用的 `trade-tracker` 或 `Tracer` 已经不在运行期 classpath 里了。
3. 如果使用的是“`exclude all`”这种比较激进的写法，那么这种“本体还在、内脏被掏空”的情况就更容易出现。
4. 这种依赖裁剪手法本身并不是错的，但它要求你非常清楚被裁掉的依赖到底只是“可选能力”，还是“静态初始化就会强依赖”的核心组件。

## 2. 类初始化本身就是懒触发的
1. 根据 [[类的生命周期]]，类的初始化阶段会执行 `<clinit>()`，而 `<clinit>()` 由静态变量赋值和静态代码块共同组成。
2. 根据 [[构造方法]]，编译器会把 `static {}` 和静态成员赋值逻辑合并到 `<clinit>()V` 中。
3. 这个初始化过程并不会在 JVM 启动时把所有类一次性跑完，而是通常在**首次主动使用**某个类时才触发。
4. 所以如果业务代码一直没有真正调用 `DateUtils`，那么即使它内部依赖有缺失，问题也可能一直潜伏着不暴露。

## 3. 这条异常链是如何被触发的
1. 当代码第一次执行 `DateUtils.stringToDate()` 时，JVM 需要先确保 `DateUtils` 已经完成加载和初始化。
2. 如果 `DateUtils` 的静态字段里存在类似 `DigestLogger digestLogger = DigestLoggerFactory.getLogger()` 的逻辑，那么在初始化 `DateUtils` 时就会继续触发 `DigestLoggerFactory` 的加载与初始化。
3. 如果 `DigestLoggerFactory` 的静态字段又依赖 `Tracer TRACER = TravelvcTracerFactory.getTracer(...)`，那么 JVM 会继续尝试解析并加载 `Tracer`。
4. 一旦 `Tracer` 对应的类因为传递依赖被裁掉而不存在，类加载 / 链接 / 初始化链条就会在这里断掉，最终表现为 `NoClassDefFoundError`、`ExceptionInInitializerError`，或者后续的 `Could not initialize class` 一类症状。
5. 这条链路可以简单记成下面这样。
    ```text
    业务代码
      -> DateUtils.stringToDate()
      -> DateUtils.<clinit>()
      -> DigestLoggerFactory.getLogger()
      -> DigestLoggerFactory.<clinit>()
      -> Tracer
      -> NoClassDefFoundError
    ```

## 4. 为什么“不调用就永远不报错”
1. 这个现象的根本原因不是 JVM “偶发抽风”，而是类初始化本来就是按需发生的。
2. 只要那段业务分支没有跑到，或者某个工具类从未被首次主动使用，对应的 `static` 初始化链就不会被触发。
3. 这也是很多线上问题表现为“系统启动正常，压测正常，但某个冷门接口第一次被访问就爆”的原因。

# 四、异常类型怎么区分
## 1. `ClassNotFoundException`
1. `ClassNotFoundException` 更常见于你**主动**通过 `Class.forName()`、`ClassLoader.loadClass()`、SPI、反射等方式按名称加载类，但 classpath 中找不到目标类的场景。
2. 这类异常更强调“我现在明确去找一个类，但找不到它”。

## 2. `NoClassDefFoundError`
1. `NoClassDefFoundError` 更常见于“这个类在编译期本来是可见的，或者某段已编译代码在运行时本来期望它存在，但 JVM 真正去定义、解析或初始化时发现它不可用”的场景。
2. 传递依赖被裁掉、运行期 jar 漏打、静态初始化链里依赖缺失，都是它的高频成因。
3. 如果错误发生在 `<clinit>()` 内部，第一次使用时也可能先看到 `ExceptionInInitializerError`；而在后续再次使用同一类时，常常又会看到 `NoClassDefFoundError: Could not initialize class ...`。
4. 所以这几个异常名虽然不同，但它们经常指向同一类根因：**运行期类路径不完整，或者类初始化链失败**。

# 五、排查与规避
## 1. 排查顺序
1. 先看完整堆栈，重点关注是否出现 `<clinit>`、`ExceptionInInitializerError`、`Could not initialize class`、缺失类的全限定名等线索。
2. 再看依赖树，确认目标 jar 是否还在，以及它依赖的下游 jar 是否被 `exclusions`、`optional` 或打包插件过滤掉了。
3. 之后去看出问题类的源码，特别是 `static` 字段、静态代码块、日志工厂、Tracer/SPI 注册等“类一初始化就会执行”的部分。
4. 如果需要在本地快速验证，可以用下面这些命令辅助定位。
5. 依赖树检查：
    ```bash
    mvn dependency:tree
    ```
6. 查看 jar 内是否真的包含目标类：
    ```bash
    jar tf travelvc-common-1.3.60-AI-SUCCESS-RATE.jar | grep DateUtils
    jar tf trade-tracker-xxx.jar | grep Tracer
    ```

## 2. 规避建议
1. 不要默认使用“`exclude all`”这类大锤式裁剪，除非你已经明确验证过目标库的运行期依赖图。
2. 如果某个二方包在编译期只暴露了一个工具类，但运行期静态初始化又强依赖其他组件，那么更稳妥的做法通常是**显式补回**必须的依赖，而不是赌它“应该不会被用到”。
3. 在 Spring Boot 自动配置场景中，可以结合 [[spring-boot-starter]] 里的 `@ConditionalOnClass` 思路，把“类路径不完整时不要初始化相关 Bean”前置到配置层面。
4. 对于通用工具类，尽量避免在 `static` 初始化里放入日志工厂、Tracer、远程配置、SPI 扫描这类重量级依赖；工具类越基础，初始化副作用越应该小。
5. 遇到“编译没问题、运行才炸”的类问题时，优先从“编译期 classpath”和“运行期 classpath 是否一致”这个角度切入，通常会比单纯盯着业务代码更快。
