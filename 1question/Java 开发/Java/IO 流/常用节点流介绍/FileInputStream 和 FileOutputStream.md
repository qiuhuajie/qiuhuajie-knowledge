# 1. 介绍
1. 通常**`FileInputStream`**流会用于以字节的方式去读取文件信息
1. `**FileOutputStream**` 是文件的字节输出流
# 2. 代码示例
## 2.1 **FileInputStream**
```Java
public static void readFile() {
    FileInputStream fileInputStream = null;
    try {
        fileInputStream = new FileInputStream(new File("C:/Users/lenovo/Desktop/25inputs.txt"));
        byte[] readData = new byte[10];
        int bufferSize = 0;
        //如果读取正常，会返回实际读取的字节数
        while ((bufferSize = fileInputStream.read(readData)) != -1){
            System.out.print(new String(readData,0,bufferSize));
        }
        System.out.println();
    }catch (Exception e){
        e.printStackTrace();
    } finally {
        //关闭文件流，释放资源
        try {
            //这个异常只要保证的确执行了close操作即可
            fileInputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

> [!important] 注意：
> 
> - 流需要进行关闭操作
> 
> - 使用`read`函数的时候，当文件读取正常时候会返回实际的字节数
## 2.2 **FileOutputStream**
```Java
public static void writeFileVersion1() {
    String filePath = "C:/Users/lenovo/Desktop/25inputs.txt";
    FileOutputStream fileOutputStream = null;
    try {
        // 如果通过new FileOutputStream(filePath)的方式执行写入，实际上数据是会覆盖原先的内容,所以根据构造函数的第二参数来实现追加的效果
        fileOutputStream = new FileOutputStream(filePath, true);
        fileOutputStream.write("input sth".getBytes());
        fileOutputStream.write("input sth2".getBytes());
    }catch (Exception e){
        e.printStackTrace();
    } finally {
        try {
            fileOutputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

> [!important] 注意：
> 
> - 注意在`FileOutputStream`的构造函数中，可以通过定义第二个`append`参数去设置写入的模式（覆盖模式还是追加模式）
> 
> - 使用字符输入流的时候，即使没有走到`close`函数，数据也会被持久化写入到磁盘
## 2.3 **实现复制图片的操作**
- 图片是**字节**文件，不能使用`FileReader`和`FileWriter`操作，要使用字节流`fileInputStream`和`fileOutputStream`
- 且`charsBuffer`数组要是字节类型的（`byte [ ]`）
```Java
public static void copy(){
    FileInputStream fileInputStream = null;
    FileOutputStream fileOutputStream = null;
    try {
        File file1 = new File("D:\\123.png");
        File file2 = new File("D:\\111.png");
        fileInputStream = new FileInputStream(file1);
        fileOutputStream = new FileOutputStream(file2);
        byte[] charsBuffer = new byte[1024];
        //缓存数组大小通常写为1024
        int read;
        while ((read = fileInputStream.read(charsBuffer)) != -1){
            fileOutputStream.write(charsBuffer,0,read);
        }
    } catch (IOException e) {
        e.printStackTrace();
    } finally {
        try {
            if(fileInputStream != null)
                fileInputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            if(fileOutputStream != null)
                fileOutputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```