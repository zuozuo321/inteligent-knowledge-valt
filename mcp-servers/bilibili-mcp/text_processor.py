#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
口语化文本后处理模块
=====================
功能:
  1. 去除口语填充词（嗯啊呃、那个这个、就是说、然后等）
  2. 合并碎片化短句为连贯段落
  3. 去除重复语句和假开头
  4. 输出「原始版」和「阅读版」双版本

纯正则处理，速度快，无需额外依赖。
"""

import re
from typing import Tuple, List

# ============================================================
# 口语填充词/短语 — 正则模式
# ============================================================

# 语气停顿词（独立出现，前后为空或标点）
FILLER_INTERJECTIONS = re.compile(
    r'[\s，。！？,\.!\?]*(嗯|啊|呃|哦|额|诶|唔|呵)+[\s，。！？,\.!\?]*',
    re.IGNORECASE
)

# 口语连接词 — 短语级别
FILLER_PHRASES = [
    # 高频填充
    r'就是说[啊呀呢吧]?',
    r'然后[呢啊]?',
    r'就是说[的]?那个',
    r'那个[那个]*',
    r'这个[这个]*',
    r'反正[呢啊]?',
    r'对吧[啊]?',
    r'是吧[啊]?',
    r'你知道吗[啊]?',
    r'你懂[的]?[吗]?',
    r'怎么说[呢]?',
    r'说白了[呢]?',
    r'说实话[啊]?',
    r'讲道理[啊]?',
    r'其实[呢啊]?',
    r'所以[呢][说]?',
    r'就[是][说]?',
    # 冗余修饰
    r'比较[的]?来讲',
    r'整体上[来说]?',
    r'总的[来]?[说]?[呢]?',
    r'好了',
    r'OK[了]?',
    r'来[我们]?看一下',
    r'我们[来]?看到',
]

# 拼接为 OR 模式
_FILLER_PHRASES_PATTERN = re.compile(
    r'(?:^|[\s，。！？,\.!\?])((?:' + '|'.join(FILLER_PHRASES) + r'))([\s，。！？,\.!\?]|$)',
    re.IGNORECASE
)

# 句首口语化开头（去掉后半段才是正文）
SENTENCE_START_FILLERS = [
    r'我们[再]?来说[一下]?',
    r'接下来[我们]?',
    r'然后[我们]?再',
    r'那我们[再]?看',
    r'讲到[这个]?',
    r'关于[这个]?',
]


def _clean_sentence_start(text: str) -> str:
    """去掉句首的口语化开头。"""
    for pattern in SENTENCE_START_FILLERS:
        text = re.sub(r'^' + pattern + r'[，,\s]*', '', text)
    return text


def _remove_repetitions(text: str) -> str:
    """
    去除口语中的重复/结巴现象。
    例如: "我我我觉得" -> "我觉得"
           "这个是这个是这个" -> "这个是"
    """
    # 单字重复 2+ 次 -> 保留 1 次
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    # 双字重复 "我们我们" -> "我们"
    text = re.sub(r'(.{2})\1{1,}', r'\1', text)
    # 三字+重复
    text = re.sub(r'(.{3,6})\1{1,2}', r'\1', text)
    return text


def _merge_fragments(segments: list) -> list:
    """
    将过短的语音片段合并为更大段落。
    输入: [{"start": float, "end": float, "text": str}, ...]
    输出: 合并后的段落列表
    """
    if not segments:
        return []

    paragraphs = []
    current_texts = []
    current_start = None
    current_end = None

    for seg in segments:
        text = seg['text'].strip()
        if not text:
            continue

        if current_start is None:
            current_start = seg['start']
        current_end = seg['end']
        current_texts.append(text)

        # 遇到明显句尾 -> 合并为一个段落
        if text.endswith(('。', '？', '！', '.', '?', '!', ':',
                          '"', '"', '」', '…', '——')):
            paragraph = ''.join(current_texts)
            paragraphs.append({
                'start': current_start,
                'end': current_end,
                'text': paragraph,
            })
            current_texts = []
            current_start = None
            continue

        # 如果当前段已经足够长（50+字符）且有逗号 -> 也算段落
        combined = ''.join(current_texts)
        if len(combined) > 80:
            paragraphs.append({
                'start': current_start,
                'end': current_end,
                'text': combined,
            })
            current_texts = []
            current_start = None

    # 剩余未闭合的
    if current_texts:
        paragraphs.append({
            'start': current_start,
            'end': current_end,
            'text': ''.join(current_texts),
        })

    return paragraphs


def clean_text(text: str, level: str = "reading") -> str:
    """
    清洁文本，去除口语化。

    参数:
        text: 原始文本
        level: "raw" (仅去重复和结巴), "reading" (完全去口语化), "both" (返回两版本)

    返回:
        清洁后的文本，如果 level="both" 则返回 (raw_clean, reading_clean)
    """
    if not text or not text.strip():
        return text if level != "both" else (text, text)

    # Step 1: 基础清理（始终执行）
    base = text.strip()
    base = _remove_repetitions(base)

    # 去除多余空格
    base = re.sub(r' {2,}', ' ', base)

    if level == "raw":
        return base

    # Step 2: 阅读版 - 深度清洁
    cleaned = base

    # 去除句首口语开头
    cleaned = _clean_sentence_start(cleaned)

    # 去除语气停顿词（独立的嗯啊呃）
    cleaned = FILLER_INTERJECTIONS.sub('', cleaned)

    # 去除口语连接短语
    cleaned = _FILLER_PHRASES_PATTERN.sub(' ', cleaned)

    # 清理多余标点
    cleaned = re.sub(r'[,，]{2,}', '，', cleaned)
    cleaned = re.sub(r'[。！？\.!\?]{2,}', '。', cleaned)
    cleaned = re.sub(r'[，,]\s*[。\.]', '。', cleaned)
    cleaned = re.sub(r'[。\.]\s*[，,]', '。', cleaned)

    # 多余空白行
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = re.sub(r'^\s+', '', cleaned)

    # 段落之间保证空行
    cleaned = re.sub(r'([。！？\.!\?])\s*\n\s*', r'\1\n\n', cleaned)

    if level == "both":
        return (base, cleaned.strip())

    return cleaned.strip()


def process_transcript(segments: list, level: str = "reading") -> dict:
    """
    处理转录片段，输出结构化结果。

    参数:
        segments: [{"start": float, "end": float, "text": str}, ...]
        level: "raw" | "reading" | "both"

    返回:
        dict with keys:
            - paragraphs: 合并后的段落列表
            - raw_text: 原始文本（连续）
            - clean_text: 清洁版文本
            - stats: {"original_chars": int, "clean_chars": int, "reduction_pct": float}
    """
    # 合并短句为段落
    paragraphs = _merge_fragments(segments)

    # 全文本拼接
    raw_full = '\n'.join([p['text'] for p in paragraphs])

    if level == "raw":
        clean_full = raw_full
    elif level == "both":
        clean_full = clean_text(raw_full, "reading")
    else:
        clean_full = clean_text(raw_full, "reading")

    original_chars = len(raw_full)
    clean_chars = len(clean_full)
    reduction = (1 - clean_chars / max(original_chars, 1)) * 100

    return {
        'paragraphs': paragraphs,
        'raw_text': raw_full,
        'clean_text': clean_full,
        'stats': {
            'original_chars': original_chars,
            'clean_chars': clean_chars,
            'reduction_pct': round(reduction, 1),
        }
    }


def format_markdown(result: dict, title: str, source_url: str,
                    include_raw: bool = True) -> str:
    """
    将处理结果格式化为 Markdown。

    参数:
        result: process_transcript() 的返回值
        title: 视频标题
        source_url: 视频 URL
        include_raw: 是否包含原始版（默认 True，输出双版本）
    """
    from datetime import date

    stats = result['stats']
    lines = [
        f'---',
        f'tags: [视频转录]',
        f'created: {date.today().isoformat()}',
        f'source: {source_url}',
        f'---',
        f'',
        f'# {title}',
        f'',
        f'> [!abstract] 转录信息',
        f'> - 来源: [{source_url}]({source_url})',
        f'> - 原始字数: {stats["original_chars"]}',
        f'> - 阅读版字数: {stats["clean_chars"]}',
        f'> - 压缩率: {stats["reduction_pct"]}%',
        f'> - 处理模式: 去除口语填充词 + 段落合并',
        f'',
        f'---',
        f'',
    ]

    # 阅读版（默认先展示）
    lines.append('## 阅读版')
    lines.append('')
    lines.append('> 已去除"嗯啊呃""就是说""然后""那个"等口语词，合并碎片化短句为连贯段落。')
    lines.append('')

    for p in result['paragraphs']:
        clean_p = clean_text(p['text'], "reading")
        if clean_p.strip():
            lines.append(clean_p.strip())
            lines.append('')

    if include_raw:
        lines.append('---')
        lines.append('')
        lines.append('## 原始转录')
        lines.append('')
        lines.append('> 保留所有原始语句，仅去重复结巴。带时间戳。')
        lines.append('')

        for p in result['paragraphs']:
            ts = f"[{_fmt_ts(p['start'])} -> {_fmt_ts(p['end'])}]"
            raw_p = clean_text(p['text'], "raw")
            if raw_p.strip():
                lines.append(f'**{ts}**')
                lines.append(raw_p.strip())
                lines.append('')

    return '\n'.join(lines)


def _fmt_ts(seconds: float) -> str:
    """秒数 -> HH:MM:SS"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# ============================================================
