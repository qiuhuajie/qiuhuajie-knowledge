---
title: "BlockingQueue 实现异步秒杀"
tags:
  - "中间件"
  - "中间件/Redis"
  - "中间件/Redis/Redis"
  - "异步秒杀"
  - "Redis"
  - "BlockingQueue"
updated: 2026-04-16
---

**（了解）**
> 💡 **存在问题**
> 1. 异步线程要从消息队列中取订单信息，而消息队列是使用 阻塞队列 `BlockingQueue` 实现的
> 2. 但是基于阻塞队列的异步秒杀存在一些问题：
>     - `BlockingQueue` 是 JDK 中的阻塞队列，会占 JVM 的内存，==带来内存限制问题==
>     - ==数据安全问题：==没有持久化机制，如果服务宕机，内存中阻塞队列的数据全部消失
# 一、阻塞队列 BlockingQueue
[[BlockingQueue]]
# 二、示例：BlockingQueue 实现异步秒杀
1. 实现方案：
    1. 新增秒杀优惠券的同时，将优惠券信息保存到Redis中
    2. 基于Lua脚本，判断秒杀库存、一人一单，决定用户是否抢购成功
    3. 如果抢购成功，将优惠券id和用户id封装后存入阻塞队列
    4. 开启线程任务，不断从阻塞队列中获取信息，实现异步下单功能

    ![[IMG-20260620224127740.png|800]]
2. 秒杀优惠券的业务 VoucherServiceImpl 中，在创建优惠券的同时，将优惠券的库存信息，存入redis缓存

    ```Java
     @Override
     @Transactional
     public void addSeckillVoucher(Voucher voucher) {
         // 保存优惠券
         save(voucher);
         // 保存秒杀信息
         ....
         //添加秒杀优惠券的同时，保存秒杀券信息到Redis缓存
         stringRedisTemplate.opsForValue().set("seckill:stock:" + voucher.getId(), voucher.getStock().toString());
     }
    ```
3. 编写Lua脚本

    ```Lua
     -- 1. 参数列表
     -- 优惠券Id
     local voucherId = ARGV[1]
     -- 用户Id
     local userId = ARGV[2]
     -- 2. 数据key
     -- 库存key
     local stockKey = "seckill:stock:" .. voucherId
     -- 订单key
     local orderKey = "seckill:order:" .. voucherId
     -- 3. 脚本业务
     -- 3.1 判断库存是否充足 get stockKey
     if(tonumber(redis.call('get', stockKey)) <= 0) then
         -- 库存不足返回1
         return 1
     end
     -- 3.2 判断用户是否下单 sismember orderKey userId
     if (tonumber(redis.call('sismember', orderKey, userId)) == 1) then
         -- 存在，即重复下单，返回2
         return 2
     end
     -- 3.4 扣库存 incrby stockKey -1
     redis.call('incrby', stockKey, -1)
     -- 3.5 下单（保存用户） sadd orderKey userId
     redis.call('sadd', orderKey, userId)
     return 0
    ```
4. VoucherOrderServiceImpl

    ```Java
     @Slf4j
     @Service
     public class VoucherOrderServiceImpl extends ServiceImpl<VoucherOrderMapper, VoucherOrder> implements IVoucherOrderService {
         @Resource
         private ISeckillVoucherService SeckillVoucherService;
         @Resource
         private RedisWorker redisWorker;
         @Resource
         private StringRedisTemplate stringRedisTemplate;
         //引入Lua脚本
         private static final DefaultRedisScript<Long> SECKILL_SCRIPT;
         static {
             SECKILL_SCRIPT = new DefaultRedisScript<>();
             SECKILL_SCRIPT.setLocation(new ClassPathResource("seckill.lua"));
             SECKILL_SCRIPT.setResultType(Long.class);
         }
         //⭐创建阻塞队列
         private BlockingQueue<VoucherOrder> orderBlockingQueue = new ArrayBlockingQueue<>(1024 * 1024);
         //⭐创建异步线程
         private static final ExecutorService SECKILL_ORDER_EXECUTOR = Executors.newSingleThreadExecutor();
         //⭐加载类时，异步线程就去阻塞队列中读取订单数据
         @PostConstruct
         private void init(){
             SECKILL_ORDER_EXECUTOR.submit(new VoucherOrderHandler());
         }
         //异步线程需要执行的Task
         private class VoucherOrderHandler implements Runnable{
             @Override
             public void run() {
                 while (true){
                     try {
                         //1. ⭐获取阻塞列中的订单信息
                         VoucherOrder voucherOrder = orderBlockingQueue.take();
                         //2. 扣除库存、保存订单
                         createVoucherOrder(voucherOrder);
                     } catch (Exception e) {
                         log.error("处理订单时异常",e);
                     }
                 }
             }
         }
         //扣除库存、保存订单
         private void createVoucherOrder(VoucherOrder voucherOrder) {
             //扣减库存
             boolean success = SeckillVoucherService.update()
                     .setSql("stock = stock - 1")
                     .eq("voucher_id", voucherOrder.getId())
                     .gt("stock",0)
                     .update();
             if (!success) {
                 log.error("库存不足！");
                 return;
             }
             //保存订单
             save(voucherOrder);
         }
         @Override
         public Result seckillVoucher(Long voucherId) {
             Long userId = UserHolder.getUser().getId();
             //1. ⭐执行lua脚本
             Long result = stringRedisTemplate.execute(SECKILL_SCRIPT, Collections.emptyList(), voucherId.toString(), userId.toString());
             //2. 判断结果是否为0
             assert result != null;
             int r = result.intValue();
             if (r != 0) {
                 //3. 不为0，代表没有购买资格
                 return Result.fail(r == 1 ? "库存不足" : "不能重复下单");
             }
             //4. 为0，代表有购买资格，把下单信息保存在阻塞队列
             VoucherOrder voucherOrder = new VoucherOrder();
             //4.1 设置订单Id
             long voucherOrderId = redisWorker.nextID("voucher_order");
             voucherOrder.setId(voucherOrderId);
             //4.2 设置用户Id
             voucherOrder.setUserId(userId);
             //4.3 设置代金券Id
             voucherOrder.setVoucherId(voucherId);
             //⭐将订单信息保存在阻塞队列中
             orderBlockingQueue.add(voucherOrder);
             //5. 返回订单Id
             return Result.ok(voucherOrderId);
         }
     }
    ```
    > 💡 **@PostConstruct**
    > - 作用：`@PostConstruct`注解的方法在项目启动的时候执行这个方法，也可以理解为在spring容器启动的时候执行
    > - 需要使用 `@PostConstruct` 的情况
    >     - 首先明确整个Bean初始化中的执行顺序：
    >         > Constructor(构造方法) ➡️ @Autowired(依赖注入) ➡️ @PostConstruct(注释的方法)
    >     - 那么如果想在生成对象时完成某些初始化操作，而偏偏这些初始化操作又依赖于依赖注入
    >     - **由于依赖注入是在构造方法之后才执行，那么就无法在构造函数中实现**
    >     - 为此，可以使用`@PostConstruct`注解一个方法来完成初始化，`@PostConstruct` 注解的方法将会在依赖注入完成后被自动调用

# 三、测试访问
[http://localhost:8080/api/voucher-order/seckill/12](http://localhost:8080/api/voucher-order/seckill/12)（记得带token）
1. redis
    1. 保存已购用户的set
    2. 优惠券库存
2. 数据库（业务执行完整）
