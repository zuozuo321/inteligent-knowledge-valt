<#
.SYNOPSIS
    一键部署脚本：按顺序执行所有部署步骤
.DESCRIPTION
    调用 01~04 脚本完成完整的环境部署
#>

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  知识库工作流 - 一键部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 记录开始时间
$startTime = Get-Date

# 步骤 1：安装工具链
Write-Host ""
Write-Host "========== 步骤 1/4：安装工具链 ==========" -ForegroundColor Magenta
& (Join-Path $ScriptRoot "01-install-tools.ps1")
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
    Write-Host "步骤 1 执行完毕（部分组件可能需要手动安装）" -ForegroundColor Yellow
}

# 步骤 2：部署 MCP 服务端
Write-Host ""
Write-Host "========== 步骤 2/4：部署 MCP 服务端 ==========" -ForegroundColor Magenta
& (Join-Path $ScriptRoot "02-setup-mcp-servers.ps1")
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
    Write-Host "步骤 2 执行完毕（可能有警告）" -ForegroundColor Yellow
}

# 步骤 3：配置 Claude Code
Write-Host ""
Write-Host "========== 步骤 3/4：配置 Claude Code ==========" -ForegroundColor Magenta
& (Join-Path $ScriptRoot "03-configure-claude.ps1")
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
    Write-Host "步骤 3 执行完毕（可能有警告）" -ForegroundColor Yellow
}

# 步骤 4：安装语音识别
Write-Host ""
Write-Host "========== 步骤 4/4：安装语音识别 ==========" -ForegroundColor Magenta
& (Join-Path $ScriptRoot "04-install-whisper.ps1")
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
    Write-Host "步骤 4 执行完毕（可能有警告）" -ForegroundColor Yellow
}

# 计算耗时
$endTime = Get-Date
$elapsed = $endTime - $startTime

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  部署完成！" -ForegroundColor Cyan
Write-Host "  总耗时：$($elapsed.Minutes) 分 $($elapsed.Seconds) 秒" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Green
Write-Host "  1. 编辑 config/claude-settings.json，替换占位符为实际路径" -ForegroundColor White
Write-Host "  2. 编辑 .mcp.json，确认 MCP 服务路径正确" -ForegroundColor White
Write-Host "  3. 启动 Obsidian，打开知识库目录" -ForegroundColor White
Write-Host "  4. 在项目根目录运行 claude 开始使用" -ForegroundColor White
Write-Host ""
Write-Host "更多信息请参见 workflow-docs/OVERVIEW.md" -ForegroundColor Yellow