# AI论文预研助手 V3.0 - 重大升级

## 🎉 新增功能

### 1. 知识库系统 (Personal Knowledge Base)

**功能**：向聊天框扔URL、推文、文章，构建可搜索的知识库

**使用方式**：

```python
from src.knowledge.base import KnowledgeBase

# 初始化知识库
kb = KnowledgeBase()

# 添加URL
kb.add_url(
    url="https://arxiv.org/abs/2026.xxxxx",
    title="大模型综述",
    content="...",
    tags=["AI", "论文"]
)

# 添加文章
kb.add_article(
    title="AI Agent最佳实践",
    content="...",
    source="知乎",
    tags=["AI", "Agent"]
)

# 添加推文
kb.add_tweet(
    tweet_id="1234567890",
    author="@elonmusk",
    content="AI is the future",
    url="https://x.com/..."
)

# 搜索知识库
results = kb.search("大模型应用")
```

**API接口**：

```
GET  /api/knowledge           # 获取所有知识
POST /api/knowledge           # 添加知识
GET  /api/knowledge/search?q= # 搜索知识库
DELETE /api/knowledge/<id>    # 删除知识
```

---

### 2. Web可视化界面

**启动方式**：

```bash
cd /Users/wangbo/.openclaw/workspace/projects/paper-research-assistant
bash start_web.sh
# 选择 1) 启动Web界面

# 或直接运行
python api_server.py
```

**访问地址**：http://localhost:5000

**界面功能**：

| 页面 | 功能 |
|------|------|
| **首页** | 统计概览、快捷入口 |
| **论文研究** | 输入课题、自动检索综述 |
| **知识库** | 添加/搜索知识条目 |
| **可视化** | 知识图谱、对比矩阵、智能问答 |
| **飞书集成** | 创建飞书文档、同步研究 |

---

### 3. 飞书文档深度集成

**功能**：

- ✅ 自动创建飞书文档
- ✅ 写入研究综述
- ✅ 分享给协作者
- ✅ 文档历史记录

**使用方式**：

**方式1：Web界面**

1. 访问 http://localhost:5000
2. 点击"飞书集成"标签
3. 输入标题和内容
4. 点击"创建飞书文档"

**方式2：API调用**

```python
from src.utils.feishu_integration import FeishuDocumentManager

feishu = FeishuDocumentManager()

# 创建文档
doc = feishu.create_document("研究综述: AI Agent")

# 写入内容
feishu.write_content(doc['document_id'], "# 标题\n\n内容...")

# 分享文档
feishu.share_document(doc['document_id'], ["ou_xxx"], "edit")
```

**方式3：研究时自动同步**

```bash
# 研究完成后自动创建飞书文档
python scripts/run_crew.py --topic "研究课题" --feishu --auto-confirm
```

---

### 4. 可视化增强

**新增3个可视化**：

| 可视化 | 文件 | 功能 |
|--------|------|------|
| **知识图谱** | output/knowledge_graph.html | 论文关系网络（D3.js交互式） |
| **对比矩阵** | output/comparison_matrix.html | 多维度论文对比表格 |
| **智能问答** | output/qa_demo.html | 评委实时提问演示 |

**比赛演示流程**：

1. 打开知识图谱 → "这是自动生成的论文关系网络"
2. 打开对比矩阵 → "论文对比一目了然"
3. 打开智能问答 → "评委可以提问试试"

---

## 📁 项目结构

```
paper-research-assistant/
├── web/                        # Web界面
│   └── index.html             # 单页应用
├── src/
│   ├── crew/                  # OpenCrew多智能体
│   ├── knowledge/             # 知识库模块 ✨新增
│   │   ├── __init__.py
│   │   └── base.py
│   ├── visualization/         # 可视化模块
│   ├── qa/                    # 智能问答
│   └── utils/
│       └── feishu_integration.py
├── scripts/
│   └── run_crew.py
├── api_server.py              # API服务器 ✨新增
├── start_web.sh               # 启动脚本 ✨新增
├── test_crew.py
└── requirements.txt
```

---

## 🚀 快速开始

### 方式1：Web界面（推荐）

```bash
cd /Users/wangbo/.openclaw/workspace/projects/paper-research-assistant
bash start_web.sh
# 选择 1) 启动Web界面
# 访问 http://localhost:5000
```

### 方式2：API服务器

```bash
python api_server.py
# API文档: http://localhost:5000/api
```

### 方式3：CLI命令

```bash
# 基础研究
python scripts/run_crew.py --topic "研究课题" --auto-confirm

# 研究+飞书文档
python scripts/run_crew.py --topic "研究课题" --feishu --auto-confirm
```

---

## 📊 功能对比

| 功能 | V1.0 | V2.0 | V3.0 |
|------|------|------|------|
| 论文检索 | ✅ | ✅ | ✅ |
| 综述撰写 | ✅ | ✅ | ✅ |
| OpenCrew架构 | - | ✅ | ✅ |
| 三模型审查 | - | ✅ | ✅ |
| 飞书文档 | 手动 | 手动 | **自动** ✨ |
| 知识库 | - | - | **✅** ✨ |
| Web界面 | - | - | **✅** ✨ |
| 可视化 | - | - | **3个** ✨ |

---

## 🔧 API文档

### 研究API

```bash
# 开始研究
curl -X POST http://localhost:5000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "大模型在教育领域的应用",
    "max_papers": 50,
    "sync_feishu": true
  }'
```

### 知识库API

```bash
# 添加URL
curl -X POST http://localhost:5000/api/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "type": "url",
    "url": "https://arxiv.org/abs/2026.xxxxx",
    "title": "大模型综述",
    "tags": ["AI", "论文"]
  }'

# 搜索知识库
curl http://localhost:5000/api/knowledge/search?q=大模型

# 获取所有知识
curl http://localhost:5000/api/knowledge
```

### 飞书API

```bash
# 创建飞书文档
curl -X POST http://localhost:5000/api/feishu/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "研究综述",
    "content": "# 标题\n\n内容..."
  }'
```

---

## 🎯 比赛亮点

1. **知识库系统** - 个人知识管理，可搜索
2. **Web界面** - 现代化UI，无需命令行
3. **飞书集成** - 自动创建文档，团队协作
4. **三大可视化** - 知识图谱、对比矩阵、智能问答
5. **OpenCrew架构** - 4个专业Agent协作

---

## 📝 更新日志

**V3.0 (2026-03-13)**
- ✨ 新增知识库系统
- ✨ 新增Web可视化界面
- ✨ 新增API服务器
- ✨ 深度集成飞书文档
- ✨ 新增3个可视化工具

**V2.0 (2026-03-13)**
- ✨ OpenCrew多智能体架构
- ✨ Agent Swarm模式
- ✨ 三模型质量审查
- ✨ Ralph Loop V2

**V1.0 (2026-03-11)**
- ✅ 基础论文检索
- ✅ 综述撰写
- ✅ Markdown/LaTeX输出

---

**状态**：✅ V3.0升级完成，生产就绪
**更新时间**：2026年3月13日 23:30
