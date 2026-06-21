---
title: "Redis 介绍"
tags:
  - "中间件"
  - "中间件/Redis"
  - "Redis"
  - "Elasticsearch"
  - "SQL"
  - "线程"
updated: 2026-04-16
---

# 一、NoSQL
## 1. 简介
1. NoSQL，指的是非关系型的数据库。NoSQL有时也称作Not Only SQL的缩写，是对不同于传统的关系型数据库的数据库管理系统的统称
2. NoSQL用于超大规模数据的存储。（例如谷歌或Facebook每天为他们的用户收集万亿比特的数据）。这些类型的数据存储不需要固定的模式，无需多余操作就可以横向扩展
## 2. RDBMS Vs NoSQL

![[IMG-20260620224127661.png|800]]

1. **RDBMS**
    1. 结构化(Structured)
    2. 关联的(Relational)
    3. SQL查询

    ```SQL
     SELECT id, name age FROM tb_user WHERE id = 1
    ```
    4. ACID

        详见 分布式理论知识

2. **NoSQL**
    1. 非结构化
        - 键值类型（Redis）
        - 文档类型（MongoDB）
        - 列类型（HBase）
        - Graph类型（Neo4j）
    2. 无关联的
    3. 非SQL查询
        - Redis

    ```Bash
     get user:1
    ```
        - MongoDB

    ```Bash
     db.users.find({_id: 1})
    ```
        - elasticsearch

    ```Bash
     GET http://localhost:9200/users/1
    ```
    4. BASE

        详见 分布式理论知识

# 二、Redis 介绍
1. **介绍**
    1. Redis 诞生于2009年全称是**Re**mote **Di**ctionary **S**erver，远程词典服务器
    2. Redis 是现在最受欢迎的NoSQL数据库之一，Redis是一个使用ANSI C编写的**开源**、包含多种数据结构、支持网络、基于内存、可选持久性的键值对存储数据库
2. **Redis 特征**
    - 键值（key-value）型
    - Redis不仅仅支持简单的 key-value 类型的数据，同时还提供 list，set，zset，hash 等**多种不同的数据结构的存储**
    - **单线程**，**每个命令具备原子性**
    - **低延迟，速度快（基于内存、IO多路复用、良好的编码）**
    - Redis 支持数据的持久化，可以将内存中的数据保存在磁盘中，重启的时候可以再次加载进行使用
    - 支持主从集群、分片集群
    - Redis 支持数据的备份，即 master-slave 模式的数据备份
    - 支持多语言客户端
