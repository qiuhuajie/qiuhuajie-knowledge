---
title: "HashMap"
tags:
  - "LeetBook"
  - "LeetBook/哈希表"
  - "HashMap"
  - "哈希表"
  - "算法刷题"
  - "算法"
updated: 2026-04-16
---
- [[#一、设计 HashMap 🙋‍♂️]]
- [[#二、场景1：需存储元素以及索引]]
    - [[#1. 📑1. 两数之和🔥✔️]]
    - [[#2. 📑205. 同构字符串]]
    - [[#3. 📑599. 两个列表的最小索引总和]]
- [[#三、场景2：设计键提取共同特征分类]]
    - [[#1. 📑49. 字母异位词分组🔥✔️]]
- [[#四、场景3：统计出现次数、重复等]]
    - [[#1. 📑387. 字符串中的第一个唯一字符]]
    - [[#2. 📑350. 两个数组的交集 II]]
    - [[#3. 📑219. 存在重复元素 II]]
    - [[#4. 📑771. 宝石与石头]]
    - [[#5. 📑454. 四数相加 II]]
    - [[#6. 📑347. 前 K 个高频元素]]
    - [[#7. 📑398. 随机索引数]]
# 一、设计 HashMap 🙋‍♂️
1. 元素节点 Node 构造

    ```Java
    class Node<K,T> {
        K key;
        T value;
        Node<K,T> next;
        public Node(K key, T value) {
            this.key = key;
            this.value = value;
        }
        public Node(K key, T value, Node<K, T> next) {
            this.key = key;
            this.value = value;
            this.next = next;
        }
        public K getKey() {
            return key;
        }
        public T getValue() {
            return value;
        }
        public void setKey(K key) {
            this.key = key;
        }
        public void setValue(T value) {
            this.value = value;
        }
    }
    ```
2. 初始化方法

    ```Java
    public MyHashMap() {
        // 初始化
        buckets = new Node[CAPCITY];
    }
    ```
3. 变量  ```Java
    Node[] buckets;
    final int CAPCITY = 3;
    final float LOAD_FACTOR = 0.75f;
    int size = 0;
    ```java
4. 扩容方法

    ```Java
    private void resize() {
        //创建一个两倍容量的桶数组
        Node<K, T>[] newBuckets = new Node[buckets.length * 2];
        //将当前元素重新散列到新的桶数组
        rehash(newBuckets);
        buckets = newBuckets;
    }
    private void rehash(Node<K, T>[] newBuckets) {
        //map大小重新计算
        size = 0;
        //将旧的桶数组的元素全部刷到新的桶数组里
        for (int i = 0; i < buckets.length; i++) {
            //为空，跳过
            if (buckets[i] == null) {
                continue;
            }
            Node<K, T> node = buckets[i];
            while (node != null) {
                //将元素放入新数组
                putVal(node.key, node.value, newBuckets);
                node = node.next;
            }
        }
    }
    ```
5. put 元素

    ```Java
    public void put(K key, T value) {
        //判断是否需要进行扩容
        if (size >= buckets.length * LOAD_FACTOR) resize();
        putVal(key, value, buckets);
        size++;
    }
    public <T> void putVal(K key, T value, Node[] buckets) {
        // 获取hash下标
        int index = Math.abs(key.hashCode() % CAPCITY);
        Node node = buckets[index];
        // 目标位置是否为空
        if (node == null) {
            buckets[index] = new Node<K, T>(key, value);
        } else {
            // 如果存在元素，则便利找相同 key.hashcode 且 key 相同的元素，替换 value
            while (node != null) {
                if (node.key.hashCode() == key.hashCode() && node.key == key) {
                    node.value = value;
                    return;
                }
                node = node.next;
            }
            // 不存在相同 key，则新建一个 node 做头插
            Node<K, T> newNode = new Node<>(key, value);
            newNode.next = buckets[index];
            buckets[index] = newNode;
        }
    }
    ```
6. get 元素

    ```Java
    public T get(K key) {
        int index = Math.abs(key.hashCode() % CAPCITY);
        Node node = buckets[index];
        if (node == null) {
            return null;
        } else {
            while (node != null) {
                if (node.key.hashCode() == key.hashCode() && node.key == key) {
                    // 找到元素，返回 value
                    return (T) node.value;
                }
                node = node.next;
            }
            return null;
        }
    }
    ```
7. 删除元素 remove

    ```Java
    public <T> void remove(K key) {
        int index = Math.abs(key.hashCode() % CAPCITY);
        Node node = buckets[index];
        if (node == null) {
            return;
        } if (node.next == null) {
            buckets[index] = null;
        } else {
            // 对链表做删除操作，要使用 pre 指向前一个元素
            Node pre = node;
            node = node.next;
            while (node != null) {
                if (node.key.hashCode() == key.hashCode() && node.key == key) {
                    pre.next = node.next;
                    return;
                }
                node = node.next;
            }
        }
        size--;
    }
    ```
8. 完整代码
    - ```Java
        import java.util.ArrayList;
        import java.util.LinkedList;
        import java.util.List;
        /**
         * @author qiutian
         * @date 2023/6/21
         */
        public class MyHashMap<K,T> {
            Node[] buckets;
            final int CAPCITY = 3;
            final float LOAD_FACTOR = 0.75f;
            int size = 0;
            public MyHashMap() {
                // 初始化
                buckets = new Node[CAPCITY];
            }
            private void resize() {
                //创建一个两倍容量的桶数组
                Node<K, T>[] newBuckets = new Node[buckets.length * 2];
                //将当前元素重新散列到新的桶数组
                rehash(newBuckets);
                buckets = newBuckets;
            }
            private void rehash(Node<K, T>[] newBuckets) {
                //map大小重新计算
                size = 0;
                //将旧的桶数组的元素全部刷到新的桶数组里
                for (int i = 0; i < buckets.length; i++) {
                    //为空，跳过
                    if (buckets[i] == null) {
                        continue;
                    }
                    Node<K, T> node = buckets[i];
                    while (node != null) {
                        //将元素放入新数组
                        putVal(node.key, node.value, newBuckets);
                        node = node.next;
                    }
                }
            }
            public void put(K key, T value) {
                //判断是否需要进行扩容
                if (size >= buckets.length * LOAD_FACTOR) resize();
                putVal(key, value, buckets);
                size++;
            }
            public <T> void putVal(K key, T value, Node[] buckets) {
                // 获取hash下标
                int index = Math.abs(key.hashCode() % CAPCITY);
                Node node = buckets[index];
                // 目标位置是否为空
                if (node == null) {
                    buckets[index] = new Node<K, T>(key, value);
                } else {
                    // 如果存在元素，则便利找相同 key.hashcode 且 key 相同的元素，替换 value
                    while (node != null) {
                        if (node.key.hashCode() == key.hashCode() && node.key == key) {
                            node.value = value;
                            return;
                        }
                        node = node.next;
                    }
                    // 不存在相同 key，则新建一个 node 做头插
                    Node<K, T> newNode = new Node<>(key, value);
                    newNode.next = buckets[index];
                    buckets[index] = newNode;
                }
            }
            public T get(K key) {
                int index = Math.abs(key.hashCode() % CAPCITY);
                Node node = buckets[index];
                if (node == null) {
                    return null;
                } else {
                    while (node != null) {
                        if (node.key.hashCode() == key.hashCode() && node.key == key) {
                            // 找到元素，返回 value
                            return (T) node.value;
                        }
                        node = node.next;
                    }
                    return null;
                }
            }
            public <T> void remove(K key) {
                int index = Math.abs(key.hashCode() % CAPCITY);
                Node node = buckets[index];
                if (node == null) {
                    return;
                } if (node.next == null) {
                    buckets[index] = null;
                } else {
                    // 对链表做删除操作，要使用 pre 指向前一个元素
                    Node pre = node;
                    node = node.next;
                    while (node != null) {
                        if (node.key.hashCode() == key.hashCode() && node.key == key) {
                            pre.next = node.next;
                            return;
                        }
                        node = node.next;
                    }
                }
                size--;
            }
        }
        class Node<K,T> {
            K key;
            T value;
            Node<K,T> next;
            public Node(K key, T value) {
                this.key = key;
                this.value = value;
            }
            public Node(K key, T value, Node<K, T> next) {
                this.key = key;
                this.value = value;
                this.next = next;
            }
            public K getKey() {
                return key;
            }
            public T getValue() {
                return value;
            }
            public void setKey(K key) {
                this.key = key;
            }
            public void setValue(T value) {
                this.value = value;
            }
        }
        ```
# 二、场景1：需存储元素以及索引
> 除元素本身之外，还需要存储索引

## 1. 📑1. 两数之和🔥✔️
> ℹ️ 力扣（LeetCode）官网 - 全球极客挚爱的技术成长平台
> 备战技术面试？力扣提供海量技术面试资源，帮助你高效提升编程技能，轻松拿下世界 IT 名企 Dream Offer。
> [https://leetcode.cn/problems/two-sum/](https://leetcode.cn/problems/two-sum/)
1. 问题描述：

    ```Plain
    给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出 和为目标值 target  的那 两个 整数，并返回它们的数组下标。
    你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。
    你可以按任意顺序返回答案
    ```
2. 示例：

    ```Plain
    输入：nums = [3,2,4], target = 6
    输出：[1,2]
    ```
3. 代码：
    1. 在这个题中，如果我们只想在有解决方案时返回 true，我们可以使用**哈希集合**来存储迭代数组时的所有值，并检查 target - current_value 是否在哈希集合中
    2. 但是，我们被要求返回更多信息，这意味着我们不仅关心值，还关心索引。我们不仅需要存储数字作为键，还需要存储索引作为值。因此，我们应该使用**哈希映射**而不是哈希集合

    ```Java
    //前后双指针无法解决，那道题的原数组是递增有序的
    //这里需要的更多信息是指，需要额外保存下标
    public static int[] twoSum(int[] numbers,int target){
        HashMap<Integer,Integer> hashMap = new HashMap<Integer,Integer>();
        int[] ints = null;
        for (int i = 0; i < numbers.length; i++) {
            //看 target - 当前遍历数字 是否在map中
            if (hashMap.containsKey(target - numbers[i])){
                ints = new int[]{hashMap.get(target - numbers[i]),i};
            }
            hashMap.put(numbers[i],i);
        }
        return ints;
    }
    ```
## 2. 📑205. 同构字符串
1. 问题描述：

    ```Plain
    给定两个字符串 s 和 t，判断它们是否是同构的。
    如果 s 中的字符可以按某种映射关系替换得到 t ，那么这两个字符串是同构的。
    每个出现的字符都应当映射到另一个字符，同时不改变字符的顺序。不同字符不能映射到同一个字符上，相同字符只能映射到同一个字符上，字符可以映射到自己本身
    可以假设 s 和 t 长度相同
    ```
2. 示例：

    ```Plain
    输入：s = "foo", t = "bar"
    输出：false
    输入：s = "paper", t = "title"
    输出：true
    ```
3. 代码：

    ```Java
    public boolean isIsomorphic(String s, String t) {
        HashMap<Character,Character> hashMap = new HashMap<>();
        //可以假设 s 和 t 长度相同
        for (int i = 0; i < s.length(); i++) {
            //false 条件: 当前s的字符 可以在map中找到对应value，且这个value不等于 当前t的字符
            if (hashMap.get(s.charAt(i)) != null && !hashMap.get(s.charAt(i)).equals(t.charAt(i))){
                return false;
            }
            //false 条件: 当前s的字符 不在map中，但是 t的当前字符已经存入 map（和其他字符已经做了映射了）
            if (!hashMap.containsKey(s.charAt(i)) && hashMap.containsValue(t.charAt(i))){
                return false;
            }
            hashMap.put(s.charAt(i),t.charAt(i));
        }
        return true;
    }
    ```
## 3. 📑599. 两个列表的最小索引总和
1. 问题描述：

    ```Plain
    假设Andy和Doris想在晚餐时选择一家餐厅，并且他们都有一个表示最喜爱餐厅的列表，每个餐厅的名字用字符串表示。
    你需要帮助他们用最少的索引和找出他们共同喜爱的餐厅。 如果答案不止一个，则输出所有答案并且不考虑顺序。 你可以假设总是存在一个答案
    ```
2. 示例：

    ```Plain
    输入:
    ["Shogun", "Tapioca Express", "Burger King", "KFC"]
    ["Piatti", "The Grill at Torrey Pines", "Hungry Hunter Steakhouse", "Shogun"]
    输出: ["Shogun"]
    解释: 他们唯一共同喜爱的餐厅是“Shogun”
    ```
3. 代码：

    ```Java
    public class FindRestaurant {
        public static String[] findRestaurant(String[] list1, String[] list2) {
            HashMap<String, Integer> hashMap1 = new HashMap<>();
            HashMap<String, Integer> hashMap2 = new HashMap<>();
            for (int i = 0; i < list1.length; i++) {
                hashMap1.put(list1[i],i);
            }
            for (int j = 0; j < list2.length; j++) {
                hashMap2.put(list2[j],j);
            }
            HashMap<String, Integer> resultMap = new HashMap<>();
            for (String s : list1) {
                if (hashMap2.containsKey(s)){
                    resultMap.put(s,hashMap1.get(s) + hashMap2.get(s));
                }
            }
            Set<Map.Entry<String, Integer>> entries = resultMap.entrySet();
            int min = Integer.MAX_VALUE;
            for (Map.Entry<String, Integer> entry : entries) {
                if (entry.getValue() < min){
                    min = entry.getValue();
                }
            }
            ArrayList<String> strings = new ArrayList<>();
            for (Map.Entry<String, Integer> entry : entries) {
                if (entry.getValue() == min){
                    strings.add(entry.getKey());
                }
            }
            return strings.toArray(new String[]{});
        }
        public static void main(String[] args) {
            String[] list1 = {"Shogun","Tapioca Express","Burger King","KFC"};
            String[] list2 = {"Piatti","The Grill at Torrey Pines","Hungry Hunter Steakhouse","Shogun"};
            String[] restaurant = findRestaurant(list1, list2);
            for (String s : restaurant) {
                System.out.println(s);
            }
        }
    }
    ```
# 三、场景2：设计键提取共同特征分类
## 1. 📑49. 字母异位词分组🔥✔️
1. 问题描述：

    ```Plain
    给你一个字符串数组，请你将 字母异位词 组合在一起。可以按任意顺序返回结果列表。
    字母异位词 是由重新排列源单词的字母得到的一个新单词，所有源单词中的字母都恰好只用一次
    ```
2. 示例：

    ```Plain
    输入: strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
    输出: [["bat"],["nat","tan"],["ate","eat","tea"]]
    ```
3. 代码：

    ```Java
    public List<List<String>> groupAnagrams(String[] strs) {
        HashMap<String, List<String>> map = new HashMap<>();
        for (String str : strs) {
            char[] chars = str.toCharArray();
            Arrays.sort(chars);
            String key = String.valueOf(chars);
            List<String> list = map.getOrDefault(key, new ArrayList<String>());
            list.add(str);
            map.put(key, list);
        }
    		// Collection<List<String>> values = hashmap.values(); 要转为 List
        return new ArrayList(map.values());
    }
    ```
# 四、场景3：统计出现次数、重复等
> 按键聚合
1. 按键聚合所有信息。我们也可以使用哈希映射来实现这一目标
2. 示例
    > 给定一个字符串，找到它中的第一个非重复字符并返回它的索引。如果它不存在，则返回 -1
    1. 解决此问题的一种简单方法是首先计算每个字符的出现次数。然后通过结果找出第一个与众不同的角色
    2. 因此，我们可以维护一个**哈希映射**，其**键是字符，而值是相应字符的计数器**
    3. 每次迭代一个字符时，我们只需将相应的值加 1
    4. ⭐当看到 与 重复 有关的场景，都可以考虑 hashmap

## 1. 📑387. 字符串中的第一个唯一字符
1. 问题描述：

    ```Plain
    给定一个字符串，找到它的第一个不重复的字符，并返回它的索引。如果不存在，则返回 -1
    ```
2. 示例：

    ```Plain
    s = "leetcode"
    返回 0
    s = "loveleetcode"
    返回 2
    ```
3. 代码：

    ```Java
    //执行用时：45 ms, 在所有 Java 提交中击败了5.04%的用户
        public static int firstUniqChar(String s) {
            HashMap<Character, int[]> hashMap = new HashMap<>();
            int count;
            //遍历字符串，因为要返回字符的索引，所以我这里 map 值设为了一个 int[]，存放出现次数和字符的索引值
            for (int i = 0; i < s.length(); i++) {
                count = 0;
                int[] ints = new int[2];
                if (hashMap.containsKey(s.charAt(i))){
                    count = hashMap.get(s.charAt(i))[0] + 1;
                    ints[0] = count;
                    ints[1] = hashMap.get(s.charAt(i))[1];
                    hashMap.put(s.charAt(i),ints);
                }else {
                    ints[0] = 1;
                    ints[1] = i;
                    hashMap.put(s.charAt(i),ints);
                }
            }
            ArrayList<Integer> list = new ArrayList<>();
            int index = 0;
            Set<Map.Entry<Character, int[]>> entries = hashMap.entrySet();
            //遍历 hashmap 找出其中 出现次数为 1 的 entries，返回其对应值中存出的字符索引值，add 到 list中
            for (Map.Entry<Character, int[]> entry : entries) {
                if (entry.getValue()[0] == 1){
                    list.add(entry.getValue()[1]);
                }
            }
            //如果 此时 list 为空，则说明不存在只出现过一次的字符
            if (list.isEmpty()){
                return -1;
            }
            //遍历 list 找出 最小值，即第一个只出现过一次的字符的索引值
            int min = Integer.MAX_VALUE;
            for (Integer integer : list) {
                if (integer < min){
                    min = integer;
                }
            }
            return min;
        }
    ```

    注意： map 中每个键值对 在 map 中的顺须并不是 push 先后的顺序

    上面写那么多代码的原因是 第二次的遍历思路是遍历 hashmap 这样无法确定 索引值，但按下面的方法，第二次的遍历还是去遍历 原字符串，很容易就能得到 对应的索引

    ```Java
    /*
    * 执行用时：33 ms, 在所有 Java 提交中击败了12.21%的用户
    * */
    public static int firstUniqChar(String s) {
        HashMap<Character, Integer> hashMap = new HashMap<>();
        int count;
        //遍历 字符串 统计每个 字符出现的次数，push 到 hashmap 中
        for (int i = 0; i < s.length(); i++) {
            /*if (hashMap.containsKey(s.charAt(i))){
                hashMap.put(s.charAt(i),hashMap.get(s.charAt(i)) + 1);
            }else {
                hashMap.put(s.charAt(i),1);
            }*/
            //⭐getOrDefault()
            int value = hashMap.getOrDefault(s.charAt(i),0);
            hashMap.put(s.charAt(i),value + 1);
        }
        //再次 遍历 字符串，判断这个字符串的 value 是否为 1
        for (int i = 0; i < s.length(); i++) {
            if (hashMap.get(s.charAt(i)) == 1){
                return i;
            }
        }
        return -1;
    }
    ```
    > 新的hashmap 方法：getOrDefault()
    > 
    > 1. 在使用hashmap 做出现次数统计时使用
    > 
    > 2. getOrDefault() 方法获取指定 key 对应对 value，如果找不到 key ，则返回设置的默认值
    > 
    > 3. getOrDefault() 方法的语法为：
>
    >     ```Java
    >     hashmap.get(Object key, V defaultValue)
    >     ```
>
    >     **参数说明：**
    >
    >     - key - 键
    >
    >     - defaultValue - 当指定的key并不存在映射关系中，则返回的该默认值

## 2. 📑350. 两个数组的交集 II
1. 问题描述：

    ```Plain
    给定两个数组，编写一个函数来计算它们的交集
    ```
2. 示例：

    ```Plain
    输入：nums1 = [1,2,2,1], nums2 = [2,2]
    输出：[2,2]
    ```
3. 代码：

    注意：本题与之前的349求交集不一样，之前的在交集中不考虑重复，所以可以将两个数组都变为 hashset

    ```Java
    //方法一：双指针（前提有序）
    public int[] intersect(int[] nums1, int[] nums2) {
            //先将两个数组排序
            Arrays.sort(nums1);
            Arrays.sort(nums2);
            ArrayList<Integer> list = new ArrayList<>();
            int i = 0,j = 0;
            //双指针遍历，只要有一个遍历完就结束
            while (i < nums1.length && j < nums2.length){
                //如果不相等，将值小的指针后移一位
                if (nums1[i] < nums2[j]){
                    i++;
                }else if (nums1[i] > nums2[j]){
                    j++;
                }else {
                //如果相等，将两个指针都后移一位，并记录结果
                    list.add(nums1[i]);
                    i++;
                    j++;
                }
            }
            int[] result = new int[list.size()];
            for (int k = 0; k < list.size(); k++) {
                result[k] = list.get(k);
            }
            return result;
        }
    }
    ```

    方法二：

    ```Java
    //方法二：hashmap
    public int[] intersect(int[] nums1, int[] nums2) {
        HashMap<Integer, Integer> hashMap = new HashMap<>();
        int count = 0;
        //遍历 第一个数组 将字符出现次数统计到 hashmap
        for (int i = 0; i < nums1.length; i++) {
            count = hashMap.getOrDefault(nums1[i],0);
            hashMap.put(nums1[i],count + 1);
        }
        ArrayList<Integer> list = new ArrayList<>();
        int value = 0;
        //遍历 第二个数组
        for (int i = 0; i < nums2.length; i++) {
            //如果 hashmap 中包含这个字符
            if (hashMap.containsKey(nums2[i])){
                //首先确定这个字符是重复的，即要加入到交集中
                list.add(nums2[i]);
                value = hashMap.get(nums2[i]);
                //如果 出现次数为 1了，则需要将hashmap 中的这个键值对删除
                if (value == 1){
                    hashMap.remove(nums2[i]);
                }else {
                    //如果不为 1 ，则将出现次数减一
                    hashMap.put(nums2[i], value - 1);
                }
            }
        }
        //list 转 int[]
        int[] ints = new int[list.size()];
        for (int i = 0; i < list.size(); i++) {
            ints[i] = list.get(i);
        }
        return ints;
    }
    ```
## 3. 📑219. 存在重复元素 II
1. 问题描述：

    ```Plain
    给定一个整数数组和一个整数 k，判断数组中是否存在两个不同的索引 i 和 j，使得 nums [i] = nums [j]，并且 i 和 j 的差的 绝对值 至多为 k
    ```
2. 示例：

    ```Plain
    输入: nums = [1,2,3,1], k = 3
    输出: true
    ```
3. 代码：

    ```Java
    public boolean containsNearbyDuplicate(int[] nums, int k) {
        HashMap<Integer, Integer> hashMap = new HashMap<>();
        for (int i = 0; i <nums.length ; i++) {
            //如果包含（两个数等值），且两个数的s距离满足 <= k
            if (hashMap.containsKey(nums[i]) && (i - hashMap.get(nums[i]) < k)){
                return true;
            }
            //不包含则添加 < 数组值 , 索引值 >
            hashMap.put(nums[i],i);
            //添加时，不需要考虑键值对替换的问题
            //因为此时 key 满足相等，但 value 不满足条件 的这个数，是离前一个等值数最近的数，如果他与前面的距离都大于 k
            //那么后边的更不需要考虑，故直接 push 替换不会影响
        }
        return false;
    }
    ```
## 4. 📑771. 宝石与石头
1. 问题描述：

    ```Plain
     给你一个字符串 jewels 代表石头中宝石的类型，另有一个字符串 stones 代表你拥有的石头。 stones 中每个字符代表了一种你拥有的石头的类型，你想知道你拥有的石头中有多少是宝石。
    字母区分大小写，因此 "a" 和 "A" 是不同类型的石头
    ```
2. 示例：

    ```Plain
    输入：jewels = "aA", stones = "aAAbbbb"
    输出：3
    ```
3. 代码：

    ```Java
    public static int numJewelsInStones(String jewels, String stones) {
        HashMap<Character, Integer> stonesMap = new HashMap<>();
        for (int i = 0; i < stones.length(); i++) {
            int num = stonesMap.getOrDefault(stones.charAt(i),0);
            stonesMap.put(stones.charAt(i),num + 1);
        }
        int count = 0;
        for (int i = 0; i < jewels.length(); i++) {
            if (stonesMap.containsKey(jewels.charAt(i))){
                count += stonesMap.get(jewels.charAt(i));
            }
        }
        return count;
    }
    ```
## 5. 📑454. 四数相加 II
1. 问题描述：

    ```Plain
    给你四个整数数组 nums1、nums2、nums3 和 nums4 ，数组长度都是 n ，请你计算有多少个元组 (i, j, k, l) 能满足：
    0 <= i, j, k, l < n
    nums1[i] + nums2[j] + nums3[k] + nums4[l] == 0
    ```
2. 示例：

    ```Plain
    输入：nums1 = [1,2], nums2 = [-2,-1], nums3 = [-1,2], nums4 = [0,2]
    输出：2
    解释：
    两个元组如下：
    1. (0, 0, 0, 1) -> nums1[0] + nums2[0] + nums3[0] + nums4[1] = 1 + (-2) + (-1) + 2 = 0
    2. (1, 1, 0, 0) -> nums1[1] + nums2[1] + nums3[0] + nums4[0] = 2 + (-1) + (-1) + 0 = 0
    ```
3. 代码：
    1. 四层循环超时
    2. 可以将四个数组分成两部分，A 和 B 为一组，C 和 D 为另外一组
    3. 对于 A 和 B，我们使用二重循环对它们进行遍历，得到所有 A[i]+B[j] 的值并存入哈希映射中

    ```Java
    public int fourSumCount(int[] nums1, int[] nums2, int[] nums3, int[] nums4) {
        //分组 ＋ 哈希表
        HashMap<Integer, Integer> hashMap = new HashMap<>();
        int count = 0;
        for (int num1 : nums1) {
            for (int num2 : nums2) {
                Integer currSum = hashMap.getOrDefault(num1 + num2, 0);
                hashMap.put(num1 + num2,currSum + 1);
            }
        }
        for (int num3 : nums3) {
            for (int num4 : nums4) {
                if (hashMap.containsKey(-(num3 + num4))){
                    count += hashMap.get(-(num3 + num4));
                }
            }
        }
        return count;
    }
    ```
## 6. 📑347. 前 K 个高频元素
1. 问题描述：

    ```Plain
    给你一个整数数组 nums 和一个整数 k ，请你返回其中出现频率前 k 高的元素。你可以按 任意顺序 返回答案
    ```
2. 示例：

    ```Plain
    输入: nums = [1,1,1,2,2,3], k = 2
    输出: [1,2]
    ```
3. 代码：

    **堆**

    ```Java
    public static int[] topKFrequent(int[] nums, int k) {
        HashMap<Integer, Integer> hashMap = new HashMap<>();
        for (int num : nums) {
            Integer currNum = hashMap.getOrDefault(num, 0);
            hashMap.put(num,currNum + 1);
        }
        //⭐堆结构的优秀实现类：PriorityQueue优先队列
        //队列每个元素存储一个元组 int[]{数字,数字出现的次数}
        PriorityQueue<int[]> queue = new PriorityQueue<>(new Comparator<int[]>() {
            //使用comparator对象来实现排序中的比较
            public int compare(int[] o1, int[] o2) {
                //o1为一个int[]，index=1指向数字出现的次数
                return o1[1] - o2[1];
            }
        });
        //使用统计出现次数后的hashmap来构建一个小根堆
        //堆中只保存k个元组
        Set<Map.Entry<Integer, Integer>> entries = hashMap.entrySet();
        for (Map.Entry<Integer, Integer> entry : entries) {
            int currKey = entry.getKey();
            int currValue = entry.getValue();
            if (queue.size() == k){
                //queue 的大小为k时：如果堆顶元组的value小于当前元组的value，则堆弹出堆顶元素，将当前元组插入
                //				      （当前堆顶是 出现次数前k高频 中 出现次数最小的元素，如果出现一个比它大的，则要把堆顶元素淘汰）
                //                 如果堆顶元组的value不小于当前元组的value，则不做任何处理
                //                    （当前堆顶是 出现次数前k高频 中 出现次数最小的元素，如果出现一个比它还小的，则直接忽略）
                if (queue.peek()[1] < currValue){
                    queue.poll();
                    //将元组offer后，优先队列会根据排序规则自动对堆进行调整
                    queue.offer(new int[]{currKey,currValue});
                }
            }else {
                //queue 的大小不等于 k 时（只能是小于k，只要一等于k），直接插入当前元组
                queue.offer(new int[]{currKey,currValue});
            }
        }
        //最后在堆中的 k 个元组的数，就是出现次数 较多的 k 个数
        int[] result = new int[k];
        for (int i = 0; i < k; i++) {
            result[i] = queue.poll()[0];
        }
        return result;
    }
    ```
## 7. 📑398. 随机索引数
1. 问题描述：

    ```Plain
    给你一个可能含有 重复元素 的整数数组 nums ，请你随机输出给定的目标数字 target 的索引。你可以假设给定的数字一定存在于数组中。
    实现 Solution 类：
    Solution(int[] nums) 用数组 nums 初始化对象。
    int pick(int target) 从 nums 中选出一个满足 nums[i] == target 的随机索引 i 。如果存在多个有效的索引，则每个索引的返回概率应当相等。
    ```
2. 示例：

    ```Plain
    输入
    ["Solution", "pick", "pick", "pick"]
    [[[1, 2, 3, 3, 3]], [3], [1], [3]]
    输出
    [null, 4, 0, 2]
    解释
    Solution solution = new Solution([1, 2, 3, 3, 3]);
    solution.pick(3); // 随机返回索引 2, 3 或者 4 之一。每个索引的返回概率应该相等。
    solution.pick(1); // 返回 0 。因为只有 nums[0] 等于 1 。
    solution.pick(3); // 随机返回索引 2, 3 或者 4 之一。每个索引的返回概率应该相等。
    ```
3. 代码：

    ```Java
    public class RandomIndex {
        //map <元素，存储所有元素下标的list>
        HashMap<Integer, List<Integer>> map;
        int size = 0;
        //初始化
        public RandomIndex(int[] nums) {
            this.map = new HashMap<Integer, List<Integer>>();
            for (int i = 0; i < nums.length; i++) {
                //已存在，新建一个list将当前index加入
                if (!map.containsKey(nums[i])) {
                    ArrayList<Integer> list = new ArrayList<>();
                    list.add(i);
                    map.put(nums[i], list);
                }else {
                    //不存在，取出list将当前index加入，再put进hashmap
                    List<Integer> list = map.get(nums[i]);
                    list.add(i);
                    map.put(nums[i], list);
                }
            }
        }
        public int pick(int target) {
            if (!map.containsKey(target)){
                return 0;
            }
            List<Integer> list = map.get(target);
            double randomIndex = Math.random() * list.size();
            //从target的list中将随机index的值取出
            return list.get((int) randomIndex);
        }
    }
    ```