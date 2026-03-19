# AI论文预研助手 - 功能说明

## 📊 项目概览

AI论文预研助手是一个基于多智能体协作的学术研究辅助系统，支持从论文检索、分析、可视化到综述生成的全流程自动化。

## 🎯 已完成功能

### 1. 论文检索系统 ✅
- **数据源**: arXiv API（真实数据）
- **功能**: 根据研究课题自动检索相关论文
- **支持**: 关键词提取、结果过滤、批量检索

### 2. 知识图谱可视化 ✅
- **技术**: ECharts
- **功能**: 
  - 论文关系网络图
  - 作者合作关系图
  - 关键词共现网络
  - 交互式探索

### 3. 论文对比矩阵 ✅
- **功能**:
  - 多维度对比（方法、数据集、创新点）
  - 统计分析（方法分布、年份分布）
  - 交互式HTML表格

### 4. 论文详情弹窗 ✅
- **功能**:
  - 论文基本信息展示
  - PDF在线查看
  - 引用信息

### 5. 智能问答系统 ✅ (已增强)
- **增强功能**:
  - 支持15+种问题类型
  - 方法类：方法概览、方法详情、方法对比
  - 数据集类：数据集概览、数据集使用情况
  - 趋势类：时间趋势、研究热点
  - 论文类：论文查找、论文推荐、论文对比
  - 作者类：作者论文查询
  - 综合类：研究总结、研究空白、未来方向
- **引用来源追踪**: 每个答案都附带相关论文引用
- **问题类型识别**: 自动识别问题类型并提供专业化回答
- **多轮对话**: 支持对话上下文管理

### 6. 综述报告生成 ✅ (已增强)
- **支持格式**:
  - Markdown格式（完整结构化报告）
  - LaTeX格式（学术论文格式）
- **报告内容**:
  - 研究背景与意义
  - 文献综述（核心文献概览）
  - 主要发现（方法发现、数据集发现）
  - 研究方法分析（方法分布、特点）
  - 数据集分析（使用分布、特点）
  - 研究趋势（时间趋势、方法趋势、未来展望）
  - 研究空白与未来方向
  - 代表性论文
  - 完整参考文献
  - 附录（作者统计、关键词统计、分类统计）

### 7. 飞书深度集成 ✅ (已增强)
- **多维表格**:
  - 自动创建论文数据库
  - 字段：标题、作者、发表时间、研究方法、数据集、核心结论、PDF链接
  - 支持批量导入论文数据
- **知识库**:
  - 归档研究报告
  - 存储论文列表
  - 上传可视化结果
- **消息卡片**:
  - 研究完成通知
  - 成果推送
- **每日推送**:
  - 定时推送最新论文
  - 支持关键词订阅

### 8. 数据持久化 ✅ (新增)
- **本地存储**:
  - 论文数据JSON格式保存
  - 元数据管理
- **缓存机制**:
  - 内存缓存
  - 文件缓存
  - 缓存过期管理
- **导入/导出**:
  - JSON格式导入导出
  - CSV格式导出（Excel兼容）
  - BibTeX格式导出（学术引用）
- **数据管理**:
  - 历史数据列表
  - 数据版本管理
  - 缓存清理

### 9. Web界面 ✅
- **UI/UX**:
  - 现代化深色主题
  - 响应式设计
  - 流畅动画效果
- **功能面板**:
  - 研究控制面板
  - 论文列表展示
  - 智能问答界面
  - 飞书集成面板
  - 报告管理面板
  - 数据管理面板

## 🚀 使用方法

### 启动服务

```bash
# 1. 进入项目目录
cd /Users/wangbo/.openclaw/workspace/projects/paper-research-assistant

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 启动API服务器
python api_server.py

# 4. 在浏览器访问
open http://localhost:8088
```

### 命令行使用

```bash
# 运行研究
python run.py "Transformer" --max-papers 30

# 禁用飞书集成
python run.py "AI Agent" --no-feishu

# 指定输出目录
python run.py "NLP" --output-dir output/nlp
```

