#!/usr/bin/env python3
"""
AI论文预研助手 - 后端API服务（简化版，无飞书功能）
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import feedparser
import urllib.parse
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 存储搜索历史
search_history = []


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


@app.route('/api/history', methods=['GET'])
def history():
    """获取搜索历史"""
    return jsonify({'history': search_history})


if __name__ == '__main__':
    print("🚀 启动AI论文预研助手后端服务...")
    print("📡 服务地址: http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
