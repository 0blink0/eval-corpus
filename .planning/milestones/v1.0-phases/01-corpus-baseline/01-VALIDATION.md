---
phase: 1
slug: corpus-baseline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-13
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pyproject.toml` — `[tool.pytest.ini_options]`（由 Wave 0 / Plan 01-01 写入） |
| **Quick run command** | `pytest -q tests/` |
| **Full suite command** | `pytest tests/` |
| **Estimated runtime** | ~5–30 seconds（随夹具规模） |

---

## Sampling Rate

- **After every task commit:** `pytest -q tests/`
- **After every plan wave:** `pytest tests/`
- **Before `/gsd-verify-work`:** Full suite green
- **Max feedback latency:** 60 seconds（目标）

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-T1 | 01 | 1 | CORP-01 | T-01-01 | 不在仓库硬编码语料路径 | unit | `pytest -q tests/test_config.py` | ❌ W0 | ⬜ pending |
| 01-01-T2 | 01 | 1 | CORP-01 | T-01-02 | 缺失路径非零退出、stderr 提示 | unit | `pytest -q tests/test_config.py` | ❌ W0 | ⬜ pending |
| 01-02-T1 | 02 | 2 | CORP-02 | — | 不跟随 symlink | unit | `pytest -q tests/test_scan.py` | ❌ W0 | ⬜ pending |
| 01-02-T2 | 02 | 2 | CORP-02 | — | JSON 含 `schema_version` | unit | `pytest -q tests/test_manifest.py` | ❌ W0 | ⬜ pending |
| 01-03-T1 | 03 | 3 | CORP-03 | — | `needs_ocr` 与页数字段可测 | unit | `pytest -q tests/test_stats.py` | ❌ W0 | ⬜ pending |
| 01-03-T2 | 03 | 3 | CORP-03 | — | 黄金统计 JSON 结构 | unit | `pytest -q tests/test_stats.py` | ❌ W0 | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` — `tmp_path` 夹具、样例二进制/文本生成辅助
- [ ] `tests/test_config.py` — CORP-01 路径解析与失败路径
- [ ] `tests/test_scan.py` — 扩展名过滤、忽略 `~$`、symlink 不跟随
- [ ] `tests/test_manifest.py` — 清单 JSON 字段
- [ ] `tests/test_stats.py` — PDF/文本统计与 `needs_ocr`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 北燃真实目录跑一次 | CORP-01–03 | 语料可能不在 CI、涉密不出库 | 本地设置 `EVAL_CORPUS_ROOT`，运行 `corpus-eval manifest` / `stats`，目检 stderr 摘要与 JSON |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity maintained
- [ ] `nyquist_compliant: true` set in frontmatter when Wave 0 green

**Approval:** pending
