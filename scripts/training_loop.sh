#!/bin/bash

# claw-rl Training Loop Script
# 用途：处理学习循环，记录奖励和提示
#
# v0.5.0: 集成 Python claw_rl.learning_loop 模块

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_ROOT/data"

# 颜色输出
GREEN='\033[0;32m'
NC='\033[0m'

# 检查虚拟环境
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# 确保数据目录存在
mkdir -p "$DATA_DIR"/{rewards,hints,learnings}

# 显示帮助
show_help() {
    echo "用法：training_loop.sh <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  run <反馈> <动作> [上下文]  - 处理一次学习循环"
    echo "  stats                       - 显示学习统计"
    echo "  recent [数量]               - 显示最近的学习记录"
    echo ""
    echo "示例:"
    echo "  training_loop.sh run '谢谢' 'created file' 'User asked to create test.txt'"
    echo "  training_loop.sh stats"
    echo "  training_loop.sh recent 5"
}

# 运行学习循环
run_learning() {
    local feedback="$1"
    local action="$2"
    local context="${3:-}"
    
    if [ -z "$feedback" ] || [ -z "$action" ]; then
        echo "错误：缺少反馈或动作参数"
        show_help
        exit 1
    fi
    
    # 调用 Python 模块
    python3 -c "
from claw_rl import LearningLoop
from pathlib import Path
import json

data_dir = Path('$DATA_DIR')
loop = LearningLoop(data_dir)

feedback = '''$feedback'''
action = '''$action'''
context = '''$context'''

result = loop.process_feedback(feedback, action, context)

print('学习记录已保存:')
print(f\"  奖励：{result['reward']}\")
print(f\"  置信度：{result['confidence']}\")
print(f\"  提示数量：{len(result['hints'])}\")
print(f\"  时间：{result['timestamp']}\")

if result['hints']:
    print()
    print('提取的提示:')
    for hint in result['hints']:
        print(f\"  - [{hint['hint_type']}] {hint['content']}\")
"
}

# 显示统计
show_stats() {
    python3 -c "
from claw_rl import LearningLoop
from pathlib import Path

data_dir = Path('$DATA_DIR')
loop = LearningLoop(data_dir)

stats = loop.get_statistics()

print('学习统计:')
print(f\"  总学习次数：{stats['total_learnings']}\")
print(f\"  总提示数量：{stats['total_hints']}\")
print(f\"  正面奖励：{stats['positive_rewards']}\")
print(f\"  中性奖励：{stats['neutral_rewards']}\")
print(f\"  负面奖励：{stats['negative_rewards']}\")
print(f\"  学习率：{stats['learning_rate']:.1%}\")
"
}

# 显示最近记录
show_recent() {
    local limit="${1:-10}"
    
    python3 -c "
from claw_rl import LearningLoop
from pathlib import Path

data_dir = Path('$DATA_DIR')
loop = LearningLoop(data_dir)

learnings = loop.get_recent_learnings(limit=$limit)

print(f'最近 {len(learnings)} 条学习记录:')
print()
for i, learning in enumerate(learnings, 1):
    print(f\"{i}. [{learning['timestamp']}]")
    print(f\"   反馈：{learning['feedback']}\")
    print(f\"   动作：{learning['action']}\")
    print(f\"   奖励：{learning['reward']}\")
    if learning['hints']:
        print(f\"   提示：{len(learning['hints'])} 条\")
    print()
"
}

# 主函数
main() {
    local command="${1:-}"
    
    case "$command" in
        run)
            shift
            run_learning "$@"
            ;;
        stats)
            show_stats
            ;;
        recent)
            shift
            show_recent "$@"
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "错误：未知命令 '$command'"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
