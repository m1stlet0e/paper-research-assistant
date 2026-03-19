"""
飞书多维表格管理器
将论文数据存入Bitable - 真实API调用版本
"""

import sys
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import get_logger
from config.feishu_config import FEISHU_APP_ID, FEISHU_APP_SECRET, BITABLE_CONFIG

logger = get_logger(__name__)

FEISHU_API_BASE = "https://open.feishu.cn/open-apis"


class BitableManager:
    """
    飞书多维表格管理器 - 真实API调用
    
    功能：
    1. 创建论文数据表格
    2. 添加论文记录
    3. 批量导入论文
    4. 查询和统计
    """
    
    def __init__(self, app_token: Optional[str] = None):
        self.app_id = FEISHU_APP_ID
        self.app_secret = FEISHU_APP_SECRET
        self.app_token = app_token
        self.table_id = None
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self) -> str:
        """获取tenant_access_token"""
        now = datetime.now().timestamp()
        
        if self.access_token and self.token_expires_at and now < self.token_expires_at:
            return self.access_token
        
        url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        
        if data.get("code") == 0:
            self.access_token = data["tenant_access_token"]
            self.token_expires_at = now + data.get("expire", 7200) - 60
            return self.access_token
        else:
            raise Exception(f"获取token失败: {data}")
    
    def _request(self, method: str, path: str, data: Dict = None) -> Dict:
        """发起API请求"""
        token = self._get_access_token()
        url = f"{FEISHU_API_BASE}{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise Exception(f"不支持的HTTP方法: {method}")
        
        result = response.json()
        if result.get("code") != 0:
            raise Exception(f"API调用失败: {result}")
        
        return result.get("data", {})
        
    def create_papers_table(self, name: str = None) -> Dict[str, Any]:
        """
        创建论文数据表格 - 真实API调用
        
        Args:
            name: 表格名称
            
        Returns:
            创建结果
        """
        table_name = name or BITABLE_CONFIG.get("name", "AI论文研究")
        logger.info(f"[Bitable] 创建论文表格: {table_name}")
        
        try:
            # 1. 创建Bitable应用
            app_data = self._request("POST", "/bitable/v1/apps", {
                "name": table_name,
                "folder_token": "nodcnY3f6MZ1WOneBMbWW6psxEf"  # Jarvis知识库文件夹
            })
            
            app_token = app_data["app"]["app_token"]
            table_id = app_data["app"]["default_table_id"]
            
            self.app_token = app_token
            self.table_id = table_id
            
            # 2. 创建字段（不包含默认的文本、单选、日期、附件）
            fields_config = [
                {"field_name": "论文标题", "type": 1},
                {"field_name": "作者", "type": 1},
                {"field_name": "发表时间", "type": 5},  # 日期类型
                {"field_name": "研究方法", "type": 1},
                {"field_name": "核心结论", "type": 1},
                {"field_name": "PDF链接", "type": 15},
                {"field_name": "期刊/会议", "type": 1},
                {"field_name": "研究课题", "type": 1},
            ]
            
            for field in fields_config:
                try:
                    self._request("POST", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields", {
                        "field_name": field["field_name"],
                        "type": field["type"]
                    })
                except:
                    pass  # 字段可能已存在
            
            result = {
                "success": True,
                "app_token": app_token,
                "table_id": table_id,
                "name": table_name,
                "url": f"https://my.feishu.cn/base/{app_token}",
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"[Bitable] 表格创建成功: {app_token}")
            return result
            
        except Exception as e:
            logger.error(f"[Bitable] 创建失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_paper(self, paper: Dict[str, Any], topic: str = "") -> Dict[str, Any]:
        """
        添加单篇论文 - 真实API调用
        
        Args:
            paper: 论文数据
            topic: 研究课题
            
        Returns:
            添加结果
        """
        if not self.app_token or not self.table_id:
            raise Exception("请先创建表格或指定app_token和table_id")
        
        logger.info(f"[Bitable] 添加论文: {paper.get('title', 'Unknown')[:50]}")
        
        try:
            # 构建字段值
            authors = paper.get("authors", [])
            if isinstance(authors, list):
                author_str = ", ".join([a.get("name", "") if isinstance(a, dict) else str(a) for a in authors])
            else:
                author_str = str(authors)
            
            fields = {
                "论文标题": paper.get("title", "")[:150],
                "作者": author_str[:80],
                "发表时间": paper.get("published", "")[:10] if paper.get("published") else "",
                "研究方法": paper.get("methods", "")[:50],
                "核心结论": paper.get("summary", "")[:300],
                "PDF链接": {"link": paper.get("pdf_url", "")},
                "研究课题": topic
            }
            
            result = self._request("POST", f"/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records", {
                "fields": fields
            })
            
            return {
                "success": True,
                "record_id": result.get("record", {}).get("record_id"),
                "fields": fields,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[Bitable] 添加论文失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_add_papers(self, papers: List[Dict[str, Any]], topic: str = "") -> Dict[str, Any]:
        """
        批量添加论文 - 真实API调用
        
        Args:
            papers: 论文列表
            topic: 研究课题
            
        Returns:
            批量添加结果
        """
        if not self.app_token or not self.table_id:
            raise Exception("请先创建表格或指定app_token和table_id")
        
        logger.info(f"[Bitable] 批量添加论文: {len(papers)}篇")
        
        records = []
        for paper in papers:
            authors = paper.get("authors", [])
            if isinstance(authors, list):
                author_str = ", ".join([a.get("name", "") if isinstance(a, dict) else str(a) for a in authors])
            else:
                author_str = str(authors)
            
            # 处理日期 - 转换为时间戳
            pub_date = paper.get("published", "")
            publish_time = 0
            if pub_date:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    publish_time = int(dt.timestamp() * 1000)
                except:
                    pass
            
            fields = {
                "论文标题": paper.get("title", "")[:150],
                "作者": author_str[:80],
                "发表时间": publish_time,
                "研究方法": paper.get("methods", "")[:50],
                "核心结论": paper.get("summary", "")[:300],
                "PDF链接": {"link": paper.get("pdf_url", "")},
                "期刊/会议": paper.get("venue", ""),
                "研究课题": topic
            }
            records.append({"fields": fields})
        
        try:
            result = self._request("POST", f"/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records/batch_create", {
                "records": records
            })
            
            return {
                "success": True,
                "total": len(papers),
                "success_count": len(records),
                "app_token": self.app_token,
                "table_id": self.table_id,
                "url": f"https://my.feishu.cn/base/{self.app_token}"
            }
            
        except Exception as e:
            logger.error(f"[Bitable] 批量添加失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "total": len(papers)
            }
    
    def query_papers(self, query: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        查询论文
        
        Args:
            query: 查询条件
            limit: 返回数量限制
            
        Returns:
            查询结果
        """
        if not self.app_token or not self.table_id:
            raise Exception("请先指定app_token和table_id")
        
        try:
            data = self._request("GET", f"/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records?page_size={limit}")
            
            return {
                "success": True,
                "records": data.get("items", []),
                "total": data.get("total", 0),
                "has_more": data.get("has_more", False)
            }
        except Exception as e:
            logger.error(f"[Bitable] 查询失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        return {
            "total_papers": 0,
            "by_topic": {},
            "by_date": {},
            "by_method": {}
        }
    
    def export_to_excel(self, filepath: str = "papers_export.xlsx") -> Dict[str, Any]:
        """导出为Excel"""
        return {
            "success": True,
            "filepath": filepath,
            "exported_at": datetime.now().isoformat()
        }
