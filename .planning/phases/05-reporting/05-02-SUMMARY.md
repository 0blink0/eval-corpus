---
phase: 05-reporting
plan: 02
subsystem: testing
tags: [synthetic-data, batch-runner, retry, threshold, smoke]
requires:
  - phase: 04-metrics
    provides: 统一指标产物可用于后续批跑验证输入
provides:
  - 三类型可复现合成数据生成能力
  - 单机目录递归批跑与失败策略控制
  - DATA-01/DATA-02 契约测试
affects: [phase-05-reporting, smoke-tests, batch-processing]
tech-stack:
  added: []
  patterns: [seeded-synthetic-generation, continue-on-error-batch-policy]
key-files:
  created:
    - src/eval_corpus/batch/__init__.py
    - src/eval_corpus/batch/models.py
    - src/eval_corpus/batch/runner.py
  modified: []
key-decisions:
  - "批跑失败阈值按 total 失败占比进行判定，并在达到阈值时终止。"
  - "目录递归批跑保持单机模型，使用可配置 worker/retry，不引入分布式组件。"
patterns-established:
  - "Pattern 1: synthetic_data 使用固定 seed + 参数模型保证可复现。"
  - "Pattern 2: batch runner 统一收敛 total/succeeded/failed/retry_succeeded 统计。"
requirements-completed: [DATA-01, DATA-02]
duration: 18min
completed: 2026-04-13
---

# Phase 05 Plan 02: Reporting Summary

**交付了可复现三类型合成数据生成器与支持失败阈值/重试的目录递归批跑器，可直接用于 smoke 与扩跑。**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-13T10:15:00Z
- **Completed:** 2026-04-13T10:33:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- 完成 text/scan/table 三类型合成样本生成，支持数量、长度、比例、seed 参数化并可复现。
- 完成单机目录递归批跑器，支持 continue-on-error、失败阈值中止与重试统计。
- 通过 `tests/test_synthetic_data.py` 与 `tests/test_batch_runner.py`，满足 DATA-01/DATA-02。

## Task Commits

Each task was committed atomically:

1. **Task 1: 实现三类型合成数据生成器（可复现）（RED）** - `e362891` (test)
2. **Task 1: 实现三类型合成数据生成器（可复现）（GREEN）** - `5e80e7b` (feat)
3. **Task 2: 实现目录递归批跑与失败策略控制（RED）** - `93846ad` (test)
4. **Task 2: 实现目录递归批跑与失败策略控制（GREEN）** - `a7d97b8` (feat)

_Note: TDD tasks include test and feature commits._

## Files Created/Modified
- `src/eval_corpus/synthetic_data/models.py` - 生成参数与 manifest 模型，含范围校验上限。
- `src/eval_corpus/synthetic_data/generator.py` - 三类型样本生成与 deterministic 输出。
- `tests/test_synthetic_data.py` - 类型覆盖与同 seed 可复现测试。
- `src/eval_corpus/batch/models.py` - 批跑配置、错误与结果模型。
- `src/eval_corpus/batch/runner.py` - 目录递归、重试、阈值中止、汇总统计。
- `tests/test_batch_runner.py` - continue-on-error、失败阈值、重试成功契约测试。

## Decisions Made
- 失败阈值判定使用 `failed / total >= failure_threshold`，确保批量任务中止行为稳定且可预测。
- 对输入目录执行 `resolve` 后递归收集并限制在根目录内，满足路径边界安全约束。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] 补齐缺失的 `eval_corpus.batch` 模块**
- **Found during:** Task 2（目录递归批跑与失败策略控制）
- **Issue:** 测试收集时 `ModuleNotFoundError: No module named 'eval_corpus.batch'`，导致任务无法执行。
- **Fix:** 新增 `batch` 包及 `models.py`、`runner.py`、`__init__.py`，并补全失败阈值逻辑以通过既有 RED 测试。
- **Files modified:** `src/eval_corpus/batch/__init__.py`, `src/eval_corpus/batch/models.py`, `src/eval_corpus/batch/runner.py`
- **Verification:** `pytest tests/test_batch_runner.py -q` 通过
- **Committed in:** `a7d97b8`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** 偏差仅用于恢复任务可执行性与契约一致性，无额外范围扩张。

## Issues Encountered
- PowerShell 会话不支持 `&&` 链接命令；执行脚本改为分步命令后恢复稳定。

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- 合成数据与批跑基础已完成，可直接接入报告目录化落盘与 CLI 入口整合。
- 当前实现保持单机执行模型，后续可在不改语义前提下扩展云端运行说明。

## Self-Check: PASSED

- FOUND: `.planning/phases/05-reporting/05-02-SUMMARY.md`
- FOUND commits: `e362891`, `5e80e7b`, `93846ad`, `a7d97b8`

---
*Phase: 05-reporting*
*Completed: 2026-04-13*
