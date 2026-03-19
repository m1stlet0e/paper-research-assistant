"""
子Agent实现
"""

import feedparser
import re
import urllib.parse
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ArxivSearcher:
    """arXiv文献检索子Agent"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = "https://export.arxiv.org/api/query"
        self.max_results = config.get('max_results', 50)

    def search(self, keywords: List[str], date_range: str = "last_3_years") -> List[Dict[str, Any]]:
        """执行arXiv检索"""
        logger.info(f"arXiv检索关键词: {keywords}")

        # 构建查询字符串（arXiv语法）
        # 使用 all: 搜索所有字段（标题、摘要、作者等）
        if keywords and len(keywords) > 0:
            # 将关键词用OR连接，扩大搜索范围
            keyword_query = " OR ".join([f'all:{kw}' for kw in keywords])
            query = f"({keyword_query})"
        else:
            query = "all"
        
        logger.info(f"arXiv查询: {query}")

        # URL编码
        query = urllib.parse.quote(query)

        # 构建请求URL
        url = f"{self.base_url}?search_query={query}&start=0&max_results={self.max_results}&sortBy=relevance&sortOrder=descending"

        logger.info(f"请求URL: {url}")

        # 发送请求
        try:
            feed = feedparser.parse(url)
            logger.info(f"找到 {len(feed.entries)} 篇论文")

            # 解析论文
            papers = []
            for entry in feed.entries:
                paper = self._parse_entry(entry)
                papers.append(paper)

            return papers

        except Exception as e:
            logger.error(f"arXiv检索失败: {e}")
            return []


    def _parse_entry(self, entry) -> Dict[str, Any]:
        """解析arXiv条目"""
        published = entry.published

        # 提取arXiv ID
        arxiv_id = None
        for link in entry.links:
            if 'id' in link:
                arxiv_id = link['id'].split('/')[-1]
                break

        # 提取PDF链接
        pdf_url = None
        for link in entry.links:
            if link.get('type') == 'application/pdf':
                pdf_url = link.href
                break

        # 提取分类
        categories = []
        if hasattr(entry, 'categories') and entry.categories:
            for category in entry.categories:
                categories.append({
                    'term': category.term,
                    'scheme': category.scheme
                })

        # 提取作者
        authors = []
        for author in entry.authors:
            authors.append({
                'name': author.name,
                'id': author.get('id', '')
            })

        return {
            "title": entry.title,
            "authors": authors,
            "published": published,
            "summary": entry.summary,
            "categories": categories,
            "doi": entry.get('doi', ''),
            "arxiv_id": arxiv_id,
            "pdf_url": pdf_url,
            "pdf_download_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else "",
            "source": "arxiv"
        }


class CitationAnalyzer:
    """引用分析Agent"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def analyze_citations(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析论文引用关系"""
        logger.info("开始引用分析...")

        # 1. 构建引用网络
        citation_network = self._build_citation_network(papers)

        # 2. 识别高被引论文
        top_cited = self._identify_top_cited(papers, top_n=10)

        # 3. 识别引用簇
        citation_clusters = self._identify_clusters(citation_network)

        # 4. 识别研究趋势
        research_trends = self._identify_trends(papers)

        # 5. 识别研究空白
        research_gaps = self._identify_gaps(papers)

        result = {
            "citation_network": citation_network,
            "top_cited": top_cited,
            "citation_clusters": citation_clusters,
            "research_trends": research_trends,
            "research_gaps": research_gaps
        }

        logger.info(f"引用分析完成: {len(papers)}篇论文")
        return result


    def _build_citation_network(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建引用网络"""
        # 提取唯一的作者
        unique_authors = set()
        categories_list = []

        for paper in papers:
            # 提取作者
            if paper.get("authors"):
                for author in paper["authors"]:
                    if isinstance(author, dict):
                        author_name = author.get("name", "")
                        if author_name:
                            unique_authors.add(author_name)
                    elif isinstance(author, str):
                        unique_authors.add(author)

            # 提取类别
            if paper.get("categories"):
                for category in paper["categories"]:
                    categories_list.append(category)

        # 统计引用次数（简化版：基于arXiv ID去重）
        citation_count = {}
        for paper in papers:
            arxiv_id = paper["arxiv_id"]
            citation_count[arxiv_id] = citation_count.get(arxiv_id, 0) + 1

        network = {
            "nodes": [],
            "edges": [],
            "statistics": {
                "total_nodes": len(papers),
                "total_edges": 0,
                "avg_citations": 0,
                "unique_authors": len(unique_authors),
                "categories": len(categories_list)
            }
        }

        # 为每篇论文分配节点ID
        for idx, paper in enumerate(papers):
            node_id = str(idx)
            network["nodes"].append({
                "id": node_id,
                "paper_id": paper["arxiv_id"],
                "title": paper["title"],
                "citations": 0,
                "authors": paper["authors"],
                "published": paper["published"]
            })

        # 更新节点引用次数
        for node in network["nodes"]:
            node["citations"] = citation_count.get(node["paper_id"], 0)

        # 统计边
        network["statistics"]["total_edges"] = len(papers)  # 每篇论文都有引用
        network["statistics"]["avg_citations"] = sum(node["citations"] for node in network["nodes"]) / len(network["nodes"])

        # 计算PageRank
        network["pagerank"] = self._calculate_pagerank(papers)

        return network

    def _calculate_pagerank(self, papers: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算论文的PageRank引用影响力"""
        import networkx as nx

        # 创建有向图
        G = nx.DiGraph()

        # 添加节点
        for paper in papers:
            paper_id = paper.get('arxiv_id') or paper.get('title', '')
            G.add_node(paper_id, title=paper.get('title', ''))

        # 添加边（简化版：同一作者的文章相互引用）
        author_papers = {}
        for i, paper in enumerate(papers):
            authors = paper.get('authors', [])
            paper_id = paper.get('arxiv_id') or f"paper_{i}"

            for author in authors:
                author_name = author.get('name', '') if isinstance(author, dict) else author
                if author_name:
                    if author_name not in author_papers:
                        author_papers[author_name] = []
                    author_papers[author_name].append(paper_id)

        # 同一作者的论文相互引用
        for author_name, paper_list in author_papers.items():
            for i in range(len(paper_list)):
                for j in range(i+1, len(paper_list)):
                    G.add_edge(paper_list[i], paper_list[j])

        # 计算PageRank
        try:
            pagerank = nx.pagerank(G, alpha=0.85)
        except:
            pagerank = {}

        return pagerank


    def _identify_top_cited(self, papers: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """识别高被引论文"""
        # 按引用次数排序
        sorted_papers = sorted(papers, key=lambda x: x.get("citation_count", 0), reverse=True)

        # 返回前N篇
        return sorted_papers[:top_n]


    def _identify_clusters(self, network: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别引用簇"""
        # 简化版：基于作者合作识别簇
        author_collaborations = {}

        for edge in network["edges"]:
            # 简化处理：每篇论文作为一个簇
            pass

        # 返回簇列表
        return {
            "method": "author_collaboration",
            "clusters": network["nodes"][:5]  # 返回前5个作为示例
        }


    def _identify_trends(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """识别研究趋势"""
        # 按年份统计
        year_counts = {}
        for paper in papers:
            year = paper["published"][:4]
            year_counts[year] = year_counts.get(year, 0) + 1

        # 返回趋势
        return {
            "method": "yearly_analysis",
            "trends": [
                {"year": year, "count": count}
                for year, count in sorted(year_counts.items())
            ]
        }


    def _identify_gaps(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别研究空白"""
        # 简化版：识别未被充分研究的问题
        # 实际实现需要NLP分析

        gaps = []

        # 分析论文摘要，提取研究问题
        for paper in papers:
            # 简化处理：每篇论文代表一个研究空白
            gaps.append({
                "paper_id": paper["arxiv_id"],
                "paper_title": paper["title"],
                "gap_type": "research_opportunity",
                "description": f"在{paper['published'][:4]}年研究了{paper['title'][:50]}...",
                "relevance": "high"
            })

        return gaps


class PDFParser:
    """PDF解析Agent"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def parse_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析论文"""
        logger.info(f"开始解析 {len(papers)} 篇论文...")

        parsed_papers = []
        for paper in papers:
            parsed_paper = self._parse_single_paper(paper)
            parsed_papers.append(parsed_paper)

        logger.info(f"解析完成: {len(parsed_papers)} 篇论文")
        return parsed_papers


    def _parse_single_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """解析单篇论文"""
        try:
            # 1. 提取元数据
            extracted = {
                **paper,
                "extracted_fields": {
                    "title": paper["title"],
                    "authors": paper["authors"],
                    "abstract": paper["summary"],
                    "published_date": paper["published"],
                    "categories": paper["categories"],
                    "doi": paper["doi"],
                    "arxiv_id": paper["arxiv_id"],
                    "pdf_url": paper["pdf_url"],
                    "pdf_download_url": paper.get("pdf_download_url", "")
                }
            }

            # 2. 提取关键词
            keywords = self._extract_keywords(paper["summary"])
            extracted["extracted_fields"]["keywords"] = keywords

            # 3. 提取研究方法
            methods = self._extract_methods(paper["summary"])
            extracted["extracted_fields"]["methods"] = methods

            # 4. 提取实验设置
            settings = self._extract_settings(paper["summary"])
            extracted["extracted_fields"]["settings"] = settings

            # 5. 提取关键发现
            findings = self._extract_findings(paper["summary"])
            extracted["extracted_fields"]["findings"] = findings

            # 6. 提取局限性
            limitations = self._extract_limitations(paper["summary"])
            extracted["extracted_fields"]["limitations"] = limitations

            # 7. 生成摘要
            summary = self._generate_summary(paper)
            extracted["extracted_fields"]["summary"] = summary

            return extracted

        except Exception as e:
            logger.error(f"解析论文失败: {e}")
            return paper


    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简化版：提取常见技术关键词
        common_keywords = [
            "deep learning", "machine learning", "neural network", "artificial intelligence",
            "transformer", "BERT", "GPT", "attention", "convolutional neural network",
            "reinforcement learning", "unsupervised learning", "supervised learning"
        ]

        text_lower = text.lower()
        keywords = [kw for kw in common_keywords if kw in text_lower]

        return keywords[:10]  # 最多返回10个


    def _extract_methods(self, text: str) -> List[str]:
        """提取研究方法"""
        methods = []

        if "deep learning" in text.lower():
            methods.append("deep learning")
        if "machine learning" in text.lower():
            methods.append("machine learning")
        if "neural network" in text.lower():
            methods.append("neural network")
        if "transformer" in text.lower():
            methods.append("transformer architecture")
        if "reinforcement learning" in text.lower():
            methods.append("reinforcement learning")

        return methods


    def _extract_settings(self, text: str) -> List[str]:
        """提取实验设置"""
        settings = []

        # 简化版：从文本中提取可能的设置
        if "dataset" in text.lower():
            settings.append("dataset")
        if "experiments" in text.lower():
            settings.append("experiments")
        if "evaluation" in text.lower():
            settings.append("evaluation")
        if "training" in text.lower():
            settings.append("training")

        return settings


    def _extract_findings(self, text: str) -> List[str]:
        """提取关键发现"""
        findings = []

        # 简化版：从文本中提取可能的发现
        if "improved" in text.lower() or "better" in text.lower():
            findings.append("性能提升")
        if "achieved" in text.lower() or "reached" in text.lower():
            findings.append("达到新水平")
        if "outperformed" in text.lower():
            findings.append("超越基线")
        if "proved" in text.lower() or "demonstrated" in text.lower():
            findings.append("验证了假设")

        return findings


    def _extract_limitations(self, text: str) -> List[str]:
        """提取局限性"""
        limitations = []

        # 简化版：从文本中提取可能的局限性
        if "limitations" in text.lower() or "limitation" in text.lower():
            limitations.append("论文明确指出了局限性")
        if "future work" in text.lower():
            limitations.append("未来工作方向")
        if "future research" in text.lower():
            limitations.append("未来研究方向")

        return limitations


    def _generate_summary(self, paper: Dict[str, Any]) -> str:
        """生成论文摘要"""
        # 简化版：使用论文摘要
        summary = paper.get("summary", "无摘要")
        return summary[:500] + "..." if len(summary) > 500 else summary


class ReviewWriter:
    """综述撰写Agent - 生成文献综述"""

    def __init__(self):
        self.logger = logger
    
    def write_review(self, papers: List[Dict[str, Any]], citations: List[str]) -> Dict[str, Any]:
        """撰写文献综述"""
        self.logger.info(f"开始撰写综述: {len(papers)}篇论文")

        # 提取基本信息和时间分布
        unique_authors = set()
        categories_list = []

        for paper in papers:
            if paper.get("authors"):
                for author in paper["authors"]:
                    if isinstance(author, dict):
                        author_name = author.get("name", "")
                        if author_name:
                            unique_authors.add(author_name)
                    elif isinstance(author, str):
                        unique_authors.add(author)

            if paper.get("categories"):
                for category in paper["categories"]:
                    categories_list.append(category)

        # 计算最早和最新发表日期
        published_dates = []
        for paper in papers:
            if paper.get("published"):
                published_dates.append(paper["published"])

        earliest_date = min(published_dates) if published_dates else "N/A"
        latest_date = max(published_dates) if published_dates else "N/A"

        # 生成综述内容
        sections = [
            {
                "title": "研究背景",
                "content": self._generate_background(papers)
            },
            {
                "title": "主要发现",
                "content": self._generate_findings(papers)
            },
            {
                "title": "研究趋势",
                "content": self._generate_trends(papers)
            }
        ]

        review = {
            "title": f"文献综述：{papers[0].get('title', 'AI论文研究')}",
            "sections": sections,
            "citations": citations,
            "statistics": {
                "unique_authors": len(unique_authors),
                "categories": len(categories_list),
                "earliest_date": earliest_date,
                "latest_date": latest_date
            }
        }

        self.logger.info(f"综述撰写完成: {len(sections)}个章节")
        return review
    
    def _generate_background(self, papers: List[Dict[str, Any]]) -> str:
        """生成研究背景"""
        if not papers:
            return "暂无相关论文数据。"
        
        # 提取第一篇论文的标题作为主题参考
        first_paper_title = papers[0].get("title", "AI研究")
        
        # 统计论文数量和时间范围
        published_dates = [p.get("published", "") for p in papers if p.get("published")]
        if published_dates:
            years = set([d[:4] for d in published_dates])
            year_range = f"{min(years)}-{max(years)}" if len(years) > 1 else list(years)[0]
        else:
            year_range = "近年"
        
        # 提取主要研究主题
        topics = set()
        for paper in papers[:10]:
            title = paper.get("title", "")
            # 提取标题中的关键词
            words = title.split()[:5]
            for word in words:
                if len(word) > 3:
                    topics.add(word)
        
        topics_str = "、".join(list(topics)[:5]) if topics else "AI技术"
        
        background = f"""本研究综述分析了{len(papers)}篇相关文献，时间跨度为{year_range}。

研究主题涵盖：{topics_str}等领域。

通过系统性分析arXiv上的最新研究成果，本综述旨在为研究者提供全面的技术概览和研究方向指引。

主要研究问题包括：
- 当前技术的最新进展是什么？
- 主流方法有哪些？各自的优缺点？
- 存在哪些研究空白和未来方向？"""
        
        return background
    
    def _generate_findings(self, papers: List[Dict[str, Any]]) -> str:
        """生成主要发现"""
        findings = []
        
        # 提取每篇论文的关键信息
        for i, paper in enumerate(papers[:10], 1):
            title = paper.get("title", "未知标题")
            authors = []
            if "authors" in paper:
                authors = paper["authors"]
            elif "extracted_fields" in paper and "authors" in paper["extracted_fields"]:
                authors = paper["extracted_fields"]["authors"]
            
            author_names = []
            for author in authors[:3]:
                if isinstance(author, dict):
                    author_names.append(author.get("name", "未知"))
                elif isinstance(author, str):
                    author_names.append(author)
            
            authors_str = ", ".join(author_names[:3]) if author_names else "未知作者"
            
            findings.append(f"{i}. {title}")
            findings.append(f"   作者: {authors_str}")
        
        return "\n".join(findings)
    
    def _generate_trends(self, papers: List[Dict[str, Any]]) -> str:
        """生成研究趋势"""
        # 统计年份分布
        year_counts = {}
        for paper in papers:
            if paper.get("published"):
                year = paper["published"][:4]
                year_counts[year] = year_counts.get(year, 0) + 1
        
        years_sorted = sorted(year_counts.items())
        
        # 提取研究热点
        keywords = {}
        for paper in papers:
            title = paper.get("title", "").lower()
            summary = paper.get("summary", "").lower()
            text = title + " " + summary
            
            # 提取常见关键词
            common_terms = [
                "agent", "ai", "model", "learning", "neural", "deep",
                "transformer", "reinforcement", "multi-agent", "autonomous",
                "workflow", "automation", "llm", "gpt", "bert"
            ]
            
            for term in common_terms:
                if term in text:
                    keywords[term] = keywords.get(term, 0) + 1
        
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]
        
        trends = "### 技术演进\n"
        for year, count in years_sorted:
            trends += f"- **{year}年**：发表{count}篇相关论文\n"
        
        trends += "\n### 研究热点\n"
        for i, (keyword, count) in enumerate(top_keywords, 1):
            trends += f"{i}. **{keyword}**：在{count}篇论文中出现\n"
        
        trends += "\n### 研究空白\n"
        trends += "- 跨领域应用的深入探索\n"
        trends += "- 实际部署中的性能优化\n"
        trends += "- 长期运行的可扩展性验证\n"
        trends += "- 多Agent协作的标准化框架"
        
        return trends
        return paper["summary"][:500] + "..." if len(paper["summary"]) > 500 else paper["summary"]
