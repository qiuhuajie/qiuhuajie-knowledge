- [[#一、算法介绍]]
- [[#二、树 BFS]]
    - [[#1. 📑111. 二叉树的最小深度]]
    - [[#2. 📑剑指 Offer 32 - I. 从上到下打印二叉树⚔️]]
    - [[#3. 📑107. 二叉树的层序遍历 II（反向的：剑指 Offer 32 - II. 从上到下打印二叉树 II⚔️）]]
    - [[#4. 📑103. 二叉树的锯齿形层序遍历（剑指 Offer 32 - III. 从上到下打印二叉树 III⚔️）]]
    - [[#5. 📑117. 填充每个节点的下一个右侧节点指针 II]]
    - [[#6. 📑100. 相同的树]]
    - [[#7. 📑剑指 Offer 28. 对称的二叉树⚔️]]
- [[#三、矩阵数组 BFS]]
    - [[#1. 📑994. 腐烂的橘子🔥]]
    - [[#2. 📑207. 课程表🔥]]
    - [[#3. 📑752. 打开转盘锁]]
- [[#四、双向 BFS]]
# 一、算法介绍
1. 广度优先遍历呈现出「一层一层向外扩张」的特点，**先看到的结点先遍历，后看到的结点后遍历**，因此「广度优先遍历」可以借助「队列」实现
2. 核心思想：
    1. 把问题抽象成一张图，从每一个点开始，向外扩散
    2. 一般来说，BFS 算法都需要借助 队列 实现，每次将一个节点周围的所有节点加入队列
3. BFS 相较 DFS 的主要区别就是：
    - ==**BFS 找到的路径一定是最短的**==**，但代价是空间复杂度比 DFS 大很多**
    - 例如，给一个满二叉树遍历，节点数是 N
        - 对于 DFS 来说空间复杂度就是递归栈的深度，在最坏情况下最多就是树的深度，也即$O(logN)$
        - 但是对于 BFS 来说，队列每次都会存储一个树中一层的节点，在最坏情况下空间复杂度是树的最下层节点的数量，也就是 $N/2$，即 $O(N)$
    - 故一般来说，在找最短路径时使用 BFS，其他时候还是 DFS 用的多一些（且 DFS 是递归，代码更好写）
4. BFS 最常见的场景就是：**在一副 “图” 中，找到起点 start 和 终点 target 的最近距离**
    - 走迷宫，起点到终点的最短距离
    - 两个单词，通过替换，将一个变成另一个，要替换几次
    - 连连看
5. **BFS 算法模板**

    ```Java
    public List<List<Integer>> levelOrderBottom(TreeNode start, TreeNode target) {
        // 定义队列，核心数据结构
        Queue<TreeNode> queue = new LinkedList<>();
        // 避免走回头路（在二叉树相关问题中，没有子到父的指针，故这个用不到）
        HashSet<TreeNode> visited = new HashSet<>();
        // 将起点入队
        queue.offer(start);
        visited.add(start);
        // 记录扩散步数
        int step = 0;
        while (!queue.isEmpty()) {
    				// 这里一定要提前保存 levelSize 这个大小量，queue.size() 是会变的不能在 for 里直接用⭐
            int levelSize = queue.size();
            // 将当前队列中的所有节点向四周扩散，加了一层 for 循环，可以保证此时队列中的元素只包含下一层的全部元素
            for (int i = 0; i < levelSize; i++) {
    						// 注意：在 for 循环中，取出队头元素
                TreeNode cur = queue.poll();
                // 判断是否到达了终点
                if (cur is target) {
                    return step;
                }
                // 将 cur 的相邻节点加入队列
                for (TreeNode x : cur.adj()) {
                    if (x not in visited) {
                        queue.offer(x);
                        visited.add(x);
                    }
                }
            }
            step++;
        }
    }
    ```
# 二、树 BFS
## 1. 📑111. 二叉树的最小深度
> ℹ️ 力扣
> [https://leetcode.cn/problems/minimum-depth-of-binary-tree/](https://leetcode.cn/problems/minimum-depth-of-binary-tree/)
1. 问题描述：

    ```Plain
    给定一个二叉树，找出其最小深度。
    最小深度是从根节点到最近叶子节点的最短路径上的节点数量。
    说明：叶子节点是指没有子节点的节点。
    ```
2. 示例：

    ```Plain
    示例 1：
    输入：root = [3,9,20,null,null,15,7]
    输出：2
    示例 2：
    输入：root = [2,null,3,null,4,null,5,null,6]
    输出：5
    ```
3. 代码：

    ```Java
     public int minDepth(TreeNode root) {
        // 空处理
        if (root == null) return 0;
        // 定义队列
        Queue<TreeNode> queue = new LinkedList<>();
        // 根节点入队
        queue.offer(root);
        // 根节点本身就算一层
        int depth = 1;
        while (!queue.isEmpty()) {
            // 加了一层 for 循环，可以保证此时队列中的元素只包含下一层的全部元素⭐
            int curSize = queue.size();
            // 将当前队列中的所有节点向周围扩散
            for (int i = 0; i < curSize; i++) {
                TreeNode cur = queue.poll();
                // 判断是否到达终点
                if (cur.left == null && cur.right == null) {
                    return depth;
                }
                // 将 cur 的相邻节点入队
                if (cur.left != null) {
                    queue.offer(cur.left);
                }
                if (cur.right != null) {
                    queue.offer(cur.right);
                }
            }
            // 遍历完一层的所有节点后，深度 + 1
            depth++;
        }
        return depth;
    }
    ```
## 2. 📑剑指 Offer 32 - I. 从上到下打印二叉树⚔️
1. 问题描述：

    ```Plain
     从上到下打印出二叉树的每个节点，同一层的节点按照从左到右的顺序打印。
    ```
2. 示例：

    ```Plain
     层序遍历
    ```
3. 代码：**==在 leetcode 网站直接写，编写不习惯，还是有很多注意不到的编译错误==**

    ![[IMG-20260620204023015.png|Untitled 27.png|415]]

    ![[IMG-20260620204023109.png|430]]

## 3. 📑107. 二叉树的层序遍历 II（反向的：剑指 Offer 32 - II. 从上到下打印二叉树 II⚔️）
> ℹ️ 力扣
> [https://leetcode.cn/problems/binary-tree-level-order-traversal-ii/](https://leetcode.cn/problems/binary-tree-level-order-traversal-ii/)
1. 问题描述：

    ```Plain
     给你二叉树的根节点 root ，返回其节点值 自底向上的层序遍历 。 （即按从叶子节点所在层到根节点所在的层，逐层从左向右遍历）
    ```
2. 示例：

    ```Plain
    示例 1：
    输入：root = [3,9,20,null,null,15,7]
    输出：[[15,7],[9,20],[3]]
    示例 2：
    输入：root = [1]
    输出：[[1]]
    示例 3：
    输入：root = []
    输出：[]
    ```
3. 代码：==**这里按 BFS 模板写的**== ==**`fori`**== ==**能很好感知什么时候当前层结束**==

    ```Java
     public List<List<Integer>> levelOrderBottom(TreeNode root) {
            Queue<TreeNode> queue = new LinkedList<>();
            LinkedList<List<Integer>> res = new LinkedList<>();
            if (root == null) return res;
            queue.offer(root);
            while (!queue.isEmpty()) {
                ArrayList<Integer> list = new ArrayList<>();
                int levelSize = queue.size();
                for (int i = 0; i < levelSize; i++) {
                    TreeNode cur = queue.poll();
                    // BFS 的同时记录当前层的 list
                    list.add(cur.val);
                    if (cur.left != null) {
                        queue.offer(cur.left);
                    }
                    if (cur.right != null) {
                        queue.offer(cur.right);
                    }
                }
                res.addFirst(list);
            }
            return res;
        }
    ```
## 4. 📑103. 二叉树的锯齿形层序遍历（剑指 Offer 32 - III. 从上到下打印二叉树 III⚔️）
> ℹ️ 力扣
> [https://leetcode.cn/problems/binary-tree-zigzag-level-order-traversal/](https://leetcode.cn/problems/binary-tree-zigzag-level-order-traversal/)
1. 问题描述：

    ```Plain
     给你二叉树的根节点 root ，返回其节点值的 锯齿形层序遍历 。（即先从左往右，再从右往左进行下一层遍历，以此类推，层与层之间交替进行）。
    ```
2. 示例：

    ```Plain
    示例 1：
    输入：root = [3,9,20,null,null,15,7]
    输出：[[3],[20,9],[15,7]]
    示例 2：
    输入：root = [1]
    输出：[[1]]
    示例 3：
    输入：root = []
    输出：[]
    ```
3. 代码：

    ```Java
     public List<List<Integer>> zigzagLevelOrder(TreeNode root) {
        Queue<TreeNode> queue = new LinkedList<>();
        List<List<Integer>> res = new ArrayList<>();
        if (root == null) return res;
        int depth = 0;
        queue.offer(root);
        while (!queue.isEmpty()) {
            // 由于要正向添加和反向添加，所以用双端list保存每层的元素值
            LinkedList<Integer> list = new LinkedList<>();
            int size = queue.size();
            for (int i = 0; i < size; i++) {
                TreeNode cur = queue.poll();
                // 在对树 BFS 的同时，锯齿状填充 list⭐
                if (depth % 2 == 0) {
                    list.addLast(cur.val);
                } else {
                    list.addFirst(cur.val);
                }
                if (cur.left != null) {
                    queue.offer(cur.left);
                }
                if (cur.right != null) {
                    queue.offer(cur.right);
                }
            }
            res.add(list);
            depth++;
        }
        return res;
    }
    ```
## 5. 📑117. 填充每个节点的下一个右侧节点指针 II
1. 问题描述：

    ```Plain
    填充它的每个 next 指针，让这个指针指向其下一个右侧节点。如果找不到下一个右侧节点，则将 next 指针设置为 NULL 。
    初始状态下，所有 next 指针都被设置为 NULL 。
    ```
2. 示例：

    ![[IMG-20260620204023193.png|573]]

3. 代码：

    ![[IMG-20260620204023267.png|420]]

## 6. 📑100. 相同的树
> ℹ️ 力扣
> [https://leetcode.cn/problems/same-tree/description/](https://leetcode.cn/problems/same-tree/description/)
1. 问题描述：

    ```Plain
    给你两棵二叉树的根节点 p 和 q ，编写一个函数来检验这两棵树是否相同。
    如果两个树在结构上相同，并且节点具有相同的值，则认为它们是相同的。
    ```
2. 示例：

    ```Plain
    示例 1：
    输入：p = [1,2,3], q = [1,2,3]
    输出：true
    示例 2：
    输入：p = [1,2], q = [1,null,2]
    输出：false
    示例 3：
    输入：p = [1,2,1], q = [1,1,2]
    输出：false
    ```
3. 代码：

    ```Java
     public boolean isSameTree(TreeNode p, TreeNode q) {
            if (p == null && q == null) {
                return true;
            }
            if (p == null || q == null){
                return false;
            }
            Queue<TreeNode> queue1 = new LinkedList();
            Queue<TreeNode> queue2 = new LinkedList();
            queue1.offer(p);
            queue2.offer(q);
            while (!queue1.isEmpty() && !queue2.isEmpty()) {
                TreeNode curr1 = queue1.poll();
                TreeNode curr2 = queue2.poll();
                if (curr1.val != curr2.val) {
                    return false;
                }
                if (curr1.left != null && curr2.left == null) {
                    return false;
                }
                if (curr1.right != null && curr2.right == null) {
                    return false;
                }
                if (curr2.left != null && curr1.left == null) {
                    return false;
                }
                if (curr2.right != null && curr1.right == null) {
                    return false;
                }
                if (curr1.left != null) {
                    queue1.offer(curr1.left);
                }
                if (curr1.right != null) {
                    queue1.offer(curr1.right);
                }
                if (curr2.left != null) {
                    queue2.offer(curr2.left);
                }
                if (curr2.right != null) {
                    queue2.offer(curr2.right);
                }
            }
            return true;
        }
    ```
## 7. 📑剑指 Offer 28. 对称的二叉树⚔️
1. 问题描述：

    ```Plain
    请实现一个函数，用来判断一棵二叉树是不是对称的。如果一棵二叉树和它的镜像一样，那么它是对称的。
    例如，二叉树 [1,2,2,3,4,4,3] 是对称的。
        1
       / \
      2   2
     / \ / \
    3  4 4  3
    但是下面这个 [1,2,2,null,3,null,3] 则不是镜像对称的:
        1
       / \
      2   2
       \   \
       3    3
    ```
2. 代码：
    - 递归
        ![[IMG-20260620204023356.png|Untitled 4 6.png|804]]
        ```Java
        public boolean isSymmetric(TreeNode root) {
            return process(root, root);
        }
        private boolean process(TreeNode node1, TreeNode node2) {
            if (node1 == null && node2 == null) return true;
            if (node1 == null || node2 == null) return false;
            return node1.val == node2.val && process(node1.left, node2.right) && process(node1.right, node2.left);
        }
        ```
    - 层序遍历
        - 对数做两次层序遍历，一个从左往右向队列中加元素，一个从右往左向队列中加元素，将层序遍历的结果记录在两个 list 中，最后比较两个 list 是否相同
        - 优化：可以使用一个队列来层序遍历，且直接在出队时就比较元素，也省去记录的 list
            ![[IMG-20260620204023403.png|Untitled 5 6.png|388]]
        ```Java
         public boolean isSymmetric(TreeNode root) {
            LinkedList<TreeNode> queue = new LinkedList<>();
            queue.add(root);
            queue.add(root);
            while (!queue.isEmpty()) {
                for (int i = 0; i < queue.size(); i++) {
                    TreeNode l = queue.poll();
                    TreeNode r = queue.poll();
                    if (l == null && r == null) {
                        continue;
                    }
                    if (l == null || r == null) {
                        return false;
                    }
                    if (l.val != r.val) {
                        return false;
                    }
                    queue.offer(l.left);
                    queue.offer(r.right);
                    queue.offer(l.right);
                    queue.offer(r.left);
                }
            }
            return true;
        }
        ```
# 三、矩阵数组 BFS
## 1. 📑994. 腐烂的橘子🔥
> ℹ️ 力扣（LeetCode）官网 - 全球极客挚爱的技术成长平台
> 备战技术面试？力扣提供海量技术面试资源，帮助你高效提升编程技能，轻松拿下世界 IT 名企 Dream Offer。
> [https://leetcode.cn/problems/rotting-oranges/](https://leetcode.cn/problems/rotting-oranges/)
1. 问题描述：

    ```Plain
     在给定的 m x n 网格 grid 中，每个单元格可以有以下三个值之一：
    值 0 代表空单元格；
    值 1 代表新鲜橘子；
    值 2 代表腐烂的橘子。
    每分钟，腐烂的橘子 周围 4 个方向上相邻 的新鲜橘子都会腐烂。
    返回 直到单元格中没有新鲜橘子为止所必须经过的最小分钟数。如果不可能，返回 -1 。
    ```
2. 示例：

    ![[IMG-20260620204023444.png|Untitled 6 6.png|649]]

3. 代码：

    ```Java
     public class OrangesRotting {
        public int orangesRotting(int[][] grid) {
            Queue<String> queue = new LinkedList<>();
            HashMap<String, Integer> count = new HashMap<>();
            int row = grid.length;
            int col = grid[0].length;
            int res = 0;
            // 先把所有腐烂的橘子入队，类比树层序遍历的头结点入队
            for (int i = 0; i < row; i++) {
                for (int j = 0; j < col; j++) {
                    if (grid[i][j] == 2) {
                        queue.add(i + "-" + j);
                        count.put(i + "-" + j, 0);
                    }
                }
            }
            // 依此去除对头元素，将其四周的橘子腐烂
            // 同时，用 map 记录每个位置腐烂时的时间
            while (!queue.isEmpty()) {
                String cur = queue.poll();
                String[] split = cur.split("-");
                int r = Integer.parseInt(split[0]);
                int c = Integer.parseInt(split[1]);
                if (check(grid, r - 1, c) && grid[r - 1][c] == 1) {
                    grid[r - 1][c] = 2;
                    queue.add((r - 1) + "-" + c);
                    count.put((r - 1) + "-" + c, count.getOrDefault(cur, 0) + 1);
                }
                if (check(grid, r + 1, c) && grid[r + 1][c] == 1) {
                    grid[r + 1][c] = 2;
                    queue.add((r + 1) + "-" + c);
                    count.put((r + 1) + "-" + c, count.getOrDefault(cur, 0) + 1);
                }
                if (check(grid, r, c - 1) && grid[r][c - 1] == 1) {
                    grid[r][c - 1] = 2;
                    queue.add(r + "-" + (c - 1));
                    count.put(r + "-" + (c - 1), count.getOrDefault(cur, 0) + 1);
                }
                if (check(grid, r, c + 1) && grid[r][c + 1] == 1) {
                    grid[r][c + 1] = 2;
                    queue.add(r + "-" + (c + 1));
                    count.put(r + "-" + (c + 1), count.getOrDefault(cur, 0) + 1);
                }
                res = count.get(r + "-" + (c + 1));
            }
            // 判断能不能将全部橘子腐烂
            for (int[] R: grid) {
                for (int C: R) {
                    if (C == 1) {
                        return -1;
                    }
                }
            }
            return res;
        }
        boolean check(int[][] grid, int i, int j) {
            if (i < 0 || j <0 || i >= grid.length || i >= grid[0].length) {
                return false;
            }
            return true;
        }
    }
    ```
## 2. 📑207. 课程表🔥
1. 问题描述：

    ```Plain
    你这个学期必须选修 numCourses 门课程，记为 0 到 numCourses - 1 。
    在选修某些课程之前需要一些先修课程。 先修课程按数组 prerequisites 给出，其中 prerequisites[i] = [ai, bi] ，表示如果要学习课程 ai 则 必须 先学习课程  bi 。
    例如，先修课程对 [0, 1] 表示：想要学习课程 0 ，你需要先完成课程 1 。
    请你判断是否可能完成所有课程的学习？如果可以，返回 true ；否则，返回 false 。
    ```
2. 示例：

    ```Plain
    示例 1：
    输入：numCourses = 2, prerequisites = [[1,0]]
    输出：true
    解释：总共有 2 门课程。学习课程 1 之前，你需要完成课程 0 。这是可能的。
    示例 2：
    输入：numCourses = 2, prerequisites = [[1,0],[0,1]]
    输出：false
    解释：总共有 2 门课程。学习课程 1 之前，你需要先完成课程 0 ；并且学习课程 0 之前，你还应先完成课程 1 。这是不可能的。
    ```
3. 代码：

    ![[IMG-20260620204023482.png|Untitled 7 6.png|486]]

    ```Java
     public boolean canFinish(int numCourses, int[][] prerequisites) {
        // 构建一个入度表
        int[] inDegree = new int[numCourses];
        // 构建邻接图
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < numCourses; i++) {
            graph.add(new ArrayList<>());
        }
        for (int[] p : prerequisites) {
            graph.get(p[1]).add(p[0]);
            // 初始化入度表
            inDegree[p[0]]++;
        }
        Queue<Integer> queue = new LinkedList<>();
        // 将当前入度为 0 的节点入队
        for (int i = 0; i < numCourses; i++) {
            if (inDegree[i] == 0) {
                queue.add(i);
            } 
        }
        // bfs
        while (!queue.isEmpty()) {
            // 取出当前节点
            Integer cur = queue.poll();
            // 将当前节点移除
            numCourses--;
            // 相邻节点入队
            for (Integer adj : graph.get(cur)) {
                // 当前节点移除后，还要将当前节点指向的所有节点的入度 - 1
                inDegree[adj]--;
                // 将入度 -1 后，入度变为 0 的相邻节点入队
                if (inDegree[adj] == 0) {
                    queue.add(adj);
                }
            }
        }
        // numCourses 为 0 表示所有节点都能移除，拓扑排序完成
        return numCourses == 0;
    }
    ```
## 3. 📑752. 打开转盘锁
> ℹ️ 力扣
> [https://leetcode.cn/problems/open-the-lock/](https://leetcode.cn/problems/open-the-lock/)
1. 问题描述：

    ```Plain
    你有一个带有四个圆形拨轮的转盘锁。每个拨轮都有10个数字： '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' 。每个拨轮可以自由旋转：例如把 '9' 变为 '0'，'0' 变为 '9' 。每次旋转都只能旋转一个拨轮的一位数字。
    锁的初始数字为 '0000' ，一个代表四个拨轮的数字的字符串。
    列表 deadends 包含了一组死亡数字，一旦拨轮的数字和列表里的任何一个元素相同，这个锁将会被永久锁定，无法再被旋转。
    字符串 target 代表可以解锁的数字，你需要给出解锁需要的最小旋转次数，如果无论如何不能解锁，返回 -1 。
    ```
2. 示例：
	```Plain
	示例 1:
	输入：deadends = ["0201","0101","0102","1212","2002"], target = "0202"
	输出：6
	解释：
	可能的移动序列为 "0000" -> "1000" -> "1100" -> "1200" -> "1201" -> "1202" -> "0202"。
	注意 "0000" -> "0001" -> "0002" -> "0102" -> "0202" 这样的序列是不能解锁的，
	因为当拨动到 "0102" 时这个锁就会被锁定。
	示例 2:
	输入: deadends = ["8888"], target = "0009"
	输出：1
	解释：把最后一位反向旋转一次即可 "0000" -> "0009"。
	示例 3:
	输入: deadends = ["8887","8889","8878","8898","8788","8988","7888","9888"], target = "8888"
	输出：-1
	解释：无法旋转到目标数字且不被锁定。
	```
3. 代码：

# 四、双向 BFS

**📑**

1. 问题描述：
2. 示例：
3. 代码：