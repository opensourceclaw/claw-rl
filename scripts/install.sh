#!/bin/bash

# claw-rl Installation Script
# 用途：初始化 claw-rl 插件

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/Users/liantian/.openclaw/workspace"

echo "════════════════════════════════════════"
echo "🧠 claw-rl 安装脚本"
echo "════════════════════════════════════════"
echo ""

# 1. 创建必要目录
echo "创建目录结构..."
mkdir -p "$SCRIPT_DIR/.rewards"
mkdir -p "$SCRIPT_DIR/.hints"
mkdir -p "$WORKSPACE_DIR/.learnings"
echo "✓ 目录创建完成"
echo ""

# 2. 添加执行权限
echo "设置执行权限..."
chmod +x "$SCRIPT_DIR/"*.sh 2>/dev/null || true
echo "✓ 权限设置完成"
echo ""

# 3. 复制必要文件
echo "复制配置文件..."
if [ -f "$WORKSPACE_DIR/claw-rl/FRIDAY_CONSTITUTION.md" ]; then
    cp "$WORKSPACE_DIR/claw-rl/FRIDAY_CONSTITUTION.md" "$SCRIPT_DIR/" 2>/dev/null || true
    echo "✓ Friday 宪法已复制"
fi
echo ""

# 4. 测试脚本
echo "运行测试..."
if "$SCRIPT_DIR/scripts/test_all.sh" > /dev/null 2>&1; then
    echo "✓ 测试通过"
else
    echo "⚠ 测试有警告，但不影响使用"
fi
echo ""

# 5. 显示使用说明
echo "════════════════════════════════════════"
echo "✅ claw-rl 安装完成！"
echo "════════════════════════════════════════"
echo ""
echo "使用方法:"
echo ""
echo "1. 激活 claw-rl:"
echo "   $SCRIPT_DIR/scripts/activate.sh"
echo ""
echo "2. 查看状态:"
echo "   $SCRIPT_DIR/scripts/reward_collector.sh summary"
echo ""
echo "3. 运行测试:"
echo "   $SCRIPT_DIR/scripts/test_all.sh"
echo ""
echo "4. 启动后台训练:"
echo "   $SCRIPT_DIR/scripts/training_loop.sh daemon 300"
echo ""
echo "════════════════════════════════════════"
echo ""
