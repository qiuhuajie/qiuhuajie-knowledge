- [[#1. 强化学习 MDP 四元组 <S,A,P,R>]]
- [[#2. Q 表格和衰减因子]]
- [[#2. 时序差分]]
- [[#3. SARSA]]
- [[#5. Q-learning]]
# 1. 强化学习 MDP 四元组 `<S,A,P,R>`
1. 用马尔可夫决策过程 MDP 描述一个**和时间相关的序列决策问题**
    

    ![[IMG-20260321173718241.png|Untitled 524.png]]

    
1. MDP 四元组
    
    - S ： state 状态
    
    - A ： action 动作
    
    - R ： reward 奖励：$R(S,A)$ 表示在状态 S 中采取行动 A 后立即得到的报酬
    
    - P ： probability 状态转移概率： $P(S_{t+1},R_t|S_t,A_t)$
    

    ![[IMG-20260404032008789.png|Untitled 1 389.png]]

    
1. **使用两个函数来描述环境**
    

    ![[IMG-20260404032008900.png|Untitled 2 315.png]]

    
1. 分类
    
    - **Model-based：**对于 p 和 r 的概率是已知的，即环境已知。算法：动态规划
    
    - **Model-free：**对于 p 和 r 的概率是未知的，即环境未知，只能够**摸着石头过河**，逐步去探索。算法强化学习
    
# 2. Q 表格和衰减因子
1. Q 函数表格
    
    1. 存储转态动作价值
    
    1. 相对应生活手册，根据价值来获取
    

    ![[IMG-20260404032008953.png|Untitled 3 236.png]]

    
1. Q 表的**延迟更新**：
    
    1. 以未来的总收益为标准，更据实际情况进行操作
    
    1. 闯红灯：送到医院的长远目标更有价值，所以当前可以选择闯红灯
        

        ![[IMG-20260404032009007.png|Untitled 4 180.png]]

        
    
    1. 但目标放得太长远也不好
        
        1. 如果是一个持续的，没有尽头的任务，考虑很远的收益就很不合理
        
        1. 添加一个**衰减因子 $\gamma$**，范围是 `[0, 1]` 之间
        
        1. 这个值给越往前越大，即越近的收益对当前影响越大；哪怕后面好久以后的数值很大但是也起不了什么波澜，对当前价值的影响就越小
        
        1. 引入衰减因子计算价值，
            

            ![[IMG-20260404032009107.png|Untitled 5 146.png]]

            
        
    
# 2. **时序差分**
1. 强化：**可以用下一个状态的价值，来更新当前状态的价值**（自举）
1. 这种单步更新的方法也就是时序差分的更新方法
1. 巴普洛夫的条件反射实验
    

    ![[IMG-20260404032009141.png|Untitled 6 121.png]]

    
    1. **当无条件刺激和有条件刺激在时间上的结合，导致无条件刺激对也产生条件反射，这样的学习叫做强化**
        

        ![[IMG-20260405035358129.png|Untitled 7 94.png]]

        
    
    1. 人类对某些事物的认知与联系就算是强化学习。看到定情信物想到爱人，本来两者毫无关联但是有了情感在里面就不一样啦
    
    1. 甚至可以形成多级的强化关系
        

        ![[IMG-20260405035358619.png|Untitled 8 76.png]]

        
    
1. 使用数学表达这种强化方式：**时序差分（TD 单步更新）**
    
    1. 拿下一步的 Q 值：$Q(S_{t+1},A_{t+1})$，来更新当前步的 Q 值：$Q(S_t,A_t)$
    
    1. 最开始 Q 值都是随机的初始值或 0，需要不断的去逼近理想中真实的 Q 值，也即目标值
    
    1. 这个目标值就是未来收益的总和，这个总和是带衰减的
    
    1. 拿到目标值后，$Q(S_t,A_t)$ 使用软更新的方式去逼近这个目标值
    
    1. 每次只更新一点点，通过 $\alpha$ 来实现，类似于学习率
        

        ![[IMG-20260405035359444.png|Untitled 9 67.png]]

        
    
1. 这样更新公式为
    
    1. 只需要拿到当前时刻的 $S_t$、$A_t$
    
    1. 以及下一步的 $S_{t+1}$、$A_{t+1}$ ，和拿到的 $R_{t+1}$
    
    1. 就可以更新计算 $Q(S_t,A_t)$ 了
    
1. 也即 SARSA
# 3. SARSA
1. Sarsa 全称是 state-action-reward-state'-action'
    
    1. 目的是学习特定的 state 下，特定 action 的价值 Q，最终建立和优化一个 Q 表格，以 state 为行，action 为列
    
    1. 根据与环境交互得到的 reward 来更新 Q 表格
        

        ![[IMG-20260405035400362.png|Untitled 10 57.png]]

        
    
1. **SARSA 的更新公式**
    

    ![[IMG-20260405035400418.png|Untitled 11 49.png]]

    
    ```Python
    class SarsaAgent(object):
        def __init__(self, obs_n, act_n, learning_rate=0.01, gamma=0.9, e_greed=0.1):
            self.act_n = act_n      # 动作维度，有几个动作可选
            self.lr = learning_rate # 学习率
            self.gamma = gamma      # reward的衰减率
            self.epsilon = e_greed  # 按一定概率随机选动作
            self.Q = np.zeros((obs_n, act_n))
        ...
        # 学习方法，也就是更新Q-table的方法
        def learn(self, obs, action, reward, next_obs, next_action, done):
            """ on-policy
                obs: 交互前的obs, s_t
                action: 本次交互选择的action, a_t
                reward: 本次动作获得的奖励r
                next_obs: 本次交互后的obs, s_t+1
                next_action: 根据当前Q表格, 针对next_obs会选择的动作, a_t+1
                done: episode是否结束
            """
    				# 使用公式更新Q表
            predict_Q = self.Q[obs, action]
            if done:
                target_Q = reward # 没有下一个状态了
            else:
                target_Q = reward + self.gamma * self.Q[next_obs, next_action] # Sarsa
            self.Q[obs, action] += self.lr * (target_Q - predict_Q) # 修正q
    
        # 保存Q表格数据到文件
        def save(self):
            npy_file = './q_table.npy'
            np.save(npy_file, self.Q)
            print(npy_file + ' saved.')
        
        # 从文件中读取Q值到Q表格中
        def restore(self, npy_file='./q_table.npy'):
            self.Q = np.load(npy_file)
            print(npy_file + ' loaded.')
    ```
    
1. **Sarsa 在训练中为了更好的探索环境，采用 `ε-greedy` 方式来训练，有一定概率随机选择动作输出**
    

    ![[IMG-20260405035402397.png|Untitled 12 43.png]]

    
    ```Python
    # 根据输入观察值，采样输出的动作值，带探索
    def sample(self, obs):
        if np.random.uniform(0, 1) < (1.0 - self.epsilon): \#根据table的Q值选动作
            action = self.predict(obs)
        else:
            action = np.random.choice(self.act_n) \#有一定概率随机探索选取一个动作 ε-greedy
        return action
    
    # 根据输入观察值，预测输出的动作值
    def predict(self, obs):
        Q_list = self.Q[obs, :]
        maxQ = np.max(Q_list)
        action_list = np.where(Q_list == maxQ)[0]  # maxQ可能对应多个action
        action = np.random.choice(action_list)
        return action
    ```
    
1. 训练
    
    ```Python
    def run_episode(env, agent, render=False):
        total_steps = 0 # 记录每个episode走了多少step
        total_reward = 0
    
        obs = env.reset() # 重置环境, 重新开一局（即开始新的一个episode）
        action = agent.sample(obs) # 根据算法选择一个动作
    
        while True:
            next_obs, reward, done, _ = env.step(action) # 与环境进行一个交互
            next_action = agent.sample(next_obs) # 根据算法选择一个动作
            # 训练 Sarsa 算法
            agent.learn(obs, action, reward, next_obs, next_action, done)
    
            action = next_action
            obs = next_obs  # 存储上一个观察值
            total_reward += reward
            total_steps += 1 # 计算step数
            if render:
                env.render() \#渲染新的一帧图形
            if done:
                break
        return total_reward, total_steps
    
    
    def test_episode(env, agent):
        total_reward = 0
        obs = env.reset()
        while True:
            action = agent.predict(obs) # greedy
            next_obs, reward, done, _ = env.step(action)
            total_reward += reward
            obs = next_obs
            # time.sleep(0.5)
            # env.render()
            if done:
                break
        return total_reward
    ```
    
# 5. **Q-learning**
1. Q-learning 也是采用Q表格的方式存储Q值（状态动作价值），决策部分与Sarsa是一样的，采用 ε-greedy 方式增加探索
1. **Q-learning 跟 Sarsa 不一样的地方是更新 Q 表格的方式（绿色框部分）**
    
    1. Q-learning的更新公式为：
        

        ![[IMG-20260404032009588.png|Untitled 13 40.png]]

        
    
    1. **Sarsa 是 on-policy 的更新方式，先做出动作再更新**
    
    1. **Q-learning 是 off-policy 的更新方式**：
        
        1. **==更新 learn() 时，无需获取下一步实际做出的动作 next_action==**==，也即目标策略不会直接和环境交互，不会关注行为策略下一步采用的动作==
            

            ![[IMG-20260404032009659.png|Untitled 14 37.png]]

            
        
        1. **==并假设下一步动作是取最大 Q 值的动作==**
            

            ![[IMG-20260404032009728.png|Untitled 15 35.png]]

            
        
    
1. **区别：**==**Sarsa 拿自己实际做的动作去回头修正，而 Q-learning 使用之后的最佳动作去回头修正，表现得更大胆，更有可能探索到最优得策略**==
    

    ![[IMG-20260404032009809.png|Untitled 16 27.png]]

    
1. **代码就是在 `learn()` 部分与 Sarsa 不同**
    
    ```Python
    # 学习方法，也就是更新Q-table的方法
    def learn(self, obs, action, reward, next_obs, done):
        """ off-policy
            obs: 交互前的obs, s_t
            action: 本次交互选择的action, a_t
            reward: 本次动作获得的奖励r
            next_obs: 本次交互后的obs, s_t+1
            done: episode是否结束
        """
        predict_Q = self.Q[obs, action]
        if done:
            target_Q = reward # 没有下一个状态了
        else:
            target_Q = reward + self.gamma * np.max(self.Q[next_obs, :]) # Q-learning
        self.Q[obs, action] += self.lr * (target_Q - predict_Q) # 修正q
    ```