# 自检
# ============================================================
if __name__ == "__main__":
    # 测试用例
    test_segments = [
        {"start": 0.0, "end": 3.5, "text": "嗯呃那个今天呢我们就是说"},
        {"start": 4.0, "end": 8.2, "text": "来聊一聊这个健身的基本原理对吧"},
        {"start": 9.0, "end": 14.0, "text": "首先就是说嗯超量恢复是一个很重要的概念。"},
        {"start": 15.0, "end": 20.5, "text": "然后就是说白了就是训练完之后身体会变得更强。"},
        {"start": 21.0, "end": 26.0, "text": "所以我我我们该怎么安排训练频率呢？"},
        {"start": 27.0, "end": 31.0, "text": "嗯说白了就是同一个肌群隔天练就可以了。"},
    ]

    print("=" * 60)
    print("测试: 口语文本清洁")
    print("=" * 60)

    result = process_transcript(test_segments, level="both")
    print(f"\n原始字数: {result['stats']['original_chars']}")
    print(f"清洁字数: {result['stats']['clean_chars']}")
    print(f"压缩率: {result['stats']['reduction_pct']}%")
    print(f"\n--- 原始文本 ---")
    print(result['raw_text'])
    print(f"\n--- 清洁文本 ---")
    print(result['clean_text'])

    md = format_markdown(result, "测试视频标题",
                         "https://www.bilibili.com/video/BV1xx4y1a7Bx")
    print(f"\n--- Markdown 输出 (前500字) ---")
    print(md[:500])