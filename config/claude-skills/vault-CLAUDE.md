# 知识库操作手册 (Vault CLAUDE.md)

本文件定义了 AI 助手操作知识库时应遵循的准则。

## 一、Karpathy 三层架构

知识库遵循 Karpathy LLM Wiki 方法论，分为三个层级：

### Layer 1: 索引层 (Index)
- 位于 `$VAULT_PATH/index/`
- 每个主题一个索引文件，如 `$VAULT_PATH/index/transformer.md`
- 格式：主题概述 + 关键概念列表 + 交叉引用链接
- AI 查询知识库时，**首先**从此层开始

### Layer 2: 知识层 (Wiki)
- 位于 `$VAULT_PATH/wiki/`
- 每个概念一个文件，深度展开
- 格式：定义、原理、示例、代码片段、参考链接
- AI 阅读到此层时，应全面理解概念并评估与问题的相关性

### Layer 3: 素材层 (Raw)
- 位于 `$VAULT_PATH/raw/`
- 原始素材：文章摘录、视频转录、笔记截图、URL 存档
- 通常由 AI 从外部导入，暂存待编译
- AI 在此层找到需要整理的内容时，应编译到 wiki/ 或 index/

## 二、四大操作

### 操作 1: 编译 (Compile)
- 输入：raw/ 中的素材
- 输出：wiki/ 中的结构化知识或 index/ 中的索引
- 触发条件：用户要求整理某素材，或 AI 发现 raw/ 中有未处理的内容
- 注意：编译后保留 raw/ 中的源文件作为参考

### 操作 2: 查询 (Query)
- 流程：index/ 定位 -> wiki/ 精读 -> 合成回答
- 如果 index/ 有相关内容但不深入，AI 应主动搜索 wiki/
- 如果 wiki/ 也没有，AI 应告知用户知识缺口，并主动搜索 raw/

### 操作 3: 回填 (Backfill)
- 触发条件：AI 在回答过程中产生了有价值的内容
- 输出：更新 wiki/ 或新建 outputs/
- 格式：与 wiki/ 格式保持一致

### 操作 4: 维护 (Maintain)
- 检查 orphan notes（无引用/被引用的文件）
- 合并重复内容
- 更新过时信息
- 重命名文件以符合规范

## 三、Obsidian 标记规范

### 文件命名
- 英文命名，全小写
- 连字符分隔：`attention-mechanism.md`
- 目录名同理：`wiki/deep-learning/`

### 元数据 (Frontmatter)
```yaml
---
tags: [topic/subtopic, source/youtube]
created: 2025-01-01
updated: 2025-06-16
---
```

### 内部链接
- 使用 Wikilink：`[[transformer]]` 或 `[[attention-mechanism|注意力机制]]`
- 引用素材：`[[raw/youtube-video-title]]`

### 标签体系
- `topic/` 前缀：学科分类，如 `topic/nlp`, `topic/ml`
- `source/` 前缀：来源分类，如 `source/youtube`, `source/paper`, `source/blog`
- `status/` 前缀：状态标记，如 `status/draft`, `status/compiled`, `status/needs-review`

## 四、AI 行为规则

1. **先查索引，再读细节**：任何查询必须先检查 index/，再到 wiki/ 深读
2. **维护引用链**：创建的每个文件都要有引用来源
3. **不要删除源素材**：编译后保留 raw/ 文件
4. **标准回答格式**：
   - 先给出直接答案
   - 附上知识库引用路径
   - 指明知识缺口（如有）
5. **定期清理**：每次会话结束时检查是否有 orphan notes 或未编译素材