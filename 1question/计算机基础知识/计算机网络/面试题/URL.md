# URL
1. URI
    1. 是一个抽象的定义，不管用什么方法表示，只要能定位一个资源，就叫 URI
    2. 使用两种方法定位资源：
        - URL：用地址定位
        - URN：用名字定位
2. **URL（Uniform Resource Locator）**
    1. ==**统一资源定位符**==，它表示 Internet 上某一资源的地址
    2. 可以用来标识一个资源，而且还指明了如何 locate 这个资源
3. URL的基本结构由5部分组成：

    ```Plain
     <传输协议>://<主机名>:<端口号>/<文件名>\#片段名?参数列表
     如:
     http://localhost:8080/examples/123.png?username=Tom&password=123
     协议     主机名   端口号    资源地址       参数
    ```
4. Java 使用示例：

    ```Java
     URL url = new URL("http://localhost:8080/examples/123.png?username=Tom&password=123");
     url.getProtocol();//获取该URL的协议名
     url.getHost();//获取该URL的主机名
     url.getPort();//获取该URL的端口号
     url.getFile();//获取该URL的文件名
     url.getQuery();//获取该URL的查询码
    ```