1. 基本语法：
    
    ```Bash
     read(选项)(参数)
    ```
    
1. 选项：
    
    1. p：指定读取值时的提示符
    
    1. t：指定读取值时等待的时间（秒），如果没有在指定的时间内输入，就不再等待了
    
1. 参数;
    
    变量-指定读取值得变量名
    
1. 应用实例：
    
    1. 案例1： 读取控制台输入一个num值
        
        ```Bash
         read -p "please input=" SUM1
         echo "input=$SUM1"
        ```
        
    
    1. 案例2： 读取控制台输入一个num值，在10秒内输入
        
        ```Bash
         read -t 10 -p "please input=" SUM1
         echo "input=$SUM1"
        ```