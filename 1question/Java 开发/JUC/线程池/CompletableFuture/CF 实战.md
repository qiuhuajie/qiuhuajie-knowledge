- [[#1. 电商比价案例]]
    - [[#1.1 需求]]
    - [[#1.2 实现]]
        - [[#一般做法：查完一家再查一家]]
        - [[#使用 CompletableFuture 优化]]
- [[#2. 自定义工具类 CompletableFutureUtils ⭐]]
    - [[#2.1 维护的线程池]]
    - [[#2.2 任务执行方法]]
    - [[#2.3 在业务中使用]]
        - [[#step1：两个长时间的查询接口做成并行]]
        - [[#step2：阻塞获取查询结果]]
- [[#3. 外卖商家端API的异步化]]
# 1. 电商比价案例
## 1.1 需求
1. 需求说明：同一款产品，同时搜索出同款产品在各大电商平台的售价
1. 输出返回：出来结果希望是同款产品在不同地方的价格清单列表，返回一个 `List<String>`
## 1.2 实现
```Java
// 实体类：
class NetMall{
    @Getter
    private String netMallName;
    public NetMall(String netMallName) {
        this.netMallName = netMallName;
    }
    public double calcPrice(String productName) {
        // 每次查询价格模拟为 1 秒
        try { TimeUnit.SECONDS.sleep(1); } catch (InterruptedException e) { e.printStackTrace(); }
        return ThreadLocalRandom.current().nextDouble() * 2 + productName.charAt(0);
    }
}
```
### 一般做法：查完一家再查一家
```Java
public class CompletableFutureMallDemo {
    static List<NetMall> list = Arrays.asList(
            new NetMall("jd"),
            new NetMall("taobao"),
            new NetMall("dangdang")
    );
    // step by step
    public static List<String> getPrice (List<NetMall> list, String productName) {
        // 2.将传入的 list 中的每个 netMall元素 重新 map 映射成自定义格式的 String
        return list.stream()
                .map(netMall -> String.format(
                        productName + " in %s price is %.2f",
                        netMall.getNetMallName(),
                        netMall.calcPrice(productName)))
                .collect(Collectors.toList());
    }
    public static void main(String[] args) {
        long startTime = System.currentTimeMillis();
        // 1.业务功能调用
        List<String> priceList = getPrice(list, "JUC");
        if (!CollectionUtil.isEmpty(priceList)) {
            for (String cur : priceList) {
                System.out.println(cur);
            }
        }
        long endTime = System.currentTimeMillis();
        System.out.println("耗时" + (endTime - startTime) + "毫秒");
    }
}
```

运行结果：

![[Attachment/1question/大数据/Java 开发/JUC/线程池/CompletableFuture/IMG-20260405035413908.png|Untitled 473.png]]

### 使用 CompletableFuture 优化
1. 对于分布式微服务的调用，按照实际业务，如果是无关联 step by step 的业务，可以尝试是否可以多箭齐发，同时调用
1. 代码示例：
    
    ```Java
    public class CompletableFutureMallDemo {
        static List<NetMall> list = Arrays.asList(
                new NetMall("jd"),
                new NetMall("taobao"),
                new NetMall("dangdang")
        );
    
        // 使用 CompletableFuture
        public static List<String> getPriceByCompletableFuture (List<NetMall> list, String productName) {
            // 2.获取线程池
            ExecutorService threadPool = Executors.newFixedThreadPool(3);
            try {
                // 3.将传入的 list 中的每个 netMall元素先 map 映射成 CompletableFuture<String>
                return list.stream()
                        .map(netMall -> CompletableFuture.supplyAsync(() -> {
                            return String.format(
                                    productName + " in %s price is %.2f",
                                    netMall.getNetMallName(),
                                    netMall.calcPrice(productName));
                        }, threadPool))
                        .collect(Collectors.toList())
                        // 4.再将每个 CompletableFuture<String> 映射成 String
                        .stream()
        //                .map(result -> result.join())
                        .map(CompletableFuture::join)
                        .collect(Collectors.toList());
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            } finally {
                // 5.关闭线程池资源
                threadPool.shutdown();
            }
        }
    
    		// 测试
        public static void main(String[] args) {
            long startTime = System.currentTimeMillis();
            // 1.业务功能调用
            List<String> priceList = getPriceByCompletableFuture(list, "JUC");
            if (!CollectionUtil.isEmpty(priceList)) {
                for (String cur : priceList) {
                    System.out.println(cur);
                }
            }
            long endTime = System.currentTimeMillis();
            System.out.println("耗时" + (endTime - startTime) + "毫秒");
        }
    }
    ```
    

    运行结果：

    

    ![[IMG-20260404031740171.png|Untitled 1 344.png]]

    
# 2. 自定义工具类 CompletableFutureUtils ⭐
## 2.1 维护的线程池
```Java
private ExecutorService executorService;
public EnhanceCompletableFuture() {
    ThreadFactory namedThreadFactory = new ThreadFactoryBuilder().setNameFormat("fastquery-pool-%d").build();
    executorService = new ThreadPoolExecutor(0, 100,
            60L, TimeUnit.SECONDS,
            new SynchronousQueue<Runnable>(), namedThreadFactory, new CallerRunsPolicy());
}
```
## 2.2 任务执行方法

[[Export-e8249ac1-4ae1-42cd-83d5-041a266841fe/1question/Java 开发/Java/Java 8 新特性/Supplier|Supplier]][[Export-e8249ac1-4ae1-42cd-83d5-041a266841fe/1question/Java 开发/Java/Java 8 新特性/Supplier|Supplier]]

```Java
public <T> CompletableFuture<T> supplyAsync(Supplier<T> supplier) {
    final RpcContext_inner rpcContext = EagleEye.getRpcContext();
    return CompletableFuture.supplyAsync(
            () -> {
                try {
                    EagleEye.setRpcContext(rpcContext);
                    return supplier.get();
                } finally {
                    EagleEye.clearRpcContext();
                }
            },
            executorService);
}

public CompletableFuture<Void> runAsync(Runnable runnable) {
    final RpcContext_inner rpcContext = EagleEye.getRpcContext();
    return CompletableFuture.runAsync(
            () -> {
                try {
                    EagleEye.setRpcContext(rpcContext);
                    runnable.run();
                } finally {
                    EagleEye.clearRpcContext();
                }
            },
            executorService);
}
```
## 2.3 在业务中使用
### step1：两个长时间的查询接口做成并行
```Java
// 接口 1
CompletableFuture<List<VisaRelatedItemDTO>> relatedFur = enhanceFuture.supplyAsync(() -> {
    TisPlusSearchParam param = buildTisPlusSearchParam(request);
	  ...
    return visaRelatedItemDTO;
    });
});
// 接口 2
CompletableFuture<List<VisaTypeDTO>> visaFur = enhanceFuture
        .supplyAsync(() -> visaStlFacadeService.queryVisaTypesByCountryId(request.getCountryId()));
// 如果是批量查询，可以将生成的每一个 CompletableFuture，add 进一个 List 中，再遍历获取结果
completableFutures.add(completableFuture1);
completableFutures.add(completableFuture2);
...
for (CompletableFuture<List<TravelItem>> completableFuture : completableFutures) {
		...
}
```
### step2：阻塞获取查询结果

`isDone()` + `get()`

```Java
context.setSnick(sellerNickF.isDone() ? sellerNickF.get() : null);
context.setPromotionInfoDO(promotionF.isDone() ? promotionF.get() : null);
```
# 3. **外卖商家端API的异步化**

[[principle]]