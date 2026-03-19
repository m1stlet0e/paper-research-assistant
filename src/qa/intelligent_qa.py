"""
智能问答系统
基于论文内容的智能问答，支持自然语言问题
"""

from typing import Dict, Any, List, Optional
from collections import defaultdict
import re
import json
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IntelligentQA:
    """
    智能问答系统
    
    功能：
    1. 理解自然语言问题
    2. 从论文中提取相关答案
    3. 支持多轮对话
    4. 生成结构化回答
    """
    
    def __init__(self, papers: List[Dict[str, Any]] = None):
        self.papers = papers or []
        self.index = self._build_index() if papers else {}
        
        # 问题模板
        self.question_patterns = {
            "method": {
                "keywords": ["方法", "method", "怎么做的", "如何实现", "技术方案", "采用什么"],
                "handler": self._answer_method_question
            },
            "dataset": {
                "keywords": ["数据集", "dataset", "数据", "实验数据", "训练数据"],
                "handler": self._answer_dataset_question
            },
            "year": {
                "keywords": ["哪年", "年份", "时间", "year", "什么时候"],
                "handler": self._answer_year_question
            },
            "comparison": {
                "keywords": ["对比", "比较", "区别", "difference", "vs", "对比分析"],
                "handler": self._answer_comparison_question
            },
            "summary": {
                "keywords": ["总结", "概览", "综述", "summary", "overview", "主要"],
                "handler": self._answer_summary_question
            },
            "author": {
                "keywords": ["作者", "author", "谁写的", "研究人员"],
                "handler": self._answer_author_question
            },
            "innovation": {
                "keywords": ["创新", "创新点", "贡献", "innovation", "贡献点"],
                "handler": self._answer_innovation_question
            },
            "performance": {
                "keywords": ["性能", "效果", "准确率", "performance", "结果"],
                "handler": self._answer_performance_question
            }
        }
    
    def _build_index(self) -> Dict[str, Any]:
        """构建论文索引"""
        index = {
            "by_method": defaultdict(list),
            "by_dataset": defaultdict(list),
            "by_year": defaultdict(list),
            "by_author": defaultdict(list),
            "by_keyword": defaultdict(list),
            "all_text": []
        }
        
        for i, paper in enumerate(self.papers):
            title = paper.get("title", "").lower()
            summary = paper.get("summary", "").lower()
            text = title + " " + summary
            
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            
            # 索引方法
            methods = self._extract_methods(text)
            for method in methods:
                index["by_method"][method].append(i)
            
            # 索引数据集
            datasets = self._extract_datasets(text)
            for dataset in datasets:
                index["by_dataset"][dataset].append(i)
            
            # 索引年份
            if year != "N/A":
                index["by_year"][year].append(i)
            
            # 索引作者
            for author in paper.get("authors", []):
                author_name = author.get("name", "") if isinstance(author, dict) else author
                if author_name:
                    index["by_author"][author_name].append(i)
            
            # 索引关键词
            keywords = re.findall(r'\b[a-zA-Z]{4,}\b', text)
            for kw in keywords:
                if len(kw) > 3:
                    index["by_keyword"][kw.lower()].append(i)
            
            # 全文索引
            index["all_text"].append({
                "index": i,
                "title": paper.get("title", ""),
                "summary": paper.get("summary", ""),
                "year": year
            })
        
        return index
    
    def _extract_methods(self, text: str) -> List[str]:
        """提取方法"""
        methods = []
        
        method_patterns = {
            "Transformer": ["transformer", "self-attention"],
            "BERT": ["bert"],
            "GPT": ["gpt"],
            "CNN": ["cnn", "convolutional"],
            "RNN/LSTM": ["rnn", "lstm", "gru"],
            "Attention": ["attention"],
            "Reinforcement Learning": ["reinforcement learning", "rl"],
            "GAN": ["gan", "adversarial"],
            "Diffusion": ["diffusion"],
            "Multimodal": ["multimodal"],
            "Graph Neural Network": ["graph neural network", "gnn"],
            "Few-shot Learning": ["few-shot", "zero-shot"],
            "Contrastive Learning": ["contrastive"],
        }
        
        for method, patterns in method_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    methods.append(method)
                    break
        
        return methods
    
    def _extract_datasets(self, text: str) -> List[str]:
        """提取数据集"""
        datasets = []
        
        dataset_patterns = {
            "ImageNet": ["imagenet"],
            "COCO": ["coco"],
            "WMT": ["wmt"],
            "SQuAD": ["squad"],
            "GLUE": ["glue"],
            "LibriSpeech": ["librispeech"],
            "Common Voice": ["common voice"],
        }
        
        for dataset, patterns in dataset_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    datasets.append(dataset)
                    break
        
        return datasets
    
    def answer(self, question: str) -> Dict[str, Any]:
        """
        回答问题
        
        Args:
            question: 用户问题
            
        Returns:
            回答结果
        """
        logger.info(f"[QA] 问题: {question}")
        
        # 识别问题类型
        question_type = self._identify_question_type(question)
        
        # 获取对应处理器
        handler = self.question_patterns.get(question_type, {}).get("handler", self._answer_general_question)
        
        # 生成回答
        answer = handler(question.lower())
        
        result = {
            "question": question,
            "question_type": question_type,
            "answer": answer,
            "total_papers": len(self.papers),
            "relevant_papers": len(self._find_relevant_papers(question))
        }
        
        return result
    
    def _identify_question_type(self, question: str) -> str:
        """识别问题类型"""
        question_lower = question.lower()
        
        for qtype, config in self.question_patterns.items():
            for keyword in config["keywords"]:
                if keyword in question_lower:
                    return qtype
        
        return "general"
    
    def _find_relevant_papers(self, question: str) -> List[int]:
        """找到相关论文索引"""
        relevant = set()
        
        # 从关键词索引中查找
        words = re.findall(r'\b[a-zA-Z]{4,}\b', question.lower())
        for word in words:
            if word in self.index.get("by_keyword", {}):
                relevant.update(self.index["by_keyword"][word])
        
        return list(relevant)
    
    def _answer_method_question(self, question: str) -> str:
        """回答方法相关问题"""
        # 检查是否询问特定方法
        methods_in_question = self._extract_methods(question)
        
        if methods_in_question:
            # 询问特定方法
            answer = f"关于 **{methods_in_question[0]}** 方法：\n\n"
            
            method_indices = self.index["by_method"].get(methods_in_question[0], [])
            
            if method_indices:
                answer += f"共有 **{len(method_indices)} 篇论文**使用了该方法。\n\n"
                answer += "**相关论文：**\n\n"
                
                for idx in method_indices[:5]:
                    paper = self.papers[idx]
                    answer += f"- [{paper.get('title', '未知标题')[:60]}](https://arxiv.org/abs/{paper.get('arxiv_id', '')})\n"
            else:
                answer += "未找到使用该方法的论文。"
            
            return answer
        
        # 列出所有方法分布
        answer = "## 研究方法分布\n\n"
        
        sorted_methods = sorted(self.index["by_method"].items(), key=lambda x: len(x[1]), reverse=True)
        
        for method, indices in sorted_methods[:10]:
            answer += f"- **{method}**: {len(indices)} 篇论文\n"
        
        if sorted_methods:
            answer += f"\n共识别出 **{len(sorted_methods)} 种研究方法**。\n"
        
        return answer
    
    def _answer_dataset_question(self, question: str) -> str:
        """回答数据集相关问题"""
        datasets_in_question = self._extract_datasets(question)
        
        if datasets_in_question:
            answer = f"关于 **{datasets_in_question[0]}** 数据集：\n\n"
            
            dataset_indices = self.index["by_dataset"].get(datasets_in_question[0], [])
            
            if dataset_indices:
                answer += f"共有 **{len(dataset_indices)} 篇论文**使用了该数据集。\n\n"
                answer += "**相关论文：**\n\n"
                
                for idx in dataset_indices[:5]:
                    paper = self.papers[idx]
                    answer += f"- [{paper.get('title', '未知标题')[:60]}](https://arxiv.org/abs/{paper.get('arxiv_id', '')})\n"
            else:
                answer += "未找到使用该数据集的论文。"
            
            return answer
        
        # 列出所有数据集分布
        answer = "## 数据集使用分布\n\n"
        
        sorted_datasets = sorted(self.index["by_dataset"].items(), key=lambda x: len(x[1]), reverse=True)
        
        for dataset, indices in sorted_datasets[:10]:
            answer += f"- **{dataset}**: {len(indices)} 篇论文\n"
        
        if sorted_datasets:
            answer += f"\n共识别出 **{len(sorted_datasets)} 个数据集**。\n"
        
        return answer
    
    def _answer_year_question(self, question: str) -> str:
        """回答年份相关问题"""
        # 提取年份
        years = re.findall(r'\b(20\d{2})\b', question)
        
        if years:
            year = years[0]
            indices = self.index["by_year"].get(year, [])
            
            if indices:
                answer = f"## {year} 年发表的论文\n\n"
                answer += f"共 **{len(indices)} 篇论文**。\n\n"
                
                for idx in indices[:10]:
                    paper = self.papers[idx]
                    answer += f"- [{paper.get('title', '未知标题')[:60]}](https://arxiv.org/abs/{paper.get('arxiv_id', '')})\n"
                
                return answer
            else:
                return f"未找到 **{year} 年**发表的相关论文。"
        
        # 列出年份分布
        answer = "## 论文年份分布\n\n"
        
        sorted_years = sorted(self.index["by_year"].items())
        
        for year, indices in sorted_years:
            answer += f"- **{year}**: {len(indices)} 篇论文\n"
        
        if sorted_years:
            earliest = min(self.index["by_year"].keys())
            latest = max(self.index["by_year"].keys())
            answer += f"\n时间跨度: **{earliest} - {latest}**\n"
        
        return answer
    
    def _answer_comparison_question(self, question: str) -> str:
        """回答对比问题"""
        answer = "## 论文对比分析\n\n"
        
        # 方法对比
        answer += "### 方法对比\n\n"
        sorted_methods = sorted(self.index["by_method"].items(), key=lambda x: len(x[1]), reverse=True)[:5]
        
        for method, indices in sorted_methods:
            paper = self.papers[indices[0]] if indices else None
            paper_title = paper.get("title", "")[:50] if paper else ""
            answer += f"- **{method}**: {len(indices)}篇论文使用\n"
            if paper_title:
                answer += f"  - 例如: {paper_title}...\n"
        
        # 数据集对比
        answer += "\n### 数据集对比\n\n"
        sorted_datasets = sorted(self.index["by_dataset"].items(), key=lambda x: len(x[1]), reverse=True)[:5]
        
        for dataset, indices in sorted_datasets:
            answer += f"- **{dataset}**: {len(indices)}篇论文使用\n"
        
        return answer
    
    def _answer_summary_question(self, question: str) -> str:
        """回答总结问题"""
        answer = "## 研究总结\n\n"
        
        # 统计信息
        answer += f"- **论文总数**: {len(self.papers)} 篇\n"
        answer += f"- **研究方法**: {len(self.index['by_method'])} 种\n"
        answer += f"- **数据集**: {len(self.index['by_dataset'])} 个\n"
        answer += f"- **时间跨度**: {len(self.index['by_year'])} 年\n"
        
        # 核心论文
        answer += "\n### 核心论文\n\n"
        
        for i, paper in enumerate(self.papers[:5], 1):
            title = paper.get("title", "未知标题")
            authors = []
            for author in paper.get("authors", [])[:3]:
                if isinstance(author, dict):
                    authors.append(author.get("name", ""))
                elif isinstance(author, str):
                    authors.append(author)
            
            answer += f"{i}. **{title[:60]}**\n"
            if authors:
                answer += f"   - 作者: {', '.join(authors)}\n"
            answer += "\n"
        
        # 主要方法
        answer += "### 主要方法\n\n"
        sorted_methods = sorted(self.index["by_method"].items(), key=lambda x: len(x[1]), reverse=True)[:5]
        for method, indices in sorted_methods:
            answer += f"- **{method}**: {len(indices)}篇\n"
        
        return answer
    
    def _answer_author_question(self, question: str) -> str:
        """回答作者相关问题"""
        # 提取可能的作者名
        answer = "## 作者分析\n\n"
        
        # 按论文数排序作者
        sorted_authors = sorted(self.index["by_author"].items(), key=lambda x: len(x[1]), reverse=True)[:10]
        
        if sorted_authors:
            answer += "### 活跃作者（按论文数）\n\n"
            for author, indices in sorted_authors:
                answer += f"- **{author}**: {len(indices)} 篇论文\n"
        else:
            answer += "暂无作者信息。\n"
        
        return answer
    
    def _answer_innovation_question(self, question: str) -> str:
        """回答创新点问题"""
        answer = "## 论文创新点分析\n\n"
        
        innovation_keywords = {
            "新颖方法": ["novel", "new method", "new approach"],
            "首次研究": ["first", "pioneering"],
            "性能提升": ["improve", "better performance"],
            "超越SOTA": ["outperform", "state-of-the-art", "sota"],
            "高效实现": ["efficient", "faster"],
        }
        
        innovation_counts = defaultdict(int)
        
        for paper in self.papers:
            text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
            for inn, keywords in innovation_keywords.items():
                for kw in keywords:
                    if kw in text:
                        innovation_counts[inn] += 1
                        break
        
        if innovation_counts:
            answer += "### 创新类型分布\n\n"
            for inn, count in sorted(innovation_counts.items(), key=lambda x: x[1], reverse=True):
                answer += f"- **{inn}**: {count} 篇论文\n"
        else:
            answer += "暂未识别到明确的创新点类型。\n"
        
        return answer
    
    def _answer_performance_question(self, question: str) -> str:
        """回答性能问题"""
        answer = "## 性能指标分析\n\n"
        
        # 搜索性能相关关键词
        perf_keywords = ["accuracy", "precision", "recall", "f1", "bleu", "perplexity", "loss"]
        
        perf_papers = []
        for paper in self.papers:
            text = paper.get("summary", "").lower()
            for kw in perf_keywords:
                if kw in text:
                    perf_papers.append(paper)
                    break
        
        if perf_papers:
            answer += f"共有 **{len(perf_papers)} 篇论文** 包含性能指标。\n\n"
            answer += "**相关论文：**\n\n"
            
            for paper in perf_papers[:5]:
                answer += f"- [{paper.get('title', '未知标题')[:60]}](https://arxiv.org/abs/{paper.get('arxiv_id', '')})\n"
        else:
            answer += "暂未找到包含性能指标的论文。\n"
        
        return answer
    
    def _answer_general_question(self, question: str) -> str:
        """回答一般问题"""
        # 搜索相关论文
        relevant_indices = self._find_relevant_papers(question)
        
        if relevant_indices:
            answer = f"找到 **{len(relevant_indices)} 篇相关论文**：\n\n"
            
            for idx in relevant_indices[:10]:
                paper = self.papers[idx]
                answer += f"- [{paper.get('title', '未知标题')[:60]}](https://arxiv.org/abs/{paper.get('arxiv_id', '')})\n"
            
            return answer
        
        return "抱歉，未找到与您问题相关的论文。请尝试更具体的问题，例如：\n\n- 主要的研究方法有哪些？\n- 哪些论文使用了Transformer？\n- 2024年发表了哪些论文？"
    
    def chat(self, questions: List[str]) -> List[Dict[str, Any]]:
        """多轮对话"""
        return [self.answer(q) for q in questions]
    
    def export_to_html(self, qa_pairs: List[Dict[str, Any]], output_path: str = "qa_demo.html") -> str:
        """导出问答演示HTML"""
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能问答演示</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}
        
        .header {{
            background: rgba(255,255,255,0.05);
            padding: 1.5rem;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .header h1 {{
            font-size: 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .stats {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            flex: 1;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{
            font-size: 0.85rem;
            color: #a0a0a0;
        }}
        
        .chat-container {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .message {{
            margin-bottom: 1.5rem;
            padding: 1rem;
            border-radius: 12px;
        }}
        
        .question {{
            background: rgba(102, 126, 234, 0.2);
            margin-left: 2rem;
        }}
        
        .answer {{
            background: rgba(255,255,255,0.05);
            margin-right: 2rem;
        }}
        
        .message-label {{
            font-size: 0.75rem;
            color: #a0a0a0;
            margin-bottom: 0.5rem;
        }}
        
        .message-content {{
            line-height: 1.6;
        }}
        
        .message-content a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .message-content a:hover {{
            text-decoration: underline;
        }}
        
        .input-container {{
            margin-top: 1.5rem;
            display: flex;
            gap: 1rem;
        }}
        
        .input {{
            flex: 1;
            padding: 1rem;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            color: #e0e0e0;
            font-size: 1rem;
        }}
        
        .input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .btn {{
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .examples {{
            margin-top: 1.5rem;
            padding: 1rem;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
        }}
        
        .examples h3 {{
            font-size: 0.9rem;
            color: #a0a0a0;
            margin-bottom: 0.75rem;
        }}
        
        .example-btn {{
            display: inline-block;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 20px;
            color: #667eea;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .example-btn:hover {{
            background: rgba(102, 126, 234, 0.2);
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>💬 智能问答系统</h1>
        <p style="color: #a0a0a0; margin-top: 0.5rem;">基于论文内容的智能问答</p>
    </header>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{qa_pairs[0].get('total_papers', 0) if qa_pairs else 0}</div>
                <div class="stat-label">论文总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(qa_pairs)}</div>
                <div class="stat-label">问答对</div>
            </div>
        </div>
        
        <div class="chat-container" id="chat">
'''
        
        for qa in qa_pairs:
            answer_html = qa.get("answer", "").replace("\n", "<br>")
            
            html += f'''
            <div class="message question">
                <div class="message-label">👤 用户提问</div>
                <div class="message-content">{qa.get("question", "")}</div>
            </div>
            
            <div class="message answer">
                <div class="message-label">🤖 AI回答</div>
                <div class="message-content">{answer_html}</div>
            </div>
'''
        
        html += '''
        </div>
        
        <div class="input-container">
            <input type="text" class="input" id="questionInput" placeholder="输入您的问题..." onkeypress="if(event.key==='Enter') sendQuestion()">
            <button class="btn" onclick="sendQuestion()">发送</button>
        </div>
        
        <div class="examples">
            <h3>💡 试试这些问题：</h3>
            <span class="example-btn" onclick="askQuestion('主要的研究方法有哪些？')">主要的研究方法有哪些？</span>
            <span class="example-btn" onclick="askQuestion('哪些论文使用了Transformer？')">哪些论文使用了Transformer？</span>
            <span class="example-btn" onclick="askQuestion('总结一下研究现状')">总结一下研究现状</span>
            <span class="example-btn" onclick="askQuestion('数据集使用情况')">数据集使用情况</span>
            <span class="example-btn" onclick="askQuestion('论文创新点分析')">论文创新点分析</span>
        </div>
    </div>
    
    <script>
        function askQuestion(question) {
            document.getElementById('questionInput').value = question;
            sendQuestion();
        }
        
        function sendQuestion() {
            const input = document.getElementById('questionInput');
            const question = input.value.trim();
            
            if (!question) return;
            
            const chat = document.getElementById('chat');
            
            // 添加问题
            chat.innerHTML += `
                <div class="message question">
                    <div class="message-label">👤 用户提问</div>
                    <div class="message-content">${question}</div>
                </div>
            `;
            
            // 模拟回答（实际应调用后端API）
            chat.innerHTML += `
                <div class="message answer">
                    <div class="message-label">🤖 AI回答</div>
                    <div class="message-content">正在分析论文数据，请稍候...</div>
                </div>
            `;
            
            input.value = '';
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"[QA] HTML导出: {output_path}")
        
        return output_path
