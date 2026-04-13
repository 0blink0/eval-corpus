---
phase: 04
slug: metrics
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-13
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `pytest tests/test_metrics_core.py -q -x` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~30-60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_metrics_core.py -q -x`
- **After every plan wave:** Run `pytest tests/test_metrics_*.py -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | METR-01 | T-04-01 | 输入严格校验，不可判定样本分流 | unit | `pytest tests/test_metrics_core.py::test_coverage_completeness -q -x` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | METR-02, METR-03 | T-04-01 | 长度/边界计算可重复且可解释 | unit | `pytest tests/test_metrics_core.py::test_length_and_boundary_metrics -q -x` | ❌ W0 | ⬜ pending |
| 04-01-03 | 01 | 1 | METR-04, METR-05, METR-06 | T-04-02 | 表格/重叠/元数据缺失不混分 | unit | `pytest tests/test_metrics_core.py::test_table_overlap_metadata_metrics -q -x` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 2 | METR-07 | T-04-03 | 规则评分与人工复核记录分离 | integration | `pytest tests/test_metrics_semantic.py::test_semantic_rule_score -q -x` | ❌ W0 | ⬜ pending |
| 04-02-02 | 02 | 2 | METR-07 | T-04-03 | 固定抽样可复现（seed+index） | integration | `pytest tests/test_metrics_semantic.py::test_semantic_sampling_reproducible -q -x` | ❌ W0 | ⬜ pending |
| 04-02-03 | 02 | 2 | METR-07 | T-04-03 | 人工复核仅校准不覆盖自动分 | integration | `pytest tests/test_metrics_semantic.py::test_manual_review_separated -q -x` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 3 | METR-01~METR-07 | T-04-04 | 三层聚合字段完整且一致 | unit | `pytest tests/test_metrics_aggregate.py -q -x` | ❌ W0 | ⬜ pending |
| 04-03-02 | 03 | 3 | METR-01~METR-07 | T-04-04 | 单一 JSON 输出含 raw/threshold/level | integration | `pytest tests/test_metrics_cli.py::test_metrics_json_output_schema -q -x` | ❌ W0 | ⬜ pending |
| 04-03-03 | 03 | 3 | METR-01~METR-07 | T-04-05 | CLI 错误路径结构化输出 | integration | `pytest tests/test_metrics_cli.py::test_metrics_cli_error_envelope -q -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_metrics_core.py` — stubs for METR-01~METR-06
- [ ] `tests/test_metrics_semantic.py` — stubs for METR-07
- [ ] `tests/test_metrics_aggregate.py` — per_file/per_tool/overall 聚合
- [ ] `tests/test_metrics_cli.py` — `metrics` 命令 I/O 与错误封装
- [ ] `tests/fixtures/metrics/` — 固定抽样夹具与种子数据

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 人工复核记录格式可读且可审计 | METR-07 | 人工抽检记录需要人工可读确认 | 运行 metrics 后检查 `semantic_review.manual_samples` 字段含样本索引、结论与备注 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
