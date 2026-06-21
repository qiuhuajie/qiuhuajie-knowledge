---
title: "IntelliJ IDEA"
tags:
  - "开发工具"
  - "IntelliJ IDEA"
  - "效率工具"
  - "工程实践"
  - "使用指南"
  - "知识梳理"
updated: 2026-04-16
---
# 一、导包操作

![[IMG-20260404032013462.jpeg]]

![[IMG-20260404032013575.jpeg]]

# 二、实体类中自动生成 serialVersionUID

[https://blog.csdn.net/Vladimirzzzzz/article/details/129372146](https://blog.csdn.net/Vladimirzzzzz/article/details/129372146)

![[IMG-20260404032013621.png|Untitled 25.png]]

# 三、开启 DashBoard
1. 找到本项目下 `workspace.xml` 文件

    **`"C:\Users\lenovo\IdeaProjects\springCloudProject.idea\workspace.xml"`**

2. 添加：

    ```XML
    <component name="RunDashboard">
        <option name="configurationTypes">
            <set>
                <option value="SpringBootApplicationConfigurationType" />
            </set>
        </option>
        <option name="ruleStates">
            <list>
                <RuleState>
                    <option name="name" value="ConfigurationTypeDashboardGroupingRule" />
                </RuleState>
                <RuleState>
                    <option name="name" value="StatusDashboardGroupingRule" />
                </RuleState>
            </list>
        </option>
    </component>
    ```
3. 可能需要重启生效：

    ![[IMG-20260404032013741.png|Untitled 1 6.png]]

# 四、新建 Maven 项目
1. **maven版本选择**

    ![[IMG-20260404032013791.png|Untitled 2 5.png]]

    ![[IMG-20260404032013842.png|Untitled 3 5.png]]

2. **字符编码**

    ![[IMG-20260404032013879.png|Untitled 4 4.png]]

3. **注解生效激活**

    ![[IMG-20260404032013990.png|Untitled 5 4.png]]

4. **Java 编译版本选择**

    ![[IMG-20260404032014039.png|Untitled 6 4.png]]

5. **File Type 过滤**

    ![[IMG-20260404032014089.png|Untitled 7 4.png]]

    ![[IMG-20260404032014142.png|Untitled 8 3.png]]
