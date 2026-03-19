"""
记忆管理工具 - 使用WAL协议
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """记忆管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory_dir = config.get("memory_dir", "memory")
        self.max_entries = config.get("max_entries", 1000)
        self.deduplicate = config.get("deduplicate", True)

        # 创建记忆目录
        os.makedirs(self.memory_dir, exist_ok=True)

    def log(self, action: str, data: Dict[str, Any]) -> str:
        """记录一条记忆"""
        entry = {
            "id": f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data
        }

        # 去重
        if self.deduplicate:
            existing = self._load_memory()
            if existing and any(
                e.get("action") == action and e.get("data") == data
                for e in existing
            ):
                logger.info(f"跳过重复记忆: {action}")
                return entry["id"]

        # 保存记忆
        self._save_memory([entry])

        logger.info(f"记录记忆: {action}")

        return entry["id"]

    def load(self) -> List[Dict[str, Any]]:
        """加载所有记忆"""
        return self._load_memory()

    def _load_memory(self) -> List[Dict[str, Any]]:
        """从文件加载记忆"""
        memory_file = os.path.join(self.memory_dir, "memory.json")

        if not os.path.exists(memory_file):
            return []

        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载记忆失败: {e}")
            return []

    def _save_memory(self, entries: List[Dict[str, Any]]) -> None:
        """保存记忆到文件"""
        memory_file = os.path.join(self.memory_dir, "memory.json")

        # 读取现有记忆
        existing = self._load_memory()

        # 合并记忆
        all_entries = existing + entries

        # 限制记忆数量
        if len(all_entries) > self.max_entries:
            all_entries = all_entries[-self.max_entries:]

        # 保存
        try:
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(all_entries, f, ensure_ascii=False, indent=2)
            logger.info(f"保存记忆: {len(entries)} 条")
        except Exception as e:
            logger.error(f"保存记忆失败: {e}")

    def search(self, action: str) -> List[Dict[str, Any]]:
        """搜索特定类型的记忆"""
        entries = self._load_memory()
        return [e for e in entries if e.get("action") == action]
