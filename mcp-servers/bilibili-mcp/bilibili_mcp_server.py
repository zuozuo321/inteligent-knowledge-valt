#!/usr/bin/env python3
"""Bilibili Video Processing MCP Server

Provides:
- get_bilibili_subtitle: Fetch CC subtitles from Bilibili videos
- transcribe_bilibili_video: Download audio + Whisper transcription
- process_bilibili_video: Full pipeline (download + transcribe + clean)
"""

import hashlib
import hmac
import json
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Configure cache directory
CACHE_DIR = Path.home() / ".cache" / "bilibili_mcp"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastMCP server
mcp = FastMCP("bilibili-mcp")


# ============================================================
# WBI Signature (Bilibili API authentication)
# ============================================================

def get_wbi_keys() -> tuple:
    """Get WBI signing keys from Bilibili's navigation API."""
    url = "https://api.bilibili.com/x/web-interface/nav"
    resp = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    data = resp.json()
    img_url = data["data"]["wbi_img"]["img_url"]
    sub_url = data["data"]["wbi_img"]["sub_url"]
    img_key = re.search(r"/([^/]+)\.png", img_url).group(1)
    sub_key = re.search(r"/([^/]+)\.png", sub_url).group(1)
    return img_key, sub_key


def encrypt_wbi(data: dict, img_key: str, sub_key: str) -> dict:
    """Sign parameters with WBI algorithm."""
    mixin_key = sub_key[:4] + img_key[:4]
    sort_dict = dict(sorted(data.items()))
    sort_str = urllib.parse.urlencode(sort_dict)
    sign = hashlib.md5((sort_str + mixin_key).encode()).hexdigest()
    sort_dict["w_ts"] = data["w_ts"]
    sort_dict["w_sign"] = sign
    return sort_dict


# ============================================================
# BV / AV Number Parsing
# ============================================================

def parse_video_id(video_input: str) -> str:
    """Parse various video ID formats into a unified BV/AV string."""
    video_input = video_input.strip()
    # Already a BV or AV number
    if video_input.startswith("BV") or video_input.startswith("av"):
        return video_input
    # Bilibili URL
    patterns = [
        r"bilibili\.com/video/(BV[0-9A-Za-z]+)",
        r"bilibili\.com/video/(av\d+)",
        r"b23\.tv/(BV[0-9A-Za-z]+)",
        r"b23\.tv/(av\d+)",
    ]
    for pat in patterns:
        match = re.search(pat, video_input)
        if match:
            return match.group(1)
    raise ValueError(f"无法解析视频ID: {video_input}")


# ============================================================
# CC Subtitle Fetcher
# ============================================================

