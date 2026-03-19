#!/bin/bash

# AI论文预研助手 - 一键启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示横幅
show_banner() {
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║           🤖 AI论文预研助手 v2.0.0                      ║"
    echo "║                                                           ║"
    echo "║     基于多智能体协作的学术研究辅助系统                    ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查Python环境
check_python() {
    print_info "检查Python环境..."
    
    if [ -d "venv" ]; then
        print_success "虚拟环境已存在"
    else
        print_info "创建虚拟环境..."
        python3 -m venv venv
        print_success "虚拟环境创建成功"
    fi
    
    source venv/bin/activate
    
    # 检查依赖
    if ! pip list | grep -q "flask"; then
        print_info "安装依赖..."
        pip install -r requirements.txt
        print_success "依赖安装完成"
    else
        print_success "依赖已安装"
    fi
}

# 检查输出目录
check_directories() {
    print_info "检查输出目录..."
    
    mkdir -p output/papers
    mkdir -p output/reports
    mkdir -p output/cache
    mkdir -p output/exports
    
    print_success "目录结构就绪"
}

# 启动API服务器
start_server() {
    print_info "启动API服务器..."
    
    # 检查端口是否被占用
    if lsof -Pi :8088 -sTCP:LISTEN -t >/dev/null ; then
        print_warning "端口8088已被占用"
        read -p "是否终止现有进程并重启？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:8088 | xargs kill -9
            print_info "已终止现有进程"
        else
            print_info "使用现有服务"
            return
        fi
    fi
    
    # 后台启动服务器
    nohup python api_server.py > logs/api.log 2>&1 &
    API_PID=$!
    echo $API_PID > logs/api.pid
    
    sleep 2
    
    if ps -p $API_PID > /dev/null; then
        print_success "API服务器启动成功 (PID: $API_PID)"
    else
        print_error "API服务器启动失败"
        cat logs/api.log
        exit 1
    fi
}

# 打开浏览器
open_browser() {
    print_info "打开浏览器..."
    
    sleep 1
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:8088
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:8088
    else
        print_info "请在浏览器访问: http://localhost:8088"
    fi
    
    print_success "浏览器已打开"
}

# 显示状态
show_status() {
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  🚀 系统已就绪${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  📊 Web界面: ${BLUE}http://localhost:8088${NC}"
    echo -e "  📡 API端点: ${BLUE}http://localhost:8088/api/status${NC}"
    echo ""
    echo -e "  📁 输出目录: ${YELLOW}$PROJECT_DIR/output/${NC}"
    echo -e "  📝 日志文件: ${YELLOW}$PROJECT_DIR/logs/${NC}"
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
    echo ""
    echo "使用方法:"
    echo "  1. 在Web界面输入研究课题"
    echo "  2. 点击「开始研究」按钮"
    echo "  3. 等待论文检索和分析完成"
    echo "  4. 使用智能问答功能提问"
    echo "  5. 生成研究报告"
    echo ""
    echo "停止服务: ./stop.sh"
    echo ""
}

# 创建日志目录
mkdir -p logs

# 主流程
main() {
    show_banner
    check_python
    check_directories
    start_server
    open_browser
    show_status
}

# 运行
main
