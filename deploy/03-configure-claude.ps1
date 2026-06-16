<#
.SYNOPSIS
    配置 Claude Code 连接 MCP 服务
.DESCRIPTION
    将 claude-settings.json 模板复制到用户目录，配置 MCP 服务连接
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ConfigDir = Join-Path $ProjectRoot "config"
$SettingsTemplate = Join-Path $ConfigDir "claude-settings.json"
$ClaudeDir = "$env:USERPROFILE\.claude"
$ClaudeSettings = Join-Path $ClaudeDir "settings.json"

Write-Host "=== 配置 Claude Code ===" -ForegroundColor Cyan

# 1. 确保 .claude 目录存在
if (-not (Test-Path $ClaudeDir)) {
    New-Item -ItemType Directory -Force -Path $ClaudeDir | Out-Null
    Write-Host "  创建 .claude 目录" -ForegroundColor Green
}

# 2. 备份现有配置
if (Test-Path $ClaudeSettings) {
    $backup = "$ClaudeSettings.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item $ClaudeSettings $backup
    Write-Host "  已备份现有配置到 $backup" -ForegroundColor Yellow
}

# 3. 复制模板配置
if (Test-Path $SettingsTemplate) {
    Copy-Item $SettingsTemplate $ClaudeSettings -Force
    Write-Host "  配置模板已复制到 $ClaudeSettings" -ForegroundColor Green
    Write-Host "  注意：请编辑该文件，替换占位符 `$VAULT_PATH 为实际路径" -ForegroundColor Yellow
} else {
    Write-Host "  错误：找不到配置模板 $SettingsTemplate" -ForegroundColor Red
    exit 1
}

# 4. 复制 .mcp.json
$McpTemplate = Join-Path $ConfigDir "mcp-template.json"
$McpJson = Join-Path $ProjectRoot ".mcp.json"
if (Test-Path $McpTemplate) {
    Copy-Item $McpTemplate $McpJson -Force
    Write-Host "  .mcp.json 已复制到项目根目录" -ForegroundColor Green
    Write-Host "  注意：请编辑该文件，替换占位符为实际路径" -ForegroundColor Yellow
} else {
    Write-Host "  警告：找不到 .mcp.json 模板" -ForegroundColor Red
}

Write-Host "=== Claude Code 配置完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：运行 04-install-whisper.ps1 安装语音识别模型" -ForegroundColor Magenta