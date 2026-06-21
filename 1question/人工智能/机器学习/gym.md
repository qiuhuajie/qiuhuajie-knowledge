---
title: "gym"
tags:
  - "人工智能"
  - "人工智能/机器学习"
  - "gym"
  - "机器学习"
  - "强化学习"
  - "模型原理"
updated: 2026-04-16
---
# Gym
1. Gym中的函数
    - **`env.reset()`**
        - 在强化学习中，智能体要通过多次尝试来积累经验，从中学到各种状态下哪个行动最好。一次尝试称为一个 episode，每次尝试都要到达终止状态
        - 一次尝试结束后，智能体需要从头开始，因此智能体需要有初始化的功能
    - **`env.render()`**
        - 类似于一个图像引擎，用于显示环境中的物体图像。首先导入rendering模块，利用rendering模块中的画图函数进行图形的绘制
        - 然后用 cart = rendering.FilledPolygon() 创建小车，然后给 cart 添加平移和旋转属性
    - **`env.action_space.sample()`**
        - 含义是在该游戏的所有动作空间里随机选择一个作为输出
        - 在这个例子中，意思就是，动作只有两个：0 和 1，一左一右
    - **`env.step()`**
        - 输入动作
        - 这个方法的作用不止于此，它还有四个返回值，分别是 observation、reward、done、info
            - observation(object)，是状态信息，是在游戏中观测到的屏幕像素值或者盘面状态描述信息
            - reward(float)：是奖励值，即 action 提交以后能够获得的奖励值。这个奖励值因游戏的不同而不同，但总体原则是，对完成游戏有帮助的动作会获得比较高的奖励值
            - done(boolean)：表示游戏是否已经完成。如果完成了，就需要重置游戏并开始一个新的 episode
            - info(dict)：是一些比较原始的用于诊断和调试的信息，或许对训练有帮助。不过，OpenAI 团队在评价你提交的机器人时，是不允许使用这些信息的
2. 每个环境都定义了自己的观测空间和动作空间
    1. 环境 env 的观测空间用env.observation_space表示，动作空间用 env.action_space 表示
    2. 观测空间和动作空间既可以是离散空间（即取值是有限个离散的值），也可以是连续空间（即取值是连续的）
    3. **在 Gym 库中，离散空间一般用 `gym.spaces.Discrete` 类表示，连续空间用 `gym.spaces.Box` 类表示**
    4. 例如
        1. 环境’MountainCar-v0’的观测空间是**`Box(2,)`**，表示观测可以用 2 个 float 值表示
        2. 环境’MountainCar-v0’的动作空间是**`Dicrete(3)`**，表示动作取值自`{0,1,2}`
        3. 对于离散空间，gym.spaces.Discrete 类实例的成员 n 表示有几个可能的取值
        4. 对于连续空间，Box 类实例的成员 low 和 high 表示每个浮点数的取值范围

        ```Python
        import gym
        env = gym.make('CartPole-v0')
        print('观测空间 = {}'.format(env.observation_space))
        print('动作空间 = {}'.format(env.action_space))
        print('观测范围 = {} ~ {}'.format(env.observation_space.low,
                env.observation_space.high))
        print('动作数 = {}'.format(env.action_space.n))
        ```
        ```Python
        观测空间 = Box([-4.8000002e+00 -3.4028235e+38 -4.1887903e-01 -3.4028235e+38], [4.8000002e+00 3.4028235e+38 4.1887903e-01 3.4028235e+38], (4,), float32)
        动作空间 = Discrete(2)
        观测范围 = [-4.8000002e+00 -3.4028235e+38 -4.1887903e-01 -3.4028235e+38] ~ [4.8000002e+00 3.4028235e+38 4.1887903e-01 3.4028235e+38]
        动作数 = 2
        ```