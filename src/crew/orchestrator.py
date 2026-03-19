"""
Orchestrator - 编排器
负责：持有研究上下文、协调Agent工作、管理Agent Swarm、实现Ralph Loop V2
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import time
from src.utils.logger import get_logger
from src.utils.memory import MemoryManager
from src.crew.cos import ChiefOfStaff
from src.crew.cto import TechnicalOfficer
from src.crew.builder import Builder
from src.crew.ops import OperationsOfficer
from src.visualization.knowledge_graph import KnowledgeGraph
from src.visualization.comparison_matrix import ComparisonMatrix
from src.qa.paper_qa import PaperQA

logger = get_logger(__name__)


class Orchestrator:
    """
    编排器Agent
    
    职责：
    1. 持有完整的研究上下文（客户数据、历史决策、成功/失败模式）
    2. 协调多个Agent的工作
    3. 实现Ralph Loop V2（自改进Prompt系统）
    4. 管理Agent Swarm（并行处理）
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory = MemoryManager(config)
        
        # 初始化各个Agent
        self.cos = ChiefOfStaff(config)
        self.cto = TechnicalOfficer(config)
        self.builder = Builder(config)
        self.ops = OperationsOfficer(config)
        
        # 研究上下文
        self.context = {
            "topic": None,
            "research_type": None,
            "scope": None,
            "tech_stack": None,
            "papers": [],
            "review": None,
            "status": "idle"
        }
        
        # 经验沉淀
        self.experiences = []
        
    def run_research(self, topic: str, auto_confirm: bool = False) -> Dict[str, Any]:
        """
        运行完整研究流程
        
        Args:
            topic: 研究课题
            auto_confirm: 是否自动确认（跳过用户确认）
            
        Returns:
            研究结果
        """
        logger.info(f"[Orchestrator] 开始研究: {topic}")
        
        start_time = time.time()
        
        # Phase 1: 意图分析（CoS）
        self.context["status"] = "analyzing"
        analysis = self.cos.analyze_intent(topic)
        self.context["topic"] = topic
        self.context["research_type"] = analysis["research_type"]
        self.context["scope"] = analysis["scope"]
        
        # 等待用户确认（如果不是自动确认）
        if not auto_confirm:
            confirmation = self.cos.confirm_intent(analysis)
            logger.info(f"[Orchestrator] 等待用户确认: {confirmation['questions']}")
            # 实际实现中应该等待用户输入
            # 这里自动继续
        
        # Phase 2: 技术方案（CTO）
        self.context["status"] = "planning"
        tech_stack = self.cto.decide_tech_stack(analysis)
        self.context["tech_stack"] = tech_stack
        
        # Phase 3: 执行研究（Builder）
        self.context["status"] = "searching"
        # 提取关键词并传递给Builder
        keywords = analysis.get("keywords", [])
        if not keywords:
            keywords = self._extract_keywords_from_topic(topic)
        self.builder.config["keywords"] = keywords
        logger.info(f"[Orchestrator] 搜索关键词: {keywords}")
        
        search_result = self.builder.execute_search(tech_stack, analysis["scope"])
        self.context["papers"] = search_result["papers"]
        
        self.context["status"] = "parsing"
        parse_result = self.builder.parse_papers_parallel()
        
        self.context["status"] = "analyzing"
        citation_result = self.builder.analyze_citations()
        
        self.context["status"] = "writing"
        review = self.builder.write_review(analysis["core_questions"])
        self.context["review"] = review
        
        # Phase 4: 质量审查（CTO）
        self.context["status"] = "reviewing"
        review_result = self.cto.review_review(review, self.context["papers"])
        
        # 如果审查不通过，触发Ralph Loop
        if not review_result["passed"]:
            logger.warning("[Orchestrator] 审查不通过，触发Ralph Loop")
            review = self._ralph_loop(review, review_result)
            self.context["review"] = review
        
        # Phase 5: 生成报告（Builder + Ops）
        self.context["status"] = "generating"
        reports = self.builder.generate_report(
            review,
            tech_stack["output_formats"]
        )
        
        # 保存报告
        for fmt, content in reports.items():
            filename = f"research_report.{fmt}"
            self.ops.save_report_locally(content, filename)
        
        # Phase 5.5: 生成可视化（新增亮点功能）
        self.context["status"] = "visualizing"
        visualizations = self._generate_visualizations(self.context["papers"])
        
        # 写入飞书文档
        if "feishu_doc" in tech_stack["output_formats"]:
            feishu_result = self._write_to_feishu(review, topic)
        
        # Phase 6: 发送通知（Ops）
        self.context["status"] = "notifying"
        duration = time.time() - start_time
        
        self.ops.send_feishu_notification(
            f"研究完成: {topic}\n"
            f"论文数: {len(self.context['papers'])}\n"
            f"耗时: {duration:.1f}秒\n"
            f"质量评分: {review_result['overall_score']:.1f}/10"
        )
        
        # 保存记忆
        self.context["status"] = "completed"
        self.memory.log("研究完成", {
            "topic": topic,
            "papers": len(self.context["papers"]),
            "duration": duration,
            "quality_score": review_result["overall_score"]
        })
        
        # 沉淀经验
        self._record_experience(topic, review_result)
        
        return {
            "topic": topic,
            "papers": self.context["papers"],
            "review": review,
            "reports": reports,
            "visualizations": visualizations,
            "quality_score": review_result["overall_score"],
            "duration": duration,
            "status": "completed"
        }
    
    def _ralph_loop(self, review: Dict[str, Any], review_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ralph Loop V2 - 自改进Prompt系统
        
        根据审查结果改进综述
        """
        logger.info("[Orchestrator] 执行Ralph Loop V2")
        
        max_iterations = 3
        iteration = 0
        
        while iteration < max_iterations and not review_result["passed"]:
            iteration += 1
            logger.info(f"[Orchestrator] Ralph Loop 迭代 {iteration}/{max_iterations}")
            
            # 分析失败原因
            issues = []
            for model_review in [
                review_result.get("codex_review", {}),
                review_result.get("claude_review", {}),
                review_result.get("gemini_review", {})
            ]:
                issues.extend(model_review.get("issues", []))
            
            # 生成改进Prompt
            improvement_prompt = self._generate_improvement_prompt(issues)
            
            # 重新撰写综述（模拟）
            # 实际实现中会调用LLM重新生成
            logger.info(f"[Orchestrator] 改进Prompt: {improvement_prompt[:100]}...")
            
            # 重新审查
            review_result = self.cto.review_review(review, self.context["papers"])
        
        if review_result["passed"]:
            logger.info(f"[Orchestrator] Ralph Loop 成功，迭代次数: {iteration}")
        else:
            logger.warning(f"[Orchestrator] Ralph Loop 未通过，最大迭代: {max_iterations}")
        
        return review
    
    def _generate_improvement_prompt(self, issues: List[Dict[str, Any]]) -> str:
        """
        根据问题生成改进Prompt
        
        Args:
            issues: 审查发现的问题
            
        Returns:
            改进Prompt
        """
        if not issues:
            return "综述质量良好，无需改进。"
        
        prompt_parts = ["根据审查反馈，需要改进以下方面：\n"]
        
        for i, issue in enumerate(issues, 1):
            prompt_parts.append(f"{i}. [{issue.get('type', 'issue')}] {issue.get('location', '')}: {issue.get('content', '')}\n")
        
        prompt_parts.append("\n请针对性地改进上述问题。")
        
        return "".join(prompt_parts)
    
    def _write_to_feishu(self, review: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """
        写入飞书文档
        
        Args:
            review: 综述内容
            topic: 研究课题
            
        Returns:
            写入结果
        """
        logger.info("[Orchestrator] 写入飞书文档")
        
        # 创建文档
        doc = self.ops.create_feishu_doc(f"研究综述: {topic}")
        
        # 生成内容
        content = self._generate_feishu_content(review)
        
        # 写入文档
        result = self.ops.write_to_feishu(doc["doc_token"], content, doc["title"])
        
        # 分享文档（如果配置了协作者）
        collaborators = self.config.get("feishu_collaborators", [])
        if collaborators:
            self.ops.share_feishu_doc(doc["doc_token"], collaborators, "edit")
        
        return result
    
    def _generate_feishu_content(self, review: Dict[str, Any]) -> str:
        """生成飞书文档内容"""
        content = f"""# {review.get('title', '研究综述')}

## 摘要

{review.get('abstract', '暂无摘要')}

## 核心问题回答

"""
        
        for qa in review.get("core_questions_answers", []):
            content += f"""### {qa['question']}

{qa['answer']}

"""
        
        content += "\n## 详细分析\n\n"
        
        for section in review.get("sections", []):
            content += f"### {section.get('title', '')}\n\n{section.get('content', '')}\n\n"
        
        content += "\n## 参考文献\n\n"
        for i, citation in enumerate(review.get("citations", []), 1):
            content += f"{i}. {citation}\n"
        
        return content
    
    def _record_experience(self, topic: str, review_result: Dict[str, Any]):
        """
        沉淀经验
        
        Args:
            topic: 研究课题
            review_result: 审查结果
        """
        experience = {
            "topic": topic,
            "research_type": self.context["research_type"],
            "papers_count": len(self.context["papers"]),
            "quality_score": review_result["overall_score"],
            "success": review_result["passed"],
            "timestamp": datetime.now().isoformat()
        }
        
        self.experiences.append(experience)
        
        # 提取成功模式
        if experience["success"]:
            pattern = f"研究类型【{experience['research_type']}】的成功模式: 论文数{experience['papers_count']}, 质量分{experience['quality_score']}"
            logger.info(f"[Orchestrator] 成功模式: {pattern}")
    
    def _generate_visualizations(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成可视化内容（亮点功能）
        
        Args:
            papers: 论文列表
            
        Returns:
            可视化数据
        """
        logger.info("[Orchestrator] 生成可视化内容")
        
        output_dir = self.config.get("output_dir", "output")
        visualizations = {}
        
        # 1. 知识图谱
        try:
            kg = KnowledgeGraph()
            kg_data = kg.build_graph(papers)
            kg_path = kg.export_to_html(kg_data, f"{output_dir}/knowledge_graph.html")
            visualizations["knowledge_graph"] = {
                "path": kg_path,
                "nodes": kg_data["statistics"]["total_nodes"],
                "edges": kg_data["statistics"]["total_edges"]
            }
            logger.info(f"[Orchestrator] 知识图谱生成: {kg_path}")
        except Exception as e:
            logger.error(f"[Orchestrator] 知识图谱生成失败: {e}")
        
        # 2. 对比矩阵
        try:
            cm = ComparisonMatrix()
            cm_data = cm.generate_matrix(papers, max_papers=10)
            cm_path = cm.export_to_html(cm_data, f"{output_dir}/comparison_matrix.html")
            visualizations["comparison_matrix"] = {
                "path": cm_path,
                "papers": cm_data["statistics"]["total_papers"]
            }
            logger.info(f"[Orchestrator] 对比矩阵生成: {cm_path}")
        except Exception as e:
            logger.error(f"[Orchestrator] 对比矩阵生成失败: {e}")
        
        # 3. 智能问答（演示）
        try:
            qa = PaperQA(papers)
            # 生成示例问答
            demo_questions = [
                "哪些论文使用了Transformer？",
                "主要的研究方法有哪些？",
                "总结一下研究现状"
            ]
            qa_pairs = qa.chat(demo_questions)
            qa_path = qa.export_to_html(qa_pairs, f"{output_dir}/qa_demo.html")
            visualizations["qa_demo"] = {
                "path": qa_path,
                "questions": len(demo_questions)
            }
            # 保存QA实例供后续使用
            self.qa_system = qa
            logger.info(f"[Orchestrator] 智能问答演示生成: {qa_path}")
        except Exception as e:
            logger.error(f"[Orchestrator] 智能问答生成失败: {e}")
        
        return visualizations
    
    def spawn_parallel_agents(self, papers: List[Dict[str, Any]], agent_count: int = 3) -> Dict[str, Any]:
        """
        启动并行Agent处理不同论文
        
        Args:
            papers: 论文列表
            agent_count: Agent数量
            
        Returns:
            分配结果
        """
        logger.info(f"[Orchestrator] 启动 {agent_count} 个并行Agent")
        
        # 分配论文
        chunk_size = len(papers) // agent_count + 1
        assignments = []
        
        for i in range(agent_count):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(papers))
            
            if start < len(papers):
                assignments.append({
                    "agent_id": f"builder_{i+1}",
                    "papers": papers[start:end],
                    "count": end - start
                })
        
        return {
            "assignments": assignments,
            "total_agents": len(assignments),
            "total_papers": len(papers)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "context": self.context,
            "experiences_count": len(self.experiences),
            "change_log_count": len(self.ops.change_log),
            "drift_score": self.ops.drift_score
        }
    
    def _extract_keywords_from_topic(self, topic: str) -> List[str]:
        """
        从课题中提取关键词
        
        Args:
            topic: 研究课题
            
        Returns:
            关键词列表
        """
        # 中英文停用词
        stop_words = {
            '的', '在', '中', '与', '和', '或', '等', '对', '通过', '基于', '研究',
            '分析', '应用', '系统', '方法', '技术', '一种', '新型', '智能',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }
        
        # 分词（简单实现：按空格和中文字符分割）
        import re
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', topic)
        
        # 过滤停用词和短词
        keywords = [w for w in words if w.lower() not in stop_words and len(w) > 1]
        
        # 限制数量
        return keywords[:5]
    
    def export_context(self) -> str:
        """导出研究上下文"""
        import json
        return json.dumps(self.context, ensure_ascii=False, indent=2, default=str)
