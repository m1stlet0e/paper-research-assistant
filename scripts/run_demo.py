#!/usr/bin/env python3
"""
演示脚本 - 运行完整的研究流程
生成真实的研究报告和可视化内容
"""

import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crew.orchestrator import Orchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)

def run_demo(topic: str = "大模型在K12英语口语教学中的应用"):
    """
    运行演示
    
    Args:
        topic: 研究课题
    """
    print(f"""
╔════════════════════════════════════════════════════════════╗
║       🦞 AI论文预研助手 - 演示模式                        ║
╠════════════════════════════════════════════════════════════╣
║  研究课题: {topic}
╚════════════════════════════════════════════════════════════╝
    """)
    
    # 初始化编排器
    config = {
        "max_papers": 20,  # 演示模式使用较少论文
        "output_dir": "output",
        "data_sources": ["arxiv"]
    }
    
    orchestrator = Orchestrator(config)
    
    print("📊 开始研究流程...\n")
    
    # 运行研究
    start_time = time.time()
    
    try:
        result = orchestrator.run_research(
            topic=topic,
            auto_confirm=True
        )
        
        duration = time.time() - start_time
        
        # 显示结果
        print(f"""
╔════════════════════════════════════════════════════════════╗
║       ✅ 研究完成                                          ║
╠════════════════════════════════════════════════════════════╣
║  📄 论文数量: {len(result['papers'])}
║  ⏱️  耗时: {duration:.1f}秒
║  📊 质量评分: {result['quality_score']:.1f}/10
║  
║  📁 生成文件:
║     - output/research_report.md (研究报告)
║     - output/research_report.tex (LaTeX报告)
║     - output/knowledge_graph.html (知识图谱)
║     - output/comparison_matrix.html (对比矩阵)
║     - output/qa_demo.html (智能问答)
╚════════════════════════════════════════════════════════════╝
        """)
        
        # 显示论文列表
        print("\n📚 检索到的论文:\n")
        for i, paper in enumerate(result['papers'][:10], 1):
            title = paper.get('title', '未知标题')[:60]
            print(f"  {i}. {title}...")
        
        if len(result['papers']) > 10:
            print(f"\n  ... 还有 {len(result['papers']) - 10} 篇论文")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 研究失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # 支持命令行参数
    topic = sys.argv[1] if len(sys.argv) > 1 else "大模型在K12英语口语教学中的应用"
    run_demo(topic)
