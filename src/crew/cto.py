"""
CTO (Chief Technical Officer) - 技术负责人
负责：技术方案决策、代码审查、质量把控
"""

from typing import Dict, Any, List
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TechnicalOfficer:
    """
    技术负责人Agent
    
    职责：
    1. 决定技术方案（数据源、分析工具、输出格式）
    2. 审查综述质量（三模型审查）
    3. 验证数据准确性
    4. 技术问题决策
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.review_history = []
        
    def decide_tech_stack(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        决定技术栈
        
        Args:
            analysis: CoS的意图分析结果
            
        Returns:
            技术方案
        """
        logger.info("[CTO] 决定技术方案")
        
        research_type = analysis.get("research_type", "exploratory")
        scope = analysis.get("scope", {})
        
        tech_stack = {
            "data_sources": self._select_data_sources(research_type),
            "analysis_tools": self._select_analysis_tools(research_type),
            "output_formats": self._select_output_formats(scope),
            "quality_checks": self._define_quality_checks(research_type)
        }
        
        return tech_stack
    
    def _select_data_sources(self, research_type: str) -> List[Dict[str, Any]]:
        """选择数据源"""
        sources = [
            {
                "name": "arXiv",
                "priority": 1,
                "use_case": "学术论文",
                "config": {
                    "max_results": 50,
                    "sort_by": "submittedDate",
                    "categories": ["cs.AI", "cs.CL", "cs.LG"]
                }
            }
        ]
        
        # 根据研究类型添加更多数据源
        if research_type in ["survey", "technical"]:
            sources.append({
                "name": "Google Scholar",
                "priority": 2,
                "use_case": "引用分析",
                "config": {
                    "max_results": 30
                }
            })
        
        if research_type == "applied":
            sources.append({
                "name": "Semantic Scholar",
                "priority": 2,
                "use_case": "应用论文",
                "config": {
                    "max_results": 20
                }
            })
        
        return sources
    
    def _select_analysis_tools(self, research_type: str) -> List[Dict[str, Any]]:
        """选择分析工具"""
        tools = [
            {
                "name": "CitationAnalyzer",
                "purpose": "构建引用网络",
                "config": {
                    "enable_pagerank": True,
                    "enable_clustering": True
                }
            },
            {
                "name": "KeywordExtractor",
                "purpose": "提取关键词",
                "config": {
                    "method": "tfidf",
                    "top_k": 10
                }
            }
        ]
        
        if research_type == "comparative":
            tools.append({
                "name": "ComparisonMatrix",
                "purpose": "生成对比矩阵",
                "config": {
                    "dimensions": ["方法", "数据集", "性能", "创新点"]
                }
            })
        
        return tools
    
    def _select_output_formats(self, scope: Dict[str, Any]) -> List[str]:
        """选择输出格式"""
        formats = ["markdown", "latex"]
        
        depth = scope.get("depth", "medium")
        if depth == "deep":
            formats.extend(["pdf", "feishu_doc"])
        
        return formats
    
    def _define_quality_checks(self, research_type: str) -> List[Dict[str, Any]]:
        """定义质量检查项"""
        checks = [
            {
                "name": "引用格式检查",
                "type": "format",
                "strictness": "high"
            },
            {
                "name": "数据准确性验证",
                "type": "validation",
                "strictness": "high"
            },
            {
                "name": "综述结构检查",
                "type": "structure",
                "strictness": "medium"
            }
        ]
        
        if research_type == "technical":
            checks.append({
                "name": "技术术语一致性检查",
                "type": "consistency",
                "strictness": "high"
            })
        
        return checks
    
    def review_review(self, review: Dict[str, Any], papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        三模型审查综述质量
        
        Args:
            review: 综述内容
            papers: 论文列表
            
        Returns:
            审查结果
        """
        logger.info("[CTO] 执行三模型审查")
        
        # 模拟三模型审查
        # 实际实现中会调用三个不同的LLM进行审查
        
        review_results = {
            "codex_review": self._codex_review(review, papers),
            "claude_review": self._claude_review(review, papers),
            "gemini_review": self._gemini_review(review, papers),
            "timestamp": datetime.now().isoformat()
        }
        
        # 综合评分
        scores = [
            review_results["codex_review"]["score"],
            review_results["claude_review"]["score"],
            review_results["gemini_review"]["score"]
        ]
        
        review_results["overall_score"] = sum(scores) / len(scores)
        review_results["passed"] = review_results["overall_score"] >= 7.0
        
        # 记录审查历史
        self.review_history.append(review_results)
        
        return review_results
    
    def _codex_review(self, review: Dict[str, Any], papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Codex审查（边界情况、逻辑错误）"""
        return {
            "score": 8.5,
            "issues": [
                {
                    "type": "suggestion",
                    "location": "第2节",
                    "content": "建议增加更多对比分析"
                }
            ],
            "strengths": [
                "逻辑清晰",
                "引用格式规范"
            ]
        }
    
    def _claude_review(self, review: Dict[str, Any], papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Claude审查（验证其他审查器的发现）"""
        return {
            "score": 7.8,
            "issues": [],
            "strengths": [
                "结构完整",
                "覆盖面广"
            ]
        }
    
    def _gemini_review(self, review: Dict[str, Any], papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gemini审查（安全漏洞、可扩展性）"""
        return {
            "score": 8.2,
            "issues": [
                {
                    "type": "warning",
                    "location": "第4节",
                    "content": "部分数据需要更新"
                }
            ],
            "strengths": [
                "数据准确",
                "引用完整"
            ]
        }
    
    def validate_data(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证数据准确性
        
        Returns:
            验证结果
        """
        logger.info(f"[CTO] 验证 {len(papers)} 篇论文数据")
        
        issues = []
        
        # 检查必要字段
        for i, paper in enumerate(papers):
            if not paper.get("title"):
                issues.append(f"论文{i+1}缺少标题")
            if not paper.get("authors"):
                issues.append(f"论文{i+1}缺少作者信息")
            if not paper.get("arxiv_id"):
                issues.append(f"论文{i+1}缺少arXiv ID")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_papers": len(papers),
            "validated_at": datetime.now().isoformat()
        }
    
    def generate_tech_report(self, tech_stack: Dict[str, Any]) -> str:
        """生成技术方案报告"""
        report = f"""
# 技术方案报告

## 数据源
"""
        for source in tech_stack.get("data_sources", []):
            report += f"- {source['name']} (优先级: {source['priority']})\n"
        
        report += "\n## 分析工具\n"
        for tool in tech_stack.get("analysis_tools", []):
            report += f"- {tool['name']}: {tool['purpose']}\n"
        
        report += "\n## 输出格式\n"
        for fmt in tech_stack.get("output_formats", []):
            report += f"- {fmt}\n"
        
        report += "\n## 质量检查\n"
        for check in tech_stack.get("quality_checks", []):
            report += f"- {check['name']} (严格度: {check['strictness']})\n"
        
        return report
