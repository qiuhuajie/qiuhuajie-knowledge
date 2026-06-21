---
title: "模拟Redis 客户端"
tags:
  - "中间件"
  - "中间件/Redis"
  - "中间件/Redis/Redis 原理"
  - "模拟Redis 客户端"
  - "通信协议"
  - "Redis"
updated: 2026-04-16
---

# 一、模拟Redis 客户端
> 💡 Redis支持TCP通信，因此我们可以使用Socket来模拟客户端，与Redis服务端建立连接：
> 例如：
> 1. 要模拟客户端给服务端发送一个命令：`set name coolcoolcool`
> 2. 则需要客户端根据`RESP`协议发送以下一串字符
> ![[IMG-20260620224127707.png|248]]
> 3. 且服务端会返回`OK`，因此也需要在客户端把服务端的返回信息也解析后，打印在控制台
```Java
public class main {
    static Socket socket;
    static PrintWriter writer;
    static BufferedReader reader;
    public static void main(String[] args) {
        //1. 定义连接参数
        String host = "192.168.10.151";
        int port = 6379;
        Object obj;
        try {
            //2. 建立TCP连接
            socket = new Socket(host,port);
            //3. 获取输入流
            writer = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
            //4. 获取输出流
            reader = new BufferedReader(new InputStreamReader(socket.getInputStream(),StandardCharsets.UTF_8));
            //5.1 获取授权 auth 111111
            sendRequest("auth","111111");
            //5.2 接收响应
            obj = handleResponse();
            System.out.println("obj = " + obj);
            //6.1 发送请求 set name coolcoolcool
            sendRequest("set","name","coolcoolcool");
            //6.2 接收响应
            obj = handleResponse();
            System.out.println("obj = " + obj);
            //7.1 发送请求 get name
            sendRequest("get","name");
            //7.2 接收响应
            obj = handleResponse();
            System.out.println("obj = " + obj);
        } catch (IOException e) {
            e.printStackTrace();
        }finally {
            //8.1 释放连接
            try {
                socket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
            //8.2 关闭输入流
            try {
                writer.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
            //8.3 关闭输出流
            try {
                reader.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    //⭐发送请求
    private static void sendRequest(String ...args) {	//接受多个字符串参数，拼接到数组里
        //写入命令的数组长度
        writer.println("*" + args.length);
        for (String arg : args) {
            //设置字节数，注意：字节数 != 字符数
            writer.println("$" + arg.getBytes(StandardCharsets.UTF_8).length);
            writer.println(arg);
        }
        writer.flush();
    }
    //⭐解析响应
    private static Object handleResponse() throws IOException {
        //1. 读取首字节
        int prefix = reader.read();     //读了之后就直接读走了
        //2. 判断数据类型标示
        switch (prefix){
            case '+' :  //单行字符串，直接读一行
                return reader.readLine();
            case '-' :  //异常，也读一行
                throw new RuntimeException(reader.readLine());
            case ':' :  //数字
                return Integer.parseInt(reader.readLine());
            case '$' :  //多行字符串
                //先读长度
                int len = Integer.parseInt(reader.readLine());
                if (len == -1) {
                    return null;
                }
                if (len == 0) {
                    return "";
                }
                //再读数据，读取len个字节，假设没有特殊字符，所以直接读取一行（简化）
                return reader.readLine();
            case '*' :  //数组
                return readBulkString();
            default:
                throw new RuntimeException("错误的数据格式！");
        }
    }
    //解析数组形式的返回信息
    private static Object readBulkString() throws IOException {
        //获取数组的大小
        int len = Integer.parseInt(reader.readLine());
        if (len <= 0) {
            return null;
        }
        // 定义集合，接受多个元素
        ArrayList<Object> list = new ArrayList<>();
        //遍历，依次获取数组中的每个元素
        for (int i = 0; i < len; i++) {
            //由于数组中的元素可能是其他四种类型的任意类型，故直接调用handleResponse即可
            list.add(handleResponse());
        }
        return list;
    }
}
```

执行结果：

![[IMG-20260620224129423.png|627]]

![[IMG-20260620224135280.png|800]]
