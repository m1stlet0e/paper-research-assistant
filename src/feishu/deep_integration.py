"""
飞书深度集成模块 - 直接调用飞书API
实现多维表格、知识库、消息卡片的真实API调用
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import get_logger
from config.feishu_config import FEISHU_APP_ID, FEISHU_APP_SECRET, TARGET_USER_ID, BITABLE_CONFIG, WIKI_CONFIG

logger = get_logger(__name__)

# 飞书API基础URL
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

# 知识库配置
WIKI_SPACE_ID = "7618500441680219079"  # Jarvis知识库
WIKI_NODE_TOKEN = "PbHZwOzqriorj8krYG0ckVgPnjd"  # 首页节点


class FeishuDeepIntegration:
    """
    飞书深度集成 - 直接调用飞书API
    """

    def __init__(self):
        self.app_id = FEISHU_APP_ID
        self.app_secret = FEISHU_APP_SECRET
        self.target_user = TARGET_USER_ID
        self.access_token = None
        self.token_expires_at = None

    def _get_access_token(self) -> str:
        """获取tenant_access_token"""
        now = datetime.now().timestamp()
        
        # 如果有有效token，直接返回
        if self.access_token and self.token_expires_at and now < self.token_expires_at:
            return self.access_token
        
        # 获取新token
        url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result["tenant_access_token"]
                # 提前5分钟过期
                self.token_expires_at = now + result.get("expire", 7200) - 300
                logger.info("[Feishu] 获取access_token成功")
                return self.access_token
            else:
                logger.error(f"[Feishu] 获取token失败: {result}")
                raise Exception(f"获取token失败: {result.get('msg')}")
        except Exception as e:
            logger.error(f"[Feishu] 获取token异常: {e}")
            raise

    def _request(self, method: str, path: str, data: dict = None) -> dict:
        """发送API请求"""
        url = f"{FEISHU_API_BASE}{path}"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            # 调试：打印响应状态和内容
            if path.startswith('/docx'):
                logger.info(f"[Feishu] API响应状态: {response.status_code}")
                logger.info(f"[Feishu] API响应内容: {response.text[:200]}")
            
            result = response.json()
            
            if result.get("code") == 0:
                return result.get("data", {})
            else:
                logger.error(f"[Feishu] API请求失败: {result}")
                raise Exception(f"API错误 {result.get('code')}: {result.get('msg')}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"[Feishu] 网络请求失败: {e}")
            raise

    def create_and_populate_bitable(self, name: str = None, papers: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建多维表格并填充论文数据
        使用飞书Bitable API
        """
        logger.info(f"[Feishu] 创建多维表格: {name}")
        
        result = {
            "success": False,
            "app_token": None,
            "table_id": None,
            "url": None,
            "records_count": 0
        }
        
        try:
            table_name = name or BITABLE_CONFIG.get("name", "AI论文研究")
            
            # 1. 创建Bitable应用，同时创建包含所需字段的表
            # 先创建应用
            app_data = self._request("POST", "/bitable/v1/apps", {
                "name": table_name,
                "folder_token": ""
            })
            
            app_token = app_data["app"]["app_token"]
            table_id = app_data["app"]["default_table_id"]
            
            result["app_token"] = app_token
            result["table_id"] = table_id
            result["url"] = f"https://my.feishu.cn/base/{app_token}"
            
            logger.info(f"[Feishu] 多维表格创建成功: {app_token}")
            
            # 2. 创建自定义字段（跳过删除默认字段，无害且省 6 秒）
            fields_to_create = [
                {"field_name": "论文标题", "type": 1},
                {"field_name": "作者", "type": 1},
                {"field_name": "发表时间", "type": 5},
                {"field_name": "研究方法", "type": 1},
                {"field_name": "核心结论", "type": 1},
                {"field_name": "PDF链接", "type": 15},
                {"field_name": "期刊/会议", "type": 1},
                {"field_name": "研究课题", "type": 1},
            ]
            
            def _create_one_field(field):
                self._request("POST", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields", {
                    "field_name": field["field_name"],
                    "type": field["type"]
                })

            with ThreadPoolExecutor(max_workers=8) as executor:
                futs = [executor.submit(_create_one_field, f) for f in fields_to_create]
                for fut in as_completed(futs):
                    try:
                        fut.result()
                    except:
                        pass
            logger.info(f"[Feishu] 并行创建了 {len(fields_to_create)} 个字段")
            
            # 3. 添加论文记录（如果有）
            if papers and len(papers) > 0:
                fields_data = self._request("GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields")
                field_map = {f["field_name"]: f["field_id"] for f in fields_data.get("items", [])}
                logger.info(f"[Feishu] 可用字段: {list(field_map.keys())}")
                
                # batch_delete 一次删完默认空记录（省 17 秒）
                try:
                    records_data = self._request("GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records")
                    record_items = records_data.get("items", [])
                    if record_items:
                        record_ids = [r["record_id"] for r in record_items]
                        self._request("POST", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_delete", {
                            "records": record_ids
                        })
                        logger.info(f"[Feishu] 批量删除了 {len(record_ids)} 行默认空数据")
                except Exception as e:
                    logger.warning(f"[Feishu] 删除默认记录失败: {e}")
                
                # 添加记录
                records = []
                for paper in papers[:50]:  # 最多50条
                    fields = {}
                    
                    # 论文标题
                    if "论文标题" in field_map:
                        fields["论文标题"] = paper.get("title", "")[:150]
                    
                    # 作者 - 只取前3个
                    if "作者" in field_map:
                        authors = paper.get("authors", [])
                        if isinstance(authors, list):
                            author_names = []
                            for a in authors[:3]:
                                if isinstance(a, dict):
                                    author_names.append(a.get("name", ""))
                                else:
                                    author_names.append(str(a))
                            fields["作者"] = ", ".join(author_names)[:80]
                        else:
                            fields["作者"] = str(authors)[:80]
                    
                    # 发表时间 - 日期字段需要时间戳
                    if "发表时间" in field_map:
                        pub_date = paper.get("published", "")
                        if pub_date:
                            try:
                                # 解析日期字符串并转换为时间戳
                                from datetime import datetime
                                date_str = pub_date[:10] if 'T' in pub_date else pub_date[:10]
                                dt = datetime.strptime(date_str, "%Y-%m-%d")
                                fields["发表时间"] = int(dt.timestamp() * 1000)
                            except:
                                pass
                    
                    # 研究方法
                    if "研究方法" in field_map:
                        fields["研究方法"] = self._extract_methods(paper)[:50]
                    
                    # 核心结论 - 取前300字符，清理换行
                    if "核心结论" in field_map:
                        summary = paper.get("summary", "")
                        if summary:
                            summary = summary.replace("\n", " ").replace("\r", " ")
                            fields["核心结论"] = summary[:300]
                    
                    # PDF链接 - URL字段需要对象格式
                    if "PDF链接" in field_map:
                        pdf_url = paper.get("pdf_url", "")
                        if pdf_url:
                            fields["PDF链接"] = {"link": pdf_url}
                    
                    # 研究课题
                    if "研究课题" in field_map:
                        fields["研究课题"] = table_name
                    
                    if fields:
                        records.append({"fields": fields})
                
                # 批量添加记录
                if records:
                    try:
                        add_result = self._request("POST", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create", {
                            "records": records
                        })
                        result["records_count"] = len(records)
                        logger.info(f"[Feishu] 批量添加 {len(records)} 条记录成功")
                    except Exception as e:
                        logger.warning(f"[Feishu] 批量添加失败: {e}")
                        result["records_count"] = 0
            
            result["success"] = True
            
        except Exception as e:
            logger.error(f"[Feishu] 多维表格创建失败: {e}")
            result["error"] = str(e)
        
        return result

    def archive_research_to_wiki(self, topic: str, review: Dict[str, Any] = None, 
                                 papers: List[Dict[str, Any]] = None,
                                 visualizations: Dict[str, str] = None) -> Dict[str, Any]:
        """
        归档研究报告到知识库
        优先在知识库内直接创建文档；若权限不足则回退到云空间独立文档。
        两种路径都会通过 Docx Blocks API 写入正文。
        """
        logger.info(f"[Feishu] 归档研究到知识库: {topic}")
        
        result = {
            "success": False,
            "doc_id": None,
            "doc_url": None,
            "url": None,
            "papers_count": 0,
            "in_wiki": False
        }
        
        title = f"{topic[:20]}研究报告-{datetime.now().strftime('%Y-%m-%d')}"
        doc_token = None
        
        try:
            # 路径一：直接在知识库里创建节点（文档会出现在知识库目录树中）
            try:
                node_data = self._request("POST", f"/wiki/v2/spaces/{WIKI_SPACE_ID}/nodes", {
                    "obj_type": "docx",
                    "parent_node_token": WIKI_NODE_TOKEN,
                    "node_type": "origin",
                    "title": title
                })
                doc_token = node_data.get("node", {}).get("obj_token")
                result["in_wiki"] = True
                logger.info(f"[Feishu] 知识库节点创建成功: {doc_token}")
            except Exception as e:
                logger.warning(f"[Feishu] 知识库创建失败(回退到云空间): {e}")
            
            # 路径二：回退到云空间创建独立文档
            if not doc_token:
                doc_data = self._request("POST", "/docx/v1/documents", {
                    "document": {"title": title}
                })
                doc_token = doc_data["document"]["document_id"]
                logger.info(f"[Feishu] 云文档创建成功: {doc_token}")
            
            # 写入正文内容块
            blocks = self._build_doc_content_blocks(topic, review, papers)
            if blocks:
                import time
                for i in range(0, len(blocks), 50):
                    batch = blocks[i:i + 50]
                    try:
                        self._request("POST",
                            f"/docx/v1/documents/{doc_token}/blocks/{doc_token}/children",
                            {"children": batch, "index": -1}
                        )
                        logger.info(f"[Feishu] 写入内容块 {i+1}~{i+len(batch)}/{len(blocks)}")
                    except Exception as e:
                        logger.warning(f"[Feishu] 写入内容块失败(batch {i}): {e}")
                    if i + 50 < len(blocks):
                        time.sleep(0.5)
            
            result["doc_id"] = doc_token
            result["doc_url"] = f"https://my.feishu.cn/docx/{doc_token}"
            result["url"] = result["doc_url"]
            result["success"] = True
            result["papers_count"] = len(papers) if papers else 0

            try:
                self._send_detailed_report(topic, review, papers, result["doc_url"])
            except Exception as e:
                logger.warning(f"[Feishu] 发送详细报告失败: {e}")
            
        except Exception as e:
            logger.error(f"[Feishu] 知识库归档失败: {e}")
            result["error"] = str(e)
        
        return result

    def _build_doc_content_blocks(self, topic: str, review: Dict[str, Any] = None,
                                   papers: List[Dict[str, Any]] = None) -> list:
        """构建飞书文档内容块列表（Docx Blocks API 格式）
        
        block_type 与字段名映射: 2->text, 4->heading2, 5->heading3, 22->divider
        """
        BLOCK_FIELD = {2: "text", 3: "heading1", 4: "heading2", 5: "heading3"}
        blocks = []

        def _text_like(content: str, block_type: int = 2) -> dict:
            field = BLOCK_FIELD[block_type]
            return {
                "block_type": block_type,
                field: {
                    "elements": [{"text_run": {"content": content, "text_element_style": {}}}],
                    "style": {}
                }
            }

        def _divider() -> dict:
            return {"block_type": 22, "divider": {}}

        paper_count = len(papers) if papers else 0
        blocks.append(_text_like(
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  论文数量: {paper_count} 篇"
        ))
        blocks.append(_divider())

        blocks.append(_text_like("研究概述", block_type=4))
        overview = f"本报告基于AI论文预研助手自动生成，分析了 {topic} 领域的研究进展。"
        if review and isinstance(review, dict):
            summary = review.get("summary", "") or review.get("content", "")
            if summary:
                overview += "\n\n" + str(summary)[:1000]
        blocks.append(_text_like(overview))

        if papers and len(papers) > 0:
            blocks.append(_divider())
            blocks.append(_text_like(f"论文列表 ({len(papers)} 篇)", block_type=4))

            for i, paper in enumerate(papers[:20], 1):
                p_title = paper.get("title", "未知标题")[:80]
                authors = self._format_authors(paper.get("authors", []))[:60]
                published = paper.get("published", "N/A")[:10]
                p_summary = paper.get("summary", "")
                if p_summary:
                    p_summary = p_summary.replace("\n", " ")[:200]

                blocks.append(_text_like(f"{i}. {p_title}", block_type=5))
                meta = f"作者: {authors}  |  时间: {published}"
                if p_summary:
                    meta += f"\n摘要: {p_summary}"
                blocks.append(_text_like(meta))

        blocks.append(_divider())
        blocks.append(_text_like("由 AI论文预研助手 自动生成"))

        return blocks

    def _send_detailed_report(self, topic: str, review: Dict, papers: List, doc_url: str = None):
        """发送详细的研究报告给用户"""
        logger.info(f"[Feishu] 发送详细报告: {topic}")
        
        # 构建消息内容
        message = f"📚 **{topic}** 研究报告\n\n"
        
        if review:
            summary = review.get("summary", "")
            if summary:
                message += f"📝 **研究总结**: {summary[:200]}\n\n"
        
        message += f"📄 **论文数量**: {len(papers) if papers else 0} 篇\n\n"
        
        if papers:
            message += "---📖 **论文列表**---\n\n"
            for i, paper in enumerate(papers[:10], 1):
                title = paper.get("title", "未知")[:50]
                authors = paper.get("authors", [])
                if isinstance(authors, list):
                    author_str = ", ".join([a.get("name", "") if isinstance(a, dict) else str(a) for a in authors[:2]])
                else:
                    author_str = str(authors)[:30] if authors else "未知"
                published = paper.get("published", "N/A")[:10]
                
                message += f"{i}. **{title}**\n"
                message += f"   👤 {author_str} | 📅 {published}\n\n"
        
        if doc_url:
            message += f"---\n🔗 [查看完整报告]({doc_url})"
        
        # 发送消息
        msg_data = {
            "receive_id": self.target_user,
            "msg_type": "text",
            "content": json.dumps({"text": message})
        }
        
        self._request("POST", f"/im/v1/messages?receive_id_type=open_id", msg_data)


    def send_research_card(self, topic: str, papers_count: int = 0,
                          visualizations: Dict[str, str] = None) -> Dict[str, Any]:
        """
        发送研究完成消息
        使用飞书IM API
        """
        logger.info(f"[Feishu] 发送消息: {topic}")
        
        result = {
            "success": False,
            "message_id": None
        }
        
        try:
            # 构建消息内容
            message = f"""📚 **AI论文研究完成**

**研究课题**: {topic}
**检索论文**: {papers_count} 篇
**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

点击链接查看完整报告 👉 http://localhost:8088"""

            # 发送消息给用户 - receive_id_type作为查询参数
            msg_data = {
                "receive_id": self.target_user,
                "msg_type": "text",
                "content": json.dumps({"text": message})
            }
            
            # receive_id_type 需要作为查询参数
            response_data = self._request("POST", f"/im/v1/messages?receive_id_type=open_id", msg_data)
            
            result["message_id"] = response_data.get("message_id")
            result["success"] = True
            
            logger.info(f"[Feishu] 消息发送成功: {result['message_id']}")
            
        except Exception as e:
            logger.error(f"[Feishu] 消息发送失败: {e}")
            result["error"] = str(e)
        
        return result

    def _build_report_markdown(self, topic: str, review: Dict[str, Any] = None, 
                               papers: List[Dict[str, Any]] = None) -> str:
        """构建报告Markdown内容"""
        md = f"""# {topic}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**论文数量**: {len(papers) if papers else 0} 篇

---

## 研究概述

本报告基于AI论文预研助手自动生成，分析了 **{topic}** 领域的研究进展。

"""
        
        if review and isinstance(review, dict):
            content = review.get("content", "")
            if content:
                md += f"## 研究内容\n\n{content[:2000]}\n\n"
        
        if papers and len(papers) > 0:
            md += "## 论文列表\n\n"
            for i, paper in enumerate(papers[:20], 1):
                title = paper.get("title", "未知标题")[:80]
                authors = self._format_authors(paper.get("authors", []))[:50]
                published = paper.get("published", "N/A")
                arxiv_id = paper.get("arxiv_id", "")
                
                md += f"### {i}. {title}\n"
                md += f"- **作者**: {authors}\n"
                md += f"- **时间**: {published}\n"
                if arxiv_id:
                    md += f"- **arXiv**: {arxiv_id}\n"
                md += "\n"
        
        md += f"\n---\n*由 AI论文预研助手 自动生成* 🤖\n"
        
        return md

    def _format_authors(self, authors: List) -> str:
        """格式化作者列表"""
        if not authors:
            return "未知"
        
        names = []
        for author in authors[:3]:
            if isinstance(author, dict):
                names.append(author.get("name", ""))
            elif isinstance(author, str):
                names.append(author)
        
        return ", ".join(names) if names else "未知"

    def _extract_methods(self, paper: Dict[str, Any]) -> str:
        """提取研究方法"""
        text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
        
        methods = []
        method_keywords = {
            "Transformer": ["transformer", "self-attention", "attention"],
            "BERT": ["bert"],
            "GPT": ["gpt", "llm", "language model"],
            "CNN": ["cnn", "convolutional"],
            "RNN": ["rnn", "lstm", "gru"],
            "RL": ["reinforcement learning", "rl"],
            "GAN": ["gan", "adversarial"],
        }
        
        for method, keywords in method_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    methods.append(method)
                    break
        
        return ", ".join(methods[:3]) if methods else "其他"

    def get_status(self) -> Dict[str, Any]:
        """获取集成状态"""
        return {
            "app_id": self.app_id,
            "target_user": self.target_user,
            "wiki_space_id": WIKI_SPACE_ID,
            "wiki_node_token": WIKI_NODE_TOKEN,
            "connected": True
        }

    def create_document_with_content(self, title: str, content: str) -> Dict[str, Any]:
        """
        创建飞书文档（带内容）
        使用docs API
        """
        logger.info(f"[Feishu] 创建文档: {title}")
        
        result = {
            "success": False,
            "doc_id": None,
            "doc_url": None
        }
        
        try:
            # 使用docs API创建文档（支持markdown）
            doc_data = self._request("POST", "/document/v1/documents", {
                "document": {
                    "title": title,
                    "content": content
                }
            })
            
            result["doc_id"] = doc_data.get("document", {}).get("document_id")
            result["doc_url"] = f"https://my.feishu.cn/docs/{result['doc_id']}"
            result["success"] = True
            
            logger.info(f"[Feishu] 文档创建成功: {result['doc_id']}")
            
        except Exception as e:
            logger.error(f"[Feishu] 创建文档失败: {e}")
            result["error"] = str(e)
        
        return result
