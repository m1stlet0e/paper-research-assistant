#!/bin/bash

# AI论文预研助手 - 启动脚本

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       AI论文预研助手 - OpenCrew                          ║"
echo "╚════════════════════════════════════════════════════════════╝"

# 进入项目目录
cd "$(dirname "$0")"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️ 虚拟环境不存在，请先运行: python -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# 安装依赖
echo "📦 检查依赖..."
pip install -q flask flask-cors

# 启动选项
echo ""
echo "请选择启动方式:"
echo "1) 启动Web界面"
echo "2) 启动API服务器"
echo "3) 运行CLI研究"
echo "4) 运行测试"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🌐 启动Web界面..."
        echo "访问: http://localhost:5000"
        python api_server.py
        ;;
    2)
        echo ""
        echo "🔌 启动API服务器..."
        echo "API文档: http://localhost:5000/api"
        python api_server.py
        ;;
    3)
        echo ""
        read -p "请输入研究课题: " topic
        read -p "最大论文数 (默认50): " max_papers
        max_papers=${max_papers:-50}
        
        echo ""
        echo "📚 开始研究: $topic"
        python scripts/run_crew.py --topic "$topic" --max-papers $max_papers --auto-confirm
        ;;
    4)
        echo ""
        echo "🧪 运行测试..."
        python test_crew.py
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac
