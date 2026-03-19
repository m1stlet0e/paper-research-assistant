"""
LaTeX报告生成器
生成学术论文格式的研究报告
"""

from typing import List, Dict, Any
from datetime import datetime


class LaTeXGenerator:
    """LaTeX格式报告生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def generate(self, topic: str, papers: List[Dict[str, Any]], review: Dict[str, Any]) -> str:
        """生成LaTeX格式研究报告"""
        try:
            latex_code = self._generate_latex_document(topic, papers, review)
            return latex_code
        except Exception as e:
            print(f"LaTeX报告生成失败: {e}")
            return self._generate_error_latex(topic, papers, e)
    
    def _generate_latex_document(self, topic: str, papers: List[Dict[str, Any]], review: Dict[str, Any]) -> str:
        """生成完整的LaTeX文档"""
        
        # 处理review为None的情况
        if review is None:
            review = {
                "sections": [],
                "citations": [],
                "statistics": {}
            }
        
        latex = r"""
% AI论文全自动预研助手 - 研究报告
% 课题: """ + topic + r"""
% 生成时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + r"""

\documentclass[12pt,a4paper]{article}

% 包配置
\usepackage[utf8]{inputenc}
\usepackage[margin=2.5cm]{geometry}
\usepackage{ctex}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{longtable}

% 代码高亮样式
\lstset{
    backgroundcolor=\color{gray!10},
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single
}

% 超链接样式
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,
    urlcolor=cyan,
}

% Title
\title{\textbf{""" + topic + r""" \\
\Large{AI论文预研助手 - 文献综述报告}}}
\author{AI论文预研助手}
\date{""" + datetime.now().strftime("%Y年%m月%d日") + r"""}

\begin{document}

\maketitle

\begin{abstract}
本报告对\textbf{""" + topic + r"""}领域的最新研究文献进行了系统性综述。
通过arXiv和Google Scholar等学术数据库检索，共获取""" + str(len(papers)) + r"""篇相关论文。
本报告分析了该领域的研究趋势、主要发现和研究空白，为后续研究提供参考。
\end{abstract}

\section{研究概述}

\subsection{研究课题}
本报告研究课题为：\textbf{""" + topic + r"""}

\subsection{数据来源}
""" + self._generate_data_sources(papers, review) + r"""

\subsection{研究统计}
""" + self._generate_statistics(papers, review) + r"""

\section{文献综述}

""" + self._generate_sections(review.get('sections', [])) + r"""

\section{主要发现}

""" + self._generate_findings(papers) + r"""

\section{研究趋势}

""" + self._generate_trends(papers) + r"""

\section{参考文献}

""" + self._generate_references(review.get('citations', [])) + r"""

\end{document}
"""
        return latex
    
    def _generate_data_sources(self, papers: List[Dict[str, Any]], review: Dict[str, Any]) -> str:
        """生成数据来源部分"""
        sources = set()
        for paper in papers:
            source = paper.get('source', 'unknown')
            sources.add(source)
        
        source_str = ", ".join([s.capitalize() for s in sources])
        return f"数据来源包括：{source_str}。共检索到 {len(papers)} 篇相关论文。"
    
    def _generate_statistics(self, papers: List[Dict[str, Any]], review: Dict[str, Any]) -> str:
        """生成统计信息"""
        stats = review.get('statistics', {})
        
        # 提取作者数量
        unique_authors = set()
        for paper in papers:
            for author in paper.get('authors', []):
                author_name = author.get('name', '') if isinstance(author, dict) else author
                if author_name:
                    unique_authors.add(author_name)
        
        # 提取发表时间
        dates = []
        for paper in papers:
            published = paper.get('published', '')
            if published:
                dates.append(published)
        
        earliest = min(dates)[:10] if dates else 'N/A'
        latest = max(dates)[:10] if dates else 'N/A'
        
        stats_text = r"""
\begin{table}[htbp]
\centering
\caption{研究统计信息}
\begin{tabular}{|c|c|}
\hline
指标 & 数值 \\
\hline
论文总数 & """ + str(len(papers)) + r""" \\
\hline
作者数量 & """ + str(len(unique_authors)) + r""" \\
\hline
最早发表 & """ + earliest + r""" \\
\hline
最新发表 & """ + latest + r""" \\
\hline
\end{tabular}
\end{table}
"""
        return stats_text
    
    def _generate_sections(self, sections: List[Dict[str, Any]]) -> str:
        """生成文献综述章节"""
        if not sections:
            return "暂无文献综述内容。"
        
        result = ""
        for i, section in enumerate(sections, 1):
            title = section.get('title', f'章节{i}')
            content = section.get('content', '')
            
            # 清理LaTeX特殊字符
            content = self._escape_latex(content)
            
            result += f"\\subsection{{{title}}}\n\n{content}\n\n"
        
        return result
    
    def _generate_findings(self, papers: List[Dict[str, Any]]) -> str:
        """生成主要发现"""
        if not papers:
            return "暂无主要发现。"
        
        findings = r"""
以下为本研究领域的主要代表性论文：
"""
        
        for i, paper in enumerate(papers[:10], 1):
            title = self._escape_latex(paper.get('title', '未知标题'))
            authors = paper.get('authors', [])
            author_names = [a.get('name', '') if isinstance(a, dict) else a for a in authors[:3]]
            authors_str = ", ".join(author_names)
            
            published = paper.get('published', '')[:10]
            
            findings += f"""
\\begin{{itemize}}
\\item {title}
\\begin{{itemize}}
\\item 作者：{authors_str}
\\item 发表时间：{published}
\\end{{itemize}}
\\end{{itemize}}
"""
        
        return findings
    
    def _generate_trends(self, papers: List[Dict[str, Any]]) -> str:
        """生成研究趋势"""
        # 统计每年的论文数量
        year_counts = {}
        for paper in papers:
            published = paper.get('published', '')
            if published:
                year = published[:4]
                year_counts[year] = year_counts.get(year, 0) + 1
        
        if not year_counts:
            return "暂无研究趋势数据。"
        
        # 按年份排序
        sorted_years = sorted(year_counts.items(), reverse=True)[:5]
        
        trends = r"""
\subsection{年度发表趋势}
"""
        
        for year, count in sorted_years:
            trends += f"- {year}年：{count}篇论文\n"
        
        trends += "\n\\subsection{研究热点}\n"
        trends += "基于文献分析，当前研究热点包括：\n\\begin{itemize}\n"
        
        # 简单的关键词统计
        keywords = self._extract_keywords(papers)
        for kw in keywords[:5]:
            trends += f"\\item {kw}\n"
        
        trends += "\\end{itemize}\n"
        
        return trends
    
    def _extract_keywords(self, papers: List[Dict[str, Any]]) -> List[str]:
        """提取高频关键词"""
        keyword_counts = {}
        
        common_keywords = [
            'deep learning', 'neural network', 'transformer', 'attention',
            'machine learning', 'natural language processing', 'computer vision',
            'speech recognition', 'asr', 'speech synthesis', 'nlp', 'cv',
            'reinforcement learning', 'gpt', 'llm', 'language model'
        ]
        
        for paper in papers:
            title = paper.get('title', '').lower()
            summary = paper.get('summary', '').lower()
            
            text = title + " " + summary
            
            for kw in common_keywords:
                if kw in text:
                    keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        # 按频率排序
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in sorted_keywords]
    
    def _generate_references(self, citations: List[str]) -> str:
        """生成参考文献"""
        if not citations:
            return "暂无参考文献。"
        
        refs = "\\begin{thebibliography}{99}\n"
        
        for i, citation in enumerate(citations[:20], 1):
            # 清理LaTeX特殊字符
            citation = self._escape_latex(citation)
            refs += f"\\bibitem{{ref{i}}} {citation}\n"
        
        refs += "\\end{thebibliography}\n"
        return refs
    
    def _escape_latex(self, text: str) -> str:
        """转义LaTeX特殊字符"""
        if not text:
            return ""
        
        # 替换LaTeX特殊字符
        replacements = {
            '\\': '\\textbackslash{}',
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '^': '\\textasciicircum{}',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    def _generate_error_latex(self, topic: str, papers: List[Dict[str, Any]], error: Exception) -> str:
        """生成错误报告"""
        return r"""\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{ctex}

\title{错误报告}
\author{AI论文预研助手}

\begin{document}
\maketitle

\section{错误信息}
生成报告时发生错误：""" + str(error) + r"""

\section{研究信息}
\begin{itemize}
\item 课题：""" + topic + r"""
\item 论文数量：""" + str(len(papers)) + r"""
\end{itemize}

\end{document}"""
