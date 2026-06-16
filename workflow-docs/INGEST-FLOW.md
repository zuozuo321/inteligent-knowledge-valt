# 素材导入流程 (Ingest Flow)

## 概述

素材导入是指将外部信息（B站视频、网页文章、个人笔记等）转化为知识库中结构化知识的过程。

本流程遵循 Karpathy 方法论的三层架构：**raw/ -> AI 编译 -> wiki/**。

## 整体流程

```
外部素材                  raw/ 层              AI 编译               wiki/ 层
+--------+              +----------+         +----------+         +----------+
| B站视频 | -----------> | raw/     |         |          |         | wiki/    |
+--------+   下载+转录   | bilibili | -------> | Claude   | -------> | topic-a  |
                         | video1   |  语音    | Code     |   提取   |          |
+--------+              | video2   |  转写    | (AI 引擎)|   概念   +----------+
| 网页    | -----------> +----------+         |          |         | wiki/    |
+--------+   保存为MD    | raw/     |         |          | -------> | topic-b  |
                         | web      | -------> | 步骤:    |   更新   +----------+
+--------+              | article1 |  读取    | 1.提取   |         | index/   |
| 笔记    | -----------> +----------+         | 2.编译   | -------> | topic    |
+--------+   拷贝到      | raw/     |         | 3.索引   |   更新   | README   |
                raw/     | notes    |         | 4.验证   |         +----------+
                         +----------+         +----------+
```

## 详细步骤

### 步骤 1: 获取素材

#### B站视频

使用 `bilibili-mcp` 服务端，有两种方式：

**方式 A: CC 字幕（快速）**
```
AI 调用: get_bilibili_subtitle(video_input)
结果: 视频的 CC 字幕纯文本
适用: 有 CC 字幕的视频（约 60% 的 B站视频）
耗时: 几秒钟
```

**方式 B: 语音识别（通用）**
```
AI 调用: process_bilibili_video(video_input, model_size="tiny")
结果: 下载音频 -> faster-whisper 转写 -> 去除口语化 -> 双版本 Markdown
适用: 所有视频（不依赖 CC 字幕）
耗时: 2-10 分钟（取决于视频长度和模型大小）
```

**保存位置**：`$VAULT_PATH/raw/bilibili/<BV号>/`

#### 网页文章
```
AI 使用 WebFetch 工具获取网页内容
保存为 Markdown 到 raw/web/<文章标题>.md
提取元数据：URL、作者、发布日期、标签
```

#### 个人笔记
```
直接复制或拖拽到 raw/notes/
AI 后续编译时处理格式统一
```

### 步骤 2: 保存到 raw/ 层

**raw/ 目录结构**：
```
$VAULT_PATH/raw/
|-- bilibili/
|   |-- BV1xx/
|   |   |-- reading.md       # 阅读版（去口语化）
|   |   |-- transcript.md    # 原始转录
|   |   |-- metadata.json    # 视频元数据
|   +-- BV2xx/
|-- web/
|   |-- article-title.md
|   +-- ...
|-- notes/
|   |-- my-thought-1.md
|   +-- ...
+-- README.md                # raw/ 层索引
```

### 步骤 3: AI 编译

AI 定期（或按用户要求）检查 raw/ 中的未编译素材，执行编译操作：

**编译流程**：
1. **读取素材**：AI 读取 raw/ 中的文件，理解内容
2. **提取概念**：识别素材中的关键概念、原理、示例
3. **检查现有知识**：在 wiki/ 和 index/ 中搜索是否已有相关内容
4. **创建/更新文件**：
   - 如果是新概念：在 wiki/ 中创建新文件
   - 如果是已有概念的补充：更新 wiki/ 中的现有文件
5. **更新索引**：如果概念涉及新的主题，更新 index/ 中的索引
6. **验证完整性**：确保新内容有正确的引用和链接

**编译输出格式**：
```markdown
---
tags: [topic/nlp, source/bilibili]
created: 2025-06-16
updated: 2025-06-16
source: [[raw/bilibili/BV1xx/reading]]
---

# 概念名称

## 定义
...

## 原理
...

## 参考
- [[raw/bilibili/BV1xx/reading]]
- [[related-concept]]
```

**注意事项**：
- 编译后**不删除** raw/ 中的源素材
- 在 wiki/ 文件的 frontmatter 中通过 `source:` 字段引用源素材
- 如果素材涉及多个独立概念，为每个概念创建独立的 wiki/ 文件

### 步骤 4: 验证

编译完成后，AI 应验证：
1. 新文件是否正确引用了源素材
2. 是否有其他 wiki/ 文件需要建立交叉引用
3. index/ 是否需要更新
4. 文件的 frontmatter 是否完整

## MCP 工具调用顺序

```
1. process_bilibili_video(video_input)    # 处理视频
   |
2. read_note("raw/bilibili/BVxx/reading") # 检查结果
   |
3. search_notes("现有概念名")             # 检查现有知识
   |
4. create_note("wiki/new-concept", ...)   # 创建知识文件
   |
5. create_note("index/topic", ...)        # 更新索引
   |
6. read_note("wiki/related-concept")      # 建立交叉引用
```

## 特殊情况处理

### 重复素材
- 如果 raw/ 中已有相同内容，AI 应跳过下载
- 基于视频 BV 号或 URL 判断

### 低质量素材
- 语音识别效果差 -> 标记为 `status/needs-review`
- 内容不完整 -> 在 wiki/ 文件中注明

### 跨语言素材
- 英文素材：保留原文，AI 编译时提供中文摘要
- 中英混合：分别处理，保持原文引用

## 最佳实践

1. **批量处理**：一次导入多个素材时，先全部下载，再统一编译
2. **渐进式编译**：大素材可分多次编译，每次处理一个子主题
3. **保留上下文**：在 wiki/ 文件中保留与源素材的链接，方便回溯
4. **定期检查**：每周检查 raw/ 中未编译的素材，避免堆积