---
title: "Agentic AI Framework for Java Developers"
source: "https://java2ai.com/docs/frameworks/agent-framework/tutorials/structured-output"
author:
  - "[[spring-ai-alibaba-team]]"
published: 2026-01-19
created: 2026-06-28
description: "Spring AI Alibaba 开源项目基于 Spring AI 构建，是阿里云通义系列模型及服务在 Java AI 应用开发领域的最佳实践，提供高层次的 AI API 抽象与云原生基础设施集成方案，帮助开发者快速构建 AI 应用。"
tags:
  - "clippings"
---
# 一、Agentic AI Framework for Java Developers 9

1. 结构化输出允许 Agent 以特定的、可预测的格式返回数据。相比于解析自然语言响应，您可以直接获得 JSON 对象或 Java POJO 形式的结构化数据，应用程序可以直接使用。
2. Spring AI Alibaba 的 `ReactAgent.Builder` 通过 `outputSchema` 和 `outputType` 方法处理结构化输出。当您设置所需的结构化输出模式时，Agent 会自动在用户消息中增加模式指令，模型会根据指定的格式生成数据。

```java
ReactAgent agent = ReactAgent.builder()
  .name("agent")
  .model(chatModel)
  .outputSchema(schemaString)  // Custom JSON schema as String
  // OR
  .outputType(MyClass.class)   // Java class - auto-converted to schema
  .build();
```

## 1. 输出格式选项

1. Spring AI Alibaba 支持两种方式控制结构化输出：
* **`outputSchema(String schema)`**: 提供 JSON schema 字符串。推荐使用 `BeanOutputConverter` 从 Java 类自动生成 schema，也可以手动提供自定义的 schema 字符串
* **`outputType(Class<?> type)`**: 提供 Java 类 - 使用 `BeanOutputConverter` 自动转换为 JSON schema（推荐方式，类型安全）
* **不指定**: 返回非结构化的自然语言响应
2. **推荐做法** ：使用 `BeanOutputConverter` 生成 schema，既保证了类型安全，又实现了自动 schema 生成，代码更易维护。
3. 结构化响应在 Agent 的 `AssistantMessage` 中作为 JSON 文本返回，可以解析为您需要的格式。

## 2. 输出 Schema 策略

1. 您可以使用 `BeanOutputConverter` 从 Java 类自动生成 JSON schema，或者直接提供 JSON schema 字符串。推荐使用 `BeanOutputConverter` 以获得类型安全和自动 schema 生成。

### 2.1 方法签名

```java
Builder outputSchema(String outputSchema)
```

1. **参数:**
* `outputSchema` (String, 必需): 定义结构化输出格式的 JSON schema 字符串。可以通过 `BeanOutputConverter.getFormat()` 方法从 Java 类自动生成，也可以手动提供自定义的 schema 字符串。

### 2.2 示例

1. **基本 JSON Schema:**
2. 使用 `BeanOutputConverter` 从 Java 类自动生成 JSON Schema：

```java
import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.converter.BeanOutputConverter;

// 定义输出类型
public static class ContactInfo {
  private String name;
  private String email;
  private String phone;

  // Getters and Setters
  public String getName() { return name; }
  public void setName(String name) { this.name = name; }
  public String getEmail() { return email; }
  public void setEmail(String email) { this.email = email; }
  public String getPhone() { return phone; }
  public void setPhone(String phone) { this.phone = phone; }
}

// 使用 BeanOutputConverter 生成 outputSchema
BeanOutputConverter<ContactInfo> outputConverter = new BeanOutputConverter<>(ContactInfo.class);
String format = outputConverter.getFormat();

ReactAgent agent = ReactAgent.builder()
  .name("contact_extractor")
  .model(chatModel)
  .outputSchema(format)
  .build();

AssistantMessage result = agent.call(
  "从以下信息提取联系方式：张三，zhangsan@example.com，(555) 123-4567"
);

System.out.println(result.getText());
// 输出: {"name": "张三", "email": "zhangsan@example.com", "phone": "(555) 123-4567"}
```

3. **复杂嵌套 Schema:**
4. 使用 `BeanOutputConverter` 处理复杂嵌套结构：

