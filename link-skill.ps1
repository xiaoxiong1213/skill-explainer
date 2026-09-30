# link-skill.ps1 — 通用技能链接器
# 把 ~/.agents/skills/<技能名> 的主副本，以 junction 链接到本机所有 AI 工具的技能目录。
# 效果：技能只存一份，修改主副本后所有工具同步生效。
#
# 用法：
#   powershell -File link-skill.ps1 -SkillName skill-explainer          # 链接指定技能（默认即此名）
#   powershell -File link-skill.ps1 -SkillName my-skill -Force          # 已存在同名真实副本时，用 -Force 删除后建链接
#   powershell -File link-skill.ps1 -MasterRoot C:\Users\me\skills      # 主副本不在默认位置时指定
#
# 说明：
#   - 只处理本机"已安装"的工具（对应的配置目录存在才建链接，未安装的自动跳过）
#   - 已存在 junction 的目录自动跳过（幂等，可重复运行）
#   - 新装工具（如 Cursor）后重跑本脚本，即可自动补齐链接

param(
    [string]$SkillName = "skill-explainer",
    [string]$MasterRoot = "$env:USERPROFILE\.agents\skills",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$master = Join-Path $MasterRoot $SkillName
if (-not (Test-Path $master)) {
    Write-Error "主副本不存在: $master （请先把技能文件夹放到 $MasterRoot 下）"
    exit 1
}

# 各工具技能目录（按配置目录是否存在自动跳过）
$userHome = $env:USERPROFILE
$candidateDirs = @(
    (Join-Path $userHome ".codex\skills"),      # OpenAI Codex CLI
    (Join-Path $userHome ".claude\skills"),     # Claude Code
    (Join-Path $userHome ".copilot\skills"),    # GitHub Copilot CLI
    (Join-Path $userHome ".cursor\skills"),     # Cursor
    (Join-Path $userHome ".windsurf\skills"),   # Windsurf
    (Join-Path $userHome ".gemini\skills"),     # Gemini CLI
    "$env:LOCALAPPDATA\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills"  # 豆包工作区
)

$linked = 0
foreach ($base in $candidateDirs) {
    $link = Join-Path $base $SkillName
    $parent = Split-Path $link
    if (-not (Test-Path $parent)) { continue }   # 该工具未安装 → 跳过

    if (Test-Path $link) {
        $item = Get-Item $link -Force
        if ($item.LinkType) { Write-Output "跳过（已是链接）: $link"; continue }
        if ($Force) {
            Remove-Item $link -Recurse -Force
            Write-Output "已删除旧真实副本: $link"
        } else {
            Write-Warning "存在同名真实副本，加 -Force 才替换: $link"
            continue
        }
    }

    cmd /c mklink /J "$link" "$master"
    if ($LASTEXITCODE -eq 0) {
        Write-Output "已链接: $link -> $master"
        $linked++
    } else {
        Write-Warning "链接失败: $link"
    }
}

Write-Output ""
Write-Output "完成。共新建 $linked 个链接。"
Write-Output "技能主副本: $master"
Write-Output "以后修改主副本文件即可，所有已链接工具同步生效。"
