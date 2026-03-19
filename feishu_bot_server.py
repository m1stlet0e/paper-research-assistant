#!/usr/bin/env python3
"""
飞书机器人服务器
接收飞书消息并处理
"""

import sys
import os
import json
from flask import Flask, request, jsonify
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.feishu.bot_handler import FeishuBotHandler
from src.feishu.bitable_manager import BitableManager
from src.feishu.wiki_manager import WikiManager
from src.feishu.daily_push import DailyPaperPusher
from config.feishu_config import FEISHU_APP_ID, FEISHU_APP_SECRET, TARGET_USER_ID
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 初始化处理器
bot_handler = FeishuBotHandler({
    "max_papers": 50,
    "output_dir": "output",
    "data_sources": ["arxiv"]
})

bitable_manager = BitableManager()
wiki_manager = WikiManager()
daily_pusher = DailyPaperPusher()


@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        "service": "AI论文预研助手 - 飞书机器人",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook",
            "research": "/api/research",
            "push": "/api/push",
            "bitable": "/api/bitable",
            "wiki": "/api/wiki"
        }
    })


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    飞书事件回调
    接收飞书发送的消息事件
    """
    logger.info(f"[Webhook] 收到请求: {request.json}")
    
    try:
        event = request.json
        
        # 验证请求（URL验证）
        if event.get("type") == "url_verification":
            challenge = event.get("challenge", "")
            return jsonify({"challenge": challenge})
        
        # 处理消息事件
        if event.get("header", {}).get("event_type") == "im.message.receive_v1":
            result = bot_handler.handle_message(event)
            return jsonify(result)
        
        # 其他事件
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"[Webhook] 处理失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/research', methods=['POST'])
def api_research():
    """
    API接口：执行研究
    """
    logger.info("[API] 执行研究")
    
    try:
        data = request.json
        topic = data.get("topic", "")
        
        if not topic:
            return jsonify({"success": False, "error": "缺少课题参数"}), 400
        
        # 执行研究
        result = bot_handler._handle_research(topic)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"[API] 研究失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/push', methods=['POST'])
def api_push():
    """
    API接口：触发推送
    """
    logger.info("[API] 触发推送")
    
    try:
        data = request.json or {}
        keywords = data.get("keywords", None)
        
        result = daily_pusher.manual_push(keywords)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"[API] 推送失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/bitable', methods=['POST'])
def api_bitable():
    """
    API接口：多维表格操作
    """
    logger.info("[API] 多维表格操作")
    
    try:
        data = request.json
        action = data.get("action", "")
        
        if action == "create":
            result = bitable_manager.create_papers_table(data.get("name"))
        elif action == "add":
            result = bitable_manager.add_paper(data.get("paper"), data.get("topic"))
        elif action == "batch_add":
            result = bitable_manager.batch_add_papers(data.get("papers"), data.get("topic"))
        else:
            return jsonify({"success": False, "error": "未知操作"}), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"[API] 操作失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/wiki', methods=['POST'])
def api_wiki():
    """
    API接口：知识库操作
    """
    logger.info("[API] 知识库操作")
    
    try:
        data = request.json
        action = data.get("action", "")
        
        if action == "create":
            result = wiki_manager.create_wiki_space(data.get("name"))
        elif action == "archive":
            result = wiki_manager.archive_research(
                data.get("topic"),
                data.get("report"),
                data.get("papers"),
                data.get("visualizations")
            )
        elif action == "list":
            result = wiki_manager.list_researches()
        elif action == "search":
            result = wiki_manager.search_research(data.get("keyword"))
        else:
            return jsonify({"success": False, "error": "未知操作"}), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"[API] 操作失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """服务状态"""
    return jsonify({
        "status": "running",
        "service": "AI论文预研助手 - 飞书机器人",
        "version": "1.0.0",
        "pusher_status": daily_pusher.get_status(),
        "timestamp": datetime.now().isoformat()
    })


def start_server(port: int = 6000):
    """启动服务器"""
    print(f"""
╔════════════════════════════════════════════════════════════╗
║       AI论文预研助手 - 飞书机器人服务器                  ║
╠════════════════════════════════════════════════════════════╣
║  访问: http://localhost:{port}                            ║
║  Webhook: http://localhost:{port}/webhook                 ║
║  API文档: http://localhost:{port}/                        ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # 启动每日推送服务
    daily_pusher.start()
    
    # 启动Flask服务器
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='飞书机器人服务器')
    parser.add_argument('--port', type=int, default=6000, help='服务端口')
    
    args = parser.parse_args()
    
    start_server(args.port)
