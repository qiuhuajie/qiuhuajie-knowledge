- [[#1. 概念]]
    - [[#1.1 Git概念汇总]]
    - [[#1.2 工作区/暂存区/仓库]]
    - [[#1.3 Git 基本流程]]
    - [[#1.4 Git 状态]]
- [[#2. 安装]]
    - [[#2.1 Git 的配置文件]]
    - [[#2.2 安装]]
- [[#3. 使用]]
    - [[#3.1 本地仓库相操作关]]
        - [[#创建本地仓库]]
        - [[#暂存区 add]]
        - [[#提交 commit-记录]]
        - [[#Git 的“指针”引用们 ⭐]]
        - [[#比较 diff]]
    - [[#3.2 远程仓库操作相关]]
        - [[#远程登陆]]
        - [[#推送 push / 拉取 pull]]
    - [[#3.3 分支操作相关]]
        - [[#合并 merge & 冲突]]
        - [[#变基 rebase]]
    - [[#3.4 撤销变更操作]]
        - [[#回退版本 reset]]
        - [[#撤销提交 revert]]
        - [[#checkout/reset/revert 总结⭐]]
# 1. 概念
## 1.1 **Git概念汇总**
![[IMG-20260412093954610.png|Untitled 11.png|460]]
## 1.2 **工作区/暂存区/仓库**
1. 工作区、暂存区、版本库是Git最基本的概念，关系如下图：

    ![[IMG-20260412093954708.png|Untitled 1 4.png|512]]
2. 名词解释：
    1. **🔸工作区**（Workspace）
        1. 就是在电脑里能看到的代码库目录，是我们搬砖的地方，新增、修改的文件会提交到暂存区
        2. 在这里新增文件、修改文件内容，或删除文件
    2. **🔸暂存区**（stage 或 index）
        1. 用于临时存放文件的修改，实际上上它只是一个文件（.git/index），保存待提交的文件列表信息
        2. 用 `git add` 命令将工作区的修改保存到暂存区
    3. **🔸版本库/仓库**（Repository 仓库）
        1. Git的管理仓库，管理版本的数据库，记录文件/目录状态的地方，所有内容的修改记录（版本）都在这里
        2. 就是工作区目录下的隐藏文件夹`.git`，包含暂存区、分支、历史记录等信息
        3. 用`git commit` 命令将暂存区的内容正式提交到版本库
        4. `master` 为仓库的默认分支`master`，**HEAD** 是一个“指针”指向当前分支的最新提交，默认指向最新的`master`
3. 如下图，为对应**本地仓库目录的结构关系**
    ![[IMG-20260412093954773.png|Untitled 2 4.png|699]]
    - `KWebNote`为项目目录，也就是 Git 工作区
    - 项目根目录下隐藏的`.git`目录就是Git仓库目录了，存放了所有Git管理的信息
    - `.git/config` 为该仓库的配置文件，可通过指令修改或直接修改
    - `index` 文件就是存放的暂存区内容

## 1.3 **Git 基本流程**
![[IMG-20260412093954839.png|Untitled 3 4.png|701]]
- **`git commit -a`**指令省略了`add`到暂存区的步骤，直接**提交**工作区的修改内容到版本库，不包括新增的文件
- **`git fetch`**、**`git pull`** 都是从远程服务端**获取最新记录**，区别是`git pull`多了一个步骤，就是自动合并更新工作区
- **`git checkout .`**、**`git checkout [file]`** 会清除**工作区**中未添加到暂存区的修改，用暂存区内容替换工作区
- **`git checkout HEAD .`**、**`git checkout HEAD [file]`** 会清除**工作区**、**暂存区**的修改，用HEAD指向的当前分支最新版本替换暂存区、工作区
- **`git diff`** 用来**对比**不同部分之间的区别，如暂存区、工作区，最新版本与未提交内容，不同版本之间等
- **`git reset`**是专门用来**撤销修改、回退版本**的指令，替代上面`checkout`的撤销功能
## 1.4 **Git 状态**
![[IMG-20260412093954923.png|Untitled 4 3.png|667]]
- 未跟踪（untracked）：新添加的文件，或被移除跟踪的文件，未建立跟踪，通过 `git add` 添加暂存并建立跟踪
- 未修改：从仓库签出的文件默认状态，修改后就是“已修改”状态了
- **已修改**（modified）：文件被修改后的状态
- **已暂存**（staged）：修改、新增的文件添加到暂存区后的状态
- **已提交**(committed)：从暂存区提交到版本库
# 2. 安装
## 2.1 **Git 的配置文件**
![[IMG-20260412093955004.png|Untitled 5 3.png|615]]
- Git 有三个主要的配置文件：三个配置文件的优先级是**① < ② < ③**
    - **① 系统全局配置**(--system)：
        - 包含了适用于系统所有用户和所有仓库（项目）的配置信息
        - 存放在Git安装目录下`C:\Program Files\Git\etc\gitconfig`
    - **② 用户全局配置**(--system)：
        - 当前系统用户的全局配置
        - 存放用户目录：`C:\Users\[系统用户名]\.gitconfig`
    - **③ 仓库/项目配置**(--local)：
        - 仓库（项目）的特定配置
        - 存放在项目目录下`.git/config`
- **最终仓库的配置是上面多个配置的集合**
## 2.2 安装
1. Git官网：下载安装包进行安装
    > [!info] Git
    > Git is a free and open source
    > [https://www.git-scm.com/](https://www.git-scm.com/)
2. ⭐**配置-初始化用户**

    ```Bash
    $ git config --global user.name "Your Name"
    $ git config --global user.email "email@example.com"
    # 配置完后，看看用户配置文件：
    $ cat 'C:\Users\Kwongad\.gitconfig'
    [user]
            name = Kanding
            email = 123anding@163.com
    ```
3. ⭐**配置-忽略.gitignore**
    1. 示例：

        ```Bash
        \#为注释
        *.txt \#忽略所有“.txt”结尾的文件
        !lib.txt \#lib.txt除外
        /temp \#仅忽略项目根目录下的temp文件,不包括其它目录下的temp，如不包括“src/temp”
        build/ \#忽略build/目录下的所有文件
        doc/*.txt \#会忽略 doc/notes.txt 但不包括 doc/server/arch.txt
        ```
    2. 各种语言项目的常用`.gitignore`文件配置：

        https://github.com/github/gitignore
# 3. 使用
## 3.1 本地仓库相操作关
### 创建本地仓库
1. 创建本地仓库的方法有两种：
    - 一种是创建全新的仓库：`git init`，会在当前目录初始化创建仓库。
    - 另一种是克隆远程仓库：`git clone [url]`
2. 示例
    - init

        ```Bash
        # 开始初始化项目，也可指定目录：git init [文件目录]
        $ git init
        Initialized empty Git repository in D:/Project_Files/github.Kwong/KwebNote/.git/
        ```
        创建完多出了一个被隐藏的`.git`目录，这就是本地仓库Git的工作场所
        ![[IMG-20260412093955093.png|Untitled 6 3.png|415]]
    - clone

        ```Bash
        $ git clone 'https://github.com/kwonganding/KWebNote.git'
        Cloning into 'KWebNote'...
        remote: Enumerating objects: 108, done.
        remote: Counting objects: 100% (108/108), done.
        remote: Compressing objects: 100% (60/60), done.
        remote: Total 108 (delta 48), reused 88 (delta 34), pack-reused 0
        Receiving objects: 100% (108/108), 9.36 KiB | 736.00 KiB/s, done.
        Resolving deltas: 100% (48/48), done.
        ```
### 暂存区 Add
1. 可以简单理解为，`git add` 命令就是把要提交的所有修改放到暂存区（Stage），然后，执行 `git commit` 就可以一次性把暂存区的所有修改提交到仓库
2. 操作指令

    ![[IMG-20260412093955152.png|Untitled 7 3.png|607]]
3. 示例

    ```Bash
    # 添加指定文件到暂存区，包括被修改的文件
    $ git add [file1] [file2] ...
    # 添加当前目录的所有文件到暂存区
    $ git add .
    # 删除工作区文件，并且将这次删除放入暂存区
    $ git rm [file1] [file2] ...
    # 改名文件，并且将这个改名放入暂存区
    $ git mv [file-original] [file-renamed]
    ```
### **提交 commit-记录**
1. `git commit` 提交是以时间顺序排列被保存到数据库中的，就如游戏关卡一样，每一次提交（commit）就会产生一条记录：`id + 描述 + 快照内容`
    - **🔸commit id**：
        - 根据修改的文件内容采用摘要算法（SHA1）计算出不重复的40位字符，这么长是因为Git是分布式的，要保证唯一性、完整性
        - 一般本地指令中可以只用前几位（6）
    - **🔸描述**：
        - 针对本次提交的描述说明，建议**准确**填写，就跟代码中的注释一样，很重要
    - **🔸快照**：
        - 就是完整的版本文件，以对象树的结构存在仓库下`\.git\objects`目录里
        - 这也是Git效率高的秘诀之一
2. 多个提交就形成了一条时间线，每次提交完，会移动当前分支`master`、`HEAD`的“指针”位置

    ![[IMG-20260412093955219.png|Untitled 8 2.png|658]]
3. 相关指令

    ![[IMG-20260412093955288.png|Untitled 9 2.png|598]]
4. 通过`git log`指令可以查看提交记录日志，可以很方便的查看每次提交修改了哪些文件，改了哪些内容，从而进行恢复等操作。

    ![[IMG-20260412093955361.png|Untitled 10 2.png|620]]
5. 示例

    ```Bash
    $ git log -n2
    commit 412b56448568ff362ef312507e78797befcf2846 (HEAD -> main)
    Author: Kanding <123anding@163.com>
    Date:   Thu Dec 1 19:02:22 2022 +0800
    commit c0ef58e3738f7d54545d8c13d603cddeee328fcb
    Author: Kanding <123anding@163.com>
    Date:   Thu Dec 1 16:52:56 2022 +0800
    ```
### **Git 的“指针”引用们 ⭐**
1. 几种指针
    1. 提交记录间的指针
        1. 提交记录之间也存在“指针”引用
        2. 每个提交会指向其上一个提交
    2. **标签**
        1. 就是对某一个提交记录的的 **固定** “指针”引用，取一个别名更容易记忆一些关键节点
        2. 存储在工作区根目录下`.git\refs\tags`
    3. **分支**
        1. 也是指向某一个提交记录的“指针”引用，“指针”位置可变，如提交、更新、回滚
        2. 存储在工作区根目录下`.git\refs\heads`
    4. **HEAD**
        1. 指向当前活动分支（最新提交）的一个“指针”引用
        2. 存在在“`.git/HEAD`”文件中，存储的内容为“`ref: refs/heads/master`”
        3. 一些特殊符号含义
            - `HEAD` 表示当前分支的最新版本，是比较常用的参数
            - `HEAD^` 上一个版本，`HEAD^^` 上上一个版本
            - `HEAD~` 或 `HEAD~1` 表示上一个版本，以此类推，`HEAD^10` 为最近第10个版本
            - `HEAD@{2}` 在 `git reflog` 日志中标记的提交记录索引
2. 图示：

    ![[IMG-20260412093955503.png|Untitled 11 2.png|631]]
    - 上图中：
        - `HEAD`始终指向当前活动分支，多个分支只能有一个处于活动状态
        - 标签`t1`在某一个提交上创建后，就不会变了。而分支、`HEAD`的位置会改变
3. 打开这些文件内容看看

    ```Bash
    # tag
    $ git tag -a 'v1' -m'v1版本'
    $ cat .git/refs/tags/v1
    a2e2c9caea35e176cf61e96ad9d5a929cfb82461
    # main分支指向最新的提交
    $ cat .git/refs/heads/main
    8f4244550c2b6c23a543b741c362b13768442090
    # HEAD指向当前活动分支
    $ cat .git/HEAD
    ref: refs/heads/main
    # 切换到dev分支，HEAD指向了dev
    $ git switch dev
    Switched to branch 'dev'
    $ cat .git/HEAD
    ref: refs/heads/dev
    ```
    > [!important] 这里的主分支名字为“
    >
    > `main`”，是因为该仓库是从Github上克隆的，**Github上创建的仓库默认主分支名字就是“`main`”，本地创建的仓库默认主分支名字为“`master`”**

### **比较 diff**
1. `git diff`用来比较不同文件版本之间的差异

    ![[IMG-20260412093955596.png|559]]
    ![[IMG-20260412093955698.png|570]]
2. 示例

    ```Bash
    # 查看文件的修改
    $ git diff README.md
    # 查看两次提交的差异
    $ git diff 8f4244 1da22
    # 显示今天你写了多少行代码：工作区+暂存区
    $ git diff --shortstat "@{0 day ago}"
    ```
## 3.2 远程仓库操作相关
### 远程登陆
1. 可以用公共的Git服务器，也可以自己搭建一套Git服务器

    ![[IMG-20260412093955789.png|534]]
    - 公共Git服务器，如Github、Gitlab、码云Gitee、腾讯Coding等
    - 搭建私有Git服务器，如开源的Gitlab、Gitea、等
2. **远程仓库指令**

    ![[IMG-20260412093955886.png|430]]
3. HTTPS 的方式：
    1. 基于HTTPS的地址连接远程仓库，Github的共有仓库克隆、拉取（pull）是不需要验证的
    2. 示例：

        ```Bash
        $ git clone 'https://github.com/kwonganding/KWebNote.git'
        Cloning into 'KWebNote'...
        # 仓库配置文件“.git/config”
        [remote "origin"]
          url = https://github.com/kwonganding/KWebNote.git
         fetch = +refs/heads/*:refs/remotes/origin/*
         pushurl = https://github.com/kwonganding/KWebNote.git
        ```
    3. 推送（push）代码的时候就会提示输入用户名、密码了，否则无法提交。记住用户密码的方式有两种：
        - **🔸URL地址配置**：在原本URL地址上加上用户名、密码，`https://` 后加 `用户名:密码@`

            ```Bash
            \# 直接修改仓库的配置文件“.git/config”
            [remote "origin"]
              url = https://用户名:密码@github.com/kwonganding/KWebNote.git
             fetch = +refs/heads/*:refs/remotes/origin/*
             pushurl = https://github.com/kwonganding/KWebNote.git
            ```
        - **🔸本地缓存**：会创建一个缓存文件`.git-credentials`，存储输入的用户名、密码。

            ```Bash
            \# 参数“--global”全局有效，也可以针对仓库设置“--local”
            \# store 表示永久存储，也可以设置临时存储
            git config --global credential.helper store
            \# 存储内容如下，打开文件“仓库\.git\.git-credentials”
            https://kwonganding:[加密内容付费可见]@github.com
            ```
### **推送 Push / 拉取 pull**
1. `git push`、`git pull`是团队协作中最常用的指令，用于同步本地、服务端的更新，与他人协作
    1. **🔸推送**（push）：推送本地仓库到远程仓库
        1. 如果推送的更新与服务端存在冲突，则会被拒绝，`push`失败
        2. 一般是有其他人推送了代码，导致文件冲突，可以先`pull`代码，在本地进行合并，然后再`push`
    2. **🔸拉取**（pull）：从服务端（远程）仓库更新到本地仓库
        - `git pull`：拉取服务端的最新提交到本地，并与本地合并，合并过程同分支的合并
        - `git fetch`：拉取服务端的最新提交到本地，不会自动合并，也不会更新工作区
            > [!important]
            >
            > 1. 两者都是从服务端获取更新，主要区别是`fetch`不会自动合并，不会影响当前工作区内容
            >
            > 2. **`git pull = git fetch + git merge`**
            >
            > ![[IMG-20260412093955976.png]]
            >
            >     - `git fetch`只获取了更新，并未影响`master`、`HEAD`的位置
            >
            >     - 要更新`master`、`HEAD`的位置需要手动执行`git merge`合并
            >
2. 图示

    ![[IMG-20260412093956088.png|648]]
3. 示例

    ```Bash
    # fetch只更新版本库
    $ git fetch
    remote: Enumerating objects: 5, done.
    remote: Counting objects: 100% (5/5), done.
    remote: Compressing objects: 100% (3/3), done.
    remote: Total 3 (delta 2), reused 0 (delta 0), pack-reused 0
    Unpacking objects: 100% (3/3), 663 bytes | 44.00 KiB/s, done.
    From github.com:kwonganding/KWebNote
       2ba12ca..c64f5b5  main       -> origin/main
    # 执行合并，合并自己
    $ git merge
    Updating 2ba12ca..c64f5b5
    Fast-forward
     README.md | 2 +-
     1 file changed, 1 insertion(+), 1 deletion(-)
    ```
## 3.3 分支操作相关
1. **分支**
    1. 就是指向某一个提交记录的“指针”引用，因此创建分支是非常快的，不管仓库多大
    2. 当我们运行 `git branch dev` 创建了一个名字为 `dev` 的分支，Git 实际上是在 `.git\refs\heads` 下创建一个`dev`的引用文件（没有扩展名）

        ![[IMG-20260412093956177.png|615]]
2. 分支指令

    ![[IMG-20260412093956270.png|543]]
### **分支的切换 checkout**
    1. 代码仓库可以有多个分支，`master` 为默认的主分支，但只有一个分支在工作状态。所以要操作不同分支，需要切换到该分支，`HEAD` 就是指向当前正在活动的分支

        ![[Untitled 20.png]]
        1. 使用 `git checkout dev` 切换分支时，**⭐干了两件事：**
            - 1️⃣**`HEAD` 指向 `dev`**：修改 `HEAD` 的“指针”引用，指向 `dev` 分支
            - 2️⃣ **还原工作空间**：把 `dev` 分支内容还原到工作空间
        2. 此时的活动分支就是`dev`了，后续的提交就会更新到分支了
    2. ⭐**切换时还没提交的代码怎么办**❓
        - 如果修改（包括未暂存、已暂存）和待切换的分支**没有冲突**，则切换成果，且未提交修改会一起带过去，所以要注意！
        - 如果**有冲突**，则会报错，提示先提交或隐藏，关于隐藏可查看后续章节内容“`stash`”
> [!important] **在Git 2.23版本以后，增加了`git switch`、`git reset` 指令**
>
> - `checkout` 是Git的底层指令，比较常用，也比较危险，他会重写工作区。支持的功能比较多，能撤销修改，能切换分支，这也导致了这个指令比较复杂
>
> - `git switch`：专门用来实现分支切换
>
>     ```Bash
>     # 切换到dev分支，HEAD指向了dev
>     # 此处 switch 作用同 checkout，switch只用于切换，不像checkout功能很多
>     $ git switch dev
>     Switched to branch 'dev'
>     $ cat .git/HEAD
>     ref: refs/heads/dev
>     ```
>
>
> - `git reset`：专门用来实现本地修改的撤销，更多可参考后续“reset”内容
### **合并 Merge & 冲突**
1. 把两个分支的修改内容合并到一起，常用的合并指令`git merge [branch]`，将分支`[branch]`合并到当前分支。根据要合并的内容的不同，具体合并过程就会有多种情况
2. **🔸快速合并（Fast forward）**
    1. 如下图，`master`分支么有任何提交，“`git merge dev`”合并分支`dev`到`master`
    2. 此时合并速度就非常快，直接移动`master`的“指针”引用到`dev`即可
    3. 这就是快速合并（Fast forward），不会产生新的提交

        [![|562](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKwyoBHNeB2zrfu1mfpj3KG2UAgdxKLgb4S1jW4bI1UZukPlBFqGbelow/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKwyoBHNeB2zrfu1mfpj3KG2UAgdxKLgb4S1jW4bI1UZukPlBFqGbelow/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)
        - 合并`dev`到`master`，注意要先切换到 `master`分支
        - 然后执行`git merge dev`，把`dev`合并到当前分支
        > 📢强制不用快速合并：`git merge --no-ff -m "merge with no-ff" dev`，参数`--no-ff`不启用快速合并，会产生一个新的合并提交记录
3. **🔸普通合并**
    1. 如果`master`有变更，存在分支交叉，则会把两边的变更合并成一个提交
        - 如果两边变更的文件不同，没有什么冲突，就自动合并了
        - 如果有修改同一个文件，则会存在冲突，到底该采用哪边的，程序无法判断，就换产生冲突。冲突内容需要人工修改后再重新提交，才能完成最终的合并

        [![|560](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKwUOIWLZXKO1O7UrqN8qLVZQ0ib2sLscOQZw6bxOlwNbUB2NzdsLxB4Lw/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKwUOIWLZXKO1O7UrqN8qLVZQ0ib2sLscOQZw6bxOlwNbUB2NzdsLxB4Lw/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)
        - 上图中，创建 `dev` 分支后，两个分支都有修改提交，因此两个分支就不在一条顺序线上了，此时合并`dev` 到 `master` 就得把他们的修改进行合并操作了
            - `v5`、`v7`共同祖先是`v4`，从这里开始分叉
            - Git 会用两个分支的末端`v6` 和 `v8`以及它们的共同祖先`v4`进行三方合并计算。合并之后会生成一个新（和并）提交`v9`
            - 合并提交`v9`就有两个祖先`v6`、`v8`

### **变基 rebase**
1. 把两个分支的修改内容合并到一起的办法有两种：`merge` 和 `rebase`，作用都是一样的，**区别是 `rebase` 的提交历史更简洁，干掉了分叉，merge的提交历史更完整**
2. 示例：

    ```Bash
    $ git rebase master
    $ git checkout master
    $ git merge dev
    ```
    [![|613](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKwrr7g2iam9CeIibLB0uET8aLhHCgoYWLtqwfXDUeuYzxHohl7csSp6ZYQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKwrr7g2iam9CeIibLB0uET8aLhHCgoYWLtqwfXDUeuYzxHohl7csSp6ZYQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)
    - 在`dev`上执行“`git rebase master`”变基，将分支上分叉的`v7`、`v8`生成补丁，然后在`master`分支上应用补丁，产生新的`v7'v8'`新的提交
    - 然后回到`master`分支，完成合并`git merge dev`，此时的合并就是快速合并了
    - 最终的提交记录就没有分叉了

## 3.4 撤销变更操作
1. **后悔指令**
![[IMG-20260412093956359.png|631]]
![[IMG-20260412093956454.png|548]]
### **回退版本 reset**
1. `reset`是专门用来撤销修改、回退版本的指令
2. 简单理解就是移动`master`分支、`HEAD`的“指针”地址，理解这一点就基本掌握`reset`了
3. 如下图：
    - 回退版本`git reset --hard v4` 或 `git reset --hard HEAD~2`，`master`、`HEAD`会指向`v4`提交，`v5`、`v6`就被废弃了
    - 也可以重新恢复到`v6`版本：`git reset --hard v6`，就是移动`master`、`HEAD`的“指针”地址

    [![|561](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKwrW4x6H9SkLnNXliazFC8fiahectFwVKYFXGRYTFl2sdBVwCo7SEPGb0A/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKwrW4x6H9SkLnNXliazFC8fiahectFwVKYFXGRYTFl2sdBVwCo7SEPGb0A/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)
4. `reset`有三种模式，对应三种参数：`mixed`（默认模式）、`soft`、`hard`。三种参数的主要区别就是对工作区、暂存区的操作不同
    - `mixed`为默认模式，参数可以省略
    - 只有`hard`模式会重置工作区、暂存区，一般用这个模式会多一点

[![|588](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKw4hTYxBfDjsO3ORU0nG3lbFv3iabQwwSBq9ia00lIeEbcawTWLHtnkqsQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKw4hTYxBfDjsO3ORU0nG3lbFv3iabQwwSBq9ia00lIeEbcawTWLHtnkqsQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)
1. 穿梭前，用`git log`可以查看提交历史，以便确定要回退到哪个版本。要重返未来，用`git reflog`查看命令历史，以便确定要回到未来的哪个版本

    ```Bash
    git reset [--soft | --mixed | --hard] [HEAD]
    \# 撤销暂存区
    $ git reset
    Unstaged changes after reset:
    M       R.md
    \# 撤销工作区、暂存区修改
    $ git reset --hard HEAD
    \# 回退版本库到上一个版本，并重置工作区、暂存
    $ git reset --hard HEAD~
    \# 回到原来的版本（恢复上一步的撤销操作），并重置工作区、暂存
    $ git reset --hard 5f8b961
    \# 查看所有历史提交记录
    $ git reflog
    ccb9937 (HEAD -> main, origin/main, origin/HEAD) HEAD@{0}: commit: 报表新增导入功能
    8f61a60 HEAD@{1}: commit: bug：修复报表导出bug
    4869ff7 HEAD@{2}: commit: 用户报表模块开发
    4b1028c HEAD@{3}: commit: 财务报表模块开发完成
    ```
### **撤销提交 revert**
1. 安全的撤销某一个提交记录，基本原理就是生产一个新的提交，用原提交的逆向操作来完成撤销操作
2. 注意，这不同于 `reset`，`reset` 是回退版本，`revert` 只是用于撤销某一次历史提交，操作是比较安全的

    [![|537](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKw9JWfUrQoc6byQhB8NuehDxQqkgAFuMZpFu9YcGUoVh2lCPSpMbSxjQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)](https://mmbiz.qpic.cn/mmbiz_png/A3ibcic1Xe0iaQlYph2qibic0ib3NzFAiciafWKw9JWfUrQoc6byQhB8NuehDxQqkgAFuMZpFu9YcGUoVh2lCPSpMbSxjQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)
3. 如上图：
    - 想撤销`v4`的修改，执行`git revert v4`，会产生一个新的提交`v-4`，是`v4`的逆向操作
    - 同时更新`maser`、`HEAD`“指针”位置，以及工作区内容
    - 如果已`push`则重新`push`即可

    ```Bash
    \# revert撤销指定的提交，“-m”附加说明
    $ git revert 41ea42 -m '撤销对***的修改'
    [main 967560f] Revert "123"
            1 file changed, 1 deletion(-)
    ```
### **checkout/reset/revert 总结⭐**
![[IMG-20260412093956535.png|619]]
- 可看出`reset`完全可以替代`checkout`来执行撤销、回退操作，本来也是专门用来干这个事情的，可以抛弃了（撤销的时候）