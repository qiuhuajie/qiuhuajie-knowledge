# 1. 介绍
1. JWT（JSON Web Token）是一种用于在网络应用间传递信息的简洁、URL 安全的方式。JWT的优势在于可以在用户和服务器之间传递安全可靠的信息
1. 可以理解为一种 Token 的实现方式：JWT的本质就是一个字符串，它是将用户信息保存到一个Json字符串中，然后进行编码后得到一个 JWT token
# 2. 组成
- JWT由三部分组成，分别是Header（头部）、Payload（载荷）和Signature（签名）
    
    1. `Header`：用于描述JWT的元数据，如算法和 token 的类型
    
    1. `Payload`：是 JWT 的主体部分，包含了要传递的信息
    
    1. `Signature`：是对 Header 和 Payload 签名的结果，用于验证消息的完整性和可信度
    
![[Attachment/1question/中间件/Redis/Redis 实战/2 登录注册功能/2 2 多系统登录/IMG-20260405035438388.png|Untitled 537.png]]
# 3. JWT 优点
- JWT Token 数据量小，可以被轻松地使用和传递
- 不需要在服务器端保存会话信息，从而减轻了服务器的负担。也更适用于分布式微服务单点登录的实现
- 可以使用公共密钥或私有密钥签名，从而保证了信息的安全性
# 4. JWT 种类
- 其实JWT(JSON Web Token)指的是一种规范，这种规范允许我们使用JWT在两个组织之间传递安全可靠的信息，JWT的具体实现可以分为以下几种：
    
    - `nonsecure JWT`：未经过签名，不安全的JWT
    
    - **`JWS`：经过签名的 JWT ✅**
    
    - `JWE`：payload 部分经过加密的JWT