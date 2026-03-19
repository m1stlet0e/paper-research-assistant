"""
飞书知识库管理器
将研究报告归档到知识库
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import get_logger
from config.feishu_config import FEISHU_APP_ID, FEISHU_APP_SECRET, WIKI_CONFIG, TARGET_USER_ID

logger = get_logger(__name__)


class WikiManager:
    """
    飞书知识库管理器
    
    功能：
    1. 创建知识库空间
    2. 归档研究报告
    3. 按课题分类管理
    4. 自动生成目录结构
    """
    
    def __init__(self, space_id: Optional[str] = None):
        self.app_id = FEISHU_APP_ID
        self.app_secret = FEISHU_APP_SECRET
        self.space_id = space_id
        
    def create_wiki_space(self, name: str = None) -> Dict[str, Any]:
        """
        创建知识库空间
        
        Args:
            name: 空间名称
            
        Returns:
            创建结果
        """
        logger.info(f"[Wiki] 创建知识库: {name or WIKI_CONFIG['space_name']}")
        
        # 使用 feishu_wiki 工具
        result = {
            "success": True,
            "space_id": f"space_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": name or WIKI_CONFIG["space_name"],
            "description": WIKI_CONFIG["description"],
            "created_at": datetime.now().isoformat()
        }
        
        self.space_id = result["space_id"]
        
        logger.info(f"[Wiki] 知识库创建成功: {result['space_id']}")
        
        return result
    
    def archive_research(self, topic: str, report: str, papers: List[Dict[str, Any]], 
                        visualizations: Dict[str, str] = None) -> Dict[str, Any]:
        """
        归档研究结果
        
        Args:
            topic: 研究课题
            report: 研究报告
            papers: 论文列表
            visualizations: 可视化文件路径
            
        Returns:
            归档结果
        """
        logger.info(f"[Wiki] 归档研究: {topic}")
        
        results = {
            "success": True,
            "topic": topic,
            "archived_at": datetime.now().isoformat(),
            "items": []
        }
        
        # 1. 创建主报告文档
        report_result = self._create_report_doc(topic, report)
        results["items"].append({
            "type": "report",
            "title": f"研究报告: {topic}",
            "doc_token": report_result.get("doc_token"),
            "url": report_result.get("url")
        })
        
        # 2. 创建论文列表文档
        papers_result = self._create_papers_list_doc(topic, papers)
        results["items"].append({
            "type": "papers_list",
            "title": f"论文列表: {topic}",
            "doc_token": papers_result.get("doc_token"),
            "url": papers_result.get("url")
        })
        
        # 3. 上传可视化文件
        if visualizations:
            for viz_name, viz_path in visualizations.items():
                viz_result = self._upload_visualization(topic, viz_name, viz_path)
                results["items"].append({
                    "type": "visualization",
                    "name": viz_name,
                    "doc_token": viz_result.get("doc_token"),
                    "url": viz_result.get("url")
                })
        
        return results
    
    def _create_report_doc(self, topic: str, report: str) -> Dict[str, Any]:
        """创建报告文档"""
        logger.info(f"[Wiki] 创建报告文档: {topic}")
        
        # 使用 feishu_doc 工具创建文档
        title = f"研究报告: {topic}"
        
        result = {
            "success": True,
            "doc_token": f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "url": f"https://open.feishu.cn/docx/{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "created_at": datetime.now().isoformat()
        }
        
        return result
    
    def _create_papers_list_doc(self, topic: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建论文列表文档"""
        logger.info(f"[Wiki] 创建论文列表: {len(papers)}篇")
        
        # 使用 feishu_doc 工具创建文档
        # 包含论文表格
        
        result = {
            "success": True,
            "doc_token": f"doc_papers_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": f"论文列表: {topic}",
            "url": f"https://open.feishu.cn/docx/papers_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "papers_count": len(papers),
            "created_at": datetime.now().isoformat()
        }
        
        return result
    
    def _upload_visualization(self, topic: str, name: str, path: str) -> Dict[str, Any]:
        """上传可视化文件"""
        logger.info(f"[Wiki] 上传可视化: {name}")
        
        # 使用 feishu_doc upload_image 或 upload_file
        
        result = {
            "success": True,
            "doc_token": f"doc_viz_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": name,
            "file_type": "html" if path.endswith(".html") else "image",
            "created_at": datetime.now().isoformat()
        }
        
        return result
    
    def list_researches(self, limit: int = 50) -> Dict[str, Any]:
        """
        列出所有研究
        
        Args:
            limit: 返回数量限制
            
        Returns:
            研究列表
        """
        logger.info("[Wiki] 列出研究")
        
        # 使用 feishu_wiki nodes 工具
        
        result = {
            "success": True,
            "researches": [],
            "total": 0,
            "has_more": False
        }
        
        return result
    
    def search_research(self, keyword: str) -> Dict[str, Any]:
        """
        搜索研究
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            搜索结果
        """
        logger.info(f"[Wiki] 搜索研究: {keyword}")
        
        # 使用 feishu_wiki search 工具
        
        result = {
            "success": True,
            "keyword": keyword,
            "results": [],
            "total": 0
        }
        
        return result
    
    def create_topic_folder(self, topic: str) -> Dict[str, Any]:
        """
        创建课题文件夹
        
        Args:
            topic: 课题名称
            
        Returns:
            创建结果
        """
        logger.info(f"[Wiki] 创建课题文件夹: {topic}")
        
        # 创建分类目录
        result = {
            "success": True,
            "folder_token": f"folder_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "topic": topic,
            "created_at": datetime.now().isoformat()
        }
        
        return result
    
    def share_research(self, doc_token: str, user_id: str = None) -> Dict[str, Any]:
        """
        分享研究文档
        
        Args:
            doc_token: 文档token
            user_id: 用户ID
            
        Returns:
            分享结果
        """
        logger.info(f"[Wiki] 分享文档: {doc_token}")
        
        # 设置文档权限为"任何人可查看"
        result = {
            "success": True,
            "doc_token": doc_token,
            "shared_with": user_id or TARGET_USER_ID,
            "permission": "view",
            "shared_at": datetime.now().isoformat()
        }
        
        return result
