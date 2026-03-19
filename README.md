# AI论文预研助手

基于OpenCrew多智能体协作框架的AI论文研究平台，支持自动检索arXiv论文、智能分析、知识图谱可视化、对比矩阵、智能问答等功能。

## ✨ 功能特性

### 核心功能
1. **论文检索** - 从arXiv自动检索真实论文数据
2. **智能分析** - 自动提取方法、数据集、创新点
3. **综述生成** - 自动生成研究报告
4. **知识图谱** - ECharts交互式论文关系网络可视化
5. **对比矩阵** - 多维度论文对比分析
6. **智能问答** - 基于论文内容的自然语言问答

### 飞书深度集成
- **多维表格** - 自动创建并填充论文数据
- **知识库** - 归档研究报告和可视化内容
- **消息卡片** - 发送研究成果通知
- **每日推送** - 定时推送最新论文

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/wangbo/.openclaw/workspace/projects/paper-research-assistant
python3 -m venv venv
source venv/bin/activate
pip install feedparser flask flask-cors networkx
```

### 2. 运行研究（命令行）

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行研究
python3 run.py "AI Agent" --max-papers 20

# 禁用飞书集成
python3 run.py "Transformer" --max-papers 30 --no-feishu

```

### 3. 启动Web界面

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动API服务器
python3 api_server.py

# 访问 http://localhost:5000
```

## 📊 可视化输出

运行研究后，在 `output/` 目录生成以下文件：

- `knowledge_graph_enhanced.html` - ECharts知识图谱
- `comparison_matrix_enhanced.html` - 对比矩阵
- `papers.json` - 论文数据
- `review.md` - 研究综述
- `research_results.json` - 完整结果

## 📁 项目结构

```
paper-research-assistant/
├── run.py                    # 主运行脚本
├── api_server.py             # API服务器
├── config/
│   └── feishu_config.py      # 飞书配置
├── src/
│   ├── agents/
│   │   └── sub_agents.py     # 子智能体（检索、解析、分析、综述）
│   ├── visualization/
│   │   ├── enhanced_knowledge_graph.py    # 知识图谱可视化
│   │   └── enhanced_comparison_matrix.py  # 对比矩阵
│   ├── qa/
│   │   └── intelligent_qa.py # 智能问答系统
│   ├── feishu/
│   │   └── deep_integration.py # 飞书深度集成
│   └── utils/
│       └── logger.py         # 日志工具
├── web/
│   └── index.html            # Web界面
├── output/                   # 输出目录
└── docs/
    └── 项目说明书.md          # 项目说明书
```

## 🔧 配置

### 飞书配置

编辑 `config/feishu_config.py`:

```python
# 飞书应用配置
FEISHU_APP_ID = "cli_xxx"
FEISHU_APP_SECRET = "xxx"

# 目标用户
TARGET_USER_ID = "ou_xxx"
```

## 📖 API文档

### GET /api/status
获取系统状态

### POST /api/research
运行研究
```json
{
  "topic": "AI Agent",
  "max_papers": 20,
  "enable_feishu": true
}
```

### POST /api/qa
智能问答
```json
{
  "question": "主要的研究方法有哪些？"
}
```

### GET /api/papers
获取论文列表

### GET /api/visualizations
获取可视化列表

### POST /api/feishu/bitable
创建飞书多维表格

### POST /api/feishu/wiki
归档到飞书知识库

### POST /api/feishu/push
发送飞书消息卡片

## 🎯 使用示例

### 命令行模式

```bash
# 研究"大模型微调"主题
python3 run.py "LLM fine-tuning" --max-papers 30

# 研究后提问
python3 run.py "Transformer" --max-papers 20
python3 run.py --question "哪些论文使用了注意力机制？"
```

### Web界面模式

1. 启动服务器: `python3 api_server.py`
2. 访问 http://localhost:5000
3. 输入研究课题，点击"开始研究"
4. 查看可视化、智能问答、飞书集成

## 📊 项目进度

- [x] 论文检索（arXiv真实数据）
- [x] 智能分析（方法、数据集、创新点提取）
- [x] 综述生成
- [x] 知识图谱可视化（ECharts）
- [x] 论文对比矩阵
- [x] 智能问答系统
- [x] 飞书多维表格集成
- [x] 飞书知识库集成
- [x] 飞书消息卡片
- [x] Web界面

## 📝 更新日志

### v2.0.0 (2026-03-18)
- 实现ECharts增强版知识图谱
- 实现增强版论文对比矩阵
- 实现智能问答系统
- 完善飞书深度集成
- 更新Web界面，连接真实API

### v1.0.0
- 初始版本
- 基础论文检索和分析功能
