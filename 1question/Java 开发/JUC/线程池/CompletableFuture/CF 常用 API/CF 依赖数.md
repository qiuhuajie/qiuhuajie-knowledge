---
title: "CF 依赖数"
tags:
  - "CompletableFuture"
  - "CF_依赖数"
  - "并发编程"
  - "异步"
  - "线程"
  - "线程池"
updated: 2026-04-16
---
# 一、CF 依赖数
1. 使用 CompletableFuture 也是**构建依赖树**的过程。一个CompletableFuture 的完成会触发另外一系列依赖它的CompletableFuture的执行：

    ![[IMG-20260619224442188.png|209]]

    > 如上图所示，这里描绘的是一个业务接口的流程
    > 1. 其中包括 `CF1\CF2\CF3\CF4\CF5` 共5个步骤，并描绘了这些步骤之间的依赖关系
    > 2. 每个步骤可以是一次RPC调用、一次数据库操作或者是一次本地方法调用等
    > 3. 在使用CompletableFuture进行异步化编程时，图中的**每个步骤都会产生一个 CompletableFuture 对象**，**最终结果也会用一个CompletableFuture来表示**
2. 根据 CompletableFuture 依赖数量，可以分为以下几类：**零依赖、一元依赖、二元依赖和多元依赖**
    - 零依赖：刚创建的 CompletableFuture

    ![[IMG-20260619224442243.png|213]]

    - 一元依赖：可以通过 `thenApply`、 `thenAccept`、 `thenCompose` 等方法来实现

        ![[IMG-20260619224442312.png|193]]

    - 二元依赖：可以通过 `thenCombine` 等回调来实现

        ![[IMG-20260619224442375.png|211]]

    - 多元依赖：可以通过 `allOf` 或 `anyOf`方法来实现，区别是当需要多个依赖全部完成时使用 `allOf`，当多个依赖中的任意一个完成即可时使用 `anyOf`

        ![[IMG-20260619224442443.png|217]]

* https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzE5ODQyNDY4OQ==&action=getalbum&album_id=4438767134088970250&scene=126#wechat_redirect

mp.weixin.qq.comhttps://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzE5ODQyNDY4OQ==&action=getalbum&album_id=4438767134088970250&scene=126#wechat_redirectmp.weixin.qq.com