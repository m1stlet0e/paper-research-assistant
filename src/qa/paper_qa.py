"""
智能问答模块
基于论文内容回答评委提问
"""

from typing import Dict, Any, List
import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PaperQA:
    """
    论文智能问答
    
    功能：
    1. 理解自然语言问题
    2. 从论文中提取答案
    3. 生成结构化回答
    """
    
    def __init__(self, papers: List[Dict[str, Any]]):
        self.papers = papers
        self.paper_index = self._build_index()
    
    def _build_index(self) -> Dict[str, Any]:
        """构建索引"""
        index = {
            "by_method": {},
            "by_dataset": {},
            "by_year": {},
            "by_keyword": {}
        }
        
        for i, paper in enumerate(self.papers):
            summary = paper.get("summary", "").lower()
            title = paper.get("title", "").lower()
            year = paper.get("published", "")[:4] if paper.get("published") else "N/A"
            
            # 按方法索引
            methods = self._extract_methods(summary)
            for method in methods:
                if method not in index["by_method"]:
                    index["by_method"][method] = []
                index["by_method"][method].append(i)
            
            # 按数据集索引
            datasets = self._extract_datasets(summary)
            for dataset in datasets:
                if dataset not in index["by_dataset"]:
                    index["by_dataset"][dataset] = []
                index["by_dataset"][dataset].append(i)
            
            # 按年份索引
            if year not in index["by_year"]:
                index["by_year"][year] = []
            index["by_year"][year].append(i)
            
            # 按关键词索引
            keywords = (title + " " + summary).split()
            for keyword in keywords:
                if len(keyword) > 3:
                    if keyword not in index["by_keyword"]:
                        index["by_keyword"][keyword] = []
                    index["by_keyword"][keyword].append(i)
        
        return index
    
    def _extract_methods(self, text: str) -> List[str]:
        """提取方法"""
        methods = []
        
        if "transformer" in text:
            methods.append("Transformer")
        if "bert" in text:
            methods.append("BERT")
        if "gpt" in text:
            methods.append("GPT")
        if "cnn" in text or "convolutional" in text:
            methods.append("CNN")
        if "rnn" in text or "recurrent" in text:
            methods.append("RNN")
        if "reinforcement learning" in text:
            methods.append("Reinforcement Learning")
        if "attention" in text:
            methods.append("Attention")
        if "multimodal" in text:
            methods.append("Multimodal")
        
        return methods
    
    def _extract_datasets(self, text: str) -> List[str]:
        """提取数据集"""
        datasets = []
        
        if "wmt" in text:
            datasets.append("WMT")
        if "imagenet" in text:
            datasets.append("ImageNet")
        if "coco" in text:
            datasets.append("COCO")
        if "librispeech" in text:
            datasets.append("LibriSpeech")
        if "common voice" in text:
            datasets.append("Common Voice")
        
        return datasets
    
    def answer(self, question: str) -> Dict[str, Any]:
        """
        回答问题
        
        Args:
            question: 用户问题
            
        Returns:
            回答结果
        """
        logger.info(f"[PaperQA] 回答问题: {question}")
        
        question_lower = question.lower()
        
        # 识别问题类型
        question_type = self._identify_question_type(question_lower)
        
        # 根据问题类型回答
        if question_type == "method":
            answer = self._answer_method_question(question_lower)
        elif question_type == "dataset":
            answer = self._answer_dataset_question(question_lower)
        elif question_type == "year":
            answer = self._answer_year_question(question_lower)
        elif question_type == "comparison":
            answer = self._answer_comparison_question(question_lower)
        elif question_type == "summary":
            answer = self._answer_summary_question(question_lower)
        else:
            answer = self._answer_general_question(question_lower)
        
        return {
            "question": question,
            "question_type": question_type,
            "answer": answer,
            "total_papers": len(self.papers)
        }
    
    def _identify_question_type(self, question: str) -> str:
        """识别问题类型"""
        if any(kw in question for kw in ["方法", "method", "怎么做的", "如何实现"]):
            return "method"
        if any(kw in question for kw in ["数据集", "dataset", "数据", "实验"]):
            return "dataset"
        if any(kw in question for kw in ["哪年", "年份", "时间", "year"]):
            return "year"
        if any(kw in question for kw in ["对比", "比较", "区别", "difference"]):
            return "comparison"
        if any(kw in question for kw in ["总结", "概览", "主要", "summary"]):
            return "summary"
        
        return "general"
    
    def _answer_method_question(self, question: str) -> str:
        """回答方法相关问题"""
        # 检查具体方法
        methods_found = []
        
        for method, indices in self.paper_index["by_method"].items():
            if method.lower() in question:
                methods_found.append((method, len(indices), indices))
        
        if methods_found:
            answer = f"根据检索结果：\n\n"
            for method, count, indices in methods_found:
                answer += f"**{method}**: 在 {count} 篇论文中出现\n\n"
                
                # 列出相关论文
                answer += "相关论文：\n"
                for idx in indices[:5]:
                    paper = self.papers[idx]
                    answer += f"- {paper.get('title', '未知标题')}\n"
                
                answer += "\n"
            
            return answer
        
        # 如果没有指定方法，列出所有方法
        answer = "研究涉及的主要方法：\n\n"
        sorted_methods = sorted(self.paper_index["by_method"].items(), key=lambda x: len(x[1]), reverse=True)
        
        for method, indices in sorted_methods[:5]:
            answer += f"- **{method}**: {len(indices)} 篇论文\n"
        
        return answer
    
    def _answer_dataset_question(self, question: str) -> str:
        """回答数据集相关问题"""
        datasets_found = []
        
        for dataset, indices in self.paper_index["by_dataset"].items():
            if dataset.lower() in question:
                datasets_found.append((dataset, len(indices), indices))
        
        if datasets_found:
            answer = f"使用该数据集的论文：\n\n"
            for dataset, count, indices in datasets_found:
                answer += f"**{dataset}**: 在 {count} 篇论文中使用\n\n"
                
                for idx in indices[:5]:
                    paper = self.papers[idx]
                    answer += f"- {paper.get('title', '未知标题')}\n"
            
            return answer
        
        # 列出所有数据集
        answer = "研究使用的主要数据集：\n\n"
        sorted_datasets = sorted(self.paper_index["by_dataset"].items(), key=lambda x: len(x[1]), reverse=True)
        
        for dataset, indices in sorted_datasets[:5]:
            answer += f"- **{dataset}**: {len(indices)} 篇论文使用\n"
        
        return answer
    
    def _answer_year_question(self, question: str) -> str:
        """回答年份相关问题"""
        # 提取年份
        years = re.findall(r'\b(20\d{2})\b', question)
        
        if years:
            year = years[0]
            if year in self.paper_index["by_year"]:
                indices = self.paper_index["by_year"][year]
                answer = f"**{year}年**发表了 {len(indices)} 篇相关论文：\n\n"
                
                for idx in indices[:10]:
                    paper = self.papers[idx]
                    answer += f"- {paper.get('title', '未知标题')}\n"
                
                return answer
            else:
                return f"未找到 {year} 年的相关论文。"
        
        # 列出年份分布
        answer = "论文年份分布：\n\n"
        sorted_years = sorted(self.paper_index["by_year"].items())
        
        for year, indices in sorted_years:
            answer += f"- **{year}**: {len(indices)} 篇论文\n"
        
        return answer
    
    def _answer_comparison_question(self, question: str) -> str:
        """回答对比问题"""
        answer = "论文对比分析：\n\n"
        
        # 方法对比
        answer += "**方法对比**：\n"
        sorted_methods = sorted(self.paper_index["by_method"].items(), key=lambda x: len(x[1]), reverse=True)
        
        for method, indices in sorted_methods[:3]:
            paper = self.papers[indices[0]]
            answer += f"- {method}: {len(indices)}篇论文使用，如《{paper.get('title', '')[:50]}...》\n"
        
        # 数据集对比
        answer += "\n**数据集对比**：\n"
        sorted_datasets = sorted(self.paper_index["by_dataset"].items(), key=lambda x: len(x[1]), reverse=True)
        
        for dataset, indices in sorted_datasets[:3]:
            answer += f"- {dataset}: {len(indices)}篇论文使用\n"
        
        return answer
    
    def _answer_summary_question(self, question: str) -> str:
        """回答总结问题"""
        answer = "研究总结：\n\n"
        
        # 统计信息
        answer += f"- **论文总数**: {len(self.papers)} 篇\n"
        answer += f"- **主要方法**: {len(self.paper_index['by_method'])} 种\n"
        answer += f"- **数据集数**: {len(self.paper_index['by_dataset'])} 个\n"
        answer += f"- **时间跨度**: {len(self.paper_index['by_year'])} 年\n\n"
        
        # 核心论文
        answer += "**核心论文**（按相关性排序）：\n\n"
        for i, paper in enumerate(self.papers[:5], 1):
            answer += f"{i}. {paper.get('title', '未知标题')}\n"
            if paper.get("authors"):
                authors = paper["authors"][:3]
                author_names = [a.get("name", "") if isinstance(a, dict) else str(a) for a in authors]
                answer += f"   作者: {', '.join(author_names)}\n"
            answer += "\n"
        
        return answer
    
    def _answer_general_question(self, question: str) -> str:
        """回答一般问题"""
        # 搜索关键词
        keywords = [w for w in question.split() if len(w) > 3]
        
        relevant_indices = set()
        for keyword in keywords:
            if keyword in self.paper_index["by_keyword"]:
                relevant_indices.update(self.paper_index["by_keyword"][keyword])
        
        if relevant_indices:
            answer = f"找到 {len(relevant_indices)} 篇相关论文：\n\n"
            
            for idx in list(relevant_indices)[:10]:
                paper = self.papers[idx]
                answer += f"- {paper.get('title', '未知标题')}\n"
            
            return answer
        
        return "抱歉，未找到相关信息。请尝试更具体的问题。"
    
    def chat(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        多轮对话
        
        Args:
            questions: 问题列表
            
        Returns:
            回答列表
        """
        answers = []
        for question in questions:
            answer = self.answer(question)
            answers.append(answer)
        
        return answers
    
    def export_to_html(self, qa_pairs: List[Dict[str, Any]], output_path: str = "qa_demo.html") -> str:
        """导出问答演示HTML"""
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>论文智能问答</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .chat-container {
            margin-top: 20px;
        }
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 10px;
        }
        .question {
            background: #e3f2fd;
            margin-left: 20%;
        }
        .answer {
            background: #f5f5f5;
            margin-right: 20%;
        }
        .question-label, .answer-label {
            font-weight: bold;
            margin-bottom: 5px;
            color: #666;
        }
        .input-container {
            margin-top: 30px;
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            padding: 10px 20px;
            background: #4A90E2;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background: #357ABD;
        }
        .example-questions {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .example-question {
            display: inline-block;
            margin: 5px;
            padding: 5px 10px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 3px;
            cursor: pointer;
        }
        .example-question:hover {
            background: #e3f2fd;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💬 论文智能问答</h1>
        <p>基于检索到的论文，AI可以回答相关问题</p>
        
        <div class="example-questions">
            <h3>示例问题（点击尝试）：</h3>
            <div class="example-question" onclick="askQuestion('哪些论文使用了Transformer？')">哪些论文使用了Transformer？</div>
            <div class="example-question" onclick="askQuestion('主要的研究方法有哪些？')">主要的研究方法有哪些？</div>
            <div class="example-question" onclick="askQuestion('2024年发表了哪些论文？')">2024年发表了哪些论文？</div>
            <div class="example-question" onclick="askQuestion('总结一下研究现状')">总结一下研究现状</div>
        </div>
        
        <div class="chat-container" id="chat">
'''
        
        # 添加问答对
        for qa in qa_pairs:
            html += f'''
            <div class="message question">
                <div class="question-label">👤 评委</div>
                <div>{qa["question"]}</div>
            </div>
            <div class="message answer">
                <div class="answer-label">🤖 AI助手</div>
                <div>{qa["answer"].replace(chr(10), "<br>")}</div>
            </div>
'''
        
        html += '''
        </div>
        
        <div class="input-container">
            <input type="text" id="questionInput" placeholder="输入您的问题..." onkeypress="if(event.key==='Enter') sendQuestion()">
            <button onclick="sendQuestion()">发送</button>
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
            
            // 添加问题
            const chat = document.getElementById('chat');
            chat.innerHTML += `
                <div class="message question">
                    <div class="question-label">👤 评委</div>
                    <div>${question}</div>
                </div>
            `;
            
            // 模拟回答（实际应该调用后端API）
            chat.innerHTML += `
                <div class="message answer">
                    <div class="answer-label">🤖 AI助手</div>
                    <div>正在分析论文数据...</div>
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
        
        logger.info(f"[PaperQA] HTML导出: {output_path}")
        
        return output_path
