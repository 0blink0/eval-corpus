---
phase: 3
slug: adapters
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-13
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `pytest -q tests/test_adapters_contract.py -x` |
| **Full suite command** | `pytest -q` |
| **Estimated runtime** | ~20-60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest -q tests/test_adapters_contract.py -x`
- **After every plan wave:** Run `pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | ADPT-01 | T-03-01 | Paddle adapter 将成功/失败统一映射为标准结构 | unit/integration | `pytest -q tests/test_adapters_paddle.py -x` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | ADPT-02 | T-03-02 | GLM adapter 在鉴权/网络失败时仍给出可定位 stage 错误 | unit/integration | `pytest -q tests/test_adapters_glm.py -x` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 3 | ADPT-03 | T-03-03 | MinerU adapter 输出可归一到 ParsedBlock[] 或标准化错误 | unit/integration | `pytest -q tests/test_adapters_mineru.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/adapters/` 三件套（文本 PDF / 扫描 PDF / 表格样例）
- [ ] `tests/test_adapters_contract.py` — 统一接口、错误模型、continue-on-error/fail-fast
- [ ] `tests/test_adapters_paddle.py`
- [ ] `tests/test_adapters_glm.py`
- [ ] `tests/test_adapters_mineru.py`
- [ ] `src/eval_corpus/adapters/` 目录与基础协议/注册

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GLM 真实在线调用 | ADPT-02 | 依赖真实 API key 与网络环境 | 设置 `GLM_API_KEY` 后运行 adapter 命令，确认成功与失败路径日志 |
| 三工具同批样例对齐检查 | ADPT-01/02/03 | 自动化难覆盖所有文档形态差异 | 对最小三件套样例执行三工具，人工抽查 block type/page/heading_path 是否语义一致 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
