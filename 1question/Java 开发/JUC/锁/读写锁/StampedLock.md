# StampedLock
1. StampedLock 自 JDK 8 加入，也是一种读写锁
    
    1. **提供了一种**==**优化的读写锁**==**实现**
    
    1. **它支持**==**乐观读**==**和**==**悲观读**==**，并且在使用上也比 ReentrantReadWriteLock 更加灵活**
    
1. 它的特点是在使用读锁、写锁时都必须配合【戳】使用
1. 加解读锁
    
    ```Java
    long stamp = lock.readLock();
    lock.unlockRead(stamp);
    ```
    
1. 加解写锁
    
    ```Java
    long stamp = lock.writeLock();
    lock.unlockWrite(stamp);
    ```
    
1. 乐观读，StampedLock 支持 tryOptimisticRead() 方法（乐观读）
    
    1. 读取完毕后需要做一次 戳校验
    
    1. 如果校验通过，表示这期间确实没有写操作，数据可以安全使用
    
    1. 如果校验没通过，需要重新获取读锁，保证数据安全
    
    ```Java
    long stamp = lock.tryOptimisticRead();
    // 验戳
    if(!lock.validate(stamp)){
    		// 锁升级
    }
    ```