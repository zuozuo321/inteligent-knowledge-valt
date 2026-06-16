<#
.SYNOPSIS
    部署 MCP 服务端（obsidian-mcp + bilibili-mcp）
.DESCRIPTION
    创建 Python 虚拟环境，安装依赖，部署 MCP 服务端
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"
$ObsidianMcpDir = Join-Path $ProjectRoot "mcp-servers\obsidian-mcp"
$BilibiliMcpDir = Join-Path $ProjectRoot "mcp-servers\bilibili-mcp"

Write-Host "=== 部署 MCP 服务端 ===" -ForegroundColor Cyan

# 1. 创建虚拟环境
Write-Host "[1/4] 创建 Python 虚拟环境..." -ForegroundColor Yellow
if (-not (Test-Path $VenvPath)) {
    & python -m venv $VenvPath
    Write-Host "  虚拟环境创建完成" -ForegroundColor Green
} else {
    Write-Host "  虚拟环境已存在，跳过" -ForegroundColor Green
}

# 激活虚拟环境的辅助函数
function Get-VenvPython {
    return Join-Path $VenvPath "Scripts\python.exe"
}
function Get-VenvPip {
    return Join-Path $VenvPath "Scripts\pip.exe"
}

$python = Get-VenvPython
$pip = Get-VenvPip

# 2. 安装基础依赖
Write-Host "[2/4] 安装基础依赖（mcp, fastmcp）..." -ForegroundColor Yellow
& $pip install mcp fastmcp httpx --quiet
Write-Host "  基础依赖安装完成" -ForegroundColor Green

# 3. 部署 obsidian-mcp
Write-Host "[3/4] 部署 obsidian-mcp..." -ForegroundColor Yellow
$obsidianReq = Join-Path $ObsidianMcpDir "requirements.txt"
if (Test-Path $obsidianReq) {
    & $pip install -r $obsidianReq --quiet
}
Write-Host "  obsidian-mcp 代码已就绪" -ForegroundColor Green

# 4. 部署 bilibili-mcp
Write-Host "[4/4] 部署 bilibili-mcp..." -ForegroundColor Yellow
$bilibiliReq = Join-Path $BilibiliMcpDir "requirements.txt"
if (Test-Path $bilibiliReq) {
    & $pip install -r $bilibiliReq --quiet
} else {
    # 安装 bilibili-mcp 所需依赖
    & $pip install httpx beautifulsoup4 --quiet
}

# 安装 whisper 相关依赖（如果可用）
Write-Host "  尝试安装语音识别依赖（可选）..." -ForegroundColor DarkYellow
& $pip install faster-whisper --quiet 2>$null

Write-Host "  bilibili-mcp 代码已就绪" -ForegroundColor Green

Write-Host "=== MCP 服务端部署完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：运行 03-configure-claude.ps1 配置 Claude Code 连接" -ForegroundColor Magenta