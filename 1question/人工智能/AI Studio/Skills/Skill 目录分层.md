---
title: "Skill 目录分层"
tags:
  - "人工智能"
  - "人工智能/AI Studio"
  - "人工智能/AI Studio/Skills"
  - "Skill 目录分层"
  - "Skills"
  - "AI Studio"
updated: 2026-04-16
---
# Skill 目录分层

给我讲解下skill的目录分层

**Skill 的目录分层** 主要指的是目前 AI Agent 领域（尤其是 **Claude / Anthropic 的 Agent Skills** ，也叫 Claude Skills 或 Claude Code Skills）中，一个 **Skill** 如何以 **目录（文件夹）** 的形式组织结构。

一个 Skill 本质上就是一个 **文件夹** ，里面打包了指令、脚本、参考资料等，让 AI Agent 在处理特定任务时能“像专家一样”工作。它的核心设计理念是 **渐进式披露（Progressive Disclosure）** ，即分层加载内容，避免一次性把所有信息塞进上下文（节省 Token，提高效率）。

## 1\. Skill 的基本目录结构（推荐/官方常见形式）

一个典型的 Skill 目录长这样：

```markdown
my-skill/                  # ← Skill 的文件夹名（建议用 kebab-case，如 pdf-form-filler）
├── SKILL.md               # 必需！核心文件，包含所有指令
├── scripts/               # 可选：可执行脚本（Python、Bash、Node.js 等）
│   ├── process.py
│   └── validate.sh
├── references/            # 可选：额外参考文档、模板、API 说明
│   ├── api-guide.md
│   └── examples.md
├── assets/                # 可选：静态资源（图片、模板、字体等）
│   └── report-template.md
└── ...                    # 其他自定义文件/子文件夹
```
- **文件夹命名规范** ：用小写英文字母 + 连字符（kebab-case），例如 notion-project-setup。不要用空格、下划线或大写字母。
- **SKILL.md 必须精确命名为 SKILL.md** （大小写敏感，不能是 skill.md 或 README.md）。

## 2\. 内容分层设计（最核心的“目录分层”概念）

Skill 采用 **三层渐进式披露架构** ，AI Agent 不会一次性加载全部内容，而是按需分层读取：

- **第一层（元数据 / 目录索引）** —— 始终加载 位于 SKILL.md 文件开头的 **YAML Frontmatter** （前置元数据）。 格式示例：
	```markdown
	---
	name: pdf-form-filler
	description: 用于填充、验证和处理 PDF 表单。当用户提到 PDF、表单、填写、提取字段等时使用。
	---
	```
	- 只包含 name 和 description（description 必须说明“做什么 + 什么时候用”）。
		- AI 先扫描所有 Skill 的这一层，形成“技能列表”，判断是否需要这个 Skill。
		- 体积很小（通常 < 100 Token），常驻系统提示词中。
- **第二层（核心指令 / 详细手册）** —— 相关时加载 SKILL.md 中 YAML 之后的所有 Markdown 内容。 这里写具体的 **操作步骤、工作流、规则、约束、示例** 等。 当 AI 判断当前任务匹配 description 时，才把整个第二层加载进上下文。
- **第三层（参考资料 / 链接文件）** —— 按需加载 通过 references/、examples.md、FORMS.md 等额外文件。 在 SKILL.md 中用文件名或链接引用它们（例如 “参考 references/api-guide.md”）。 AI 只有在真正需要细节时，才会进一步读取这些文件。 这层可以无限扩展（子文件夹、脚本等），适合复杂 Skill。

这种分层像一本 **带目录的说明书** ：AI 先看目录（第一层）→ 决定是否翻开正文（第二层）→ 需要时再查附录（第三层）。

## 3\. 实际示例（来自官方/社区常见 Skill）
- **简单 Skill** ：可能只有一个 SKILL.md。
- **复杂 Skill** （如文档处理）：
	```markdown
	document-skills/pdf/
	├── SKILL.md
	├── forms.md
	├── reference.md
	└── scripts/
	    ├── fill_form.py
	    └── validate.py
	```
## 4\. Skill 的存放位置（影响作用范围）
- **项目级（工作区范围）** ：放在项目根目录下的.claude/skills/ 或.agent/skills/（仅当前项目生效，适合项目专属流程）。
- **全局范围** ：放在用户主目录的 ~/.claude/skills/ 或 ~/.gemini/antigravity/skills/（所有项目都能用，适合通用工具，如“格式化 JSON”“生成 UUID”）。

Claude 会按优先级自动发现并加载这些目录。

## 5\. 为什么这样设计目录分层？
- **节省 Token** ：不相关 Skill 只占用第一层极小空间。
- **可组合性** ：多个 Skill 可以同时加载，互相配合。
- **可维护性** ：指令、脚本、参考资料分开放，便于更新和复用。
- **可移植性** ：一个 Skill 目录可以直接复制到不同环境（Claude.ai、Claude Code、API）使用。

如果你是想自己创建一个 Skill，推荐先从一个简单的 SKILL.md 开始，写好 YAML + 清晰的工作流步骤，再逐步添加 scripts/ 和 references/。

如果你指的是其他上下文的 “skill 目录分层”（比如 Android 技能树、某个特定框架的目录结构），可以再补充一些细节，我可以针对性地再讲解！