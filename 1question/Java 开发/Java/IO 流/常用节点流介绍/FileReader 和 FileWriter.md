# 1. 介绍
1. **`FileReader`**字符流**支持每次读取文件的时候按照**`char`**为基本单位进行读取**
    
    1. 这款 io 流非常适合用于读取一些小的文本内容
    
    1. 同样的，==`FileReader`====的====`read`====函数在调用完之后会返回读取到的文本内容长度，如果长度为====`-1`====，则表示读取到的内容已经结束==
    
1. **`FileWriter`**是一款基于字符为基本单位的输出流，可以用于往文本文件内部写入一定的数据
# 2. 代码示例
## 2.1 **FileReader**
```Java
public static void readFile(){
    FileReader fileReader = null;
    try {
        fileReader = new FileReader("C:/Users/lenovo/Desktop/25inputs.txt");
				// 一次性读入5个字符
        char[] chars = new char[3];
        int readLen = 0;
        while ((readLen = fileReader.read(chars))!=-1){
            System.out.println(new String(chars, 0, readLen));
        }
    } catch (Exception e) {
        e.printStackTrace();
    } finally {
        try {
            fileReader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```
## 2.2 **FileWriter**
```Java
public static void writeFileVersion1(){
    FileWriter fileWriter = null;
    try {
        //默认是覆盖模式
//      fileWriter = new FileWriter("C:/Users/lenovo/Desktop/25inputs.txt");
        fileWriter = new FileWriter("C:/Users/lenovo/Desktop/25inputs.txt",true);
        fileWriter.write("this is test\n");
    } catch (Exception e) {
        e.printStackTrace();
    } finally {
        try {
            // 底层使用了sun.nio.cs.StreamEncoder.writeBytes，
            // 底层其实是使用了Nio 的 bytebuffer做数据实际刷盘操作
            // 所以其实底层还是使用了byte作为基本单位来进行操作
            fileWriter.close();
            //flush也会写入数据，但是没有执行close操作
//                fileWriter.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

> [!important] 注意：
> 
> - 使用流结束之后记得要手动调用close函数，执行关闭行为操作
> 
> - 使用完毕后如果不执行`close`操作或者`flush`操作则并不会将实际的内容持久化输出到磁盘当中。这一点和`FileOutputStream`很不一样
> 
> - 在使用`FileWriter`的构造函数中，有一个`append`的布尔类型变量，用于声明当前的数据写入之后是否会覆盖原先的内容
>     
>     ![[IMG-20260405035413935.png|Untitled 453.png]]
>     
## 2.3 **实现文本文件复制操作**
- 文本文件（.txt、.java、.c、.cpp）只能使用字符流操作，因为如果有中文的话，字节数组中放不下中文编码
- 如果**使用字节流处理文本文件，仅限于复制文件的操作（不会在内存中转换显示）**
```Java
public static void copy(){
    FileReader fileReader = null;
    FileWriter fileWriter = null;
    try {
        File file1 = new File("D:\\hh.txt");
        File file2 = new File("D:\\h2.txt");
        fileReader = new FileReader(file1);
        fileWriter = new FileWriter(file2);
        char[] charsBuffer = new char[5];
        int read;
        while ((read = fileReader.read(charsBuffer)) != -1){
            fileWriter.write(charsBuffer,0,read);
        }
    } catch (IOException e) {
        e.printStackTrace();
    }
    finally {
        try {
            if(fileReader != null)
                fileReader.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            if(fileWriter != null)
                fileWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```