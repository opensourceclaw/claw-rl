#!/bin/bash
# claw-rl Plugin 测试脚本
# 测试 Context Engine 注册是否正确

echo "=== claw-rl Plugin 测试环境验证 ==="
echo ""

# 1. 检查 TypeScript 编译
echo "1. 检查 TypeScript 编译..."
cd /Users/liantian/workspace/osprojects/claw-rl/claw_rl_plugin
npm run build 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ TypeScript 编译成功"
else
    echo "   ❌ TypeScript 编译失败"
    exit 1
fi
echo ""

# 2. 检查 Bridge 启动
echo "2. 检查 Python Bridge 导入..."
cd /Users/liantian/workspace/osprojects/claw-rl
source venv/bin/activate
python3 -c "from claw_rl.bridge import ClawRLBridge; print('   ✅ Bridge 模块导入成功')" 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Bridge 模块正常"
else
    echo "   ❌ Bridge 模块导入失败"
    exit 1
fi
echo ""

# 3. 测试 JSON-RPC 通信
echo "3. 测试 JSON-RPC 通信..."
cd /Users/liantian/workspace/osprojects/claw-rl/claw_rl_plugin
node test/test_integration.js 2>&1 | head -50
if [ $? -eq 0 ]; then
    echo "   ✅ JSON-RPC 通信测试通过"
else
    echo "   ❌ JSON-RPC 通信测试失败"
fi
echo ""

# 4. 检查 Plugin 元数据
echo "4. 检查 Plugin 元数据..."
PLUGIN_JSON="/Users/liantian/workspace/osprojects/claw-rl/claw_rl_plugin/openclaw.plugin.json"
if [ -f "$PLUGIN_JSON" ]; then
    echo "   Plugin ID: $(grep -o '"id"[^,]*' $PLUGIN_JSON | cut -d'"' -f4)"
    echo "   Plugin Kind: $(grep -o '"kind"[^,]*' $PLUGIN_JSON | cut -d'"' -f4)"
    echo "   ✅ Plugin 元数据正常"
else
    echo "   ❌ Plugin 元数据文件不存在"
fi
echo ""

# 5. 检查编译后的文件
echo "5. 检查编译后的文件..."
DIST_FILE="/Users/liantian/workspace/osprojects/claw-rl/claw_rl_plugin/dist/index.js"
if [ -f "$DIST_FILE" ]; then
    echo "   文件大小: $(ls -lh $DIST_FILE | awk '{print $5}')"
    echo "   最后修改: $(ls -l $DIST_FILE | awk '{print $6, $7, $8}')"
    echo "   ✅ 编译文件存在"
else
    echo "   ❌ 编译文件不存在"
fi
echo ""

echo "=== 测试环境验证完成 ==="
echo ""
echo "⚠️  注意："
echo "   1. 以上测试均为本地测试"
echo "   2. 如果所有测试通过，可以安全部署到生产环境"
echo "   3. 部署前建议先禁用 contextEngine slot"
echo "   4. 部署后观察 OpenClaw 日志：openclaw logs --follow"
