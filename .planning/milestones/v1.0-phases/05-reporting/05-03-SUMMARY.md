---
phase: 05-reporting
plan: 03
subsystem: reporting
tags: [cli, reporting, batch, synthetic-data, runbook]
requires:
  - phase: 05-01
    provides: 报告统一模型与四格式导出器
  - phase: 05-02
    provides: 合成数据生成器与批跑执行器
provides:
  - report/synthetic-data/batch CLI 子命令入口
  - run_id+时间戳目录布局与 runtime 元信息采集
  - 批跑与云端扩跑运行手册
affects: [phase-05-reporting, cli-contracts, run-artifacts]
tech-stack:
  added: []
  patterns: [cli-orchestrated-run-layout, tdd-red-green-commits]
key-files:
  created:
    - src/eval_corpus/reporting/runtime.py
    - src/eval_corpus/reporting/layout.py
    - tests/test_reporting_cli.py
    - docs/phase5_batch_runbook.md
  modified:
    - src/eval_corpus/cli.py
    - src/eval_corpus/reporting/__init__.py
key-decisions:
  - "CLI 命令统一落盘到 by_tool/by_artifact 双维目录，保证可追溯与可比对。"
  - "report 命令在 git 不可用时降级为 git_commit:null 与 git_status:unavailable，不中断流程。"
patterns-established:
  - "Pattern 1: 先创建 run layout，再写入 report/batch/synthetic 各类工件。"
  - "Pattern 2: 参数/输入错误返回 2，运行中止返回 1，保持 CLI 退出码约定一致。"
requirements-completed: [RPT-03, DATA-02]
duration: 6min
completed: 2026-04-13
---

# Phase 05 Plan 03: Reporting Summary

**交付了 report/synthetic-data/batch 三个可执行 CLI 入口，并将报告、明细、日志与运行元信息统一落盘到 run_id+时间戳目录以支持本地与云主机扩跑。**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-13T10:00:20Z
- **Completed:** 2026-04-13T10:06:27Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- 新增 `report` 命令，消费 metrics 工件并一次性导出 JSON/CSV/Markdown/HTML 四格式报告。
- 新增 `batch` 与 `synthetic-data` 命令，支持目录递归、并发、失败阈值和重试参数。
- 新增 runbook，覆盖单机执行、常见故障排查和云主机扩跑步骤，并明确不引入分布式队列边界。

## Task Commits

Each task was committed atomically:

1. **Task 1: 实现 run 目录布局与运行元信息采集（RED）** - `3751505` (test)
2. **Task 1: 实现 run 目录布局与运行元信息采集（GREEN）** - `194b208` (feat)
3. **Task 2: 接入 CLI 子命令并打通端到端落盘（RED）** - `974fc3e` (test)
4. **Task 2: 接入 CLI 子命令并打通端到端落盘（GREEN）** - `a74dcdb` (feat)
5. **Task 3: 编写批跑与云端扩跑运行手册** - `2288ebe` (chore)

_Note: TDD tasks include test and feature commits._

## Files Created/Modified
- `src/eval_corpus/reporting/runtime.py` - 采集 generated_at/tool_versions/git_commit/git_status 并提供 git 不可用降级。
- `src/eval_corpus/reporting/layout.py` - 创建 `run_id-UTC时间戳` 根目录及 by_tool/by_artifact 双维目录。
- `src/eval_corpus/cli.py` - 新增 `report`、`batch`、`synthetic-data` 子命令并串联前置模块。
- `tests/test_reporting_cli.py` - 覆盖 run 目录契约与三类 CLI 命令端到端落盘契约。
- `docs/phase5_batch_runbook.md` - 提供批跑和云端扩跑操作手册。

## Decisions Made
- report/batch/synthetic-data 三命令全部复用统一 run 布局能力，不在命令层各自重复拼目录。
- batch 命令默认 continue-on-error，同时暴露阈值与重试参数满足单机扩跑控制需求。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- PowerShell 不支持 `&&` 与 bash heredoc 语法，提交命令改为 PowerShell here-string 方式后恢复。

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 5 最终 CLI 交付链路已贯通，可直接用于本地与云主机批跑。
- 报告导出、合成数据、批跑参数和 runbook 已形成完整可复现闭环。

---
*Phase: 05-reporting*
*Completed: 2026-04-13*

## Self-Check: PASSED

- FOUND: .planning/phases/05-reporting/05-03-SUMMARY.md
- FOUND: 3751505
- FOUND: 194b208
- FOUND: 974fc3e
- FOUND: a74dcdb
- FOUND: 2288ebe
