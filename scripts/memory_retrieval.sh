#!/bin/bash

# claw-rl Memory Retrieval Script
# 用途：根据当前场景自动检索并注入相关记忆

WORKSPACE_DIR="/Users/liantian/.openclaw/workspace"
TOOLS_MD="$WORKSPACE_DIR/TOOLS.md"
CONSTITUTION_MD="$WORKSPACE_DIR/claw-rl/FRIDAY_CONSTITUTION.md"
LEARNINGS_MD="$WORKSPACE_DIR/.learnings/LEARNINGS.md"
MEMORY_DIR="$WORKSPACE_DIR/memory"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

log_section() {
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
}

# 注入宪法核心原则
inject_constitution() {
    log_section "📜 Friday 宪法 - 核心原则"
    if [ -f "$CONSTITUTION_MD" ]; then
        grep -E "^### [0-9]" "$CONSTITUTION_MD" | sed 's/^/  /'
        echo ""
        echo "  📌 详细原则：$CONSTITUTION_MD"
    else
        log_warn "宪法文件不存在"
    fi
    echo ""
}

# 检索 TOOLS.md 工作目录配置
retrieve_workspace() {
    log_section "📁 工作目录配置 (TOOLS.md)"
    if [ -f "$TOOLS_MD" ]; then
        grep -A15 "日常工作主目录\|OpenClaw 系统配置" "$TOOLS_MD" | head -20
    else
        log_warn "TOOLS.md 不存在"
    fi
    echo ""
}

# 检索学习条目
retrieve_learnings() {
    local keywords="$1"
    log_section "📚 相关学习条目"
    if [ -f "$LEARNINGS_MD" ]; then
        for kw in $keywords; do
            grep -i -B1 -A10 "$kw" "$LEARNINGS_MD" 2>/dev/null || true
        done
    else
        log_warn "LEARNINGS.md 不存在"
    fi
    echo ""
}

# 主函数
main() {
    local scenario="${1:-general}"
    
    # 总是注入宪法
    inject_constitution
    
    # 根据场景检索
    case "$scenario" in
        file*|create*|write*)
            log_info "检测到文件操作场景..."
            retrieve_workspace
            retrieve_learnings "目录 workspace 文件"
            ;;
        skill*|tool*)
            log_info "检测到技能使用场景..."
            retrieve_learnings "技能 skill"
            ;;
        permission*|exec*)
            log_info "检测到权限场景..."
            retrieve_learnings "请示 授权 边界"
            ;;
        full)
            retrieve_workspace
            retrieve_learnings "目录 技能 请示"
            ;;
        *)
            log_info "通用场景"
            ;;
    esac
}

main "$@"
