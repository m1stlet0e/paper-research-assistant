#!/usr/bin/env python3
"""
API服务器 - AI论文预研助手
提供REST API接口供Web界面调用
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run import PaperResearchAssistant
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 创建Flask应用
app = Flask(__name__, static_folder='web/static', static_url_path='/static')
CORS(app)

# 全局助手实例
assistant = None


def get_assistant() -> PaperResearchAssistant:
    """获取或创建助手实例"""
    global assistant
    if assistant is None:
        assistant = PaperResearchAssistant({"output_dir": "output"})
    return assistant


# ==================== 静态文件路由 ====================

@app.route('/')
def index():
    """主页"""
    return send_file('web/index.html')


@app.route('/output/<path:filename>')
def serve_output(filename):
    """提供输出文件"""
    return send_from_directory('output', filename)


# ==================== API路由 ====================

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统状态"""
    try:
        ast = get_assistant()
        status = ast.get_status()
        status["server_time"] = datetime.now().isoformat()
        status["connected"] = True
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/research', methods=['POST'])
def run_research():
    """运行研究"""
    try:
        data = request.get_json()
        topic = data.get('topic', 'AI Agent')
        max_papers = data.get('max_papers', 50)
        enable_feishu = data.get('enable_feishu', True)
        
        logger.info(f"开始研究: {topic}")
        
        ast = get_assistant()
        result = ast.run_research(
            topic=topic,
            max_papers=max_papers,
            enable_feishu=enable_feishu
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"研究失败: {e}")
        return jsonify({"error": str(e), "status": "failed"}), 500


@app.route('/api/qa', methods=['POST'])
def ask_question():
    """智能问答"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        use_enhanced = data.get('enhanced', True)  # 默认使用增强版
        
        if not question:
            return jsonify({"error": "请输入问题"}), 400
        
        ast = get_assistant()
        
        # 优先使用增强问答系统
        if use_enhanced and ast.enhanced_qa:
            result = ast.enhanced_qa.answer(question)
            result["enhanced"] = True
            return jsonify(result)
        
        if not ast.qa_system:
            return jsonify({"error": "请先运行研究以初始化问答系统"}), 400
        
        result = ast.ask_question(question)
        result["enhanced"] = False
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"问答失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/qa/history', methods=['GET'])
def get_qa_history():
    """获取问答历史"""
    try:
        ast = get_assistant()
        
        if not ast.enhanced_qa:
            return jsonify({"history": []})
        
        history = ast.enhanced_qa.get_conversation_history()
        return jsonify({"history": history})
        
    except Exception as e:
        logger.error(f"获取历史失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/qa/clear', methods=['POST'])
def clear_qa_history():
    """清空问答历史"""
    try:
        ast = get_assistant()
        
        if ast.enhanced_qa:
            ast.enhanced_qa.clear_history()
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"清空历史失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/papers', methods=['GET'])
def get_papers():
    """获取论文列表"""
    try:
        ast = get_assistant()
        
        if not ast.current_papers:
            # 尝试从文件加载
            papers_path = "output/papers.json"
            if os.path.exists(papers_path):
                with open(papers_path, 'r', encoding='utf-8') as f:
                    papers = json.load(f)
                    return jsonify({"papers": papers, "count": len(papers)})
            else:
                return jsonify({"papers": [], "count": 0})
        
        return jsonify({
            "papers": ast.current_papers,
            "count": len(ast.current_papers)
        })
        
    except Exception as e:
        logger.error(f"获取论文失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/visualizations', methods=['GET'])
def get_visualizations():
    """获取可视化列表"""
    try:
        output_dir = "output"
        visualizations = []
        
        viz_files = {
            "knowledge_graph": "knowledge_graph_enhanced.html",
            "comparison_matrix": "comparison_matrix_enhanced.html",
            "qa_demo": "qa_demo.html"
        }
        
        for name, filename in viz_files.items():
            filepath = os.path.join(output_dir, filename)
            if os.path.exists(filepath):
                visualizations.append({
                    "name": name,
                    "filename": filename,
                    "url": f"/output/{filename}",
                    "size": os.path.getsize(filepath)
                })
        
        return jsonify({
            "visualizations": visualizations,
            "count": len(visualizations)
        })
        
    except Exception as e:
        logger.error(f"获取可视化失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/review', methods=['GET'])
def get_review():
    """获取综述"""
    try:
        ast = get_assistant()
        
        if ast.current_review:
            return jsonify(ast.current_review)
        
        # 尝试从文件加载
        review_path = "output/review.md"
        if os.path.exists(review_path):
            with open(review_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return jsonify({
                    "title": "研究综述",
                    "content": content,
                    "format": "markdown"
                })
        
        return jsonify({"error": "暂无综述内容"}), 404
        
    except Exception as e:
        logger.error(f"获取综述失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/feishu/status', methods=['GET'])
def feishu_status():
    """获取飞书集成状态"""
    try:
        ast = get_assistant()
        return jsonify(ast.feishu.get_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/feishu/push', methods=['POST'])
def feishu_push():
    """发送飞书推送"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        papers_count = data.get('papers_count', 0)
        
        ast = get_assistant()
        result = ast.feishu.send_research_card(topic, papers_count)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"飞书推送失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/feishu/bitable', methods=['POST'])
