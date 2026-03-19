"""
Google Scholar文献检索子Agent
提供与arXiv并行的文献检索能力
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleScholarSearcher:
    """Google Scholar文献检索子Agent"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_results = config.get('max_results', 50)

    def search(self, keywords: List[str], date_range: str = "last_3_years") -> List[Dict[str, Any]]:
        """执行Google Scholar检索"""
        logger.info(f"Google Scholar检索关键词: {keywords}")

        try:
            from scholarly import scholarly

            # 构建查询字符串
            query = " ".join(keywords)

            # 设置日期范围
            if date_range == "last_3_years":
                start_year = datetime.now().year - 3
            else:
                start_year = 2000

            # 搜索论文
            search_query = scholarly.search_pubs(query)

            papers = []
            for i, pub in enumerate(search_query):
                if i >= self.max_results:
                    break

                # 提取论文信息
                bib = pub.get('bib', {})
                paper = {
                    "title": bib.get('title', ''),
                    "authors": self._parse_authors(bib.get('author', [])),
                    "published": self._parse_year(bib.get('pub_year', '')),
                    "summary": bib.get('abstract', ''),
                    "categories": [],  # Google Scholar不提供分类
                    "doi": bib.get('doi', ''),
                    "arxiv_id": "",
                    "pdf_url": pub.get('eprint_url', ''),
                    "pdf_download_url": pub.get('eprint_url', ''),
                    "source": "google_scholar",
                    "citation_count": pub.get('num_citations', 0),
                    "url": pub.get('pub_url', '')
                }

                # 检查年份是否符合要求
                if paper['published']:
                    try:
                        year = int(paper['published'][:4])
                        if year < start_year:
                            continue
                    except:
                        pass

                papers.append(paper)

            logger.info(f"Google Scholar找到 {len(papers)} 篇论文")
            return papers

        except Exception as e:
            logger.error(f"Google Scholar检索失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_authors(self, authors) -> List[Dict[str, str]]:
        """解析作者列表"""
        if isinstance(authors, str):
            # 如果是字符串，按逗号分割
            author_names = [name.strip() for name in authors.split(',')]
        elif isinstance(authors, list):
            author_names = authors
        else:
            return []

        return [{"name": name, "id": ""} for name in author_names]

    def _parse_year(self, year_str) -> str:
        """解析年份为ISO格式"""
        if not year_str:
            return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            year = int(year_str)
            return f"{year}-01-01T00:00:00Z"
        except:
            return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")


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
            sources: 数据源列表 ['arxiv', 'google_scholar']，默认两者都用

        Returns:
            合并后的论文列表
        """
        if sources is None:
            sources = ['arxiv', 'google_scholar']

        all_papers = []

        # arXiv搜索
        if 'arxiv' in sources:
            from src.agents.sub_agents import ArxivSearcher
            self.arxiv_searcher = ArxivSearcher(self.config)
            arxiv_papers = self.arxiv_searcher.search(keywords, date_range)
            all_papers.extend(arxiv_papers)
            logger.info(f"arXiv检索完成: {len(arxiv_papers)} 篇")

        # Google Scholar搜索
        if 'google_scholar' in sources:
            self.scholar_searcher = GoogleScholarSearcher(self.config)
            scholar_papers = self.scholar_searcher.search(keywords, date_range)
            all_papers.extend(scholar_papers)
            logger.info(f"Google Scholar检索完成: {len(scholar_papers)} 篇")

        # 去重（基于标题相似度）
        unique_papers = self._deduplicate_papers(all_papers)

        logger.info(f"混合检索完成: 共 {len(unique_papers)} 篇唯一论文")
        return unique_papers

    def _deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基于标题相似度去重"""
        seen_titles = {}
        unique_papers = []

        for paper in papers:
            title = paper.get('title', '').lower().strip()

            # 简单去重：完全相同的标题
            if title in seen_titles:
                continue

            seen_titles[title] = True
            unique_papers.append(paper)

        return unique_papers
