"""
数据持久化模块
支持论文数据的保存、加载、导入、导出和缓存
"""

import os
import json
import csv
import pickle
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib
import threading
import time
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataPersistence:
    """
    数据持久化管理器
    
    功能：
    1. 论文数据持久化存储
    2. 缓存机制（避免重复检索）
    3. 导入/导出（JSON、CSV、BibTeX）
    4. 数据版本管理
    """
    
    def __init__(self, base_dir: str = "output/data"):
        """
        初始化持久化管理器
        
        Args:
            base_dir: 数据存储基础目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 子目录
        self.papers_dir = self.base_dir / "papers"
        self.cache_dir = self.base_dir / "cache"
        self.exports_dir = self.base_dir / "exports"
        
        # 创建子目录
        self.papers_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.exports_dir.mkdir(exist_ok=True)
        
        # 内存缓存
        self._memory_cache: Dict[str, Any] = {}
        self._cache_lock = threading.Lock()
        
        # 缓存有效期（秒）
        self.cache_ttl = 3600 * 24 * 7  # 7天
        
        logger.info(f"[Persistence] 初始化完成，数据目录: {self.base_dir}")
    
    # ==================== 论文数据存储 ====================
    
    def save_papers(self, papers: List[Dict[str, Any]], topic: str, 
                    metadata: Dict[str, Any] = None) -> str:
        """
        保存论文数据
        
        Args:
            papers: 论文列表
            topic: 研究课题
            metadata: 元数据
            
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"papers_{self._safe_filename(topic)}_{timestamp}.json"
        filepath = self.papers_dir / filename
        
        # 构建保存数据
        data = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "papers_count": len(papers),
            "papers": papers,
            "metadata": metadata or {}
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[Persistence] 保存论文数据: {filepath} ({len(papers)}篇)")
        
        # 更新内存缓存
        cache_key = self._get_cache_key(topic)
        with self._cache_lock:
            self._memory_cache[cache_key] = {
                "data": data,
                "timestamp": time.time()
            }
        
        # 同时保存为最新数据（方便快速加载）
        latest_path = self.papers_dir / "papers_latest.json"
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def load_papers(self, topic: str = None, latest: bool = True) -> Optional[Dict[str, Any]]:
        """
        加载论文数据
        
        Args:
            topic: 研究课题（可选）
            latest: 是否加载最新数据
            
        Returns:
            论文数据
        """
        # 尝试从内存缓存加载
        if topic:
            cache_key = self._get_cache_key(topic)
            with self._cache_lock:
                if cache_key in self._memory_cache:
                    cached = self._memory_cache[cache_key]
                    if time.time() - cached["timestamp"] < self.cache_ttl:
                        logger.info(f"[Persistence] 从内存缓存加载: {topic}")
                        return cached["data"]
        
        # 从文件加载
        if latest:
            filepath = self.papers_dir / "papers_latest.json"
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"[Persistence] 加载最新论文数据: {len(data.get('papers', []))}篇")
                    return data
        
        # 查找特定主题的文件
        if topic:
            safe_name = self._safe_filename(topic)
            files = list(self.papers_dir.glob(f"papers_{safe_name}_*.json"))
            if files:
                # 按时间排序，选择最新的
                latest_file = max(files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"[Persistence] 加载论文数据: {latest_file}")
                    return data
        
        logger.warning(f"[Persistence] 未找到论文数据")
        return None
    
    def list_saved_papers(self) -> List[Dict[str, Any]]:
        """
        列出所有保存的论文数据
        
        Returns:
            文件列表
        """
        files = list(self.papers_dir.glob("papers_*.json"))
        
        result = []
        for f in files:
            if f.name == "papers_latest.json":
                continue
            
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    result.append({
                        "filename": f.name,
                        "topic": data.get("topic", "未知"),
                        "papers_count": data.get("papers_count", 0),
                        "timestamp": data.get("timestamp", ""),
                        "size": f.stat().st_size
                    })
            except Exception as e:
                logger.error(f"[Persistence] 读取文件失败 {f}: {e}")
        
        # 按时间排序
        result.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return result
    
    # ==================== 缓存机制 ====================
    
    def get_cache(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存数据
        """
        # 检查内存缓存
        with self._cache_lock:
            if key in self._memory_cache:
                cached = self._memory_cache[key]
                if time.time() - cached["timestamp"] < self.cache_ttl:
                    return cached["data"]
        
        # 检查文件缓存
        cache_file = self.cache_dir / f"{self._safe_filename(key)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if time.time() - data.get("timestamp", 0) < self.cache_ttl:
                        # 更新内存缓存
                        with self._cache_lock:
                            self._memory_cache[key] = data
                        return data.get("data")
            except Exception as e:
                logger.error(f"[Persistence] 读取缓存失败: {e}")
        
        return None
    
    def set_cache(self, key: str, data: Any, ttl: int = None) -> None:
        """
        设置缓存
        
        Args:
            key: 缓存键
            data: 缓存数据
            ttl: 有效期（秒）
        """
        cache_data = {
            "data": data,
            "timestamp": time.time(),
            "ttl": ttl or self.cache_ttl
        }
        
        # 更新内存缓存
        with self._cache_lock:
            self._memory_cache[key] = cache_data
        
        # 更新文件缓存
        cache_file = self.cache_dir / f"{self._safe_filename(key)}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[Persistence] 写入缓存失败: {e}")
    
    def clear_cache(self, key: str = None) -> None:
        """
        清除缓存
        
        Args:
            key: 缓存键（None表示清除所有）
        """
        if key:
            # 清除特定缓存
            with self._cache_lock:
                self._memory_cache.pop(key, None)
            
            cache_file = self.cache_dir / f"{self._safe_filename(key)}.json"
            if cache_file.exists():
                cache_file.unlink()
        else:
            # 清除所有缓存
            with self._cache_lock:
                self._memory_cache.clear()
            
            for f in self.cache_dir.glob("*.json"):
                f.unlink()
        
        logger.info(f"[Persistence] 清除缓存: {key or '全部'}")
    
    # ==================== 导入/导出 ====================
    
    def export_to_json(self, papers: List[Dict[str, Any]], 
                       filename: str = None) -> str:
        """
        导出为JSON文件
        
        Args:
            papers: 论文列表
            filename: 文件名
            
        Returns:
            导出文件路径
        """
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.exports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[Persistence] 导出JSON: {filepath}")
        return str(filepath)
    
    def export_to_csv(self, papers: List[Dict[str, Any]], 
                      filename: str = None) -> str:
        """
        导出为CSV文件
        
        Args:
            papers: 论文列表
            filename: 文件名
            
        Returns:
            导出文件路径
        """
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.exports_dir / filename
        
        # 提取字段
        fieldnames = [
            "title", "authors", "published", "summary", 
            "arxiv_id", "pdf_url", "categories"
        ]
        
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for paper in papers:
                # 处理作者字段
                row = paper.copy()
                if isinstance(row.get("authors"), list):
                    authors = []
                    for author in row["authors"]:
                        if isinstance(author, dict):
                            authors.append(author.get("name", ""))
                        else:
                            authors.append(str(author))
                    row["authors"] = "; ".join(authors)
                
                # 处理分类字段
                if isinstance(row.get("categories"), list):
                    categories = [c.get("term", "") if isinstance(c, dict) else str(c) 
                                 for c in row["categories"]]
                    row["categories"] = "; ".join(categories)
                
                writer.writerow(row)
        
        logger.info(f"[Persistence] 导出CSV: {filepath}")
        return str(filepath)
    
    def export_to_bibtex(self, papers: List[Dict[str, Any]], 
                         filename: str = None) -> str:
        """
        导出为BibTeX格式
        
        Args:
            papers: 论文列表
            filename: 文件名
            
        Returns:
            导出文件路径
        """
        if not filename:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bib"
        
        filepath = self.exports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, paper in enumerate(papers, 1):
                # 生成引用键
                arxiv_id = paper.get("arxiv_id", f"unknown{i}")
                cite_key = f"arxiv_{arxiv_id.replace('/', '_')}"
                
                # 提取作者
                authors = []
                for author in paper.get("authors", []):
                    if isinstance(author, dict):
                        authors.append(author.get("name", ""))
                    else:
                        authors.append(str(author))
                authors_str = " and ".join(authors) if authors else "Unknown"
                
                # 提取年份
                year = paper.get("published", "")[:4] if paper.get("published") else "2024"
                
                # 写入BibTeX条目
                f.write(f"@article{{{cite_key},\n")
                f.write(f"  title = {{{paper.get('title', 'Unknown')}}},\n")
                f.write(f"  author = {{{authors_str}}},\n")
                f.write(f"  year = {{{year}}},\n")
                f.write(f"  eprint = {{{arxiv_id}}},\n")
                f.write(f"  archiveprefix = {{arXiv}},\n")
                f.write(f"  url = {{https://arxiv.org/abs/{arxiv_id}}},\n")
                f.write("}\n\n")
        
        logger.info(f"[Persistence] 导出BibTeX: {filepath}")
        return str(filepath)
    
    def import_from_json(self, filepath: str) -> List[Dict[str, Any]]:
        """
        从JSON文件导入
        
        Args:
            filepath: 文件路径
            
        Returns:
            论文列表
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持两种格式
        if isinstance(data, list):
            papers = data
        elif isinstance(data, dict) and "papers" in data:
            papers = data["papers"]
        else:
            papers = [data]
        
        logger.info(f"[Persistence] 导入JSON: {filepath} ({len(papers)}篇)")
        return papers
    
    # ==================== 辅助方法 ====================
    
    def _safe_filename(self, name: str) -> str:
        """生成安全的文件名"""
        # 移除不安全字符
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
        # 限制长度
        return safe[:100]
    
    def _get_cache_key(self, topic: str) -> str:
        """生成缓存键"""
        return hashlib.md5(topic.encode()).hexdigest()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        papers_files = list(self.papers_dir.glob("papers_*.json"))
        cache_files = list(self.cache_dir.glob("*.json"))
        
        total_size = sum(f.stat().st_size for f in papers_files)
        
        return {
            "papers_files": len(papers_files),
            "cache_files": len(cache_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "memory_cache_items": len(self._memory_cache),
            "base_dir": str(self.base_dir)
        }


# 单例实例
_persistence_instance: Optional[DataPersistence] = None


def get_persistence() -> DataPersistence:
    """获取持久化管理器单例"""
    global _persistence_instance
    if _persistence_instance is None:
        _persistence_instance = DataPersistence()
    return _persistence_instance
