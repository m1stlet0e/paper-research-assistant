#!/bin/bash

# AI论文全自动预研助手 - 可视化界面启动脚本

echo "=========================================="
echo "AI论文全自动预研助手"
echo "可视化界面启动"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    echo "请先安装Python3"
    exit 1
fi

# 检查index.html是否存在
if [ ! -f "index.html" ]; then
    echo "❌ 错误：index.html不存在"
    echo "请确保在docs目录下运行此脚本"
    exit 1
fi

# 启动本地服务器
echo "🚀 启动本地HTTP服务器..."
echo "服务器地址：http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

# 启动服务器
python3 -m http.server 8000
