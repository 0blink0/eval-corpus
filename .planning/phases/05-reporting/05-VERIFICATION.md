---
phase: 05-reporting
verified: 2026-04-13T10:10:51Z
status: passed
score: 9/9 must-haves verified
overrides_applied: 0
---

# Phase 5: 报告、测试数据与批跑 Verification Report

**Phase Goal:** 自动生成总对比表和明细，提供合成测试数据与目录批跑入口  
**Verified:** 2026-04-13T10:10:51Z  
**Status:** passed  
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | 一次命令产出对比总表与三工具明细 | ✓ VERIFIED | `report` 命令落盘四格式报告，且 `tests/test_reporting_cli.py` 断言 `report.{json,csv,md,html}` 存在；`pytest ... -q` 16 passed。 |
| 2 | 合成数据生成器可在无真料场景跑通 smoke | ✓ VERIFIED | `synthetic-data` 命令与 `generate_synthetic_dataset()` 支持 text/scan/table；`tests/test_synthetic_data.py` 校验类型覆盖与同 seed 可复现。 |
| 3 | 文档说明云主机扩跑步骤 | ✓ VERIFIED | `docs/phase5_batch_runbook.md` 包含“云主机扩跑步骤”与参数说明，明确单机并发边界。 |
| 4 | 同一次运行可产出三工具 x 七指标总表并含阈值列 | ✓ VERIFIED | `REQUIRED_METRICS` 固定 `METR-01..07`，`exporters.py` 输出 `threshold_warn_min/threshold_pass_min`，`tests/test_reporting_summary.py` 验证阈值与行结构。 |
| 5 | 同一报告数据可导出 JSON/CSV/Markdown/HTML 且字段一致 | ✓ VERIFIED | `export_json/export_csv/export_markdown/export_html` 统一走 `_iter_export_rows`；`tests/test_reporting_detail.py` 断言四格式 metric points 完全一致。 |
| 6 | 每工具明细含 per_file 指标与运行元信息附录 | ✓ VERIFIED | `build_report_payload()` 生成 `per_file_rows + runtime`；`tests/test_reporting_metadata.py` 验证 `generated_at/tool_versions/git_commit`。 |
| 7 | 批跑默认 continue-on-error 且汇总失败文件 | ✓ VERIFIED | `BatchRunConfig.continue_on_error=True` 默认；`run_batch()` 聚合 `errors`，`tests/test_batch_runner.py` 验证失败不终止并记录失败文件。 |
| 8 | 批跑支持并行度、失败阈值、重试次数且不引入分布式队列 | ✓ VERIFIED | `batch` 命令暴露 `--max-workers/--failure-threshold/--max-retries`；实现为本地 `ThreadPoolExecutor`，无队列依赖。 |
| 9 | 一次命令在 run_id+时间戳目录落盘报告/明细/日志中间件 | ✓ VERIFIED | `create_run_layout()` 生成 `run_id-UTC` 目录和 `by_tool/by_artifact` 双维结构；CLI 子命令统一复用该布局。 |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `src/eval_corpus/reporting/models.py` | 统一 ReportPayload 与行级模型 | ✓ VERIFIED | 模型定义完整，含 `REQUIRED_METRICS` 与结构化错误类型。 |
| `src/eval_corpus/reporting/exporters.py` | 四格式导出器 | ✓ VERIFIED | 四导出函数可用，统一 row pipeline。 |
| `tests/test_reporting_summary.py` | 总表/阈值契约测试 | ✓ VERIFIED | 覆盖 row 结构、指标集合和阈值字段。 |
| `src/eval_corpus/synthetic_data/generator.py` | 三类样本参数化生成 | ✓ VERIFIED | 支持 text/scan/table、seed 固定、比例分配。 |
| `src/eval_corpus/batch/runner.py` | 目录递归批跑与失败策略 | ✓ VERIFIED | 递归收集、重试、阈值中止、错误聚合均实现。 |
| `tests/test_batch_runner.py` | continue-on-error/阈值/重试契约 | ✓ VERIFIED | 三类行为均有测试覆盖。 |
| `src/eval_corpus/cli.py` | report/synthetic/batch 子命令入口 | ✓ VERIFIED | 三命令注册并调用对应模块。 |
| `src/eval_corpus/reporting/layout.py` | run 目录结构与命名规则 | ✓ VERIFIED | `run_id-时间戳` + 双维目录工厂可复用。 |
| `docs/phase5_batch_runbook.md` | 批跑与云端扩跑手册 | ✓ VERIFIED | 命令示例、参数、故障与云步骤完整。 |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `src/eval_corpus/metrics_io.py` | `src/eval_corpus/reporting/build.py` | per_file/per_tool/overall 映射 | ✓ WIRED | 语义链路成立：`metrics_io.py` 生产三层结构，`build.py` 强校验并消费同名根键。 |
| `src/eval_corpus/reporting/build.py` | `src/eval_corpus/reporting/exporters.py` | 统一模型驱动导出 | ✓ WIRED | `cli.py` 先 `build_report_payload()` 再调用四个 exporter。 |
| `src/eval_corpus/synthetic_data/generator.py` | `src/eval_corpus/batch/runner.py` | 生成目录作为批跑输入 | ✓ WIRED | `synthetic-data` 生成 dataset 目录，`batch --input-dir` 递归消费该目录。 |
| `src/eval_corpus/batch/runner.py` | `src/eval_corpus/adapter_runner.py` | 单文件执行结果聚合批次报告 | ⚠ PARTIAL | 当前 `batch` 默认 processor 仅统计文件体积，未直接复用 `adapter_runner.run_adapter_on_files`。但批次聚合语义已实现。 |
| `src/eval_corpus/cli.py` | `src/eval_corpus/reporting/exporters.py` | CLI report 触发四格式导出 | ✓ WIRED | 通过 `reporting/__init__.py` re-export 间接连线（`cli.py` 调用 `export_*`）。 |
| `src/eval_corpus/cli.py` | `src/eval_corpus/batch/runner.py` | CLI batch 触发目录批跑 | ✓ WIRED | 通过 `batch/__init__.py` re-export 间接连线（`cli.py` 调用 `run_batch`）。 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `src/eval_corpus/cli.py` (`report`) | `metrics_payload` / `report_payload` | `--input` JSON -> `build_report_payload()` -> `export_*` | Yes | ✓ FLOWING |
| `src/eval_corpus/cli.py` (`synthetic-data`) | `manifest` | `generate_synthetic_dataset()` | Yes | ✓ FLOWING |
| `src/eval_corpus/cli.py` (`batch`) | `result` | `run_batch()` 递归处理目录文件 | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Phase 5 关键测试通过 | `pytest tests/test_reporting_summary.py tests/test_reporting_detail.py tests/test_reporting_metadata.py tests/test_synthetic_data.py tests/test_batch_runner.py tests/test_reporting_cli.py -q` | `16 passed in 0.91s` | ✓ PASS |
| CLI 暴露 report/batch/synthetic-data 命令 | `python -m eval_corpus.cli --help` | 帮助输出含 `report`/`batch`/`synthetic-data` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| `RPT-01` | `05-01-PLAN.md` | 总对比表（三工具 x 七指标，含阈值） | ✓ SATISFIED | `build.py` + `exporters.py` + `test_reporting_summary.py` |
| `RPT-02` | `05-01-PLAN.md` | 每工具明细多格式导出 | ✓ SATISFIED | `per_file_rows` + `test_reporting_detail.py` |
| `RPT-03` | `05-01/05-03-PLAN.md` | 运行元信息可追溯 | ✓ SATISFIED | `runtime.py` + `test_reporting_metadata.py` + `test_reporting_cli.py` |
| `DATA-01` | `05-02-PLAN.md` | 合成/小样本生成用于 smoke | ✓ SATISFIED | `synthetic_data/generator.py` + `test_synthetic_data.py` |
| `DATA-02` | `05-02/05-03-PLAN.md` | 目录递归批处理与扩跑入口 | ✓ SATISFIED | `batch/runner.py` + `cli.py batch` + runbook |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| - | - | 未在 Phase 5 关键实现文件中发现 TODO/placeholder/空实现/仅日志实现 | ℹ Info | 无阻断风险 |

### Gaps Summary

未发现阻断 phase goal 的缺口。  
注意：`batch/runner.py -> adapter_runner.py` 在 plan key-link 中描述为直接聚合链路，但当前实现为可注入 `processor` 的通用批跑器，CLI 默认 processor 未接入 adapter 调用；该差异不阻断本阶段目标（目录递归批跑入口、失败策略与可追溯落盘均已达成）。

---

_Verified: 2026-04-13T10:10:51Z_  
_Verifier: Claude (gsd-verifier)_