def create_bitable():
    """创建飞书多维表格"""
    try:
        data = request.get_json()
        name = data.get('name', 'AI论文研究')
        papers = data.get('papers', [])

        ast = get_assistant()
        result = ast.feishu.create_and_populate_bitable(name=name, papers=papers)

        if result.get("success") and result.get("url"):
            try:
                msg = f"多维表格创建成功!\n\n课题: {name}\n论文数: {result.get('records_count', 0)}\n\n链接: {result['url']}"
                ast.feishu._request("POST", "/im/v1/messages?receive_id_type=open_id", {
                    "receive_id": ast.feishu.target_user,
                    "msg_type": "text",
                    "content": json.dumps({"text": msg})
                })
            except Exception:
                pass

        return jsonify(result)

    except Exception as e:
        logger.error(f"创建多维表格失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/feishu/wiki', methods=['POST'])
def archive_wiki():
    """归档到飞书知识库"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        review = data.get('review', {})
        papers = data.get('papers', [])

        ast = get_assistant()
        result = ast.feishu.archive_research_to_wiki(
            topic=topic, review=review, papers=papers
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"归档知识库失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ==================== 报告生成API ====================

@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """生成综述报告"""
    try:
        data = request.get_json()
        topic = data.get('topic', 'AI研究')
        papers = data.get('papers', [])
        format = data.get('format', 'markdown')  # markdown 或 latex
        
        ast = get_assistant()
        
        # 如果没有提供论文，使用当前论文
        if not papers and ast.current_papers:
            papers = ast.current_papers
        
        result = ast.report_generator.generate(
            topic=topic,
            papers=papers,
            format=format,
            include_analysis=True
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"报告生成失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/report/list', methods=['GET'])
def list_reports():
    """列出所有报告"""
    try:
        reports_dir = "output/reports"
        if not os.path.exists(reports_dir):
            return jsonify({"reports": []})
        
        reports = []
        for f in os.listdir(reports_dir):
            if f.endswith('.md') or f.endswith('.tex'):
                filepath = os.path.join(reports_dir, f)
                reports.append({
                    "filename": f,
                    "path": filepath,
                    "size": os.path.getsize(filepath),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        
        # 按修改时间排序
        reports.sort(key=lambda x: x["modified"], reverse=True)
        
        return jsonify({"reports": reports, "count": len(reports)})
        
    except Exception as e:
        logger.error(f"列出报告失败: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== 数据持久化API ====================

@app.route('/api/data/save', methods=['POST'])
def save_data():
    """保存论文数据"""
    try:
        data = request.get_json()
        topic = data.get('topic', '未知课题')
        papers = data.get('papers', [])
        metadata = data.get('metadata', {})
        
        ast = get_assistant()
        filepath = ast.persistence.save_papers(papers, topic, metadata)
        
        return jsonify({
            "success": True,
            "filepath": filepath,
            "papers_count": len(papers)
        })
        
    except Exception as e:
        logger.error(f"保存数据失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/data/load', methods=['GET'])
def load_data():
    """加载论文数据"""
    try:
        topic = request.args.get('topic')
        latest = request.args.get('latest', 'true').lower() == 'true'
        
        ast = get_assistant()
        data = ast.persistence.load_papers(topic=topic, latest=latest)
        
        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "未找到数据"}), 404
        
    except Exception as e:
        logger.error(f"加载数据失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/data/list', methods=['GET'])
def list_saved_data():
    """列出保存的数据"""
    try:
        ast = get_assistant()
        files = ast.persistence.list_saved_papers()
        
        return jsonify({"files": files, "count": len(files)})
        
    except Exception as e:
        logger.error(f"列出数据失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/data/export', methods=['POST'])
def export_data():
    """导出数据"""
    try:
        data = request.get_json()
        papers = data.get('papers', [])
        format = data.get('format', 'json')  # json, csv, bibtex
        
        ast = get_assistant()
        
        if format == 'csv':
            filepath = ast.persistence.export_to_csv(papers)
        elif format == 'bibtex':
            filepath = ast.persistence.export_to_bibtex(papers)
        else:
            filepath = ast.persistence.export_to_json(papers)
        
        return jsonify({
            "success": True,
            "filepath": filepath,
            "format": format
        })
        
    except Exception as e:
        logger.error(f"导出数据失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/data/import', methods=['POST'])
def import_data():
    """导入数据"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "未找到文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "未选择文件"}), 400
        
        # 保存临时文件
        temp_path = os.path.join('output', 'temp_import.json')
        file.save(temp_path)
        
        ast = get_assistant()
        papers = ast.persistence.import_from_json(temp_path)
        
        # 删除临时文件
        os.remove(temp_path)
        
        return jsonify({
            "success": True,
            "papers_count": len(papers)
        })
        
    except Exception as e:
        logger.error(f"导入数据失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清除缓存"""
    try:
        ast = get_assistant()
        ast.persistence.clear_cache()
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ==================== 主函数 ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI论文预研助手 - API服务器")
    print("="*60)
    print("\n启动参数:")
    print("  - Host: 0.0.0.0")
    print("  - Port: 8088")
    print("  - Debug: False")
    print("\n访问地址:")
    print("  - API: http://localhost:8088/api/status")
    print("  - Web: http://localhost:8088")
    print("\n" + "="*60 + "\n")
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    # 启动服务器
    app.run(host='0.0.0.0', port=8088, debug=False)
