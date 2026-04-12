# 介绍
1. 如果一个**接口**中==**只声明了一个抽象方法**==，则就是函数式接口
1. 可以通过 Lambda 表达式来创建该接口的对象
1. 可以在一个接口上使用 `@FunctionalInterface` 注解，这样做可以检查它是否是一个函数式接口
1. Java 内置四大核心函数式接口
    
    ![[Attachment/1question/大数据/Java 开发/Java/Java 8 新特性/IMG-20260405035413796.png|Untitled 280.png]]
    
1. 其他接口
    
    ![[IMG-20260404031802969.png|Untitled 1 210.png]]
    
  
# 示例一
1. 场景-工作中是否会经常遇到以下场景：
    
    1. **字段映射繁复**：表中存储某个字段作为 ID 或唯一标识符，但返回给其他人时需做大量字段映射。
        
        举例来说，某业务数据的统计表，是在表中设置一个业务 id（business_id）字段，而在业务配置表（business_config）中存储具体业务信息。在给前端同学提供统计查询接口时，需要根据业务 id 在业务配置表查找业务名称等信息，映射到统计数据中，一并返回给前端。
        
    
    1. **联表查询不适**：源表与配置表的关系不适合或不希望使用联表查询处理。
    
    1. **涉及多种场景**：字段映射涉及多种不同场景，但在这些场景中都采用了相同的处理逻辑，具有共同的特点。
    
1. 优化前
    
    ```Java
    List<BusinessData> list = businessDataService.listBusinessDataByParam(param);
    if (CollectionUtils.isEmpty(list)) {
        return;
    }
    // 获取所有唯一的业务ID
    List<Long> idList = list.stream().map(BusinessData::getBusinessId).distinct().collect(Collectors.toList());
    // 根据ID列表批量查询业务实体
    List<BusinessEntity> businessList = businessService.listBusinessByIds(idList);
    // 将查询结果按ID分组为Map
    Map<Long, BusinessEntity> businessId2EntityMap = businessList.stream().collect(Collectors.toMap(BusinessEntity::getId, Function.identity(), (v1, v2) -> v1));
    // 对原始数据进行字段映射
    for (BusinessData result : list) {
        BusinessEntity businessEntity = businessId2EntityMap.get(result.getBusinessId());
        if (businessEntity != null) {
            result.setBusinessName(businessEntity.getName());
        }
    }
    ```
    
1. 优化后
    
    把基本步骤定义出来，变化部分作为入参传入，即可实现。
    
    ```Java
    public <Source, QueryResult, IdType> void mappingFields(List<Source> sourceList, Function<Source, IdType> idExtractor, Function<List<IdType>, List<QueryResult>> queryFunction, Function<QueryResult, IdType> groupByFunction, BiConsumer<Source, QueryResult> setterFunction) {
        if (CollectionUtils.isEmpty(sourceList)) {
            return;
        }
        // 提取所有唯一标识
        List<IdType> idList = sourceList.stream().map(idExtractor).filter(Objects::nonNull).distinct().collect(Collectors.toList());
        if (CollectionUtils.isEmpty(idList)) {
            return;
        }
        // 查询结果
        List<QueryResult> queryResultList = queryFunction.apply(idList);
        if (CollectionUtils.isEmpty(queryResultList)) {
            return;
        }
        Map<IdType, QueryResult> temp2ResultMap = queryResultList.stream().collect(Collectors.toMap(groupByFunction, Function.identity()));
        // 将结果映射回原对象
        sourceList.forEach(item -> {
            IdType id = idExtractor.apply(item);
            QueryResult queryResult = temp2ResultMap.get(id);
            if (queryResult != null) {
                setterFunction.accept(item, queryResult);
            }
        });
    }
    ```
    
    ```Java
    mapperService.mappingFields(data, BusinessData::getBusinessId, businessMapper::listBusinessByIdList, BusinessData::getBusinessId, (source, query) -> source.setBusinessName(query.getName()));
    ```
    
