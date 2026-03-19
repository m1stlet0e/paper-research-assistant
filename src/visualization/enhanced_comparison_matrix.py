"""
增强论文对比矩阵模块
多维度对比分析，生成交互式HTML表格
"""

from typing import Dict, Any, List, Optional
import json
from collections import defaultdict
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedComparisonMatrix:
    """
    增强版论文对比矩阵
    
    功能：
    1. 多维度对比（方法、数据集、创新点、局限性、性能）
    2. 自动提取关键信息
    3. 统计分析
    4. 交互式HTML导出
    """
    
    def __init__(self):
        self.dimensions = [
            "方法", "数据集", "主要贡献", "创新点", "局限性", "性能指标"
        ]
        
        # 方法关键词映射
        self.method_patterns = {
            "Transformer": ["transformer", "self-attention"],
            "BERT": ["bert"],
            "GPT": ["gpt-", "gpt "],
            "CNN": ["cnn", "convolutional"],
            "RNN/LSTM": ["rnn", "lstm", "gru"],
            "Attention": ["attention mechanism"],
            "RL": ["reinforcement learning", "policy gradient"],
            "GAN": ["gan", "adversarial"],
            "Diffusion": ["diffusion model"],
            "Multimodal": ["multimodal", "cross-modal"],
            "Contrastive": ["contrastive learning"],
            "Few-shot": ["few-shot", "zero-shot"],
            "Knowledge Distillation": ["distill"],
        }
        
        # 数据集关键词映射
        self.dataset_patterns = {
            "ImageNet": ["imagenet"],
            "COCO": ["coco"],
            "WMT": ["wmt"],
            "SQuAD": ["squad"],
            "GLUE": ["glue"],
            "LibriSpeech": ["librispeech"],
            "Common Voice": ["common voice"],
            "PASCAL VOC": ["pascal voc"],
            "Cityscapes": ["cityscapes"],
            "LJSpeech": ["ljspeech"],
        }
        
        # 创新点关键词
        self.innovation_patterns = {
            "新颖方法": ["novel", "new method", "new approach"],
            "首次研究": ["first", "first time", "pioneering"],
            "性能提升": ["improve", "improvement", "better performance"],
            "超越SOTA": ["outperform", "state-of-the-art", "sota", "best result"],
            "高效实现": ["efficient", "faster", "lightweight"],
            "新架构": ["new architecture", "novel architecture"],
            "新数据集": ["new dataset", "novel dataset"],
        }
        
        # 局限性关键词
        self.limitation_patterns = {
            "计算成本高": ["computational cost", "expensive", "resource-intensive"],
            "数据依赖": ["data-dependent", "require large data"],
            "泛化问题": ["generalization", "domain adaptation"],
            "可解释性": ["interpretability", "explainability"],
            "未来工作": ["future work", "future research"],
        }
    
    def generate_matrix(self, papers: List[Dict[str, Any]], max_papers: int = 15) -> Dict[str, Any]:
        """
        生成对比矩阵
        
        Args:
            papers: 论文列表
            max_papers: 最大论文数
            
        Returns:
            矩阵数据
        """
        logger.info(f"[ComparisonMatrix] 生成 {min(len(papers), max_papers)} 篇论文的对比矩阵")
        
        rows = []
        
        for i, paper in enumerate(papers[:max_papers]):
            row = self._extract_paper_dimensions(paper, i + 1)
            rows.append(row)
        
        # 统计分析
        statistics = self._calculate_statistics(rows)
        
        # 生成矩阵
        matrix = {
            "headers": ["序号", "论文标题", "年份", "作者", "方法", "数据集", "主要贡献", "创新点", "局限性"],
            "rows": rows,
            "statistics": statistics
        }
        
        return matrix
    
    def _extract_paper_dimensions(self, paper: Dict[str, Any], index: int) -> Dict[str, Any]:
        """提取论文各维度信息"""
        title = paper.get("title", "未知标题")
        year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
        
        # 提取作者
        authors = []
        for author in paper.get("authors", [])[:3]:
            if isinstance(author, dict):
                authors.append(author.get("name", ""))
            elif isinstance(author, str):
                authors.append(author)
        authors_str = ", ".join(authors) if authors else "N/A"
        
        # 提取方法
        methods = self._extract_methods(paper)
        
        # 提取数据集
        datasets = self._extract_datasets(paper)
        
        # 提取贡献
        contribution = self._extract_contribution(paper)
        
        # 提取创新点
        innovations = self._extract_innovations(paper)
        
        # 提取局限性
        limitations = self._extract_limitations(paper)
        
        return {
            "index": index,
            "title": title,
            "year": year,
            "authors": authors_str,
            "methods": methods,
            "datasets": datasets,
            "contribution": contribution,
            "innovations": innovations,
            "limitations": limitations,
            "arxiv_id": paper.get("arxiv_id", ""),
            "pdf_url": paper.get("pdf_url", "")
        }
    
    def _extract_methods(self, paper: Dict[str, Any]) -> List[str]:
        """提取研究方法"""
        text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
        
        methods = []
        for method, patterns in self.method_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    methods.append(method)
                    break
        
        return methods[:4] if methods else ["未明确"]
    
    def _extract_datasets(self, paper: Dict[str, Any]) -> List[str]:
        """提取数据集"""
        text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
        
        datasets = []
        for dataset, patterns in self.dataset_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    datasets.append(dataset)
                    break
        
        return datasets[:3] if datasets else ["未明确"]
    
    def _extract_contribution(self, paper: Dict[str, Any]) -> str:
        """提取主要贡献"""
        summary = paper.get("summary", "")
        
        if summary:
            # 取摘要前150字符
            return summary[:120] + "..." if len(summary) > 120 else summary
        
        return "未提供摘要"
    
    def _extract_innovations(self, paper: Dict[str, Any]) -> List[str]:
        """提取创新点"""
        text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
        
        innovations = []
        for innovation, patterns in self.innovation_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    innovations.append(innovation)
                    break
        
        return innovations[:3] if innovations else ["通用研究"]
    
    def _extract_limitations(self, paper: Dict[str, Any]) -> List[str]:
        """提取局限性"""
        text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
        
        limitations = []
        for limitation, patterns in self.limitation_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    limitations.append(limitation)
                    break
        
        return limitations[:2] if limitations else ["未明确"]
    
    def _calculate_statistics(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算统计信息"""
        # 方法分布
        method_dist = defaultdict(int)
        for row in rows:
            for method in row["methods"]:
                if method != "未明确":
                    method_dist[method] += 1
        
        # 数据集分布
        dataset_dist = defaultdict(int)
        for row in rows:
            for dataset in row["datasets"]:
                if dataset != "未明确":
                    dataset_dist[dataset] += 1
        
        # 年份分布
        year_dist = defaultdict(int)
        for row in rows:
            year = row["year"]
            if year != "N/A":
                year_dist[year] += 1
        
        # 创新点分布
        innovation_dist = defaultdict(int)
        for row in rows:
            for inn in row["innovations"]:
                if inn != "通用研究":
                    innovation_dist[inn] += 1
        
        return {
            "total_papers": len(rows),
            "method_distribution": dict(sorted(method_dist.items(), key=lambda x: x[1], reverse=True)),
            "dataset_distribution": dict(sorted(dataset_dist.items(), key=lambda x: x[1], reverse=True)),
            "year_distribution": dict(sorted(year_dist.items())),
            "innovation_distribution": dict(sorted(innovation_dist.items(), key=lambda x: x[1], reverse=True))
        }
    
    def export_to_html(self, matrix: Dict[str, Any], output_path: str = "comparison_matrix_enhanced.html") -> str:
        """导出为交互式HTML"""
        
        stats = matrix["statistics"]
        rows = matrix["rows"]
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>论文对比矩阵</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}
        
        .header {{
            background: rgba(255,255,255,0.05);
            padding: 1.5rem 2rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .header h1 {{
            font-size: 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .stat-card h3 {{
            font-size: 0.85rem;
            color: #a0a0a0;
            margin-bottom: 0.5rem;
        }}
        
        .stat-card .value {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .table-container {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        td {{
            padding: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            vertical-align: top;
        }}
        
        tr:hover {{
            background: rgba(102, 126, 234, 0.1);
        }}
        
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin: 2px;
        }}
        
        .tag-method {{
            background: rgba(91, 204, 117, 0.2);
            color: #91CC75;
        }}
        
        .tag-dataset {{
            background: rgba(250, 200, 88, 0.2);
            color: #FAC858;
        }}
        
        .tag-innovation {{
            background: rgba(145, 84, 162, 0.2);
            color: #EE6666;
        }}
        
        .tag-limitation {{
            background: rgba(84, 112, 198, 0.2);
            color: #5470C6;
        }}
        
        .paper-title {{
            color: #667eea;
            font-weight: 500;
            max-width: 300px;
        }}
        
        .contribution {{
            max-width: 250px;
            font-size: 0.85rem;
            color: #a0a0a0;
            line-height: 1.4;
        }}
        
        .chart-section {{
            margin-top: 2rem;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .chart-section h2 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #a0a0a0;
        }}
        
        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .bar-row {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .bar-label {{
            width: 120px;
            font-size: 0.85rem;
        }}
        
        .bar-container {{
            flex: 1;
            height: 24px;
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .bar-fill {{
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            padding-left: 0.5rem;
            font-size: 0.75rem;
            color: white;
            border-radius: 4px;
        }}
        
        .arxiv-link {{
            color: #667eea;
            text-decoration: none;
            font-size: 0.8rem;
        }}
        
        .arxiv-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>📊 论文对比矩阵</h1>
        <p style="color: #a0a0a0; margin-top: 0.5rem;">多维度对比分析 · {stats["total_papers"]} 篇论文</p>
    </header>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📄 论文总数</h3>
                <div class="value">{stats["total_papers"]}</div>
            </div>
            <div class="stat-card">
                <h3>🔬 研究方法</h3>
                <div class="value">{len(stats["method_distribution"])}</div>
            </div>
            <div class="stat-card">
                <h3>📊 数据集</h3>
                <div class="value">{len(stats["dataset_distribution"])}</div>
            </div>
            <div class="stat-card">
                <h3>💡 创新类型</h3>
                <div class="value">{len(stats["innovation_distribution"])}</div>
            </div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 40px;">#</th>
                        <th style="width: 250px;">论文标题</th>
                        <th style="width: 60px;">年份</th>
                        <th style="width: 150px;">方法</th>
                        <th style="width: 120px;">数据集</th>
                        <th style="width: 200px;">主要贡献</th>
                        <th style="width: 120px;">创新点</th>
                        <th style="width: 100px;">局限性</th>
                    </tr>
                </thead>
                <tbody>
'''
        
        for row in rows:
            # 格式化标签
            methods_tags = "".join([f'<span class="tag tag-method">{m}</span>' for m in row["methods"]])
            datasets_tags = "".join([f'<span class="tag tag-dataset">{d}</span>' for d in row["datasets"]])
            innovations_tags = "".join([f'<span class="tag tag-innovation">{i}</span>' for i in row["innovations"]])
            limitations_tags = "".join([f'<span class="tag tag-limitation">{l}</span>' for l in row["limitations"]])
            
            # 链接
            title_cell = row["title"]
            if row.get("arxiv_id"):
                title_cell = f'''<a href="https://arxiv.org/abs/{row["arxiv_id"]}" target="_blank" class="paper-title">{row["title"][:80]}{'...' if len(row['title']) > 80 else ''}</a>'''
            else:
                title_cell = f'<span class="paper-title">{row["title"][:80]}{"..." if len(row["title"]) > 80 else ""}</span>'
            
            html += f'''
                    <tr>
                        <td>{row["index"]}</td>
                        <td>{title_cell}</td>
                        <td>{row["year"]}</td>
                        <td>{methods_tags}</td>
                        <td>{datasets_tags}</td>
                        <td class="contribution">{row["contribution"][:150]}{"..." if len(row["contribution"]) > 150 else ""}</td>
                        <td>{innovations_tags}</td>
                        <td>{limitations_tags}</td>
                    </tr>
'''
        
        html += '''
                </tbody>
            </table>
        </div>
        
        <div class="chart-section">
            <h2>📈 方法分布统计</h2>
            <div class="bar-chart">
'''
        
        max_count = max(stats["method_distribution"].values()) if stats["method_distribution"] else 1
        for method, count in list(stats["method_distribution"].items())[:8]:
            percentage = (count / max_count) * 100
            html += f'''
                <div class="bar-row">
                    <div class="bar-label">{method}</div>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {percentage}%;">
                            {count}篇
                        </div>
                    </div>
                </div>
'''
        
        html += '''
            </div>
        </div>
        
        <div class="chart-section">
            <h2>📊 数据集使用统计</h2>
            <div class="bar-chart">
'''
        
        max_count = max(stats["dataset_distribution"].values()) if stats["dataset_distribution"] else 1
        for dataset, count in list(stats["dataset_distribution"].items())[:8]:
            percentage = (count / max_count) * 100
            html += f'''
                <div class="bar-row">
                    <div class="bar-label">{dataset}</div>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: {percentage}%;">
                            {count}篇
                        </div>
                    </div>
                </div>
'''
        
        html += '''
            </div>
        </div>
    </div>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"[ComparisonMatrix] HTML导出: {output_path}")
        
        return output_path
    
    def export_to_markdown(self, matrix: Dict[str, Any]) -> str:
        """导出为Markdown表格"""
        stats = matrix["statistics"]
        rows = matrix["rows"]
        
        md = f"# 📊 论文对比矩阵\n\n"
        md += f"**论文总数**: {stats['total_papers']}篇\n\n"
        
        # 表格
        md += "| # | 论文标题 | 年份 | 方法 | 数据集 | 创新点 |\n"
        md += "|---|---------|------|------|--------|--------|\n"
        
        for row in rows:
            methods = ", ".join(row["methods"][:2])
            datasets = ", ".join(row["datasets"][:2])
            innovations = ", ".join(row["innovations"][:2])
            
            md += f"| {row['index']} | {row['title'][:50]}... | {row['year']} | {methods} | {datasets} | {innovations} |\n"
        
        return md
