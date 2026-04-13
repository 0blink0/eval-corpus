---
phase: 05-reporting
plan: 01
subsystem: reporting
tags: [metrics, reporting, csv, markdown, html, json]
requires:
  - phase: 04-metrics
    provides: 统一的 per_file/per_tool/overall 指标工件
provides:
  - 统一 ReportPayload 模型与构建器
  - JSON/CSV/Markdown/HTML 四格式导出器
  - 报告层总表/明细/元信息契约测试
affects: [phase-05-reporting, verification, cli-reporting]
tech-stack:
  added: []
  patterns: [single-canonical-model, multi-format-export-from-shared-rows]
key-files:
  created:
    - src/eval_corpus/reporting/models.py
    - src/eval_corpus/reporting/build.py
    - src/eval_corpus/reporting/exporters.py
    - tests/test_reporting_summary.py
    - tests/test_reporting_detail.py
    - tests/test_reporting_metadata.py
  modified:
    - src/eval_corpus/reporting/__init__.py
key-decisions:
  - "报告层只消费 Phase 4 工件，不在报告层重算指标。"
  - "四格式导出统一复用同一行级数据集，避免字段漂移。"
patterns-established:
  - "Pattern 1: 先构建 canonical ReportPayload，再执行格式导出。"
  - "Pattern 2: HTML 导出统一 escape 动态文本字段。"
requirements-completed: [RPT-01, RPT-02, RPT-03]
duration: 3min
completed: 2026-04-13
---

# Phase 05 Plan 01: Reporting Summary

**基于 Phase 4 指标工件交付了可审计的统一报告模型，并一次性导出 JSON/CSV/Markdown/HTML 四种一致格式。**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-13T17:51:41+08:00
- **Completed:** 2026-04-13T17:54:09+08:00
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- 建立 `ReportPayload` / `SummaryRow` / `DetailRow` / `RuntimeAppendix` 统一模型与结构化校验错误。
- 实现 `per_file/per_tool/overall` 到 canonical 报告模型的稳定映射，保障三工具 + overall 总表一致排序。
- 实现四格式导出器并保证跨格式指标字段一致，且在 HTML 输出执行文本 escape 以降低注入风险。

## Task Commits

Each task was committed atomically:

1. **Task 1: 建立统一报告数据模型与构建器（RED）** - `f41ddb7` (test)
2. **Task 1: 建立统一报告数据模型与构建器（GREEN）** - `02a5f19` (feat)
3. **Task 2: 实现四格式导出器与每工具明细输出（RED）** - `a47a114` (test)
4. **Task 2: 实现四格式导出器与每工具明细输出（GREEN）** - `6ed9007` (feat)

_Note: TDD tasks include test and feature commits._

## Files Created/Modified
- `src/eval_corpus/reporting/models.py` - 定义报告 canonical 模型与结构化错误类型。
- `src/eval_corpus/reporting/build.py` - 指标工件到报告模型的映射与必填字段校验。
- `src/eval_corpus/reporting/exporters.py` - 四格式导出实现，复用统一行级数据集。
- `src/eval_corpus/reporting/__init__.py` - 对外导出 builder 与 exporters API。
- `tests/test_reporting_summary.py` - 总表字段与排序契约测试。
- `tests/test_reporting_detail.py` - 跨格式一致性与明细字段契约测试。
- `tests/test_reporting_metadata.py` - 运行元信息附录契约测试。

## Decisions Made
- 报告构建器对根键与指标缺失做结构化异常抛出，避免静默降级。
- 导出器统一复用 `_iter_export_rows`，确保 JSON/CSV/Markdown/HTML 口径完全同源。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- 已具备报告层核心能力，可直接在后续计划中接入 CLI 命令与落盘目录策略。
- 报告层测试基线完整，后续扩展输出样式不会影响字段契约。

## Self-Check: PASSED

- FOUND: `.planning/phases/05-reporting/05-01-SUMMARY.md`
- FOUND commits: `f41ddb7`, `02a5f19`, `a47a114`, `6ed9007`

---
*Phase: 05-reporting*
*Completed: 2026-04-13*
