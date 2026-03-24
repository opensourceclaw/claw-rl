#!/bin/bash

# claw-rl PRM Judge Script
# 用途：评估用户回复，判断对 AI 动作的满意度
# 输出：+1 (满意) / -1 (不满意) / 0 (中性)
# 
# v0.5.0: 集成 Python claw_rl.binary_rl 模块

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查虚拟环境
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# 显示帮助
show_help() {
    echo "用法：prm_judge.sh <用户反馈> [动作描述]"
    echo ""
    echo "示例:"
    echo "  prm_judge.sh '谢谢，很好！' 'created file'"
    echo "  prm_judge.sh '不对，应该这样' 'deleted file'"
    echo ""
    echo "输出："
    echo "  reward: +1 (满意), -1 (不满意), 0 (中性)"
}

# 主函数
main() {
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_help
        exit 0
    fi
    
    if [ -z "$1" ]; then
        echo "错误：缺少用户反馈参数"
        show_help
        exit 1
    fi
    
    local feedback="$1"
    local action="${2:-}"
    
    # 调用 Python 模块
    local result
    result=$(python3 -c "
from claw_rl import BinaryRLJudge
import json

judge = BinaryRLJudge()
feedback = '''$feedback'''
action = '''$action'''

result = judge.judge_with_reason(feedback, action)
print(json.dumps({
    'reward': result.reward,
    'confidence': result.confidence,
    'pattern_matched': result.pattern_matched
}))
" 2>/dev/null)
    
    # 解析结果
    local reward confidence pattern
    reward=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['reward'])")
    confidence=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['confidence'])")
    pattern=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['pattern_matched'])")
    
    # 显示结果
    case "$reward" in
        1)
            printf "${GREEN}[PRM]${NC} 奖励：+1 (满意)\n"
            ;;
        -1)
            printf "${RED}[PRM]${NC} 奖励：-1 (不满意)\n"
            ;;
        0)
            printf "${YELLOW}[PRM]${NC} 奖励：0 (中性)\n"
            ;;
    esac
    
    echo "置信度：$confidence"
    echo "匹配模式：$pattern"
    
    # 返回奖励值
    return $((reward < 0 ? 1 : reward))
}

main "$@"