### API接口

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/status` | GET | 获取系统状态 |
| `/api/research` | POST | 开始研究 |
| `/api/papers` | GET | 获取论文列表 |
| `/api/qa` | POST | 智能问答 |
| `/api/qa/history` | GET | 获取问答历史 |
| `/api/report/generate` | POST | 生成报告 |
| `/api/data/save` | POST | 保存数据 |
| `/api/data/load` | GET | 加载数据 |
| `/api/data/export` | POST | 导出数据 |
| `/api/feishu/bitable` | POST | 创建多维表格 |
| `/api/feishu/wiki` | POST | 归档知识库 |

## 📝 智能问答示例

```
用户: 主要的研究方法有哪些？
系统: 识别出15种主要研究方法：Transformer、CNN、RNN/LSTM...
     [附带相关论文引用]

用户: 哪些论文使用了Transformer？
系统: 共有25篇论文使用了Transformer方法...
     [列出具体论文和链接]

用户: 研究趋势是什么？
系统: 从2020年到2024年，论文数量增长了150%...
     [提供时间分布表格和趋势分析]
```

## 🔧 技术架构

```
AI论文预研助手
├── 后端 (Python 3.9+)
│   ├── Flask API服务器
│   ├── 多智能体协作系统
│   │   ├── ArxivSearcher - 论文检索
│   │   ├── CitationAnalyzer - 引用分析
│   │   ├── PDFParser - PDF解析
│   │   └── ReviewWriter - 综述撰写
│   ├── 智能问答系统
│   │   ├── IntelligentQA - 基础问答
│   │   └── EnhancedQA - 增强问答
│   ├── 报告生成器
│   │   ├── ReportGenerator - 基础报告
│   │   └── EnhancedReportGenerator - 增强报告
│   ├── 飞书集成
│   │   ├── FeishuDeepIntegration - 基础集成
│   │   └── FeishuRealIntegration - 真实API
│   └── 数据持久化
│       └── DataPersistence - 存储管理
├── 前端 (原生HTML + JavaScript)
│   ├── Tailwind CSS
│   ├── ECharts可视化
│   └── 响应式设计
└── 数据源
    └── arXiv API
```

## 📁 项目结构

```
paper-research-assistant/
├── api_server.py          # API服务器
├── run.py                 # 主运行脚本
├── config/
│   └── feishu_config.py   # 飞书配置
├── src/
│   ├── agents/
│   │   └── sub_agents.py  # 多智能体
│   ├── qa/
│   │   ├── intelligent_qa.py
│   │   └── enhanced_qa.py # 增强问答
│   ├── generators/
│   │   ├── report_generator.py
│   │   └── enhanced_report_generator.py
│   ├── feishu/
│   │   ├── deep_integration.py
│   │   └── real_integration.py
│   ├── utils/
│   │   ├── logger.py
│   │   └── data_persistence.py # 数据持久化
│   └── visualization/
│       ├── enhanced_knowledge_graph.py
│       └── enhanced_comparison_matrix.py
├── web/
│   └── index.html         # 前端界面
├── output/
│   ├── papers/            # 论文数据
│   ├── reports/           # 生成的报告
│   ├── cache/             # 缓存数据
│   └── exports/           # 导出文件
└── requirements.txt
```

## ✨ 特色功能

1. **真实数据**: 所有论文数据来自arXiv真实API，无Mock数据
2. **智能问答**: 支持多维度问题分析，提供精确引用来源
3. **双格式报告**: 同时支持Markdown和LaTeX格式
4. **飞书集成**: 深度集成飞书生态，支持多维表格、知识库、消息推送
5. **数据持久化**: 完善的缓存机制，避免重复检索
6. **可视化**: ECharts交互式知识图谱和对比矩阵
7. **响应式UI**: 现代化深色主题，流畅动画效果

## 🔮 未来计划

- [ ] 支持更多数据源（Semantic Scholar、Google Scholar）
- [ ] 增强PDF解析能力（表格提取、图表分析）
- [ ] 实现多语言支持
- [ ] 添加用户认证系统
- [ ] 支持协作研究

---

**版本**: v2.0.0  
**更新时间**: 2026-03-18  
**作者**: AI论文预研助手团队
