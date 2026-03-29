#!/bin/bash
# claw-rl 文档分类脚本

cd /Users/liantian/workspace/osprojects/claw-rl/docs

# v0.5.0 相关文档
mv REFACTOR_PLAN_v0.5.0.md v0.5.0/ 2>/dev/null || true
mv RELEASE_NOTES_v0.5.0.md v0.5.0/ 2>/dev/null || true
mv RELEASE_PLAN_v0.5.0.md v0.5.0/ 2>/dev/null || true

# v0.6.0 相关文档
mv DEPLOYMENT_REPORT_v0.6.0.md v0.6.0/ 2>/dev/null || true
mv DEPLOYMENT_COMPLETE_v0.6.0.md v0.6.0/ 2>/dev/null || true

# v0.7.0 相关文档
mv DEPLOYMENT_REPORT_v0.7.0.md v0.7.0/ 2>/dev/null || true

# v0.8.0, v0.9.0 暂无特定文档

# v1.0.0 相关文档
mv FINAL_STATUS_v1.0.0.md v1.0.0/ 2>/dev/null || true
mv PHASE3_PLAN.md v1.0.0/ 2>/dev/null || true
mv RELEASE_PLAN.md v1.0.0/ 2>/dev/null || true
mv p0-emotion-dashboard-v1.0.0.md v1.0.0/ 2>/dev/null || true
mv p1-expression-radar-v1.0.0.md v1.0.0/ 2>/dev/null || true
mv p2-openclaw-integration-notes.md v1.0.0/ 2>/dev/null || true
mv p2-pillar-collaboration-demo.md v1.0.0/ 2>/dev/null || true

# Phase 2 相关文档归档
mv PHASE2_DESIGN.md archive/ 2>/dev/null || true
mv PHASE2_README.md archive/ 2>/dev/null || true
mv phase2-fix-report.md archive/ 2>/dev/null || true
mv phase2-summary-report.md archive/ 2>/dev/null || true
mv phase2-technical-review-report.md archive/ 2>/dev/null || true

# 归档旧文档
mv CLAW_RL_CURRENT_STATUS.md archive/ 2>/dev/null || true
mv CLAW_RL_INTEGRATION_PLAN.md archive/ 2>/dev/null || true
mv CLAW_RL_MIGRATION_REPORT.md archive/ 2>/dev/null || true
mv CLAW_RL_PROJECT_STRUCTURE.md archive/ 2>/dev/null || true
mv CLAW_RL_REFACTORING_PLAN.md archive/ 2>/dev/null || true
mv VISION_ALIGNMENT_CLAW_RL.md archive/ 2>/dev/null || true
mv SHELL_PYTHON_INTEGRATION.md archive/ 2>/dev/null || true
mv work-log-2026-03-29.md archive/ 2>/dev/null || true

echo "claw-rl 文档分类完成！"
