---
phase: 04-metrics
plan: 03
subsystem: testing
tags: [python, typer, pytest, metrics]
requires:
  - phase: 04-01
    provides: METR-01~06 指标契约与计算函数
  - phase: 04-02
    provides: METR-07 规则评分与语义抽检基础
provides:
  - 三层聚合模块（per_file/per_tool/overall）
  - metrics JSON 工件 I/O 与结构校验
  - CLI `metrics` 子命令与端到端测试
affects: [phase-05-reporting, metrics-consumer]
tech-stack:
  added: []
  patterns: [single-json-artifact, cli-orchestration, applicability-preservation]
key-files:
  created:
    - src/eval_corpus/metrics/aggregate.py
    - src/eval_corpus/metrics_io.py
    - tests/test_metrics_aggregate.py
    - tests/test_metrics_cli.py
  modified:
    - src/eval_corpus/cli.py
key-decisions:
  - "Phase 4 输出统一为单一 JSON 工件，仅暴露 per_file/per_tool/overall 三层接口。"
  - "聚合层保留 raw_value/threshold/level 与 applicable/not_applicable/errors 统计，避免下游丢失审计信息。"
patterns-established:
  - "Pattern 1: 聚合逻辑与 CLI 编排分离，CLI 仅负责参数与落盘。"
  - "Pattern 2: 写出前执行 payload 结构校验，避免无效工件进入下游。"
requirements-completed: [METR-01, METR-02, METR-03, METR-04, METR-05, METR-06, METR-07]
duration: 8min
completed: 2026-04-13
---

# Phase 4 Plan 03: Metrics CLI & Artifact Summary

**交付了可一键执行的 metrics 标准接口：从适配器结果构建三层聚合并输出单一 JSON 工件，且通过 CLI 端到端回归测试验证。**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-13T17:12:34+08:00
- **Completed:** 2026-04-13T17:20:05+08:00
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- 新增 `aggregate.py`，实现 `per_file/per_tool/overall` 三层聚合与指标汇总。
- 新增 `metrics_io.py`，实现适配器结果到单 JSON 工件的构建、校验与写出。
- 在 `cli.py` 集成 `metrics` 命令，并补齐聚合与 CLI 端到端测试。

## Task Commits

Each task was committed atomically:

1. **Task 1: 实现三层聚合与聚合测试** - `e72f86a` (test), `013c718` (feat)
2. **Task 2: 新增 metrics JSON I/O 与 CLI metrics 命令** - `8b34c50` (feat)
3. **Task 3: 补齐 CLI 端到端测试并完成 Phase 4 验收** - `88b59a3` (test)

_Note: Task 1 采用 TDD，包含红灯测试提交 + 绿灯实现提交。_

## Files Created/Modified
- `src/eval_corpus/metrics/aggregate.py` - 三层聚合与跨文件/跨工具汇总。
- `src/eval_corpus/metrics_io.py` - metrics 工件读取、构建、结构校验与写出。
- `src/eval_corpus/cli.py` - 新增 `metrics` 命令入口与摘要输出。
- `tests/test_metrics_aggregate.py` - 三层结构与字段保留测试。
- `tests/test_metrics_cli.py` - 成功路径与参数错误路径端到端测试。

## Decisions Made
- 维持 D-51 的单工件策略，不在本计划引入 CSV/HTML/Markdown 输出分支。
- 将 `generated_at` 与 `runtime_metadata` 放入 `overall`，满足追溯与审计需求。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] 修复 PowerShell 下 `&&` 命令链导致验证脚本中断**
- **Found during:** Task 3
- **Issue:** 计划中的 bash 风格命令链在当前 PowerShell 环境报语法错误，阻塞测试执行。
- **Fix:** 改为 PowerShell 兼容的顺序执行与 `$LASTEXITCODE` 守卫。
- **Files modified:** 无代码文件修改（仅执行命令修正）
- **Verification:** `pytest` 定向与全量测试均通过
- **Committed in:** `88b59a3`（任务验收流程）

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** 仅影响执行命令形态，不影响功能范围与交付接口。

## Issues Encountered
- PowerShell 对 bash 风格 heredoc/`&&` 语法不兼容；已统一使用 PowerShell 兼容命令完成提交与验证。

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 4 现已具备可消费的标准 JSON 工件接口，Phase 5 可直接读取并生成报告层产物。
- 指标字段（raw/threshold/level + applicability）已在聚合与 CLI 层保持完整，适合做下游可解释报告。

## Self-Check: PASSED

- Summary file exists: `.planning/phases/04-metrics/04-03-SUMMARY.md`
- Commit hashes verified in git history: `e72f86a`, `013c718`, `8b34c50`, `88b59a3`

---
*Phase: 04-metrics*
*Completed: 2026-04-13*
