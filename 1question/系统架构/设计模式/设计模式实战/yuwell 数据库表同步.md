---
title: "yuwell 数据库表同步"
tags:
  - "系统架构"
  - "系统架构/设计模式"
  - "系统架构/设计模式/设计模式"
  - "yuwell 数据库表同步"
  - "设计模式"
  - "ConcurrentHashMap"
updated: 2026-04-16
---
# 一、业务描述
根据请求中传入的数据库表名，将对应数据库表的数据封装成 JSON 返回
# 二、代码实现（传统方案）
1. 根据传入的表名参数，在处理方法中写 `if-else`
1. 存在的问题：
    1. **当由新的表要同步时，需要加新的判断条件，违反的开闭原则**
    1. **一共有二十多张表，每个表的处理逻辑都不同，那么这个处理方法的代码长度有多长可想而知**

# 三、代码实现（策略模式 + 工厂模式）
![[IMG-20260315213656249.png|Untitled 278.png]]
1. `TableSynchronizationDownloadController`

    ```Java
    @Api(value = "TableSynchronizationDownloadController", tags = {"表格下载同步接口"})
    @RestController
    @RequestMapping("/tableSynchronizationDownload")
    public class TableSynchronizationDownloadController {
        @Autowired
        TableSynchronizationDownloadService tableSynchronizationDownloadService;
        @PostMapping("oneWayDownload")
        @ApiOperation("下载")
            public CommonResult<TableSynchronizationDownloadRes> oneWayDownload(HttpServletRequest httpServletRequest, @RequestBody TableSynchronizationDownloadReq tableSynchronizationDownloadReq) {
            return tableSynchronizationDownloadService.oneWayDownload(httpServletRequest,tableSynchronizationDownloadReq);
        }
    }
    ```
1. `TableSynchronizationDownloadService`

    ```Java
    public interface TableSynchronizationDownloadService {
        CommonResult<TableSynchronizationDownloadRes> oneWayDownload(HttpServletRequest httpServletRequest, TableSynchronizationDownloadReq tableSynchronizationDownloadReq);
    }
    ```
1. `TableSynchronizationDownloadServiceImpl`

    ```Java
    @Service
    public class TableSynchronizationDownloadServiceImpl implements TableSynchronizationDownloadService {
        @Override
        public CommonResult<TableSynchronizationDownloadRes> oneWayDownload(HttpServletRequest httpServletRequest, TableSynchronizationDownloadReq tableSynchronizationDownloadReq) {
            String hospitalUid = HospitalInfo.getHospitalUid(httpServletRequest);
            if (StringUtils.isEmpty(hospitalUid)){
                return CommonResult.failed("Token获取的hospitalUid不能为空");
            }
            TableSyncHandler synHandler = SynHandlerFactory.getSynHandler(tableSynchronizationDownloadReq.getTableName());
            return synHandler.syncTable(hospitalUid, tableSynchronizationDownloadReq);
        }
    }
    ```
    > ❗ **注意点：**
    >
    > - `SynHandlerFactory.getSynHandler(tableSynchronizationDownloadReq.getTableName());` ：**根据`SynHandlerFactory` 对象工厂获取到想要用的 `Handler`**
    >
    > - `synHandler.syncTable(hospitalUid, tableSynchronizationDownloadReq);` ：**用不同的策略调用同步表的方法，而具体实现的逻辑是每个 `Handler` 自己实现的不同的同步逻辑**
1. `TableSyncHandler` ==**数据表同步的 Handler 接口⭐**==

    ```Java
    public interface TableSyncHandler extends InitializingBean {
        CommonResult syncTable(String hospitalUid, TableSynchronizationDownloadReq downloadReq);
    }
    ```
    > ❗ **注意点：**
    >
    > 1. 这里将 `TableSyncHandler` 接口**继承 `InitializingBean` ，可以将所有 `Handler` 交给 Spring 来管理，让Spring 来对** `tableSyncHandlerMap` 进行初始化
    >
    > 1. 继承后，在 `TableSyncHandler` 接口的实现类中，重写 **`afterPropertiesSet()`** 方法，在里面将当前实现类`Handler` 注册到 `tableSyncHandlerMap` 中（注册方法写在工厂中，见下）
    >
    > - 如果不这样做也可以，但是需要写初始化 `tableSyncHandlerMap` 的代码，即把所有 `Handler` 都放在 Map 中：（要把所有的 `handler` 都先依赖注入到当前类，代码也是很臃肿的。。。）
    >
    >     ![[IMG-20260315213656460.png|Untitled 1 208.png]]
    >
1. `AdviceInformationHandler` （医嘱表的同步处理器）

    ```Java
    @Service("adviceInformationHandler") // 交给 spring 管理
    @Component  // 可省略
    public class AdviceInformationHandler implements TableSyncHandler {
    		...
        @Override
        public void afterPropertiesSet() throws Exception {
            SynHandlerFactory.register(Constant.advice_information, this);
        }
        @Override
        public CommonResult syncTable(String hospitalUid, TableSynchronizationDownloadReq tableSynchronizationDownloadReq) {
            // 具体的同步表的逻辑
        }
    }
    ```
1. `BedInformationTblHandler`（病床信息表的同步处理器）

    ```Java
    @Service("bedInformationTblHandler")
    public class BedInformationTblHandler implements TableSyncHandler {
    		...
    		@Override
        public void afterPropertiesSet() throws Exception {
            SynHandlerFactory.register(Constant.bed_information, this);
        }
        @Override
        public CommonResult syncTable(String hospitalUid, TableSynchronizationDownloadReq tableSynchronizationDownloadReq) {
    				// 具体的同步表的逻辑
        }
    }
    ```
1. `SynHandlerFactory` ==**处理器工厂⭐**==

    ```Java
    public class SynHandlerFactory {
        private static Map<String, TableSyncHandler> tableSyncHandlerMap = new ConcurrentHashMap<>();
        public static TableSyncHandler getSynHandler(String tableName){
            return tableSyncHandlerMap.get(tableName);
        }
        public static void register (String tableName, TableSyncHandler tableSyncHandler) {
            if (StringUtils.isEmpty(tableName) || tableSyncHandler == null) {
                return;
            }
            tableSyncHandlerMap.put(tableName, tableSyncHandler);
        }
    }
    ```
    > ❗ **`SynHandlerFactory` 中提供了两个方法**
    >
    > 1. 一个是用于获取 `Handler` 对象的 `getSynHandler()`
    >
    > 1. 另一个是用于注册可能要用到的所有 `Handler` 对象，即将它们放在 Map 中
