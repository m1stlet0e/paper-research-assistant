"""
报告生成器
"""

from typing import List, Dict, Any
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, topic: str, papers: List[Dict[str, Any]], review: Dict[str, Any]) -> str:
        """生成研究报告"""
        logger.info("生成研究报告")

        try:
            report = self._generate_markdown_report(topic, papers, review)
            logger.info("报告生成成功")
            return report
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回一个简单的错误报告
            return f"""# AI论文全自动预研助手 - 错误报告

## 错误信息

生成报告时出错: {e}

## 研究信息

**研究课题：** {topic}

**完成时间：** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**论文总数：** {len(papers)} 篇

---
"""

    def _generate_markdown_report(self, topic: str, papers: List[Dict[str, Any]], review: Dict[str, Any]) -> str:
        """生成Markdown格式报告"""
        # 处理review为None的情况
        if review is None:
            review = {
                "sections": [],
                "citations": [],
                "statistics": {}
            }

        logger.info(f"_generate_markdown_report: review类型={type(review)}")
        logger.info(f"_generate_markdown_report: sections={review.get('sections', [])}")
        logger.info(f"_generate_markdown_report: citations={review.get('citations', [])}")

        report = f"""# AI论文全自动预研助手 - 研究报告

## 📋 研究信息

**研究课题：** {topic}

**完成时间：** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**论文总数：** {len(papers)} 篇

---

## 📊 研究统计

### 基本信息
- **作者数量：** {review.get('statistics', {}).get('unique_authors', 0)} 位
- **研究领域：** {review.get('statistics', {}).get('categories', 0)} 个
- **检索来源：** arXiv

### 时间分布
- **最早发表：** {review.get('statistics', {}).get('earliest_date', 'N/A')}
- **最新发表：** {review.get('statistics', {}).get('latest_date', 'N/A')}

---

## 📖 文献综述

{self._format_sections(review['sections'])}

---

## 📚 参考文献列表

{self._format_citations(review['citations'])}

---

## 💡 核心发现

{self._format_findings(papers)}

---

## 🎯 研究建议

基于以上分析，建议：

1. **重点关注：** {topic}
2. **推荐阅读：** 前10篇论文
3. **跟踪趋势：** 每周自动更新

---

**报告生成时间：** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**生成工具：** AI论文全自动预研助手
"""

        return report

    def _format_sections(self, sections: List[Dict[str, str]]) -> str:
        """格式化章节"""
        if not sections:
            return ""
        formatted = []
        for section in sections:
            title = section.get('title', '未命名章节')
            content = section.get('content', '')
            formatted.append(f"### {title}\n\n{content}\n")
        logger.info(f"_format_sections: 格式化了 {len(formatted)} 个章节")
        return "\n".join(formatted)

    def _format_citations(self, citations: List[str]) -> str:
        """格式化引用"""
        if not citations:
            return ""
        formatted = []
        for i, c in enumerate(citations, 1):
            if isinstance(c, str):
                formatted.append(f"{i}. {c}")
            else:
                formatted.append(f"{i}. {str(c)}")
        return "\n".join(formatted)

    def _format_findings(self, papers: List[Dict[str, Any]]) -> str:
        """格式化发现"""
        findings = []
        for i, paper in enumerate(papers[:5], 1):
            # 获取authors
            authors = []
            if 'authors' in paper:
                authors = paper['authors']
            elif 'extracted_fields' in paper and 'authors' in paper['extracted_fields']:
                authors = paper['extracted_fields']['authors']
            elif 'extracted_fields' in paper:
                authors = paper['extracted_fields'].get('authors', [])

            # 提取author names
            author_names = []
            for author in authors:
                if isinstance(author, dict):
                    author_names.append(author.get('name', '未知'))
                elif isinstance(author, str):
                    author_names.append(author)
                else:
                    author_names.append(str(author))

            # 获取published_date
            published_date = 'N/A'
            if 'published_date' in paper:
                published_date = paper['published_date']
            elif 'extracted_fields' in paper and 'published_date' in paper['extracted_fields']:
                published_date = paper['extracted_fields']['published_date']

            # 获取pdf_url
            pdf_url = paper.get('pdf_url', 'N/A')

            findings.append(f"**{i}. {paper['title']}**\n")
            findings.append(f"   - 作者: {', '.join(author_names[:3] if author_names else [])}\n")
            findings.append(f"   - 发布时间: {published_date}\n")
            findings.append(f"   - 链接: {pdf_url}\n\n")
        return "\n".join(findings)
