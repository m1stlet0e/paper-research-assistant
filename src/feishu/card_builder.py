"""
飞书消息卡片构建器
构建交互式消息卡片
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class CardBuilder:
    """
    飞书消息卡片构建器
    
    功能：
    1. 构建研究结果卡片
    2. 构建进度卡片
    3. 构建论文卡片
    4. 构建错误卡片
    """
    
    def __init__(self):
        self.card_template = {
            "config": {
                "wide_screen_mode": True
            },
            "elements": []
        }
    
    def build_result_card(self, topic: str, papers_count: int, duration: float,
                         quality_score: float, report_url: str = "", 
                         graph_url: str = "") -> Dict[str, Any]:
        """
        构建研究结果卡片
        
        Args:
            topic: 研究课题
            papers_count: 论文数量
            duration: 耗时（秒）
            quality_score: 质量评分
            report_url: 报告链接
            graph_url: 知识图谱链接
            
        Returns:
            卡片数据
        """
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🦞 研究完成: {topic}"
                },
                "template": "blue"
            },
            "elements": [
                # 统计数据
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**📄 论文数量**\n{papers_count} 篇"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**⏱️ 耗时**\n{duration:.1f} 秒"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**📊 质量评分**\n{quality_score:.1f}/10"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**📅 完成时间**\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            }
                        }
                    ]
                },
                # 分隔线
                {
                    "tag": "hr"
                },
                # 操作按钮
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "📄 查看报告"
                            },
                            "url": report_url or "http://localhost:9000/output/research_report.md",
                            "type": "primary"
                        },
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "🕸️ 知识图谱"
                            },
                            "url": graph_url or "http://localhost:9000/knowledge_graph.html",
                            "type": "default"
                        }
                    ]
                },
                # 备注
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "💡 效率提升: 传统方式需要1周+，本系统仅需30分钟"
                        }
                    ]
                }
            ]
        }
        
        return {
            "msg_type": "interactive",
            "card": card
        }
    
    def build_progress_card(self, topic: str, status: str, progress: int) -> Dict[str, Any]:
        """
        构建进度卡片
        
        Args:
            topic: 研究课题
            status: 当前状态
            progress: 进度百分比
            
        Returns:
            卡片数据
        """
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🔍 正在研究: {topic}"
                },
                "template": "blue"
            },
            "elements": [
                # 进度条
                {
                    "tag": "progress",
                    "percent": progress / 100.0
                },
                # 状态文本
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{status}**\n进度: {progress}%"
                    }
                }
            ]
        }
        
        return {
            "msg_type": "interactive",
            "card": card
        }
    
    def build_paper_card(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建论文卡片
        
        Args:
            paper: 论文数据
            
        Returns:
            卡片数据
        """
        title = paper.get("title", "Unknown")
        authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])])
        published = paper.get("published", "")
        summary = paper.get("summary", "")[:200] + "..."
        pdf_url = paper.get("pdf_url", "")
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📄 {title[:50]}..."
                },
                "template": "turquoise"
            },
            "elements": [
                # 基本信息
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**👥 作者**\n{authors[:50]}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**📅 发表时间**\n{published[:10]}"
                            }
                        }
                    ]
                },
                # 摘要
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**📝 摘要**\n{summary}"
                    }
                },
                # 操作按钮
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "📥 下载PDF"
                            },
                            "url": pdf_url,
                            "type": "primary"
                        }
                    ]
                }
            ]
        }
        
        return {
            "msg_type": "interactive",
            "card": card
        }
    
    def build_error_card(self, error_message: str, topic: str = "") -> Dict[str, Any]:
        """
        构建错误卡片
        
        Args:
            error_message: 错误消息
            topic: 研究课题
            
        Returns:
            卡片数据
        """
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "❌ 研究失败"
                },
                "template": "red"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**课题**: {topic}\n\n**错误**: {error_message}"
                    }
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "请检查课题是否有效，或联系管理员"
                        }
                    ]
                }
            ]
        }
        
        return {
            "msg_type": "interactive",
            "card": card
        }
    
    def build_daily_push_card(self, papers: List[Dict[str, Any]], date: str = None) -> Dict[str, Any]:
        """
        构建每日推送卡片
        
        Args:
            papers: 论文列表
            date: 日期
            
        Returns:
            卡片数据
        """
        date = date or datetime.now().strftime("%Y-%m-%d")
        
        # 构建论文列表
        paper_list = []
        for i, paper in enumerate(papers[:10], 1):
            title = paper.get("title", "Unknown")[:60]
            paper_list.append(f"{i}. {title}")
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📰 每日论文推送 - {date}"
                },
                "template": "blue"
            },
            "elements": [
                # 统计
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**今日新论文**: {len(papers)} 篇\n\n" + "\n".join(paper_list)
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "🦞 AI论文预研助手 | 让AI帮你读论文"
                        }
                    ]
                }
            ]
        }
        
        return {
            "msg_type": "interactive",
            "card": card
        }
    
    def build_welcome_card(self) -> Dict[str, Any]:
        """构建欢迎卡片"""
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🦞 AI论文预研助手"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "**欢迎使用AI论文预研助手！**\n\n我可以帮你：\n• 🔍 快速检索学术论文\n• 📖 自动解析论文内容\n• 📋 生成研究综述\n• 🕸️ 构建知识图谱\n\n**使用方法**：\n直接发送研究课题即可开始，例如：\n`大模型在教育中的应用`\n\n或使用指令：\n• `研究 [课题]` - 开始研究\n• `搜索 [关键词]` - 快速搜索\n• `帮助` - 查看使用说明"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "效率提升: 将一周的文献调研工作压缩到30分钟"
                        }
                    ]
                }
            ]
        }
        
        return {
            "msg_type": "interactive",
            "card": card
        }
