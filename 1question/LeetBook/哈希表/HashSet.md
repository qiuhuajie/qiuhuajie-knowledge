---
title: "HashSet"
tags:
  - "LeetBook"
  - "LeetBook/哈希表"
  - "HashSet"
  - "哈希表"
  - "算法刷题"
  - "线程"
updated: 2026-04-16
---
- [[#一、📑128. 最长连续序列🔥✔️]]
- [[#二、📑剑指 Offer 03. 数组中重复的数字⚔️]]
- [[#三、📑349. 两个数组的交集]]
- [[#四、设计 HashSet]]
# 一、📑128. 最长连续序列🔥✔️
> ℹ️ 力扣（LeetCode）官网 - 全球极客挚爱的技术成长平台
> 备战技术面试？力扣提供海量技术面试资源，帮助你高效提升编程技能，轻松拿下世界 IT 名企 Dream Offer。
> [https://leetcode.cn/problems/longest-consecutive-sequence/](https://leetcode.cn/problems/longest-consecutive-sequence/)
1. 问题描述：

    ```Plain
    给定一个未排序的整数数组 nums ，找出数字连续的最长序列（不要求序列元素在原数组中连续）的长度。
    请你设计并实现时间复杂度为 O(n) 的算法解决此问题。
    ```
2. 示例：

    ```Plain
    示例 1：
    输入：nums = [100,4,200,1,3,2]
    输出：4
    解释：最长数字连续序列是 [1, 2, 3, 4]。它的长度为 4。
    示例 2：
    输入：nums = [0,3,7,2,5,8,4,6,0,1]
    输出：9
    ```
3. 代码：

    ```Java
    public int longestConsecutive(int[] nums) {
        if (nums.length == 0) return 0;
    		// 建立一个存储所有数的哈希表，同时起到去重功能
        Set<Integer> set = new HashSet<>();
        for (int num : nums) {
            set.add(num);
        }
        int res = Integer.MIN_VALUE;
        for (int num : nums) {
            int count = 1;
    				// 只有当num-1不存在时，才开始向后遍历num+1，num+2，num+3......，即找到连续的数中最小的那个
            if (!set.contains(num - 1)) {
                while (set.contains(num + count)) {
                    count++;
                }
            }
            res = Math.max(count, res);
        }
        return res;
    }
    ```
# 二、📑剑指 Offer 03. 数组中重复的数字⚔️
1. 问题描述：

    ```Plain
    找出数组中重复的数字。
    在一个长度为 n 的数组 nums 里的所有数字都在 0～n-1 的范围内。数组中某些数字是重复的，但不知道有几个数字重复了，也不知道每个数字重复了几次。请找出数组中任意一个重复的数字。
    ```
2. 示例：

    ```Plain
    输入：
    [2, 3, 1, 0, 2, 5, 3]
    输出：2 或 3
    ```
3. 代码：
    1. 哈希表
		```Java
		public int findRepeatNumber(int[] nums) {
			Set<Integer> dic = new HashSet<>();
			for(int num : nums) {
				if(dic.contains(num)) {
					return num;
				}
				dic.add(num);
			}
			return -1;
		}
		```
    2. ==**原地交换**==
        1. 题目：在一个长度为 n 的数组 nums 里的所有数字都在 0 ~ n-1 的范围内
        2. 此说明含义：数组元素的 索引 和 值 是 一对多 的关系。 因此，可遍历数组并通过交换操作，使元素的 索引 与 值 一一对应（即 nums[i]=i ）。因而，就能通过索引映射对应的值，起到与字典等价的作用
            ![[IMG-20260620203821884.png|563]]
        ```Java
        public static int findRepeatNumber(int[] nums) {
            int len = nums.length;
            int i = 0;
            while (i < len) {
                if (nums[i] == i) {
                    i++;
                    continue;
                }
                if (nums[nums[i]] == nums[i]) {
                    return nums[i];
                } else {
                    swap(nums, i, nums[i]);
                }
            }
            return -1;
        }
        private static void swap(int[] nums, int a, int b) {
            int tmp = nums[a];
            nums[a] = nums[b];
            nums[b] = tmp;
        }
        ```
# 三、📑349. 两个数组的交集
1. 问题描述：

    ```Plain
    给定两个数组，编写一个函数来计算它们的交集
    ```
2. 示例：

    ```Plain
    输入：nums1 = [1,2,2,1], nums2 = [2,2]
    输出：[2]
    ```
3. 代码：

    ```Java
    public static int[] intersection(int[] nums1, int[] nums2) {
        //将两个 数组放大 hashset中
        HashSet<Integer> set1 = new HashSet<>();
        HashSet<Integer> set2 = new HashSet<>();
        for (int num1 : nums1) {
            set1.add(num1);
        }
        for (int num2 : nums2) {
            set2.add(num2);
        }
        //选出两个set 公有的元素，存入 ArrayList<Integer> result
        ArrayList<Integer> result = new ArrayList<Integer>();
        Iterator<Integer> iterator = set1.iterator();
        //一个while (iterator.hasNext()) 中不能出现两个 .next()，否则会报NoSuchElementException异常（线程越界）
        /*while (iterator.hasNext()) {
            if (set2.contains(iterator.next())) {
                result.add(iterator.next());
            }
        }*/
        while (iterator.hasNext()) {
            Integer next = iterator.next();
            if (set2.contains(next)) {
                result.add(next);
            }
        }
        //把 ArrayList 转成 int[]
        int[] ints = new int[result.size()];
        int i = 0;
        for (Integer integer : result) {
            ints[i] = integer.intValue();
            i++;
        }
        return ints;
    }
    ```
# 四、设计 HashSet
```Java
 //执行用时：19 ms, 在所有 Java 提交中击败了29.79%的用户
 //内存消耗：45.1 MB, 在所有 Java 提交中击败了57.06%的用户
 class MyHashSet {
     private static final int BASE = 769;
     public LinkedList[] data ;
     public int hash(int key){
         return key % BASE;
     }
     public MyHashSet() {
         data = new LinkedList[BASE];
         for (int i = 0; i < BASE; i++) {
             data[i] = new LinkedList<Integer>();
         }
     }
     public void add(int key) {
         int index = hash(key);
         Iterator<Integer> iterator = data[index].iterator();
         while (iterator.hasNext()){
             Integer next = iterator.next();
             if (next == key){
                 return;
             }
         }
         data[index].offerLast(key);
     }
     public void remove(int key) {
         int index = hash(key);
         Iterator<Integer> iterator = data[index].iterator();
         while (iterator.hasNext()){
             Integer next = iterator.next();
             if (next == key){
                 data[index].remove(next);
                 return;
             }
         }
     }
     public boolean contains(int key) {
         int index = hash(key);
         Iterator<Integer> iterator = data[index].iterator();
         while (iterator.hasNext()){
             Integer next = iterator.next();
             if (next == key){
                 return true;
             }
         }
         return false;
     }
 }
```
```Java
//执行用时：17 ms, 在所有 Java 提交中击败了45.14%的用户
//内存消耗：46.3 MB, 在所有 Java 提交中击败了36.48%的用户
class MyHashSet {
    private static final int BASE = 769;
    public LinkedList[] data ;
    public int hash(int key){
        return key % BASE;
    }
    public MyHashSet() {
        data = new LinkedList[BASE];
        for (int i = 0; i < BASE; i++) {
            data[i] = new LinkedList();
        }
    }
    public void add(int key) {
        int index = hash(key);
        for (Object o : data[index]) {
            if (o.equals(key)){
                return;
            }
        }
        data[index].offerLast(key);
    }
    public void remove(int key) {
        int index = hash(key);
        for (Object o : data[index]) {
            if (o.equals(key)){
                data[index].remove(o);
                return;
            }
        }
    }
    public boolean contains(int key) {
        int index = hash(key);
        Iterator<Integer> iterator = data[index].iterator();
        for (Object o : data[index]) {
            if (o.equals(key)){
                return true;
            }
        }
        return false;
    }
}
```