<#
.SYNOPSIS
    安装工具链：ffmpeg, yt-dlp, Git 便携版
.DESCRIPTION
    将工具安装到 $ToolsDir 目录，并配置系统 PATH
#>

$ErrorActionPreference = "Stop"
$ToolsDir = "D:\左悦琦\.tools"

# 确保目录存在
if (-not (Test-Path $ToolsDir)) {
    New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null
}

Write-Host "=== 安装工具链 ===" -ForegroundColor Cyan

# 1. 安装 Git
Write-Host "[1/3] 安装 Git..." -ForegroundColor Yellow
try {
    winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements
    Write-Host "  Git 安装完成" -ForegroundColor Green
} catch {
    Write-Host "  警告：Git 安装失败（$($_.Exception.Message)），请手动安装" -ForegroundColor Red
}

# 2. 安装 ffmpeg
Write-Host "[2/3] 安装 ffmpeg..." -ForegroundColor Yellow
try {
    winget install --id Gyan.FFmpeg -e --source winget --silent --accept-package-agreements --accept-source-agreements
    Write-Host "  ffmpeg 安装完成" -ForegroundColor Green
} catch {
    Write-Host "  警告：ffmpeg 安装失败（$($_.Exception.Message)），请手动安装" -ForegroundColor Red
}

# 3. 安装 yt-dlp
Write-Host "[3/3] 安装 yt-dlp..." -ForegroundColor Yellow
$ytdlpPath = Join-Path $ToolsDir "yt-dlp.exe"
if (-not (Test-Path $ytdlpPath)) {
    try {
        Invoke-WebRequest -Uri "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" -OutFile $ytdlpPath
        Write-Host "  yt-dlp 下载完成" -ForegroundColor Green
    } catch {
        Write-Host "  警告：yt-dlp 下载失败（$($_.Exception.Message)）" -ForegroundColor Red
    }
} else {
    Write-Host "  yt-dlp 已存在，跳过" -ForegroundColor Green
}

# 4. 配置 PATH
Write-Host "配置 PATH..." -ForegroundColor Yellow
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$ToolsDir*") {
    $newPath = "$ToolsDir;" + $userPath
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    # 更新当前会话
    $env:Path = $newPath + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
    Write-Host "  PATH 已更新" -ForegroundColor Green
} else {
    Write-Host "  PATH 已包含 $ToolsDir，跳过" -ForegroundColor Green
}

Write-Host "=== 工具链安装完成 ===" -ForegroundColor Cyan