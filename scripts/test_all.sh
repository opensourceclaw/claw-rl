#!/bin/bash

# claw-rl Phase 2 综合测试脚本

SCRIPTS_DIR="/Users/liantian/.openclaw/workspace/claw-rl/scripts"

echo "════════════════════════════════════════"
echo "🧪 claw-rl Phase 2 综合测试"
echo "════════════════════════════════════════"
echo ""

# 测试 1: PRM Judge
echo "测试 1: PRM Judge - 满意反馈"
echo "输入：'谢谢，很好'"
bash "$SCRIPTS_DIR/prm_judge.sh" rule "谢谢，很好" "创建了文件" 2>&1 | grep -E "(奖励 | 原因)"
echo ""

echo "测试 2: PRM Judge - 不满意反馈"
echo "输入：'不对，应该放这里'"
bash "$SCRIPTS_DIR/prm_judge.sh" rule "不对，应该放这里" "创建了文件" 2>&1 | grep -E "(奖励 | 原因)"
echo ""

# 测试 3: Hint Extractor
echo "测试 3: Hint Extractor - '应该'模式"
echo "输入：'应该先检查文件'"
bash "$SCRIPTS_DIR/hint_extractor.sh" extract "应该先检查文件" 2>&1 | grep -E "(Hint|提取)"
echo ""

echo "测试 4: Hint Extractor - '不要'模式"
echo "输入：'不要直接执行'"
bash "$SCRIPTS_DIR/hint_extractor.sh" extract "不要直接执行" 2>&1 | grep -E "(Hint|提取)"
echo ""

# 测试 5: Reward Collector
echo "测试 5: Reward Collector - 记录奖励"
bash "$SCRIPTS_DIR/reward_collector.sh" summary 2>&1 | head -10
echo ""

# 测试 6: Training Loop
echo "测试 6: Training Loop - 生成报告"
bash "$SCRIPTS_DIR/training_loop.sh" report 2>&1 | head -15
echo ""

echo "════════════════════════════════════════"
echo "✅ 测试完成"
echo "════════════════════════════════════════"
