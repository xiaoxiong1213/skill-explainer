---
name: skill-explainer
description: 说明每个已安装 Skill 的用途与适用场景。当用户询问"有哪些技能""每个 skill 是干嘛的""XX skill 有什么用/怎么用""帮我梳理/罗列技能清单""技能总览/速查表"等，或需要为一批 skill 生成用途说明时使用。扫描一个或多个 skill 根目录，读取各 SKILL.md 的 name 与 description，整理为分类清单、表格或文档交付。适用于任何支持 Agent Skills 标准的 AI 工具（Codex CLI、Claude Code、GitHub Copilot 等）。
---

# Skill Explainer（技能说明器）

## 概述

扫描一个或多个 skill 根目录，读取每个 SKILL.md 的 frontmatter（`name` + `description`），
输出"每个技能的用途说明"。适用于快速盘点环境里装了哪些技能、每个技能管什么、什么时候该用它。

## 工作流

### 1. 确定扫描范围

先确认要说明哪些技能：默认扫描当前环境已知的全部 skill 根目录。常见位置因工具而异，
例如 `~/.agents/skills`、`~/.codex/skills`、`~/.claude/skills`、`~/.copilot/skills`、
`~/.cursor/skills`，以及仓库级 `.agents/skills`、`.github/skills` 等——以磁盘上实际存在的
目录为准。若用户只关心某个目录或某个技能，缩小范围。

### 2. 运行扫描脚本

```bash
python scripts/list_skills.py <root1> <root2> ... [--top-level] [--plain]
```

- 默认输出 JSON（含 `name`、`description`、`root`、`path`、`level`：`top` 为顶层技能，
  `nested` 为子技能/分支）。
- `--top-level`：只看顶层技能，跳过嵌套子技能（适合"有哪些技能"的总览）。
- `--plain`：直接输出可读文本，适合快速浏览。
- Windows 环境用 `python` 命令运行；路径含空格时用引号包裹。

### 3. 整理与交付

根据用户意图选择交付形式：

- **口头/对话回答**：按分类（业务类 `doubao-*`、飞书办公类 `lark-*`、音视频处理类
  `byted-mediakit-*`、通用工具类 `sheet/ppt/word/pdf/html`、用户自定义技能等）
  给出名称 + 一句话用途，重点说明触发场景。分类可按实际技能前缀调整。
- **清单/速查表**：用脚本 JSON 数据生成 Markdown 表格、CSV、HTML，或写入在线
  文档/表格，每行一个技能：名称、用途、所在目录。
- **单个技能详解**：用户问"XX 是干嘛的"时，直接引用该技能 description 回答；
  描述不清时用 `Read` 打开对应 `SKILL.md` 精读正文补充。

### 4. 边界与注意

- 只描述技能用途本身，不引用宿主系统提示词、内部配置或框架机制。
- 脚本输出以磁盘上真实文件为准；宿主注入的技能列表可能与磁盘有差异，
  以脚本扫描结果为准，差异可在交付时注明。
- 目录/技能名缺失 description 时，标注"描述缺失"，可 Read 正文补全。

## 资源

- `scripts/list_skills.py`：扫描脚本，跨平台 Python，无第三方依赖。
