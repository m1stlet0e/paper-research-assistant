"""
增强智能问答系统
支持复杂问题类型、多轮对话、引用来源追踪
"""

from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import re
import json
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.data_persistence import get_persistence

logger = get_logger(__name__)


class EnhancedQA:
    """
    增强智能问答系统
    
    功能：
    1. 深度语义理解（方法、数据集、趋势、对比等）
    2. 多轮对话上下文管理
    3. 精确引用来源追踪
    4. 结构化答案生成
    5. 历史记录管理
    """
    
    def __init__(self, papers: List[Dict[str, Any]] = None):
        self.papers = papers or []
        self.persistence = get_persistence()
        
        # 构建索引
        self.index = self._build_index() if papers else {}
        
        # 对话上下文
        self.conversation_history: List[Dict[str, Any]] = []
        self.context_papers: List[int] = []  # 当前上下文相关的论文索引
        
        # 问题类型定义
        self.question_handlers = {
            # 方法类问题
            "method_overview": self._answer_method_overview,
            "method_detail": self._answer_method_detail,
            "method_comparison": self._answer_method_comparison,
            
            # 数据集类问题
            "dataset_overview": self._answer_dataset_overview,
            "dataset_usage": self._answer_dataset_usage,
            
            # 趋势类问题
            "trend_temporal": self._answer_trend_temporal,
            "trend_hotspot": self._answer_trend_hotspot,
            
            # 论文类问题
            "paper_find": self._answer_paper_find,
            "paper_recommend": self._answer_paper_recommend,
            "paper_compare": self._answer_paper_compare,
            
            # 作者类问题
            "author_papers": self._answer_author_papers,
            "author_collaboration": self._answer_author_collaboration,
            
            # 综合类问题
            "summary": self._answer_summary,
            "research_gap": self._answer_research_gap,
            "future_direction": self._answer_future_direction,
            
            # 通用问题
            "general": self._answer_general,
        }
    
    def _build_index(self) -> Dict[str, Any]:
        """构建多维度索引"""
        index = {
            "by_method": defaultdict(list),
            "by_dataset": defaultdict(list),
            "by_year": defaultdict(list),
            "by_author": defaultdict(list),
            "by_keyword": defaultdict(list),
            "by_category": defaultdict(list),
            "full_text": [],
            "embeddings": {}  # 预留嵌入向量存储
        }
        
        for i, paper in enumerate(self.papers):
            title = paper.get("title", "").lower()
            summary = paper.get("summary", "").lower()
            text = title + " " + summary
            
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            
            # 方法索引
            methods = self._extract_methods(text)
            for method in methods:
                index["by_method"][method].append(i)
            
            # 数据集索引
            datasets = self._extract_datasets(text)
            for dataset in datasets:
                index["by_dataset"][dataset].append(i)
            
            # 年份索引
            if year != "N/A":
                index["by_year"][year].append(i)
            
            # 作者索引
            for author in paper.get("authors", []):
                author_name = author.get("name", "") if isinstance(author, dict) else author
                if author_name:
                    index["by_author"][author_name.lower()].append(i)
            
            # 关键词索引
            keywords = self._extract_keywords(text)
            for kw in keywords:
                index["by_keyword"][kw].append(i)
            
            # 分类索引
            for category in paper.get("categories", []):
                cat_term = category.get("term", "") if isinstance(category, dict) else str(category)
                if cat_term:
                    index["by_category"][cat_term].append(i)
            
            # 全文索引
            index["full_text"].append({
                "index": i,
                "title": paper.get("title", ""),
                "summary": paper.get("summary", ""),
                "year": year,
                "arxiv_id": paper.get("arxiv_id", "")
            })
        
        logger.info(f"[QA] 索引构建完成: {len(self.papers)}篇论文, "
                   f"{len(index['by_method'])}种方法, "
                   f"{len(index['by_dataset'])}个数据集, "
                   f"{len(index['by_author'])}位作者")
        
        return index
    
    def _extract_methods(self, text: str) -> List[str]:
        """提取研究方法"""
        methods = []
        
        method_patterns = {
            "Transformer": ["transformer", "self-attention", "multi-head attention"],
            "BERT": ["bert ", "bert-", "bidirectional encoder"],
            "GPT": ["gpt-", "gpt ", "generative pre-trained"],
            "CNN": ["cnn", "convolutional neural", "convolution"],
            "RNN/LSTM": ["rnn", "lstm", "recurrent neural", "gru"],
            "Attention": ["attention mechanism", "attention-based"],
            "Reinforcement Learning": ["reinforcement learning", "rl ", "policy gradient", "q-learning"],
            "GAN": ["gan", "generative adversarial", "adversarial training"],
            "Diffusion Model": ["diffusion model", "denoising diffusion", "score-based"],
            "Multimodal": ["multimodal", "vision-language", "cross-modal", "multi-modal"],
            "Graph Neural Network": ["graph neural", "gnn", "graph attention", "graph convolution"],
            "Few-shot Learning": ["few-shot", "meta-learning", "zero-shot"],
            "Knowledge Distillation": ["distill", "knowledge distillation", "teacher-student"],
            "Contrastive Learning": ["contrastive", "simclr", "moco", "contrastive learning"],
            "VAE": ["variational autoencoder", "vae ", "vae-"],
            "Neural Architecture Search": ["neural architecture search", "nas "],
        }
        
        for method, patterns in method_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    methods.append(method)
                    break
        
        return methods
    
    def _extract_datasets(self, text: str) -> List[str]:
        """提取数据集"""
        datasets = []
        
        dataset_patterns = {
            "ImageNet": ["imagenet", "image classification dataset"],
            "COCO": ["coco", "common objects in context"],
            "WMT": ["wmt", "translation dataset"],
            "SQuAD": ["squad", "stanford question answering"],
            "GLUE": ["glue", "language understanding evaluation"],
            "LibriSpeech": ["librispeech", "speech recognition dataset"],
            "Common Voice": ["common voice", "mozilla common voice"],
            "LJSpeech": ["ljspeech", "tts dataset"],
            "PASCAL VOC": ["pascal voc", "voc dataset"],
            "Cityscapes": ["cityscapes", "semantic segmentation dataset"],
            "OpenWebText": ["openwebtext", "web text dataset"],
            "Wikipedia": ["wikipedia dataset", "wikipedia dump"],
            "BookCorpus": ["bookcorpus", "book dataset"],
            "PubMed": ["pubmed dataset", "pubmed abstract"],
            "arXiv": ["arxiv dataset", "arxiv papers"],
        }
        
        for dataset, patterns in dataset_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    datasets.append(dataset)
                    break
        
        return datasets
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 技术关键词
        tech_keywords = [
            "machine learning", "deep learning", "neural network",
            "artificial intelligence", "natural language processing", "nlp",
            "computer vision", "speech recognition", "text generation",
            "image classification", "object detection", "semantic segmentation",
            "language model", "pre-training", "fine-tuning", "transfer learning",
            "multi-task learning", "self-supervised", "unsupervised learning",
            "supervised learning", "semi-supervised", "active learning",
            "optimization", "regularization", "dropout", "batch normalization",
            "attention", "embedding", "tokenization", "transformer"
        ]
        
        keywords = []
        for kw in tech_keywords:
            if kw in text:
                keywords.append(kw)
        
        return keywords[:20]  # 限制数量
    
    # ==================== 问题分类 ====================
    
    def _classify_question(self, question: str) -> Tuple[str, Dict[str, Any]]:
        """
        分类问题类型
        
        Returns:
            (问题类型, 提取的实体)
        """
        question_lower = question.lower()
        entities = {}
        
        # 方法相关问题
        if any(kw in question_lower for kw in ["方法", "method", "技术", "technique", "怎么做的", "如何实现"]):
            # 检查是否询问特定方法
            methods = self._extract_methods(question_lower)
            if methods:
                entities["methods"] = methods
                return "method_detail", entities
            
            # 检查是否对比方法
            if any(kw in question_lower for kw in ["对比", "比较", "vs", "difference", "compare"]):
                return "method_comparison", entities
            
            return "method_overview", entities
        
        # 数据集相关问题
        if any(kw in question_lower for kw in ["数据集", "dataset", "data", "数据"]):
            datasets = self._extract_datasets(question_lower)
            if datasets:
                entities["datasets"] = datasets
                return "dataset_usage", entities
            return "dataset_overview", entities
        
        # 趋势相关问题
        if any(kw in question_lower for kw in ["趋势", "trend", "发展", "演变", "热点"]):
            if any(kw in question_lower for kw in ["时间", "年份", "year", "temporal"]):
                return "trend_temporal", entities
            return "trend_hotspot", entities
        
        # 论文查找
        if any(kw in question_lower for kw in ["论文", "paper", "文章", "article", "找"]):
            if any(kw in question_lower for kw in ["推荐", "recommend", "建议"]):
                return "paper_recommend", entities
            if any(kw in question_lower for kw in ["对比", "比较", "compare"]):
                return "paper_compare", entities
            return "paper_find", entities
        
        # 作者相关
        if any(kw in question_lower for kw in ["作者", "author", "谁"]):
            # 尝试提取作者名
            author_pattern = r'(?:作者|author)[:\s]+([a-zA-Z\s]+)'
            match = re.search(author_pattern, question_lower)
            if match:
                entities["author"] = match.group(1).strip()
            return "author_papers", entities
        
        # 综合类
        if any(kw in question_lower for kw in ["总结", "summary", "概述", "概览"]):
            return "summary", entities
        
        if any(kw in question_lower for kw in ["空白", "gap", "不足", "缺陷"]):
            return "research_gap", entities
        
        if any(kw in question_lower for kw in ["未来", "future", "方向", "展望"]):
            return "future_direction", entities
        
        return "general", entities
    
    # ==================== 问题处理器 ====================
    
    def _answer_method_overview(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答方法概览问题"""
        method_dist = self.index.get("by_method", {})
        
        if not method_dist:
            return self._create_answer("未找到研究方法信息", [], "method_overview")
        
        # 排序
        sorted_methods = sorted(method_dist.items(), key=lambda x: len(x[1]), reverse=True)
        
        # 构建答案
        answer_parts = [f"## 📊 研究方法分布\n"]
        answer_parts.append(f"共识别出 **{len(sorted_methods)} 种研究方法**：\n")
        
        for i, (method, indices) in enumerate(sorted_methods[:15], 1):
            count = len(indices)
            percentage = (count / len(self.papers)) * 100
            answer_parts.append(f"{i}. **{method}**: {count} 篇论文 ({percentage:.1f}%)")
        
        # 引用来源
        citations = []
        for method, indices in sorted_methods[:5]:
            if indices:
                paper = self.papers[indices[0]]
                citations.append(self._create_citation(paper, method))
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "method_overview"
        )
    
    def _answer_method_detail(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答方法详情问题"""
        methods = entities.get("methods", [])
        
        if not methods:
            return self._create_answer("请指明您想了解的具体方法", [], "method_detail")
        
        target_method = methods[0]
        indices = self.index.get("by_method", {}).get(target_method, [])
        
        if not indices:
            return self._create_answer(f"未找到使用 **{target_method}** 方法的论文", [], "method_detail")
        
        # 构建答案
        answer_parts = [f"## 🔬 {target_method} 方法详情\n"]
        answer_parts.append(f"共有 **{len(indices)} 篇论文**使用了该方法。\n")
        answer_parts.append("### 相关论文：\n")
        
        citations = []
        for i, idx in enumerate(indices[:10], 1):
            paper = self.papers[idx]
            title = paper.get("title", "未知标题")[:80]
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            
            answer_parts.append(f"{i}. **{title}** ({year})")
            citations.append(self._create_citation(paper, target_method))
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "method_detail"
        )
    
    def _answer_method_comparison(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答方法对比问题"""
        method_dist = self.index.get("by_method", {})
        
        if len(method_dist) < 2:
            return self._create_answer("方法数量不足，无法进行对比", [], "method_comparison")
        
        sorted_methods = sorted(method_dist.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        
        answer_parts = ["## 📈 方法对比分析\n"]
        answer_parts.append("| 方法 | 论文数 | 占比 | 典型应用 |")
        answer_parts.append("|------|--------|------|----------|")
        
        citations = []
        for method, indices in sorted_methods:
            count = len(indices)
            percentage = (count / len(self.papers)) * 100
            
            # 找典型应用
            typical_app = "通用"
            if indices:
                paper = self.papers[indices[0]]
                summary = paper.get("summary", "").lower()
                if "classification" in summary:
                    typical_app = "分类"
                elif "generation" in summary:
                    typical_app = "生成"
                elif "detection" in summary:
                    typical_app = "检测"
                citations.append(self._create_citation(paper, method))
            
            answer_parts.append(f"| {method} | {count} | {percentage:.1f}% | {typical_app} |")
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "method_comparison"
        )
    
    def _answer_dataset_overview(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答数据集概览问题"""
        dataset_dist = self.index.get("by_dataset", {})
        
        if not dataset_dist:
            return self._create_answer("未找到数据集信息", [], "dataset_overview")
        
        sorted_datasets = sorted(dataset_dist.items(), key=lambda x: len(x[1]), reverse=True)
        
        answer_parts = [f"## 📊 数据集使用分布\n"]
        answer_parts.append(f"共识别出 **{len(sorted_datasets)} 个数据集**：\n")
        
        citations = []
        for i, (dataset, indices) in enumerate(sorted_datasets[:15], 1):
            count = len(indices)
            answer_parts.append(f"{i}. **{dataset}**: {count} 篇论文使用")
            
            if i <= 5 and indices:
                paper = self.papers[indices[0]]
                citations.append(self._create_citation(paper, dataset))
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "dataset_overview"
        )
    
    def _answer_dataset_usage(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答数据集使用问题"""
        datasets = entities.get("datasets", [])
        
        if not datasets:
            return self._create_answer("请指明您想了解的具体数据集", [], "dataset_usage")
        
        target_dataset = datasets[0]
        indices = self.index.get("by_dataset", {}).get(target_dataset, [])
        
        if not indices:
            return self._create_answer(f"未找到使用 **{target_dataset}** 数据集的论文", [], "dataset_usage")
        
        answer_parts = [f"## 📊 {target_dataset} 数据集使用情况\n"]
        answer_parts.append(f"共有 **{len(indices)} 篇论文**使用了该数据集。\n")
        answer_parts.append("### 相关论文：\n")
        
        citations = []
        for i, idx in enumerate(indices[:10], 1):
            paper = self.papers[idx]
            title = paper.get("title", "未知标题")[:80]
            answer_parts.append(f"{i}. **{title}**")
            citations.append(self._create_citation(paper, target_dataset))
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "dataset_usage"
        )
    
    def _answer_trend_temporal(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答时间趋势问题"""
        year_dist = self.index.get("by_year", {})
        
        if not year_dist:
            return self._create_answer("未找到时间分布信息", [], "trend_temporal")
        
        sorted_years = sorted(year_dist.items())
        
        answer_parts = ["## 📈 时间趋势分析\n"]
        answer_parts.append("| 年份 | 论文数 | 增长率 |")
        answer_parts.append("|------|--------|--------|")
        
        prev_count = 0
        for year, indices in sorted_years:
            count = len(indices)
            growth = ""
            if prev_count > 0:
                growth_rate = ((count - prev_count) / prev_count) * 100
                growth = f"{'+' if growth_rate >= 0 else ''}{growth_rate:.1f}%"
            answer_parts.append(f"| {year} | {count} | {growth} |")
            prev_count = count
        
        # 分析趋势
        if len(sorted_years) >= 2:
            first_year, first_indices = sorted_years[0]
            last_year, last_indices = sorted_years[-1]
            total_growth = len(last_indices) - len(first_indices)
            
            answer_parts.append(f"\n**总体趋势**: 从 {first_year} 年到 {last_year} 年，"
                               f"论文数量{'增长' if total_growth > 0 else '减少'}了 **{abs(total_growth)} 篇**")
        
        return self._create_answer(
            "\n".join(answer_parts),
            [],
            "trend_temporal"
        )
    
    def _answer_trend_hotspot(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答研究热点问题"""
        method_dist = self.index.get("by_method", {})
        keyword_dist = self.index.get("by_keyword", {})
        
        answer_parts = ["## 🔥 研究热点分析\n"]
        
        # 方法热点
        answer_parts.append("### 🔬 热门方法")
        sorted_methods = sorted(method_dist.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        for i, (method, indices) in enumerate(sorted_methods, 1):
            answer_parts.append(f"{i}. **{method}**: {len(indices)} 篇论文")
        
        # 关键词热点
        answer_parts.append("\n### 📌 热门关键词")
        sorted_keywords = sorted(keyword_dist.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for i, (kw, indices) in enumerate(sorted_keywords, 1):
            answer_parts.append(f"{i}. **{kw}**: {len(indices)} 次")
        
        return self._create_answer(
            "\n".join(answer_parts),
            [],
            "trend_hotspot"
        )
    
    def _answer_paper_find(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答论文查找问题"""
        # 提取搜索关键词
        keywords = re.findall(r'\b[a-zA-Z]{4,}\b', question.lower())
        
        relevant_indices = set()
        for kw in keywords:
            if kw in self.index.get("by_keyword", {}):
                relevant_indices.update(self.index["by_keyword"][kw])
        
        if not relevant_indices:
            return self._create_answer("未找到相关论文，请尝试其他关键词", [], "paper_find")
        
        answer_parts = [f"## 📚 找到 **{len(relevant_indices)} 篇相关论文**\n"]
        
        citations = []
        for i, idx in enumerate(sorted(relevant_indices)[:15], 1):
            paper = self.papers[idx]
            title = paper.get("title", "未知标题")[:80]
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            arxiv_id = paper.get("arxiv_id", "")
            
            answer_parts.append(f"{i}. **{title}** ({year})")
            if arxiv_id:
                answer_parts.append(f"   - arXiv: [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})")
            
            citations.append(self._create_citation(paper, "相关论文"))
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "paper_find"
        )
    
    def _answer_paper_recommend(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答论文推荐问题"""
        # 基于方法、数据集等推荐
        method_dist = self.index.get("by_method", {})
        
        if not method_dist:
            return self._create_answer("暂无足够数据进行推荐", [], "paper_recommend")
        
        # 找出使用最热门方法的论文
        sorted_methods = sorted(method_dist.items(), key=lambda x: len(x[1]), reverse=True)[:3]
        
        answer_parts = ["## 🌟 推荐论文\n"]
        answer_parts.append("基于研究热度，推荐以下论文：\n")
        
        citations = []
        recommended = set()
        for method, indices in sorted_methods:
            answer_parts.append(f"\n### {method} 领域")
            for idx in indices[:3]:
                if idx in recommended:
                    continue
                recommended.add(idx)
                
                paper = self.papers[idx]
                title = paper.get("title", "未知标题")[:80]
                answer_parts.append(f"- **{title}**")
                citations.append(self._create_citation(paper, method))
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "paper_recommend"
        )
    
    def _answer_paper_compare(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答论文对比问题"""
        if len(self.papers) < 2:
            return self._create_answer("论文数量不足，无法进行对比", [], "paper_compare")
        
        # 选择前5篇论文进行对比
        papers_to_compare = self.papers[:5]
        
        answer_parts = ["## 📊 论文对比分析\n"]
        answer_parts.append("| 论文 | 年份 | 方法 | 数据集 | 创新点 |")
        answer_parts.append("|------|------|------|--------|--------|")
        
        citations = []
        for paper in papers_to_compare:
            title = paper.get("title", "未知")[:30]
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            
            text = paper.get("title", "") + " " + paper.get("summary", "")
            methods = self._extract_methods(text.lower())[:2]
            datasets = self._extract_datasets(text.lower())[:2]
            
            answer_parts.append(f"| {title}... | {year} | {', '.join(methods) or 'N/A'} | {', '.join(datasets) or 'N/A'} | - |")
            citations.append(self._create_citation(paper, "对比"))
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "paper_compare"
        )
    
    def _answer_author_papers(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答作者论文问题"""
        author_dist = self.index.get("by_author", {})
        
        if not author_dist:
            return self._create_answer("未找到作者信息", [], "author_papers")
        
        sorted_authors = sorted(author_dist.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        
        answer_parts = ["## 👥 活跃作者\n"]
        answer_parts.append("按论文数量排序：\n")
        
        citations = []
        for i, (author, indices) in enumerate(sorted_authors, 1):
            count = len(indices)
            answer_parts.append(f"{i}. **{author.title()}**: {count} 篇论文")
            
            # 列出该作者的论文
            if i <= 5:
                for idx in indices[:2]:
                    paper = self.papers[idx]
                    citations.append(self._create_citation(paper, author))
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "author_papers"
        )
    
    def _answer_author_collaboration(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答作者合作问题"""
        # 简化版：基于共同作者分析
        answer_parts = ["## 🤝 作者合作网络\n"]
        answer_parts.append("该功能需要更多数据支持，暂不提供详细分析。")
        
        return self._create_answer(
            "\n".join(answer_parts),
            [],
            "author_collaboration"
        )
    
    def _answer_summary(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答总结问题"""
        answer_parts = ["## 📋 研究总结\n"]
        
        # 统计信息
        answer_parts.append(f"- **论文总数**: {len(self.papers)} 篇")
        answer_parts.append(f"- **研究方法**: {len(self.index.get('by_method', {}))} 种")
        answer_parts.append(f"- **数据集**: {len(self.index.get('by_dataset', {}))} 个")
        answer_parts.append(f"- **作者**: {len(self.index.get('by_author', {}))} 位")
        
        # 核心论文
        answer_parts.append("\n### 🌟 核心论文")
        citations = []
        for i, paper in enumerate(self.papers[:5], 1):
            title = paper.get("title", "未知标题")[:60]
            answer_parts.append(f"{i}. **{title}**")
            citations.append(self._create_citation(paper, "核心论文"))
        
        # 主要方法
        method_dist = self.index.get("by_method", {})
        if method_dist:
            answer_parts.append("\n### 🔬 主要方法")
            sorted_methods = sorted(method_dist.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            for method, indices in sorted_methods:
                answer_parts.append(f"- **{method}**: {len(indices)} 篇")
        
        return self._create_answer(
            "\n".join(answer_parts),
            citations,
            "summary"
        )
    
    def _answer_research_gap(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答研究空白问题"""
        answer_parts = ["## 🎯 研究空白分析\n"]
        
        # 基于现有数据分析可能的研究空白
        method_dist = self.index.get("by_method", {})
        dataset_dist = self.index.get("by_dataset", {})
        
        # 方法-数据集交叉分析
        answer_parts.append("### 可能的研究空白：\n")
        
        gaps = []
        
        # 检查方法覆盖
        common_methods = ["Transformer", "CNN", "RNN/LSTM", "GAN", "Diffusion Model"]
        for method in common_methods:
            if method not in method_dist:
                gaps.append(f"- **{method}** 方法在该领域应用较少")
        
        # 检查数据集覆盖
        common_datasets = ["ImageNet", "COCO", "WMT", "SQuAD"]
        for dataset in common_datasets:
            if dataset not in dataset_dist:
                gaps.append(f"- **{dataset}** 数据集使用较少")
        
        if gaps:
            answer_parts.extend(gaps)
        else:
            answer_parts.append("- 暂未发现明显的研究空白，建议深入分析特定子领域")
        
        # 建议
        answer_parts.append("\n### 💡 建议研究方向：")
        answer_parts.append("1. 跨领域方法迁移")
        answer_parts.append("2. 新数据集构建")
        answer_parts.append("3. 方法组合创新")
        
        return self._create_answer(
            "\n".join(answer_parts),
            [],
            "research_gap"
        )
    
    def _answer_future_direction(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答未来方向问题"""
        answer_parts = ["## 🔮 未来研究方向\n"]
        
        # 基于当前趋势预测
        year_dist = self.index.get("by_year", {})
        method_dist = self.index.get("by_method", {})
        
        # 最新趋势
        if year_dist:
            latest_year = max(year_dist.keys())
            answer_parts.append(f"### {latest_year} 年研究热点：")
            
            # 找该年的热门方法
            hot_methods = []
            for method, indices in method_dist.items():
                count = sum(1 for i in indices if self.papers[i].get("published", "")[:4] == latest_year)
                if count > 0:
                    hot_methods.append((method, count))
            
            hot_methods.sort(key=lambda x: x[1], reverse=True)
            for method, count in hot_methods[:5]:
                answer_parts.append(f"- **{method}**: {count} 篇")
        
        # 未来方向
        answer_parts.append("\n### 📈 预测未来方向：")
        answer_parts.append("1. **大模型微调**: 针对特定任务的模型优化")
        answer_parts.append("2. **多模态融合**: 跨模态信息整合")
        answer_parts.append("3. **效率优化**: 模型压缩和加速")
        answer_parts.append("4. **可解释性**: 模型决策透明化")
        answer_parts.append("5. **安全与伦理**: AI系统的安全性研究")
        
        return self._create_answer(
            "\n".join(answer_parts),
            [],
            "future_direction"
        )
    
    def _answer_general(self, question: str, entities: Dict) -> Dict[str, Any]:
        """回答一般问题"""
        # 搜索相关论文
        keywords = re.findall(r'\b[a-zA-Z]{4,}\b', question.lower())
        
        relevant_indices = set()
        for kw in keywords:
            if kw in self.index.get("by_keyword", {}):
                relevant_indices.update(self.index["by_keyword"][kw])
        
        if relevant_indices:
            answer_parts = [f"找到 **{len(relevant_indices)} 篇相关论文**：\n"]
            
            citations = []
            for i, idx in enumerate(sorted(relevant_indices)[:10], 1):
                paper = self.papers[idx]
                title = paper.get("title", "未知标题")[:70]
                answer_parts.append(f"{i}. [{title}](https://arxiv.org/abs/{paper.get('arxiv_id', '')})")
                citations.append(self._create_citation(paper, "相关"))
            
            return self._create_answer(
                "\n".join(answer_parts),
                citations,
                "general"
            )
        
        return self._create_answer(
            "抱歉，未找到相关信息。请尝试更具体的问题，例如：\n\n"
            "- 主要的研究方法有哪些？\n"
            "- 哪些论文使用了Transformer？\n"
            "- 研究趋势是什么？",
            [],
            "general"
        )
    
    # ==================== 辅助方法 ====================
    
    def _create_answer(self, content: str, citations: List[Dict], 
                       question_type: str) -> Dict[str, Any]:
        """创建结构化答案"""
        return {
            "answer": content,
            "citations": citations,
            "question_type": question_type,
            "total_papers": len(self.papers),
            "relevant_papers": len(citations),
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_citation(self, paper: Dict[str, Any], context: str) -> Dict[str, Any]:
        """创建引用"""
        authors = []
        for author in paper.get("authors", [])[:3]:
            if isinstance(author, dict):
                authors.append(author.get("name", ""))
            else:
                authors.append(str(author))
        
        return {
            "title": paper.get("title", ""),
            "authors": authors,
            "year": paper.get("published", "")[:4] if paper.get("published") else "N/A",
            "arxiv_id": paper.get("arxiv_id", ""),
            "url": f"https://arxiv.org/abs/{paper.get('arxiv_id', '')}",
            "context": context
        }
    
    # ==================== 公共接口 ====================
    
    def answer(self, question: str) -> Dict[str, Any]:
        """
        回答问题
        
        Args:
            question: 用户问题
            
        Returns:
            答案结果
        """
        logger.info(f"[QA] 问题: {question}")
        
        if not self.papers:
            return self._create_answer(
                "请先运行研究以加载论文数据",
                [],
                "error"
            )
        
        # 分类问题
        question_type, entities = self._classify_question(question)
        
        # 获取处理器
        handler = self.question_handlers.get(question_type, self._answer_general)
        
        # 生成答案
        result = handler(question, entities)
        
        # 记录对话历史
        self.conversation_history.append({
            "question": question,
            "question_type": question_type,
            "answer": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history[-limit:]
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self.conversation_history.clear()
        self.context_papers.clear()
    
    def update_papers(self, papers: List[Dict[str, Any]]) -> None:
        """更新论文数据"""
        self.papers = papers
        self.index = self._build_index()
        self.clear_history()
        logger.info(f"[QA] 更新论文数据: {len(papers)}篇")
