---
name: rzcode-study-skill
version: 2.1.0
description: "通过云端 API 对接 RZCode 学习知识库，管理书籍、概念、笔记和知识关系"
category: knowledge_management
tags:
  - knowledge_graph
  - learning
  - study
  - api
  - rzcode
author: "Yi Wang"
maintainer: "Yi Wang"
license: MIT
---

# RZCode Study Skill

通过云端 API 对接 RZCode 学习知识库，管理书籍、概念、笔记和知识关系的强大工具。

## 快速开始（2分钟）

### 1. 配置 API Key

获取 API key：访问 [https://rzcode.vip/settings](https://rzcode.vip/settings)

配置到 `~/.rzcode/config.json`：
```json
{
  "api_key": "your_api_key_here",
  "api_host": "https://rzcode.vip"
}
```

### 2. 第一次调用

```python
import requests
import json

# 加载配置
with open(os.path.expanduser("~/.rzcode/config.json")) as f:
    config = json.load(f)

headers = {
    "X-API-Key": config["api_key"]
}

# 列出所有书籍
response = requests.get(
    f"{config['api_host']}/api/study/books/",
    headers=headers
)
books = response.json()
print(f"Total books: {len(books.get('books', []))}")
```

更多示例见 [examples/](examples/)。

## 核心能力

| 能力 | 工具 | 说明 |
|------|------|------|
| 📚 书籍管理 | list_books, get_book, upsert_book, delete_book | 创建、查询、删除书籍 |
| 📖 章节管理 | upsert_chapter, delete_chapter, list_chapters | 支持嵌套层级的章节结构 |
| 💡 概念管理 | upsert_concept, delete_concept, get_concept | 定义学习概念 |
| 📝 笔记管理 | create_note, upload_note, get_note, list_notes | 文本或文件笔记 |
| 🔗 关系管理 | upsert_part_of, upsert_mentioned_in, upsert_related_to, upsert_prerequisite_for | 构建知识图谱 |
| 🔍 知识查询 | search_knowledge, get_knowledge_graph, get_graph_stats | 查询和分析知识库 |

## 批量导入目录（推荐）

> 📌 依赖：Python 3.7+；使用 requests 示例前请先 `pip install requests`；批量导入也可直接用 `curl`（无第三方依赖）。
> 已封装脚本：[scripts/generate_import_cmds.py](scripts/generate_import_cmds.py)

```bash
# 1) 把出版社页面的目录贴进 toc.txt（每行：编号 标题 页码）
# 2) 生成 curl 批处理
python3 scripts/generate_import_cmds.py toc.txt \
    --book "书名" --author "作者A" --author "作者B" \
    --edition "出版社 时间 · ISBN xxx" --out /tmp/import_cmds.sh
# 3) 执行（每个请求打印一行状态码，200/201 即成功）
sh /tmp/import_cmds.sh
# 4) 校验：chapters 接口返回的是嵌套树，统计总数要递归 children
curl -sL -H "X-API-Key: $KEY" "$HOST/api/study/books/<url编码书名>/chapters"
```

## 架构设计

```
书籍 (Book)
├─ 章节 (Chapter)
│  └─ 章节 (Chapter, 嵌套)
│     └─ 笔记 (Note)
│
概念 (Concept)
├─ 别名、定义、类型
└─ 关系
   ├─ MENTIONED_IN: 在哪些章节出现
   ├─ RELATED_TO: 相关概念
   ├─ PREREQUISITE_FOR: 学习依赖，其中前置关系，包含相关关系。
   └─ 笔记 (Note)
```

其中 PART_OF 表示书籍与章节，父章节与子章节的层级关系。
MENTIONED_IN 表示概念在某些章节中出现。
RELATED_TO 表示概念之间的关联。
PREREQUISITE_FOR 表示概念的前置依赖关系。（前置关系优先于相关关系：两个概念若已有 PREREQUISITE_FOR，再建 RELATED_TO 会被服务端返回 409 拒绝，这是预期行为。）

> 📌 **路由以 `tools/*.tool.json` 的 `endpoint` 字段为准**（已逐条核对，全部可用），字段与行为细节见 `instructions/20-tools.md` 顶部的「使用须知」。

## 工作流示例

### 工作流 1：导入书籍并组织知识

1. `upsert_book` - 创建书籍
2. `upsert_chapter` - 添加章节（支持嵌套）
3. `upsert_part_of` - 明确层级关系
4. 验证：`get_book` + `list_chapters`

### 工作流 2：提取和标记概念

1. `upsert_concept` - 定义新概念
2. `search_knowledge` - 查重避免重复
3. `upsert_mentioned_in` - 标记出现位置
4. `upsert_related_to` - 建立关联
5. 验证：`get_knowledge_graph`

### 工作流 3：添加学习笔记

1. `create_note` - 文本笔记（markdown）
2. `upload_note` - 文件笔记（PDF、图片等）
3. `list_notes` - 查看笔记列表
4. 验证：`get_note`

## 使用指南

- **新手上路** → [00-overview.md](instructions/00-overview.md)
- **工作流详解** → [10-workflow.md](instructions/10-workflow.md)
- **工具完全参考** → [20-tools.md](instructions/20-tools.md)
- **高级主题** → [30-advanced.md](instructions/30-advanced.md)
- **示例代码** → [examples/](examples/)
- **规范命名** → [resources/docs/canonical_naming.md](resources/docs/canonical_naming.md)

## 支持

如有问题，请：
1. 查阅 [30-advanced.md](instructions/30-advanced.md) 的故障排查章节
2. 检查 [examples/](examples/) 中的示例代码
3. 确保配置了正确的 API key 和 api_host
