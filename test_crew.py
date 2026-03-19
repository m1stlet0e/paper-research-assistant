"""
测试OpenCrew多智能体协作系统
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.crew.orchestrator import Orchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_crew():
    """测试OpenCrew系统"""
    
    print("""
╔════════════════════════════════════════════════════════════╗
║       OpenCrew多智能体协作系统 - 测试                     ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # 配置
    config = {
        "max_papers": 10,
        "output_dir": "output",
        "feishu_collaborators": []
    }
    
    # 创建编排器
    orchestrator = Orchestrator(config)
    
    # 测试课题
    topic = "大模型在K12英语口语教学中的应用"
    
    print(f"测试课题: {topic}")
    print("-" * 60)
    
    # Phase 1: 测试CoS意图分析
    print("\n[Phase 1] CoS意图分析...")
    analysis = orchestrator.cos.analyze_intent(topic)
    print(f"  研究类型: {analysis['research_type']}")
    print(f"  核心问题: {analysis['core_questions'][0]}")
    print(f"  研究范围: 论文数{analysis['scope']['max_papers']}, 时间{analysis['scope']['time_range']}")
    
    # Phase 2: 测试CTO技术方案
    print("\n[Phase 2] CTO技术方案...")
    tech_stack = orchestrator.cto.decide_tech_stack(analysis)
    print(f"  数据源: {[s['name'] for s in tech_stack['data_sources']]}")
    print(f"  输出格式: {tech_stack['output_formats']}")
    
    # Phase 3: 测试Builder文献检索
    print("\n[Phase 3] Builder文献检索...")
    orchestrator.context["keywords"] = ["大模型", "英语教学", "K12"]
    search_result = orchestrator.builder.execute_search(tech_stack, analysis["scope"])
    print(f"  检索到论文: {search_result['final_count']}篇")
    
    if search_result['final_count'] > 0:
        # Phase 4: 测试Builder论文解析
        print("\n[Phase 4] Builder论文解析...")
        parse_result = orchestrator.builder.parse_papers_parallel()
        print(f"  解析完成: {parse_result['total_parsed']}篇")
        
        # Phase 5: 测试Builder引用分析
        print("\n[Phase 5] Builder引用分析...")
        citation_result = orchestrator.builder.analyze_citations()
        print(f"  引用网络节点: {citation_result['citation_network']['statistics']['total_nodes']}")
        
        # Phase 6: 测试Builder综述撰写
        print("\n[Phase 6] Builder综述撰写...")
        review = orchestrator.builder.write_review(analysis['core_questions'])
        print(f"  综述章节: {review.get('sections_count', 0)}个")
        print(f"  引用数量: {review.get('citations_count', 0)}条")
        
        # Phase 7: 测试CTO质量审查
        print("\n[Phase 7] CTO质量审查...")
        review_result = orchestrator.cto.review_review(review, orchestrator.builder.papers)
        print(f"  综合评分: {review_result['overall_score']:.1f}/10")
        print(f"  审查通过: {'是' if review_result['passed'] else '否'}")
        
        # Phase 8: 测试Builder报告生成
        print("\n[Phase 8] Builder报告生成...")
        reports = orchestrator.builder.generate_report(review, tech_stack['output_formats'])
        print(f"  生成格式: {list(reports.keys())}")
        
        # Phase 9: 测试Ops变更审计
        print("\n[Phase 9] Ops变更审计...")
        orchestrator.ops.audit_change(
            "test_complete",
            None,
            {"papers": search_result['final_count']},
            "测试完成"
        )
        print(f"  变更记录: {len(orchestrator.ops.change_log)}条")
        
    else:
        print("  ⚠️ 未检索到论文，跳过后续测试")
    
    # 输出系统状态
    print("\n" + "=" * 60)
    print("系统状态:")
    status = orchestrator.get_status()
    print(f"  研究课题: {status['context']['topic']}")
    print(f"  研究类型: {status['context']['research_type']}")
    print(f"  论文数量: {len(status['context']['papers'])}")
    print(f"  经验沉淀: {status['experiences_count']}条")
    print(f"  变更记录: {status['change_log_count']}条")
    print(f"  漂移分数: {status['drift_score']:.2f}")
    
    print("\n✅ 测试完成!")
    
    return orchestrator


if __name__ == "__main__":
    test_crew()
