#!/usr/bin/env python3
"""
AI论文预研助手 - 后端API服务 + 飞书集成
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import feedparser
import urllib.parse
import time
import os
import json
import subprocess
import re
import tempfile
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
    import requests
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    response = requests.post(url, json=data)
    result = response.json()
    return result.get("tenant_access_token", "")


def send_feishu_message(content):
    """发送飞书消息"""
    import requests
    token = get_feishu_access_token()
    if not token:
        return False
    
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "receive_id_type": "open_id",
        "receive_id": FEISHU_USER_ID,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200


def create_feishu_doc(title, content):
    """创建飞书文档 - 使用openclaw命令行工具"""
    try:
        # 使用subprocess调用openclaw命令行工具
        # 创建文档
        result = subprocess.run(
            ['openclaw', 'feishu_doc', 'create', '--title', title],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        print(f"创建文档输出: {output[:500]}")
        
        # 提取document_id
        match = re.search(r'docx/([a-zA-Z0-9]+)', output)
        if match:
            doc_id = match.group(1)
            print(f"提取到文档ID: {doc_id}")
            
            # 写入内容（保存到临时文件）
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write(content)
                temp_file = f.name
            
            # 写入内容
            write_result = subprocess.run(
                ['openclaw', 'feishu_doc', 'write', '--doc-token', doc_id, '--file', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            print(f"写入结果: {write_result.stdout[:200]}")
            
            # 清理临时文件
            os.unlink(temp_file)
            
            return doc_id
        else:
            print("无法提取document_id")
    except Exception as e:
        print(f"创建飞书文档失败: {e}")
        import traceback
        traceback.print_exc()
    
    return None


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
        
        import json
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


@app.route('/api/save_to_feishu', methods=['POST'])
def save_to_feishu():
    """保存报告到飞书"""
    data = request.json
    query = data.get('query', '')
    papers = data.get('papers', [])
    stats = data.get('stats', {})
    
    if not query:
        return jsonify({'error': '请提供课题'}), 400
    
    try:
        # 生成报告内容
        report_content = f"""# 📚 {query} - 研究报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 统计概览

| 指标 | 数值 |
|------|------|
| 论文总数 | {stats.get('total', len(papers))} |
| 独特作者 | {stats.get('authors', 0)} |
| 研究领域 | {stats.get('categories', 0)} |

### 年份分布
"""
        
        for year, count in sorted(stats.get('years', {}).items(), reverse=True):
            report_content += f"- {year}: {count}篇\n"
        
        report_content += """
---

## 📄 论文列表

"""
        
        for i, p in enumerate(papers[:20], 1):
            authors = ', '.join([a['name'] for a in p.get('authors', [])[:3]])
            report_content += f"""
### {i}. {p['title']}

- **作者**: {authors}
- **arXiv**: {p.get('arxiv_id', 'N/A')}
- **发表日期**: {p.get('published', 'N/A')[:10]}
- **分类**: {', '.join(p.get('categories', [])[:3])}
- **PDF**: {p.get('pdf_url', 'N/A')}

"""
        
        report_content += """
---

*由 AI论文预研助手 自动生成*
"""
        
        # 保存到本地文件
        filename = f"output/report_{query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        os.makedirs("output", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 创建飞书文档并写入内容
        doc_token = create_feishu_doc(f"研究报告: {query}", report_content)
        
        if doc_token:
            print(f"文档已创建并写入: https://feishu.cn/docx/{doc_token}")
        
        return jsonify({
            'success': True,
            'local_file': filename,
            'doc_url': f'https://feishu.cn/docx/{doc_token}' if doc_token else None,
            'message': f'报告已保存到: {filename}'
        })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_topics', methods=['GET'])
def get_topics():
    """从飞书获取课题列表"""
    default_topics = [
        "machine learning",
        "deep learning", 
        "neural network",
        "speech recognition",
        "computer vision",
        "natural language processing",
        "transformer",
        "reinforcement learning"
    ]
    
    return jsonify({
        'topics': default_topics,
        'source': 'feishu'
    })


@app.route('/api/notify', methods=['POST'])
def notify():
    """发送通知到飞书"""
    data = request.json
    message = data.get('message', '')
    
    if send_feishu_message(message):
        return jsonify({'success': True})
    else:
        return jsonify({'error': '发送失败'}), 500


@app.route('/api/history', methods=['GET'])
def history():
    """获取搜索历史"""
    return jsonify({'history': search_history})


if __name__ == '__main__':
    print("🚀 启动AI论文预研助手后端服务...")
    print("📡 服务地址: http://localhost:5002")
    print("🔗 飞书集成: 已启用")
    app.run(host='0.0.0.0', port=5002, debug=True)
