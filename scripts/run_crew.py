"""
OpenCrew 多智能体协作系统 - 主入口
基于Agent Swarm模式的论文预研助手
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from datetime import datetime
from src.crew.orchestrator import Orchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description='AI论文预研助手 - OpenCrew多智能体协作系统')
    parser.add_argument('--topic', type=str, required=True, help='研究课题')
    parser.add_argument('--max-papers', type=int, default=50, help='最大论文数')
    parser.add_argument('--output-dir', type=str, default='output', help='输出目录')
    parser.add_argument('--auto-confirm', action='store_true', help='自动确认，跳过用户交互')
    parser.add_argument('--feishu', action='store_true', help='写入飞书文档')
    parser.add_argument('--parallel-agents', type=int, default=3, help='并行Agent数量')
    
    args = parser.parse_args()
    
    # 配置
    config = {
        "max_papers": args.max_papers,
        "output_dir": args.output_dir,
        "feishu_collaborators": [] if not args.feishu else ["ou_0cdbe8a5a456c32beb95d46bb00b2bc1"]
    }
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║       AI论文预研助手 - OpenCrew多智能体协作系统         ║
╠════════════════════════════════════════════════════════════╣
║  CoS (战略参谋)  →  意图对齐、研究范围确定              ║
║  CTO (技术负责人) →  技术方案、质量审查                  ║
║  Builder (执行者) →  文献检索、论文解析、综述撰写        ║
║  Ops (运维官)     →  变更审计、飞书文档、通知推送        ║
╚════════════════════════════════════════════════════════════╝

研究课题: {args.topic}
最大论文数: {args.max_papers}
并行Agent: {args.parallel_agents}
飞书文档: {'是' if args.feishu else '否'}
""")
    
    # 创建编排器
    orchestrator = Orchestrator(config)
    
    # 运行研究
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 开始研究...")
    
    result = orchestrator.run_research(
        topic=args.topic,
        auto_confirm=args.auto_confirm
    )
    
    # 输出结果
    print(f"\n{'='*60}")
    print(f"研究完成!")
    print(f"{'='*60}")
    print(f"课题: {result['topic']}")
    print(f"论文数: {len(result['papers'])}")
    print(f"质量评分: {result['quality_score']:.1f}/10")
    print(f"耗时: {result['duration']:.1f}秒")
    print(f"\n生成的报告:")
    for fmt, content in result['reports'].items():
        print(f"  - research_report.{fmt}")
    
    print(f"\n{'='*60}")
    print("系统状态:")
    status = orchestrator.get_status()
    print(f"  - 经验沉淀: {status['experiences_count']}条")
    print(f"  - 变更记录: {status['change_log_count']}条")
    print(f"  - 漂移分数: {status['drift_score']:.2f}")
    
    return result


if __name__ == "__main__":
    main()
