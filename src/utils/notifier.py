"""
通知工具 - 使用Feishu API
"""

import json
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Notifier:
    """通知器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.platform = config.get("platform", "feishu")

        # Feishu配置
        self.feishu_app_id = config.get("feishu_app_id", "")
        self.feishu_app_secret = config.get("feishu_app_secret", "")
        self.feishu_target_user = config.get("feishu_target_user", "")

    def send_completion_notification(self, topic: str, total_papers: int, duration: float) -> None:
        """发送完成通知"""
        if not self.enabled:
            logger.info("通知已禁用，跳过发送")
            return

        logger.info("发送完成通知")

        message = f"""✅ AI论文预研助手 - 研究完成

📊 **研究课题：** {topic}

📈 **研究成果：**
- 📄 找到论文：{total_papers} 篇
- ⏱️ 耗时：{duration:.2f} 秒

📍 **报告位置：** output/research_report.md

---

🎉 研究完成！"""

        self._send_feishu(message)

    def send_daily_update(self, topic: str, new_papers: int) -> None:
        """发送每日更新通知"""
        if not self.enabled:
            return

        logger.info(f"发送每日更新: {new_papers} 篇新论文")

        message = f"""🔔 AI论文预研助手 - 每日更新

📊 **追踪课题：** {topic}

📰 **新发现：** {new_papers} 篇新论文

⏰ **更新时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

点击查看详细报告"""

        self._send_feishu(message)

    def _send_feishu(self, message: str) -> None:
        """发送Feishu消息"""
        try:
            # 这里应该调用Feishu API
            # 暂时只记录日志
            logger.info(f"发送Feishu消息: {message[:100]}...")

            # TODO: 实际发送
            # import requests
            # response = requests.post(
            #     "https://open.feishu.cn/open-apis/bot/v2/hook/...",
            #     json={"msg_type": "text", "content": {"text": message}}
            # )

        except Exception as e:
            logger.error(f"发送Feishu消息失败: {e}")
