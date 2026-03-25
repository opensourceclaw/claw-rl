#!/bin/bash

# claw-rl OPD Hint Extractor Script
# 用途：从用户纠正中提取学习提示
# 输出：OPD hint (JSON 格式)
#
# v0.5.0: 集成 Python claw_rl.opd_hint 模块

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
GREEN='\033[0;32m'
NC='\033[0m'

# 检查虚拟环境
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# 显示帮助
show_help() {
    echo "用法：hint_extractor.sh <用户反馈> [context]"
    echo ""
    echo "示例:"
    echo "  hint_extractor.sh '应该先检查文件'"
    echo "  hint_extractor.sh '不要放到 workspace'"
    echo "  hint_extractor.sh '先确认目录，再创建文件'"
    echo "  hint_extractor.sh '应该先检查' '{\"agent\": \"Tech\"}'"
    echo ""
    echo "输出："
    echo "  hint_type: should, should_not, sequence, conditional"
    echo "  content: 提取的提示内容"
    echo "  priority: 1-5 (越高越重要)"
    echo "  confidence: 0.0-1.0"
    echo "  context: 可选上下文信息（v0.6.0+）"
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
    local context="${2:-}"  # 可选参数：context
    
    # 调用 Python 模块
    local result
    if [ -n "$context" ]; then
        result=$(python3 -c "
from claw_rl import OPDHintExtractor
import json

extractor = OPDHintExtractor()
feedback = '''$feedback'''
context = '''$context'''

hint = extractor.extract(feedback, context=context)
if hint:
    print(json.dumps({
        'hint_type': hint.hint_type,
        'content': hint.content,
        'priority': hint.priority,
        'confidence': hint.confidence,
        'context': context,
        'found': True
    }))
else:
    print(json.dumps({
        'found': False,
        'message': 'No pattern matched'
    }))
" 2>/dev/null)
    else
        result=$(python3 -c "
from claw_rl import OPDHintExtractor
import json

extractor = OPDHintExtractor()
feedback = '''$feedback'''

hint = extractor.extract(feedback)
if hint:
    print(json.dumps({
        'hint_type': hint.hint_type,
        'content': hint.content,
        'priority': hint.priority,
        'confidence': hint.confidence,
        'found': True
    }))
else:
    print(json.dumps({
        'found': False,
        'message': 'No pattern matched'
    }))
" 2>/dev/null)
    fi
    
    # 解析并显示结果
    local found hint_type content priority confidence
    found=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['found'])")
    
    if [ "$found" = "True" ]; then
        hint_type=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['hint_type'])")
        content=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['content'])")
        priority=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['priority'])")
        confidence=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin)['confidence'])")
        
        echo -e "${GREEN}[OPD]${NC} 提取到提示:"
        echo "  类型：$hint_type"
        echo "  内容：$content"
        echo "  优先级：$priority"
        echo "  置信度：$confidence"
    else
        echo "未提取到提示（无匹配模式）"
    fi
    
    # 输出 JSON（便于脚本处理）
    echo ""
    echo "JSON 输出:"
    echo "$result" | python3 -m json.tool
}

main "$@"
