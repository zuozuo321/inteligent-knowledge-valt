<#
.SYNOPSIS
    安装 faster-whisper 语音识别模型
.DESCRIPTION
    下载 faster-whisper 模型到缓存目录，配置 HF_ENDPOINT 镜像加速
#>

$ErrorActionPreference = "Stop"
$CacheDir = "D:\左悦琦\.cache"
$WhisperDir = Join-Path $CacheDir "whisper_models"

Write-Host "=== 安装 Whisper 语音识别模型 ===" -ForegroundColor Cyan

# 1. 确保缓存目录存在
if (-not (Test-Path $WhisperDir)) {
    New-Item -ItemType Directory -Force -Path $WhisperDir | Out-Null
    Write-Host "  创建模型缓存目录：$WhisperDir" -ForegroundColor Green
}

# 2. 设置 HuggingFace 镜像（国内加速）
$env:HF_ENDPOINT = "https://hf-mirror.com"

# 3. 检查并安装 faster-whisper
Write-Host "[1/2] 检查 faster-whisper 库..." -ForegroundColor Yellow
$pipList = & pip list 2>$null | Select-String "faster-whisper"
if (-not $pipList) {
    & pip install faster-whisper --quiet
    Write-Host "  faster-whisper 安装完成" -ForegroundColor Green
} else {
    Write-Host "  faster-whisper 已安装" -ForegroundColor Green
}

# 4. 预下载 tiny 模型（最小最快）
Write-Host "[2/2] 预下载 whisper tiny 模型（首次运行时会自动下载）..." -ForegroundColor Yellow
Write-Host "  运行快速测试以触发模型下载..." -ForegroundColor DarkYellow

try {
    & python -c "
from faster_whisper import WhisperModel
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
model = WhisperModel('tiny', download_root=r'$WhisperDir', device='auto')
print('模型加载成功！')
" 2>&1
    Write-Host "  tiny 模型下载完成" -ForegroundColor Green
} catch {
    Write-Host "  注意：tiny 模型下载失败（$($_.Exception.Message)）" -ForegroundColor Yellow
    Write-Host "  首次转录时模型会自动下载，无需担心" -ForegroundColor Yellow
}

# 5. 写入环境变量配置
Write-Host "配置环境变量..." -ForegroundColor Yellow
[Environment]::SetEnvironmentVariable("HF_ENDPOINT", "https://hf-mirror.com", "User")
$env:HF_ENDPOINT = "https://hf-mirror.com"
Write-Host "  HF_ENDPOINT 已设置为 hf-mirror.com（国内镜像）" -ForegroundColor Green

Write-Host "=== Whisper 语音识别模型安装完成 ===" -ForegroundColor Cyan