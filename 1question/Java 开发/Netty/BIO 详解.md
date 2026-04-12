- [[#1. Java BIO 工作机制]]
- [[#2. Java BIO 应用实例]]
    - [[#2.1 实例说明]]
    - [[#2.2 代码示例]]
    - [[#2.3 测试]]
# 1. Java BIO 工作机制

![[IMG-20260404031809621.png|Untitled 81.png]]

1. 流程
    
    1. 服务器端启动一个 `ServerSocket`
    
    1. 客户端启动 `Socket` 对服务器进行通信，默认情况下服务器端需要对每个客户建立一个线程与之通讯
    
    1. 客户端发出请求后，先咨询服务器是否有线程响应
        
        1. 如果没有则会等待，或者被拒绝
        
        1. 如果有响应，客户端线程会等待请求结束后，再继续执行
        
    
1. 服务器实现模式为**客户端有一个连接请求时服务器端就需要启动一个线程进行处理**
1. **线程在 BIO 中在连接请求和处理数据时，都会产阻塞**
    
    1. 连接请求：`Socket socket = serverSocket.accept();` 会产生阻塞，服务端线程接收到一个客户端连接后才能继续运行
    
    1. 读写数据：`inputStream.read(readData)` 也会产生阻塞，如果是单线程，则线程挂起，那么只能处理极少数连接
    
1. 所以**为了让程序能支持多个客户端，不得不使用多线程**
    
    ```Java
    threadPool.execute(new Runnable() {
        @Override
        public void run() {
            handler(socket);
        }
    });
    ```
    
# 2. Java BIO 应用实例
## 2.1 实例说明
1. 使用 BIO 模型编写一个服务器端，监听 `6666` 端口，当有客户端连接时，就启动一个线程与之通讯
1. 要求使用线程池机制改善，可以连接多个客户端
1. 服务器端可以接收客户端发送的数据（`telnet` 方式即可）
## 2.2 代码示例
1. `BIOServer`
    
    ```Java
    public class BIOServer {
        public static void main(String[] args) throws IOException {
            ExecutorService threadPool = Executors.newFixedThreadPool(10);
    
            ServerSocket serverSocket = new ServerSocket(6666);
            System.out.println("服务器启动，监听6666端口");
    
            while (true) {
                System.out.println("线程 id = " + Thread.currentThread().getId() + "，线程 name = " + Thread.currentThread().getName());
                System.out.println("服务器正在等待连接...");
                Socket socket = serverSocket.accept();
                System.out.println("有的新的连接建立");
                threadPool.execute(new Runnable() {
                    @Override
                    public void run() {
                        handler(socket);
                    }
                });
            }
        }
    
        private static void handler(Socket socket) {
            try {
                System.out.println("线程 id = " + Thread.currentThread().getId() + "，线程 name = " + Thread.currentThread().getName());
                byte[] readData = new byte[1024];
                int bufferSize = 0;
                InputStream inputStream = socket.getInputStream();
                while (true) {
                    System.out.println("线程正在等待读数据...");
                    if ((bufferSize = inputStream.read(readData)) != -1){
                        System.out.println(new String(readData, 0, bufferSize));
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            } finally {
                try {
                    socket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
    ```
    
## 2.3 测试
1. 启动**服务端**：此时主线程启动，创建了一个 `ServerSocket` ，监听 `6666` 端口
    

    ![[IMG-20260404031809695.png|Untitled 1 49.png]]

    
1. 此时，在命令端使用 `telnet` 建立一个连接（模拟**第一个客户端**）
    
    ```Java
    C:\Users\lenovo>telnet 127.0.0.1 6666
    // 连接后按 ctrl + ]
    ```
    

    ![[IMG-20260404031809768.png|Untitled 2 38.png]]

    

    此时的服务端控制台输出：

    

    ![[IMG-20260405035425996.png|Untitled 3 31.png]]

    
    > [!important]
    > 
    > - **此时`main`主线程在监听到有新连接时，会起一个新的线程`pool-1-thread-1`，让这个新线程去处理连接**
    > 
    > - **而`main`主线程自己由于有** `**while**` **循环，会接着返回去，继续等待新的连接请求到来**==**（此时线程**== `==**main**==` ==**处于阻塞状态）**==
    > 
    > - **新起的线程`pool-1-thread-1`，进入处理连接的代码逻辑，会一直等待接受客户端发来的数据**==**（此时线程**====**`pool-1-thread-1`**== ==**处于阻塞状态）**==
    
1. 此时在客户端发一个信息
    
    ```Java
    send hello
    ```
    

    ![[IMG-20260405035439239.png|Untitled 4 26.png]]

    

    此时的服务端控制台输出：

    

    ![[IMG-20260405035501485.png|Untitled 5 24.png]]

    
    > [!important]
    > 
    > - **服务端线程`pool-1-thread-1`将客户端发来的数据打印出来后，还会一直监听着连接，等待有新的数据传过来**==**（此时线程**==`==**pool-1-thread-1**==`==**又处于阻塞状态了）**==
    
1. 此时，再在命令端使用 `telnet` 建立新的一个连接（模拟**第二个客户端**）
    
    ```Java
    C:\Users\lenovo>telnet 127.0.0.1 6666
    ```
    

    此时的服务端控制台输出：

    

    ![[IMG-20260405035503319.png|Untitled 6 21.png]]

    
    > [!important]
    > 
    > - **可以看到服务器 `main` 线程为第二个客户端连接，又起了一个新的线程 `pool-1-thread-2` ， 而 `main` 线程自己又重新回去监听新的连接**==**（此时线程**== `==**main**==` ==**处于阻塞状态）**==
    > 
    > - **新起的线程 `pool-1-thread-2` 进入处理连接的代码逻辑，会一直等待接受客户端发来的数据**==**（此时线程**====`**pool-1-thread-2**`== ==**处于阻塞状态）**==