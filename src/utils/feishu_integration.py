"""
飞书文档集成模块
支持创建文档、写入内容、分享文档
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FeishuDocumentManager:
    """
    飞书文档管理器
    
    功能：
    1. 创建飞书文档
    2. 写入内容到文档
    3. 分享文档给协作者
    4. 获取文档信息
    """
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        """
        初始化
        
        Args:
            app_id: 飞书应用ID（可从环境变量获取）
            app_secret: 飞书应用密钥
        """
        self.app_id = app_id or os.getenv("FEISHU_APP_ID", "cli_a9f6f82a4ff89bd9")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET", "XSGDLKj0CAPvFYJPnDQMhexOdWcxS0ON")
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None
        self.token_expires_at = None
        
    def get_access_token(self) -> str:
        """
        获取访问令牌
        
        Returns:
            access_token
        """
        # 如果token未过期，直接返回
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # 获取新token
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result["tenant_access_token"]
                # token有效期7200秒，提前5分钟过期
                expires_in = result.get("expire", 7200) - 300
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info(f"[Feishu] 获取访问令牌成功，有效期{expires_in}秒")
                return self.access_token
            else:
                logger.error(f"[Feishu] 获取访问令牌失败: {result}")
                return None
                
        except Exception as e:
            logger.error(f"[Feishu] 获取访问令牌异常: {e}")
            return None
    
    def create_document(self, title: str, folder_token: str = None) -> Dict[str, Any]:
        """
        创建飞书文档
        
        Args:
            title: 文档标题
            folder_token: 文件夹token（可选）
            
        Returns:
            创建结果
        """
        logger.info(f"[Feishu] 创建文档: {title}")
        
        token = self.get_access_token()
        if not token:
            return {"success": False, "error": "获取访问令牌失败"}
        
        url = f"{self.base_url}/docx/v1/documents"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "title": title
        }
        
        if folder_token:
            data["folder_token"] = folder_token
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                doc = result.get("document", {})
                logger.info(f"[Feishu] 文档创建成功: {doc.get('document_id')}")
                return {
                    "success": True,
                    "document_id": doc.get("document_id"),
                    "title": doc.get("title"),
                    "created_at": datetime.now().isoformat()
                }
            else:
                logger.error(f"[Feishu] 创建文档失败: {result}")
                return {"success": False, "error": result.get("msg", "未知错误")}
                
        except Exception as e:
            logger.error(f"[Feishu] 创建文档异常: {e}")
            return {"success": False, "error": str(e)}
    
    def write_content(self, document_id: str, content: str) -> Dict[str, Any]:
        """
        写入内容到文档
        
        Args:
            document_id: 文档ID
            content: 文档内容（Markdown格式）
            
        Returns:
            写入结果
        """
        logger.info(f"[Feishu] 写入内容到文档: {document_id}")
        
        token = self.get_access_token()
        if not token:
            return {"success": False, "error": "获取访问令牌失败"}
        
        # 将Markdown转换为飞书文档块
        blocks = self._markdown_to_blocks(content)
        
        url = f"{self.base_url}/docx/v1/documents/{document_id}/blocks/batch_update"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "requests": [
                {
                    "request_type": "InsertBlocksRequestType",
                    "insert_blocks": {
                        "payload": json.dumps({
                            "index": 0,
                            "children": blocks
                        }),
                        "location": {
                            "zone_id": document_id,
                            "index": 0
                        }
                    }
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"[Feishu] 内容写入成功")
                return {
                    "success": True,
                    "document_id": document_id,
                    "content_length": len(content)
                }
            else:
                logger.error(f"[Feishu] 写入内容失败: {result}")
                return {"success": False, "error": result.get("msg", "未知错误")}
                
        except Exception as e:
            logger.error(f"[Feishu] 写入内容异常: {e}")
            return {"success": False, "error": str(e)}
    
    def _markdown_to_blocks(self, markdown: str) -> List[Dict[str, Any]]:
        """
        将Markdown转换为飞书文档块
        
        Args:
            markdown: Markdown文本
            
        Returns:
            飞书文档块列表
        """
        blocks = []
        lines = markdown.split('\n')
        
        for line in lines:
            if line.startswith('# '):
                # 一级标题
                blocks.append({
                    "block_type": 3,  # heading1
                    "heading1": {
                        "elements": [{"text_run": {"content": line[2:]}}]
                    }
                })
            elif line.startswith('## '):
                # 二级标题
                blocks.append({
                    "block_type": 4,  # heading2
                    "heading2": {
                        "elements": [{"text_run": {"content": line[3:]}}]
                    }
                })
            elif line.startswith('### '):
                # 三级标题
                blocks.append({
                    "block_type": 5,  # heading3
                    "heading3": {
                        "elements": [{"text_run": {"content": line[4:]}}]
                    }
                })
            elif line.strip():
                # 普通段落
                blocks.append({
                    "block_type": 2,  # text
                    "text": {
                        "elements": [{"text_run": {"content": line}}]
                    }
                })
        
        return blocks
    
    def share_document(self, document_id: str, user_ids: List[str], permission: str = "view") -> Dict[str, Any]:
        """
        分享文档
        
        Args:
            document_id: 文档ID
            user_ids: 用户ID列表
            permission: 权限类型（view/edit）
            
        Returns:
            分享结果
        """
        logger.info(f"[Feishu] 分享文档: {document_id}")
        
        token = self.get_access_token()
        if not token:
            return {"success": False, "error": "获取访问令牌失败"}
        
        url = f"{self.base_url}/drive/v1/permissions/{document_id}/members"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        results = []
        for user_id in user_ids:
            data = {
                "member_type": "openid",
                "member_id": user_id,
                "perm": permission
            }
            
            try:
                response = requests.post(url, headers=headers, json=data)
                result = response.json()
                results.append({
                    "user_id": user_id,
                    "success": result.get("code") == 0
                })
            except Exception as e:
                results.append({
                    "user_id": user_id,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"[Feishu] 分享完成: {sum(1 for r in results if r['success'])}/{len(results)}")
        
        return {
            "success": all(r["success"] for r in results),
            "results": results
        }
    
    def send_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        发送消息给用户
        
        Args:
            user_id: 用户ID
            message: 消息内容
            
        Returns:
            发送结果
        """
        logger.info(f"[Feishu] 发送消息给用户: {user_id}")
        
        token = self.get_access_token()
        if not token:
            return {"success": False, "error": "获取访问令牌失败"}
        
        url = f"{self.base_url}/im/v1/messages?receive_id_type=user_id"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "receive_id": user_id,
            "msg_type": "text",
            "content": json.dumps({"text": message})
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"[Feishu] 消息发送成功")
                return {"success": True}
            else:
                logger.error(f"[Feishu] 发送消息失败: {result}")
                return {"success": False, "error": result.get("msg", "未知错误")}
                
        except Exception as e:
            logger.error(f"[Feishu] 发送消息异常: {e}")
            return {"success": False, "error": str(e)}


# 导入timedelta
from datetime import timedelta