# 示例二
1. 在 Java 引入 lambda 表达式之前，一些结构近似，但操作对象类型不同的代码，是难以复用的。有了函数式编程后，可以简化很多类似的冗余代码，下面是具体的示例。
1. 重构前：业务逻辑做的是遍历数据对象，将不同属性的值求和，为便于展示，将不同场景代码放在一起，因为存在各种 DO、DTO、VO 等，相近的结构在代码中反复出现。
    
    ```Java
    List<SecurityCheckRecordDetailDO> list1 = List.of();
    // Case 1: List元素的Integer属性求和
    list1.stream().map(SecurityCheckRecordDetailDO::getPassPieces)
        .filter(Objects::nonNull)
        .reduce(Integer::sum)
        .orElse(0);
    // Case 2: 相同数据对象,不同类型属性（BigDecimal）求和
    list1.stream().map(SecurityCheckRecordDetailDO::getFailWeight)
        .filter(Objects::nonNull)
        .reduce(BigDecimal::add)
        .orElse(BigDecimal.ZERO);
    // Case 3: 不同的数据对象类型 SearchCargoInventoryResultDTO
    List<SearchCargoInventoryResultDTO> list2 = List.of();
    list2.stream().map(SearchCargoInventoryResultDTO::getPieces)
        .filter(Objects::nonNull)
        .reduce(Integer::sum)
        .orElse(0);
    // 几个Case抽象看有同样的结构：遍历集合、获取数据、加工、返回（默认值）
    ```
    
1. 通过模板方法把类似代码结构抽象出来，使用时通过函数参数将取数逻辑和处理逻辑传入，以精简代码提高复用度。
    
    ```Java
    /**
     * 将逻辑抽象成模板方法
     * @param mapFunction 取数逻辑
     * @param reduceFunction 处理逻辑
     * @param defaultValue 默认值
     */
    public static <T, C> C collectionExtract(Collection<T> collection
            , Function<T, C> mapFunction, BinaryOperator<C> reduceFunction
            , C defaultValue) {
        return collection.stream()
            .filter(Objects::nonNull)
            .map(mapFunction)
            .filter(Objects::nonNull)
            .reduce(reduceFunction)
            .orElse(defaultValue);
    }
    // 为使用方便，提供快捷实现，比如Integer求和
    public static <T> Integer sumIntegerField(Collection<T> collection
            , Function<T, Integer> fieldExtractFuntion) {
        return collectionExtract(collection, fieldExtractFuntion, Integer::sum, 0);
    }
    // BigDecimal求和
    public static <T> BigDecimal sumBigDecimalField(Collection<T> collection
            , Function<T, BigDecimal> fieldExtractFuntion) {
        return collectionExtract(collection, fieldExtractFuntion
            , BigDecimal::add, BigDecimal.ZERO);
    }
    // 甚至可以扩展到其他场景，如取Date属性的最大最小值
    public static <T> Date extractMinDate(Collection<T> collection
            , Function<T, Date> fieldExtractFuntion) {
        return collectionExtract(collection, fieldExtractFuntion
            , BinaryOperator.minBy(Date::compareTo), null);
    }
    ```
    
    调用
    
    ```Java
    List<SecurityCheckRecordDetailDO> list1 = List.of();
    // Case 1: List元素的Integer属性求和
    sumIntegerField(list1, SecurityCheckRecordDetailDO::getPassPieces);
    // Case 2: 相同数据对象,不同类型属性（BigDecimal）求和
    sumBigDecimalField(list1, SecurityCheckRecordDetailDO::getFailWeight);
    // Case 3: 不同的数据对象类型 SearchCargoInventoryResultDTO
    List<SearchCargoInventoryResultDTO> list2 = List.of();
    sumIntegerField(list2, SearchCargoInventoryResultDTO::getPieces);
    // 最大最小值的Case类似，不重复举例
    ```