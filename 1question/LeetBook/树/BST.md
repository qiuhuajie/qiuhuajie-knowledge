---
title: "BST"
tags:
  - "LeetBook"
  - "LeetBook/树"
  - "BST"
  - "树"
  - "算法刷题"
  - "SQL"
updated: 2026-04-16
---
- [[#一、BST 介绍]]
- [[#二、例题]]
    - [[#1. 📑98. 验证二叉搜索树🔥]]
    - [[#2. 📑109. 有序链表转换二叉搜索树]]
    - [[#3. 📑108. 将有序数组转换为二叉搜索树]]
    - [[#4. 📑96. 不同的二叉搜索树🔥]]
    - [[#5. 📑538. 把二叉搜索树转换为累加树🔥]]
    - [[#6. 📑剑指 Offer 33. 二叉搜索树的后序遍历序列⚔️]]
    - [[#7. 📑剑指 Offer 36. 二叉搜索树与双向链表⚔️]]
    - [[#8. 📑剑指 Offer 54. 二叉搜索树的第k大节点⚔️]]
    - [[#9. 📑剑指 Offer 68 - I. 二叉搜索树的最近公共祖先⚔️]]
# 一、BST 介绍
1. 二叉树算法的设计总路线：**==明确一个节点要做的事，然后剩下的事交给递归框架==**
2. 二叉搜索树（BST）是二叉树的一种特殊表示形式，它满足如下特性：
    1. 每个节点中的值必须**大于**存储在其左侧子树中的任何值
    2. 每个节点中的值必须**小于**存储在其右子树中的任何值
3. 下面是一个二叉搜索树的例子：

    ![[IMG-20260620200017491.png|218]]

4. 像普通的二叉树一样，我们可以按照前序、中序和后序来遍历一个二叉搜索树
    1. BST **==中序遍历==**的特点
        1. **对于二叉搜索树，**==**可以通过中序遍历得到一个递增的有序序列**==
        2. 因此，中序遍历是二叉搜索树中最常用的遍历方法
    2. BST **==后序遍历==**的特点
        1. 在 BST 后序遍历形成的序列中，==**最后一个数字是根节点的值**==
        2. 数组中==前面的数字可以分为====**两部分**====：第一部分是左子树的元素（都比根节点小）；第二部分是右子树的元素（都比根节点大）==

            ![[IMG-20260620200017623.png|360]]

        3. 序列中不可能存在 `3，1，2` 模式的子序列

# 二、例题
## 1. 📑98. 验证二叉搜索树🔥
1. 问题描述：

    ```Plain
    给你一个二叉树的根节点 root ，判断其是否是一个有效的二叉搜索树。
    有效 二叉搜索树定义如下：
    节点的左子树只包含 小于 当前节点的数。
    节点的右子树只包含 大于 当前节点的数。
    所有左子树和右子树自身必须也是二叉搜索树。
    ```
2. 示例：

    ```Plain
    输入：root = [2,1,3]
    输出：true
    输入：root = [5,1,4,null,null,3,6]
    输出：false
    解释：根节点的值是 5 ，但是右子节点的值是 4
    ```
3. 代码：
    1. 使用中序遍历

        ```Java
        public class IsValidBST {
            long pre = Long.MIN_VALUE;
            //int pre = Integer.MIN_VALUE;
            //注：Integer.MIN_VALUE = -2147483648
            //输入[-2147483648]时，返回false(×)
            public boolean isValidBST(TreeNode root) {
                return InOrder(root);
            }
            public boolean InOrder(TreeNode root){
                if (root == null){
                    return true;
                }
                boolean left = InOrder(root.left);
                //在中序遍历中，就直接比较当前val和上一个val(pre)的大小关系
                if (root.val <= pre){
                    return false;
                }
                pre = root.val;
                boolean right = InOrder(root.right);
                return left && right;
            }
        }
        ```
    2. 使用递归

        ```SQL
        public boolean isValidBST(TreeNode root){
            return isValidBST(root, null, null);
        }
        // (min, max) 表示当前遍历到的节点的取值范围，不在里面的直接返回 false
        public boolean isValidBST(TreeNode root, TreeNode min, TreeNode max) {
            if (root == null){
                return true;
            }
            if (min != null && min.val >= root.val) return false;
            if (max != null && max.val <= root.val) return false;
            // 当前节点左树上节点的范围为：在当前节点的基础上，将最大值缩小为当前节点的值
            // 当前节点右树上节点的范围为：在当前节点的基础上，将最小值放大为当前节点的值
            return isValidBST(root.left, min, root) && isValidBST(root.right, root, max);
        }
        ```
## 2. 📑109. 有序链表转换二叉搜索树
> ℹ️ 力扣（LeetCode）官网 - 全球极客挚爱的技术成长平台
> 备战技术面试？力扣提供海量技术面试资源，帮助你高效提升编程技能，轻松拿下世界 IT 名企 Dream Offer。
> [https://leetcode.cn/problems/convert-sorted-list-to-binary-search-tree/](https://leetcode.cn/problems/convert-sorted-list-to-binary-search-tree/)
1. 问题描述：

    ```Plain
    给定一个单链表的头节点  head ，其中的元素 按升序排序 ，将其转换为高度平衡的二叉搜索树。
    本题中，一个高度平衡二叉树是指一个二叉树每个节点 的左右两个子树的高度差不超过 1。 
    ```
2. 示例：

    ![[IMG-20260620200017731.png|335]]

3. 代码：

    ```Java
     public class SortedListToBST {
        public static TreeNode sortedListToBST(ListNode head) {
            return generate(head, null);
        }
        private static TreeNode generate(ListNode left, ListNode right) {
            if (left == right) return null;
            // 找中点
            ListNode median = getMedian(left, right);
            // 构造树节点
            TreeNode treeNode = new TreeNode(median.val);
            // 构造左右子树
            treeNode.left = generate(left, median);
            treeNode.right = generate(median.next, right);
            return treeNode;
        }
        // 需要新加 tail，因为这里不对链表做截断处理，所以需要标明取哪段链表的中点
        private static ListNode getMedian(ListNode head, ListNode tail) {
            ListNode slow = head;
            ListNode fast = head.next;
            while (fast != tail && fast.next != tail) {
                slow = slow.next;
                fast = fast.next.next;
            }
            return slow;
        }
    }
    ```
## 3. 📑108. 将有序数组转换为二叉搜索树
> ℹ️ 力扣（LeetCode）官网 - 全球极客挚爱的技术成长平台
> 备战技术面试？力扣提供海量技术面试资源，帮助你高效提升编程技能，轻松拿下世界 IT 名企 Dream Offer。
> [https://leetcode.cn/problems/convert-sorted-array-to-binary-search-tree/](https://leetcode.cn/problems/convert-sorted-array-to-binary-search-tree/)
1. 问题描述：

    ```Plain
    给你一个整数数组 nums ，其中元素已经按 升序 排列，请你将其转换为一棵 高度平衡 二叉搜索树。
    高度平衡 二叉树是一棵满足「每个节点的左右两个子树的高度差的绝对值不超过 1 」的二叉树
    ```
2. 代码：**中序遍历，总是选择中间位置左边的数字作为根节点**

    ```Java
     class Solution {
        public TreeNode sortedArrayToBST(int[] nums) {
            return generate(nums, 0, nums.length - 1);
        }
        private TreeNode generate(int[] nums, int left, int right) {
            if (left > right) return null;
            int mid = (right + left) / 2;
            TreeNode node = new TreeNode(nums[mid]);
            node.left = generate(nums, left, mid - 1);
            node.right = generate(nums, mid + 1, right);
            return node;
        }
    }
    ```
## 4. 📑96. 不同的二叉搜索树🔥
1. 问题描述：

    ```Plain
     给你一个整数 n ，求恰由 n 个节点组成且节点值从 1 到 n 互不相同的 二叉搜索树 有多少种？返回满足题意的二叉搜索树的种数。
    ```
2. 示例：

    ```Plain
    示例 1：
    输入：n = 3
    输出：5
    示例 2：
    输入：n = 1
    输出：1
    ```
3. 代码：
    1. 动态规划
    2. 数学：**卡特兰数**

        $$C0=1, Cn+1=\frac{2(2n+1)}{n+2}Cn$$

        ```Java
        public int numTrees(int n) {
            long c = 1;
            for (int i = 0; i < n; i++) {
                c = c * 2 * (2 * i + 1) / (i + 2);
            }
            return (int) c;
        }
        ```
## 5. 📑538. 把二叉搜索树转换为累加树🔥
> ℹ️ 力扣
> [https://leetcode.cn/problems/convert-bst-to-greater-tree/](https://leetcode.cn/problems/convert-bst-to-greater-tree/)
1. 问题描述：

    ```Plain
     给出二叉 搜索 树的根节点，该树的节点值各不相同，请你将其转换为累加树（Greater Sum Tree），使每个节点 node 的新值等于原树中大于或等于 node.val 的值之和。
    ```
2. 示例：

    [![|381](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2019/05/03/tree.png)](https://assets.leetcode-cn.com/aliyun-lc-upload/uploads/2019/05/03/tree.png)

    ```Plain
    示例 1：
    输入：[4,1,6,0,2,5,7,null,null,null,3,null,null,null,8]
    输出：[30,36,21,36,35,26,15,null,null,null,33,null,null,null,8]
    ```
3. 代码：
    - **利用 BST 中序遍历有序的性质，对树进行逆中序遍历，并记录之前所有值累加和，用以更新当前节点值**

    ```Java
    int sum = 0;
    public TreeNode convertBST(TreeNode root) {
        if (root == null) return null;
        InOrder(root);
        return root;
    }
    private void InOrder(TreeNode root) {
        // 递归出口
        if (root == null) return;
        // 逆中序遍历
        InOrder(root.right);
        root.val += sum;
        sum = root.val;
        InOrder(root.left);
    }
    ```
## 6. 📑剑指 Offer 33. 二叉搜索树的后序遍历序列⚔️
> ℹ️ 力扣
> [https://leetcode.cn/problems/er-cha-sou-suo-shu-de-hou-xu-bian-li-xu-lie-lcof/description/?favorite=xb9nqhhg](https://leetcode.cn/problems/er-cha-sou-suo-shu-de-hou-xu-bian-li-xu-lie-lcof/description/?favorite=xb9nqhhg)
1. 问题描述：

    ```Plain
     输入一个整数数组，判断该数组是不是某二叉搜索树的后序遍历结果。如果是则返回 true，否则返回 false。假设输入的数组的任意两个数字都互不相同。
    ```
2. 示例：

    ```Plain
    示例 1：
    输入: [1,6,3,2,5]
    输出: false
    ```
3. 利用 BST 后序遍历的特点解题
4. 代码：
    1. 递归分治：

        ```Java
         public static boolean verifyPostorder(int[] postorder) {
            return verifyPostorder(postorder, 0, postorder.length - 1);
        }
        public static boolean verifyPostorder(int[] postorder, int left, int right) {
            // 递归出口
            if (left >= right) return true;
            // postorder[right]即为当前根节点，从左向右找到第一个大于根节点的元素
            int p = left;
            while (postorder[p] < postorder[right]) {
                p++;
            }
            int m = p;
            // 判断当前位置后面是否有比根节点小的数
            while (postorder[p] > postorder[right]) {
                p++;
            }
            // 如果 p 走到头了，则表示以当前节点为根的序列符合 BST 的要求
            // 且还需左右子树都是 BST 才能返回 true
            return p == right && verifyPostorder(postorder, left, m - 1) && verifyPostorder(postorder, m, right - 1);
        }
        ```
    2. 单调栈：
        1. 找出一个 **`3，1，2`** 序列即返回 false
        2. 类比单调栈中的 `1，3，2` 序列题[[单调栈]]

        ```Java
        public static boolean verifyPostorder(int[] postorder) {
            Stack<Integer> stack = new Stack<>();
            int last = Integer.MAX_VALUE;
            for(int i = postorder.length - 1; i >= 0; i--) {
        				// 发现（3，1，2）
                if(postorder[i] > last) return false;
                // 把所有栈中大的都弹出，root 保存比当前元素大的中最小的（1，2）
                while(!stack.isEmpty() && stack.peek() > postorder[i])
                    last = stack.pop();
                // 当前元素入栈
                stack.add(postorder[i]);
            }
            return true;
        }
        ```
## 7. 📑剑指 Offer 36. 二叉搜索树与双向链表⚔️
> ℹ️ 力扣
> [https://leetcode.cn/problems/er-cha-sou-suo-shu-de-di-kda-jie-dian-lcof/?favorite=xb9nqhhg](https://leetcode.cn/problems/er-cha-sou-suo-shu-de-di-kda-jie-dian-lcof/?favorite=xb9nqhhg)
1. 问题描述：

    ```Plain
     输入一棵二叉搜索树，将该二叉搜索树转换成一个排序的循环双向链表。要求不能创建任何新的节点，只能调整树中节点指针的指向。
    ```
2. 示例：

    ![[IMG-20260620200017840.png|295]]

    [![|585](https://assets.leetcode.com/uploads/2018/10/12/bstdllreturndll.png)](https://assets.leetcode.com/uploads/2018/10/12/bstdllreturndll.png)

3. 代码：**中序遍历 + 保存上一个遍历到的元素**

    ```Java
    Node pre, head;
    public Node treeToDoublyList(Node root) {
        if (root == null) return null;
        inOrder(root);
        // 最后还需形成循环链表
        pre.right = head;
        head.left = pre;
        return head;
    }
    private void inOrder(Node cur) {
        if (cur == null) return;
        inOrder(cur.left);
        // pre 即为中序遍历中上一个遍历到的数
        if (pre != null) {
            pre.right = cur;
        } else {
            head = cur;
        }
        cur.left = pre;
        // 更新 pre
        pre = cur;
        inOrder(cur.right);
    }
    ```
## 8. 📑剑指 Offer 54. 二叉搜索树的第k大节点⚔️
1. 问题描述：

    ```Plain
     给定一棵二叉搜索树，请找出其中第 k 大的节点的值。
    ```
2. 示例：

    ```Plain
    示例 1:
    输入: root = [3,1,4,null,2], k = 1
       3
      / \
     1   4
      \
       2
    输出: 4
    ```
3. 代码：**逆中序遍历**

    ```Java
    int count = 0;
    int res = 0;
    public int kthLargest(TreeNode root, int k) {
        count = k;
        inOrder(root);
        return res;
    }
    private void inOrder(TreeNode cur) {
        if (cur == null) return;
        inOrder(cur.right);
        count--;
        if (count == 0) {
            res = cur.val;
        }
        inOrder(cur.left);
    }
    ```
## 9. 📑剑指 Offer 68 - I. 二叉搜索树的最近公共祖先⚔️
> ℹ️ 力扣
> [https://leetcode.cn/problems/er-cha-sou-suo-shu-de-zui-jin-gong-gong-zu-xian-lcof/?favorite=xb9nqhhg](https://leetcode.cn/problems/er-cha-sou-suo-shu-de-zui-jin-gong-gong-zu-xian-lcof/?favorite=xb9nqhhg)
1. 问题描述：

    ```Plain
    给定一个二叉搜索树, 找到该树中两个指定节点的最近公共祖先。
    百度百科中最近公共祖先的定义为：“对于有根树 T 的两个结点 p、q，最近公共祖先表示为一个结点 x，满足 x 是 p、q 的祖先且 x 的深度尽可能大（一个节点也可以是它自己的祖先）。”
    例如，给定如下二叉搜索树:  root = [6,2,8,0,4,7,9,null,null,3,5]
    ```
2. 示例：

    ```Plain
    示例 1:
    输入: root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 8
    输出: 6 
    解释: 节点 2 和节点 8 的最近公共祖先是 6。
    ```
3. 代码：