```java
import org.springframework.ai.converter.BeanOutputConverter;

// 定义输出类型（包含嵌套类）
public static class ProductReview {
  private int rating;
  private String sentiment;
  private String[] keyPoints;
  private ReviewDetails details;

  // Getters and Setters
  public int getRating() { return rating; }
  public void setRating(int rating) { this.rating = rating; }
  public String getSentiment() { return sentiment; }
  public void setSentiment(String sentiment) { this.sentiment = sentiment; }
  public String[] getKeyPoints() { return keyPoints; }
  public void setKeyPoints(String[] keyPoints) { this.keyPoints = keyPoints; }
  public ReviewDetails getDetails() { return details; }
  public void setDetails(ReviewDetails details) { this.details = details; }

  public static class ReviewDetails {
      private String[] pros;
      private String[] cons;
      // Getters and Setters
  }
}

// 使用 BeanOutputConverter 生成 outputSchema
BeanOutputConverter<ProductReview> outputConverter = new BeanOutputConverter<>(ProductReview.class);
String format = outputConverter.getFormat();

ReactAgent agent = ReactAgent.builder()
  .name("review_analyzer")
  .model(chatModel)
  .outputSchema(format)
  .build();

AssistantMessage result = agent.call(
  "分析评价：这个产品很棒，5星好评。配送快速，但价格稍贵。"
);

System.out.println(result.getText());
// 输出: {"rating": 5, "sentiment": "正面", "keyPoints": [...], "details": {...}}
```

5. **结构化分析 Schema:**
6. 使用 `BeanOutputConverter` 处理包含实体识别的复杂结构：

```java
import org.springframework.ai.converter.BeanOutputConverter;

// 定义输出类型（包含嵌套实体类）
public static class TextAnalysis {
  private String summary;
  private String[] keywords;
  private String sentiment;
  private Entities entities;

  // Getters and Setters
  public String getSummary() { return summary; }
  public void setSummary(String summary) { this.summary = summary; }
  public String[] getKeywords() { return keywords; }
  public void setKeywords(String[] keywords) { this.keywords = keywords; }
  public String getSentiment() { return sentiment; }
  public void setSentiment(String sentiment) { this.sentiment = sentiment; }
  public Entities getEntities() { return entities; }
  public void setEntities(Entities entities) { this.entities = entities; }

  public static class Entities {
      private String[] persons;
      private String[] locations;
      private String[] organizations;
      // Getters and Setters
  }
}

// 使用 BeanOutputConverter 生成 outputSchema
BeanOutputConverter<TextAnalysis> outputConverter = new BeanOutputConverter<>(TextAnalysis.class);
String format = outputConverter.getFormat();

ReactAgent agent = ReactAgent.builder()
  .name("text_analyzer")
  .model(chatModel)
  .outputSchema(format)
  .build();

AssistantMessage result = agent.call(
  "分析这段文字：昨天，李明在北京参加了阿里巴巴公司的技术大会，感受到了创新的力量。"
);

System.out.println(result.getText());
```

7. 使用 `BeanOutputConverter` 生成 schema 提供了类型安全和自动生成的优势。如果您需要完全自定义的 schema 格式，也可以直接提供 JSON schema 字符串。 `outputSchema` 方法支持两种方式，为您提供最大的灵活性。

## 3. 输出类型策略

1. 对于类型安全的结构化输出，您可以提供 Java 类，Spring AI Alibaba 将使用 `BeanOutputConverter` 自动将其转换为 JSON schema。这种方法确保了编译时类型安全和自动 schema 生成。

### 3.1 方法签名

```java
Builder outputType(Class<?> outputType)
```

1. **参数:**
* `outputType` (`Class<?>`, 必需): 定义输出结构的 Java 类。该类应该是带有标准 getter 和 setter 的 POJO。

### 3.2 示例

1. 使用 `outputType` 是最简洁的方式，框架会自动使用 `BeanOutputConverter` 将 Java 类转换为 JSON schema：

```java
import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import com.alibaba.cloud.ai.graph.checkpoint.savers.MemorySaver;
import org.springframework.ai.chat.messages.AssistantMessage;

// 定义输出类型
public static class ContactInfo {
  private String name;
  private String email;
  private String phone;

  // Getters and Setters
  public String getName() { return name; }
  public void setName(String name) { this.name = name; }
  public String getEmail() { return email; }
  public void setEmail(String email) { this.email = email; }
  public String getPhone() { return phone; }
  public void setPhone(String phone) { this.phone = phone; }
}

// 直接使用 outputType，框架会自动处理 schema 转换
ReactAgent agent = ReactAgent.builder()
  .name("contact_extractor")
  .model(chatModel)
  .outputType(ContactInfo.class)
  .saver(new MemorySaver())
  .build();

AssistantMessage result = agent.call(
  "从以下信息提取联系方式：张三，zhangsan@example.com，(555) 123-4567"
);

System.out.println(result.getText());
// 输出: {"name": "张三", "email": "zhangsan@example.com", "phone": "(555) 123-4567"}
```

2. **`outputType` vs `outputSchema`** ：
* `outputType`: 更简洁，直接传入 Java 类，框架自动处理（ **推荐** ）
* `outputSchema`: 需要手动使用 `BeanOutputConverter` 生成 schema，或提供自定义字符串，提供更多控制

