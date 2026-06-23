---
title: "Spring AI如何构建流式输出的ReAct Agent"
source: "https://ata.atatech.org/articles/11020428852?spm=ata.23639746.0.0.20fa11dceffq6U"
author:
published:
created: 2026-06-23
description:
---
# Spring AI如何构建流式输出的ReAct Agent

中国电商事业群-淘天集团

勋章

粉丝 5影响力 48

** 15

** 17

** 1

** 原创文章

**

[宗志伟(铁钢)](https://ata.atatech.org/users/11002116158)

** 朗读

** 字号

** 笔记

** 分享 **

朗读文章12:19

**

## 引言

Spring AI 1.0.0版本上月底发布至今，我发现目前的java应用、示例除了直接用模型的steam输出，其他的大部分都是block输出，在代码里使用reactor写一些回调代码确实比较麻烦，本文从头开始一步步通过Spring AI构建一个纯流式输出，支持MCP的ReAct Agent，整体流程参考OpenManus的代码。

## OpenManus 结构

我们看下这个号称三小时就复刻了Manus的是怎么个事， 代码做了删减，取核心部分

## main()

```java
async def main():
    agent = Manus()
    await agent.run(prompt)
```

main方法里面启动了一个Manus, 接收用户输出;

## run()

Manus -> ToolCallAgent -> ReActAgent -> BaseAgent构成了一条继承链；

BaseAgent里写了run方法的模版,

```java
async def run(self, request: Optional[str] = None) -> str:
    if self.state != AgentState.IDLE:
        raise RuntimeError(f"Cannot run agent from state: {self.state}")

    if request:
        self.update_memory("user", request)

    async with self.state_context(AgentState.RUNNING):
        while (
            self.current_step < self.max_steps and self.state != AgentState.FINISHED
        ):
            self.current_step += 1
            step_result = await self.step()

        if self.current_step >= self.max_steps:
            self.current_step = 0
            self.state = AgentState.IDLE
```

好的，每个agent实例维护一个自身的状态机和执行step，通过状态和step控制什么时候跳出循环，其他时间都在循环里面跑step

## step()

step的模版在ReactAgent中, 实现在ToolCallAgent里

```java
async def step(self) -> str:
    """Execute a single step: think and act."""
    should_act = await self.think()
    if not should_act:
        return "Thinking complete - no action needed"
    return await self.act()
```

每个步骤做think-> act循环，直到模型决定不再should\_act, 这个字段是通过模型决定是否使用工具判断的，依赖模型的Function Calling能力。

## think()

```java
async def think(self) -> bool:
    # 保存记忆
    if self.next_step_prompt:
        user_msg = Message.user_message(self.next_step_prompt)
        self.messages += [user_msg]

    # 调用模型
    response = await self.llm.ask_tool(
        messages=self.messages,
        system_msgs=(
            [Message.system_message(self.system_prompt)]
            if self.system_prompt
            else None
        ),
        tools=self.available_tools.to_params(),
        tool_choice=self.tool_choices,
    )

    # 工具判断
    self.tool_calls = tool_calls = (
        response.tool_calls if response and response.tool_calls else []
    )
    content = response.content if response and response.content else ""

    # 保存模型回复
    assistant_msg = (
        Message.from_tool_calls(content=content, tool_calls=self.tool_calls)
        if self.tool_calls
        else Message.assistant_message(content)
    )
    self.memory.add_message(assistant_msg)

    return bool(self.tool_calls)
```

1. 每次think之前给模型下一步提示牵引任务继续完成，openManus这么写的
	"If you want to stop interaction, use `terminate` tool/function call.",
2. 通过模型api的tool\_calls字段，判断模型是否决定调用工具-> think的结果。tool\_choice这个字段也是openai的api字段，可以决定模型是否使用工具/强制使用，有兴趣的同学可以看下。
3. 保存模型的回复
## act()

```java
async def act(self) -> str:
    for command in self.tool_calls:
        # Reset base64_image for each tool call
        self._current_base64_image = None

        result = await self.execute_tool(command)

        # Add tool response to memory
        tool_msg = Message.tool_message(
            content=result,
            tool_call_id=command.id,
            name=command.function.name,
            base64_image=self._current_base64_image,
        )
        self.memory.add_message(tool_msg)
```

act里面做工具的调用和工具返回结果 observation的保存，openManus有调用浏览器的工具和python执行工具，这不是我们的重点

## 总结

OpenManus通过构建ReAct单智能体进行思考-行动-观察，行动的时候调用浏览器，代码解释器，mcp工具，直到任务完成。

## 开始正题

## Flux&Mono是什么

我们发现Spring AI的steam返回的是FLux，这是个什么东西。

```java
@GetMapping(value = "/tgtest", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<String> tgtest(
    HttpServletResponse response) {
    modifyHeader(response);
    return SpringUtil.getBean(ChatClient.class).prompt("介绍一下自己").stream().content();
```

本人约两年前接触过这个东西，之前看到有同学在网关里面咔咔用这个东西写了一串点，写法着实抽象，难以理解。幸好现在有大模型，可以解释一些之前难以理解的东西。

我们知道模型的回复是预测下一个token，所以可以不用等所有的数据返回，预测一个字返回一个，几乎所有的模型厂商api都会支持steam输出，所以不用Spring AI，直接调用模型的API输出，也可以获得这个效果，Spring AI在上层做了抽象，屏蔽了模型的细节。

> 在 Java 中，Reactor 是一个用于响应式编程的库，由 Pivotal（现为 VMware）开发，广泛用于构建高性能、异步、非阻塞的应用程序。它是基于 Reactive Streams 规范的实现，专注于处理数据流的异步处理和背压（backpressure）管理。
> Reactor 的核心概念
> Reactor 的核心是两个关键的响应式类型：Flux 和 Mono。它们代表了两种不同类型的异步数据流：
> 
> 1. Flux
> 定义：Flux 是一个异步序列，可以发出 0 到 N 个元素，并最终完成或出错。
> 适用场景：适合处理多个数据项的流，例如从数据库查询多条记录、处理多个事件等。
> 特点：
> 支持 背压（Backpressure），即消费者可以控制生产者的发送速率，避免内存溢出。
> 提供丰富的操作符（Operators）对数据流进行转换、过滤、合并等操作。
> 2. Mono
> 定义：Mono 是一个异步序列，最多只能发出 0 或 1 个元素，并最终完成或出错。
> 适用场景：适合处理单个结果或空值的场景，例如数据库查询单条记录、HTTP 请求返回单个响应等。
> 特点：
> 与 Flux 类似，但只能处理单个值或空值。
> 常用于表示完成、空值或错误。

嘟嘟一大堆，简单的理解 SpringAI把模型API的http返回封装成了Flux，Flux是一个数据流，模型返回的字会不断的从里面发射出来。我们的需求是在代码逻辑执行思考-行动-观察的过程中发射一些数据出来，那么，如何把这个写在代码里？需要用到FluxSink

> 在 Reactor 中，FluxSink 是一个用于 动态生成 Flux 数据流 的接口，允许你手动控制数据的发射过程，尤其适用于需要 逐步生成数据 或 异步/外部数据源集成 的场景。

通过Flux的create可以创建一个流，通过lambda参数sink可以创建一个FluxSink，我们把sink往下传，在需要的时候把数据发射出来就行了，我们先简单的按照OpenManus的继承结构创建好代码。

## run()

首先创建一个BaseAgent

```java
/**
 * some desc
 *
 * @author tiegang
 * @version 2025/6/22
 */
public abstract class BaseAgent {

    @Getter
    private final AgentContext agentContext;
    @Getter
    @Setter
    private AgentState agentState = AgentState.IDLE;

    @Getter
    private int currStep = 0;
    @Getter
    private final int maxStep;

    public BaseAgent(AgentContext agentContext, int maxStep) {
        this.agentContext = agentContext;
        this.maxStep = maxStep;
    }

    /**
     * 状态
     */
    @Getter
    public enum AgentState {
        IDLE,
        RUNNING,
        FINISHED,
        ERROR
    }

    public Flux<String> run() {
        return Flux.create(sink -> {
            setAgentState(AgentState.RUNNING);
            AtomicInteger stepCounter = new AtomicInteger(0);
            executeStep(sink, stepCounter);
        });
    }

    void executeStep(FluxSink<String> sink, AtomicInteger stepCounter) {
        currStep = stepCounter.get();
        if (!AgentState.RUNNING.equals(getAgentState())) {
            sink.next("[DONE]");
            sink.complete();
            return;
        }

        if (stepCounter.get() >= maxStep) {
            sink.next("[DONE]");
            sink.complete();
            return;
        }

        step(sink)
            .doOnSuccess(v -> {
                stepCounter.incrementAndGet();
                executeStep(sink, stepCounter);
            })
            .doOnError(e -> {
                sink.error(e);
                sink.complete();
            })
            .doOnSubscribe(s -> {
                sink.next("execute step\n");
            })
            .subscribe();
    }

    public abstract Mono<Boolean> step(FluxSink<String> sink);
}
```

构建一个上下文存储信息:

```java
/**
 * some desc
 *
 * @author tiegang
 * @version 2025/6/22
 */
@Builder
public class AgentContext {
    private ChatClient chatClient;
    private ChatMemory chatMemory;
    private List<ToolCallback> toolCallbacks;
    private String systemPrompt;
    private String query;
    private String sessionId;
}
```

在BaseAgent中写上run方法的模版，循环写起来比较麻烦，我们通过递归编写它。

分析一下这段代码做了什么：

1. run方法创建了一个Flux, 这个Flux会在前端发起请求的时候subscribe。在run内部执行一个递归方法executeStep，当agent不再running / 超过最大步数的时候到达递归基，我们回传SSE的结束\[DONE\], 并把sink关闭。
2. step的几个回调方法中
- 成功时进入下一步
- 失败时关闭Flux并返回
- 订阅时发射一个字段出去，这个可以让前端感知到每个步骤在执行，可以做一些步骤执行的动画。
3. 随后我们直接触发subscribe，因为step是另外一个Mono，Flux/Mono不订阅的时候是没办法触发的，仅仅是代码声明。

## step()

我们创建ReAgentAgent，在它里面写好step的模版和think，act的抽象方法：

```java
/**
 * some desc
 *
 * @author tiegang
 * @version 2025/6/22
 */
public abstract class ReActAgent extends BaseAgent {
    public abstract Mono<Boolean> think(FluxSink<String> sink);

    public abstract void act(FluxSink<String> sink);

    public Mono<Boolean> step(FluxSink<String> sink) {
        return think(sink).log().mapNotNull(b -> {
            if (b != null && b) {
                act(sink);
            } else {
                //    思考结束
                setAgentState(AgentState.FINISHED);
            }
            return true;
        });
    }
}
```

think返回一个Mono，对应OpenManus的shoud\_act，获取到思考结果以后，当判断需要使用工具的时候，进入act，否则设置agent的状态为结束，这样在下一个step的时候就会返回了。

## think() & act()

```java
/**
 * some desc
 *
 * @author tiegang
 * @version 2025/6/22
 */
public class ToolCallAgent extends ReActAgent {
    @Override
    public Mono<Boolean> think(FluxSink<String> sink) {

        AgentContext agentContext = getAgentContext();
        ChatOptions chatOptions = OpenAiChatOptions.builder().internalToolExecutionEnabled(false).build();
        String userMessage = "请回顾一下用户的问题, 结合工具的使用结果，进行下一个步骤";
        if (getCurrStep() == 0) {
            userMessage = agentContext.getQuery();
        }

        List<Message> memory = agentContext.getChatMemory().get(agentContext.getSessionId());
        List<Message> messages = new ArrayList<>(memory);
        messages.add(new SystemMessage(agentContext.getSystemPrompt()));
        messages.add(new UserMessage(userMessage));
        Prompt prompt = new Prompt(messages);

        agentContext.getChatMemory().add(agentContext.getSessionId(), new UserMessage(userMessage));
        Flux<ChatResponse> chatResponseFlux = agentContext.getChatClient()
            .prompt(prompt)
            .options(chatOptions)
            .toolCallbacks(agentContext.getToolCallbacks())
            .stream()
            .chatResponse();

        return chatResponseFlux.
            transform(c -> new MethodAggregatorWithToolCalls().aggregate(c, chatResponse -> {
                List<ToolCall> toolCalls = chatResponse.getResult().getOutput().getToolCalls();
                agentContext.setDecideTools(toolCalls);
                agentContext.getChatMemory().add(agentContext.getSessionId(),
                    chatResponse.getResult().getOutput());
            })).
            mapNotNull(c -> {
                if (c.getResult() == null) {
                    return "";
                }
                return c.getResult().getOutput().getText();
            })
            .doOnNext(sink::next)
            .doOnError(sink::error)
            .log()
            .then(Mono.defer(
                () -> agentContext.getDecideTools() != null && !agentContext.getDecideTools()
                    .isEmpty() ? Mono.just(true) : Mono.just(false)));
    }

    @Override
    public void act(FluxSink<String> sink) {
        AgentContext agentContext = getAgentContext();
        agentContext.getDecideTools().stream().findFirst().ifPresent(
            toolCall -> {
                if (agentContext.getAutoApprove()) {
                    sink.next("自动使用工具");
                    String callRes = ToolUtils.execute(toolCall, agentContext);
                } else {
                    sink.next("判断是否使用工具" + toolCall);
                    setAgentState(AgentState.FINISHED);
                }
            });
    }
}
```

在think代码中做了以下几件事

1. 设置chatOption internalToolExecutionEnabled = false，这个参数默认为true，Spring AI会在模型返回toolCall的时候，执行工具调用，并拿着结果在再次调用一次模型，再把最终的结果返回来，我们自己控制方法的调用，把这个结果设置为false即可。
2. 手动维护chatMemory，Spring AI可以通过advisor为模型调用自动添加记忆，这是一个切面的原理，stream返回时有个bug，assistant memory写的有问题，这里我们自己维护。
3. chatResponseFlux是拿到的模型返回，由于流式发送，这里的flux每个数据是一个数据块，mapNotNull方法中，我们拿到每一个数据块中的text，并在doOnNext的时候调用sink的next方法返回。then方法在chatResponseFlux完成后回调，返回返回是否应该进行act，这是通过content里面的decideTools判断的
4. 每块数据通过transform进行聚合，聚合完成以后在aggregate方法中进行回调，设置context内部的decideTools，并将assistant的数据存储到记忆里。
5. 把数据流聚合的方法是在源码里面找的，这个MethodAggregator.class，这个方法不会把toolCall设置进去，我添加了一下拿来用了，以下是修改后的代码

```java
public class MethodAggregatorWithToolCalls {

    public Flux<ChatResponse> aggregate(Flux<ChatResponse> fluxChatResponse,
        Consumer<ChatResponse> onAggregationComplete) {

        // Assistant Message
        AtomicReference<StringBuilder> messageTextContentRef = new AtomicReference<>(new StringBuilder());
        // 修改了这里
        AtomicReference<List<ToolCall>> toolCallRef = new AtomicReference<>();
        AtomicReference<Map<String, Object>> messageMetadataMapRef = new AtomicReference<>();

        // ChatGeneration Metadata
        AtomicReference<ChatGenerationMetadata> generationMetadataRef = new AtomicReference<>(
            ChatGenerationMetadata.NULL);

        // Usage
        AtomicReference<Integer> metadataUsagePromptTokensRef = new AtomicReference<Integer>(0);
        AtomicReference<Integer> metadataUsageGenerationTokensRef = new AtomicReference<Integer>(0);
        AtomicReference<Integer> metadataUsageTotalTokensRef = new AtomicReference<Integer>(0);

        AtomicReference<PromptMetadata> metadataPromptMetadataRef = new AtomicReference<>(PromptMetadata.empty());
        AtomicReference<RateLimit> metadataRateLimitRef = new AtomicReference<>(new EmptyRateLimit());

        AtomicReference<String> metadataIdRef = new AtomicReference<>("");
        AtomicReference<String> metadataModelRef = new AtomicReference<>("");

        return fluxChatResponse.doOnSubscribe(subscription -> {
            messageTextContentRef.set(new StringBuilder());
            messageMetadataMapRef.set(new HashMap<>());
            metadataIdRef.set("");
            metadataModelRef.set("");
            metadataUsagePromptTokensRef.set(0);
            metadataUsageGenerationTokensRef.set(0);
            metadataUsageTotalTokensRef.set(0);
            metadataPromptMetadataRef.set(PromptMetadata.empty());
            metadataRateLimitRef.set(new EmptyRateLimit());
            // 修改了这里
            toolCallRef.set(List.of());

        }).doOnNext(chatResponse -> {

            if (chatResponse.getResult() != null) {
                if (chatResponse.getResult().getMetadata() != null
                    && chatResponse.getResult().getMetadata() != ChatGenerationMetadata.NULL) {
                    generationMetadataRef.set(chatResponse.getResult().getMetadata());
                }
                if (chatResponse.getResult().getOutput().getText() != null) {
                    messageTextContentRef.get().append(chatResponse.getResult().getOutput().getText());
                }
                if (chatResponse.getResult().getOutput().getMetadata() != null) {
                    messageMetadataMapRef.get().putAll(chatResponse.getResult().getOutput().getMetadata());
                }
                // 修改了这里
                if (chatResponse.getResult().getOutput().getToolCalls() != null) {
                    toolCallRef.set(chatResponse.getResult().getOutput().getToolCalls());
                }
            }
            if (chatResponse.getMetadata() != null) {
                if (chatResponse.getMetadata().getUsage() != null) {
                    Usage usage = chatResponse.getMetadata().getUsage();
                    metadataUsagePromptTokensRef.set(
                        usage.getPromptTokens() > 0 ? usage.getPromptTokens() : metadataUsagePromptTokensRef.get());
                    metadataUsageGenerationTokensRef.set(usage.getCompletionTokens() > 0 ? usage.getCompletionTokens()
                        : metadataUsageGenerationTokensRef.get());
                    metadataUsageTotalTokensRef
                        .set(usage.getTotalTokens() > 0 ? usage.getTotalTokens() : metadataUsageTotalTokensRef.get());
                }
                if (chatResponse.getMetadata().getPromptMetadata() != null
                    && chatResponse.getMetadata().getPromptMetadata().iterator().hasNext()) {
                    metadataPromptMetadataRef.set(chatResponse.getMetadata().getPromptMetadata());
                }
                if (chatResponse.getMetadata().getRateLimit() != null
                    && !(metadataRateLimitRef.get() instanceof EmptyRateLimit)) {
                    metadataRateLimitRef.set(chatResponse.getMetadata().getRateLimit());
                }
                if (StringUtils.hasText(chatResponse.getMetadata().getId())) {
                    metadataIdRef.set(chatResponse.getMetadata().getId());
                }
                if (StringUtils.hasText(chatResponse.getMetadata().getModel())) {
                    metadataModelRef.set(chatResponse.getMetadata().getModel());
                }
            }
        }).doOnComplete(() -> {

            var usage = new DefaultUsage(metadataUsagePromptTokensRef.get(), metadataUsageGenerationTokensRef.get(),
                metadataUsageTotalTokensRef.get());

            var chatResponseMetadata = ChatResponseMetadata.builder()
                .id(metadataIdRef.get())
                .model(metadataModelRef.get())
                .rateLimit(metadataRateLimitRef.get())
                .usage(usage)
                .promptMetadata(metadataPromptMetadataRef.get())
                .build();

            // 修改了这里
            onAggregationComplete.accept(new ChatResponse(List.of(new Generation(
                new AssistantMessage(messageTextContentRef.get().toString(), messageMetadataMapRef.get(),
                    toolCallRef.get()),
                generationMetadataRef.get())), chatResponseMetadata));

            messageTextContentRef.set(new StringBuilder());
            messageMetadataMapRef.set(new HashMap<>());
            metadataIdRef.set("");
            metadataModelRef.set("");
            metadataUsagePromptTokensRef.set(0);
            metadataUsageGenerationTokensRef.set(0);
            metadataUsageTotalTokensRef.set(0);
            metadataPromptMetadataRef.set(PromptMetadata.empty());
            metadataRateLimitRef.set(new EmptyRateLimit());

        });
    }

    public record DefaultUsage(Integer promptTokens, Integer completionTokens, Integer totalTokens) implements Usage {

        @Override
        public Integer getPromptTokens() {
            return promptTokens();
        }

        @Override
        public Integer getCompletionTokens() {
            return completionTokens();
        }

        @Override
        public Integer getTotalTokens() {
            return totalTokens();
        }

        @Override
        public Map<String, Integer> getNativeUsage() {
            Map<String, Integer> usage = new HashMap<>();
            usage.put("promptTokens", promptTokens());
            usage.put("completionTokens", completionTokens());
            usage.put("totalTokens", totalTokens());
            return usage;
        }
    }

}
```

act方法比较简单，拿到模型返回的toolCall调用就可以了，需要通过toolCall方法名字找到执行的toolCallBack，调用它的call执行方法，SpringAI现在支持的方法感觉不太统一，我自己把方法存在缓存里面了，下面是我用的ToolUtils

```java
/**
 * some desc
 *
 * @author tiegang
 * @version 2025/6/15
 */
public class ToolUtils {
    private ToolUtils() {}

    public static ToolCallback resolve(String toolName) {
        ToolCallback toolCallback = ToolsCache.get(toolName);
        if (toolCallback == null) {
            toolCallback = SpringUtil.getBean(ToolsCache.class).get(
                toolName + "@Tool");
        }
        if (toolCallback == null) {
            throw new RuntimeException("未找到可用工具");
        }
        return toolCallback;
    }

    public static String execute(ToolCall toolCall, AgentContext context) {
        ToolCallback toolCallback = ToolUtils.resolve(toolCall.name());
        String callRes = toolCallback.call(JSON.parse(toolCall.arguments()).toString());
        context.getChatMemory().add(context.getSessionId(), new ToolResponseMessage(
            Collections.singletonList(new ToolResponse(toolCall.id(), toolCall.name(), callRes))));
        return callRes;
    }

    public static void registerMcpTools(List<ToolCallback> toolCallbacks) {
        toolCallbacks.forEach(toolCallback -> ToolsCache.put(toolCallback.getToolDefinition().name(), toolCallback));
    }

    public static List<ToolCallback> registerAnnotationTool(Class<?> clazz)
        throws NoSuchMethodException, InvocationTargetException, InstantiationException, IllegalAccessException {
        ToolCallback[] from = ToolCallbacks.from(clazz.getDeclaredConstructor().newInstance());
        for (ToolCallback toolCallback : from) {
            SpringUtil.getBean(ToolsCache.class).put(toolCallback.getToolDefinition().name() + "@Tool", toolCallback);
        }
        return Arrays.asList(from);
    }
}
```

在Tools.execute以后，记得把工具的执行记忆添加到memory里面。

cache，简单的map

```java
@Component
public class ToolsCache {
    private static final HashMap<String, ToolCallback> toolsCache = new HashMap<>();

    public static ToolCallback get(String toolName) {
        return toolsCache.get(toolName);
    }

    public static void put(String toolName, ToolCallback toolCallback) {
        toolsCache.put(toolName, toolCallback);
    }

}
```

也可以用SpringAI的org.springframework.ai.model.tool.ToolCallingManager#executeToolCalls，这个方法要传入完整的prompt和chatResponse

## 支持MCP

如果在application中写了Spring AI的mcp配置，spring会自动把配置解析，注入McpClient，可以通过org.springframework.ai.mcp.SyncMcpToolCallbackProvider#getToolCallbacks 这个方法获取到自动注入到注入到mcp工具，拿到ToolCallBack以后就可以用模型返回的 `toolCall.arguments` 作为参数调用了，如果我们想通过sse 链接直接拿到toolCallBack怎么办呢？

我们看下SpringAI的源码怎么解析的就行了-\_-!，有兴趣的同学可以自己看下，我打包了一个工具

```java
/**
 * some desc
 *
 * @author tiegang
 * @version 2025/6/15
 */
public class MCPUtils {

    /**
     * 根据端点获取所有MCP工具
     *
     * @param endPoint
     * @return
     */
    public static List<ToolCallback> getByEndPoint(String key, String endPoint) {
        McpSyncClient mcpClient = getMcpSyncClientByEndPoint(key, endPoint);
        return getToolCallbacks(mcpClient);

    }

    public static List<ToolCallback> getToolCallbacks(McpSyncClient mcpClient) {
        var toolCallbacks = mcpClient.listTools()
            .tools()
            .stream()
            //.filter(tool -> this.toolFilter.test(mcpClient, tool))
            .map(tool -> new SyncMcpToolCallback(mcpClient, tool))
            .toArray(ToolCallback[]::new);
        List<String> duplicateToolNames = ToolUtils.getDuplicateToolNames(toolCallbacks);
        if (!duplicateToolNames.isEmpty()) {
            throw new IllegalStateException(
                "Multiple tools with the same name (%s)".formatted(String.join(", ", duplicateToolNames)));
        }
        return Arrays.asList(toolCallbacks);
    }

    public static McpSyncClient getMcpSyncClientByEndPoint(String key, String endPoint) {
        NamedClientMcpTransport namedTransport = getNamedClientMcpTransport(key, endPoint);
        McpClientCommonProperties commonProperties = SpringUtil.getBean(McpClientCommonProperties.class);
        McpSchema.Implementation clientInfo = new McpSchema.Implementation(
            commonProperties.getName() + " - " + namedTransport.name(),
            "1.0.0");

        McpClient.SyncSpec spec = McpClient.sync(namedTransport.transport())
            .clientInfo(clientInfo)
            .requestTimeout(Duration.ofSeconds(30));

        spec = SpringUtil.getBean(McpSyncClientConfigurer.class).configure(namedTransport.name(), spec);
        var client = spec.build();
        client.initialize();
        return client;
    }

    private static NamedClientMcpTransport getNamedClientMcpTransport(String key, String endPoint) {
        String baseUrl = endPoint;
        ObjectMapper objectMapper = new ObjectMapper();

        String sseEndpoint = endPoint;
        var transport = HttpClientSseClientTransport.builder(baseUrl)
            .sseEndpoint(sseEndpoint)
            .clientBuilder(HttpClient.newBuilder())
            .objectMapper(objectMapper)
            .build();
        return new NamedClientMcpTransport(key, transport);
    }

    public static void closeConnection(List<McpSyncClient> mcpSyncClients) {
        mcpSyncClients.forEach(McpSyncClient::close);
    }

}
```

通过MCPUtils#getMcpSyncClientByEndPoint这个方法，就可以建立mcp连接了，记得要关闭啊。

我自己用的时候会把mcp工具全都放在cache里面，每次调用的时候都建立一次连接，结束以后销毁连接。

```java
private void findTools(AgentExecContext agentExecContext, AgentInfo agentInfo) {
	 List<ToolCallback> toolCallbacks = Lists.newArrayList();
      List<McpSyncClient> mcpSyncClients = Lists.newArrayList();
      CollectionUtils.emptyIfNull(agentInfo.getMcpConfig())
          .forEach(mcpConfig -> {
              McpSyncClient mcpSyncClientByEndPoint = MCPUtils.getMcpSyncClientByEndPoint(mcpConfig.getKey(),
                  mcpConfig.getUrl());
              List<ToolCallback> tbs = MCPUtils.getToolCallbacks(mcpSyncClientByEndPoint);
              toolCallbacks.addAll(tbs);
              mcpSyncClients.add(mcpSyncClientByEndPoint);
          });

      ToolUtils.registerMcpTools(toolCallbacks);
      agentExecContext.setAvaliableTools(toolCallbacks);
      agentExecContext.setMcpSyncClients(mcpSyncClients);
  }
```

## SSE返回给前端

我们在sink里面每次发射一个字符串，按照SSE的协议，格式应该是data: 数据

```java
@GetMapping(value = "/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
 public Flux<ServerSentEvent<String>> chat(@RequestParam("conversationId") String conversationId,
     @RequestParam("query") String query, @RequestParam("autoApprove") Boolean autoApprove,
     @RequestParam("agentId") String agentId,
     HttpServletResponse response) {
     modifyHeader(response);
     return agentGateway.chat(conversationId, query, autoApprove, agentId)
         .map(text -> ServerSentEvent.builder(text).build());
 }

 private static void modifyHeader(HttpServletResponse response) {
     response.setCharacterEncoding("UTF-8");
     response.setHeader("Cache-Control", "no-cache");
     response.setHeader("X-Accel-Buffering", "no");
 }
```

可以通过ServerSentEvent.builder(text).build()把text转换成data: 字符串的格式，字符串里面填什么，比如IdeaTalk填的 `data: {"id":"2013037870","content":"<think>\n好的","firstTokenRt":1494,"traceId":"213e062917505998721628824e8006","modelProvider":"bailianx"}` ，看跟前端的约定了吧。

如果在容器里部署机器使用域名访问，一定要修改返回头 ` response.setHeader("X-Accel-Buffering", "no");`，否则stream输出会被网关缓存统一返回，这样就被网关阻塞了。。。

## 总结

目前市面上的一些ReAct Agent大抵也都是这个原理，比如CLine，不过它没有用FunctionCalling，还是用的Prompt做的工具调用。

SpringAI还有一些问题需要解决，现在没有办法支持工具的SSE调用，这让我们的一些想法，比如做HandOff把agent作为MCP工具调用不太现实，以及有一些奇怪的bug需要修复。

实际上这些在python上很多框架都会给完整的示例，相比python而言，SpringAI还需要很多迭代，包括对多智能体的支持不知道什么时候能出。

新手勿喷，祝Spring AI越来越好，希望对大家有所帮助～

附开箱即用代码 [https://code.alibaba-inc.com/zongzhiwei.zzw/spring-ai-react](https://code.alibaba-inc.com/zongzhiwei.zzw/spring-ai-react)

另外，有没有懂哥回复一下，为什么有工作流还要用SpringAI？为什么？为什么？

END

引言

OpenManus 结构

main()

run()

step()

think()

act()

总结

开始正题

Flux&Mono是什么

run()

step()

think() & act()

支持MCP

SSE返回给前端

总结

有什么问题，和我聊聊吧～

**

内部资料

INTERNAL

405832