"""
Google Scholar文献检索模块
提供与arXiv并行的文献检索能力
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import requests
import time


class GoogleScholarSearcher:
    """Google Scholar文献检索器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_results = config.get('max_results', 50)
        self.base_url = "https://scholar.google.com/scholar"
    
    def search(self, keywords: List[str], date_range: str = "last_3_years") -> List[Dict[str, Any]]:
        """
        执行Google Scholar检索
        
        Args:
            keywords: 关键词列表
            date_range: 日期范围
            
        Returns:
            论文列表
        """
        try:
            # 使用SerpAPI或其他Google Scholar API
            # 这里使用模拟数据演示
            query = " ".join(keywords)
            
            # 构建查询参数
            params = {
                'q': query,
                'num': self.max_results,
                'sort': 'date'  # 按日期排序
            }
            
            # 模拟返回结果
            papers = self._mock_search(query, date_range)
            
            return papers
            
        except Exception as e:
            print(f"Google Scholar检索失败: {e}")
            return []
    
    def _mock_search(self, query: str, date_range: str) -> List[Dict[str, Any]]:
        """模拟搜索结果（实际项目中应使用真实API）"""
        # 返回模拟数据
        return [
            {
                'title': f'Google Scholar: {query} - Paper 1',
                'authors': [{'name': 'Author A'}, {'name': 'Author B'}],
                'published': '2024-01-15T00:00:00Z',
                'summary': f'Summary of {query} research paper 1',
                'categories': ['cs.AI', 'cs.LG'],
                'arxiv_id': '',
                'pdf_url': '',
                'source': 'google_scholar'
            },
            {
                'title': f'Google Scholar: {query} - Paper 2',
                'authors': [{'name': 'Author C'}],
                'published': '2023-12-20T00:00:00Z',
                'summary': f'Summary of {query} research paper 2',
                'categories': ['cs.CL'],
                'arxiv_id': '',
                'pdf_url': '',
                'source': 'google_scholar'
            }
        ]


class HybridSearcher:
    """混合搜索器：同时使用arXiv和Google Scholar"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.arxiv_searcher = None
        self.scholar_searcher = None
    
    def search(self, keywords: List[str], date_range: str = "last_3_years",
               sources: List[str] = None) -> List[Dict[str, Any]]:
        """
        执行混合检索
        
        Args:
            keywords: 关键词列表
            date_range: 日期范围
            sources: 数据源列表 ['arxiv', 'google_scholar']
            
        Returns:
            合并后的论文列表
        """
        if sources is None:
            sources = ['arxiv']
        
        all_papers = []
        
        # arXiv搜索
        if 'arxiv' in sources:
            from .arxiv_searcher import ArxivSearcher
            self.arxiv_searcher = ArxivSearcher(self.config)
            arxiv_papers = self.arxiv_searcher.search(keywords, date_range)
            all_papers.extend(arxiv_papers)
        
        # Google Scholar搜索
        if 'google_scholar' in sources:
            self.scholar_searcher = GoogleScholarSearcher(self.config)
            scholar_papers = self.scholar_searcher.search(keywords, date_range)
            all_papers.extend(scholar_papers)
        
        # 去重
        unique_papers = self._deduplicate_papers(all_papers)
        
        return unique_papers
    
    def _deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基于标题相似度去重"""
        seen_titles = {}
        unique_papers = []
        
        for paper in papers:
            title = paper.get('title', '').lower().strip()
            
            if title in seen_titles:
                continue
            
            seen_titles[title] = True
            unique_papers.append(paper)
        
        return unique_papers
