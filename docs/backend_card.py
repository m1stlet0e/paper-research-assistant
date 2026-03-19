#!/usr/bin/env python3
"""
AI论文预研助手 - 后端API服务 + 飞书消息卡片推送
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import feedparser
import urllib.parse
import os
import json
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 飞书配置
FEISHU_APP_ID = "cli_a9f6f82a4ff89bd9"
FEISHU_APP_SECRET = "XSGDLKj0CAPvFYJPnDQMhexOdWcxS0ON"
FEISHU_USER_ID = "ou_0cdbe8a5a456c32beb95d46bb00b2bc1"

# 存储搜索历史
search_history = []


def get_feishu_access_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    response = requests.post(url, json=data)
    result = response.json()
    return result.get("tenant_access_token", "")


def send_feishu_card(query, papers, stats):
    """发送飞书消息卡片"""
    token = get_feishu_access_token()
    if not token:
        return False, "无法获取访问令牌"
    
    # 构建卡片内容
    paper_elements = []
    for i, p in enumerate(papers[:5], 1):
        authors = ', '.join([a['name'] for a in p.get('authors', [])[:2]])
        paper_elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{i}. {p['title'][:50]}...**\n👤 {authors} | 📅 {p.get('published', 'N/A')[:10]}"
            }
        })
        paper_elements.append({"tag": "hr"})
    
    # 添加"查看更多"提示
    if len(papers) > 5:
        paper_elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"*...还有 {len(papers)-5} 篇论文*"
            }
        })
    
    # 构建消息卡片
    card_content = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": f"📚 {query} - 研究报告"
            },
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📊 统计概览**\n📄 论文总数: {stats.get('total', len(papers))} | 👤 独特作者: {stats.get('authors', 0)} | 🏷️ 研究领域: {stats.get('categories', 0)}"
                }
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**📄 论文列表**"
                }
            },
            *paper_elements,
            {"tag": "hr"},
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "🔗 打开研究页面"
                        },
                        "type": "primary",
                        "url": "http://localhost:8080/index.html"
                    }
                ]
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "由 AI论文预研助手 自动生成"
                    }
                ]
            }
        ]
    }
    
    # 发送消息
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "receive_id_type": "open_id",
        "receive_id": FEISHU_USER_ID,
        "msg_type": "interactive",
        "content": json.dumps(card_content)
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return True, "消息卡片已发送"
    else:
        return False, f"发送失败: {response.text}"


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    max_results = data.get('max_results', 50)
    
    if not query:
        return jsonify({'error': '请提供搜索关键词'}), 400
    
    try:
        encoded_query = urllib.parse.quote(query)
        url = f'https://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending'
        
        feed = feedparser.parse(url)
        
        papers = []
        for entry in feed.entries:
            authors = []
            for author in entry.authors:
                authors.append({
                    'name': author.name,
                    'id': author.get('id', '')
                })
            
            categories = []
            for cat in entry.get('tags', []):
                categories.append(cat.get('term', ''))
            
            pdf_url = ''
            for link in entry.links:
                if link.get('type') == 'application/pdf':
                    pdf_url = link.href
                    break
            
            arxiv_id = entry.id.split('/')[-1] if entry.id else ''
            
            paper = {
                'title': entry.title.replace('\n', ' ').strip(),
                'authors': authors,
                'summary': entry.summary.replace('\n', ' ').strip(),
                'published': entry.published,
                'categories': categories,
                'pdf_url': pdf_url,
                'arxiv_id': arxiv_id,
                'source': 'arxiv'
            }
            papers.append(paper)
        
        # 统计信息
        all_authors = set()
        all_cats = set()
        year_counts = {}
        for p in papers:
            for a in p.get('authors', []):
                all_authors.add(a.get('name', ''))
            for c in p.get('categories', []):
                all_cats.add(c)
            year = p.get('published', '2024')[:4]
            year_counts[year] = year_counts.get(year, 0) + 1
        
        # 保存到历史记录
        search_history.append({
            'query': query,
            'papers': papers,
            'timestamp': datetime.now().isoformat(),
            'stats': {
                'total': len(papers),
                'authors': len(all_authors),
                'categories': len(all_cats),
                'years': year_counts
            }
        })
        
        response_data = {
            'papers': papers,
            'count': len(papers),
            'query': query,
            'stats': {
                'total': len(papers),
                'authors': len(all_authors),
                'categories': len(all_cats),
                'years': year_counts
            }
        }
        return app.response_class(
            response=json.dumps(response_data, ensure_ascii=False, indent=2),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/send_card', methods=['POST'])
def send_card():
    """发送飞书消息卡片"""
    data = request.json
    query = data.get('query', '')
    papers = data.get('papers', [])
    stats = data.get('stats', {})
    
    if not query:
        return jsonify({'error': '请提供课题'}), 400
    
    success, message = send_feishu_card(query, papers, stats)
    
    if success:
        return jsonify({
            'success': True,
            'message': '消息卡片已发送到飞书'
        })
    else:
        return jsonify({'error': message}), 500


@app.route('/api/history', methods=['GET'])
def history():
    """获取搜索历史"""
    return jsonify({'history': search_history})


if __name__ == '__main__':
    print("🚀 启动AI论文预研助手后端服务...")
    print("📡 服务地址: http://localhost:5002")
    print("💬 飞书消息卡片: 已启用")
    app.run(host='0.0.0.0', port=5002, debug=True)
