"""
Chief of Staff (CoS) - 战略参谋
负责：意图对齐、研究范围确定、异步推进决策
"""

from typing import Dict, Any, List
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ChiefOfStaff:
    """
    战略参谋Agent
    
    职责：
    1. 分析用户研究意图
    2. 确定研究范围和边界
    3. 协调其他Agent的工作
    4. 在用户不在线时推进任务
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.decision_history = []
        self.active_projects = {}
        
    def analyze_intent(self, topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析研究意图
        
        Args:
            topic: 研究课题
            context: 上下文信息（历史对话、偏好等）
            
        Returns:
            意图分析结果
        """
        logger.info(f"[CoS] 分析研究意图: {topic}")
        
        # 1. 识别研究类型
        research_type = self._identify_research_type(topic)
        
        # 2. 提取关键词
        keywords = self._extract_keywords(topic, research_type)
        logger.info(f"[CoS] 提取关键词: {keywords}")
        
        # 3. 提取核心问题
        core_questions = self._extract_core_questions(topic, research_type)
        
        # 4. 确定研究范围
        scope = self._determine_scope(topic, research_type)
        
        # 5. 生成研究计划
        plan = self._generate_research_plan(topic, research_type, scope)
        
        result = {
            "topic": topic,
            "research_type": research_type,
            "keywords": keywords,
            "core_questions": core_questions,
            "scope": scope,
            "plan": plan,
            "timestamp": datetime.now().isoformat()
        }
        
        # 记录决策
        self._log_decision("intent_analysis", result)
        
        return result
    
    def _identify_research_type(self, topic: str) -> str:
        """识别研究类型"""
        topic_lower = topic.lower()
        
        # 技术研究
        if any(kw in topic_lower for kw in ['算法', '模型', '架构', 'algorithm', 'model', 'architecture']):
            return "technical"
        
        # 应用研究
        if any(kw in topic_lower for kw in ['应用', '实践', 'implementation', 'application']):
            return "applied"
        
        # 综述研究
        if any(kw in topic_lower for kw in ['综述', '调查', 'survey', 'review']):
            return "survey"
        
        # 对比研究
        if any(kw in topic_lower for kw in ['对比', '比较', 'comparison', 'versus']):
            return "comparative"
        
        # 默认为探索性研究
        return "exploratory"
    
    def _extract_keywords(self, topic: str, research_type: str) -> List[str]:
        """
        从课题中提取关键词
        
        Args:
            topic: 研究课题
            research_type: 研究类型
            
        Returns:
            关键词列表
        """
        # 中英文停用词
        stop_words = {
            '的', '在', '中', '与', '和', '或', '等', '对', '通过', '基于', '研究',
            '分析', '应用', '系统', '方法', '技术', '一种', '新型', '智能', '最新',
            '进展', '现状', '问题', '方向', '趋势', '发展', '实践', '案例',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }
        
        # 分词（简单实现：按空格和中文字符分割）
        import re
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', topic)
        
        # 过滤停用词和短词
        keywords = [w for w in words if w.lower() not in stop_words and len(w) > 1]
        
        # 英文关键词转小写
        keywords = [w.lower() if w.isalpha() else w for w in keywords]
        
        # 根据研究类型添加领域关键词
        if research_type == "technical":
            # 技术研究：添加技术相关英文关键词
            if "agent" not in [k.lower() for k in keywords]:
                keywords.append("agent")
        elif research_type == "applied":
            # 应用研究：添加应用相关英文关键词
            pass
        
        # 去重并限制数量
        unique_keywords = []
        seen = set()
        for k in keywords:
            if k.lower() not in seen:
                seen.add(k.lower())
                unique_keywords.append(k)
        
        return unique_keywords[:6]
    
    def _extract_core_questions(self, topic: str, research_type: str) -> List[str]:
        """提取核心研究问题"""
        questions = []
        
        if research_type == "technical":
            questions = [
                f"当前{topic}的技术现状是什么？",
                f"主流方法有哪些？各自的优缺点？",
                f"最新的技术突破有哪些？",
                f"未来的研究方向是什么？"
            ]
        elif research_type == "applied":
            questions = [
                f"{topic}在实际场景中如何应用？",
                f"应用中遇到的主要挑战是什么？",
                f"有哪些成功的案例？",
                f"最佳实践是什么？"
            ]
        elif research_type == "survey":
            questions = [
                f"{topic}领域的发展历程？",
                f"当前的研究热点？",
                f"主要的研究团队和机构？",
                f"未来的发展趋势？"
            ]
        else:
            questions = [
                f"{topic}是什么？",
                f"为什么重要？",
                f"当前的发展状况？",
                f"有哪些关键问题需要解决？"
            ]
        
        return questions
    
    def _determine_scope(self, topic: str, research_type: str) -> Dict[str, Any]:
        """确定研究范围"""
        scope = {
            "time_range": "last_3_years",  # 默认最近3年
            "max_papers": 50,  # 默认最多50篇
            "sources": ["arxiv", "google_scholar"],
            "depth": "medium",  # shallow/medium/deep
            "focus_areas": []
        }
        
        # 根据研究类型调整范围
        if research_type == "survey":
            scope["time_range"] = "last_5_years"
            scope["max_papers"] = 100
            scope["depth"] = "deep"
        elif research_type == "technical":
            scope["time_range"] = "last_2_years"
            scope["depth"] = "deep"
        elif research_type == "comparative":
            scope["max_papers"] = 30
            scope["depth"] = "shallow"
        
        return scope
    
    def _generate_research_plan(self, topic: str, research_type: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """生成研究计划"""
        plan = {
            "phases": [
                {
                    "id": "literature_search",
                    "name": "文献检索",
                    "tasks": ["检索arXiv", "检索Google Scholar", "去重排序"],
                    "estimated_time": "10分钟",
                    "agent": "Builder"
                },
                {
                    "id": "paper_analysis",
                    "name": "论文分析",
                    "tasks": ["解析摘要", "提取关键信息", "构建引用网络"],
                    "estimated_time": "20分钟",
                    "agent": "Builder"
                },
                {
                    "id": "review_writing",
                    "name": "综述撰写",
                    "tasks": ["生成综述框架", "撰写各章节", "添加引用"],
                    "estimated_time": "15分钟",
                    "agent": "Builder"
                },
                {
                    "id": "quality_review",
                    "name": "质量审查",
                    "tasks": ["三模型审查", "检查引用格式", "验证数据准确性"],
                    "estimated_time": "10分钟",
                    "agent": "CTO"
                },
                {
                    "id": "delivery",
                    "name": "交付输出",
                    "tasks": ["生成Markdown报告", "写入飞书文档", "发送通知"],
                    "estimated_time": "5分钟",
                    "agent": "Ops"
                }
            ],
            "total_estimated_time": "60分钟",
            "checkpoints": [
                "文献检索完成后确认",
                "综述初稿完成后审查",
                "最终报告生成后验收"
            ]
        }
        
        return plan
    
    def _log_decision(self, decision_type: str, result: Dict[str, Any]):
        """记录决策"""
        self.decision_history.append({
            "type": decision_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"[CoS] 决策记录: {decision_type}")
    
    def confirm_intent(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        确认研究意图（等待用户确认）
        
        Returns:
            确认问题列表
        """
        questions = [
            f"研究类型识别为【{analysis['research_type']}】，是否正确？",
            f"核心问题包括：{', '.join(analysis['core_questions'][:2])}，是否需要调整？",
            f"计划检索约{analysis['scope']['max_papers']}篇论文，时间范围{analysis['scope']['time_range']}，是否合适？"
        ]
        
        return {
            "need_confirmation": True,
            "questions": questions,
            "analysis": analysis
        }
    
    def coordinate_agents(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        协调其他Agent的工作
        
        Returns:
            Agent任务分配结果
        """
        assignments = []
        
        for phase in plan["phases"]:
            assignment = {
                "phase_id": phase["id"],
                "agent": phase["agent"],
                "tasks": phase["tasks"],
                "status": "pending"
            }
            assignments.append(assignment)
        
        return {
            "assignments": assignments,
            "total_phases": len(assignments)
        }
