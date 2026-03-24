#!/bin/bash

# claw-rl Activation Script
# 用途：在 OpenClaw 会话中激活 claw-rl 功能

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/Users/liantian/.openclaw/workspace"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[claw-rl]${NC} $1"; }

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  🧠 claw-rl 已激活${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# 1. 注入 Friday 宪法
log_info "注入 Friday 宪法..."
if [ -f "$WORKSPACE_DIR/claw-rl/FRIDAY_CONSTITUTION.md" ]; then
    echo ""
    echo "📜 Friday 宪法 - 核心原则:"
    grep -E "^### [0-9]" "$WORKSPACE_DIR/claw-rl/FRIDAY_CONSTITUTION.md" | sed 's/^/   /'
    echo ""
fi

# 2. 检查工作目录配置
log_info "检查工作目录配置..."
if [ -f "$WORKSPACE_DIR/TOOLS.md" ]; then
    echo ""
    echo "📁 工作目录分工:"
    grep -A5 "日常工作主目录\|OpenClaw 系统配置" "$WORKSPACE_DIR/TOOLS.md" | head -10 | sed 's/^/   /'
    echo ""
fi

# 3. 检查今日学习提示
log_info "检查学习提示..."
if [ -f "$WORKSPACE_DIR/claw-rl/.hints/$(date +%Y-%m-%d).jsonl" ]; then
    "$SCRIPT_DIR/hint_extractor.sh" inject 2>/dev/null | sed 's/^/   /'
else
    echo "   今日暂无学习提示"
fi
echo ""

# 4. 检查奖励统计
log_info "今日奖励统计..."
"$SCRIPT_DIR/reward_collector.sh" summary 2>/dev/null | grep -E "(总记录 | 正面 | 负面)" | sed 's/^/   /'
echo ""

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  ✅ claw-rl 准备就绪${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# 5. 启动后台训练循环（如果未运行）
if ! pgrep -f "training_loop.sh daemon" > /dev/null 2>&1; then
    log_info "启动后台训练循环..."
    nohup "$SCRIPT_DIR/training_loop.sh" daemon 300 > /tmp/clawrl_training.log 2>&1 &
    echo "   训练循环 PID: $!"
fi

echo ""
log_info "使用提示:"
echo "   - 文件操作前自动检查目录分工"
echo "   - 用户反馈自动评估 (PRM Judge)"
echo "   - 用户纠正自动提取改进方向 (OPD)"
echo "   - 后台定期处理学习信号"
echo ""
