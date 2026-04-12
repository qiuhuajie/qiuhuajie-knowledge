- [[#1. 流程描述]]
- [[#2. 代码示例]]
    - [[#2.1 服务端的处理流程]]
    - [[#2.2 客户端给服务器发送消息]]
# 1. 流程描述
1. **服务器端流程：**

    1. 加载套接字库

    2. 创建套接字 (`socket`)

    3. 将套接字绑定到一个本地地址和端口上 (**`bind`**)

    4. 将套接字设为监听模式，准备接收客户请求 (**`listen`**)

    5. 等待客户请求到来;当请求到来后，接受连接请求，返回一个新的对应于此次连接的套接字(**`accept`**)

    6. 用返回的套接字和客户端进行通信 (`send/recv`)

    7. 返回，等待另一客户请求

    8. 关闭套接字

2. **客户端流程：**

    1. 加载套接字库

    2. 创建套接字 (`socket`)

    3. 向服务器发出连接请求 (**`connect`**)

    4. 和服务器端进行通信 (`send/recv`)

    5. 关闭套接字

# 2. 代码示例
## 2.1 服务端的处理流程

包括监听端口、接受连接请求、读取数据的代码案例，可以参考 Netty BIO 中的例子[[BIO 详解]]

## 2.2 客户端给服务器发送消息

![[IMG-20260315141441602.png|Untitled 165.png]]

1. 服务端

    ```Java
    @Test
    public void server(){
        ServerSocket serverSocket = null;
        Socket socket = null;
        InputStream is = null;
        ByteArrayOutputStream baos = null;
        try {
            
            //1.创建服务器端的socke：ServerSocket
            serverSocket = new ServerSocket(8899);
            
            //2.调用acept()表示接受来自于客户端的socket
            socket = serverSocket.accept();
            
            //3.获取输入流
            is = socket.getInputStream();
    
            //4.读取输入流中的数据
            baos = new ByteArrayOutputStream();
            byte[] bytes = new byte[5];
            int len;
            while ((len = is.read(bytes)) != -1 ){
                baos.write(bytes,0,len);
            }
            String s = baos.toString();
            System.out.println(s);
            System.out.println("来自于"+socket.getInetAddress().getHostName()+"的消息");
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if(baos != null)
                    baos.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
            try {
                if(is != null)
                    is.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
            try {
                if(socket != null)
                    socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
            try {
                if(serverSocket != null)
                    serverSocket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    ```

2. 客户端

    ```Java
    @Test
    public void client(){
    
        Socket socket = null;
        OutputStream os = null;
        try {
            
            //1.创建socke对象，指明服务器端的ip和端口号
            InetAddress inetAddress = InetAddress.getByName("192.168.110.150");
            socket = new Socket(inetAddress,8899);
            
            //2.获取一个输出流，用于输出数据
            os = socket.getOutputStream();
            
            //3.写出数据
            os.write("你好".getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                os.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
    
            try {
                socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    ```