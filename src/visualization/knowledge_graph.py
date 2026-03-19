"""
知识图谱可视化模块
构建论文关系图谱，支持交互式可视化
"""

from typing import Dict, Any, List, Tuple
from collections import defaultdict
import json
from src.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeGraph:
    """
    论文知识图谱
    
    功能：
    1. 构建引用网络
    2. 提取方法/数据集/创新点
    3. 生成可视化数据
    """
    
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.clusters = defaultdict(list)
        
    def build_graph(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        构建知识图谱
        
        Args:
            papers: 论文列表
            
        Returns:
            图谱数据（用于可视化）
        """
        logger.info(f"[KnowledgeGraph] 构建 {len(papers)} 篇论文的知识图谱")
        
        # 1. 提取实体节点
        self._extract_nodes(papers)
        
        # 2. 构建关系边
        self._extract_edges(papers)
        
        # 3. 识别聚类
        self._identify_clusters()
        
        # 4. 计算节点重要性
        pagerank = self._calculate_importance()
        
        # 5. 生成可视化数据
        viz_data = self._generate_visualization_data(pagerank)
        
        return viz_data
    
    def _extract_nodes(self, papers: List[Dict[str, Any]]):
        """提取节点"""
        # 论文节点
        for i, paper in enumerate(papers):
            node = {
                "id": f"paper_{i}",
                "type": "paper",
                "label": paper.get("title", "未知标题")[:50],
                "full_title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "year": paper.get("published", "")[:4] if paper.get("published") else "N/A",
                "arxiv_id": paper.get("arxiv_id", ""),
                "summary": paper.get("summary", "")[:200]
            }
            self.nodes.append(node)
        
        # 方法节点
        methods = set()
        for paper in papers:
            summary = paper.get("summary", "").lower()
            if "transformer" in summary:
                methods.add("Transformer")
            if "bert" in summary or "gpt" in summary:
                methods.add("BERT/GPT")
            if "reinforcement learning" in summary:
                methods.add("Reinforcement Learning")
            if "cnn" in summary or "convolutional" in summary:
                methods.add("CNN")
            if "rnn" in summary or "recurrent" in summary:
                methods.add("RNN")
            if "attention" in summary:
                methods.add("Attention")
            if "multimodal" in summary:
                methods.add("Multimodal")
        
        for method in methods:
            self.nodes.append({
                "id": f"method_{method.lower().replace('/', '_')}",
                "type": "method",
                "label": method
            })
        
        # 数据集节点
        datasets = set()
        for paper in papers:
            summary = paper.get("summary", "").lower()
            if "wmt" in summary:
                datasets.add("WMT")
            if "imagenet" in summary:
                datasets.add("ImageNet")
            if "coco" in summary:
                datasets.add("COCO")
            if "librispeech" in summary:
                datasets.add("LibriSpeech")
            if "common voice" in summary:
                datasets.add("Common Voice")
        
        for dataset in datasets:
            self.nodes.append({
                "id": f"dataset_{dataset.lower().replace(' ', '_')}",
                "type": "dataset",
                "label": dataset
            })
    
    def _extract_edges(self, papers: List[Dict[str, Any]]):
        """构建边"""
        # 论文-方法关系
        for i, paper in enumerate(papers):
            summary = paper.get("summary", "").lower()
            paper_id = f"paper_{i}"
            
            # 检查方法
            if "transformer" in summary:
                self.edges.append({
                    "source": paper_id,
                    "target": "method_transformer",
                    "type": "uses"
                })
            if "bert" in summary or "gpt" in summary:
                self.edges.append({
                    "source": paper_id,
                    "target": "method_bert_gpt",
                    "type": "uses"
                })
            if "reinforcement learning" in summary:
                self.edges.append({
                    "source": paper_id,
                    "target": "method_reinforcement_learning",
                    "type": "uses"
                })
            if "attention" in summary:
                self.edges.append({
                    "source": paper_id,
                    "target": "method_attention",
                    "type": "uses"
                })
            
            # 检查数据集
            if "wmt" in summary:
                self.edges.append({
                    "source": paper_id,
                    "target": "dataset_wmt",
                    "type": "evaluates_on"
                })
            if "librispeech" in summary:
                self.edges.append({
                    "source": paper_id,
                    "target": "dataset_librispeech",
                    "type": "evaluates_on"
                })
        
        # 论文-论文相似关系（基于关键词）
        for i, paper1 in enumerate(papers[:20]):
            for j, paper2 in enumerate(papers[i+1:i+21], i+1):
                # 简单相似度：共同关键词
                kw1 = set(paper1.get("title", "").lower().split())
                kw2 = set(paper2.get("title", "").lower().split())
                common = kw1 & kw2
                if len(common) >= 2:
                    self.edges.append({
                        "source": f"paper_{i}",
                        "target": f"paper_{j}",
                        "type": "similar",
                        "weight": len(common)
                    })
    
    def _identify_clusters(self):
        """识别聚类"""
        # 基于方法聚类
        method_nodes = [n for n in self.nodes if n["type"] == "method"]
        for method_node in method_nodes:
            method_id = method_node["id"]
            # 找到使用该方法的论文
            related_papers = [
                e["source"] for e in self.edges 
                if e["target"] == method_id and e["type"] == "uses"
            ]
            if related_papers:
                self.clusters[method_id] = related_papers
    
    def _calculate_importance(self) -> Dict[str, float]:
        """计算节点重要性（简化PageRank）"""
        # 统计每个节点的入度
        in_degree = defaultdict(int)
        for edge in self.edges:
            in_degree[edge["target"]] += 1
        
        # 归一化
        max_degree = max(in_degree.values()) if in_degree else 1
        
        pagerank = {}
        for node in self.nodes:
            node_id = node["id"]
            pagerank[node_id] = in_degree.get(node_id, 0) / max_degree
        
        return pagerank
    
    def _generate_visualization_data(self, pagerank: Dict[str, float]) -> Dict[str, Any]:
        """生成可视化数据"""
        # 节点大小基于重要性
        viz_nodes = []
        for node in self.nodes:
            viz_node = {
                **node,
                "size": 20 + pagerank.get(node["id"], 0) * 40,
                "importance": pagerank.get(node["id"], 0)
            }
            viz_nodes.append(viz_node)
        
        return {
            "nodes": viz_nodes,
            "edges": self.edges,
            "clusters": dict(self.clusters),
            "statistics": {
                "total_nodes": len(viz_nodes),
                "total_edges": len(self.edges),
                "node_types": {
                    "paper": len([n for n in viz_nodes if n["type"] == "paper"]),
                    "method": len([n for n in viz_nodes if n["type"] == "method"]),
                    "dataset": len([n for n in viz_nodes if n["type"] == "dataset"])
                }
            }
        }
    
    def export_to_html(self, viz_data: Dict[str, Any], output_path: str = "knowledge_graph.html") -> str:
        """导出为HTML可视化"""
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>论文知识图谱</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }}
        #container {{
            width: 100%;
            height: 800px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .node {{
            cursor: pointer;
        }}
        .node.paper {{
            fill: #4A90E2;
        }}
        .node.method {{
            fill: #7ED321;
        }}
        .node.dataset {{
            fill: #F5A623;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        .tooltip {{
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            max-width: 300px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            pointer-events: none;
            font-size: 12px;
        }}
        .legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            margin: 5px 0;
        }}
        .legend-color {{
            display: inline-block;
            width: 15px;
            height: 15px;
            margin-right: 10px;
            border-radius: 50%;
        }}
        h1 {{
            color: #333;
            margin-bottom: 20px;
        }}
        .stats {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <h1>📚 论文知识图谱</h1>
    <div id="container"></div>
    
    <div class="legend">
        <h3>图例</h3>
        <div class="legend-item">
            <span class="legend-color" style="background: #4A90E2;"></span>
            论文节点
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #7ED321;"></span>
            方法节点
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #F5A623;"></span>
            数据集节点
        </div>
    </div>
    
    <div class="stats">
        <h3>统计信息</h3>
        <p>节点总数: {viz_data["statistics"]["total_nodes"]}</p>
        <p>关系总数: {viz_data["statistics"]["total_edges"]}</p>
        <p>论文数: {viz_data["statistics"]["node_types"]["paper"]}</p>
        <p>方法数: {viz_data["statistics"]["node_types"]["method"]}</p>
        <p>数据集数: {viz_data["statistics"]["node_types"]["dataset"]}</p>
    </div>
    
    <script>
        const data = {json.dumps(viz_data)};
        
        const width = 1200;
        const height = 800;
        
        const svg = d3.select("#container")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // 创建力导向图
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.edges).id(d => d.id))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        // 绘制边
        const link = svg.append("g")
            .selectAll("line")
            .data(data.edges)
            .enter().append("line")
            .attr("class", "link")
            .attr("stroke-width", d => d.weight || 1);
        
        // 绘制节点
        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .enter().append("circle")
            .attr("class", d => "node " + d.type)
            .attr("r", d => d.size || 15)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // 添加标签
        const label = svg.append("g")
            .selectAll("text")
            .data(data.nodes)
            .enter().append("text")
            .attr("dx", 12)
            .attr("dy", ".35em")
            .text(d => d.label)
            .style("font-size", "10px");
        
        // Tooltip
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        
        node.on("mouseover", function(event, d) {{
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(`
                <strong>${{d.label}}</strong><br>
                类型: ${{d.type}}<br>
                ${{d.summary ? '摘要: ' + d.summary.substring(0, 100) + '...' : ''}}
            `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        }})
        .on("mouseout", function(d) {{
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        }});
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});
        
        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}
        
        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}
        
        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}
    </script>
</body>
</html>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"[KnowledgeGraph] HTML导出: {output_path}")
        
        return output_path
