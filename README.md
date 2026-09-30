# skill-explainer（技能说明器）

一个通用 **Agent Skill**：扫描你的技能目录，读取每个 `SKILL.md` 的 `name` 与 `description`，
把"每个技能是干嘛的"整理成清单、表格或文档。适用于任何支持
[Agent Skills](https://agentskills.me/) 标准的 AI 工具 —— Codex CLI、Claude Code、
GitHub Copilot CLI、Cursor 等。

## 它能做什么

- 一键盘点：**有哪些技能、每个技能管什么、什么时候该用它**
- 输出结构化结果（JSON / 纯文本），可整理为分类清单、Markdown 表格、CSV、HTML
- 支持只看顶层技能（`--top-level`），跳过子技能/分支
- 跨平台 Python 脚本，无第三方依赖

触发方式（自然语言即可）："有哪些技能""每个 skill 是干嘛的""XX skill 有什么用"
"帮我梳理技能清单""技能总览/速查表"……

## 目录结构

```
skill-explainer/
├── SKILL.md              # 技能定义（name + description + 工作流）
└── scripts/
    └── list_skills.py    # 扫描脚本：读 frontmatter，输出 JSON / 文本
```

## 安装

### 方式一：放入任意技能目录（通用）

把 `skill-explainer/` 文件夹放进你的 AI 工具读取的技能目录即可（任选其一）：

| 工具 | 全局技能目录 |
| --- | --- |
| Codex CLI | `~/.codex/skills/` |
| Claude Code | `~/.claude/skills/` |
| GitHub Copilot CLI / VS Code | `~/.agents/skills/` |
| Cursor | `~/.cursor/skills/` |
| 项目级（任意工具） | `.agents/skills/` 或 `.github/skills/`（仓库根下） |

安装后重启/新开会话，技能自动加载。

### 方式二：Windows 一键全工具安装

本仓库同时提供 [`link-skill.ps1`](link-skill.ps1)（见下方"配套脚本"）：技能只存一份在
`~/.agents/skills/`，自动为所有已安装的 AI 工具建立目录联接（junction），
**改一次、处处生效**。

## 使用

```bash
# 扫描某个技能根目录，输出可读清单
python skill-explainer/scripts/list_skills.py ~/.agents/skills --plain

# 扫描多个根目录，只看顶层技能，输出 JSON
python skill-explainer/scripts/list_skills.py ~/.codex/skills ~/.claude/skills --top-level

# 完整 JSON（含 level 层级标记）
python skill-explainer/scripts/list_skills.py ~/.agents/skills
```

日常其实不用手动跑：在 AI 工具里直接问"列出所有技能的用途"，技能会自动触发并调用脚本。

## 配套脚本：link-skill.ps1（可选）

Windows 下的通用技能链接器，解决"一个技能要在多个工具里各复制一份"的问题：

```powershell
powershell -File link-skill.ps1 -SkillName skill-explainer   # 为所有已装工具建链接
powershell -File link-skill.ps1 -SkillName my-skill -Force   # 新技能；-Force 替换同名旧副本
```

它只对**已安装**的工具生效（配置目录存在才建链接），新装工具后重跑即可自动补齐。
已存在的链接自动跳过，可反复运行。

## License

[MIT](LICENSE)
