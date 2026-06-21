---
title: "BlockingQueue"
tags:
  - "BlockingQueue"
  - "BlockingDeque"
  - "DelayQueue"
  - "无锁"
  - "SychronousQueue"
  - "ArrayBlockingQueue"
updated: 2026-04-16
---
- [[#一、BlockingQueue]]
- [[#二、BlockingDeque]]

# 一、BlockingQueue
1. BlockingQueue 通常**用于一个线程生产对象，而另外一个线程消费这些对象的场景**

    ![[IMG-20260619223614846.png|302]]

    **一个线程往里边放，另外一个线程从里边取的一个 BlockingQueue**

2. 这样的阻塞队列可以应对生产者和消费者之间**数据处理速度不匹配的问题**
    1. **生产者会持续生产新对象并将其插入到队列之中**
        1. 如果该阻塞队列到==达了其临界点==，负责生产的线程将会在往里边插入新对象时发生==阻塞==
        2. 它会一直处于阻塞之中，直到负责消费的线程从队列中拿走一个对象
    2. **消费者将会一直从该阻塞队列中拿出对象**
        1. 如果消费线程尝试去从一个==空的队列==中提取对象的话，这个消费线程将会处于==阻塞==之中
        2. 直到一个生产线程把一个对象丢进队列
3. **阻塞队列 BlockingQueue 种类：（**==**在**==[[ThreadPoolExecutor]]==**提供的几种线程池部分有应用**==**）**

    ![[IMG-20260619223614961.png|648]]

    - **`ArrayBlockingQueue`**：基于**数组**实现的有界阻塞队列
    - **`LinkedBlockingQueue`**：由**链表**结果组成的有界阻塞队列（默认大小Integer.MAX_VALUE）阻塞队列（大小可选，如果设置了最大值，则接近无界）
        - 加锁方式：
            - ==用两把锁，分别锁住头尾==
            - ==同一时刻，可以允许一个生产者与一个消费者两个线程同时执行==
            - 保证消费者和生产者之间不会互斥放取
            - 消费者与消费者，生产者与生产者之间会互斥，仍然串行
    - **`SychronousQueue`**：**不存储元素的阻塞队列**，也即单个元素队列。每个插入操作必须等待一个对应的移除操作，反之亦然，因此可以用于直接传递数据的场景
    - **`PriorityBlockingQueue`**：基于堆实现，支持**优先级排序**的无界阻塞队列
    - **`DelayQueue`**：一个支持**延迟元素**的无界阻塞队列，每个元素都有一个**过期时间**，只有在过期时才能被消费
    - **`ConcurrentLinkedQueue`**：基于**链表**实现的无界非阻塞队列，采用**无锁**算法实现并发安全，适用于高并发场景
    - `LinkedTransferQueue`：由链表结构组成的无界阻塞队列
4. **BlockingQueue 的核心方法：**

    应用案例：[[线程的通信]]

    ```Java
    public interface BlockingQueue<E> extends Queue<E> {
        //将给定元素设置到队列中，如果设置成功返回true, 否则返回false。如果是往限定了长度的队列中设置值，推荐使用offer()方法。
        boolean add(E e);
        //将给定的元素设置到队列中，如果设置成功返回true, 否则返回false. e的值不能为空，否则抛出空指针异常。
        boolean offer(E e);
        //将元素设置到队列中，如果队列中没有多余的空间，该方法会一直阻塞，直到队列中有多余的空间。
        void put(E e) throws InterruptedException;
        //将给定元素在给定的时间内设置到队列中，如果设置成功返回true, 否则返回false.
        boolean offer(E e, long timeout, TimeUnit unit) throws InterruptedException;
        //从队列中获取值，如果队列中没有值，线程会一直阻塞，直到队列中有值，并且该方法取得了该值。
        E take() throws InterruptedException;
        //在给定的时间里，从队列中获取值，时间到了直接调用普通的poll方法，为null则直接返回null。
        E poll(long timeout, TimeUnit unit) throws InterruptedException;
        //获取队列中剩余的空间。
        int remainingCapacity();
        //从队列中移除指定的值。
        boolean remove(Object o);
        //判断队列中是否拥有该值。
        public boolean contains(Object o);
        //将队列中值，全部移除，并发设置到给定的集合中。
        int drainTo(Collection<? super E> c);
        //指定最多数量限制将队列中值，全部移除，并发设置到给定的集合中。
        int drainTo(Collection<? super E> c, int maxElements);
    }
    ```
# 二、BlockingDeque
1. deque（双端队列）是 "Double Ended Queue" 的缩写
2. 因此，**BlockingDeque 可以从任意一端插入或者抽取元素的队列**
    1. 且在不能够插入元素时，它将==阻塞==住试图插入元素的线程
    2. 在不能够抽取元素时，它将==阻塞==住试图抽取的线程

    ![[IMG-20260619223615043.png|356]]

3. **使用场景**
    1. 在线程既是一个队列的生产者又是这个队列的消费者的时候可以使用到 BlockingDeque
    2. 如果生产者线程需要在队列的两端都可以插入数据，消费者线程需要在队列的两端都可以移除数据，这个时候也可以使用 BlockingDeque
4. **BlockingDeque 接口继承自 BlockingQueue 接口**。这就意味着你可以像使用一个 BlockingQueue 那样使用 BlockingDeque
5. 种类
    - **`LinkedBlockingDeque`**：由链表结构组成的双端阻塞队列