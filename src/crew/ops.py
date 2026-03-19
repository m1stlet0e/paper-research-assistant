"""
Operations Officer (Ops) - 运维官
负责：变更审计、防漂移、飞书文档管理、通知推送
"""

from typing import Dict, Any, List
from datetime import datetime
import json
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OperationsOfficer:
    """
    运维官Agent
    
    职责：
    1. 变更审计（记录所有修改）
    2. 防漂移（检测异常变更）
    3. 飞书文档管理（创建、写入、分享）
    4. 通知推送（飞书消息）
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.change_log = []
        self.drift_score = 0.0
        
    def audit_change(self, change_type: str, before: Any, after: Any, reason: str = "") -> Dict[str, Any]:
        """
        审计变更
        
        Args:
            change_type: 变更类型
            before: 变更前状态
            after: 变更后状态
            reason: 变更原因
            
        Returns:
            审计记录
        """
        record = {
            "change_id": f"change_{len(self.change_log) + 1}",
            "change_type": change_type,
            "before": before,
            "after": after,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "approved": True  # 默认批准，实际应该有人工审核
        }
        
        self.change_log.append(record)
        
        logger.info(f"[Ops] 变更审计: {change_type}")
        
        return record
    
    def detect_drift(self, expected_state: Dict[str, Any], actual_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测漂移
        
        Args:
            expected_state: 预期状态
            actual_state: 实际状态
            
        Returns:
            漂移检测结果
        """
        drifts = []
        
        # 检查关键字段
        for key in expected_state:
            if key not in actual_state:
                drifts.append({
                    "type": "missing",
                    "field": key,
                    "expected": expected_state[key],
                    "actual": None
                })
            elif expected_state[key] != actual_state[key]:
                drifts.append({
                    "type": "mismatch",
                    "field": key,
                    "expected": expected_state[key],
                    "actual": actual_state[key]
                })
        
        # 计算漂移分数
        if len(expected_state) > 0:
            self.drift_score = len(drifts) / len(expected_state)
        else:
            self.drift_score = 0.0
        
        result = {
            "has_drift": len(drifts) > 0,
            "drift_score": self.drift_score,
            "drifts": drifts,
            "timestamp": datetime.now().isoformat()
        }
        
        if result["has_drift"]:
            logger.warning(f"[Ops] 检测到漂移: {len(drifts)} 个问题")
        else:
            logger.info("[Ops] 无漂移检测")
        
        return result
    
    def write_to_feishu(self, doc_token: str, content: str, title: str = "") -> Dict[str, Any]:
        """
        写入飞书文档
        
        Args:
            doc_token: 文档token
            content: 文档内容
            title: 文档标题
            
        Returns:
            写入结果
        """
        logger.info(f"[Ops] 写入飞书文档: {doc_token}")
        
        # 使用Feishu API写入
        # 这里需要调用实际的飞书API
        # 暂时返回模拟结果
        
        result = {
            "success": True,
            "doc_token": doc_token,
            "title": title,
            "content_length": len(content),
            "written_at": datetime.now().isoformat()
        }
        
        # 记录变更
        self.audit_change(
            "feishu_write",
            None,
            {"doc_token": doc_token, "title": title},
            "写入综述到飞书文档"
        )
        
        return result
    
    def create_feishu_doc(self, title: str, folder_token: str = None) -> Dict[str, Any]:
        """
        创建飞书文档
        
        Args:
            title: 文档标题
            folder_token: 文件夹token（可选）
            
        Returns:
            创建结果
        """
        logger.info(f"[Ops] 创建飞书文档: {title}")
        
        # 模拟创建文档
        # 实际应该调用飞书API
        
        result = {
            "success": True,
            "doc_token": f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "folder_token": folder_token,
            "created_at": datetime.now().isoformat()
        }
        
        return result
    
    def share_feishu_doc(self, doc_token: str, users: List[str] = None, permission: str = "view") -> Dict[str, Any]:
        """
        分享飞书文档
        
        Args:
            doc_token: 文档token
            users: 用户列表（可选）
            permission: 权限类型
            
        Returns:
            分享结果
        """
        logger.info(f"[Ops] 分享飞书文档: {doc_token}")
        
        result = {
            "success": True,
            "doc_token": doc_token,
            "shared_with": users or [],
            "permission": permission,
            "shared_at": datetime.now().isoformat()
        }
        
        # 记录变更
        self.audit_change(
            "feishu_share",
            None,
            {"doc_token": doc_token, "users": users, "permission": permission},
            "分享文档给协作者"
        )
        
        return result
    
    def send_feishu_notification(self, message: str, users: List[str] = None) -> Dict[str, Any]:
        """
        发送飞书通知
        
        Args:
            message: 通知消息
            users: 接收用户列表
            
        Returns:
            发送结果
        """
        logger.info("[Ops] 发送飞书通知")
        
        result = {
            "success": True,
            "message": message,
            "recipients": users or [],
            "sent_at": datetime.now().isoformat()
        }
        
        return result
    
    def save_report_locally(self, report: str, filename: str, output_dir: str = "output") -> Dict[str, Any]:
        """
        保存报告到本地
        
        Args:
            report: 报告内容
            filename: 文件名
            output_dir: 输出目录
            
        Returns:
            保存结果
        """
        logger.info(f"[Ops] 保存报告: {filename}")
        
        # 创建目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存文件
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        result = {
            "success": True,
            "filepath": filepath,
            "size": os.path.getsize(filepath),
            "saved_at": datetime.now().isoformat()
        }
        
        return result
    
    def generate_change_report(self) -> str:
        """生成变更报告"""
        report = f"""# 变更审计报告

## 概览
- 总变更数: {len(self.change_log)}
- 漂移分数: {self.drift_score:.2f}
- 生成时间: {datetime.now().isoformat()}

## 变更记录

"""
        
        for change in self.change_log:
            report += f"""### {change['change_id']}
- 类型: {change['change_type']}
- 时间: {change['timestamp']}
- 原因: {change['reason']}

"""
        
        return report
    
    def export_change_log(self, filepath: str = "change_log.json"):
        """导出变更日志"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.change_log, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[Ops] 变更日志已导出: {filepath}")
