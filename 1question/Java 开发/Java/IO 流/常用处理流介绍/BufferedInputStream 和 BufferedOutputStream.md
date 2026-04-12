# 1. 介绍
1. 这类流在传统的字节流基础上做了一层包装，单纯的字节节点流每次处理数据读取或者写入的时候都是直接对磁盘进行字节为单位的io操作，所以性能方面会有一定的缺陷
1. 缓冲字节流的出现就是通过引入一个缓冲 **`Buffer`** 的来**优化这种多次读写操作导致的io性能不足的设计**
1. 缓存区的工作原理：
    
    1. 缓冲字节处理流的内部存在一个叫做 `buffer` 的缓冲区，每次写入数据的时候都会往缓冲区中写入数据，当缓冲区积攒了足够多的数据后再一次性写回到数据源中
        
        ```Java
        public class BufferedInputStream extends FilterInputStream {
        
            private static int DEFAULT_BUFFER_SIZE = 8192;   // 8k
            ...
            public BufferedInputStream(InputStream in) {
                this(in, DEFAULT_BUFFER_SIZE);
            }
        		...
        }
        ```
        
    
    1. 这种设计思路相比原先的一次写一次io要高效更多，由于 buffer 在内存中，而从内存中读取要比从磁盘中读取效率高
        
        ![[Attachment/1question/大数据/Java 开发/Java/IO 流/常用处理流介绍/IMG-20260405035413932.png|Untitled 454.png]]
        
    
1. `BufferedInputStream`和`BufferedOutputStream`内部采用了修饰器模式，通过构造函数注入一个`java.io.InputStream/java.io.OutputStream`对象，从而达到可以注入多种字节输入输出流
# 2. 代码示例
## 2.1 基于字节为单位实现文件拷贝
```Java
public static void fileCopyByByte(String sourceFile, String destPath){
    BufferedInputStream bufferedInputStream = null;
    BufferedOutputStream bufferedOutputStream = null;
    try {
        bufferedInputStream = new BufferedInputStream(new FileInputStream(sourceFile));   // 处理流就套接在已有流上
        bufferedOutputStream = new BufferedOutputStream(new FileOutputStream(destPath));
        byte[] tempByte = new byte[1024];
        int tempByteLen = 0;
        while ((tempByteLen = bufferedInputStream.read(tempByte)) != -1) {
            bufferedOutputStream.write(tempByte,0,tempByteLen);
        }
    } catch (IOException e) {
        e.printStackTrace();
    } finally {
        //外层流关闭时，内层流也会自动进行关闭，故可以省略关闭内层
        try {
            bufferedInputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            bufferedOutputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

> [!important] 注意：
> 
> - 当关闭流的时候只需要关闭外界包装的字节缓冲流即可，它的`close`操作会触发对应的字节流内部的`close`函数
> 
> - 使用缓冲处理流的时候要记得调用`close`或者`flush`操作才能将实际数据真正写入到磁盘当中
## 2.2 **文本文件**的复制操作
```Java
public static void fileCopyByByte(String sourceFile, String destPath){
    BufferedReader bufferedReader = null;
    BufferedWriter bufferedWriter = null;
    try {
        bufferedReader = new BufferedReader(new FileReader(sourceFile));
        bufferedWriter = new BufferedWriter(new FileWriter(destPath));
        String data;
        while ((data = bufferedReader.readLine()) != null){
            bufferedWriter.write(data);
            bufferedWriter.newLine();    // 一行一行读
        }
    } catch (IOException e) {
        e.printStackTrace();
    } finally {
        //外层流关闭时，内层流也会自动进行关闭，故可以省略关闭内层
        try {
            bufferedReader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            bufferedWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```
## 2.3 实现图片的加密：(解密同理)
```Java
byte[] bytes = new byte[1024];
int read;
while ((read = bufferedInputStream.read(bytes)) != -1 ){
    for (int i = 0; i < read; i++) {
        bytes[i] = (byte) (bytes[i]^5);
    }
    bufferedOutputStream.write(bytes,0,read);
}
```