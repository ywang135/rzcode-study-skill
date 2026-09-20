# RZCode Study Skill

通过云端 API 对接 RZCode 学习知识库的 Agent Skill。通过 cloud API 管理书籍、概念、笔记和知识关系，构建完整的学习知识图谱。

## ✨ 核心功能

- 📚 **书籍管理** - 导入、组织、删除书籍
- 📖 **章节管理** - 支持嵌套层级的章节结构
- 💡 **概念管理** - 定义、搜索、更新学习概念
- 📝 **笔记管理** - 文本或文件形式的学习笔记
- 🔗 **关系管理** - 建立知识之间的关系（包含、提及、相关、依赖）
- 🔍 **知识查询** - 搜索、可视化知识图谱

## 🚀 快速开始

### 1. 获取 API Key

访问 [https://rzcode.vip/settings](https://rzcode.vip/settings) 生成 API key。

### 2. 配置

创建 `~/.rzcode/config.json`：
```json
{
  "api_key": "your_api_key_here",
  "api_host": "https://rzcode.vip"
}
```

### 3. 使用

```python
# 参见 examples/ 中的示例代码
python examples/import_book_example.py
python examples/manage_concepts_example.py
python examples/knowledge_graph_example.py
```

## 📁 目录结构

```
rzcode-study-skill/
├── SKILL.md                   # Skill 入口点
├── README.md                  # 本文件
├── manifest.yaml              # 配置信息
├── .skillignore               # 忽略文件列表
│
├── instructions/              # 使用指南
│   ├── 00-overview.md        # 概念和基础（新手必读）
│   ├── 10-workflow.md        # 常见工作流和使用场景
│   ├── 20-tools.md           # 工具完全参考
│   └── 30-advanced.md        # 高级主题和故障排查
│
├── tools/                     # API 工具定义（25 个）
│   ├── list_books.json
│   ├── get_book.json
│   ├── upsert_concept.json
│   ├── search_knowledge.json
│   ├── get_knowledge_graph.json
│   └── ... 其他 22 个工具
│
├── resources/                 # 静态资源
│   └── docs/
│       └── canonical_naming.md  # 规范命名检查清单
│
└── examples/                  # 可运行的示例代码
    ├── import_book_example.py
    ├── manage_concepts_example.py
    └── knowledge_graph_example.py
```

## 🛠️ 主要工具

| 工具 | 功能 | 用途 |
|------|------|------|
| `list_books` | 列出书籍 | 查看已导入的所有书籍 |
| `get_book` | 获取书籍详情 | 查看书籍和所有章节 |
| `upsert_book` | 创建/更新书籍 | 导入新书或更新元数据 |
| `upsert_chapter` | 创建/更新章节 | 添加和管理章节结构 |
| `get_concept` | 获取概念详情 | 查看概念定义和出处 |
| `upsert_concept` | 创建/更新概念 | 定义新学习概念 |
| `search_knowledge` | 搜索概念 | 快速查找相关概念 |
| `create_note` | 创建笔记 | 添加文本笔记 |
| `upload_note` | 上传笔记 | 上传文件笔记（PDF等） |
| `upsert_mentioned_in` | 建立提及关系 | 标记概念在哪些章节出现 |
| `get_knowledge_graph` | 查看知识图谱 | 可视化概念关系网络 |

完整列表参见 [20-tools.md](instructions/20-tools.md)。

## 🔄 典型工作流

### 流程 1：导入书籍

1. `upsert_book` - 创建书籍
2. `upsert_chapter` - 添加章节（支持嵌套）
3. 验证：`get_book` 查看结果

### 流程 2：提取概念并建立关系

1. `search_knowledge` - 查重，避免重复
2. `upsert_concept` - 定义新概念
3. `upsert_mentioned_in` - 标记出现位置
4. `upsert_related_to` - 建立关联
5. `upsert_prerequisite_for` - 建立前后置关系
6. 验证：`get_knowledge_graph` 查看关系

### 流程 3：添加学习笔记

1. `create_note` - 文本笔记
2. `upload_note` - 文件笔记
3. `list_notes` - 查看笔记列表

## 📚 使用指南

| 指南 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 快速入门和架构概览 |
| [00-overview.md](instructions/00-overview.md) | 新手必读：核心概念 |
| [10-workflow.md](instructions/10-workflow.md) | 常见工作流详解 |
| [20-tools.md](instructions/20-tools.md) | 工具完全参考手册 |
| [30-advanced.md](instructions/30-advanced.md) | 高级主题和故障排查 |
| [canonical_naming.md](resources/docs/canonical_naming.md) | 命名规范检查清单 |
| [examples/](examples/) | 示例代码 |

## 🌐 环境配置

### 生产环境（默认）
```json
{
  "api_host": "https://rzcode.vip",
  "api_key": "your_api_key"
}
```

### 本地调试
```json
{
  "api_host": "http://localhost:8000",
  "api_key": "your_api_key"
}
```

## 🔐 安全提示

- 🔒 **不要**在代码中硬编码 API key
- 📄 使用 `~/.rzcode/config.json`
- 🔑 生成 API key：https://rzcode.vip/settings
- ⚠️ 保持 config.json 权限为 `600`

## 🤝 贡献

如有问题或建议，请查阅 [30-advanced.md](instructions/30-advanced.md#故障排查) 的故障排查章节。

## 📝 许可

MIT License
