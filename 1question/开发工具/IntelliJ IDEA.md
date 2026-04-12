- [[#1. 导包操作]]
- [[#2. 实体类中自动生成 serialVersionUID]]
- [[#3. 开启 DashBoard]]
- [[#4. 新建 Maven 项目]]
# 1. 导包操作

![[IMG-20260404032013462.jpeg]]

![[IMG-20260404032013575.jpeg]]

# 2. 实体类中**自动生成 serialVersionUID**

[https://blog.csdn.net/Vladimirzzzzz/article/details/129372146](https://blog.csdn.net/Vladimirzzzzz/article/details/129372146)

![[IMG-20260404032013621.png|Untitled 25.png]]

# 3. **开启 DashBoard**
1. 找到本项目下 `workspace.xml` 文件
    

    `**"C:\Users\lenovo\IdeaProjects\springCloudProject.idea\workspace.xml"**`

    
1. 添加：
    
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
    
1. 可能需要重启生效：
    

    ![[IMG-20260404032013741.png|Untitled 1 6.png]]

    
# 4. **新建 Maven 项目**
1. **maven版本选择**
    

    ![[IMG-20260404032013791.png|Untitled 2 5.png]]

    

    ![[IMG-20260404032013842.png|Untitled 3 5.png]]

    
1. **字符编码**
    

    ![[IMG-20260404032013879.png|Untitled 4 4.png]]

    
1. **注解生效激活**
    

    ![[IMG-20260404032013990.png|Untitled 5 4.png]]

    
1. **Java 编译版本选择**
    

    ![[IMG-20260404032014039.png|Untitled 6 4.png]]

    
1. **File Type 过滤**
    

    ![[IMG-20260404032014089.png|Untitled 7 4.png]]

    

    ![[IMG-20260404032014142.png|Untitled 8 3.png]]