## 4. 工作原理

1. 当 outputFormat 或 outputType 被指定时，Spring AI Alibaba 会自动选择：
* 当大模型服务支持 “原生结构化输出” 时（目前支持 OpenAiChatModel、DashScopeChatModel），自动使用模型内置的结构化输出能力（这也是目前最稳定、可靠的方式，因为模型服务会自动提供校验支持）。
* 针对其他没有 “原生结构化输出” 的模型，Spring AI Alibaba 会使用内置的 ToolCall策略，通过一个动态的 ToolCall 来格式化模型输出。
2. 结构化响应将在 Agent 的状态对象 OverAllState 中返回，可通过 `structured_output` 读取。

### 4.1 模型原生结构化输出

1. 比如，针对 DashScopeChatModel 模型，在配置 outputSchema 或 outputType 后，Spring AI Alibaba 会自动设置如下参数，以启用模型原生结构化输出能力。

```java
ChatOptions options = DashScopeChatOptions.builder()
.withResponseFormat(
    DashScopeResponseFormat.builder()
        .type(DashScopeResponseFormat.Type.JSON_OBJECT)
        .build())
.build();
```

2. 同时，Spring AI Alibaba 框架会增强系统 Prompt，引导模型输出格式化内容

```java
// In AgentLlmNode.augmentUserMessage() method
public void augmentUserMessage(List<Message> messages, String outputSchema) {
  if (!StringUtils.hasText(outputSchema)) {
      return;
  }

  for (int i = messages.size() - 1; i >= 0; i--) {
      Message message = messages.get(i);
      if (message instanceof UserMessage userMessage) {
          messages.set(i, userMessage.mutate()
              .text(userMessage.getText() + System.lineSeparator() + outputSchema)
              .build());
          break;
      }
  }
}
```

> 注意，相比于 DashScope 模型是通过增强 Prompt 提示词实现最终的 JSON 格式，实现的是一个尽最大努力的效果，OpenAI 模型则是在模型 API 层面支持 Json 格式，提供格式的严格保证支持。

### 4.2 ToolCall 结构化输出

1. 对于不支持原生结构化输出的模型，Spring AI Alibaba 支持通过调用工具来实现相同效果。此方法适用于所有支持工具调用的模型，即大多数现代模型。

## 5. 错误处理

1. 模型可能不总是返回格式完美的 JSON。以下是处理潜在问题的策略:

### 5.1 Try-Catch 模式

```java
ReactAgent agent = ReactAgent.builder()
  .name("data_extractor")
  .model(chatModel)
  .outputType(DataOutput.class)
  .build();

try {
  AssistantMessage result = agent.call("提取数据");
  ObjectMapper mapper = new ObjectMapper();
  DataOutput data = mapper.readValue(result.getText(), DataOutput.class);
  // 处理数据
} catch (JsonProcessingException e) {
  System.err.println("JSON解析失败: " + e.getMessage());
  System.err.println("原始输出: " + result.getText());
  // 回退处理
}
```

### 5.2 验证模式

```java
public class ValidatedOutput {
  private String title;
  private Integer rating;

  public void validate() throws IllegalArgumentException {
      if (title == null || title.isEmpty()) {
          throw new IllegalArgumentException("标题不能为空");
      }
      if (rating != null && (rating < 1 || rating > 5)) {
          throw new IllegalArgumentException("评分必须在1-5之间");
      }
  }

  // Getter 和 Setter 方法...
}

AssistantMessage result = agent.call("生成评价");
ValidatedOutput output = mapper.readValue(result.getText(), ValidatedOutput.class);
output.validate();  // 如果无效则抛出异常
```

### 5.3 重试模式

```java
int maxRetries = 3;
DataOutput data = null;

for (int i = 0; i < maxRetries; i++) {
  try {
      AssistantMessage result = agent.call("提取数据");
      data = mapper.readValue(result.getText(), DataOutput.class);
      break;  // 成功
  } catch (Exception e) {
      if (i == maxRetries - 1) {
          throw new RuntimeException("多次尝试后仍然失败", e);
      }
      System.out.println("第" + (i + 1) + "次尝试失败，重试中...");
  }
}
```

1. Spring AI Alibaba 专注于简单性和灵活性，允许开发者在显式 schema 字符串（最大控制）和 Java 类（类型安全）之间进行选择。

## 6. 相关文档

* [Agents](https://java2ai.com/docs/frameworks/agent-framework/tutorials/agents) - 了解 ReactAgent 功能
* [Models](https://java2ai.com/docs/frameworks/agent-framework/tutorials/models) - 支持的聊天模型
* [Messages](https://java2ai.com/docs/frameworks/agent-framework/tutorials/messages) - 消息类型和处理
