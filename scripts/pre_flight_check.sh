#!/bin/bash

# claw-rl Pre-Flight Checklist Script
# 用途：特定操作前强制执行预检查
#
# v0.7.0: 增强检查规则 + 性能优化

set -e

WORKSPACE_DIR="/Users/liantian/.openclaw/workspace"
TOOLS_MD="$WORKSPACE_DIR/TOOLS.md"
CONSTITUTION_MD="$WORKSPACE_DIR/claw-rl/FRIDAY_CONSTITUTION.md"
LEARNINGS_MD="$WORKSPACE_DIR/.learnings/LEARNINGS.md"
SKILLS_DIR="$WORKSPACE_DIR/skills"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 1: 文件操作 - 验证目录分工
check_file_operation() {
    local target_path="$1"
    
    log_info "检查文件操作：$target_path"
    
    # 检查是否包含 workspace 路径
    if [[ "$target_path" == *"/Users/liantian/workspace/"* ]]; then
        log_info "✓ 目标目录：日常工作目录 (/Users/liantian/workspace/)"
        log_info "  用途：日常项目、文档、MBA 论文等"
    elif [[ "$target_path" == *"/.openclaw/workspace/"* ]] || [[ "$target_path" == *"~/.openclaw/workspace/"* ]]; then
        log_info "✓ 目标目录：OpenClaw 系统配置目录 (~/.openclaw/workspace/)"
        log_info "  用途：AI 配置、记忆文件、技能模块"
    else
        log_warn "⚠ 目标目录不在已知分工范围内，请确认："
        log_warn "  - 日常项目文档 → /Users/liantian/workspace/"
        log_warn "  - OpenClaw 配置 → ~/.openclaw/workspace/"
        return 1
    fi
    
    # 检查目录是否存在
    local dir=$(dirname "$target_path")
    if [ ! -d "$dir" ]; then
        log_warn "⚠ 目录不存在：$dir"
        read -p "是否创建该目录？(y/n): " confirm
        if [ "$confirm" != "y" ]; then
            log_error "操作取消"
            return 1
        fi
    fi
    
    log_info "✓ 文件操作预检查通过"
    return 0
}

# 检查 2: 技能使用 - 验证技能是否存在
check_skill_exists() {
    local skill_name="$1"
    
    log_info "检查技能：$skill_name"
    
    if [ -d "$SKILLS_DIR/$skill_name" ]; then
        log_info "✓ 技能存在：$SKILLS_DIR/$skill_name"
        
        # 检查 SKILL.md
        if [ -f "$SKILLS_DIR/$skill_name/SKILL.md" ]; then
            log_info "✓ SKILL.md 存在"
        else
            log_warn "⚠ SKILL.md 不存在，技能可能不完整"
        fi
    else
        log_error "✗ 技能不存在：$skill_name"
        log_info "已安装技能列表："
        ls -1 "$SKILLS_DIR" 2>/dev/null || log_info "skills/ 目录为空"
        return 1
    fi
    
    log_info "✓ 技能检查通过"
    return 0
}

# 检查 3: 学习条目检索 - 根据关键词检索相关学习
check_learnings() {
    local keywords="$1"
    
    log_info "检索学习条目：$keywords"
    
    if [ ! -f "$LEARNINGS_MD" ]; then
        log_info "学习记录文件不存在"
        return 0
    fi
    
    # 检索相关条目
    local results=$(grep -i -B2 -A10 "$keywords" "$LEARNINGS_MD" 2>/dev/null || true)
    
    if [ -n "$results" ]; then
        log_info "找到相关学习条目："
        echo "$results"
    else
        log_info "未找到相关学习条目"
    fi
    
    return 0
}

# 检查 4: 宪法原则注入
inject_constitution() {
    log_info "注入 Friday 宪法原则..."
    
    if [ ! -f "$CONSTITUTION_MD" ]; then
        log_error "宪法文件不存在：$CONSTITUTION_MD"
        return 1
    fi
    
    # 输出核心原则摘要
    echo ""
    echo "════════════════════════════════════════"
    echo "📜 Friday 宪法 - 核心原则"
    echo "════════════════════════════════════════"
    grep -E "^### [0-9]+️⃣" "$CONSTITUTION_MD" | head -5
    echo ""
    echo "📌 详细原则请参阅：$CONSTITUTION_MD"
    echo "════════════════════════════════════════"
    echo ""
    
    return 0
}

# 主函数：根据操作类型执行相应检查
main() {
    local operation="$1"
    shift
    
    case "$operation" in
        file_write)
            log_info "执行文件写操作预检查..."
            inject_constitution
            check_file_operation "$@"
            ;;
        skill_use)
            log_info "执行技能使用预检查..."
            inject_constitution
            check_skill_exists "$@"
            ;;
        learning_check)
            log_info "执行学习条目检索..."
            check_learnings "$@"
            ;;
        full_check)
            log_info "执行完整预检查..."
            inject_constitution
            ;;
        *)
            log_error "未知操作类型：$operation"
            echo "用法：$0 {file_write|skill_use|learning_check|full_check} [args...]"
            echo ""
            echo "操作类型:"
            echo "  file_write <path>    - 文件写操作检查"
            echo "  skill_use <name>     - 技能使用检查"
            echo "  learning_check <kw>  - 学习条目检索"
            echo "  full_check           - 完整检查（宪法注入）"
            exit 1
            ;;
    esac
}

# 如果没有参数，显示帮助
if [ $# -eq 0 ]; then
    main "full_check"
else
    main "$@"
fi
