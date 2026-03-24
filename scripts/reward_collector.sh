#!/bin/bash

# claw-rl Reward Collector Script
# 用途：收集和处理奖励信号，触发学习更新

WORKSPACE_DIR="/Users/liantian/.openclaw/workspace"
REWARDS_DIR="$WORKSPACE_DIR/claw-rl/.rewards"
LEARNINGS_MD="$WORKSPACE_DIR/.learnings/LEARNINGS.md"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_section() {
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
}

# 初始化奖励目录
init_rewards_dir() {
    mkdir -p "$REWARDS_DIR"
    log_info "奖励目录：$REWARDS_DIR"
}

# 记录奖励
record_reward() {
    local reward="$1"
    local reason="$2"
    local action="$3"
    local reply="$4"
    local timestamp=$(date -Iseconds)
    
    local today=$(date +%Y-%m-%d)
    local rewards_file="$REWARDS_DIR/$today.jsonl"
    
    # JSONL 格式
    echo "{\"timestamp\":\"$timestamp\",\"reward\":$reward,\"reason\":\"$reason\",\"action\":\"$action\",\"reply\":\"$reply\"}" >> "$rewards_file"
    
    log_info "奖励已记录：r=$reward"
}

# 统计今日奖励
summarize_today() {
    local today=$(date +%Y-%m-%d)
    local rewards_file="$REWARDS_DIR/$today.jsonl"
    
    log_section "📊 今日奖励统计 ($today)"
    
    if [ ! -f "$rewards_file" ]; then
        log_info "今日暂无奖励记录"
        return
    fi
    
    local total=$(wc -l < "$rewards_file")
    local positive=$(grep -c '"reward":1' "$rewards_file" 2>/dev/null || echo 0)
    local negative=$(grep -c '"reward":-1' "$rewards_file" 2>/dev/null || echo 0)
    local neutral=$(grep -c '"reward":0' "$rewards_file" 2>/dev/null || echo 0)
    
    echo "总记录数：$total"
    echo "正面奖励 (+1): $positive"
    echo "负面奖励 (-1): $negative"
    echo "中性奖励 (0):  $neutral"
    
    if [ "$total" -gt 0 ]; then
        local avg=$(echo "scale=2; ($positive - $negative) / $total" | bc 2>/dev/null || echo "N/A")
        echo "平均奖励：$avg"
    fi
    
    echo ""
}

# 检测需要学习的场景（累积负面奖励）
check_learning_triggers() {
    log_section "🔍 检测学习触发条件"
    
    # 查找累积负面奖励 >= 3 的场景
    local rewards_file="$REWARDS_DIR/$(date +%Y-%m-%d).jsonl"
    
    if [ ! -f "$rewards_file" ]; then
        log_info "无奖励记录"
        return
    fi
    
    # 简化：检查是否有连续负面奖励
    local neg_count=$(grep -c '"reward":-1' "$rewards_file" 2>/dev/null || echo 0)
    
    if [ "$neg_count" -ge 3 ]; then
        log_warn "⚠️  检测到 $neg_count 次负面奖励，建议生成学习条目"
        echo ""
        echo "最近负面奖励："
        grep '"reward":-1' "$rewards_file" | tail -3 | while read -r line; do
            echo "  $line"
        done
    else
        log_info "负面奖励次数：$neg_count (阈值：3)"
    fi
}

# 生成学习条目
generate_learning() {
    local action="$1"
    local feedback="$2"
    local lesson="$3"
    
    if [ ! -f "$LEARNINGS_MD" ]; then
        log_error "学习记录文件不存在：$LEARNINGS_MD"
        return 1
    fi
    
    local id=$(date +%Y%m%d)-$(shuf -i 1-999 -n 1)
    local timestamp=$(date -Iseconds)
    
    cat >> "$LEARNINGS_MD" << EOF

---

## [LRN-$id] 自动学习条目

**Logged**: $timestamp
**Priority**: high
**Status**: pending
**Area**: workflow

### Summary
$lesson

### Details
- 动作：$action
- 用户反馈：$feedback
- 来源：claw-rl Phase 2 自动学习

### Suggested Action
$lesson

### Metadata
- Source: claw-rl-reward-system
- Tags: 自动学习，RL, Phase2
- Pattern-Key: auto.learn.$(echo "$lesson" | head -c 20 | tr ' ' '_')

---
EOF
    
    log_info "学习条目已生成：LRN-$id"
}

# 主函数
main() {
    local action="${1:-summary}"
    shift || true
    
    init_rewards_dir
    
    case "$action" in
        record)
            # record <reward> <reason> <action> <reply>
            record_reward "$@"
            ;;
        summary)
            summarize_today
            check_learning_triggers
            ;;
        check)
            check_learning_triggers
            ;;
        generate)
            # generate <action> <feedback> <lesson>
            generate_learning "$@"
            ;;
        *)
            echo "用法：$0 {record|summary|check|generate} [args...]"
            echo ""
            echo "命令:"
            echo "  record <r> <reason> <action> <reply>  - 记录奖励"
            echo "  summary                               - 今日统计"
            echo "  check                                 - 检查学习触发"
            echo "  generate <action> <feedback> <lesson> - 生成学习条目"
            exit 1
            ;;
    esac
}

main "$@"
