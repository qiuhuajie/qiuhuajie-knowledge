# DFS 算法
- [[#📑200. 岛屿数量🔥]]
- [[#📑剑指 Offer 13. 机器人的运动范围⚔️]]
- [[#📑79. 单词搜索🔥⚔️]]
## **📑200. 岛屿数量**🔥
1. 问题描述：
    
    ```Plain
    给你一个由 '1'（陆地）和 '0'（水）组成的的二维网格，请你计算网格中岛屿的数量。
    
    岛屿总是被水包围，并且每座岛屿只能由水平方向和/或竖直方向上相邻的陆地连接形成。
    
    此外，你可以假设该网格的四条边均被水包围。
    ```
    
1. 示例：
    
    ```Plain
    示例 1：
    输入：grid = [
      ["1","1","1","1","0"],
      ["1","1","0","1","0"],
      ["1","1","0","0","0"],
      ["0","0","0","0","0"]
    ]
    输出：1
    ```
    
1. 代码：
    
    - 如何避免重复遍历？：标记已经遍历过的格子
        
        - 0 —— 海洋格子
        
        - 1 —— 陆地格子（未遍历过）
        
        - 2 —— 陆地格子（已遍历过）
        
    
    ```Java
    int res = 0;
    int m = 0;
    int n = 0;
    
    public int numIslands(char[][] grid) {
        m = grid.length;
        n = grid[0].length;
    
        for (int k = 0; k < m; k++) {
            for (int l = 0; l < n; l++) {
                if (grid[k][l] == '1') {
                    dfs(grid, k, l);
                    res++;
                }
            }
        }
        return res;
    }
    
    private void dfs(char[][] grid, int i, int j) {
    
        // 判断当前位置是否合法
        if (!inArea(grid, i, j)) {
            return;
        }
    
        // 如果当前位置为 0 或者被访问过为2 则直接返回
        if (!(grid[i][j] == '1')){
            return;
        }
    
        // 将访问过的位置置为 2
        grid[i][j] = '2';
    
        // 访问四个相邻节点
        dfs(grid, i , j - 1);
        dfs(grid, i , j + 1);
        dfs(grid, i + 1, j);
        dfs(grid, i - 1, j);
    }
    
    // 位置合法检验
    private boolean inArea(char[][] grid, int i, int j) {
        if (i < 0 || i >= m || j < 0 || j >= n) {
            return false;
        }
        return true;
    }
    ```
    
## **📑剑指 Offer 13. 机器人的运动范围**⚔️
1. 问题描述：
    
    ```Plain
     地上有一个m行n列的方格，从坐标 [0,0] 到坐标 [m-1,n-1] 。一个机器人从坐标 [0, 0] 的格子开始移动，它每次可以向左、右、上、下移动一格（不能移动到方格外），也不能进入行坐标和列坐标的数位之和大于k的格子。例如，当k为18时，机器人能够进入方格 [35, 37] ，因为3+5+3+7=18。但它不能进入方格 [35, 38]，因为3+5+3+8=19。请问该机器人能够到达多少个格子？
    ```
    
1. 示例：
    
    ```Plain
    示例 1：
    输入：m = 2, n = 3, k = 1
    输出：3
    
    示例 2：
    输入：m = 3, n = 1, k = 0
    输出：1
    ```
    
1. 代码：
    
    ```Java
     public class MovingCount {
    
        int res = 0;
        public int movingCount(int m, int n, int k) {
            int[][] ints = new int[m][n];
            dfs(ints, m, n, 0, 0, k);
            return res;
        }
    
        private void dfs(int[][] ints, int m, int n, int i, int j, int k) {
            if (!check(m, n, i, j, k) || ints[i][j] == 1) {
                return;
            }
    
            ints[i][j] = 1;
            res++;
    
            dfs(ints, m, n, i + 1, j, k);
            dfs(ints, m, n, i - 1, j, k);
            dfs(ints, m, n, i, j + 1, k);
            dfs(ints, m, n, i, j - 1, k);
        }
    
        private boolean check(int m, int n, int i, int j, int k) {
            if (i >= m || i < 0 || j >= n || j < 0) {
                return false;
            }
    
            char[] ci = String.valueOf(i).toCharArray();
            char[] cj = String.valueOf(j).toCharArray();
            int tmp = 0;
    
            for (char c : ci) {
                tmp += c - '0';
            }
            for (char c : cj) {
                tmp += c - '0';
            }
            return tmp <= k;
        }
    }
    ```
    
      
    
## **📑79. 单词搜索**🔥⚔️

> [!info] 力扣  
> 
> [https://leetcode.cn/problems/word-search/?favorite=2cktkvj](https://leetcode.cn/problems/word-search/?favorite=2cktkvj)  
1. 问题描述：
    
    ```Plain
    给定一个 m x n 二维字符网格 board 和一个字符串单词 word 。如果 word 存在于网格中，返回 true ；否则，返回 false 。
    
    单词必须按照字母顺序，通过相邻的单元格内的字母构成，其中“相邻”单元格是那些水平相邻或垂直相邻的单元格。同一个单元格内的字母不允许被重复使用。
    ```
    
1. 示例：
    
    ```Plain
    输入：board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
    输出：true
    ```
    
1. 代码：
    
    ```Java
    int len = 0;
    public boolean exist(char[][] board, String word) {
        len = word.length();
        int n = board.length;
        int m = board[0].length;
    
        // 遍历所有起始寻找点
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (dfs(board, i, j, word, 0)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    private boolean dfs(char[][] board, int i, int j, String word, int depth) {
    
        // 检查边界 以及 是否和 word 对应位置上的字符匹配
        if (!check(board, i, j) || board[i][j] != word.charAt(depth)) {
            return false;
        }
    
        // 如果字符匹配，且已经匹配到 word 的最后一个字符，则匹配成功
        if (depth == len - 1) {
            return true;
        }
    
        // 将遍历过的位置置为空
        board[i][j] = '\0';
    
        boolean dfs1 = dfs(board, i - 1, j, word, depth + 1);
        boolean dfs2 = dfs(board, i + 1, j, word, depth + 1);
        boolean dfs3 = dfs(board, i, j - 1, word, depth + 1);
        boolean dfs4 = dfs(board, i, j + 1, word, depth + 1);
    
        // 当前位置为起始点的 dfs 完后，要将该位置恢复
        board[i][j] = word.charAt(depth);
    
        // 只要四个方向能匹配到一个就算匹配成功
        return dfs1 || dfs2 || dfs3 || dfs4;
    }
    
    boolean check(char[][] board, int i, int j) {
        int m = board.length;
        int n = board[0].length;
    
        if (i < 0 || i >= m || j < 0 || j >= n) {
            return false;
        }
        return true;
    }
    ```