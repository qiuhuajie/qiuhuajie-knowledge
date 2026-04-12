---
name: my-markdown
description: Apply this skill to all Obsidian markdown note rewriting and editing tasks for consistent personal writing style.
---

# My Markdown Style

1. 使用 # 、## 等多级标题对文档进行层级安排
2. 每段话都需要进行编号：
    2.1 所有内容要使用 1. 2. 或 * 等markdown格式进行编号
        - 如果当前标题下只有一段话，则使用 * 编号
        - 如果当前标题下有多段话，则需要根据内容判断段与段之间是递进关系，还是并列关系。如果是并列关系，则使用 * 编号，如果是递进关系，则使用 1. 2. 编号
    2.2 每个新标题下，要从 1. 开始重新编号
3. 缩进
    - 根据图片/代码块上面是否有文字进行缩进
    - 如果前面有文字，则添加4个空格缩进
    - 如果前面没有文字，则保持原样
4. 改写是保持原内容的 加粗 （** **），高亮（== ==）。禁止额外添加任何强调高亮和加粗。

## 图片缩进示例。
1. xxx
2. xxx
    ![[xxxxxx|500]]

## 代码块内的缩进示例，代码换行要使用8个缩进符号进行缩进。
```java
public Result<VisaFreeEntryPolicyQueryRes> queryVisaFreeEntryPolicy(VisaFreeEntryPolicyQueryReq request) {
        try {
                xxxx
        } catch (Exception e) {
                xxx
        }
}
```

## 代码块和上方文字的缩进示例，注意不止代码块的内容，需要把代码块标签```java 本身也需要加上对应的缩进。
1. xxx
2. 以下是xxx的代码示例：
	```java
	public Result<VisaFreeEntryPolicyQueryRes> queryVisaFreeEntryPolicy(VisaFreeEntryPolicyQueryReq request) {
            try {
                    xxxx
            } catch (Exception e) {
                    xxx
            }
	}
	```


