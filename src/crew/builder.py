"""
Builder - 执行者
负责：文献检索、论文解析、综述撰写、报告生成
"""

from typing import Dict, Any, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.logger import get_logger
from src.agents.sub_agents import ArxivSearcher, CitationAnalyzer, ReviewWriter

logger = get_logger(__name__)


class Builder:
    """
    执行者Agent
    
    职责：
    1. 执行文献检索
    2. 解析论文内容
    3. 撰写综述
    4. 生成报告
    
    支持并行处理多个论文
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.papers = []
        self.task_registry = {}  # 任务注册表
        
    def execute_search(self, tech_stack: Dict[str, Any], scope: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行文献检索
        
        Args:
            tech_stack: 技术方案
            scope: 研究范围
            
        Returns:
            检索结果
        """
        logger.info("[Builder] 执行文献检索")
        
        all_papers = []
        sources = tech_stack.get("data_sources", [])
        
        # 并行检索多个数据源
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            for source in sources:
                if source["name"] == "arXiv":
                    searcher = ArxivSearcher({
                        "max_results": source["config"].get("max_results", 50)
                    })
                    future = executor.submit(
                        searcher.search,
                        self.config.get("keywords", []),
                        scope.get("time_range", "last_3_years")
                    )
                    futures[future] = "arXiv"
            
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    papers = future.result()
                    logger.info(f"[Builder] {source_name}检索到 {len(papers)} 篇论文")
                    all_papers.extend(papers)
                except Exception as e:
                    logger.error(f"[Builder] {source_name}检索失败: {e}")
        
        # 去重
        unique_papers = self._deduplicate_papers(all_papers)
        
        # 排序（按日期）
        sorted_papers = sorted(
            unique_papers,
            key=lambda x: x.get("published", ""),
            reverse=True
        )
        
        # 限制数量
        max_papers = scope.get("max_papers", 50)
        self.papers = sorted_papers[:max_papers]
        
        logger.info(f"[Builder] 检索完成，共 {len(self.papers)} 篇论文")
        
        return {
            "total_found": len(all_papers),
            "after_dedup": len(unique_papers),
            "final_count": len(self.papers),
            "papers": self.papers
        }
    
    def _deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重"""
        seen_ids = set()
        unique_papers = []
        
        for paper in papers:
            paper_id = paper.get("arxiv_id") or paper.get("doi") or paper.get("title")
            if paper_id and paper_id not in seen_ids:
                seen_ids.add(paper_id)
                unique_papers.append(paper)
        
        return unique_papers
    
    def parse_papers_parallel(self, papers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        并行解析论文
        
        Args:
            papers: 论文列表（可选，默认使用self.papers）
            
        Returns:
            解析结果
        """
        if papers is None:
            papers = self.papers
        
        logger.info(f"[Builder] 并行解析 {len(papers)} 篇论文")
        
        parsed_papers = []
        
        # 并行解析
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._parse_single_paper, paper): paper
                for paper in papers
            }
            
            for future in as_completed(futures):
                paper = futures[future]
                try:
                    parsed = future.result()
                    parsed_papers.append(parsed)
                except Exception as e:
                    logger.error(f"[Builder] 论文解析失败: {e}")
                    # 保留原始论文数据
                    parsed_papers.append(paper)
        
        self.papers = parsed_papers
        
        return {
            "total_parsed": len(parsed_papers),
            "papers": parsed_papers
        }
    
    def _parse_single_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """解析单篇论文"""
        # 提取关键字段
        parsed = {
            **paper,
            "extracted_fields": {
                "title": paper.get("title", ""),
                "authors": [a.get("name", "") for a in paper.get("authors", [])],
                "abstract": paper.get("summary", ""),
                "keywords": self._extract_keywords(paper.get("summary", "")),
                "published_date": paper.get("published", "")
            }
        }
        
        return parsed
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单实现：提取出现频率高的词
        words = text.lower().split()
        
        # 停用词
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        # 过滤
        filtered = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # 统计频率
        from collections import Counter
        word_counts = Counter(filtered)
        
        # 返回前10个
        return [w for w, _ in word_counts.most_common(10)]
    
    def analyze_citations(self) -> Dict[str, Any]:
        """
        分析引用关系
        
        Returns:
            引用分析结果
        """
        logger.info("[Builder] 分析引用关系")
        
        analyzer = CitationAnalyzer(self.config)
        result = analyzer.analyze_citations(self.papers)
        
        return result
    
    def write_review(self, core_questions: List[str] = None) -> Dict[str, Any]:
        """
        撰写综述
        
        Args:
            core_questions: 核心研究问题
            
        Returns:
            综述内容
        """
        logger.info("[Builder] 撰写综述")
        
        writer = ReviewWriter()
        
        # 生成引用列表
        citations = self._generate_citations()
        
        # 撰写综述
        review = writer.write_review(self.papers, citations)
        
        # 添加核心问题回答
        if core_questions:
            review["core_questions_answers"] = self._answer_core_questions(
                core_questions, 
                self.papers
            )
        
        return review
    
    def _generate_citations(self) -> List[str]:
        """生成引用列表"""
        citations = []
        
        for paper in self.papers[:20]:
            authors = paper.get("extracted_fields", {}).get("authors", ["未知作者"])
            if isinstance(authors, list):
                authors_str = ", ".join(authors[:3])
            else:
                authors_str = str(authors)
            
            title = paper.get("title", "未知标题")
            arxiv_id = paper.get("arxiv_id", "")
            year = paper.get("published", "")[:4] if paper.get("published") else "2024"
            
            citation = f"{authors_str}. ({year}). {title}. arXiv:{arxiv_id}."
            citations.append(citation)
        
        return citations
    
    def _answer_core_questions(self, questions: List[str], papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """回答核心问题"""
        answers = []
        
        for question in questions:
            # 简单实现：从论文中找相关信息
            relevant_papers = []
            for paper in papers[:10]:
                abstract = paper.get("summary", "") or paper.get("extracted_fields", {}).get("abstract", "")
                if abstract:
                    relevant_papers.append({
                        "title": paper.get("title", ""),
                        "relevance": "相关"
                    })
            
            answers.append({
                "question": question,
                "answer": f"基于{len(relevant_papers)}篇论文的分析...",
                "supporting_papers": relevant_papers[:3]
            })
        
        return answers
    
    def generate_report(self, review: Dict[str, Any], output_formats: List[str]) -> Dict[str, Any]:
        """
        生成报告
        
        Args:
            review: 综述内容
            output_formats: 输出格式列表
            
        Returns:
            生成的报告
        """
        logger.info(f"[Builder] 生成报告: {output_formats}")
        
        reports = {}
        
        if "markdown" in output_formats:
            reports["markdown"] = self._generate_markdown(review)
        
        if "latex" in output_formats:
            reports["latex"] = self._generate_latex(review)
        
        return reports
    
    def _generate_markdown(self, review: Dict[str, Any]) -> str:
        """生成Markdown报告"""
        md = f"""# {review.get('title', '研究综述')}

## 摘要

{review.get('abstract', '暂无摘要')}

## 目录

"""
        
        for section in review.get("sections", []):
            md += f"### {section.get('title', '')}\n\n"
            md += f"{section.get('content', '')}\n\n"
        
        md += "## 参考文献\n\n"
        for i, citation in enumerate(review.get("citations", []), 1):
            md += f"[{i}] {citation}\n\n"
        
        return md
    
    def _generate_latex(self, review: Dict[str, Any]) -> str:
        """生成LaTeX报告"""
        latex = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{ctex}

\title{%s}
\author{AI论文预研助手}
\date{\today}

\begin{document}
\maketitle

\section{摘要}
%s

""" % (review.get('title', '研究综述'), review.get('abstract', '暂无摘要'))
        
        for section in review.get("sections", []):
            latex += "\\section{%s}\n%s\n\n" % (
                section.get("title", ""),
                section.get("content", "")
            )
        
        latex += r"""
\section{参考文献}
\begin{thebibliography}{99}
"""
        
        for i, citation in enumerate(review.get("citations", []), 1):
            latex += "\\bibitem{%d} %s\n" % (i, citation)
        
        latex += r"""
\end{thebibliography}
\end{document}
"""
        
        return latex
    
    def update_task_registry(self, task_id: str, status: str, result: Any = None):
        """更新任务注册表"""
        self.task_registry[task_id] = {
            "status": status,
            "result": result,
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"[Builder] 任务 {task_id} 状态更新: {status}")
