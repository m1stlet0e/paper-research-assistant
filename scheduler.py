#!/usr/bin/env python3
"""
定时推送服务 - 每天自动推送研究热点到飞书
"""

import schedule
import time
import requests
import json
from datetime import datetime

# 配置
FEISHU_APP_ID = "cli_a9f6f82a4ff89bd9"
FEISHU_APP_SECRET = "XSGDLKj0CAPvFYJPnDQMhexOdWcxS0ON"
FEISHU_USER_ID = "ou_0cdbe8a5a456c32beb95d46bb00b2bc1"

# 热门研究课题
HOT_TOPICS = [
    "machine learning",
    "deep learning",
    "neural network",
    "natural language processing",
    "computer vision",
    "speech recognition",
    "transformer",
    "reinforcement learning"
]

def get_feishu_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    response = requests.post(url, json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    return response.json().get("tenant_access_token", "")

def send_daily_report():
    """发送每日研究热点报告"""
    print(f"[{datetime.now()}] 开始生成每日研究热点报告...")
    
    # 随机选择一个热门课题
    import random
    topic = random.choice(HOT_TOPICS)
    
    # 搜索论文
    try:
        import feedparser
        import urllib.parse
        
        encoded_query = urllib.parse.quote(topic)
        url = f'https://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending'
        
        feed = feedparser.parse(url)
        papers = []
        
        for entry in feed.entries[:5]:
            papers.append({
                'title': entry.title.replace('\n', ' ').strip(),
                'authors': ', '.join([a.name for a in entry.authors[:2]]),
                'arxiv_id': entry.id.split('/')[-1] if entry.id else '',
                'published': entry.published[:10],
                'pdf_url': next((link.href for link in entry.links if link.get('type') == 'application/pdf'), '')
            })
        
        # 构建消息
        lines = [
            f"🔥 **每日研究热点 - {datetime.now().strftime('%Y-%m-%d')}**",
            "",
            f"📚 **今日课题**: {topic}",
            "",
            "─" * 30,
            "",
            "📄 **最新论文**",
        ]
        
        for i, p in enumerate(papers, 1):
            lines.extend([
                "",
                f"**{i}. {p['title'][:50]}...**",
                f"   👤 {p['authors']}",
                f"   📅 {p['published']}",
                f"   🔗 https://arxiv.org/abs/{p['arxiv_id']}"
            ])
        
        lines.extend([
            "",
            "─" * 30,
            "",
            "💡 **提示**: 回复课题名称，获取详细报告",
            "",
            "*由 AI论文预研助手 自动生成*"
        ])
        
        message = '\n'.join(lines)
        
        # 发送消息
        token = get_feishu_token()
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "receive_id_type": "user_id",
            "receive_id": FEISHU_USER_ID,
            "msg_type": "text",
            "content": json.dumps({"text": message})
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('code') == 0:
            print(f"[{datetime.now()}] 每日报告发送成功！")
            return True
        else:
            print(f"[{datetime.now()}] 发送失败: {result}")
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] 错误: {e}")
        return False

def main():
    """主函数 - 设置定时任务"""
    print("🚀 启动定时推送服务...")
    print("⏰ 每天 08:00 自动推送研究热点")
    print("💡 按 Ctrl+C 停止")
    print()
    
    # 设置定时任务 - 每天早上8点
    schedule.every().day.at("08:00").do(send_daily_report)
    
    # 立即发送一次测试
    print("📨 发送测试消息...")
    send_daily_report()
    
    # 运行调度器
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    main()
