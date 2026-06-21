---
title: "Seata 使用"
tags:
  - "seata-server-0_9_0"
  - "Seata_使用"
  - "事务测试"
  - "Seata"
  - "分布式事务"
  - "yaml_配置文件"
updated: 2026-04-16
---

# 一、演示案例架构
1. 应用案例：Seata 分布式交易解决方案：
    1. 在 **Spring 单体服务**中开启事务的方式：`@Transactional`
    2. 而**分布式事务**的开启：只需要使用一个 **`@GlobalTransactional`** 在业务类上
2. **实践 订单/库存/账户业务 案例架构图：**
    ![[IMG-20260405035413904.png|800]]
# 二、Seata-Server 安装
1. 下载：[https://github.com/seata/seata/releases](https://github.com/seata/seata/releases)**（0.9里由sql脚本、1.4没有...好像是在github的readme里）**
2. 修改conf目录下的`file.conf`配置文件：自定义事务组名称+事务日志存储模式为db+数据库连接信息

    ```JSON
    service {
      \#transaction service group mapping
      # 🟡自定义事务组名称
      \#vgroup_mapping.my_test_tx_group = "default"
      vgroup_mapping.my_test_tx_group = "qhj_tx_group"
      \#only support when registry.type=file, please don't set multiple addresses
      default.grouplist = "127.0.0.1:8091"
      \#disable seata
      disableGlobalTransaction = false
    }
    ## transaction log store, only used in seata-server
    store {
      ## store mode: file、db
      # 🟡事务日志存储模式为db
      \#mode = "file"
      mode = "db"
      ## file store property
      file {
        ## store location dir
        dir = "sessionStore"
      }
      ## database store property
      db {
        ## the implement of javax.sql.DataSource, such as DruidDataSource(druid)/BasicDataSource(dbcp) etc.
        datasource = "dbcp"
        ## mysql/oracle/h2/oceanbase etc.
        db-type = "mysql"
        driver-class-name = "com.mysql.jdbc.Driver"
        # 🟡数据库连接信息
        url = "jdbc:mysql://127.0.0.1:3306/seata"
        user = "root"
        password = "ZXT774276296qq.."
      }
    }
    ```
3. mysql5.7 数据库新建库 seata
4. 在seata库里建表：`\seata-server-0.9.0\seata\conf\db_store.sql`

    ![[IMG-20260404031846876.png|800]]

5. 修改`seata-server-0.9.0\seata\conf`目录下的`registry.conf`配置文件：将

    ```JSON
    registry {
      # file 、nacos 、eureka、redis、zk、consul、etcd3、sofa
      # 🟡注册在 nacos
      \#type = "file"
      type = "nacos"
      nacos {
         # 🟡nacos 连接地址
        \#serverAddr = "localhost"
      serverAddr = "localhost:8848"
        namespace = ""
        cluster = "default"
      }
      eureka {
        serviceUrl = "http://localhost:8761/eureka"
        application = "default"
        weight = "1"
      }
      redis {
        serverAddr = "localhost:6379"
        db = "0"
      }
      zk {
        cluster = "default"
        serverAddr = "127.0.0.1:2181"
        session.timeout = 6000
        connect.timeout = 2000
      }
      consul {
        cluster = "default"
        serverAddr = "127.0.0.1:8500"
      }
      etcd3 {
        cluster = "default"
        serverAddr = "http://localhost:2379"
      }
      sofa {
        serverAddr = "127.0.0.1:9603"
        application = "default"
        region = "DEFAULT_ZONE"
        datacenter = "DefaultDataCenter"
        cluster = "default"
        group = "SEATA_GROUP"
        addressWaitTime = "3000"
      }
      file {
        name = "file.conf"
      }
    }
    ...
    ```
6. 先启动 Nacos 端口号 8848
7. 再启动seata-server：`softs\seata-server-0.9.0\seata\bin\seata-server.bat`

    ![[IMG-20260405035420312.png|800]]

# 三、订单/库存/账户业务 数据库准备
1. 分布式 订单/库存/账户业务 说明：
    1. 这里我们会创建三个服务，一个订单服务，一个库存服务，一个账户服务
    2. 当用户下单时，会在订单服务中创建一个订单，然后通过远程调用库存服务来扣减下单商品的库存，再通过远程调用账户服务来扣减用户账户里面的余额，最后在订单服务中修改订单状态为已完成
    3. 该操作跨越三个数据库，有两次远程调用，很明显会有分布式事务问题
2. 下订单--->扣库存--->减账户(余额)
## 1. 创建数据库
1. seata_order：存储订单的数据库
2. seata_storage：存储库存的数据库
3. seata_account：存储账户信息的数据库

    ```SQL
    CREATE DATABASE seata_order;
    CREATE DATABASE seata_storage;
    CREATE DATABASE seata_account;
    ```
## 2. 三个数据库创建数据表
1. seata_order库下建t_order表

    ```SQL
    CREATE TABLE t_order (
      `id` BIGINT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `user_id` BIGINT(11) DEFAULT NULL COMMENT '用户id',
      `product_id` BIGINT(11) DEFAULT NULL COMMENT '产品id',
      `count` INT(11) DEFAULT NULL COMMENT '数量',
      `money` DECIMAL(11,0) DEFAULT NULL COMMENT '金额',
      `status` INT(1) DEFAULT NULL COMMENT '订单状态：0：创建中；1：已完结'
    ) ENGINE=INNODB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
    SELECT * FROM t_order;
    ```
2. seata_storage库下建t_storage 表

    ```SQL
    CREATE TABLE t_storage (
     `id` BIGINT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
     `product_id` BIGINT(11) DEFAULT NULL COMMENT '产品id',
     `total` INT(11) DEFAULT NULL COMMENT '总库存',
     `used` INT(11) DEFAULT NULL COMMENT '已用库存',
     `residue` INT(11) DEFAULT NULL COMMENT '剩余库存'
    ) ENGINE=INNODB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
    INSERT INTO seata_storage.t_storage(`id`, `product_id`, `total`, `used`, `residue`)
    VALUES ('1', '1', '100', '0', '100');
    SELECT * FROM t_storage;
    ```
3. seata_account库下建t_account 表

    ```SQL
    CREATE TABLE t_account (
      `id` BIGINT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'id',
      `user_id` BIGINT(11) DEFAULT NULL COMMENT '用户id',
      `total` DECIMAL(10,0) DEFAULT NULL COMMENT '总额度',
      `used` DECIMAL(10,0) DEFAULT NULL COMMENT '已用余额',
      `residue` DECIMAL(10,0) DEFAULT '0' COMMENT '剩余可用额度'
    ) ENGINE=INNODB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
    INSERT INTO seata_account.t_account(`id`, `user_id`, `total`, `used`, `residue`)  VALUES ('1', '1', '1000', '0', '1000');
    SELECT * FROM t_account;
    ```
## 3. 三个数据库创建回滚日志表
1. 三个数据库分别执行：`\seata-server-0.9.0\seata\conf`目录下的`db_undo_log.sql`

    ```SQL
    drop table `undo_log`;
    CREATE TABLE `undo_log` (
      `id` bigint(20) NOT NULL AUTO_INCREMENT,
      `branch_id` bigint(20) NOT NULL,
      `xid` varchar(100) NOT NULL,
      `context` varchar(128) NOT NULL,
      `rollback_info` longblob NOT NULL,
      `log_status` int(11) NOT NULL,
      `log_created` datetime NOT NULL,
      `log_modified` datetime NOT NULL,
      `ext` varchar(100) DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `ux_undo_log` (`xid`,`branch_id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
    ```
2. 最终DB：

    ![[IMG-20260405035426916.png|311]]

# 四、订单/库存/账户业务 微服务准备

**下订单 \to 减库存 \to 扣余额 \to 改(订单)状态**

## 1. 订单微服务 2001
1. **新建Moudle：seata-order-service2001**
2. **pom.xml**

    ```XML
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <parent>
            <artifactId>springCloudProject</artifactId>
            <groupId>com.atguigu.springcloud</groupId>
            <version>1.0-SNAPSHOT</version>
        </parent>
        <modelVersion>4.0.0</modelVersion>
        <artifactId>seata-order-service2001</artifactId>
        <dependencies>
            <!--nacos-->
            <dependency>
                <groupId>com.alibaba.cloud</groupId>
                <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
            </dependency>
            <!--seata-->
            <dependency>
                <groupId>com.alibaba.cloud</groupId>
                <artifactId>spring-cloud-starter-alibaba-seata</artifactId>
                <exclusions>
                    <exclusion>
                        <artifactId>seata-all</artifactId>
                        <groupId>io.seata</groupId>
                    </exclusion>
                </exclusions>
            </dependency>
            <dependency>
                <groupId>io.seata</groupId>
                <artifactId>seata-all</artifactId>
                <version>0.9.0</version>
            </dependency>
            <!--feign-->
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-starter-openfeign</artifactId>
            </dependency>
            <!--web-actuator-->
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-web</artifactId>
            </dependency>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-actuator</artifactId>
            </dependency>
            <!--mysql-druid-->
            <dependency>
                <groupId>mysql</groupId>
                <artifactId>mysql-connector-java</artifactId>
                <version>5.1.37</version>
            </dependency>
            <dependency>
                <groupId>com.alibaba</groupId>
                <artifactId>druid-spring-boot-starter</artifactId>
                <version>1.1.10</version>
            </dependency>
            <dependency>
                <groupId>org.mybatis.spring.boot</groupId>
                <artifactId>mybatis-spring-boot-starter</artifactId>
                <version>2.0.0</version>
            </dependency>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-test</artifactId>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <optional>true</optional>
            </dependency>
        </dependencies>
    </project>
    ```
3. **yaml 配置文件**

    ```YAML
    server:
      port: 2001
    spring:
      application:
        name: seata-order-service
      cloud:
        alibaba:
          seata:
            # 自定义事务组名称需要与seata-server中的对应
            tx-service-group: qhj_tx_group
        nacos:
          discovery:
            server-addr: localhost:8848
      datasource:
        driver-class-name: com.mysql.jdbc.Driver
        url: jdbc:mysql://localhost:3306/seata_order
        username: root
        password: ZXT774276296qq..
    feign:
      hystrix:
        enabled: false
    logging:
      level:
        io:
          seata: info
    mybatis:
      mapperLocations: classpath:mapper/*.xml
    ```
4. **file.conf**

    ```JSON
    transport {
      # tcp udt unix-domain-socket
      type = "TCP"
      \#NIO NATIVE
      server = "NIO"
      \#enable heartbeat
      heartbeat = true
      \#thread factory for netty
      thread-factory {
        boss-thread-prefix = "NettyBoss"
        worker-thread-prefix = "NettyServerNIOWorker"
        server-executor-thread-prefix = "NettyServerBizHandler"
        share-boss-worker = false
        client-selector-thread-prefix = "NettyClientSelector"
        client-selector-thread-size = 1
        client-worker-thread-prefix = "NettyClientWorkerThread"
        # netty boss thread size,will not be used for UDT
        boss-thread-size = 1
        \#auto default pin or 8
        worker-thread-size = 8
      }
      shutdown {
        # when destroy server, wait seconds
        wait = 3
      }
      serialization = "seata"
      compressor = "none"
    }
    service {
      ## 🟡修改自定义事务组名称
      vgroup_mapping.qhj_tx_group = "default"
      default.grouplist = "127.0.0.1:8091"
      enableDegrade = false
      disable = false
      max.commit.retry.timeout = "-1"
      max.rollback.retry.timeout = "-1"
      disableGlobalTransaction = false
    }
    client {
      async.commit.buffer.limit = 10000
      lock {
        retry.internal = 10
        retry.times = 30
      }
      report.retry.count = 5
      tm.commit.retry.count = 1
      tm.rollback.retry.count = 1
    }
    ## transaction log store
    store {
      ## 🟡store mode: file、db
      mode = "db"
      ## file store
      file {
        dir = "sessionStore"
        # branch session size , if exceeded first try compress lockkey, still exceeded throws exceptions
        max-branch-session-size = 16384
        # globe session size , if exceeded throws exceptions
        max-global-session-size = 512
        # file buffer size , if exceeded allocate new buffer
        file-write-buffer-cache-size = 16384
        # when recover batch read size
        session.reload.read_size = 100
        # async, sync
        flush-disk-mode = async
      }
      ## database store
      db {
        ## the implement of javax.sql.DataSource, such as DruidDataSource(druid)/BasicDataSource(dbcp) etc.
        datasource = "dbcp"
        ## 🟡mysql/oracle/h2/oceanbase etc.
        db-type = "mysql"
        driver-class-name = "com.mysql.jdbc.Driver"
        url = "jdbc:mysql://127.0.0.1:3306/seata"
        user = "root"
        password = "ZXT774276296qq.."
        min-conn = 1
        max-conn = 3
        global.table = "global_table"
        branch.table = "branch_table"
        lock-table = "lock_table"
        query-limit = 100
      }
    }
    lock {
      ## the lock store mode: local、remote
      mode = "remote"
      local {
        ## store locks in user's database
      }
      remote {
        ## store locks in the seata's server
      }
    }
    recovery {
      \#schedule committing retry period in milliseconds
      committing-retry-period = 1000
      \#schedule asyn committing retry period in milliseconds
      asyn-committing-retry-period = 1000
      \#schedule rollbacking retry period in milliseconds
      rollbacking-retry-period = 1000
      \#schedule timeout retry period in milliseconds
      timeout-retry-period = 1000
    }
    transaction {
      undo.data.validation = true
      undo.log.serialization = "jackson"
      undo.log.save.days = 7
      \#schedule delete expired undo_log in milliseconds
      undo.log.delete.period = 86400000
      undo.log.table = "undo_log"
    }
    ## metrics settings
    metrics {
      enabled = false
      registry-type = "compact"
      # multi exporters use comma divided
      exporter-list = "prometheus"
      exporter-prometheus-port = 9898
    }
    support {
      ## spring
      spring {
        # auto proxy the DataSource bean
        datasource.autoproxy = false
      }
    }
    ```
5. **registry.conf**

    ```JSON
    registry {
      \#🟡 file 、nacos 、eureka、redis、zk、consul、etcd3、sofa
      type = "nacos"
      nacos {
         ## 🟡
        serverAddr = "localhost:8848"
        namespace = ""
        cluster = "default"
      }
      eureka {
        serviceUrl = "http://localhost:8761/eureka"
        application = "default"
        weight = "1"
      }
      redis {
        serverAddr = "localhost:6379"
        db = "0"
      }
      zk {
        cluster = "default"
        serverAddr = "127.0.0.1:2181"
        session.timeout = 6000
        connect.timeout = 2000
      }
      consul {
        cluster = "default"
        serverAddr = "127.0.0.1:8500"
      }
      etcd3 {
        cluster = "default"
        serverAddr = "http://localhost:2379"
      }
      sofa {
        serverAddr = "127.0.0.1:9603"
        application = "default"
        region = "DEFAULT_ZONE"
        datacenter = "DefaultDataCenter"
        cluster = "default"
        group = "SEATA_GROUP"
        addressWaitTime = "3000"
      }
      file {
        name = "file.conf"
      }
    }
    config {
      # file、nacos 、apollo、zk、consul、etcd3
      type = "file"
      nacos {
        serverAddr = "localhost"
        namespace = ""
      }
      consul {
        serverAddr = "127.0.0.1:8500"
      }
      apollo {
        app.id = "seata-server"
        apollo.meta = "http://192.168.1.204:8801"
      }
      zk {
        serverAddr = "127.0.0.1:2181"
        session.timeout = 6000
        connect.timeout = 2000
      }
      etcd3 {
        serverAddr = "http://localhost:2379"
      }
      file {
        name = "file.conf"
      }
    }
    ```
6. **实体类**
    1. **CommonResult**

    ```Plain
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public class CommonResult<T> {
        private Integer code;
        private String  message;
        private T       data;
        public CommonResult(Integer code, String message) {
            this(code,message,null);
        }
    }
    ```
    2. **Order**

    ```Java
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public class Order {
        private Long id;
        private Long userId;
        private Long productId;
        private Integer count;
        private BigDecimal money;
        /**
         * 订单状态：0：创建中；1：已完结
         */
        private Integer status;
    }
    ```
7. **Dao（Mapper）**

    ```Java
    @Mapper
    public interface OrderDao {
        /**
         * 创建订单
         */
        void create(Order order);
        /**
         * 修改订单状态
         */
        void update(@Param("userId") Long userId, @Param("status") Integer status);
    }
    ```
8. **SQL 映射文件**

    ```XML
    <?xml version="1.0" encoding="UTF-8" ?>
    <!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd" >
    <mapper namespace="com.atguigu.springcloud.Dao.OrderDao">
        <resultM
    ap id="BaseResultMap" type="com.atguigu.springcloud.entity.Order">
            <id column="id" property="id" jdbcType="BIGINT"/>
            <result column="user_id" property="userId" jdbcType="BIGINT"/>
            <result column="product_id" property="productId" jdbcType="BIGINT"/>
            <result column="count" property="count" jdbcType="INTEGER"/>
            <result column="money" property="money" jdbcType="DECIMAL"/>
            <result column="status" property="status" jdbcType="INTEGER"/>
        </resultMap>
        <insert id="create">
            INSERT INTO `t_order` (`id`, `user_id`, `product_id`, `count`, `money`, `status`)
            VALUES (NULL, #{userId}, #{productId}, #{count}, #{money}, 0);
        </insert>
        <update id="update">
            UPDATE `t_order`
            SET status = 1
            WHERE user_id = #{userId} AND status = #{status};
        </update>
    </mapper>
    ```
9. **Service**
    1. **业务接口**

    ```Java
    public interface OrderService {
        /**
         * 创建订单
         */
        void create(Order order);
    }
    ```
    ```Java
    @Service
    @Slf4j
    public class OrderServiceImpl implements OrderService
    {
        @Resource
        private OrderDao orderDao;
        @Resource
        private StorageService storageService;
        @Resource
        private AccountService accountService;
        /**
         * 创建订单->调用库存服务扣减库存->调用账户服务扣减账户余额->修改订单状态
         * 简单说：
         * 下订单->减库存->减余额->改状态
         */
        @Override
        public void create(Order order) {
            log.info("------->下单开始");
            //本应用创建订单
            orderDao.create(order);
            //远程调用库存服务扣减库存
            log.info("------->order-service中扣减库存开始");
            storageService.decrease(order.getProductId(),order.getCount());
            log.info("------->order-service中扣减库存结束");
            //远程调用账户服务扣减余额
            log.info("------->order-service中扣减余额开始");
            accountService.decrease(order.getUserId(),order.getMoney());
            log.info("------->order-service中扣减余额结束");
            //修改订单状态为已完成
            log.info("------->order-service中修改订单状态开始");
            orderDao.update(order.getUserId(),0);
            log.info("------->order-service中修改订单状态结束");
            log.info("------->下单结束");
        }
    }
    ```
    2. **Feign 接口**

    ```Java
    @FeignClient(value = "seata-account-service")
    public interface AccountService {
        /**
         * 扣减账户余额
         */
        //@RequestMapping(value = "/account/decrease", method = RequestMethod.POST, produces = "application/json; charset=UTF-8")
        @PostMapping("/account/decrease")
        CommonResult decrease(@RequestParam("userId") Long userId, @RequestParam("money") BigDecimal money);
    }
    ```
    ```Java
    @FeignClient(value = "seata-storage-service")
    public interface StorageService {
        /**
         * 扣减库存
         */
        @PostMapping(value = "/storage/decrease")
        CommonResult decrease(@RequestParam("productId") Long productId, @RequestParam("count") Integer count);
    }
    ```
10. **Controller**

    ```Java
    @RestController
    public class OrderController {
        @Autowired
        private OrderService orderService;
        /**
         * 创建订单
         */
        @GetMapping("/order/create")
        public CommonResult create(Order order) {
            orderService.create(order);
            return new CommonResult(200, "订单创建成功!");
        }
    }
    ```
11. **配置类**
    - 注意这里的数据源配置是必须的！（第一次做的时候，以为这些都是无用的，直接让自动配置类配置不就好了，结果是大意了，**这里的 DataSourceProxy 是 Seata 数据源代理类**...）
    - 需要使用Seata 代理数据源 `import io.seata.rm.datasource.DataSourceProxy;`

    ![[IMG-20260405035440164.png|800]]

    - 否则 事务回滚会一直不生效！
    - 而且 MyBatisConfig 中 @MapperScan({"com.atguigu.springcloud.Dao"}) 也是必要的
    - 因为 我们又新加载了 一个SqlSessionFactory组件，这个会使系统扫描不到 Dao
    - （我看帖子说，甚至会使 MyBatis Plus 的乐观锁、分页插件都失效！[https://blog.csdn.net/qq_35721287/article/details/103282589](https://blog.csdn.net/qq_35721287/article/details/103282589)）

    ![[IMG-20260405035502865.png|800]]

    - 而不去新加载了 一个SqlSessionFactory组件，又会使 seata 的数据源代理失效
    - 所有需要对 mybatis 进行配置，让其能扫描到 Dao
    1. **MyBatisConfig**

    ```Java
    @Configuration
    @MapperScan({"com.atguigu.springcloud.Dao"})
    public class MyBatisConfig {
    }
    ```
    2. **DataSourceProxyConfig**

    ```Java
    @Configuration
    public class DataSourceProxyConfig {
        @Value("${mybatis.mapperLocations}")
        private String mapperLocations;
        @Bean
        @ConfigurationProperties(prefix = "spring.datasource")
        public DataSource druidDataSource(){
            return new DruidDataSource();
        }
        //⭐io.seata.rm.datasource.DataSourceProxy
        @Bean
        public DataSourceProxy dataSourceProxy(DataSource dataSource) {
            return new DataSourceProxy(dataSource);
        }
        @Bean
        public SqlSessionFactory sqlSessionFactoryBean(DataSourceProxy dataSourceProxy) throws Exception {
            SqlSessionFactoryBean sqlSessionFactoryBean = new SqlSessionFactoryBean();
            sqlSessionFactoryBean.setDataSource(dataSourceProxy);
            sqlSessionFactoryBean.setMapperLocations(new PathMatchingResourcePatternResolver().getResources(mapperLocations));
            sqlSessionFactoryBean.setTransactionFactory(new SpringManagedTransactionFactory());
            return sqlSessionFactoryBean.getObject();
        }
    }
    ```
12. **主启动类**

    ```Java
    @EnableDiscoveryClient
    @EnableFeignClients
    @SpringBootApplication(exclude = DataSourceAutoConfiguration.class)//⭐取消自动配置的数据源的自动创建seata代理数据源
    public class SeataOrderMainApp2001 {
        public static void main(String[] args) {
            SpringApplication.run(SeataOrderMainApp2001.class, args);
        }
    }
    ```
## 2. 库存微服务 2002
1. **新建Moudle：seata-order-service2002**
2. **pom.xml：同 2001**
3. **yaml 配置文件**

    ```YAML
    server:
      port: 2002
    spring:
      application:
        name: seata-storage-service
      cloud:
        alibaba:
          seata:
            tx-service-group: qhj_tx_group
        nacos:
          discovery:
            server-addr: localhost:8848
      datasource:
        driver-class-name: com.mysql.jdbc.Driver
        url: jdbc:mysql://localhost:3306/seata_storage
        username: root
        password: ZXT774276296qq..
    logging:
      level:
        io:
          seata: info
    mybatis:
      mapperLocations: classpath:mapper/*.xml
    ```
4. **file.conf：同 2001**
5. **registry.conf：同 2001**
6. **实体类**
    1. **CommonResult：同 2001**
    2. **Storage**

    ```Java
    package com.atguigu.springcloud.entity;
    import lombok.AllArgsConstructor;
    import lombok.Data;
    import lombok.NoArgsConstructor;
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public class Storage {
        private Long id;
        /**
         * 产品id
         */
        private Long productId;
        /**
         * 总库存
         */
        private Integer total;
        /**
         * 已用库存
         */
        private Integer used;
        /**
         * 剩余库存
         */
        private Integer residue;
    }
    ```
7. **Dao（Mapper）**

    ```Java
    @Mapper
    public interface StorageDao {
        /**
         * 扣减库存
         */
        void decrease(@Param("productId") Long productId, @Param("count") Integer count);
    }
    ```
8. **SQL 映射文件**

    ```XML
    <?xml version="1.0" encoding="UTF-8" ?>
    <!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd" >
    <mapper namespace="com.atguigu.springcloud.Dao.StorageDao">
        <resultMap id="BaseResultMap" type="com.atguigu.springcloud.entity.Storage">
            <id column="id" property="id" jdbcType="BIGINT"/>
            <result column="product_id" property="productId" jdbcType="BIGINT"/>
            <result column="total" property="total" jdbcType="INTEGER"/>
            <result column="used" property="used" jdbcType="INTEGER"/>
            <result column="residue" property="residue" jdbcType="INTEGER"/>
        </resultMap>
        <update id="decrease">
            UPDATE t_storage
            SET used    = used + #{count},
                residue = residue - #{count}
            WHERE product_id = #{productId}
        </update>
    </mapper>
    ```
9. **Service 业务接口**

    ```Java
    public interface StorageService {
        /**
         * 扣减库存
         */
        void decrease(Long productId, Integer count);
    }
    ```
    ```Java
    @Service
    @Slf4j
    public class StorageServiceImpl implements StorageService {
        @Resource
        private StorageDao storageDao;
        /**
         * 扣减库存
         */
        @Override
        public void decrease(Long productId, Integer count) {
            log.info("------->storage-service中扣减库存开始");
            storageDao.decrease(productId,count);
            log.info("------->storage-service中扣减库存结束");
        }
    }
    ```
10. **Controller**

    ```Java
    @RestController
    public class StorageController {
        @Autowired
        private StorageService storageService;
        /**
         * 扣减库存
         */
        @RequestMapping("/storage/decrease")
        public CommonResult decrease(Long productId, Integer count) {
            storageService.decrease(productId, count);
            return new CommonResult(200,"扣减库存成功！");
        }
    }
    ```
11. **配置类**
    1. **MyBatisConfig：同 2001**
    2. **DataSourceProxyConfig：同 2001**
12. **主启动类**

    ```Java
    @SpringBootApplication(exclude = DataSourceAutoConfiguration.class)
    @EnableDiscoveryClient
    @EnableFeignClients
    public class SeataStorageServiceApplication2002 {
        public static void main(String[] args) {
            SpringApplication.run(SeataStorageServiceApplication2002.class, args);
        }
    }
    ```
## 3. 账户微服务 2003
1. **新建Moudle：seata-order-service2003**
2. **pom.xml：同 2001**
3. **yaml 配置文件**

    ```YAML
    server:
      port: 2003
    spring:
      application:
        name: seata-account-service
      cloud:
        alibaba:
          seata:
            tx-service-group: qhj_tx_group
        nacos:
          discovery:
            server-addr: localhost:8848
      datasource:
        driver-class-name: com.mysql.jdbc.Driver
        url: jdbc:mysql://localhost:3306/seata_account
        username: root
        password: ZXT774276296qq..
    feign:
      hystrix:
        enabled: false
      client:
        config:
          default:
            connect-timeout: 30000
            read-timeout=300000: 30000
    logging:
      level:
        io:
          seata: info
    mybatis:
      mapperLocations: classpath:mapper/*.xml
    ```
4. **file.conf：同 2001**
5. **registry.conf：同 2001**
6. **实体类**
    1. **CommonResult：同 2001**
    2. **Account**

    ```Java
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public class Account {
        private Long id;
        /**
         * 用户id
         */
        private Long userId;
        /**
         * 总额度
         */
        private BigDecimal total;
        /**
         * 已用额度
         */
        private BigDecimal used;
        /**
         * 剩余额度
         */
        private BigDecimal residue;
    }
    ```
7. **Dao（Mapper）**

    ```Java
    @Mapper
    public interface AccountDao {
        /**
         * 扣减账户余额
         */
        void decrease(@Param("userId") Long userId, @Param("money") BigDecimal money);
    }
    ```
8. **SQL 映射文件**

    ```XML
    <?xml version="1.0" encoding="UTF-8" ?>
    <!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd" >
    <mapper namespace="com.atguigu.springcloud.Dao.AccountDao">
        <resultMap id="BaseResultMap" type="com.atguigu.springcloud.entity.Account">
            <id column="id" property="id" jdbcType="BIGINT"/>
            <result column="user_id" property="userId" jdbcType="BIGINT"/>
            <result column="total" property="total" jdbcType="DECIMAL"/>
            <result column="used" property="used" jdbcType="DECIMAL"/>
            <result column="residue" property="residue" jdbcType="DECIMAL"/>
        </resultMap>
        <update id="decrease">
            UPDATE t_account
            SET
                residue = residue - #{money},used = used + #{money}
            WHERE
                user_id = #{userId};
        </update>
    </mapper>
    ```
9. **Service：业务接口**

    ```Java
    public interface AccountService {
        /**
         * 扣减账户余额
         * @param userId 用户id
         * @param money 金额
         */
        void decrease(@RequestParam("userId") Long userId, @RequestParam("money") BigDecimal money);
    }
    ```
    ```Java
    package com.atguigu.springcloud.service.Impl;
    import com.atguigu.springcloud.Dao.AccountDao;
    import com.atguigu.springcloud.service.AccountService;
    import lombok.extern.slf4j.Slf4j;
    import org.springframework.stereotype.Service;
    import javax.annotation.Resource;
    import java.math.BigDecimal;
    import java.util.concurrent.TimeUnit;
    @Service
    @Slf4j
    public class AccountServiceImpl implements AccountService {
        @Resource
        AccountDao accountDao;
        /**
         * 扣减账户余额
         */
        @Override
        public void decrease(Long userId, BigDecimal money) {
            log.info("------->account-service中扣减账户余额开始");
            accountDao.decrease(userId, money);
            log.info("------->account-service中扣减账户余额结束");
        }
    }
    ```
10. **Controller**

    ```Java
    @RestController
    public class AccountController {
        @Resource
        AccountService accountService;
        /**
         * 扣减账户余额
         */
        @RequestMapping("/account/decrease")
        public CommonResult decrease(@RequestParam("userId") Long userId, @RequestParam("money") BigDecimal money){
            accountService.decrease(userId,money);
            return new CommonResult(200,"扣减账户余额成功！");
        }
    }
    ```
11. **配置类**
    1. **MyBatisConfig：同 2001**
    2. **DataSourceProxyConfig：同 2001**
12. **主启动类**

    ```Java
    @SpringBootApplication(exclude = DataSourceAutoConfiguration.class)
    @EnableDiscoveryClient
    @EnableFeignClients
    public class SeataAccountMainApp2003{
        public static void main(String[] args){
            SpringApplication.run(SeataAccountMainApp2003.class, args);
        }
    }
    ```
# 五、事务测试
## 1. 正常业务测试
1. 启动 Nacos、Seata、2001、2002、2003
2. Nacos 服务注册情况：

    ![[IMG-20260405035510260.png|800]]

3. 访问：[http://localhost:2001/order/create?userId=1&productId=1&count=10&money=100](http://localhost:2001/order/create?userId=1&productId=1&count=10&money=100)
4. 查看数据库：

    **插入了一条订单数据，库存和账户也都进行了相应的扣减，订单状态也从 0（未完成） 修改为 1（完成）**

![[IMG-20260405035518184.png|800]]

## 2. 模拟业务调用超时

在 2003 扣除账单余额中设置超时：

```Java
@Service
@Slf4j
public class AccountServiceImpl implements AccountService {
    @Resource
    AccountDao accountDao;
    /**
     * 扣减账户余额
     */
    @Override
    public void decrease(Long userId, BigDecimal money) {
        log.info("------->account-service中扣减账户余额开始");
        //⭐模拟超时异常，全局事务回滚
        //暂停几秒钟线程
        try {
            TimeUnit.SECONDS.sleep(30);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        accountDao.decrease(userId, money);
        log.info("------->account-service中扣减账户余额结束");
    }
}
```
## 3. 异常业务测试
1. 启动 Nacos、Seata、2001、2002、2003
2. 访问：[http://localhost:2001/order/create?userId=1&productId=1&count=10&money=100](http://localhost:2001/order/create?userId=1&productId=1&count=10&money=100)
3. 查看数据库：

    **库存行了相应的扣减，但是账户余额却没有扣！**

![[IMG-20260405035525755.png|506]]

## 4. 使用 Seata 处理 ⭐
- ==**在事务的发起者，也就是订单微服务的 OrderServiceImpl 中的**== `==**create()**==` ==**方法上添加**== ==**`@GlobalTransactional`**==
    ```Java
    @Service
    @Slf4j
    public class OrderServiceImpl implements OrderService
    {
        @Resource
        private OrderDao orderDao;
        @Resource
        private StorageService storageService;
        @Resource
        private AccountService accountService;
        /**
         * 创建订单->调用库存服务扣减库存->调用账户服务扣减账户余额->修改订单状态
         * 简单说：
         * 下订单->减库存->减余额->改状态
         */
        @Override
        //⭐@GlobalTransactional注解
        @GlobalTransactional(name = "qhj-create-order",rollbackFor = Exception.class) //这里name随便取名字
        public void create(Order order) {
            log.info("------->下单开始");
            //本应用创建订单
            orderDao.create(order);
            //远程调用库存服务扣减库存
            log.info("------->order-service中扣减库存开始");
            storageService.decrease(order.getProductId(),order.getCount());
            log.info("------->order-service中扣减库存结束");
            //远程调用账户服务扣减余额
            log.info("------->order-service中扣减余额开始");
            accountService.decrease(order.getUserId(),order.getMoney());
            log.info("------->order-service中扣减余额结束");
            //修改订单状态为已完成
            log.info("------->order-service中修改订单状态开始");
            orderDao.update(order.getUserId(),0);
            log.info("------->order-service中修改订单状态结束");
            log.info("------->下单结束");
        }
    }
    ```
## 5. 测试
1. 启动 Nacos、Seata、2001、2002、2003
2. 在 2001的业务类中的： 调用 扣除库存之后、扣除账户余额之前打断点
3. debug 运行 2001
4. 访问：[http://localhost:2001/order/create?userId=1&productId=1&count=10&money=100](http://localhost:2001/order/create?userId=1&productId=1&count=10&money=100)
5. 查看数据库：**订单创建语句、库存扣减语句已经执行**

    ![[IMG-20260405035531174.png|729]]

6. 放行断点，让开始执行账户余额扣减
7. 查看数据库：==**创建的订单、扣除的库存都恢复了！可见当 创建了订单和扣减了库存后，去扣除余额时，出现了超时异常，所有数据库都执行了回滚**==

    ![[IMG-20260405035532725.png|706]]
