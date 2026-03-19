#!/bin/bash

# AI论文预研助手 - 停止脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}[INFO]${NC} 停止AI论文预研助手..."

# 检查PID文件
if [ -f "logs/api.pid" ]; then
    PID=$(cat logs/api.pid)
    
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo -e "${GREEN}[SUCCESS]${NC} API服务器已停止 (PID: $PID)"
    else
        echo -e "${RED}[INFO]${NC} 服务进程不存在"
    fi
    
    rm logs/api.pid
fi

# 检查端口占用
if lsof -Pi :8088 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${BLUE}[INFO]${NC} 发现端口8088占用，正在清理..."
    lsof -ti:8088 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}[SUCCESS]${NC} 端口已释放"
fi

echo -e "${GREEN}[SUCCESS]${NC} 所有服务已停止"
