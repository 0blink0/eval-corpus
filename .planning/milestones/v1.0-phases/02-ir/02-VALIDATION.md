---
phase: 2
slug: ir
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-13
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `pytest -q tests/test_chunker_core.py -x` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~10-30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest -q tests/test_chunker_core.py -x`
- **After every plan wave:** Run `pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | CHUNK-01 | T-02-01 | 仅接受合法 `ParsedBlock` 结构，非法输入显式报错 | unit | `pytest -q tests/test_chunker_core.py::test_parsed_block_schema -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | CHUNK-02 | T-02-02 | table 不被拆分、重叠仅文本块、长度限制可复现 | unit | `pytest -q tests/test_chunker_core.py::test_chunking_rules -x` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 3 | CHUNK-03 | T-02-03 | 同一分块器对统一输入稳定输出 | integration | `pytest -q tests/test_chunker_cli.py::test_chunk_command_roundtrip -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_chunker_core.py` — CHUNK-01 / CHUNK-02 骨架
- [ ] `tests/test_chunker_cli.py` — CHUNK-03 骨架
- [ ] `src/eval_corpus/ir_models.py` — Pydantic 模型
- [ ] `src/eval_corpus/chunker.py` — 纯函数分块核心

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 真实复杂语料分块人工 spot-check | CHUNK-02/03 | 自动化难覆盖全部文档结构边角 | 在本地选 2-3 个复杂样本运行 `corpus-eval chunk`，抽查 table 原子与 heading/page 元数据 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
