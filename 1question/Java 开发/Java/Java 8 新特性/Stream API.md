- [[#1. Stream API 简介]]
- [[#2. Stream 的三个操作步骤]]
    - [[#2.1 Stream 的实例化]]
    - [[#2.2 Stream 的中间操作]]
        - [[#a. 筛选与切片]]
        - [[#b. 映射]]
        - [[#c. 排序]]
    - [[#2.3 Stream的终止操作]]
        - [[#a. 匹配与查找]]
        - [[#b. 归约]]
        - [[#c. 收集]]
# 1. **Stream API 简介**
1. **Java Stream 是 Java 8 引入的一个新特性，用于**==**简化集合类（Collection）的操作**==
    
    1. 它允许开发人员以**声明式**的方式处理集合，而不是使用传统的迭代方式
    
    1. Stream 可以看作是**对集合的函数式操作**，Stream 的操作可以更加灵活，能够处理更加复杂的逻辑
    
    1. 可以通过一系列的中间操作对集合进行处理，并返回一个新的 Stream 对象，最终通过终止操作来生成结果
    
    1. 并且**支持并行**化操作，可以提高程序的执行效率
    
1. **🙋‍♂️ Stream 操作可以分为两类：**==**中间操作**== **和** ==**终止操作**==
    
    1. **中间操作**包括：过滤、映射、排序、去重等
    
    1. **终止操作**包括：计数、查找、归约、收集等
    
1. Stream 和 Collection 集合的区别：
    
    1. **Collection** 是一种静态的内存数据结构，而 **Stream** 是有关计算的
    
    1. 前者是主要面向内存，存储在内存中；后者主要是面向 CPU，通过 CPU 实现计算
    
    1. 集合讲的是数据， Stream 讲的是计算
        
        1. Stream 自己不会存储元素
        
        1. Stream 不会改变源对象。相反，他们会返回一个持有结果的**新 Stream**
        
        1. Stream 操作是**延迟执行的**。这意味着他们会等到**需要结果的时候才执行**
        
    
# 2. Stream 的三个操作步骤
![[IMG-20260405035413790.png]]
- **创建 Stream**：一个数据源（如：集合、数组），获取一个流
- **中间操作**：一个中间操作链，对数据源的数据进行处理
- **终止操作**（终端操作）：一旦执行终止操作， 才会执行中间操作链（ `Lazy Evalustion`），并产生结果；之后便不会再被使用
![[IMG-20260404031802706.png]]
## 2.1 **Stream 的实例化**
1. 方式一：⭐通过集合实例化
    
    ```Java
     class getData {
         public static List<Person> getArrayList(){
             ArrayList<Person> peoples = new ArrayList<>();
             peoples.add(new Person("Tom",23));
             peoples.add(new Person("Jack",22));
             peoples.add(new Person("Mike",21));
             peoples.add(new Person("Ted",20));
             return peoples;
         }
     }
     
     public class test{
         public static void main(String[] args) {
             List<Person> peoples = getData.getArrayList();
    
             //  default Steam<E> stream() : 返回一个顺序流
             Stream<Person> stream = peoples.stream();
     
             //  default Steam<E> parallelStream() : 返回一个并行流
             Stream<Person> personStream = peoples.parallelStream();
         }
     }
    ```
    
1. 方式二：通过数组实例化：
    
    ```Java
     //调用Array类的static <T> stream(T[] array): 返回一个流
     int[] ints = new int[]{1,2,3,4,5};
     IntStream stream1 = Arrays.stream(ints);
     
     Person p1 = new Person("Tom", 22);
     Person p2 = new Person("Jack", 22);
     Person[] peoples = {p1, p2};
     Stream<Person> stream2 = Arrays.stream(peoples);
    ```
    
1. 方式三：通过Stream的of( )
    
    ```Java
     Stream<Integer> stream = Stream.of(1, 2, 3, 4, 5);
    ```
    
1. 方式四：创建无限流
    
    ```Java
     //迭代 :public static<T> Stream<T> iterate(final T seed, final UnaryOperator<T> f)
     Stream.iterate(0,t->t+2).limit(10).forEach(System.out::println);
     
     //生成 :public static<T> Stream<T> generate(Supplier<T> s)
     Stream.generate(Math::random).limit(10).forEach(System.out::println);
    ```
    
## 2.2 **Stream 的中间操作**
![[IMG-20260405035420152.png]]
### a. **筛选与切片**
1. ⭐ `**filter(Predicate p)**`：接收 Lambda ， 从流中**排除某些元素**
    
    ```Java
    peoples.stream().filter(e -> e.getAge() > 20).forEach(System.out::println);
    //只有当终止操作forEach()执行时，才会产生结果
    ```
    
    ```Java
    // 过滤掉已经关闭的病区信息
    List<WardDto> collect = wardDtos.stream().filter(cur -> {
        if (CommonConstants.WARD_USE_TYPE_ALL_OFF.equals(cur.getUseType())) {
            return false;
        }else {
            return true;
        }
    }).collect(Collectors.toList());
    ```
    
1. `**distinct(n)**`：筛选，通过流所生成元素的 hashCode() 和 equals() **去除重复元素**
    
    ```Java
    //去重（元素类一定要实现 hashCode() 和 equals() ）
     peoples.add(new Person("Tom",23));
     peoples.add(new Person("Tom",23));
    
     peoples.stream().distinct().forEach(System.out::println);
    ```
    
1. `**limit(long maxSize)**`：截断流，**使其元素不超过给定数量**
    
    ```Java
    peoples.stream().limit(3).forEach(System.out::println);
    ```
    
1. `**skip(long n)**`：
    
    - 跳过元素，返回一个**扔掉了前 n 个元素**的流
    
    - 若流中元素不足 n 个，则返回一 个空流
    
    - 与 `limit(n)` 互补
    
    ```Java
    peoples.stream().skip(1).forEach(System.out::println);
    ```
    
### b. **映射**
1. ⭐ `**map(Function f)**`：接收一个函数作为参数
    
    - ==该函数会被应用到==**==每个元素上==**
    
    - ==并将其==**==映射成一个新的元素==**
    
    ```Java
    List<String> list = Arrays.asList("aa", "bb", "cc", "dd");
    //map(Function f)
    list.stream().map(e -> e.toUpperCase()).forEach(System.out::println);
    //AA BB CC DD
    ```
    
    ```Java
    // 从病区信息的 List<DTO> 中获取 List<String ID>
    List<String> wardIdList = wardManagementRelationshipDtos.stream().map(WardManagementRelationshipDto::getWardUid).collect(Collectors.toList());
    ```
    
    > map练习：找出名字长度大于3的人的名字
    
    ```Java
     List<Person> peoples = getData.getArrayList();
     Stream<String> namesstream = peoples.stream().map(e -> e.getName());
     namesstream.filter(name -> name.length() > 3).forEach(System.out::println);
     //Jack Mike
    ```
    
1. `**flatMap(Function f)**`：接收一个函数作为参数，将流中的每个值都换成另 一个流，然后把所有流连接成一个流
    
    ```Java
     //类比理解：
     ArrayList list1 = new ArrayList();
     list1.add(1);
     list1.add(2);
     list1.add(3);
     
     ArrayList list2 = new ArrayList();
     list2.add(4);
     list2.add(5);
     list2.add(6);
     
     //1.
     //list1.add(list2);
     //System.out.println(list1);
     //[1, 2, 3, [4, 5, 6]]，集合里面套集合
     
     //2.
     list1.addAll(list2);
     System.out.println(list1);
     //[1, 2, 3, 4, 5, 6]，将list2拆开放入list1
    ```
    
    ```Java
     public class test{
    
         //此方法返回一个stream流
         public static Stream<Character> fromStringToStream(String str){
             ArrayList<Character> list = new ArrayList<>();
             for (Character c : str.toCharArray()
                  ) {
                 list.add(c);
             }
             return list.stream();
         }
    
         public static void main(String[] args) {
             List<String> list = Arrays.asList("aa", "bb", "cc", "dd");
    
             //flatMap(Function f)
    
             //每次将list中的每个字符串传入方法后，就得到一个流
             //如果使用map会得到流中包含流
             Stream<Stream<Character>> stream1 = list.stream().map(s -> test.fromStringToStream(s));
             stream1.forEach(System.out::println);
             //结果：流中的流
             //java.util.stream.ReferencePipeline$Head@568db2f2
             //java.util.stream.ReferencePipeline$Head@378bf509
             //java.util.stream.ReferencePipeline$Head@5fd0d5ae
             //java.util.stream.ReferencePipeline$Head@2d98a335
     
             //如果使用flatMap会将每个流的内容拿出来，合到一个流中
             Stream<Character> stream = list.stream().flatMap(s -> test.fromStringToStream(s));
             stream.forEach(System.out::print);
             //a a b b c c d d
         }
     }
    ```
    
1. `**mapToDouble(ToDoubleFunction f)**`：接收一个函数作为参数，该函数会被应用到每个元素上，产生一个新的 DoubleStream
1. `**mapToInt(ToIntFunction f)**`：接收一个函数作为参数，该函数会被应用到每个元素上，产生一个新的 IntStream
1. `**mapToLong(ToLongFunction f)**`：接收一个函数作为参数，该函数会被应用到每个元素上，产生一个新的 LongStream
### c. **排序**
1. **`sorted()`**：产生一个新流，其中按自然顺序排序
    
    ```Java
     List<String> list = Arrays.asList("aa", "bb", "dd", "cc");
     list.stream().sorted().forEach(System.out::println);
    ```
    
1. `**sorted(Comparator com)**`：产生一个新流，其中按比较器顺序排序
    
    ```Java
     //List<Person> peoples = getData.getArrayList();
     //peoples.stream().sorted().forEach(System.out::println);
     //抛出ClassCastException，Person没有实现Comparable接口
     
     //定制排序,按年龄排
     List<Person> peoples = getData.getArrayList();
     peoples.stream().sorted((e1,e2) -> Integer.compare(e1.getAge(),e2.getAge())).forEach(System.out::println);
    ```
    
## 2.3 **Stream的终止操作**
### a. **匹配与查找**
1. `**allMatch(Predicate p)**`：检查是否匹配所有元素
1. `**anyMatch(Predicate p)**`：检查是否至少匹配一个元素
1. ✅ `**noneMatch(Predicate p)**`：检查是否没有匹配所有元素
    
    ```Java
    if (addressDTOS.stream().noneMatch(
            p -> p.getPosition().equalsIgnoreCase(travelItemAddress.getPosition()))) {
        ...
    }
    ```
    
1. ✅ `**findFirst()**`：返回第一个元素
    
    1. 返回的是一个`Optional`对象，这个对象包含了该stream中的第一个元素或者一个空的`Optional`
    
    1. 如果`lis`中没有元素，那么返回的就是空的`Optional`对象
    
    1. 如果需要获取 `Optional`对象中的元素，可以使用`orElse()`方法：如果`Optional`对象不为空，则返回其中的元素，否则返回一个默认值
    
    ```Java
    // 解析商品上的国家属性
    for (TravelItem item : travelItems) {
        Integer nationIdPid = item.getItemDO().getItemProperties().stream()
                .filter(p -> p.getPropertyId() == AREA_PID)
                .map(ItemPVPairDO::getSubPropId)
                .findFirst().orElse(null);
        if (nationIdPid == null) {
            continue;
        }
        ...
    }
    ```
    
1. `**findAny()**`：返回当前流中的任意元素
1. `**count()**`：返回流中元素总数
1. `**max(Comparator c)**`：返回流中最大值
1. `**min(Comparator c)**`：返回流中最小值
1. ✅ `**forEach(Consumer c)**`：内部迭代 ,使用 Collection 接口需要用户去做迭代， 称为外部迭代，Stream API 使用内部迭代——它帮你把迭代做了
    
    ```Java
    travelItem.getSkuList().stream()
    				.filter(o -> o.getPickUpSelf() && skuSet.contains(o.getSkuId()))
    				.forEach(o -> {
    				    ...
    				    });
    				});
    ```
    
### b. **归约**
1. `**reduce(T iden, BinaryOperator b)**`：可以**将流中元素反复结合起来，得到一个值**。返回 T
    
    ```Java
    List<Integer> list = Arrays.asList(1,2,3,4,5,6);
    
    Integer sum = list.stream().reduce(0, (x, y) -> Integer.sum(x, y));
    System.out.println(sum);//21
    ```
    
1. `**reduce(BinaryOperator b)**`：可以将流中元素反复结合起来，得到一个值。返回 Optional<T>
    
    ```Java
    List<Person> peoples = getData.getArrayList();
    
    Stream<Integer> ageStream = peoples.stream().map(p ->p.getAge());
    
    Optional<Integer> ageSum = ageStream.reduce((x, y) -> Integer.sum(x, y));
    
    System.out.println(ageSum);
    ```
    
### c. **收集**
⭐ `**collect(Collector c)**`：
- 将流转换为其他形式
- 接收一个 Collector 接口的实现，用于给 Stream 中元素做汇总的方法
    
    ```Java
     List<Person> peoples = getData.getArrayList();
     //收集到List中
     List<Person> personList = peoples.stream().filter(p -> p.getAge() > 20).collect(Collectors.toList());
     personList.forEach(System.out::println);
     
     //收集到Set中
     Set<Person> personSet = peoples.stream().filter(p -> p.getAge() > 20).collect(Collectors.toSet());
     personSet.forEach(System.out::println);
    ```