@mcp.tool()
def get_bilibili_subtitle(video_input: str) -> str:
    """获取B站视频的CC字幕(快速)。

    Args:
        video_input: 视频URL或BV号

    Returns:
        字幕纯文本（合并后的完整文本）
    """
    try:
        video_id = parse_video_id(video_input)
        video_id_clean = video_id.replace("BV", "").replace("av", "")
        prefix = "BV" if video_id.startswith("BV") else "av"

        # Fetch video info page to get aid and cid
        if prefix == "BV":
            info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={video_id}"
        else:
            info_url = f"https://api.bilibili.com/x/web-interface/view?aid={video_id_clean}"

        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com/"}
        resp = httpx.get(info_url, headers=headers, timeout=15)
        data = resp.json()

        if data["code"] != 0:
            return json.dumps({"error": f"API错误: {data.get('message', '未知错误')}"}, ensure_ascii=False)

        aid = data["data"]["aid"]
        cid = data["data"]["cid"]
        title = data["data"]["title"]

        # Fetch subtitle list
        subtitle_url = f"https://api.bilibili.com/x/player/v2?aid={aid}&cid={cid}"
        resp2 = httpx.get(subtitle_url, headers=headers, timeout=15)
        sub_data = resp2.json()

        subtitle_list = sub_data.get("data", {}).get("subtitle", {}).get("subtitles", [])
        if not subtitle_list:
            return json.dumps({"error": "该视频没有CC字幕"}, ensure_ascii=False)

        # Prefer Chinese subtitle
        selected = None
        for sub in subtitle_list:
            lang = sub.get("lang", "")
            if "zh" in lang:
                selected = sub
                break
        if not selected:
            selected = subtitle_list[0]

        # Download subtitle JSON
        sub_url = "https:" + selected["subtitle_url"] if selected["subtitle_url"].startswith("//") else selected["subtitle_url"]
        resp3 = httpx.get(sub_url, headers=headers, timeout=15)
        sub_json = resp3.json()

        # Extract and merge text
        body_parts = [item["content"] for item in sub_json.get("body", [])]
        full_text = " ".join(body_parts)

        return json.dumps({
            "success": True,
            "title": title,
            "subtitle": full_text,
            "duration": sub_json.get("body", [{}])[-1].get("to", 0) if sub_json.get("body") else 0
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ============================================================
# Video Transcription (download + whisper)
# ============================================================

@mcp.tool()
def transcribe_bilibili_video(
    video_input: str,
    model_size: str = "medium",
    language: str = "zh",
    text_mode: str = "raw"
) -> str:
    """下载B站视频音频并通过本地GPU语音识别(faster-whisper)转写为文字。

    Args:
        video_input: 视频URL或BV号
        model_size: whisper模型大小 (tiny/base/small/medium/large-v3)
        language: 语言代码 (默认zh)
        text_mode: raw保留原始口语/reading去除口语词阅读版

    Returns:
        带时间戳的完整转录文本
    """
    # Delegate to transcribe_bv module
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from transcribe_bv import transcribe_video
        result = transcribe_video(
            video_input=video_input,
            model_size=model_size,
            language=language,
            text_mode=text_mode
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except ImportError:
        return json.dumps({"error": "transcribe_bv 模块未找到，请确保 transcribe_bv.py 在同目录"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ============================================================
# Full Pipeline: download + transcribe + clean
# ============================================================

@mcp.tool()
def process_bilibili_video(
    video_input: str,
    model_size: str = "tiny",
    language: str = "zh",
    mode: str = "full"
) -> str:
    """B站视频一站式处理：下载音频 -> 语音识别转写 -> 去除口语化 -> 生成双版本Markdown。

    Args:
        video_input: 视频URL或BV号
        model_size: whisper模型大小 (tiny/base/small/medium/large-v3, 默认tiny以加速)
        language: 语言代码 (默认zh)
        mode: full含原始版/clean仅阅读版

    Returns:
        包含「阅读版」和「原始转录」两份内容的Markdown
    """
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from transcribe_bv import transcribe_video
        from text_processor import process_transcript

        # Step 1: Transcribe
        transcript = transcribe_video(
            video_input=video_input,
            model_size=model_size,
            language=language,
            text_mode="raw"
        )

        if "error" in transcript:
            return json.dumps(transcript, ensure_ascii=False, indent=2)

        raw_text = transcript.get("full_text", "")

        # Step 2: Clean transcript
        cleaned = process_transcript(raw_text, language=language)

        # Step 3: Build output
        result = {
            "success": True,
            "title": transcript.get("title", ""),
            "duration": transcript.get("duration", 0),
            "bvid": transcript.get("bvid", ""),
        }

        # Reading version (cleaned)
        reading_lines = []
        reading_lines.append(f"# {transcript.get('title', '视频转录')}")
        reading_lines.append("")
        reading_lines.append(cleaned["reading_version"])
        result["reading_version"] = "\n".join(reading_lines)

        # Raw version (optional)
        if mode == "full":
            raw_lines = []
            raw_lines.append(f"# {transcript.get('title', '视频转录')} - 原始转录")
            raw_lines.append("")
            raw_lines.append(cleaned["raw_with_timestamps"])
            result["original_transcript"] = "\n".join(raw_lines)

        return json.dumps(result, ensure_ascii=False, indent=2)

    except ImportError as e:
        return json.dumps({"error": f"模块导入失败: {e}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")