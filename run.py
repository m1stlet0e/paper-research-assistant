#!/usr/bin/env python3
"""
主运行脚本 - AI论文预研助手
整合所有功能模块，提供统一的命令行入口
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.sub_agents import ArxivSearcher, CitationAnalyzer, PDFParser, ReviewWriter
from src.visualization.enhanced_knowledge_graph import EnhancedKnowledgeGraph
from src.visualization.enhanced_comparison_matrix import EnhancedComparisonMatrix
from src.qa.intelligent_qa import IntelligentQA
from src.qa.enhanced_qa import EnhancedQA
from src.feishu.deep_integration import FeishuDeepIntegration
from src.feishu.real_integration import FeishuRealIntegration
from src.utils.logger import get_logger
from src.utils.data_persistence import DataPersistence, get_persistence
from src.generators.report_generator import ReportGenerator
from src.generators.enhanced_report_generator import EnhancedReportGenerator

logger = get_logger(__name__)


class PaperResearchAssistant:
    """AI论文预研助手主类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.output_dir = config.get("output_dir", "output")
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化组件
        self.arxiv_searcher = ArxivSearcher({"max_results": config.get("max_results", 50)})
        self.citation_analyzer = CitationAnalyzer(config)
        self.pdf_parser = PDFParser(config)
        self.review_writer = ReviewWriter()
        
        # 增强模块
        self.knowledge_graph = EnhancedKnowledgeGraph()
        self.comparison_matrix = EnhancedComparisonMatrix()
        self.qa_system = None  # 基础问答
        self.enhanced_qa = None  # 增强问答
        self.feishu = FeishuDeepIntegration()
        self.feishu_real = FeishuRealIntegration()
        
        # 数据持久化
        self.persistence = get_persistence()
        
        # 报告生成器
        self.report_generator = EnhancedReportGenerator(
            output_dir=os.path.join(self.output_dir, "reports")
        )
        
        # 研究结果缓存
        self.current_papers = []
        self.current_analysis = None
        self.current_review = None
        
    def run_research(self, topic: str, max_papers: int = 50, enable_feishu: bool = True) -> Dict[str, Any]:
        """
        运行完整研究流程
        
        Args:
            topic: 研究课题
            max_papers: 最大论文数
            enable_feishu: 是否启用飞书集成
            
        Returns:
            研究结果
        """
        logger.info(f"[Main] 开始研究: {topic}")
        start_time = datetime.now()
        
        results = {
            "topic": topic,
            "started_at": start_time.isoformat(),
            "status": "running",
            "papers": [],
            "analysis": None,
            "review": None,
            "visualizations": {},
            "feishu_docs": {}
        }
        
        try:
            # Phase 1: 检索论文（真实数据）
            logger.info("[Main] Phase 1: 检索论文...")
            keywords = self._extract_keywords(topic)
            self.arxiv_searcher.max_results = max_papers
            papers = self.arxiv_searcher.search(keywords)
            
            if not papers:
                logger.warning("[Main] 未找到论文，尝试扩大搜索范围...")
                # 扩大搜索
                papers = self.arxiv_searcher.search([topic])
            
            self.current_papers = papers
            results["papers"] = papers
            results["papers_count"] = len(papers)
            logger.info(f"[Main] 检索到 {len(papers)} 篇论文")
            
            # Phase 2: 解析论文
            logger.info("[Main] Phase 2: 解析论文...")
            parsed_papers = self.pdf_parser.parse_papers(papers)
            
            # Phase 3: 引用分析
            logger.info("[Main] Phase 3: 引用分析...")
            analysis = self.citation_analyzer.analyze_citations(parsed_papers)
            self.current_analysis = analysis
            results["analysis"] = analysis
            
            # Phase 4: 撰写综述
            logger.info("[Main] Phase 4: 撰写综述...")
            citations = [p.get("arxiv_id", "") for p in parsed_papers if p.get("arxiv_id")]
            review = self.review_writer.write_review(parsed_papers, citations)
            self.current_review = review
            results["review"] = review
            
            # Phase 5: 生成可视化（增强版）
            logger.info("[Main] Phase 5: 生成增强可视化...")
            visualizations = self._generate_enhanced_visualizations(parsed_papers)
            results["visualizations"] = visualizations
            
            # Phase 6: 初始化智能问答
            logger.info("[Main] Phase 6: 初始化智能问答系统...")
            self.qa_system = IntelligentQA(parsed_papers)
            self.enhanced_qa = EnhancedQA(parsed_papers)
            
            # Phase 7: 生成综述报告
            logger.info("[Main] Phase 7: 生成增强综述报告...")
            report_result = self.report_generator.generate(
                topic=topic,
                papers=parsed_papers,
                format="markdown",
                include_analysis=True
            )
            results["report"] = {
                "filepath": report_result.get("filepath"),
                "format": report_result.get("format"),
                "content_length": len(report_result.get("content", ""))
            }
            
            # 同时生成LaTeX格式
            latex_result = self.report_generator.generate(
                topic=topic,
                papers=parsed_papers,
                format="latex",
                include_analysis=True
            )
            results["report_latex"] = {
                "filepath": latex_result.get("filepath"),
                "format": latex_result.get("format")
            }
            
            # Phase 8: 数据持久化
            logger.info("[Main] Phase 8: 保存数据...")
            persistence_path = self.persistence.save_papers(
                papers=parsed_papers,
                topic=topic,
                metadata={
                    "analysis": analysis,
                    "report_path": report_result.get("filepath")
                }
            )
            results["persistence"] = {
                "data_path": persistence_path,
                "statistics": self.persistence.get_statistics()
            }
            
            # Phase 9: 飞书集成
            if enable_feishu:
                logger.info("[Main] Phase 9: 飞书深度集成(完整)...")
                feishu_results = self._integrate_with_feishu(topic, parsed_papers, review, visualizations)
                results["feishu_docs"] = feishu_results
            else:
                logger.info("[Main] Phase 9: 发送飞书通知...")
                self._send_feishu_notification(topic, parsed_papers, review)
            
            # 保存结果
            results["status"] = "completed"
            results["completed_at"] = datetime.now().isoformat()
            results["duration_seconds"] = (datetime.now() - start_time).total_seconds()
            
            # 保存到文件
            self._save_results(results)
            
            logger.info(f"[Main] 研究完成: {len(papers)}篇论文, 耗时{results['duration_seconds']:.1f}秒")
            
        except Exception as e:
            logger.error(f"[Main] 研究失败: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            import traceback
            results["traceback"] = traceback.format_exc()
        
        return results
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """从课题中提取关键词"""
        # 中英文停用词
        stop_words = {
            '的', '在', '中', '与', '和', '或', '等', '对', '通过', '基于', '研究',
            '分析', '应用', '系统', '方法', '技术', '一种', '新型', '智能',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }
        
        import re
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', topic)
        keywords = [w for w in words if w.lower() not in stop_words and len(w) > 1]
        
        return keywords[:5] if keywords else [topic]
    
    def _generate_enhanced_visualizations(self, papers: List[Dict[str, Any]]) -> Dict[str, str]:
        """生成增强可视化"""
        visualizations = {}
        
        try:
            # 1. 增强知识图谱（ECharts）
            logger.info("[Main] 生成增强知识图谱...")
            kg_data = self.knowledge_graph.build_graph(papers)
            kg_path = os.path.join(self.output_dir, "knowledge_graph_enhanced.html")
            self.knowledge_graph.export_to_html(kg_data, kg_path)
            visualizations["knowledge_graph"] = kg_path
            logger.info(f"[Main] 知识图谱: {kg_path}")
        except Exception as e:
            logger.error(f"[Main] 知识图谱生成失败: {e}")
        
        try:
            # 2. 增强对比矩阵
            logger.info("[Main] 生成增强对比矩阵...")
            cm_data = self.comparison_matrix.generate_matrix(papers)
            cm_path = os.path.join(self.output_dir, "comparison_matrix_enhanced.html")
            self.comparison_matrix.export_to_html(cm_data, cm_path)
            visualizations["comparison_matrix"] = cm_path
            logger.info(f"[Main] 对比矩阵: {cm_path}")
        except Exception as e:
            logger.error(f"[Main] 对比矩阵生成失败: {e}")
        
        try:
            # 3. 智能问答演示
            if self.qa_system:
                logger.info("[Main] 生成智能问答演示...")
                demo_questions = [
                    "主要的研究方法有哪些？",
                    "哪些论文使用了Transformer？",
                    "总结一下研究现状"
                ]
                qa_pairs = [self.qa_system.answer(q) for q in demo_questions]
                qa_path = os.path.join(self.output_dir, "qa_demo.html")
                self.qa_system.export_to_html(qa_pairs, qa_path)
                visualizations["qa_demo"] = qa_path
                logger.info(f"[Main] 智能问答: {qa_path}")
        except Exception as e:
            logger.error(f"[Main] 智能问答生成失败: {e}")
        
        return visualizations
    
    def _integrate_with_feishu(self, topic: str, papers: List[Dict[str, Any]], 
                               review: Dict[str, Any], visualizations: Dict[str, str]) -> Dict[str, Any]:
        """飞书深度集成"""
        feishu_results = {}
        
        try:
            # 1. 创建多维表格并导入论文
            logger.info("[Main] 创建飞书多维表格...")
            bitable_result = self.feishu.create_and_populate_bitable(
                name=f"论文研究: {topic[:30]}",
                papers=papers
            )
            feishu_results["bitable"] = bitable_result
            logger.info(f"[Main] 多维表格: {bitable_result.get('app_token', 'N/A')}")
        except Exception as e:
            logger.error(f"[Main] 多维表格创建失败: {e}")
            feishu_results["bitable_error"] = str(e)
        
        try:
            # 2. 创建知识库并归档报告
            logger.info("[Main] 创建飞书知识库...")
            wiki_result = self.feishu.archive_research_to_wiki(
                topic=topic,
                review=review,
                papers=papers,
                visualizations=visualizations
            )
            feishu_results["wiki"] = wiki_result
            logger.info(f"[Main] 知识库: {wiki_result.get('space_id', 'N/A')}")
        except Exception as e:
            logger.error(f"[Main] 知识库创建失败: {e}")
            feishu_results["wiki_error"] = str(e)
        
        try:
            # 3. 发送消息卡片
            logger.info("[Main] 发送飞书消息卡片...")
            card_result = self.feishu.send_research_card(
                topic=topic,
                papers_count=len(papers),
                visualizations=visualizations
            )
            feishu_results["card"] = card_result
            logger.info("[Main] 消息卡片已发送")
        except Exception as e:
            logger.error(f"[Main] 消息卡片发送失败: {e}")
            feishu_results["card_error"] = str(e)
        
        return feishu_results

    def _send_feishu_notification(self, topic: str, papers: List[Dict[str, Any]],
                                  review: Dict[str, Any] = None):
        """只发飞书消息通知，不创建多维表格和知识库（快速，1-2秒）"""
        try:
            self.feishu._send_detailed_report(topic, review, papers)
            logger.info("[Main] 详细报告已发送")
        except Exception as e:
            logger.warning(f"[Main] 详细报告发送失败: {e}")
        try:
            self.feishu.send_research_card(topic=topic, papers_count=len(papers))
            logger.info("[Main] 消息卡片已发送")
        except Exception as e:
            logger.warning(f"[Main] 消息卡片发送失败: {e}")
    
    def _save_results(self, results: Dict[str, Any]):
        """保存研究结果"""
        # 保存完整结果
        results_path = os.path.join(self.output_dir, "research_results.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        # 保存论文列表
        papers_path = os.path.join(self.output_dir, "papers.json")
        with open(papers_path, 'w', encoding='utf-8') as f:
            json.dump(results.get("papers", []), f, ensure_ascii=False, indent=2, default=str)
        
        # 保存综述
        if results.get("review"):
            review_path = os.path.join(self.output_dir, "review.md")
            with open(review_path, 'w', encoding='utf-8') as f:
                f.write(self._format_review_markdown(results["review"]))
        
        logger.info(f"[Main] 结果已保存到 {self.output_dir}")
    
    def _format_review_markdown(self, review: Dict[str, Any]) -> str:
        """格式化综述为Markdown"""
        md = f"""# {review.get('title', '研究综述')}

## 概要

- **论文总数**: {review.get('statistics', {}).get('unique_authors', 'N/A')} 位作者
- **时间跨度**: {review.get('statistics', {}).get('earliest_date', 'N/A')} 至 {review.get('statistics', {}).get('latest_date', 'N/A')}

"""
        
        for section in review.get("sections", []):
            md += f"## {section.get('title', '')}\n\n{section.get('content', '')}\n\n"
        
        return md
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """智能问答"""
        if not self.qa_system:
            return {"error": "请先运行研究以初始化问答系统"}
        
        return self.qa_system.answer(question)
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        persistence_stats = self.persistence.get_statistics()
        
        return {
            "papers_count": len(self.current_papers),
            "has_analysis": self.current_analysis is not None,
            "has_review": self.current_review is not None,
            "qa_ready": self.qa_system is not None,
            "enhanced_qa_ready": self.enhanced_qa is not None,
            "output_dir": self.output_dir,
            "persistence": persistence_stats,
            "features": {
                "arxiv_search": True,
                "citation_analysis": True,
                "knowledge_graph": True,
                "comparison_matrix": True,
                "intelligent_qa": True,
                "enhanced_qa": True,
                "report_generation": True,
                "latex_export": True,
                "feishu_integration": True,
                "data_persistence": True,
                "cache_mechanism": True
            }
        }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="AI论文预研助手")
    parser.add_argument("topic", nargs="?", default="AI Agent", help="研究课题")
    parser.add_argument("--max-papers", type=int, default=50, help="最大论文数")
    parser.add_argument("--no-feishu", action="store_true", help="禁用飞书集成")
    parser.add_argument("--output-dir", default="output", help="输出目录")
    parser.add_argument("--question", help="提问问题（智能问答模式）")
    
    args = parser.parse_args()
    
    # 初始化助手
    assistant = PaperResearchAssistant({
        "max_results": args.max_papers,
        "output_dir": args.output_dir
    })
    
    # 问答模式
    if args.question:
        if not assistant.current_papers:
            print("请先运行研究以初始化问答系统")
            return
        
        result = assistant.ask_question(args.question)
        print(f"\n问题: {result.get('question', args.question)}")
        print(f"\n回答:\n{result.get('answer', '无法回答')}")
        return
    
    # 运行研究
    print(f"\n{'='*60}")
    print(f"AI论文预研助手")
    print(f"{'='*60}")
    print(f"研究课题: {args.topic}")
    print(f"最大论文数: {args.max_papers}")
    print(f"飞书集成: {'禁用' if args.no_feishu else '启用'}")
    print(f"{'='*60}\n")
    
    result = assistant.run_research(
        topic=args.topic,
        max_papers=args.max_papers,
        enable_feishu=not args.no_feishu
    )
    
    # 输出结果摘要
    print(f"\n{'='*60}")
    print(f"研究完成!")
    print(f"{'='*60}")
    print(f"状态: {result.get('status', 'unknown')}")
    print(f"论文数: {result.get('papers_count', 0)}")
    print(f"耗时: {result.get('duration_seconds', 0):.1f}秒")
    
    if result.get("visualizations"):
        print(f"\n可视化文件:")
        for name, path in result["visualizations"].items():
            print(f"  - {name}: {path}")
    
    if result.get("feishu_docs"):
        print(f"\n飞书文档:")
        for name, info in result["feishu_docs"].items():
            if isinstance(info, dict) and info.get("success"):
                print(f"  - {name}: ✅ 成功")
            elif isinstance(info, dict):
                print(f"  - {name}: ❌ {info.get('error', '未知错误')}")
    
    print(f"\n结果已保存到: {args.output_dir}/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
