"""
知识库模块 - Personal Knowledge Base (RAG)
支持URL、推文、文章的存储和语义搜索
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeBase:
    """
    个人知识库
    
    功能：
    1. 存储URL、推文、文章
    2. 向量化存储（简化版，实际应接入向量数据库）
    3. 语义搜索
    4. 自动分类
    """
    
    def __init__(self, storage_path: str = "knowledge"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 知识库文件
        self.db_file = self.storage_path / "knowledge_db.json"
        self.index_file = self.storage_path / "search_index.json"
        
        # 加载现有数据
        self.knowledge_db = self._load_db()
        self.search_index = self._load_index()
        
    def _load_db(self) -> Dict[str, Any]:
        """加载数据库"""
        if self.db_file.exists():
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"items": [], "metadata": {"total": 0, "created_at": datetime.now().isoformat()}}
    
    def _save_db(self):
        """保存数据库"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_db, f, ensure_ascii=False, indent=2)
    
    def _load_index(self) -> Dict[str, List[str]]:
        """加载搜索索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """保存搜索索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.search_index, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, content: str) -> str:
        """生成唯一ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（实际应使用NLP）
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # 英文停用词
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
            'was', 'one', 'our', 'out', 'has', 'had', 'his', 'how', 'its', 'may',
            'new', 'now', 'old', 'see', 'way', 'who', 'boy', 'did', 'get', 'let',
            'put', 'say', 'she', 'too', 'use'
        }
        
        keywords = [w for w in words if w not in stop_words]
        
        # 统计频率
        from collections import Counter
        word_counts = Counter(keywords)
        
        return [w for w, _ in word_counts.most_common(20)]
    
    def add_url(self, url: str, title: str = None, content: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """
        添加URL到知识库
        
        Args:
            url: 网址
            title: 标题（可选）
            content: 内容（可选）
            tags: 标签（可选）
            
        Returns:
            添加结果
        """
        logger.info(f"[KnowledgeBase] 添加URL: {url}")
        
        # 生成ID
        item_id = self._generate_id(url)
        
        # 检查是否已存在
        if any(item.get("id") == item_id for item in self.knowledge_db["items"]):
            return {"success": False, "message": "URL已存在于知识库"}
        
        # 创建知识条目
        item = {
            "id": item_id,
            "type": "url",
            "url": url,
            "title": title or url,
            "content": content or "",
            "tags": tags or [],
            "keywords": self._extract_keywords(content or url),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 添加到数据库
        self.knowledge_db["items"].append(item)
        self.knowledge_db["metadata"]["total"] += 1
        
        # 更新搜索索引
        for keyword in item["keywords"]:
            if keyword not in self.search_index:
                self.search_index[keyword] = []
            self.search_index[keyword].append(item_id)
        
        # 保存
        self._save_db()
        self._save_index()
        
        logger.info(f"[KnowledgeBase] URL添加成功: {item_id}")
        
        return {
            "success": True,
            "id": item_id,
            "message": "URL已添加到知识库"
        }
    
    def add_article(self, title: str, content: str, source: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """
        添加文章到知识库
        
        Args:
            title: 标题
            content: 内容
            source: 来源（可选）
            tags: 标签（可选）
            
        Returns:
            添加结果
        """
        logger.info(f"[KnowledgeBase] 添加文章: {title}")
        
        # 生成ID
        item_id = self._generate_id(title + content[:100])
        
        # 创建知识条目
        item = {
            "id": item_id,
            "type": "article",
            "title": title,
            "content": content,
            "source": source or "unknown",
            "tags": tags or [],
            "keywords": self._extract_keywords(content),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 添加到数据库
        self.knowledge_db["items"].append(item)
        self.knowledge_db["metadata"]["total"] += 1
        
        # 更新搜索索引
        for keyword in item["keywords"]:
            if keyword not in self.search_index:
                self.search_index[keyword] = []
            self.search_index[keyword].append(item_id)
        
        # 保存
        self._save_db()
        self._save_index()
        
        return {
            "success": True,
            "id": item_id,
            "message": "文章已添加到知识库"
        }
    
    def add_tweet(self, tweet_id: str, author: str, content: str, url: str = None) -> Dict[str, Any]:
        """
        添加推文到知识库
        
        Args:
            tweet_id: 推文ID
            author: 作者
            content: 内容
            url: 推文链接（可选）
            
        Returns:
            添加结果
        """
        logger.info(f"[KnowledgeBase] 添加推文: {tweet_id}")
        
        # 创建知识条目
        item = {
            "id": tweet_id,
            "type": "tweet",
            "author": author,
            "content": content,
            "url": url or f"https://x.com/i/status/{tweet_id}",
            "keywords": self._extract_keywords(content),
            "created_at": datetime.now().isoformat()
        }
        
        # 添加到数据库
        self.knowledge_db["items"].append(item)
        self.knowledge_db["metadata"]["total"] += 1
        
        # 更新搜索索引
        for keyword in item["keywords"]:
            if keyword not in self.search_index:
                self.search_index[keyword] = []
            self.search_index[keyword].append(tweet_id)
        
        # 保存
        self._save_db()
        self._save_index()
        
        return {
            "success": True,
            "id": tweet_id,
            "message": "推文已添加到知识库"
        }
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 搜索查询
            limit: 返回数量限制
            
        Returns:
            搜索结果
        """
        logger.info(f"[KnowledgeBase] 搜索: {query}")
        
        # 提取查询关键词
        query_keywords = self._extract_keywords(query)
        
        # 查找匹配的条目ID
        matched_ids = set()
        for keyword in query_keywords:
            if keyword in self.search_index:
                matched_ids.update(self.search_index[keyword])
        
        # 获取匹配的条目
        results = []
        for item in self.knowledge_db["items"]:
            if item["id"] in matched_ids:
                # 计算相关度分数
                score = sum(1 for kw in query_keywords if kw in item.get("keywords", []))
                results.append({
                    **item,
                    "relevance_score": score
                })
        
        # 排序
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # 限制数量
        return results[:limit]
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """获取指定条目"""
        for item in self.knowledge_db["items"]:
            if item["id"] == item_id:
                return item
        return None
    
    def get_all(self, item_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取所有条目
        
        Args:
            item_type: 类型过滤（url/article/tweet）
            limit: 数量限制
            
        Returns:
            条目列表
        """
        items = self.knowledge_db["items"]
        
        if item_type:
            items = [item for item in items if item.get("type") == item_type]
        
        return items[:limit]
    
    def delete_item(self, item_id: str) -> Dict[str, Any]:
        """删除条目"""
        for i, item in enumerate(self.knowledge_db["items"]):
            if item["id"] == item_id:
                # 从数据库删除
                deleted = self.knowledge_db["items"].pop(i)
                self.knowledge_db["metadata"]["total"] -= 1
                
                # 从搜索索引删除
                for keyword in deleted.get("keywords", []):
                    if keyword in self.search_index and item_id in self.search_index[keyword]:
                        self.search_index[keyword].remove(item_id)
                
                # 保存
                self._save_db()
                self._save_index()
                
                return {"success": True, "message": "条目已删除"}
        
        return {"success": False, "message": "条目不存在"}
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        items = self.knowledge_db["items"]
        
        type_counts = {}
        for item in items:
            item_type = item.get("type", "unknown")
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        return {
            "total": len(items),
            "by_type": type_counts,
            "keywords_count": len(self.search_index),
            "created_at": self.knowledge_db["metadata"].get("created_at"),
            "last_updated": datetime.now().isoformat()
        }
    
    def export_to_json(self, output_path: str = None) -> str:
        """导出为JSON"""
        if output_path is None:
            output_path = str(self.storage_path / "export.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_db, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[KnowledgeBase] 导出完成: {output_path}")
        
        return output_path
