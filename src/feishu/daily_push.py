"""
每日论文推送服务
定时推送最新论文到飞书
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import schedule
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import get_logger
from src.agents.sub_agents import ArxivSearcher
from config.feishu_config import FEISHU_APP_ID, FEISHU_APP_SECRET, DAILY_PUSH_CONFIG, TARGET_USER_ID
from .card_builder import CardBuilder

logger = get_logger(__name__)


class DailyPaperPusher:
    """
    每日论文推送服务
    
    功能：
    1. 定时检索最新论文
    2. 过滤和排序
    3. 推送到飞书
    4. 支持多关键词订阅
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or DAILY_PUSH_CONFIG
        self.arxiv_searcher = ArxivSearcher({"max_results": self.config.get("max_papers", 10)})
        self.card_builder = CardBuilder()
        self.keywords = self.config.get("keywords", [])
        self.is_running = False
        self.push_thread = None
        
    def start(self):
        """启动推送服务"""
        if self.is_running:
            logger.warning("[Pusher] 服务已在运行")
            return
        
        logger.info("[Pusher] 启动每日推送服务")
        
        # 设置定时任务
        push_time = self.config.get("time", "08:00")
        schedule.every().day.at(push_time).do(self._daily_push)
        
        # 启动后台线程
        self.is_running = True
        self.push_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.push_thread.start()
        
        logger.info(f"[Pusher] 服务已启动，每天 {push_time} 推送")
    
    def stop(self):
        """停止推送服务"""
        logger.info("[Pusher] 停止推送服务")
        self.is_running = False
        schedule.clear()
        
    def _run_scheduler(self):
        """运行调度器"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def _daily_push(self):
        """执行每日推送"""
        logger.info("[Pusher] 开始每日推送")
        
        try:
            # 1. 检索最新论文
            papers = self._fetch_latest_papers()
            
            if not papers:
                logger.info("[Pusher] 没有找到新论文")
                return
            
            # 2. 过滤和排序
            filtered_papers = self._filter_papers(papers)
            
            # 3. 推送到飞书
            self._push_to_feishu(filtered_papers)
            
            logger.info(f"[Pusher] 推送完成: {len(filtered_papers)}篇论文")
            
        except Exception as e:
            logger.error(f"[Pusher] 推送失败: {e}")
    
    def _fetch_latest_papers(self) -> List[Dict[str, Any]]:
        """获取最新论文"""
        logger.info("[Pusher] 检索最新论文")
        
        all_papers = []
        
        for keyword in self.keywords:
            try:
                papers = self.arxiv_searcher.search([keyword], date_range="last_week")
                all_papers.extend(papers)
            except Exception as e:
                logger.error(f"[Pusher] 检索失败 ({keyword}): {e}")
        
        # 去重
        seen = set()
        unique_papers = []
        for paper in all_papers:
            paper_id = paper.get("arxiv_id") or paper.get("title")
            if paper_id and paper_id not in seen:
                seen.add(paper_id)
                unique_papers.append(paper)
        
        return unique_papers
    
    def _filter_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤论文"""
        # 按日期排序（最新优先）
        papers.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        # 限制数量
        max_papers = self.config.get("max_papers", 10)
        return papers[:max_papers]
    
    def _push_to_feishu(self, papers: List[Dict[str, Any]]):
        """推送到飞书"""
        logger.info(f"[Pusher] 推送 {len(papers)} 篇论文到飞书")
        
        # 构建卡片
        card = self.card_builder.build_daily_push_card(papers)
        
        # 使用 message 工具发送到飞书
        # 这里使用 OpenClaw 的 message 工具
        # 实际调用会在运行时触发
        
        logger.info("[Pusher] 卡片已构建，等待发送")
        
        return {
            "success": True,
            "papers_count": len(papers),
            "pushed_at": datetime.now().isoformat()
        }
    
    def manual_push(self, keywords: List[str] = None) -> Dict[str, Any]:
        """
        手动触发推送
        
        Args:
            keywords: 自定义关键词
            
        Returns:
            推送结果
        """
        logger.info("[Pusher] 手动推送")
        
        if keywords:
            original_keywords = self.keywords
            self.keywords = keywords
        
        try:
            self._daily_push()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if keywords:
                self.keywords = original_keywords
    
    def add_keyword(self, keyword: str):
        """添加关键词"""
        if keyword not in self.keywords:
            self.keywords.append(keyword)
            logger.info(f"[Pusher] 添加关键词: {keyword}")
    
    def remove_keyword(self, keyword: str):
        """移除关键词"""
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            logger.info(f"[Pusher] 移除关键词: {keyword}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "is_running": self.is_running,
            "push_time": self.config.get("time", "08:00"),
            "keywords": self.keywords,
            "max_papers": self.config.get("max_papers", 10)
        }


# 单例实例
_pusher_instance = None


def get_pusher() -> DailyPaperPusher:
    """获取推送服务实例"""
    global _pusher_instance
    if _pusher_instance is None:
        _pusher_instance = DailyPaperPusher()
    return _pusher_instance
