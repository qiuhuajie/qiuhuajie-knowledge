---
title: "Set 接口"
tags:
  - "HashSet"
  - "TreeSet"
  - "Set_接口"
  - "LinkedHashSet"
  - "集合元素处于有序状态"
  - "线程"
updated: 2026-04-16
---

# 一、Set 接口介绍
1. 存储无序的、不可重复的数据
    1. **Set 的无序性：**
        1. 不等于随机性
        2. 存储的数据在底层数组中，**并非按照数组索引的顺序添加**，而是根据**数据的哈希值**添加的（以 `HashSet` 为例说明）
    2. **Set 的不可重复性：**
        1. 保证添加的元素按照 **`equals()`** **判断** 时，不能返回 true
        2. 相同的元素只能添加一次
2. `HashSet`、`LinkedHashSet`和 `TreeSet`都是 `Set`接口的实现类，==**都能保证元素唯一，并且都不是线程安全的**==
# 二、LinkedHashSet
- `LinkedHashSet` 的底层数据结构是**链表和哈希表**，元素的插入和取出顺序满足 FIFO
- `LinkedHashSet` 用于保证元素的插入和取出顺序满足 FIFO 的场景
- `LinkedHashSet` 是 `HashSet` 的子类
# 三、TreeSet
- `TreeSet` 底层数据结构是**红黑树**，元素是**==有序的==**，排序的方式有自然排序和定制排序
- `TreeSet` 用于支持对元素自定义排序规则的场景
- `TreeSet` 是 `SortedSet` 接口的实现类， TreeSet 可以确保**集合元素处于有序状态**
# 四、HashSet
## 1. 介绍
- `HashSet` 的底层数据结构是**哈希表（基于 `HashMap` 实现）**
- `HashSet` 用于不需要保证元素插入和取出顺序的场景
## 2. HashSet 中添加元素的过程
1. 过程和 HashMap `put()` 的过程类似
    1. **先用 `hashCode()` 得到哈希值，再根据哈希值得到索引位置**
    2. **如果该位置有元素了，要使用两步比较来确认这两个对象是不是一样的：先比较哈希值，如果哈希值也相同；再用 `equals()` 比较原始值**
    3. ==**和 HashMap put() 区别在于发生冲突后，HashMap 比较的是 key，而 HashSet 比较的是对象**==
    4. 判断冲突的比较顺序：位置 ➡️ 哈希值 ➡️ 原对象
2. 在 a 添加成功的情况下：元素 a 与已经存在指定位置上的数据以链表的形式存储

    ![[IMG-20260620221215321.png|438]]

3. HashSet 与 HashMap 比较

| HashMap | HashSet |
| --- | --- |
| 实现了 `Map` 接口 | 实现 `Set` 接口 |
| 存储**键值对** | 仅存储**对象** |
| 调用 `put()` 向 map 中添加元素 | 调用 `add()` 方法向 `Set` 中添加元素 |
| `HashMap` 使用**键**（Key）计算 `hashcode` | `HashSet` 使用成员**对象**来计算 `hashcode` 值，对于两个对象来说 `hashcode` 可能相同，所以 `equals()` 方法用来判断对象的相等性 |
## 3. JDK1.8 HashSet 源码
1. **`HashSet`** **底层就是基于** **`HashMap`** ==**实现的**==，除了 `clone()`、`writeObject()`、`readObject()` 是 `HashSet` 自己不得不实现之外，其他方法都是**直接调用 `HashMap` 中的方法**
2. 直接看一下`HashSet`中 `add()` 的源码：
    - `HashSet`的`add()`方法只是简单的调用了`HashMap`的`put()`方法，并且判断了一下返回值以确保是否有重复元素
    - 返回值：当 set 中没有包含 add 的元素时返回真

    ![[IMG-20260620221215424.png|587]]

3. 而在`HashMap`的`putVal()`方法中也能看到如下说明：
    - 返回值：如果插入位置没有元素返回null，否则返回上一个元素

    ![[IMG-20260620221215523.png|584]]

    ![[IMG-20260620221215622.png|495]]

4. ⭐也就是说，在 JDK1.8 中，==实际上无论====`HashSet`====中是否已经存在了某元素，====`HashSet`====都会直接插入==
    - **如果存在，底层调用的 HashMap 的** **`putVal()`** **会返回上一个元素，也即在 HashSet 的** **`add()`** **中，`map.put(e, PRESENT)==null` 为 **`false`**，表示插入失败**
    - **如果不存在，底层调用的 HashMap 的** **`putVal()`** **会返回** **`null`** **，也即在 HashSet 的** **`add()`** **中，`map.put(e, PRESENT)==null` 为 **`true`**，表示插入成功**
