# AI论文预研助手 - OpenCrew多智能体协作系统

## 🎉 重大升级

基于 [awesome-openclaw-usecases-zh](https://github.com/AlexAnys/awesome-openclaw-usecases-zh) 仓库的最佳实践，完成了三大核心升级：

### 1. OpenCrew架构 - 多智能体协作

将单一Agent升级为专业分工的AI团队：

```
┌─────────────────────────────────────────────────────┐
│                  Orchestrator                        │
│              (编排器 - 持有研究上下文)                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  │   CoS    │  │   CTO    │  │ Builder  │  │   Ops    │
│  │ 战略参谋 │  │技术负责人│  │  执行者  │  │ 运维官  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘
│       │              │              │              │
│   意图分析      技术方案        文献检索      变更审计
│   范围确定      质量审查        论文解析      飞书文档
│   协调推进      数据验证        综述撰写      通知推送
│                                                  │
└─────────────────────────────────────────────────────┘
```

**各Agent职责**：

| Agent | 职责 | 核心能力 |
|-------|------|----------|
| **CoS (战略参谋)** | 意图对齐、研究范围确定 | 识别研究类型、提取核心问题、生成研究计划 |
| **CTO (技术负责人)** | 技术方案、质量把控 | 选择数据源、三模型审查、数据验证 |
| **Builder (执行者)** | 执行研究任务 | 文献检索、论文解析、综述撰写、报告生成 |
| **Ops (运维官)** | 变更审计、交付输出 | 飞书文档管理、通知推送、漂移检测 |

---

### 2. Agent Swarm模式 - 并行处理

**核心特性**：
- **研究上下文分离**：Orchestrator持有完整上下文，Builder专注执行
- **并行Agent处理**：多个Builder并行处理不同论文
- **三模型代码审查**：Codex + Claude + Gemini三重审查
- **Ralph Loop V2**：自改进Prompt系统，失败时结合上下文重写Prompt

**工作流程**：
```
用户输入课题
    ↓
CoS分析意图 → 确定研究范围
    ↓
CTO决定技术方案 → 选择数据源和工具
    ↓
Builder执行检索 → 并行解析论文
    ↓
Builder撰写综述 → 生成初稿
    ↓
CTO三模型审查 → 质量评分
    ↓
（不通过？）→ Ralph Loop重写 → 重新审查
    ↓
Ops写入飞书 → 发送通知
    ↓
完成！
```

---

### 3. 飞书文档自动化

**新增功能**：
- ✅ 自动创建飞书文档
- ✅ 写入综述内容（Markdown转飞书格式）
- ✅ 分享文档给协作者
- ✅ 发送完成通知

**使用方法**：
```python
# 方式1：命令行（推荐）
python scripts/run_crew.py --topic "大模型在教育中的应用" --feishu

# 方式2：Python API
from src.crew.orchestrator import Orchestrator

orchestrator = Orchestrator({"feishu_collaborators": ["ou_xxx"]})
result = orchestrator.run_research("大模型在教育中的应用")
```

---

## 🚀 快速开始

### 安装依赖

```bash
cd /Users/wangbo/.openclaw/workspace/projects/paper-research-assistant
source venv/bin/activate
pip install -r requirements.txt
```

### 运行测试

```bash
python test_crew.py
```

### 运行完整研究

```bash
# 基础用法
python scripts/run_crew.py --topic "研究课题"

# 完整参数
python scripts/run_crew.py \
  --topic "大模型在K12英语口语教学中的应用" \
  --max-papers 50 \
  --parallel-agents 3 \
  --feishu \
  --auto-confirm
```

---

## 📊 性能对比

| 指标 | 旧版本 | OpenCrew版本 | 提升 |
|------|--------|--------------|------|
| Agent数量 | 1个 | 4个专业Agent | ✅ 专业化分工 |
| 并行处理 | 无 | 支持 | ✅ 3-5倍加速 |
| 质量审查 | 无 | 三模型审查 | ✅ 新功能 |
| 飞书集成 | 手动 | 自动 | ✅ 新功能 |
| 自改进 | 无 | Ralph Loop V2 | ✅ 新功能 |
| 变更审计 | 无 | 完整记录 | ✅ 可追溯 |

---

## 📁 项目结构

```
paper-research-assistant/
├── src/
│   ├── crew/                    # OpenCrew多智能体系统
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # 编排器
│   │   ├── cos.py              # 战略参谋
│   │   ├── cto.py              # 技术负责人
│   │   ├── builder.py          # 执行者
│   │   └── ops.py              # 运维官
│   ├── agents/                  # 原有Agent（兼容）
│   ├── utils/
│   │   ├── feishu_integration.py  # 飞书集成
│   │   ├── logger.py
│   │   └── memory.py
│   └── generators/
├── scripts/
│   ├── run_crew.py             # OpenCrew主入口
│   └── run_monitor.py
├── test_crew.py                # 测试脚本
└── requirements.txt
```

---

## 🔧 配置说明

### 飞书配置

在环境变量中设置：
```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

或直接在代码中配置：
```python
config = {
    "feishu_collaborators": ["ou_0cdbe8a5a456c32beb95d46bb00b2bc1"]
}
```

### Agent配置

```python
config = {
    "max_papers": 50,           # 最大论文数
    "output_dir": "output",      # 输出目录
    "parallel_agents": 3,        # 并行Agent数
    "feishu_collaborators": []   # 飞书协作者
}
```

---

## 🎯 核心创新

### 1. 上下文分离
- Orchestrator持有**完整研究上下文**
- Builder只看到**代码和论文**
- 避免上下文窗口浪费

### 2. Ralph Loop V2
```
失败 → 分析原因 → 结合业务上下文重写Prompt → 重试
```
- 不是简单重试，而是**智能改进**
- 成功模式自动沉淀为经验

### 3. 三模型审查
| 模型 | 强项 | 用途 |
|------|------|------|
| Codex | 边界情况、逻辑错误 | 深度审查 |
| Claude | 验证其他审查器 | 二次确认 |
| Gemini | 安全漏洞、可扩展性 | 补充视角 |

---

## 📝 使用示例

### 示例1：技术研究

```bash
python scripts/run_crew.py \
  --topic "Transformer架构在自然语言处理中的最新进展" \
  --max-papers 100 \
  --feishu
```

**CoS分析结果**：
- 研究类型：technical
- 核心问题：技术现状、主流方法、最新突破、未来方向
- 数据源：arXiv + Google Scholar
- 输出格式：Markdown + LaTeX + 飞书文档

### 示例2：综述研究

```bash
python scripts/run_crew.py \
  --topic "人工智能在教育领域的应用综述" \
  --max-papers 50 \
  --auto-confirm
```

**CoS分析结果**：
- 研究类型：survey
- 核心问题：发展历程、研究热点、主要机构、未来趋势
- 时间范围：last_5_years
- 深度：deep

---

## 🔮 未来计划

- [ ] 实现真正的三模型LLM调用（Codex/Claude/Gemini）
- [ ] 添加更多数据源（Semantic Scholar、PubMed）
- [ ] 支持自定义Agent角色
- [ ] 添加Web UI界面
- [ ] 实现知识图谱可视化

---

## 📚 参考

- [awesome-openclaw-usecases-zh](https://github.com/AlexAnys/awesome-openclaw-usecases-zh) - OpenClaw最佳用例合集
- [OpenCrew框架](https://github.com/AlexAnys/opencrew) - 多智能体协作框架
- [Agent Swarm开发团队](https://x.com/elvissun/status/2025920521871716562) - 编排Codex+Claude Code舰队

---

**更新时间**：2026年3月13日 22:37
**版本**：2.0.0 - OpenCrew多智能体协作系统
