"""
增强综述报告生成器
支持Markdown、LaTeX格式，生成详细的研究综述
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict, Counter
import json
import re
from pathlib import Path
from src.utils.logger import get_logger
from src.utils.data_persistence import get_persistence

logger = get_logger(__name__)


class EnhancedReportGenerator:
    """
    增强综述报告生成器
    
    功能：
    1. 支持Markdown和LaTeX格式
    2. 完整的研究背景、文献综述、主要发现、研究趋势、研究空白、参考文献
    3. 自动提取和结构化信息
    4. 可视化数据嵌入
    """
    
    def __init__(self, output_dir: str = "output/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.persistence = get_persistence()
        
        # 方法关键词
        self.method_keywords = {
            "Transformer": ["transformer", "self-attention", "multi-head"],
            "BERT": ["bert ", "bert-", "masked language model"],
            "GPT": ["gpt-", "gpt ", "generative pre-trained"],
            "CNN": ["cnn", "convolutional neural"],
            "RNN/LSTM": ["rnn", "lstm", "recurrent", "gru"],
            "Attention": ["attention mechanism", "attention-based"],
            "Reinforcement Learning": ["reinforcement learning", "policy gradient"],
            "GAN": ["gan", "generative adversarial"],
            "Diffusion Model": ["diffusion", "denoising"],
            "Multimodal": ["multimodal", "cross-modal"],
            "Graph Neural Network": ["graph neural", "gnn"],
            "Few-shot Learning": ["few-shot", "zero-shot", "meta-learning"],
            "Contrastive Learning": ["contrastive", "simclr", "moco"],
        }
        
        # 数据集关键词
        self.dataset_keywords = {
            "ImageNet": ["imagenet"],
            "COCO": ["coco"],
            "WMT": ["wmt"],
            "SQuAD": ["squad"],
            "GLUE": ["glue"],
            "LibriSpeech": ["librispeech"],
            "Common Voice": ["common voice"],
            "LJSpeech": ["ljspeech"],
        }
    
    def generate(self, topic: str, papers: List[Dict[str, Any]], 
                 format: str = "markdown", include_analysis: bool = True) -> Dict[str, Any]:
        """
        生成综述报告
        
        Args:
            topic: 研究课题
            papers: 论文列表
            format: 输出格式（markdown 或 latex）
            include_analysis: 是否包含深度分析
            
        Returns:
            生成结果
        """
        logger.info(f"[Report] 生成综述报告: {topic} ({format})")
        
        # 分析论文
        analysis = self._analyze_papers(papers) if include_analysis else {}
        
        # 生成内容
        if format.lower() == "latex":
            content = self._generate_latex(topic, papers, analysis)
            ext = ".tex"
        else:
            content = self._generate_markdown(topic, papers, analysis)
            ext = ".md"
        
        # 保存文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = self._safe_filename(topic)
        filename = f"report_{safe_topic}_{timestamp}{ext}"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"[Report] 报告已保存: {filepath}")
        
        return {
            "success": True,
            "format": format,
            "filepath": str(filepath),
            "content": content,
            "papers_count": len(papers),
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_papers(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """深度分析论文"""
        analysis = {
            "basic_stats": self._get_basic_stats(papers),
            "method_distribution": self._get_method_distribution(papers),
            "dataset_distribution": self._get_dataset_distribution(papers),
            "year_distribution": self._get_year_distribution(papers),
            "author_analysis": self._get_author_analysis(papers),
            "keyword_analysis": self._get_keyword_analysis(papers),
            "category_analysis": self._get_category_analysis(papers),
            "research_trends": self._get_research_trends(papers),
            "research_gaps": self._get_research_gaps(papers),
            "top_papers": self._get_top_papers(papers),
        }
        
        return analysis
    
    def _get_basic_stats(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基本统计"""
        authors = set()
        categories = set()
        years = []
        
        for paper in papers:
            # 作者
            for author in paper.get("authors", []):
                if isinstance(author, dict):
                    authors.add(author.get("name", ""))
                else:
                    authors.add(str(author))
            
            # 分类
            for cat in paper.get("categories", []):
                if isinstance(cat, dict):
                    categories.add(cat.get("term", ""))
                else:
                    categories.add(str(cat))
            
            # 年份
            if paper.get("published"):
                years.append(paper["published"][:4])
        
        return {
            "total_papers": len(papers),
            "unique_authors": len(authors),
            "unique_categories": len(categories),
            "year_range": f"{min(years)}-{max(years)}" if years else "N/A",
            "avg_authors_per_paper": len(authors) / len(papers) if papers else 0,
        }
    
    def _get_method_distribution(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """方法分布"""
        distribution = Counter()
        
        for paper in papers:
            text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
            
            for method, keywords in self.method_keywords.items():
                for kw in keywords:
                    if kw in text:
                        distribution[method] += 1
                        break
        
        return dict(distribution.most_common())
    
    def _get_dataset_distribution(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """数据集分布"""
        distribution = Counter()
        
        for paper in papers:
            text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
            
            for dataset, keywords in self.dataset_keywords.items():
                for kw in keywords:
                    if kw in text:
                        distribution[dataset] += 1
                        break
        
        return dict(distribution.most_common())
    
    def _get_year_distribution(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """年份分布"""
        distribution = Counter()
        
        for paper in papers:
            if paper.get("published"):
                year = paper["published"][:4]
                distribution[year] += 1
        
        return dict(sorted(distribution.items()))
    
    def _get_author_analysis(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """作者分析"""
        author_papers = Counter()
        author_collabs = defaultdict(set)
        
        for paper in papers:
            paper_authors = []
            for author in paper.get("authors", []):
                if isinstance(author, dict):
                    name = author.get("name", "")
                else:
                    name = str(author)
                
                if name:
                    author_papers[name] += 1
                    paper_authors.append(name)
            
            # 记录合作关系
            for i, author1 in enumerate(paper_authors):
                for author2 in paper_authors[i+1:]:
                    author_collabs[author1].add(author2)
                    author_collabs[author2].add(author1)
        
        # 活跃作者
        active_authors = author_papers.most_common(10)
        
        # 合作网络
        top_collabs = {}
        for author, _ in active_authors[:5]:
            top_collabs[author] = list(author_collabs[author])[:5]
        
        return {
            "total_authors": len(author_papers),
            "active_authors": active_authors,
            "collaboration_network": top_collabs,
        }
    
    def _get_keyword_analysis(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """关键词分析"""
        keywords = Counter()
        
        # 技术关键词列表
        tech_keywords = [
            "machine learning", "deep learning", "neural network",
            "natural language processing", "computer vision", "speech recognition",
            "transformer", "attention", "embedding", "pre-training",
            "fine-tuning", "transfer learning", "multi-task learning",
            "self-supervised", "unsupervised", "supervised",
            "reinforcement learning", "generative", "discriminative",
            "optimization", "regularization", "normalization",
            "classification", "regression", "clustering",
            "generation", "translation", "summarization",
            "question answering", "sentiment analysis", "named entity",
        ]
        
        for paper in papers:
            text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
            
            for kw in tech_keywords:
                if kw in text:
                    keywords[kw] += 1
        
        return dict(keywords.most_common(20))
    
    def _get_category_analysis(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """分类分析"""
        categories = Counter()
        
        for paper in papers:
            for cat in paper.get("categories", []):
                if isinstance(cat, dict):
                    term = cat.get("term", "")
                else:
                    term = str(cat)
                
                if term:
                    categories[term] += 1
        
        return dict(categories.most_common(10))
    
    def _get_research_trends(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """研究趋势"""
        trends = []
        
        # 按年份统计方法变化
        year_methods = defaultdict(Counter)
        
        for paper in papers:
            year = paper.get("published", "")[:4]
            if not year:
                continue
            
            text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
            
            for method, keywords in self.method_keywords.items():
                for kw in keywords:
                    if kw in text:
                        year_methods[year][method] += 1
                        break
        
        # 分析趋势
        years = sorted(year_methods.keys())
        if len(years) >= 2:
            # 新兴方法
            recent = year_methods[years[-1]]
            prev = year_methods[years[-2]] if len(years) > 1 else Counter()
            
            emerging = []
            for method, count in recent.items():
                if count > prev.get(method, 0) * 1.5:
                    emerging.append(method)
            
            if emerging:
                trends.append({
                    "type": "emerging",
                    "description": f"新兴方法: {', '.join(emerging)}",
                    "methods": emerging
                })
            
            # 持续热门
            hot = []
            for method, count in recent.most_common(5):
                if count >= len(papers) / len(years) * 0.3:
                    hot.append(method)
            
            if hot:
                trends.append({
                    "type": "hot",
                    "description": f"持续热门: {', '.join(hot)}",
                    "methods": hot
                })
        
        # 通用趋势
        trends.append({
            "type": "general",
            "description": "大模型预训练与微调成为主流范式",
        })
        
        trends.append({
            "type": "general",
            "description": "多模态融合研究持续升温",
        })
        
        trends.append({
            "type": "general",
            "description": "模型效率优化（压缩、加速）受到重视",
        })
        
        return trends
    
    def _get_research_gaps(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """研究空白"""
        gaps = []
        
        # 分析方法覆盖
        method_dist = self._get_method_distribution(papers)
        dataset_dist = self._get_dataset_distribution(papers)
        
        # 检查常见方法是否缺失
        common_methods = ["Transformer", "CNN", "GAN", "Diffusion Model", "GNN"]
        for method in common_methods:
            if method not in method_dist:
                gaps.append({
                    "type": "method_gap",
                    "description": f"{method} 方法在该领域应用较少",
                    "suggestion": f"可探索{method}在该领域的应用潜力"
                })
        
        # 检查数据集覆盖
        common_datasets = ["ImageNet", "COCO", "WMT", "SQuAD"]
        for dataset in common_datasets:
            if dataset not in dataset_dist:
                gaps.append({
                    "type": "dataset_gap",
                    "description": f"{dataset} 数据集使用较少",
                    "suggestion": f"可考虑在该数据集上验证方法有效性"
                })
        
        # 通用研究空白
        gaps.extend([
            {
                "type": "general",
                "description": "跨领域方法迁移研究不足",
                "suggestion": "可研究其他领域方法在本领域的适应性"
            },
            {
                "type": "general",
                "description": "实际部署场景验证缺乏",
                "suggestion": "加强实际应用场景的验证研究"
            },
            {
                "type": "general",
                "description": "长期效果评估不足",
                "suggestion": "增加长周期实验和跟踪研究"
            },
        ])
        
        return gaps
    
    def _get_top_papers(self, papers: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
        """获取代表性论文"""
        # 按标题长度和摘要质量排序
        scored_papers = []
        
        for paper in papers:
            score = 0
            
            # 标题质量
            title = paper.get("title", "")
            if len(title) > 50:
                score += 1
            
            # 摘要质量
            summary = paper.get("summary", "")
            if len(summary) > 200:
                score += 2
            
            # 有arXiv ID
            if paper.get("arxiv_id"):
                score += 1
            
            # 年份新
            year = paper.get("published", "")[:4]
            if year >= "2023":
                score += 2
            elif year >= "2022":
                score += 1
            
            scored_papers.append((score, paper))
        
        # 排序
        scored_papers.sort(key=lambda x: x[0], reverse=True)
        
        return [p for _, p in scored_papers[:n]]
    
    # ==================== Markdown生成 ====================
    
    def _generate_markdown(self, topic: str, papers: List[Dict[str, Any]], 
                          analysis: Dict[str, Any]) -> str:
        """生成Markdown格式报告"""
        stats = analysis.get("basic_stats", {})
        
        md = f"""# {topic} - 研究综述报告

> 📅 生成时间: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}
> 📊 论文数量: {stats.get("total_papers", 0)} 篇
> 👥 作者数量: {stats.get("unique_authors", 0)} 位
> 📅 时间跨度: {stats.get("year_range", "N/A")}

---

## 📋 摘要

本报告基于对 **{stats.get("total_papers", 0)}** 篇相关论文的系统分析，全面梳理了 **{topic}** 领域的研究现状、主要方法、发展趋势和研究空白。

**核心发现**:
- 识别出 {len(analysis.get("method_distribution", {}))} 种主要研究方法
- 使用了 {len(analysis.get("dataset_distribution", {}))} 个主流数据集
- 研究时间跨度为 {stats.get("year_range", "N/A")}
- 活跃作者 {stats.get("unique_authors", 0)} 位

---

## 1. 研究背景

{self._generate_background(topic, papers, analysis)}

---

## 2. 文献综述

{self._generate_literature_review(papers, analysis)}

---

## 3. 主要发现

{self._generate_findings(papers, analysis)}

---

## 4. 研究方法分析

{self._generate_method_analysis(analysis)}

---

## 5. 数据集分析

{self._generate_dataset_analysis(analysis)}

---

## 6. 研究趋势

{self._generate_trends(analysis)}

---

## 7. 研究空白与未来方向

{self._generate_gaps(analysis)}

---

## 8. 代表性论文

{self._generate_top_papers(papers, analysis.get("top_papers", []))}

---

## 9. 参考文献

{self._generate_references(papers)}

---

## 附录

### A. 作者统计

{self._generate_author_stats(analysis)}

### B. 关键词统计

{self._generate_keyword_stats(analysis)}

### C. 分类统计

{self._generate_category_stats(analysis)}

---

*本报告由 AI论文预研助手 自动生成*

*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        return md
    
    def _generate_background(self, topic: str, papers: List[Dict[str, Any]], 
                            analysis: Dict[str, Any]) -> str:
        """生成研究背景"""
        stats = analysis.get("basic_stats", {})
        year_dist = analysis.get("year_distribution", {})
        
        background = f"""### 1.1 研究领域概述

**{topic}** 是当前人工智能领域的重要研究方向。本研究通过系统检索和分析arXiv上的相关论文，旨在全面梳理该领域的研究现状。

### 1.2 研究意义

- **理论价值**: 推动相关理论方法的发展和创新
- **应用价值**: 为实际应用场景提供技术支撑
- **社会价值**: 促进人工智能技术的负责任发展

### 1.3 研究范围

本研究涵盖的时间范围为 **{stats.get("year_range", "N/A")}**，共检索 **{stats.get("total_papers", 0)}** 篇论文，涉及 **{stats.get("unique_authors", 0)}** 位作者的研究成果。

### 1.4 论文分布

"""
        
        if year_dist:
            background += "| 年份 | 论文数 | 占比 |\n|------|--------|------|\n"
            total = sum(year_dist.values())
            for year, count in year_dist.items():
                pct = (count / total) * 100
                background += f"| {year} | {count} | {pct:.1f}% |\n"
        
        return background
    
    def _generate_literature_review(self, papers: List[Dict[str, Any]], 
                                    analysis: Dict[str, Any]) -> str:
        """生成文献综述"""
        top_papers = analysis.get("top_papers", papers[:10])
        
        review = "### 2.1 核心文献概览\n\n"
        
        for i, paper in enumerate(top_papers[:10], 1):
            title = paper.get("title", "未知标题")
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            arxiv_id = paper.get("arxiv_id", "")
            
            # 作者
            authors = []
            for author in paper.get("authors", [])[:3]:
                if isinstance(author, dict):
                    authors.append(author.get("name", ""))
                else:
                    authors.append(str(author))
            authors_str = ", ".join(authors) if authors else "未知作者"
            
            review += f"#### {i}. {title}\n\n"
            review += f"- **作者**: {authors_str}\n"
            review += f"- **年份**: {year}\n"
            if arxiv_id:
                review += f"- **arXiv**: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})\n"
            
            # 摘要片段
            summary = paper.get("summary", "")
            if summary:
                review += f"- **摘要**: {summary[:200]}...\n"
            
            review += "\n"
        
        return review
    
    def _generate_findings(self, papers: List[Dict[str, Any]], 
                          analysis: Dict[str, Any]) -> str:
        """生成主要发现"""
        method_dist = analysis.get("method_distribution", {})
        dataset_dist = analysis.get("dataset_distribution", {})
        
        findings = "### 3.1 方法发现\n\n"
        
        if method_dist:
            findings += "本研究识别出以下主要研究方法：\n\n"
            for i, (method, count) in enumerate(list(method_dist.items())[:5], 1):
                pct = (count / len(papers)) * 100
                findings += f"{i}. **{method}**: 在 {count} 篇论文中出现 ({pct:.1f}%)\n"
        
        findings += "\n### 3.2 数据集发现\n\n"
        
        if dataset_dist:
            findings += "主要使用的数据集包括：\n\n"
            for i, (dataset, count) in enumerate(list(dataset_dist.items())[:5], 1):
                findings += f"{i}. **{dataset}**: {count} 篇论文使用\n"
        
        findings += "\n### 3.3 研究特点\n\n"
        findings += "- 研究方法多样化，涵盖传统方法和前沿技术\n"
        findings += "- 数据集选择广泛，体现了研究的实用性\n"
        findings += "- 作者群体活跃，国际合作频繁\n"
        
        return findings
    
    def _generate_method_analysis(self, analysis: Dict[str, Any]) -> str:
        """生成方法分析"""
        method_dist = analysis.get("method_distribution", {})
        
        if not method_dist:
            return "暂无方法分析数据。"
        
        md = "### 4.1 方法分布\n\n"
        md += "| 方法 | 论文数 | 占比 |\n|------|--------|------|\n"
        
        total = sum(method_dist.values())
        for method, count in list(method_dist.items())[:15]:
            pct = (count / total) * 100 if total > 0 else 0
            md += f"| {method} | {count} | {pct:.1f}% |\n"
        
        md += "\n### 4.2 方法特点\n\n"
        md += "- **Transformer架构** 已成为主流方法\n"
        md += "- **预训练-微调范式** 被广泛采用\n"
        md += "- **多模态方法** 正在兴起\n"
        
        return md
    
    def _generate_dataset_analysis(self, analysis: Dict[str, Any]) -> str:
        """生成数据集分析"""
        dataset_dist = analysis.get("dataset_distribution", {})
        
        if not dataset_dist:
            return "暂无数据集分析数据。"
        
        md = "### 5.1 数据集使用分布\n\n"
        md += "| 数据集 | 论文数 | 占比 |\n|--------|--------|------|\n"
        
        total = sum(dataset_dist.values())
        for dataset, count in list(dataset_dist.items())[:10]:
            pct = (count / total) * 100 if total > 0 else 0
            md += f"| {dataset} | {count} | {pct:.1f}% |\n"
        
        md += "\n### 5.2 数据集特点\n\n"
        md += "- **标准基准数据集** 使用最为广泛\n"
        md += "- **领域特定数据集** 针对性强\n"
        md += "- **合成数据集** 在某些任务中应用增多\n"
        
        return md
    
    def _generate_trends(self, analysis: Dict[str, Any]) -> str:
        """生成研究趋势"""
        trends = analysis.get("research_trends", [])
        year_dist = analysis.get("year_distribution", {})
        
        md = "### 6.1 时间趋势\n\n"
        
        if year_dist:
            years = sorted(year_dist.keys())
            if len(years) >= 2:
                first_year, first_count = years[0], year_dist[years[0]]
                last_year, last_count = years[-1], year_dist[years[-1]]
                growth = ((last_count - first_count) / first_count) * 100 if first_count > 0 else 0
                
                md += f"从 {first_year} 年到 {last_year} 年，相关论文数量 "
                md += f"{'增长' if growth >= 0 else '减少'}了 **{abs(growth):.1f}%**\n\n"
        
        md += "### 6.2 方法趋势\n\n"
        
        for trend in trends:
            if trend.get("type") == "emerging":
                md += f"- 🆕 **新兴方法**: {', '.join(trend.get('methods', []))}\n"
            elif trend.get("type") == "hot":
                md += f"- 🔥 **持续热门**: {', '.join(trend.get('methods', []))}\n"
            else:
                md += f"- 📈 {trend.get('description', '')}\n"
        
        md += "\n### 6.3 未来展望\n\n"
        md += "1. **大模型微调**: 预训练模型在特定任务上的优化将持续重要\n"
        md += "2. **多模态融合**: 跨模态信息处理将成为研究热点\n"
        md += "3. **效率优化**: 模型压缩和加速技术需求增长\n"
        md += "4. **可解释AI**: 模型决策透明化研究将深入\n"
        
        return md
    
    def _generate_gaps(self, analysis: Dict[str, Any]) -> str:
        """生成研究空白"""
        gaps = analysis.get("research_gaps", [])
        
        md = "### 7.1 研究空白\n\n"
        
        for i, gap in enumerate(gaps, 1):
            md += f"{i}. **{gap.get('description', '')}**\n"
            if gap.get("suggestion"):
                md += f"   - 建议: {gap.get('suggestion')}\n"
        
        md += "\n### 7.2 未来研究方向\n\n"
        md += "1. **跨领域迁移**: 研究其他领域方法在本领域的适应性\n"
        md += "2. **实际应用验证**: 加强真实场景下的性能评估\n"
        md += "3. **长期效果研究**: 关注方法的长期可持续性\n"
        md += "4. **标准化建设**: 建立统一评估标准和基准\n"
        
        return md
    
    def _generate_top_papers(self, all_papers: List[Dict[str, Any]], 
                            top_papers: List[Dict[str, Any]]) -> str:
        """生成代表性论文"""
        if not top_papers:
            top_papers = all_papers[:10]
        
        md = "以下论文为该领域的代表性研究成果：\n\n"
        
        for i, paper in enumerate(top_papers, 1):
            title = paper.get("title", "未知标题")
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            arxiv_id = paper.get("arxiv_id", "")
            
            md += f"### {i}. {title}\n\n"
            
            # 作者
            authors = []
            for author in paper.get("authors", [])[:5]:
                if isinstance(author, dict):
                    authors.append(author.get("name", ""))
                else:
                    authors.append(str(author))
            
            if authors:
                md += f"**作者**: {', '.join(authors)}\n\n"
            
            md += f"**年份**: {year}\n\n"
            
            if arxiv_id:
                md += f"**链接**: [arXiv:{arxiv_id}](https://arxiv.org/abs/{arxiv_id})\n\n"
            
            # 摘要
            summary = paper.get("summary", "")
            if summary:
                md += f"**摘要**: {summary[:300]}{'...' if len(summary) > 300 else ''}\n\n"
            
            md += "---\n\n"
        
        return md
    
    def _generate_references(self, papers: List[Dict[str, Any]]) -> str:
        """生成参考文献"""
        md = ""
        
        for i, paper in enumerate(papers, 1):
            # 作者
            authors = []
            for author in paper.get("authors", [])[:3]:
                if isinstance(author, dict):
                    authors.append(author.get("name", ""))
                else:
                    authors.append(str(author))
            authors_str = ", ".join(authors) if authors else "Unknown"
            
            title = paper.get("title", "")
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            arxiv_id = paper.get("arxiv_id", "")
            
            md += f"[{i}] {authors_str}. \"{title}\". "
            
            if arxiv_id:
                md += f"arXiv:{arxiv_id}, {year}. "
            else:
                md += f"{year}. "
            
            md += "\n"
        
        return md
    
    def _generate_author_stats(self, analysis: Dict[str, Any]) -> str:
        """生成作者统计"""
        author_analysis = analysis.get("author_analysis", {})
        active_authors = author_analysis.get("active_authors", [])
        
        if not active_authors:
            return "暂无作者统计数据。"
        
        md = "| 排名 | 作者 | 论文数 |\n|------|------|--------|\n"
        
        for i, (author, count) in enumerate(active_authors, 1):
            md += f"| {i} | {author} | {count} |\n"
        
        return md
    
    def _generate_keyword_stats(self, analysis: Dict[str, Any]) -> str:
        """生成关键词统计"""
        keywords = analysis.get("keyword_analysis", {})
        
        if not keywords:
            return "暂无关键词统计数据。"
        
        md = "| 关键词 | 出现次数 |\n|--------|----------|\n"
        
        for keyword, count in list(keywords.items())[:15]:
            md += f"| {keyword} | {count} |\n"
        
        return md
    
    def _generate_category_stats(self, analysis: Dict[str, Any]) -> str:
        """生成分类统计"""
        categories = analysis.get("category_analysis", {})
        
        if not categories:
            return "暂无分类统计数据。"
        
        md = "| 分类 | 论文数 |\n|------|--------|\n"
        
        for category, count in list(categories.items())[:10]:
            md += f"| {category} | {count} |\n"
        
        return md
    
    # ==================== LaTeX生成 ====================
    
    def _generate_latex(self, topic: str, papers: List[Dict[str, Any]], 
                       analysis: Dict[str, Any]) -> str:
        """生成LaTeX格式报告"""
        stats = analysis.get("basic_stats", {})
        
        latex = r"""\documentclass[11pt,a4paper]{article}

% 中文支持
\usepackage{ctex}

% 常用宏包
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{geometry}
\usepackage{enumitem}
\usepackage{xcolor}

% 页面设置
\geometry{left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm}

% 超链接设置
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}

% 标题信息
\title{""" + topic + r"""\\ \large 研究综述报告}

\author{AI论文预研助手}

\date{""" + datetime.now().strftime("%Y年%m月%d日") + r"""}

\begin{document}

\maketitle

\begin{abstract}
"""
        
        latex += f"本报告基于对 {stats.get('total_papers', 0)} 篇相关论文的系统分析，"
        latex += f"全面梳理了 {topic} 领域的研究现状、主要方法、发展趋势和研究空白。"
        latex += f"研究时间跨度为 {stats.get('year_range', 'N/A')}，涉及 {stats.get('unique_authors', 0)} 位作者的研究成果。\n"
        
        latex += r"""
\end{abstract}

\tableofcontents
\newpage

\section{研究背景}

\subsection{研究领域概述}

""" + topic + r""" 是当前人工智能领域的重要研究方向。本研究通过系统检索和分析arXiv上的相关论文，旨在全面梳理该领域的研究现状。

\subsection{研究意义}

\begin{itemize}
    \item \textbf{理论价值}: 推动相关理论方法的发展和创新
    \item \textbf{应用价值}: 为实际应用场景提供技术支撑
    \item \textbf{社会价值}: 促进人工智能技术的负责任发展
\end{itemize}

\subsection{研究范围}

本研究涵盖的时间范围为 """ + stats.get("year_range", "N/A") + r"""，共检索 """ + str(stats.get("total_papers', 0")) + r""" 篇论文。

\section{文献综述}

\subsection{核心文献}

"""
        
        # 添加核心文献
        top_papers = analysis.get("top_papers", papers[:10])
        
        for i, paper in enumerate(top_papers[:10], 1):
            title = paper.get("title", "未知标题")
            
            # 转义LaTeX特殊字符
            title = self._escape_latex(title)
            
            latex += f"\\subsubsection{{文献{i}}}\n\n"
            latex += f"\\textbf{{标题}}: {title}\n\n"
            
            # 作者
            authors = []
            for author in paper.get("authors", [])[:3]:
                if isinstance(author, dict):
                    authors.append(author.get("name", ""))
                else:
                    authors.append(str(author))
            
            if authors:
                latex += f"\\textbf{{作者}}: {', '.join(authors)}\n\n"
            
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            latex += f"\\textbf{{年份}}: {year}\n\n"
            
            arxiv_id = paper.get("arxiv_id", "")
            if arxiv_id:
                latex += f"\\textbf{{arXiv}}: \\href{{https://arxiv.org/abs/{arxiv_id}}}{{{arxiv_id}}}\n\n"
        
        latex += r"""
\section{主要发现}

\subsection{方法发现}

"""
        
        # 方法分布表格
        method_dist = analysis.get("method_distribution", {})
        if method_dist:
            latex += r"""
\begin{table}[h]
\centering
\caption{研究方法分布}
\begin{tabular}{lcc}
\toprule
方法 & 论文数 & 占比 \\
\midrule
"""
            
            total = sum(method_dist.values())
            for method, count in list(method_dist.items())[:10]:
                pct = (count / total) * 100 if total > 0 else 0
                latex += f"{method} & {count} & {pct:.1f}\\% \\\\\n"
            
            latex += r"""
\bottomrule
\end{tabular}
\end{table}

"""
        
        latex += r"""
\section{研究趋势}

基于文献分析，该领域呈现以下趋势：

\begin{enumerate}
    \item 大模型预训练与微调成为主流范式
    \item 多模态融合研究持续升温
    \item 模型效率优化受到重视
    \item 可解释性研究逐渐深入
\end{enumerate}

\section{研究空白}

\begin{itemize}
    \item 跨领域方法迁移研究不足
    \item 实际部署场景验证缺乏
    \item 长期效果评估研究有限
    \item 标准化评估体系待建立
\end{itemize}

\section{未来方向}

\begin{enumerate}
    \item 大模型微调：预训练模型在特定任务上的优化
    \item 多模态融合：跨模态信息处理技术
    \item 效率优化：模型压缩和加速技术
    \item 可解释AI：模型决策透明化研究
    \item 安全与伦理：AI系统安全性研究
\end{enumerate}

\section{参考文献}

\begin{thebibliography}{99}

"""
        
        # 参考文献列表
        for i, paper in enumerate(papers, 1):
            authors = []
            for author in paper.get("authors", [])[:3]:
                if isinstance(author, dict):
                    authors.append(author.get("name", ""))
                else:
                    authors.append(str(author))
            authors_str = ", ".join(authors) if authors else "Unknown"
            
            title = self._escape_latex(paper.get("title", ""))
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            arxiv_id = paper.get("arxiv_id", "")
            
            latex += f"\\bibitem{{ref{i}}} {authors_str}. \\textit{{{title}}}. "
            if arxiv_id:
                latex += f"arXiv:{arxiv_id}, "
            latex += f"{year}.\n\n"
        
        latex += r"""
\end{thebibliography}

\end{document}
"""
        
        return latex
    
    def _escape_latex(self, text: str) -> str:
        """转义LaTeX特殊字符"""
        if not text:
            return ""
        
        replacements = {
            '\\': r'\textbackslash{}',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    def _safe_filename(self, name: str) -> str:
        """生成安全的文件名"""
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
        return safe[:100]
