#!/usr/bin/env python3
"""
AI论文全自动预研助手 - 主脚本
"""

import sys
import argparse
from datetime import datetime
from src.utils.logger import get_logger
from src.agents.main_agent import PaperResearchMainAgent

logger = get_logger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI论文全自动预研助手")
    parser.add_argument("--topic", type=str, required=True, help="研究课题")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--output", type=str, default="output", help="输出目录")

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("AI论文全自动预研助手")
    logger.info("=" * 60)
    logger.info(f"研究课题: {args.topic}")
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # 加载配置
    import yaml
    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 创建主Agent
    main_agent = PaperResearchMainAgent(config)

    # 运行完整研究流程
    try:
        result = main_agent.run_full_research(args.topic)

        logger.info("=" * 60)
        logger.info("✅ 研究完成！")
        logger.info("=" * 60)
        logger.info(f"论文总数: {result['total_papers']}")
        logger.info(f"总耗时: {result['total_duration']:.2f} 秒")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ 研究失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
