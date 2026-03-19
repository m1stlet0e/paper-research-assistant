# AI论文预研助手 - 优化任务清单

## 任务概览
完成三个高优先级优化任务，提升项目竞争力。

## 任务1：添加Google Scholar支持（2小时）

### 目标
实现Google Scholar文献检索功能，与arXiv并行使用。

### 实现步骤
1. 安装依赖：`pip install scholarly`
2. 创建 `src/agents/google_scholar_searcher.py`
3. 实现搜索接口（与ArxivSearcher相同接口）
4. 在main_agent.py中集成
5. 添加配置选项

### 代码结构
```python
class GoogleScholarSearcher:
    def __init__(self, config):
        self.config = config
        
    def search(self, keywords, date_range="last_3_years"):
        # 使用scholarly库搜索
        # 返回与arXiv相同格式的论文列表
        pass
```

## 任务2：增强引用分析（添加PageRank）（3小时）

### 目标
实现PageRank算法计算论文引用影响力。

### 实现步骤
1. 安装依赖：`pip install networkx`
2. 在 `src/agents/sub_agents.py` 的 CitationAnalyzer 中添加：
   - PageRank计算
   - 引用路径分析
   - 共被引分析
3. 更新报告生成，显示影响力排名

### 代码结构
```python
def calculate_pagerank(self, citation_network):
    import networkx as nx
    G = nx.DiGraph()
    # 构建图并计算PageRank
    return pagerank
```

## 任务3：优化报告格式（添加LaTeX）（2小时）

### 目标
实现LaTeX格式报告输出。

### 实现步骤
1. 创建 `src/generators/latex_generator.py`
2. 实现LaTeX模板
3. 添加编译脚本（pdflatex）
4. 在main_agent.py中添加输出格式选项
5. 测试LaTeX生成

### 代码结构
```python
class LaTeXGenerator:
    def generate(self, topic, papers, review):
        # 生成LaTeX代码
        # 保存.tex文件
        pass
```

## 验收标准
- [ ] Google Scholar能正常搜索并返回结果
- [ ] PageRank计算正确，显示影响力排名
- [ ] LaTeX报告能正常生成并编译
- [ ] 所有功能通过测试

## 注意事项
- 保持代码风格一致
- 添加适当的错误处理
- 更新文档
- 记录修改到memory/2026-03-13.md
