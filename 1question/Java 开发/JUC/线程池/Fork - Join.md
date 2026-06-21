---
title: "Fork - Join"
tags:
  - "ForkJoin"
  - "ForkJoinPool"
  - "CompletableFuture"
  - "并发编程"
  - "线程"
  - "线程池"
updated: 2026-04-16
---
- [[#一、介绍]]
- [[#二、使用]]

# 一、介绍
1. Fork/Join 是 JDK 1.7 加入的新的线程池实现
2. **`Fork/Join`** ==**在分治的基础上加入了多线程**==**，可以**==**把每个任务的分解和合并交给不同的线程来完成**==**，进一步提升了运算效率**
    1. 所谓的任务拆分，是将一个大任务拆分为算法上相同的小任务，直至不能拆分可以直接求解
    2. 跟递归相关的一些计算，如归并排序、斐波那契数列、都可以用分治思想进行求解
3. ==**适用于能够进行任务拆分的 cpu 密集型运算**==
4. Fork/Join 默认会创建与 cpu 核心数大小相同的线程池 `ForkJoinPool`
    > `CompletableFuture` 在不指定执行器（`Executor`）时使用默认的 `ForkJoinPool.commonPool()` 作为线程池来执行异步代码，主要是由于以下几个原因：
    > 1. **高效的线程池管理，减少创建开销**
    >     - 使用默认的共享线程池可以减少每次提交异步任务时创建新线程的开销。创建和销毁线程是比较昂贵的操作，复用线程资源可以显著提高性能
    > 1. **支持 Fork/Join 并行计算**
    >     - `ForkJoinPool` 是专为支持“分而治之”模式而设计的，可以有效地处理那些可以被分解成许多小任务并行工作的任务。这种工作窃取策略可以利用多核处理器的能力。
    >     - `CompletableFuture` 是为支持异步编程而设计，其异步操作通常可以表示为可以被拆分的小任务，因此使用 `ForkJoinPool` 是合适的选择。
    > 1. **与 Java 8 并行流的协同工作**
    >     - 在 Java 8 中，`ForkJoinPool` 还支持并行流（`parallelStream()`），能够使得集合操作可以在多核 CPU 上并行处理
    >     - 因为 `CompletableFuture` 和并行流都利用 `ForkJoinPool.commonPool()`，这样使得它们之间有了更好的兼容性和协作

    ![[IMG-20260618165430211.png|730]]

5. Fork/Join框架主要包含三个模块：
    - 任务对象: `ForkJoinTask` （包括`RecursiveTask`、`RecursiveAction` 和 `CountedCompleter`）
    - 执行 Fork/Join 任务的线程：`ForkJoinWorkerThread`
    - 线程池： `ForkJoinPool`
6. 正确使用姿势

    ![[IMG-20260618165430413.png|699]]

# 二、使用
1. 提交给 Fork/Join 线程池的任务需要继承 RecursiveTask（有返回值）或 RecursiveAction（没有返回值）
2. 例如下面定义了一个对 1~n 之间的整数求和的任务

    ```Java
    public class ForkJoinTest {
        public static void main(String[] args) {
            ForkJoinPool pool = new ForkJoinPool(4);
            System.out.println(pool.invoke(new AddTask1(5)));
        }
    }
    class AddTask1 extends RecursiveTask<Integer> {
        int n;
        public AddTask1(int n) {
            this.n = n;
        }
        @Override
        public String toString() {
            return "{" + n + '}';
        }
        @Override
        protected Integer compute() {
            // 如果 n 已经为 1，可以求得结果了
            if (n == 1) {
                System.out.println("join() " + n);
                return n;
            }
            // 将任务进行拆分(fork)
            AddTask1 t1 = new AddTask1(n - 1);
            t1.fork();
            System.out.println("fork() " + n + " " + t1);
            // 合并(join)结果
            int result = n + t1.join();
            System.out.println("join() " + n + " " + t1  + " " + result);
            return result;
        }
    }
    ```

    运行结果

    ```Java
    fork() 5 {4}
    fork() 4 {3}
    fork() 2 {1}
    fork() 3 {2}
    join() 1
    join() 2 {1} 3
    join() 3 {2} 6
    join() 4 {3} 10
    join() 5 {4} 15
    15
    ```