# RZCode Study Skill 新手指南

**预计阅读时间：5 分钟**

## 架构概览

```
┌─────────────────┐
│   Agent/User    │
└────────┬────────┘
         │
    ┌────v────┐
    │  Skill  │  (这就是 rzcode-study-skill)
    └────┬────┘
         │
    ┌────v──────────────────┐
    │  25 个 API 工具        │
    │ (tools/*.json)         │
    └────┬──────────────────┘
         │
    ┌────v──────────────────┐
    │  REST API             │
    │ https://rzcode.vip    │
    │ /api/study/books/     │
    │ /api/study/concepts/  │
    │ ... 等等               │
    └────┬──────────────────┘
         │
    ┌────v──────────────────┐
    │  RZCode Backend       │
    │  (softwareCert)       │
    │  ├─ Neo4j             │
    │  └─ 文件存储          │
    └───────────────────────┘
```

## 核心概念（2分钟速查）

### 节点 (Node)
- **Book** - 书籍（最顶层）
- **Chapter** - 章节（支持嵌套，可以有子章节）
- **Concept** - 概念（定义、定理、方法、人物等）
- **Note** - 笔记（关联到任何节点）

### 关系 (Relationship)
| 关系 | 中文 | 说明 | 例子 |
|------|------|------|------|
| PART_OF | 属于 | 章节属于某个书籍/章节 | "第2.1节" PART_OF "第2章" |
| MENTIONED_IN | 提及于 | 概念在某个章节出现 | "微积分" MENTIONED_IN "高等数学第2章" |
| RELATED_TO | 相关于 | 概念之间有联系 | "导数" RELATED_TO "积分" |
| PREREQUISITE_FOR | 前置于 | 学习依赖关系 | "线性代数" PREREQUISITE_FOR "微积分" |

### 属性 (Properties)

**Book**:
- title, authors, edition, file_path

**Chapter**:
- title, level, order, summary, parent_title

**Concept**:
- canonical_name, kind, definition, aliases, summary

**Note**:
- title, content, file_type, created_at, updated_at

## 三步快速开始

### 第 1 步：配置 API Key

```bash
mkdir -p ~/.rzcode
cat > ~/.rzcode/config.json << 'EOF'
{
  "api_key": "sk.xxx.yyy",
  "api_host": "https://rzcode.vip"
}
EOF
chmod 600 ~/.rzcode/config.json
```

### 第 2 步：导入书籍

```python
import requests
import json

# 加载配置
with open(os.path.expanduser("~/.rzcode/config.json")) as f:
    config = json.load(f)

headers = {"X-API-Key": config["api_key"]}

# 创建书籍
response = requests.post(
    f"{config['api_host']}/api/study/books/深度学习",
    json={
        "authors": ["Ian Goodfellow"],
        "edition": "第1版"
    },
    headers=headers
)
print(f"Book created: {response.json()}")
```

### 第 3 步：创建概念和关系

```python
# 创建概念
response = requests.post(
    f"{config['api_host']}/api/study/concepts/反向传播",
    json={
        "canonical_name": "反向传播",
        "kind": "方法",
        "definition": "通过链式法则计算梯度的算法"
    },
    headers=headers
)

# 标记出现位置（注意：路由用下划线；role 与 source 两个字段都必须给，缺一个会 400）
response = requests.post(
    f"{config['api_host']}/api/study/relationships/mentioned_in",
    json={
        "concept_title": "反向传播",
        "chapter_title": "第6章 深度学习基础",
        "role": "核心算法",
        "source": "agent"
    },
    headers=headers
)
```

## 最小可用工具集

| 工具 | 说明 | 何时用 |
|------|------|--------|
| `list_books` | 列出所有书籍 | 查看已导入的书籍 |
| `upsert_concept` | 创建或更新概念 | 定义新概念 |
| `search_knowledge` | 搜索概念 | 查找概念避免重复 |
| `get_knowledge_graph` | 查看知识图谱 | 理解概念关系 |
| `create_note` | 创建笔记 | 添加学习笔记 |

完整工具列表见 [20-tools.md](20-tools.md)。

## 最佳实践

### ✅ DO

1. **先搜索再创建** - 调用 `search_knowledge` 查重，避免重复概念
2. **批量写入** - 将多个操作合并减少 API 调用
3. **使用规范名称** - 遵循 [canonical_naming.md](../resources/docs/canonical_naming.md) 的命名规范
4. **保存配置文件** - 用 `~/.rzcode/config.json` 管理 API key
5. **验证结果** - 写入后用 `get_book` 或 `get_concept` 验证

### ❌ DON'T

1. **硬编码 API key** - 使用配置文件或环境变量
2. **频繁调用 API** - 在循环中调用应该批量进行
3. **跳过查重** - 直接创建可能导致重复概念
4. **忽视错误** - 总是检查 HTTP 状态码和错误信息
5. **修改已有数据** - 如需变更，使用 upsert 而不是直接更新

## 常见问题 (FAQ)

**Q: 如何重新开始学习一本书？**

A: 调用 `delete_book` 删除整本书及其所有数据，然后重新创建。

**Q: 支持导入 PDF 吗？**

A: 支持。使用 `upload_book` 上传 PDF 文件，使用 `upload_note` 上传笔记文件。

**Q: 可以离线使用吗？**

A: 不行。所有操作都需要通过 API 调用，需要网络连接和 API key。

**Q: 如何回退到本地 v1.0 版本？**

A: 查看 [30-advanced.md](30-advanced.md#从-v20-回退到-v10) 的回退指南。

**Q: API key 的有效期是多久？**

A: 永久有效，除非在 https://rzcode.vip/settings 中吊销。

## 下一步

- 学习工作流 → [10-workflow.md](10-workflow.md)
- 查看工具参考 → [20-tools.md](20-tools.md)
- 查阅高级主题 → [30-advanced.md](30-advanced.md)
- 查看示例代码 → [../examples/](../examples/)
