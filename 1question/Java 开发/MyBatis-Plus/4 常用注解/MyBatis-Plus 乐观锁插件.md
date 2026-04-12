1. **修改实体类** ==**@Version**==
    
    ```Java
     @Data
     public class Product {
         private Long id;
         private String name;
         private Integer price;
    
         @Version
         private Integer version;
     }
    ```
    
1. **添加乐观锁插件配置：**==**MybatisPlusInterceptor**==
    
    ```Java
     @Bean
     public MybatisPlusInterceptor mybatisPlusInterceptor(){
         MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    
         //添加分页插件
         interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
    
         //添加乐观锁插件
         interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
    
         return interceptor;
     }
    ```
    
1. **测试**
    
    ```Java
     @Test
     public void testConcurrentUpdate() {
    
         //1、小李
         Product p1 = productMapper.selectById(1L);
         System.out.println("小李取出的价格：" + p1.getPrice());
    
         //2、小王
         Product p2 = productMapper.selectById(1L);
         System.out.println("小王取出的价格：" + p2.getPrice());
    
         //3、小李将价格加了50元，存入了数据库
         p1.setPrice(p1.getPrice() + 50);
         int result1 = productMapper.updateById(p1);
         System.out.println("小李修改结果：" + result1);
    
         //4、小王将商品减了30元，存入了数据库
         p2.setPrice(p2.getPrice() - 30);
         int result2 = productMapper.updateById(p2);
         System.out.println("小王修改结果：" + result2);
    
         //⭐增加一个失败重试的逻辑
         if(result2 == 0){
             //注意：每次操作更新前，都要重新获取当前 version，再进行操作
             p2 = productMapper.selectById(1L);
             p2.setPrice(p2.getPrice() - 30);
             result2 = productMapper.updateById(p2);
         }
    
         //老板最后的查询结果：120
         Product p3 = productMapper.selectById(1L);
         System.out.println("最后的结果：" + p3.getPrice());
     }
    ```