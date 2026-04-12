# 1. 介绍
管道流通常会被用在**不同的线程之间进行消息通讯**中使用
# 2. 代码示例
- 定义了一个子线程，该线程会往`PipedOutputStream`中写入数据，然后main线程会去`PipedInputStream`中读取子线程写入的数据
```Java
public static void main(String[] args) {
    try (PipedOutputStream out = new PipedOutputStream()) {
        PipedInputStream in = new PipedInputStream(out);
        new Thread(() -> {
            try {
                Thread.sleep(2000);
                String item = new String();
                for (int i=0;i<1000;i++){
                    item = item + "1";
                }
                out.write(item.getBytes(StandardCharsets.UTF_8));
                out.close();
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
        int receive = 0;
        System.out.println("try");
        byte[] temp = new byte[1024];
        //等待子线程往pipedOutputStream内部写入数据
        while ((receive = in.read(temp)) != -1) {
            String outStr = new String(temp,0,receive);
            System.out.println(outStr);
        }
    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

> [!important]
> 
>   
> 
> 1. `out`底层是用了一个字节缓冲数组`buffer`接收数据传输，当这个**字节缓冲数组满了之后**通过使用`notifyAll`唤醒`PipedInputStream in`内部读数据的线程
> 
> 1. 所以这里面的底层原理还是离不开`sync`和`notifyall`