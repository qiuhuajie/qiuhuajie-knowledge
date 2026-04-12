1. DistributeLock类
    
    ```Java
     public class DistributeLock {
         private final ZooKeeper zooKeeper;
         private  String connectString = "hadoop102:2181,hadoop103:2181,hadoop104:2181";
         private  int sessionTimeout = 2000;
     
         private CountDownLatch connectLatch1 = new CountDownLatch(1);
         private CountDownLatch connectLatch2 = new CountDownLatch(1);
         private String preNodePath;
         private String currentMode;
     
         public DistributeLock() throws IOException, InterruptedException, KeeperException {
             //获取连接
             zooKeeper = new ZooKeeper(connectString, sessionTimeout, new Watcher() {
                 @Override
                 public void process(WatchedEvent watchedEvent) {
                     //如果连接上了zookeeper集群，则释放connectLatch1
                     if(watchedEvent.getState() == Event.KeeperState.SyncConnected){
                         connectLatch1.countDown();
                     }
                     //如果前一个操作是删除节点操作，且删除的是当前的前一个节点，则释放connectLatch2
                     if(watchedEvent.getType() == Event.EventType.NodeDeleted && watchedEvent.getPath().equals(preNodePath)){
                         connectLatch2.countDown();
                     }
                 }
             });
     
             //等待zk正常连接后，往下走程序
             connectLatch1.await();
     
             //判断根节点/locks是否存在
             Stat stat = zooKeeper.exists("/locks", false);
             //如果不存在则创建根节点
             if(stat == null){
                 zooKeeper.create("/locks", "locks".getBytes(), ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
             }
         }
         //对zk加锁
         public void zklock() throws InterruptedException, KeeperException {
             //在对应目录下创建临时的带序号的节点
             currentMode = zooKeeper.create("/locks/" + "seq-", null, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);
             /*判断当前节点是不是序号最小的节点
             如果是：获取到锁
             如果不是：监听序号顺序前一个节点*/
             List<String> children = zooKeeper.getChildren("/locks", false);
             if(children.size() == 1){
                 return;
             }else {
                 //对集合排序
                 Collections.sort(children);
                 //获取节点名称
                 //Examples："unhappy".substring(2) returns "happy"
                 String thisNode = currentMode.substring("/locks/".length());
     
                 //获取当前节点的下标位置
                 int index = children.indexOf(thisNode);
                 if(index == -1){
                     System.out.println("数据异常");
                 }else if(index == 0){
                     //当前节点为第一，即序号最小，直接返回
                     return;
                 }else {
                     //获取当前节点的前一个节点路径
                     preNodePath = "/locks/"+children.get(index - 1);
                     //监听当前节点的前一个节点的数据变化
                     zooKeeper.getData(preNodePath,true,null);
     
                     //等待上述操作完成，才继续执行下面的语句
                     connectLatch2.await();
                     return;
                 }
             }
     
         }
         //解锁
         public void zkunlock() throws InterruptedException, KeeperException {
             //删除节点
             zooKeeper.delete(currentMode,-1);
         }
     }
    ```
    
1. DistributeLockTest测试类
    
    ```Java
     public class DistributedLockTest {
         public static void main(String[] args) throws IOException, InterruptedException, KeeperException {
             final DistributeLock lock1 = new DistributeLock();
             final DistributeLock lock2 = new DistributeLock();
     
             //创建两个线程
             new Thread(new Runnable() {
                 @Override
                 public void run() {
                     try {
                         lock1.zklock();
                         System.out.println("线程1获取锁");
                         //设置睡眠时间，保证第二个线程也起动，争抢锁
                         Thread.sleep(5*1000);
                         lock1.zkunlock();
                         System.out.println("线程1释放锁");
                     } catch (InterruptedException e) {
                         e.printStackTrace();
                     } catch (KeeperException e) {
                         e.printStackTrace();
                     }
     
                 }
             }).start();
     
             new Thread(new Runnable() {
                 @Override
                 public void run() {
                     try {
                         lock2.zklock();
                         System.out.println("线程2获取锁");
                         Thread.sleep(5*1000);
                         lock2.zkunlock();
                         System.out.println("线程2释放锁");
                     } catch (InterruptedException e) {
                         e.printStackTrace();
                     } catch (KeeperException e) {
                         e.printStackTrace();
                     }
     
                 }
             }).start();
         }
     }
    ```
    
1. 测试结果：
    
    ![[Attachment/1question/中间件/ZooKeeper/实践案例/分布式锁/IMG-20260405035438372.png|Untitled 449.png]]