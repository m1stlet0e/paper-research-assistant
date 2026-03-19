"""
主Agent：论文预研助手总控
负责整体规划、任务分配、进度跟踪和结果汇总
"""

import time
from typing import List, Dict, Any
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.memory import MemoryManager
from src.generators.report_generator import ReportGenerator
from src.generators.latex_generator import LaTeXGenerator
from src.utils.notifier import Notifier
from src.agents.sub_agents import ArxivSearcher, PDFParser, CitationAnalyzer, ReviewWriter
from src.agents.google_scholar_searcher import HybridSearcher

logger = get_logger(__name__)


class PaperResearchMainAgent:
    """论文预研主Agent"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = MemoryManager(config)
        self.report_generator = ReportGenerator(config)
        self.latex_generator = LaTeXGenerator(config)
        self.notifier = Notifier(config)
        self.papers = []
        self.tasks = []

    def analyze_topic(self, topic: str) -> Dict[str, Any]:
        """分析课题关键词"""
        logger.info(f"分析课题: {topic}")

        # 从课题中提取关键词
        keywords = self._extract_keywords(topic)

        return {
            "topic": topic,
            "keywords": keywords,
            "analysis_time": datetime.now().isoformat()
        }

    def _extract_keywords(self, topic: str) -> List[str]:
        """从课题中提取关键词"""
        # 简单实现：按空格分割
        keywords = topic.split()
        # 过滤掉常见停用词
        stop_words = ['的', '在', '中', '与', '和', '或', '等', '对', '通过']
        keywords = [k for k in keywords if k not in stop_words and len(k) > 1]
        return keywords

    def plan_tasks(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """规划任务"""
        logger.info("规划任务...")

        tasks = [
            {
                "id": "search_arxiv",
                "name": "arXiv文献检索",
                "agent": "ArxivSearcher",
                "status": "pending",
                "priority": 1
            },
            {
                "id": "parse_papers",
                "name": "PDF解析和信息提取",
                "agent": "PDFParser",
                "status": "pending",
                "priority": 2
            },
            {
                "id": "analyze_citations",
                "name": "引用分析",
                "agent": "CitationAnalyzer",
                "status": "pending",
                "priority": 2.5
            },
            {
                "id": "write_review",
                "name": "综述撰写",
                "agent": "ReviewWriter",
                "status": "pending",
                "priority": 3
            },
            {
                "id": "generate_report",
                "name": "报告生成",
                "agent": "Reporter",
                "status": "pending",
                "priority": 4
            }
        ]

        self.tasks = tasks
        self.memory.log("任务规划完成", {"tasks": len(tasks)})

        # 存储分析结果
        self.tasks[0]["analysis_result"] = analysis_result

        return tasks

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个任务"""
        logger.info(f"执行任务: {task['name']}")

        task["status"] = "running"
        start_time = time.time()

        try:
            # 调用对应的Agent
            if task["agent"] == "ArxivSearcher":
                result = self._execute_arxiv_search()
            elif task["agent"] == "PDFParser":
                result = self._execute_pdf_parsing()
            elif task["agent"] == "CitationAnalyzer":
                result = self._execute_citation_analysis()
            elif task["agent"] == "ReviewWriter":
                result = self._execute_review_writing()
            elif task["agent"] == "Reporter":
                result = self._execute_report_generation()
            else:
                raise ValueError(f"未知的Agent: {task['agent']}")

            task["status"] = "completed"
            task["duration"] = time.time() - start_time
            task["result"] = result

            self.memory.log(f"任务完成: {task['name']}", {"duration": task["duration"]})

            return task

        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            logger.error(f"任务失败: {task['name']}, 错误: {e}")
            return task

    def _execute_arxiv_search(self) -> Dict[str, Any]:
        """执行文献检索（arXiv + Google Scholar）"""
        logger.info("执行文献检索...")

        # 获取课题关键词
        keywords = self.tasks[0]["analysis_result"]["keywords"]

        # 获取数据源配置
        sources = self.config.get('data_sources', ['arxiv', 'google_scholar'])

        # 创建混合搜索器
        hybrid_searcher = HybridSearcher(self.config)

        # 执行混合检索
        papers = hybrid_searcher.search(keywords, date_range="last_3_years", sources=sources)

        self.papers.extend(papers)

        logger.info(f"找到 {len(papers)} 篇arXiv论文")

        return {
            "total_found": len(papers),
            "papers": papers
        }

    def _execute_citation_analysis(self) -> Dict[str, Any]:
        """执行引用分析"""
        logger.info("执行引用分析...")

        # 创建CitationAnalyzer子Agent
        citation_analyzer = CitationAnalyzer(self.config)

        # 执行分析
        analysis_result = citation_analyzer.analyze_citations(self.papers)

        logger.info(f"引用分析完成")

        return {
            "analysis_result": analysis_result,
            "total_papers": len(self.papers)
        }

    def _execute_pdf_parsing(self) -> Dict[str, Any]:
        """执行PDF解析"""
        logger.info("执行PDF解析...")

        # 创建PDFParser子Agent
        pdf_parser = PDFParser(self.config)

        # 执行解析
        parsed_papers = pdf_parser.parse_papers(self.papers)

        return {
            "total_parsed": len(parsed_papers),
            "parsed_papers": parsed_papers
        }

    def _execute_review_writing(self) -> Dict[str, Any]:
        """执行综述撰写"""
        logger.info("执行综述撰写...")

        # 创建ReviewWriter实例
        review_writer = ReviewWriter()

        # 生成引用列表
        citations = []
        for i, paper in enumerate(self.papers[:20], 1):
            title = paper.get("title", "未知标题")
            authors = []
            if "authors" in paper:
                authors = paper["authors"]
            elif "extracted_fields" in paper and "authors" in paper["extracted_fields"]:
                authors = paper["extracted_fields"]["authors"]

            author_names = []
            for author in authors[:3]:
                if isinstance(author, dict):
                    author_names.append(author.get("name", "未知"))
                elif isinstance(author, str):
                    author_names.append(author)

            authors_str = ", ".join(author_names[:3]) if author_names else "未知作者"

            arxiv_id = paper.get("arxiv_id", "")
            citation = f"{authors_str}. ({self._get_year()}). {title}. arXiv:{arxiv_id}."
            citations.append(citation)

        # 撰写综述
        review = review_writer.write_review(self.papers, citations)

        return {
            "review": review,
            "sections_count": len(review["sections"]),
            "citations_count": len(review["citations"])
        }
    
    def _get_year(self) -> int:
        """获取论文年份"""
        if not self.papers:
            return 2024
        published = self.papers[0].get("published", "")
        if published:
            try:
                return int(published[:4])
            except:
                return 2024
        return 2024

    def _execute_report_generation(self) -> Dict[str, Any]:
        """执行报告生成"""
        logger.info("执行报告生成...")

        # 生成完整报告
        topic = self.tasks[0]["analysis_result"]["topic"] if len(self.tasks) > 0 else "未指定课题"
        review = None
        # ReviewWriter任务应该在tasks的后面，找到ReviewWriter任务
        for task in self.tasks:
            if task.get("agent") == "ReviewWriter" and "result" in task and "review" in task["result"]:
                review = task["result"]["review"]
                logger.info(f"找到ReviewWriter结果: {len(review.get('sections', []))}个章节, {len(review.get('citations', []))}条引用")
                break

        report = self.report_generator.generate(
            topic=topic,
            papers=self.papers,
            review=review
        )

        # 保存报告到文件
        import os
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # 保存Markdown报告
        report_path = os.path.join(output_dir, "research_report.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Markdown报告已保存: {report_path}")

        # 生成LaTeX报告
        latex_report = self.latex_generator.generate(
            topic=topic,
            papers=self.papers,
            review=review
        )

        latex_path = os.path.join(output_dir, "research_report.tex")
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write(latex_report)

        logger.info(f"LaTeX报告已保存: {latex_path}")

        return {
            "report": report,
            "report_path": report_path,
            "latex_report": latex_report,
            "latex_path": latex_path,
            "excel_path": os.path.join(output_dir, "papers_comparison.xlsx")
        }

    def run_full_research(self, topic: str) -> Dict[str, Any]:
        """运行完整的研究流程"""
        logger.info(f"开始完整研究流程: {topic}")

        # 1. 分析课题
        analysis_result = self.analyze_topic(topic)

        # 2. 规划任务
        tasks = self.plan_tasks(analysis_result)

        # 3. 执行任务
        results = []
        for task in tasks:
            result = self.execute_task(task)
            results.append(result)

        # 4. 发送通知
        self.notifier.send_completion_notification(
            topic=topic,
            total_papers=len(self.papers),
            duration=sum(t.get("duration", 0) for t in results)
        )

        # 5. 保存记忆
        self.memory.log("完整研究流程完成", {
            "topic": topic,
            "total_papers": len(self.papers),
            "total_duration": sum(t.get("duration", 0) for t in results)
        })

        return {
            "topic": topic,
            "tasks": results,
            "total_papers": len(self.papers),
            "total_duration": sum(t.get("duration", 0) for t in results)
        }
