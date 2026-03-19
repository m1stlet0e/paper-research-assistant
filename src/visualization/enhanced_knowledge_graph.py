"""
增强知识图谱可视化模块
使用ECharts构建交互式论文关系图谱
"""

from typing import Dict, Any, List, Set
from collections import defaultdict
import json
import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedKnowledgeGraph:
    """
    增强版知识图谱
    
    功能：
    1. 提取论文实体（方法、数据集、创新点）
    2. 构建引用网络和相似关系
    3. 计算节点重要性（PageRank）
    4. 生成ECharts交互式可视化
    """
    
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.categories = []
        
        # 方法关键词映射
        self.method_keywords = {
            "Transformer": ["transformer", "self-attention", "multi-head attention"],
            "BERT": ["bert", "masked language model", "pre-training"],
            "GPT": ["gpt", "generative pre-trained", "language generation"],
            "CNN": ["cnn", "convolutional", "convolution"],
            "RNN/LSTM": ["rnn", "lstm", "recurrent", "gru"],
            "Attention": ["attention", "attention mechanism"],
            "Reinforcement Learning": ["reinforcement learning", "rl", "policy gradient", "q-learning"],
            "GAN": ["gan", "generative adversarial", "adversarial training"],
            "Diffusion Model": ["diffusion", "denoising diffusion", "score-based"],
            "Multimodal": ["multimodal", "vision-language", "cross-modal"],
            "Graph Neural Network": ["graph neural network", "gnn", "graph attention"],
            "Few-shot Learning": ["few-shot", "meta-learning", "zero-shot"],
            "Knowledge Distillation": ["distill", "knowledge distillation", "teacher-student"],
            "Contrastive Learning": ["contrastive", "simclr", "moco"],
        }
        
        # 数据集关键词映射
        self.dataset_keywords = {
            "ImageNet": ["imagenet", "image classification"],
            "COCO": ["coco", "common objects in context"],
            "WMT": ["wmt", "translation", "machine translation"],
            "SQuAD": ["squad", "question answering", "stanford question"],
            "GLUE": ["glue", "language understanding"],
            "LibriSpeech": ["librispeech", "speech recognition"],
            "Common Voice": ["common voice", "mozilla common voice"],
            "LJSpeech": ["ljspeech", "tts", "text-to-speech"],
            "PASCAL VOC": ["pascal voc", "voc"],
            "Cityscapes": ["cityscapes", "semantic segmentation"],
        }
        
    def build_graph(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        构建知识图谱
        
        Args:
            papers: 论文列表
            
        Returns:
            图谱数据
        """
        logger.info(f"[KnowledgeGraph] 构建 {len(papers)} 篇论文的知识图谱")
        
        self.nodes = []
        self.edges = []
        
        # 1. 提取论文节点
        paper_nodes = self._extract_paper_nodes(papers)
        
        # 2. 提取方法节点
        method_nodes, method_edges = self._extract_method_nodes(papers)
        
        # 3. 提取数据集节点
        dataset_nodes, dataset_edges = self._extract_dataset_nodes(papers)
        
        # 4. 提取论文相似关系
        similarity_edges = self._extract_similarity_edges(papers)
        
        # 合并所有节点和边
        self.nodes = paper_nodes + method_nodes + dataset_nodes
        self.edges = method_edges + dataset_edges + similarity_edges
        
        # 5. 计算节点重要性
        importance = self._calculate_importance()
        
        # 6. 生成类别
        self.categories = [
            {"name": "论文", "itemStyle": {"color": "#5470C6"}},
            {"name": "方法", "itemStyle": {"color": "#91CC75"}},
            {"name": "数据集", "itemStyle": {"color": "#FAC858"}},
        ]
        
        # 更新节点大小
        for node in self.nodes:
            node["symbolSize"] = 20 + importance.get(node["id"], 0) * 30
            node["importance"] = importance.get(node["id"], 0)
        
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "categories": self.categories,
            "statistics": self._calculate_statistics()
        }
    
    def _extract_paper_nodes(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取论文节点"""
        nodes = []
        
        for i, paper in enumerate(papers):
            # 提取年份
            year = "N/A"
            if paper.get("published"):
                year = paper["published"][:4]
            
            # 提取作者
            authors = []
            for author in paper.get("authors", [])[:5]:  # 保存更多作者
                if isinstance(author, dict):
                    authors.append(author.get("name", ""))
                elif isinstance(author, str):
                    authors.append(author)
            
            # 提取完整摘要
            full_summary = paper.get("summary", "")
            if not full_summary:
                full_summary = paper.get("abstract", "")
            
            node = {
                "id": f"paper_{i}",
                "name": paper.get("title", "未知标题")[:60],
                "category": 0,  # 论文类别
                "type": "paper",
                "full_title": paper.get("title", ""),
                "authors": authors,
                "year": year,
                "arxiv_id": paper.get("arxiv_id", ""),
                "summary": full_summary[:300] if full_summary else "",
                "full_summary": full_summary,  # 保存完整摘要
                "value": 1
            }
            nodes.append(node)
        
        return nodes
    
    def _extract_method_nodes(self, papers: List[Dict[str, Any]]) -> tuple:
        """提取方法节点和关系"""
        nodes = []
        edges = []
        method_count = defaultdict(int)
        paper_methods = defaultdict(list)
        
        # 检测每篇论文使用的方法
        for i, paper in enumerate(papers):
            text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
            
            for method, keywords in self.method_keywords.items():
                for kw in keywords:
                    if kw in text:
                        method_count[method] += 1
                        paper_methods[i].append(method)
                        break
        
        # 创建方法节点
        for method, count in method_count.items():
            nodes.append({
                "id": f"method_{method.lower().replace(' ', '_').replace('/', '_')}",
                "name": method,
                "category": 1,  # 方法类别
                "type": "method",
                "count": count,
                "value": count
            })
        
        # 创建论文-方法边
        for paper_idx, methods in paper_methods.items():
            for method in set(methods):
                method_id = f"method_{method.lower().replace(' ', '_').replace('/', '_')}"
                edges.append({
                    "source": f"paper_{paper_idx}",
                    "target": method_id,
                    "value": 1,
                    "lineStyle": {"color": "#91CC75", "width": 1}
                })
        
        return nodes, edges
    
    def _extract_dataset_nodes(self, papers: List[Dict[str, Any]]) -> tuple:
        """提取数据集节点和关系"""
        nodes = []
        edges = []
        dataset_count = defaultdict(int)
        paper_datasets = defaultdict(list)
        
        # 检测每篇论文使用的数据集
        for i, paper in enumerate(papers):
            text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
            
            for dataset, keywords in self.dataset_keywords.items():
                for kw in keywords:
                    if kw in text:
                        dataset_count[dataset] += 1
                        paper_datasets[i].append(dataset)
                        break
        
        # 创建数据集节点
        for dataset, count in dataset_count.items():
            nodes.append({
                "id": f"dataset_{dataset.lower().replace(' ', '_')}",
                "name": dataset,
                "category": 2,  # 数据集类别
                "type": "dataset",
                "count": count,
                "value": count
            })
        
        # 创建论文-数据集边
        for paper_idx, datasets in paper_datasets.items():
            for dataset in set(datasets):
                dataset_id = f"dataset_{dataset.lower().replace(' ', '_')}"
                edges.append({
                    "source": f"paper_{paper_idx}",
                    "target": dataset_id,
                    "value": 1,
                    "lineStyle": {"color": "#FAC858", "width": 1}
                })
        
        return nodes, edges
    
    def _extract_similarity_edges(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取论文相似关系"""
        edges = []
        
        # 基于标题关键词计算相似度
        for i in range(len(papers)):
            for j in range(i + 1, min(i + 20, len(papers))):  # 限制比较范围
                title1 = papers[i].get("title", "").lower()
                title2 = papers[j].get("title", "").lower()
                
                # 提取关键词
                words1 = set(re.findall(r'\b[a-zA-Z]{4,}\b', title1))
                words2 = set(re.findall(r'\b[a-zA-Z]{4,}\b', title2))
                
                # 计算交集
                common = words1 & words2
                
                if len(common) >= 2:
                    edges.append({
                        "source": f"paper_{i}",
                        "target": f"paper_{j}",
                        "value": len(common),
                        "lineStyle": {"color": "#5470C6", "width": len(common), "type": "dashed"}
                    })
        
        return edges
    
    def _calculate_importance(self) -> Dict[str, float]:
        """计算节点重要性（简化PageRank）"""
        in_degree = defaultdict(int)
        
        for edge in self.edges:
            in_degree[edge["target"]] += 1
        
        # 归一化
        max_degree = max(in_degree.values()) if in_degree else 1
        
        importance = {}
        for node in self.nodes:
            node_id = node["id"]
            # 方法/数据集节点根据出现次数
            if node["type"] in ["method", "dataset"]:
                importance[node_id] = node.get("count", 0) / max(10, max_degree)
            else:
                importance[node_id] = in_degree.get(node_id, 0) / max_degree
        
        return importance
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """计算统计信息"""
        paper_count = len([n for n in self.nodes if n["type"] == "paper"])
        method_count = len([n for n in self.nodes if n["type"] == "method"])
        dataset_count = len([n for n in self.nodes if n["type"] == "dataset"])
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "paper_count": paper_count,
            "method_count": method_count,
            "dataset_count": dataset_count,
            "node_types": {
                "论文": paper_count,
                "方法": method_count,
                "数据集": dataset_count
            }
        }
    
    def export_to_html(self, graph_data: Dict[str, Any], output_path: str = "knowledge_graph_enhanced.html") -> str:
        """导出为ECharts HTML可视化"""
        
        # 转换数据格式
        nodes_json = json.dumps(graph_data["nodes"], ensure_ascii=False)
        edges_json = json.dumps(graph_data["edges"], ensure_ascii=False)
        categories_json = json.dumps(graph_data["categories"], ensure_ascii=False)
        stats = graph_data["statistics"]
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>论文知识图谱 - ECharts</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
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
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .header h1 {{
            font-size: 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            color: #a0a0a0;
            margin-top: 0.5rem;
        }}
        
        .container {{
            display: flex;
            height: calc(100vh - 100px);
        }}
        
        #graph {{
            flex: 1;
            min-height: 600px;
        }}
        
        .sidebar {{
            width: 300px;
            background: rgba(255,255,255,0.03);
            padding: 1.5rem;
            overflow-y: auto;
            border-left: 1px solid rgba(255,255,255,0.1);
        }}
        
        .stats-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        
        .stats-card h3 {{
            font-size: 0.9rem;
            color: #a0a0a0;
            margin-bottom: 0.5rem;
        }}
        
        .stats-card .value {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .legend {{
            margin-top: 1rem;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 0.5rem 0;
        }}
        
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }}
        
        .controls {{
            margin-top: 1.5rem;
        }}
        
        .control-btn {{
            width: 100%;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            background: rgba(102, 126, 234, 0.2);
            border: 1px solid rgba(102, 126, 234, 0.3);
            color: #667eea;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s;
        }}
        
        .control-btn:hover {{
            background: rgba(102, 126, 234, 0.3);
        }}
        
        .tooltip-content {{
            max-width: 400px;
        }}
        
        .tooltip-title {{
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #667eea;
        }}
        
        .tooltip-info {{
            font-size: 0.85rem;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>🕸️ 论文知识图谱</h1>
        <p>交互式可视化 · 节点可拖拽 · 点击查看详情</p>
    </header>
    
    <div class="container">
        <div id="graph"></div>
        
        <aside class="sidebar">
            <div class="stats-card">
                <h3>📊 节点统计</h3>
                <div class="value">{stats["total_nodes"]}</div>
            </div>
            
            <div class="stats-card">
                <h3>🔗 关系数量</h3>
                <div class="value">{stats["total_edges"]}</div>
            </div>
            
            <div class="legend">
                <h3>图例</h3>
                <div class="legend-item">
                    <span class="legend-color" style="background: #5470C6;"></span>
                    <span>论文 ({stats["paper_count"]})</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background: #91CC75;"></span>
                    <span>方法 ({stats["method_count"]})</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background: #FAC858;"></span>
                    <span>数据集 ({stats["dataset_count"]})</span>
                </div>
            </div>
            
            <div class="controls">
                <button class="control-btn" onclick="resetGraph()">🔄 重置视图</button>
                <button class="control-btn" onclick="highlightPapers()">📄 高亮论文</button>
                <button class="control-btn" onclick="highlightMethods()">🔬 高亮方法</button>
                <button class="control-btn" onclick="highlightDatasets()">📊 高亮数据集</button>
            </div>
        </aside>
    </div>
    
    <script>
        // 数据
        const nodes = {nodes_json};
        const edges = {edges_json};
        const categories = {categories_json};
        
        // 初始化图表
        const chart = echarts.init(document.getElementById('graph'));
        
        // 配置项
        const option = {{
            tooltip: {{
                trigger: 'item',
                formatter: function(params) {{
                    if (params.dataType === 'node') {{
                        const node = params.data;
                        let html = '<div class="tooltip-content">';
                        html += '<div class="tooltip-title">' + node.name + '</div>';
                        
                        if (node.type === 'paper') {{
                            html += '<div class="tooltip-info">';
                            html += '<p>📅 年份: ' + (node.year || 'N/A') + '</p>';
                            html += '<p>👥 作者: ' + (node.authors ? node.authors.slice(0, 3).join(', ') : 'N/A') + '</p>';
                            if (node.summary) {{
                                html += '<p style="margin-top: 0.5rem;">📝 ' + node.summary.substring(0, 150) + '...</p>';
                            }}
                            html += '</div>';
                        }} else if (node.type === 'method') {{
                            html += '<div class="tooltip-info">';
                            html += '<p>📊 出现次数: ' + (node.count || 0) + '</p>';
                            html += '</div>';
                        }} else if (node.type === 'dataset') {{
                            html += '<div class="tooltip-info">';
                            html += '<p>📊 使用次数: ' + (node.count || 0) + '</p>';
                            html += '</div>';
                        }}
                        
                        html += '</div>';
                        return html;
                    }}
                    return '';
                }}
            }},
            legend: [{{
                data: categories.map(c => c.name),
                textStyle: {{ color: '#a0a0a0' }}
            }}],
            series: [{{
                type: 'graph',
                layout: 'force',
                data: nodes,
                links: edges,
                categories: categories,
                roam: true,
                draggable: true,
                label: {{
                    show: true,
                    position: 'right',
                    formatter: '{{b}}',
                    fontSize: 10,
                    color: '#e0e0e0'
                }},
                labelLayout: {{
                    hideOverlap: true
                }},
                scaleLimit: {{
                    min: 0.4,
                    max: 2
                }},
                lineStyle: {{
                    opacity: 0.6
                }},
                emphasis: {{
                    focus: 'adjacency',
                    lineStyle: {{
                        width: 3
                    }}
                }},
                force: {{
                    repulsion: 200,
                    edgeLength: [50, 150],
                    gravity: 0.1
                }}
            }}]
        }};
        
        chart.setOption(option);
        
        // 点击事件 - 显示论文详情
        chart.on('click', function(params) {{
            if (params.dataType === 'node' && params.data.type === 'paper') {{
                showPaperDetail(params.data);
            }}
        }});
        
        // 显示论文详情弹窗
        function showPaperDetail(paper) {{
            // 创建弹窗
            const modal = document.createElement('div');
            modal.id = 'paper-detail-modal';
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                animation: fadeIn 0.3s;
            `;
            
            // 弹窗内容
            const content = document.createElement('div');
            content.style.cssText = `
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                border-radius: 16px;
                padding: 2rem;
                max-width: 800px;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 20px 60px rgba(0,0,0,0.5);
                border: 1px solid rgba(255,255,255,0.1);
                position: relative;
            `;
            
            // 关闭按钮
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '✕';
            closeBtn.style.cssText = `
                position: absolute;
                top: 1rem;
                right: 1rem;
                background: rgba(255,255,255,0.1);
                border: none;
                color: #e0e0e0;
                font-size: 1.5rem;
                cursor: pointer;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                transition: all 0.3s;
            `;
            closeBtn.onmouseover = () => closeBtn.style.background = 'rgba(255,255,255,0.2)';
            closeBtn.onmouseout = () => closeBtn.style.background = 'rgba(255,255,255,0.1)';
            closeBtn.onclick = () => modal.remove();
            
            // 论文内容
            content.innerHTML = `
                <h2 style="font-size: 1.5rem; margin-bottom: 1.5rem; color: #667eea; line-height: 1.4;">
                    ${{paper.name || paper.full_title || '未知标题'}}
                </h2>
                
                <div style="display: grid; gap: 1rem; margin-bottom: 1.5rem;">
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 200px;">
                            <div style="color: #a0a0a0; font-size: 0.85rem; margin-bottom: 0.25rem;">📅 发表时间</div>
                            <div style="font-size: 1.1rem;">${{paper.year || 'N/A'}}</div>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <div style="color: #a0a0a0; font-size: 0.85rem; margin-bottom: 0.25rem;">📄 arXiv ID</div>
                            <div style="font-size: 1.1rem;">${{paper.arxiv_id || 'N/A'}}</div>
                        </div>
                    </div>
                    
                    <div>
                        <div style="color: #a0a0a0; font-size: 0.85rem; margin-bottom: 0.25rem;">👥 作者</div>
                        <div style="font-size: 1rem; line-height: 1.5;">${{(paper.authors && paper.authors.length > 0) ? paper.authors.join(', ') : '未知作者'}}</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 1.5rem;">
                    <div style="color: #a0a0a0; font-size: 0.85rem; margin-bottom: 0.5rem;">📝 摘要</div>
                    <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; line-height: 1.6; font-size: 0.95rem;">
                        ${{paper.summary || paper.full_summary || '暂无摘要'}}
                    </div>
                </div>
                
                ${{paper.arxiv_id ? `
                <div style="margin-top: 1.5rem;">
                    <a href="https://arxiv.org/abs/${{paper.arxiv_id}}" 
                       target="_blank"
                       style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; font-weight: 600; transition: transform 0.3s;">
                        📖 查看完整论文 (arXiv)
                    </a>
                </div>
                ` : ''}}
            `;
            
            content.appendChild(closeBtn);
            modal.appendChild(content);
            document.body.appendChild(modal);
            
            // 点击背景关闭
            modal.onclick = function(e) {{
                if (e.target === modal) {{
                    modal.remove();
                }}
            }};
            
            // ESC键关闭
            document.addEventListener('keydown', function escHandler(e) {{
                if (e.key === 'Escape') {{
                    modal.remove();
                    document.removeEventListener('keydown', escHandler);
                }}
            }});
        }}
        
        // 响应式
        window.addEventListener('resize', () => {{
            chart.resize();
        }});
        
        // 控制函数
        function resetGraph() {{
            chart.dispatchAction({{
                type: 'restore'
            }});
        }}
        
        function highlightPapers() {{
            chart.dispatchAction({{
                type: 'highlight',
                seriesIndex: 0,
                dataIndex: nodes
                    .map((n, i) => n.type === 'paper' ? i : -1)
                    .filter(i => i >= 0)
            }});
        }}
        
        function highlightMethods() {{
            chart.dispatchAction({{
                type: 'highlight',
                seriesIndex: 0,
                dataIndex: nodes
                    .map((n, i) => n.type === 'method' ? i : -1)
                    .filter(i => i >= 0)
            }});
        }}
        
        function highlightDatasets() {{
            chart.dispatchAction({{
                type: 'highlight',
                seriesIndex: 0,
                dataIndex: nodes
                    .map((n, i) => n.type === 'dataset' ? i : -1)
                    .filter(i => i >= 0)
            }});
        }}
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"[KnowledgeGraph] ECharts HTML导出: {output_path}")
        
        return output_path
