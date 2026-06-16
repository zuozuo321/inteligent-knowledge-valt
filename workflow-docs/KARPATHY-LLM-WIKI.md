# Karpathy LLM Wiki 方法论详解

## 概述

Karpathy LLM Wiki 方法论由 Andrej Karpathy 提出，核心思想是：
**利用 LLM 作为知识库的编译器和查询引擎，构建一个动态增长的个人知识系统。**

与传统的笔记系统不同，Karpathy 方法论强调：
- **AI 优先**：AI 负责知识的导入、整理、查询和维护
- **三层架构**：索引层、知识层、素材层，各自承担不同职责
- **持续编译**：素材不断被 AI 编译为结构化知识
- **主动回填**：AI 在回答过程中产生的有价值内容被保存回知识库

## 三层架构

### Layer 1: 索引层 (Index)

**位置**：`$VAULT_PATH/index/`

**功能**：
- 提供知识库的目录和导航
- 每个主题一个索引文件，概述该主题的关键概念
- 索引文件中包含指向 wiki/ 层详细内容的交叉引用链接

**格式示例**：
```markdown
# Transformer 架构

## 核心概念
- [[attention-mechanism]]: 自注意力机制
- [[positional-encoding]]: 位置编码
- [[feed-forward-network]]: 前馈网络

## 相关主题
- [[layer-normalization]]
- [[residual-connection]]

## 进阶阅读
- [[raw/attention-is-all-you-need-paper]]
```

**查询路径**：AI 收到问题时，**首先**访问 index/ 定位相关主题。

### Layer 2: 知识层 (Wiki)

**位置**：`$VAULT_PATH/wiki/`

**功能**：
- 深度展开每个概念，提供完整知识
- 包含定义、原理、示例、代码片段、参考链接
- 是知识库的主体，AI 精读的内容来源

**格式示例**：
```markdown
---
tags: [topic/nlp, topic/deep-learning]
created: 2025-01-15
updated: 2025-06-10
---

# 自注意力机制 (Self-Attention)

## 定义
自注意力机制是 Transformer 的核心组件，允许序列中的每个位置关注所有其他位置。

## 数学原理
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

## 代码示例
```python
import torch.nn as nn

class SelfAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
```

## 参考
- [[attention-is-all-you-need]]
- [[raw/illustrated-transformer]]
```

### Layer 3: 素材层 (Raw)

**位置**：`$VAULT_PATH/raw/`

**功能**：
- 存放原始素材：文章摘录、视频转录、截图、URL 存档
- 素材按来源分类存放，保持原始格式
- AI 定期或按需编译 raw/ 中的内容到 wiki/ 或 index/

## 四大操作

### 操作 1: 编译 (Compile)

将 raw/ 中的原始素材转换为 wiki/ 中的结构化知识。

**流程**：
1. AI 读取 raw/ 中的素材
2. 提取关键概念和知识点
3. 在 wiki/ 中创建或更新对应文件
4. 如果概念涉及多个方面，在 index/ 中更新索引
5. 保留 raw/ 中的源文件作为参考

**触发条件**：
- 用户要求整理某素材
- AI 发现 raw/ 中有未处理的内容
- 定期维护检查

### 操作 2: 查询 (Query)

从知识库中检索信息并合成回答。

**流程**：
1. 用户提出问题
2. AI 先在 index/ 中查找相关主题索引
3. 根据索引定位到 wiki/ 中的具体文件
4. 精读 wiki/ 文件，理解概念
5. 合成回答给用户
6. 如果 wiki/ 中没有足够信息，搜索 raw/ 或外部资源

### 操作 3: 回填 (Backfill)

将 AI 在回答问题过程中产生的有价值内容保存到知识库。

**触发条件**：
- AI 生成了详细的解释或分析
- AI 从多个 wiki/ 文件综合出了新的见解
- 用户明确要求保存某段内容

**输出位置**：
- 更新现有 wiki/ 文件（补充内容）
- 创建新的 wiki/ 文件（新概念）
- 保存到 `$VAULT_PATH/outputs/`（对话记录、分析报告）

### 操作 4: 维护 (Maintain)

定期检查和优化知识库。

**任务**：
- 检查 orphan notes（没有任何链接指向的文件）
- 合并重复内容
- 更新过时信息
- 重命名文件以符合规范
- 检查 frontmatter 元数据是否完整

## 索引体系

索引是 Karpathy 方法论的核心创新，它解决了传统笔记系统中"知识越多越难找"的问题。

### 索引类型

1. **主题索引**：按学科或领域分类，如 `index/transformer.md`
2. **层级索引**：`index/` 根目录下的 `README.md` 作为顶级导航
3. **交叉引用**：wiki/ 文件之间的双向链接

### 索引维护原则

- 每个索引文件对应一个**核心主题**
- 索引文件只包含**概述**和**链接**，不包含深度内容
- 索引文件的大小控制在 50 行以内
- 当 wiki/ 中新增文件时，检查是否需要更新索引

## 与传统笔记法的对比

| 特性 | 传统笔记 | Karpathy LLM Wiki |
|------|---------|-------------------|
| 录入方式 | 手动 | AI 自动编译 |
| 查询方式 | 手动搜索 | AI 智能检索 |
| 组织结构 | 固定文件夹 | 动态三层架构 |
| 维护负担 | 高 | AI 辅助维护 |
| 知识覆盖 | 取决于个人 | AI 辅助扩展 |
| 成本 | 时间 | API 调用 |

## 参考资料

- [Karpathy 原始推文](https://x.com/karpathy/status/1803184396885774370)
- [llm-wiki 项目](https://github.com/gliderwiki/llm-wiki)
- 本仓库的 [VAULT-SCHEMA.md](VAULT-SCHEMA.md) - 目录结构和命名规范
- 本仓库的 [INGEST-FLOW.md](INGEST-FLOW.md) - 素材导入流程
- 本仓库的 [QUERY-FLOW.md](QUERY-FLOW.md) - 查询与回填流程