#!/usr/bin/env python3
"""
AI论文预研助手 - 后端API服务 v2
飞书消息推送 - 完整版
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

search_history = []


def get_feishu_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    return resp.json().get("tenant_access_token", "")


def send_feishu_message_v2(query, papers, stats):
    """发送飞书富文本消息 - 改进版"""
    token = get_feishu_token()
    if not token:
        return False, "无法获取token"
    
    # 构建美观的富文本消息
    msg_lines = []
    msg_lines.append(f"📚 **{query}** - 研究报告")
    msg_lines.append("")
    msg_lines.append("─" * 20)
    msg_lines.append("")
    msg_lines.append("📊 **统计概览**")
    msg_lines.append(f"  • 📄 论文总数: **{stats.get('total', len(papers))}**")
    msg_lines.append(f"  • 👤 独特作者: **{stats.get('authors', 0)}**")
    msg_lines.append(f"  • 🏷️ 研究领域: **{stats.get('categories', 0)}**")
    
    # 年份分布
    if stats.get('years'):
        msg_lines.append("")
        msg_lines.append("📅 **年份分布**")
        for year, count in sorted(stats.get('years', {}).items(), reverse=True)[:5]:
            msg_lines.append(f"  • {year}: {count}篇")
    
    msg_lines.append("")
    msg_lines.append("─" * 20)
    msg_lines.append("")
    msg_lines.append("📄 **论文列表**")
    
    # 论文列表 - 详细展示
    for i, p in enumerate(papers[:10], 1):
        title = p.get('title', 'N/A')[:60]
        authors = ', '.join([a['name'] for a in p.get('authors', [])[:3]])
        arxiv_id = p.get('arxiv_id', 'N/A')
        date = p.get('published', 'N/A')[:10]
        
        msg_lines.append("")
        msg_lines.append(f"**{i}. {title}**")
        msg_lines.append(f"   👤 作者: {authors}")
        msg_lines.append(f"   🔖 arXiv: {arxiv_id}")
        msg_lines.append(f"   📅 日期: {date}")
        if p.get('pdf_url'):
            msg_lines.append(f"   📥 PDF: {p.get('pdf_url')}")
    
    if len(papers) > 10:
        msg_lines.append("")
        msg_lines.append(f"... 还有 {len(papers)-10} 篇论文")
    
    msg_lines.append("")
    msg_lines.append("─" * 20)
    msg_lines.append("")
    msg_lines.append("🔗 打开研究页面: http://localhost:8080/index.html")
    msg_lines.append("")
    msg_lines.append("*由 AI论文预研助手 自动生成*")
    
    message_text = '\n'.join(msg_lines)
    
    # 发送消息
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "receive_id": FEISHU_USER_ID,
        "msg_type": "text",
        "content": json.dumps({"text": message_text})
    }
    
    resp = requests.post(url, headers=headers, json=data)
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get('code') == 0:
            return True, "消息发送成功"
        else:
            return False, f"发送失败: {result.get('msg')}"
    else:
        return False, f"HTTP错误: {resp.status_code}"


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
                authors.append({'name': author.name, 'id': author.get('id', '')})
            
            categories = []
            for cat in entry.get('tags', []):
                categories.append(cat.get('term', ''))
            
            pdf_url = ''
            for link in entry.links:
                if link.get('type') == 'application/pdf':
                    pdf_url = link.href
                    break
            
            arxiv_id = entry.id.split('/')[-1] if entry.id else ''
            
            papers.append({
                'title': entry.title.replace('\n', ' ').strip(),
                'authors': authors,
                'summary': entry.summary.replace('\n', ' ').strip(),
                'published': entry.published,
                'categories': categories,
                'pdf_url': pdf_url,
                'arxiv_id': arxiv_id,
                'source': 'arxiv'
            })
        
        # 统计
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
        
        search_history.append({
            'query': query,
            'papers': papers,
            'timestamp': datetime.now().isoformat(),
            'stats': {'total': len(papers), 'authors': len(all_authors), 'categories': len(all_cats), 'years': year_counts}
        })
        
        response_data = {
            'papers': papers,
            'count': len(papers),
            'query': query,
            'stats': {'total': len(papers), 'authors': len(all_authors), 'categories': len(all_cats), 'years': year_counts}
        }
        return app.response_class(response=json.dumps(response_data, ensure_ascii=False, indent=2), status=200, mimetype='application/json')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/send_card', methods=['POST'])
def send_card():
    """发送飞书消息"""
    data = request.json
    query = data.get('query', '')
    papers = data.get('papers', [])
    stats = data.get('stats', {})
    
    if not query:
        return jsonify({'error': '请提供课题'}), 400
    
    success, message = send_feishu_message_v2(query, papers, stats)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'error': message}), 500


@app.route('/api/history', methods=['GET'])
def history():
    return jsonify({'history': search_history})


if __name__ == '__main__':
    print("🚀 AI论文预研助手后端服务 v2")
    print("📡 服务地址: http://localhost:5002")
    print("💬 飞书消息推送: 已启用 (改进版)")
    app.run(host='0.0.0.0', port=5002, debug=True)
