---
phase: 05
slug: reporting
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-13
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` |
| **Quick run command** | `pytest tests/test_reporting_summary.py -q -x` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~45-90 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_reporting_summary.py -q -x`（或对应最小子集）
- **After every plan wave:** Run `pytest tests/test_reporting_*.py tests/test_batch_runner.py tests/test_synthetic_data.py -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | RPT-01 | T-05-01 | 总表按 METR-01..07 固定顺序，阈值与等级一致 | unit | `pytest tests/test_reporting_summary.py -q -x` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | RPT-02, RPT-03 | T-05-02 | 多格式明细一致且元信息完整 | integration-lite | `pytest tests/test_reporting_detail.py tests/test_reporting_metadata.py -q -x` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 1 | DATA-01 | T-05-03 | 三类合成样本可复现（seed 固定） | unit | `pytest tests/test_synthetic_data.py -q -x` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 1 | DATA-02 | T-05-04 | 批跑支持 continue-on-error/阈值中止/重试 | integration-lite | `pytest tests/test_batch_runner.py -q -x` | ❌ W0 | ⬜ pending |
| 05-03-01 | 03 | 2 | RPT-01, RPT-02 | T-05-05 | CLI 导出 JSON/CSV/MD/HTML 并保持同源数据 | integration | `pytest tests/test_reporting_cli.py::test_multi_format_exports -q -x` | ❌ W0 | ⬜ pending |
| 05-03-02 | 03 | 2 | RPT-03 | T-05-06 | git unavailable/dirty 时元信息按降级规范输出 | integration | `pytest tests/test_reporting_cli.py::test_git_metadata_fallback -q -x` | ❌ W0 | ⬜ pending |
| 05-03-03 | 03 | 2 | DATA-02 | T-05-07 | run_id + timestamp 目录布局与 runbook 一致 | integration | `pytest tests/test_reporting_cli.py::test_run_layout_and_batch_entry -q -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_reporting_summary.py` — RPT-01
- [ ] `tests/test_reporting_detail.py` — RPT-02
- [ ] `tests/test_reporting_metadata.py` — RPT-03
- [ ] `tests/test_synthetic_data.py` — DATA-01
- [ ] `tests/test_batch_runner.py` — DATA-02
- [ ] `tests/test_reporting_cli.py` — 导出/降级/目录布局契约

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| HTML 报告可读性与样式可用性 | RPT-02 | 人类可读体验需人工确认 | 运行导出后打开 `report.html`，检查表格渲染、列顺序、级别标记和元信息段 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 90s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
