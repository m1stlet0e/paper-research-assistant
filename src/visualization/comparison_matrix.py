"""
论文对比矩阵模块
生成论文对比表格，支持多维度分析
"""

from typing import Dict, Any, List
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ComparisonMatrix:
    """
    论文对比矩阵
    
    功能：
    1. 多维度对比论文
    2. 提取关键信息
    3. 生成可视化表格
    """
    
    def __init__(self):
        self.dimensions = [
            "方法",
            "数据集",
            "主要贡献",
            "创新点",
            "局限性"
        ]
    
    def generate_matrix(self, papers: List[Dict[str, Any]], max_papers: int = 10) -> Dict[str, Any]:
        """
        生成对比矩阵
        
        Args:
            papers: 论文列表
            max_papers: 最大论文数
            
        Returns:
            矩阵数据
        """
        logger.info(f"[ComparisonMatrix] 生成 {min(len(papers), max_papers)} 篇论文的对比矩阵")
        
        # 提取论文关键信息
        rows = []
        for i, paper in enumerate(papers[:max_papers]):
            row = self._extract_paper_info(paper, i + 1)
            rows.append(row)
        
        # 生成矩阵数据
        matrix = {
            "headers": ["序号", "论文标题", "年份", "方法", "数据集", "主要贡献", "创新点", "局限性"],
            "rows": rows,
            "statistics": self._calculate_statistics(rows)
        }
        
        return matrix
    
    def _extract_paper_info(self, paper: Dict[str, Any], index: int) -> List[str]:
        """提取单篇论文信息"""
        title = paper.get("title", "未知标题")
        year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
        summary = paper.get("summary", "").lower()
        
        # 提取方法
        method = self._extract_method(summary)
        
        # 提取数据集
        dataset = self._extract_dataset(summary)
        
        # 提取主要贡献
        contribution = self._extract_contribution(paper)
        
        # 提取创新点
        innovation = self._extract_innovation(summary)
        
        # 提取局限性
        limitation = self._extract_limitation(summary)
        
        return [
            str(index),
            title[:60] + "..." if len(title) > 60 else title,
            year,
            method,
            dataset,
            contribution,
            innovation,
            limitation
        ]
    
    def _extract_method(self, summary: str) -> str:
        """提取方法"""
        methods = []
        
        if "transformer" in summary:
            methods.append("Transformer")
        if "bert" in summary:
            methods.append("BERT")
        if "gpt" in summary:
            methods.append("GPT")
        if "cnn" in summary or "convolutional" in summary:
            methods.append("CNN")
        if "rnn" in summary or "recurrent" in summary:
            methods.append("RNN")
        if "reinforcement learning" in summary:
            methods.append("RL")
        if "attention" in summary:
            methods.append("Attention")
        if "multimodal" in summary:
            methods.append("Multimodal")
        if "end-to-end" in summary:
            methods.append("End-to-End")
        
        return ", ".join(methods[:3]) if methods else "未明确"
    
    def _extract_dataset(self, summary: str) -> str:
        """提取数据集"""
        datasets = []
        
        if "wmt" in summary:
            datasets.append("WMT")
        if "imagenet" in summary:
            datasets.append("ImageNet")
        if "coco" in summary:
            datasets.append("COCO")
        if "librispeech" in summary:
            datasets.append("LibriSpeech")
        if "common voice" in summary:
            datasets.append("Common Voice")
        if "squad" in summary:
            datasets.append("SQuAD")
        if "glue" in summary:
            datasets.append("GLUE")
        
        return ", ".join(datasets[:3]) if datasets else "未明确"
    
    def _extract_contribution(self, paper: Dict[str, Any]) -> str:
        """提取主要贡献"""
        summary = paper.get("summary", "")
        
        # 简单提取：取摘要的前100字符
        if summary:
            return summary[:80] + "..." if len(summary) > 80 else summary
        
        return "未提供摘要"
    
    def _extract_innovation(self, summary: str) -> str:
        """提取创新点"""
        innovations = []
        
        if "novel" in summary or "new" in summary:
            innovations.append("新颖方法")
        if "first" in summary:
            innovations.append("首次研究")
        if "improve" in summary or "improvement" in summary:
            innovations.append("性能提升")
        if "outperform" in summary:
            innovations.append("超越基线")
        if "state-of-the-art" in summary or "sota" in summary:
            innovations.append("达到SOTA")
        if "efficient" in summary:
            innovations.append("高效实现")
        
        return ", ".join(innovations[:2]) if innovations else "通用研究"
    
    def _extract_limitation(self, summary: str) -> str:
        """提取局限性"""
        limitations = []
        
        if "limitation" in summary:
            limitations.append("存在局限")
        if "future work" in summary:
            limitations.append("需进一步研究")
        if "small" in summary and "dataset" in summary:
            limitations.append("数据集规模小")
        
        return ", ".join(limitations) if limitations else "未明确"
    
    def _calculate_statistics(self, rows: List[List[str]]) -> Dict[str, Any]:
        """计算统计信息"""
        # 统计方法分布
        method_counts = {}
        for row in rows:
            method = row[3]  # 方法列
            if method != "未明确":
                for m in method.split(", "):
                    method_counts[m] = method_counts.get(m, 0) + 1
        
        # 统计年份分布
        year_counts = {}
        for row in rows:
            year = row[2]  # 年份列
            if year != "N/A":
                year_counts[year] = year_counts.get(year, 0) + 1
        
        return {
            "method_distribution": method_counts,
            "year_distribution": year_counts,
            "total_papers": len(rows)
        }
    
    def export_to_html(self, matrix: Dict[str, Any], output_path: str = "comparison_matrix.html") -> str:
        """导出为HTML表格"""
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>论文对比矩阵</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            flex: 1;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
        }}
        .stat-card p {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            color: #4A90E2;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }}
        th {{
            background: #4A90E2;
            color: white;
            padding: 12px;
            text-align: left;
            position: sticky;
            top: 0;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #eee;
            vertical-align: top;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .method-tag {{
            display: inline-block;
            background: #7ED321;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin: 2px;
        }}
        .dataset-tag {{
            display: inline-block;
            background: #F5A623;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin: 2px;
        }}
        .innovation-tag {{
            display: inline-block;
            background: #BD10E0;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin: 2px;
        }}
        .chart {{
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .bar-label {{
            width: 150px;
            font-weight: bold;
        }}
        .bar-fill {{
            background: #4A90E2;
            height: 30px;
            border-radius: 3px;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 论文对比矩阵</h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3>论文总数</h3>
                <p>{matrix["statistics"]["total_papers"]}</p>
            </div>
            <div class="stat-card">
                <h3>主要方法</h3>
                <p>{len(matrix["statistics"]["method_distribution"])}</p>
            </div>
            <div class="stat-card">
                <h3>时间跨度</h3>
                <p>{len(matrix["statistics"]["year_distribution"])} 年</p>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    {''.join([f'<th>{h}</th>' for h in matrix["headers"]])}
                </tr>
            </thead>
            <tbody>
'''
        
        for row in matrix["rows"]:
            html += '<tr>'
            for i, cell in enumerate(row):
                # 为方法、数据集、创新点添加标签样式
                if i == 3:  # 方法列
                    tags = ''.join([f'<span class="method-tag">{m}</span>' for m in cell.split(', ')])
                    html += f'<td>{tags}</td>'
                elif i == 4:  # 数据集列
                    tags = ''.join([f'<span class="dataset-tag">{d}</span>' for d in cell.split(', ')])
                    html += f'<td>{tags}</td>'
                elif i == 6:  # 创新点列
                    tags = ''.join([f'<span class="innovation-tag">{inn}</span>' for inn in cell.split(', ')])
                    html += f'<td>{tags}</td>'
                else:
                    html += f'<td>{cell}</td>'
            html += '</tr>\n'
        
        html += '''
            </tbody>
        </table>
        
        <div class="chart">
            <h2>方法分布</h2>
'''
        
        for method, count in sorted(matrix["statistics"]["method_distribution"].items(), key=lambda x: x[1], reverse=True):
            percentage = count / matrix["statistics"]["total_papers"] * 100
            html += f'''
            <div class="bar">
                <div class="bar-label">{method}</div>
                <div class="bar-fill" style="width: {percentage}%">
                    {count}篇 ({percentage:.1f}%)
                </div>
            </div>
'''
        
        html += '''
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
        md = "# 📊 论文对比矩阵\n\n"
        
        # 统计信息
        md += f"**论文总数**: {matrix['statistics']['total_papers']}\n\n"
        
        # 表格
        md += "| " + " | ".join(matrix["headers"]) + " |\n"
        md += "|" + "|".join(["---"] * len(matrix["headers"])) + "|\n"
        
        for row in matrix["rows"]:
            md += "| " + " | ".join(row) + " |\n"
        
        return md
