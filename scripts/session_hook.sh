#!/bin/bash

# claw-rl Session Hook Script
# 用途：在 OpenClaw 会话前后自动触发 claw-rl 功能

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/Users/liantian/.openclaw/workspace"

# 会话前钩子
pre_session_hook() {
    local user_input="$1"
    
    # 根据用户输入场景自动注入记忆
    if echo "$user_input" | grep -qiE "(文件 | 创建 | 写入 | 保存)"; then
        "$SCRIPT_DIR/memory_retrieval.sh" file 2>/dev/null
    elif echo "$user_input" | grep -qiE "(技能 | 工具 | 命令)"; then
        "$SCRIPT_DIR/memory_retrieval.sh" skill 2>/dev/null
    elif echo "$user_input" | grep -qiE "(执行 | 权限 | 授权)"; then
        "$SCRIPT_DIR/memory_retrieval.sh" permission 2>/dev/null
    else
        # 通用场景
        "$SCRIPT_DIR/memory_retrieval.sh" auto general 2>/dev/null
    fi
}

# 会话后钩子（处理学习信号）
post_session_hook() {
    local user_input="$1"
    local ai_response="$2"
    local user_reply="$3"
    
    # 如果有用户回复，评估学习信号
    if [ -n "$user_reply" ]; then
        # PRM Judge 评估
        "$SCRIPT_DIR/prm_judge.sh" rule "$user_reply" "$ai_response" 2>/dev/null
        
        # OPD Hint 提取（如果用户纠正）
        if echo "$user_reply" | grep -qiE "(不对 | 错了 | 应该 | 不要)"; then
            "$SCRIPT_DIR/hint_extractor.sh" extract "$user_reply" "$ai_response" 2>/dev/null
        fi
    fi
}

# 主函数
main() {
    local hook_type="$1"
    shift
    
    case "$hook_type" in
        pre)
            pre_session_hook "$@"
            ;;
        post)
            post_session_hook "$@"
            ;;
        *)
            echo "用法：$0 {pre|post} [args...]"
            exit 1
            ;;
    esac
}

main "$@"
