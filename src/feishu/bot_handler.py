"""
飞书机器人消息处理器
处理飞书消息，触发研究任务
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import get_logger
from src.crew.orchestrator import Orchestrator
from .card_builder import CardBuilder

logger = get_logger(__name__)


class FeishuBotHandler:
    """
    飞书机器人消息处理器
    
    功能：
    1. 解析飞书消息
    2. 识别研究指令
    3. 触发研究任务
    4. 返回结果卡片
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.orchestrator = Orchestrator(config)
        self.card_builder = CardBuilder()
        
        # 支持的指令格式
        self.commands = {
            "研究": self._handle_research,
            "搜索": self._handle_search,
            "帮助": self._handle_help,
            "状态": self._handle_status,
        }
        
    def handle_message(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理飞书消息事件
        
        Args:
            event: 飞书事件数据
            
        Returns:
            响应结果
        """
        logger.info(f"[Bot] 收到消息: {event}")
        
        try:
            # 解析消息内容
            message = self._parse_message(event)
            
            if not message:
                return self._create_text_response("抱歉，我没有理解您的消息。发送'帮助'查看使用说明。")
            
            # 识别指令
            command, params = self._parse_command(message)
            
            if command in self.commands:
                return self.commands[command](params)
            else:
                # 默认作为研究课题
                return self._handle_research(message)
                
        except Exception as e:
            logger.error(f"[Bot] 处理消息失败: {e}")
            return self._create_text_response(f"处理失败: {str(e)}")
    
    def _parse_message(self, event: Dict[str, Any]) -> Optional[str]:
        """解析消息内容"""
        # 飞书消息格式
        if "event" in event:
            message = event["event"].get("message", {})
            content = message.get("content", "{}")
            
            # 解析JSON内容
            if isinstance(content, str):
                content_data = json.loads(content)
            else:
                content_data = content
            
            # 提取文本
            if "text" in content_data:
                return content_data["text"]
        
        return None
    
    def _parse_command(self, message: str) -> tuple:
        """解析指令"""
        message = message.strip()
        
        for cmd in self.commands:
            if message.startswith(cmd):
                params = message[len(cmd):].strip()
                return cmd, params
        
        return None, message
    
    def _handle_research(self, topic: str) -> Dict[str, Any]:
        """处理研究指令"""
        if not topic:
            return self._create_text_response("请提供研究课题，例如：研究 大模型在教育中的应用")
        
        logger.info(f"[Bot] 开始研究: {topic}")
        
        # 发送开始消息
        start_card = self.card_builder.build_progress_card(
            topic=topic,
            status="正在检索论文...",
            progress=0
        )
        
        # 执行研究
        try:
            result = self.orchestrator.run_research(
                topic=topic,
                auto_confirm=True
            )
            
            # 构建结果卡片
            result_card = self.card_builder.build_result_card(
                topic=topic,
                papers_count=len(result["papers"]),
                duration=result["duration"],
                quality_score=result["quality_score"],
                report_url=result.get("report_url", ""),
                graph_url=result.get("graph_url", "")
            )
            
            return result_card
            
        except Exception as e:
            logger.error(f"[Bot] 研究失败: {e}")
            return self._create_text_response(f"研究失败: {str(e)}")
    
    def _handle_search(self, keywords: str) -> Dict[str, Any]:
        """处理搜索指令"""
        if not keywords:
            return self._create_text_response("请提供搜索关键词，例如：搜索 Transformer 语音识别")
        
        # 简化的搜索（只检索不生成报告）
        logger.info(f"[Bot] 搜索论文: {keywords}")
        
        # TODO: 实现简化搜索
        
        return self._create_text_response(f"搜索功能开发中，关键词: {keywords}")
    
    def _handle_help(self, params: str) -> Dict[str, Any]:
        """处理帮助指令"""
        help_text = """
🦞 AI论文预研助手 - 使用说明

📖 基本用法：
• 直接发送研究课题，例如：大模型在教育中的应用
• 研究 [课题] - 开始研究
• 搜索 [关键词] - 快速搜索论文

📊 其他指令：
• 状态 - 查看系统状态
• 帮助 - 显示此帮助

⏱️ 研究流程：
1. 输入课题 → 2. 自动检索 → 3. 解析论文 → 4. 生成报告

💡 示例：
• 研究 Transformer models for speech recognition
• 大模型在K12英语口语教学中的应用
"""
        
        return self._create_text_response(help_text)
    
    def _handle_status(self, params: str) -> Dict[str, Any]:
        """处理状态指令"""
        status = self.orchestrator.get_status()
        
        status_text = f"""
📊 系统状态

• 状态: {status['context']['status']}
• 已完成研究: {len(self.orchestrator.experiences)} 次
• 经验沉淀: {status['experiences_count']} 条
• 变更记录: {status['change_log_count']} 条
• 漂移分数: {status['drift_score']:.2f}
"""
        
        return self._create_text_response(status_text)
    
    def _create_text_response(self, text: str) -> Dict[str, Any]:
        """创建文本响应"""
        return {
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False)
        }
    
    def _create_card_response(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """创建卡片响应"""
        return {
            "msg_type": "interactive",
            "card": card
        }
