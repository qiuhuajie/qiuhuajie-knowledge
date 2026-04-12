- `File` 类对象可以是**文件**，也可以是**目录**
# 1. **构造器**
1. `public File(String pathname)`以pathname为路径创建File对象，可以是绝对路径或者相对路径，如果pathname是相对路径，则默认的当前路径在**系统属性**`user.dir`中存储
    
    ```Java
     File file = new File("hello.txt");
    ```
    
    > [!important] 注意：如果创建文件或者文件目录没有写盘符路径， 那么默认在项目路径下
    
1. `public File(String parent,String child)`以parent为父路径， child为子路径创建File对象
    
    ```Java
     File file1 = new File("E:", "aaa");
    ```
    
1. `public File(File parent,String child)`根据一个父File对象和子文件路径创建File对象
    
    ```Java
     File file2 = new File(file, "bbb.txt");
    ```
    

> [!important] **注意：此时都没有考虑在硬盘中真实存在这些文件，只是生成内存层面的对象而已**
# 2. **路径分隔符**
1. 路径中的每级目录之间用一个路径分隔符隔开
1. 存在的问题：
    
    1. 路径分隔符和系统有关：
        
        1. windows 和 DOS 系统默认使用 “`\`” 来表示
        
        1. UNIX 和 URL 使用 “`/`” 来表示
        
        1. Java 程序支持跨平台运行，因此路径分隔符要慎用
        
    
1. 解决方法：
    
    1. 为了解决这个隐患， File类提供了一个常量 **`public static final String separator`**
    
    1. **`File.separator` 会根据操作系统，动态的提供分隔符**
    
    ```Java
     File file = new File("hello.txt");//相对路径
    
     File file1 = new File("E:\\1_课件\\dbcp.txt");//绝对路径 windows
    
     File file2 = new File("E:/1_课件/dbcp.txt");//Unix和URL
    
     File file3 = new File("E:"+File.separator+"1_课件"+File.separator+"dbcp.txt"); //⭐通用
    ```
    
# 3. **常用方法：**

> [!important]
> 
> 1. **并未涉及到写入或者读取文件内容的操作，这些操作需要使用 IO 流来完成**
> 
> 1. **后续**`**File**`**类的对象会作为参数传递到**==**流的构造器**==**中，指明读取或写入的”终点“**
## 3.1 File类的获取功能
1. `String getAbsolutePath()`： 获取绝对路径
1. `String getPath()`： 获取路径
1. `String getName()`： 获取名称
1. `String getParent()`： 获取上层文件目录路径，若无，返回null
1. `long length()`： 获取文件长度（即：字节数），不能获取目录的长度。
1. `long lastModified()`： 获取最后一次的修改时间， 毫秒值
1. `String[] list()`： 获取指定目录下的所有文件或者文件目录的**名称数组**
    
    ```Java
     File file = new File("D:\\DriverGenius");
     String[] list = file.list();
     
     for (String s:list
          ) {
         System.out.println(s);
     }
     //kadblock kcdpt kplanet ksoft log
    ```
    
1. `File[] listFiles()`： 获取指定目录下的所有文件或者文件目录的**File数组**
    
    ```Java
     File file = new File("D:\\DriverGenius");
     File[] files = file.listFiles();
     
     for (File f:files
          ) {
         System.out.println(f);
     }
     //D:\DriverGenius\kcdpt
     //D:\DriverGenius\kplanet
     //D:\DriverGenius\ksoft
    ```
    
## 3.2 File类的重命名功能
1. `boolean renameTo(File dest)`：把文件重命名为指定的文件路径，file1移动到file2指定位置，且改名为指定名
    
    ```Java
     File file1 = new File("D:\\hi.txt");
     File file2 = new File("D:\\hh.txt");
     boolean b = file1.renameTo(file2);
    ```
    
    要想返回true，需要file1一定是存在的，且file2不能存在（执行完file1会消失，如果再执行一次，会返回false）
    
## 3.3 File类的判断功能
1. `boolean isDirectory()`： 判断是否是文件目录
1. `boolean isFile()` ： 判断是否是文件
1. `boolean exists()` ： 判断是否存在
1. `boolean canRead()` ： 判断是否可读
1. `boolean canWrite()`： 判断是否可写
1. `boolean isHidden()` ： 判断是否隐藏
## 3.4 File类的创建功能
1. `boolean createNewFile()`： 创建文件。 若文件存在， 则不创建， 返回false
1. `boolean mkdir()`： 创建文件目录。 如果此文件目录存在， 就不创建了；如果此文件目录的上层目录不存在， 也不创建
1. `boolean mkdirs()` ： 创建文件目录。 如果**输入路径中上层文件目录不存在， 一并创建**
## 3.5 File类的删除功能
1. `boolean delete()`： 删除文件或者文件夹
    
    > [!important] 删除注意事项：
    > 
    > 1. Java中的删除不走回收站
    > 
    > 1. 要删除一个文件目录， 该文件目录内不能包含文件或者文件目录（空才能删）