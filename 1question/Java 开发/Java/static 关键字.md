---
title: "static 关键字"
tags:
  - "static_关键字"
  - "方法区"
  - "JVM"
  - "堆内存"
  - "US"
  - "Java基础"
updated: 2026-04-16
---

# 一、为什么需要
1. 当我们编写一个类时，其实就是在描述其对象的属性和行为，而并没有产生实质上的对象
2. 只有通过 `new` 关键字才会产生出对象，这时系统才会分配内存空间给对象，其方法才可以供外部调用
3. ==有时候希望==**==无论是否产生了对象==**==或==**==无论产生了多少对象==**==的情况下，====**某些特定的数据在内存空间里只有一份**==
    1. 例如所有的中国人都有个国家名称，**每一个中国人都共享这个国家名称**
    2. **不必在每一个中国人的实例对象中都单独分配一个用于代表国家名称的变量**

    ![[IMG-20260620222522643.png|418]]

# 二、static 介绍
- static 可以用来修饰：属性、方法、代码块、内部类
## 1. static 修饰属性（静态变量）
1. ==静态变量== ==**随着类**== ==的加载而加载==，因此静态变量加载**早于对象的创建**
2. 可以在没有对象的情况下，就使用类去调用：`Person.nation = "US";`
3. 由于**类只会加载一次，所以静态变量只会在内存中保存一份，**==**存在方法区的⭐静态域中**==[[类的生命周期]][[类的生命周期]][[类的生命周期]]
    1. 即使==创建了类的多个对象，每一个对象====**共享有同一个静态变量**==，当通过某一个对象修改静态变量时，会导致其他对象调用静态变量时也会变为修改过的值

    ![[IMG-20260620222522691.png|499]]

    2. 如果是非静态变量：如果创建了类的多个对象，每个对象都**独立拥有一套类中的非静态属性**，当修改一个对象的非静态属性时，不会改变其他对象的属性值
4. **`static`** ==**变量的赋值**==[[类的生命周期]]
5. **静态变量的内存图示：**

    ![[IMG-20260620222522753.png|564]]

## 2. static 修饰方法（静态方法）
1. 随着类的加载而加载，也是**存在方法区的==静态域==中**，可以通过 `类.静态方法` 的方式调用静态方法
2. 静态方法中属性的调用限制：
    1. **==静态方法中，只能调用静态的方法和属性==**
    2. 非静态方法中，既可以调用非静态方法或属性，也可以调用静态的方法或属性
3. **==在静态方法和静态代码块中不能使用====`this`====或====`super`====关键字==**

    ![[IMG-20260620222522807.png|443]]

    - 首先，`static` 静态方法先于任何的对象出现，在==方法区的静态域==中
    - 而 `this` 指针指向的是实例化对象的时候，JVM 在==堆中分配一个具体的对象，不在同一个范围，所以不能调用==
    - 同理，`super` 代表子类对父类满参构造函数的初始化，也是需要产生对象才可以使用

# 三、应用示例
1. 关于静态属性和静态方法的使用，要**从生命周期的角度考虑**
2. 开发中：
    1. 如何确定一个属性是否要声明称 static ？
        1. 属性可以被多个对象共享的，不会随着对象不同而不同
        2. 类中的常量一般也声明为static
    2. 如何确定一个方法是否要声明称 static ？
        1. 操作静态属性的方法通常设为静态方法，无需造对象调用
        2. 工具类中的方法，习惯上声明为 static，比如：**`Math.Arrays`**

    ```Java
     public class Circle {
         private double radius;
         private int id;
         public Circle() {
             id = init++;
             total++;
         }
         public Circle(double radius) {
             //id = init++;
             //total++;
             this();//调用Circle()
             this.radius = radius;
         }
         private static int total;//创建圆的个数
         private static int init = 1001;// id初始值，被多个对象共享
         public double findArea(){
             return Math.PI * radius * radius;
         }
         public double getRadius() {
             return radius;
         }
         public int getId() {
             return id;
         }
         public static int getTotal() {
             return total;
         }
     }
     public class CircleTest {
         public static void main(String[] args) {
             Circle circle1 = new Circle();
             Circle circle2 = new Circle();
             System.out.println(circle1.getId());//1001
             System.out.println(circle2.getId());//1002
             System.out.println(Circle.getTotal());//2
         }
     }
    ```
