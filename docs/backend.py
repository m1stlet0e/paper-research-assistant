#!/usr/bin/env python3
"""
AI论文预研助手 - 后端API服务 v3 (修复版)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import feedparser
import urllib.parse
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

FEISHU_APP_ID = "cli_a9f6f82a4ff89bd9"
FEISHU_APP_SECRET = "XSGDLKj0CAPvFYJPnDQMhexOdWcxS0ON"
FEISHU_USER_ID = "ou_0cdbe8a5a456c32beb95d46bb00b2bc1"

search_history = []

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    return resp.json().get("tenant_access_token", "")

def send_msg(query, papers, stats):
    token = get_token()
    if not token:
        return False, "无法获取token"
    
    # 构建消息
    lines = [f"📚 **{query}** - 研究报告", "", "─" * 20, "", "📊 **统计概览**"]
    lines.append(f"  • 📄 论文总数: **{stats.get('total', len(papers))}**")
    lines.append(f"  • 👤 独特作者: **{stats.get('authors', 0)}**")
    lines.append(f"  • 🏷️ 研究领域: **{stats.get('categories', 0)}**")
    
    if stats.get('years'):
        lines.extend(["", "📅 **年份分布**"])
        for y, c in sorted(stats.get('years', {}).items(), reverse=True)[:5]:
            lines.append(f"  • {y}: {c}篇")
    
    lines.extend(["", "─" * 20, "", "📄 **论文列表**"])
    
    for i, p in enumerate(papers[:10], 1):
        lines.extend(["", f"**{i}. {p.get('title', 'N/A')[:60]}**"])
        lines.append(f"   👤 作者: {', '.join([a['name'] for a in p.get('authors', [])[:3]])}")
        lines.append(f"   🔖 arXiv: {p.get('arxiv_id', 'N/A')}")
        lines.append(f"   📅 日期: {p.get('published', 'N/A')[:10]}")
        if p.get('pdf_url'):
            lines.append(f"   📥 PDF: {p.get('pdf_url')}")
    
    lines.extend(["", "─" * 20, "", f"🔗 打开页面: http://localhost:8080/index.html", "", "*由 AI论文预研助手 自动生成*"])
    
    msg = "\n".join(lines)
    
    # 发送 - 使用user_id类型
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "receive_id_type": "user_id",  # 关键修复
        "receive_id": FEISHU_USER_ID,
        "msg_type": "text",
        "content": json.dumps({"text": msg})
    }
    
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()
    
    if resp.status_code == 200 and result.get('code') == 0:
        return True, "发送成功"
    else:
        return False, f"错误: {result}"

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    max_results = data.get('max_results', 50)
    
    if not query:
        return jsonify({"error": "请提供关键词"}), 400
    
    try:
        url = f'https://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&start=0&max_results={max_results}&sortBy=relevance'
        feed = feedparser.parse(url)
        
        papers = []
        for entry in feed.entries:
            authors = [{"name": a.name} for a in entry.authors]
            cats = [t.get('term', '') for t in entry.get('tags', [])]
            pdf = ""
            for link in entry.links:
                if link.get('type') == 'application/pdf':
                    pdf = link.href
                    break
            papers.append({
                "title": entry.title.replace("\n", " ").strip(),
                "authors": authors,
                "published": entry.published,
                "categories": cats,
                "pdf_url": pdf,
                "arxiv_id": entry.id.split('/')[-1] if entry.id else ""
            })
        
        all_authors = set()
        all_cats = set()
        years = {}
        for p in papers:
            for a in p.get('authors', []):
                all_authors.add(a.get('name', ''))
            for c in p.get('categories', []):
                all_cats.add(c)
            y = p.get('published', '2024')[:4]
            years[y] = years.get(y, 0) + 1
        
        resp_data = {
            "papers": papers,
            "count": len(papers),
            "query": query,
            "stats": {"total": len(papers), "authors": len(all_authors), "categories": len(all_cats), "years": years}
        }
        return app.response_class(response=json.dumps(resp_data, ensure_ascii=False), status=200, mimetype='application/json')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send_card', methods=['POST'])
def send_card():
    data = request.json
    query = data.get('query', '')
    papers = data.get('papers', [])
    stats = data.get('stats', {})
    
    if not query:
        return jsonify({"error": "请提供课题"}), 400
    
    success, msg = send_msg(query, papers, stats)
    
    if success:
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"error": msg}), 500

if __name__ == "__main__":
    print("🚀 AI论文预研助手后端 v3")
    print("📡 http://localhost:5002")
    app.run(host="0.0.0.0", port=5002)
