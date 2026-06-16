# 知识库 Schema 说明

## 概述

本文档定义知识库的目录结构、文件命名规范、Obsidian 标记规范以及 AI 操作规则。

知识库遵循 Karpathy 三层架构：**index/** (索引层) -> **wiki/** (知识层) -> **raw/** (素材层)。

## 目录结构

### 完整结构

```
$VAULT_PATH/
|
|-- index/                    # 索引层 - 主题导航
|   |-- README.md             # 顶层索引，列出所有主题
|   |-- deep-learning.md      # 深度学习主题索引
|   |-- nlp.md                # NLP 主题索引
|   |-- programming.md        # 编程主题索引
|   +-- tools.md              # 工具链主题索引
|
|-- wiki/                     # 知识层 - 深度知识
|   |-- deep-learning/
|   |   |-- attention-mechanism.md
|   |   |-- transformer-architecture.md
|   |   |-- backpropagation.md
|   |   +-- ...
|   |-- nlp/
|   |   |-- word-embedding.md
|   |   |-- language-model.md
|   |   +-- ...
|   |-- programming/
|   |   |-- python/
|   |   |   |-- async-programming.md
|   |   |   +-- ...
|   |   +-- ...
|   +-- ...
|
|-- raw/                      # 素材层 - 原始材料
|   |-- bilibili/
|   |   |-- BV1xx411c7fQ/
|   |   |   |-- reading.md       # 阅读版（去口语化）
|   |   |   |-- transcript.md    # 原始转录
|   |   |   +-- metadata.json    # 视频元数据
|   |   +-- ...
|   |-- web/
|   |   |-- article-title.md
|   |   +-- ...
|   |-- notes/
|   |   |-- my-quick-thought.md
|   |   +-- ...
|   +-- README.md             # raw/ 层索引
|
|-- outputs/                  # 输出层 - AI 对话记录和分析报告
|   |-- 2025-06-16-transformer-discussion.md
|   +-- ...
|
|-- templates/                # 模板（可选）
|   |-- wiki-template.md
|   +-- index-template.md
|
+-- .obsidian/                # Obsidian 配置（自动生成）
```

### 关键目录说明

| 目录 | 作用 | 访问频率 | 维护者 |
|------|------|---------|-------|
| `index/` | 主题导航和索引 | 每次查询 | AI |
| `wiki/` | 结构化知识主体 | 精读时 | AI |
| `raw/` | 原始素材暂存 | 编译时 | AI + 用户 |
| `outputs/` | AI 对话记录 | 参考时 | AI |
| `templates/` | 文件模板 | 创建时 | 用户 |

## 文件命名规范

### 名称规则

1. **全小写**：所有文件名使用小写字母
2. **连字符分隔**：多词用连字符 `-` 连接，不用下划线或空格
3. **英文命名**：文件名使用英文，不使用拼音或中文
4. **无特殊字符**：避免 `@`, `#`, `$`, `%` 等特殊字符
5. **扩展名**：统一使用 `.md`

**正确示例**：
- `attention-mechanism.md`
- `transformer-architecture.md`
- `gradient-descent-optimizers.md`

**错误示例**：
- `AttentionMechanism.md` (大写)
- `attention_mechanism.md` (下划线)
- `注意力机制.md` (中文)
- `attention mechanism.md` (空格)

### 特殊命名

- **索引文件**：直接以主题命名，如 `nlp.md`, `deep-learning.md`
- **raw/ 视频目录**：以 BV 号命名，如 `BV1xx411c7fQ/`
- **outputs/ 文件**：以日期开头，如 `2025-06-16-topic.md`
- **README.md**：每个目录的索引入口

## Frontmatter 规范

### 标准模板

```yaml
---
tags:
  - topic/<category>
  - source/<origin>
  - status/<state>
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: ""
---
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `tags` | 是 | 标签列表，至少包含一个 `topic/` 标签 |
| `created` | 是 | 创建日期 |
| `updated` | 是 | 最后更新日期 |
| `source` | 否 | 来源链接或引用文件路径 |
| `aliases` | 否 | Obsidian 别名，用于链接匹配 |

### 不同层级的前置元数据示例

**index/ 文件**：
```yaml
---
tags: [topic/nlp, type/index]
created: 2025-03-01
updated: 2025-06-10
---
```

**wiki/ 文件**：
```yaml
---
tags: [topic/nlp, topic/deep-learning, source/youtube]
created: 2025-06-15
updated: 2025-06-16
source: [[raw/bilibili/BV1xx411c7fQ/reading]]
aliases: [self-attention, scaled dot-product attention]
---
```

**raw/ 文件**：
```yaml
---
tags: [type/raw, source/bilibili, status/uncompiled]
created: 2025-06-16
updated: 2025-06-16
source: https://www.bilibili.com/video/BV1xx411c7fQ
---
```

## 标签体系

### 分类标签 (`topic/`)

- `topic/nlp` - 自然语言处理
- `topic/deep-learning` - 深度学习
- `topic/ml` - 机器学习
- `topic/programming` - 编程
- `topic/math` - 数学
- `topic/tools` - 工具
- 可根据需要扩展

### 来源标签 (`source/`)

- `source/youtube` - YouTube 视频
- `source/bilibili` - B站视频
- `source/paper` - 学术论文
- `source/blog` - 博客文章
- `source/book` - 书籍
- `source/course` - 课程
- `source/conversation` - AI 对话生成

### 状态标签 (`status/`)

- `status/draft` - 草稿，内容未完成
- `status/compiled` - 已完成编译
- `status/needs-review` - 需要人工审核
- `status/outdated` - 内容过时

### 类型标签 (`type/`)

- `type/index` - 索引文件
- `type/raw` - 原始素材
- `type/output` - 输出文件

## Obsidian 标记语法

### 内部链接

```markdown
[[attention-mechanism]]              # 链接到 wiki/deep-learning/attention-mechanism
[[index/deep-learning|深度学习索引]]  # 带显示文字的链接
[[raw/bilibili/BV1xx/reading]]       # 链接到 raw/ 素材
```

### 嵌入

```markdown
![[attention-mechanism#定义]]        # 嵌入其他文件的特定段落
```

### 标签

```markdown
#topic/nlp     # 行内标签
#source/web    # 行内标签
```

### 待办

```markdown
- [ ] 编译 BV1xx411c7fQ 视频
- [x] 更新 transformer 索引
```

### Callout

```markdown
> [!note] 注意事项
> 这里写注意事项的内容

> [!abstract] 摘要
> 这里写摘要内容

> [!warning] 警告
> 这里写警告内容
```

## AI 操作规则

### 创建文件时的检查清单

- [ ] 文件名是否符合命名规范（英文小写、连字符）
- [ ] 是否放在正确的目录
- [ ] frontmatter 是否完整（tags, created, updated）
- [ ] 是否有正确的 `source` 引用
- [ ] 是否通过交叉链接连接到现有知识
- [ ] 索引文件是否需要更新

### 更新文件时的检查清单

- [ ] `updated` 字段是否更新
- [ ] 新增内容是否标注了来源
- [ ] 是否保持了与现有内容的一致性
- [ ] 是否需要更新索引文件中的链接

### 搜索顺序

1. 先查 `index/` 定位主题
2. 再到 `wiki/` 精读
3. 如果不足，搜索 `raw/`
4. 如果还不足，使用外部工具（WebFetch 等）

### 禁止操作

- 不要删除 `raw/` 文件（编译后保留源素材）
- 不要编辑 `.obsidian/` 中的配置文件
- 不要创建非 Markdown 格式的知识文件
- 不要使用中文文件名或带空格的文件名
- 不要在 wiki/ 中保存原始转录（保留在 raw/）

## 模板文件

### wiki 文件模板

```markdown
---
tags: [topic/<category>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: ""
---

# 标题

## 定义

## 原理

## 示例

## 代码

## 参考

```

### index 文件模板

```markdown
---
tags: [topic/<category>, type/index]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# 主题名称

## 核心概念

- [[concept-a]]: 概念 A 简介
- [[concept-b]]: 概念 B 简介

## 进阶阅读

- [[raw/source-material]]

```

## 版本记录

| 日期 | 变更 |
|------|------|
| 2025-06-16 | 初始版本 |

---

> 本文件是知识库的 Schema 定义文档，描述了整个知识库的
> 组织规范。所有 AI 操作应遵循本文件中的规则。