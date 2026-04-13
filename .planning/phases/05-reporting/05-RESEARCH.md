# Phase 5: reporting - Research

**Researched:** 2026-04-13  
**Domain:** Python CLI reporting pipeline (metrics artifact -> multi-format report + synthetic data + batch entrypoints)  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-54:** 优先保证三类核心输出齐备：总对比表、每工具明细、运行元信息附录。
- **D-55:** 机器可读与人读结果并重，但先确保机器可读结构稳定，再生成人读视图。
- **D-56:** 本阶段推荐一次到位支持 `JSON / CSV / Markdown / HTML` 四种导出格式。
- **D-57:** 所有格式共享同一份中间报告数据模型，避免各格式口径漂移。
- **D-58:** 先落地单机可用批跑入口，并预留云端扩跑参数与文档说明。
- **D-59:** 调度复杂度控制在 v1：不引入分布式队列，仅提供可配置并行度与目录批处理。
- **D-60:** 覆盖三类样本：文本型、扫描型、表格型。
- **D-61:** 支持可控规模（样本数量/长度/比例）生成，便于 CI smoke 与回归复现。
- **D-62:** 每次运行使用 `run_id` + 时间戳目录，统一保存报告、明细、日志与中间文件。
- **D-63:** 目录按 tool 与 artifact type 双维组织，保证可追溯与可比对。
- **D-64:** 默认 `continue-on-error`（单文件失败不中止整批），并汇总失败清单。
- **D-65:** 提供失败阈值与重试开关：超过阈值可中止；重试次数可配置。

### Claude's Discretion
- 报告模板样式（表头文案、配色、排序）可由实现阶段决定，但必须保持与 D-54~D-57 一致。
- 合成样本具体文本内容可轻量实现，重点是结构类型覆盖与可复现参数化。

### Deferred Ideas (OUT OF SCOPE)
- 分布式调度/任务队列（如 Celery/Ray）不纳入 Phase 5 v1
- LLM 驱动自动讲解报告（Narrative generation）不纳入 Phase 5 v1
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RPT-01 | 生成总对比表（三工具 x 七指标，含阈值） | 统一中间数据模型 + 四格式导出器（JSON/CSV/MD/HTML） |
| RPT-02 | 生成每工具明细（原始指标 JSON/CSV + Markdown/HTML 摘要） | 按 `per_tool`/`per_file` 分层渲染，保留 `raw_value/threshold/level` |
| RPT-03 | 写入运行元信息（时间、工具版本、git commit） | 复用 `runtime_metadata`，补齐 run-level provenance 字段 |
| DATA-01 | 生成可用于 smoke/回归的合成或小样本数据 | 三类样本生成器（文本/扫描/表格）+ 固定随机种子 |
| DATA-02 | 支持目录递归批处理，便于云端扩跑 | 单机批跑入口 + 并行度参数 + 失败阈值/重试策略 |
</phase_requirements>

## Project Constraints (from .cursor/rules/)

- 未发现 `.cursor/rules/` 目录，因此无额外项目规则覆盖当前 phase。[VERIFIED: codebase glob]

## Summary

Phase 5 最关键的规划点是把 Phase 4 已稳定的三层指标工件（`per_file / per_tool / overall`）作为唯一上游，构建一个“单一报告中间模型 + 多格式导出器”的薄层，不在报告阶段重算指标。[VERIFIED: `src/eval_corpus/metrics_io.py`, `src/eval_corpus/metrics/aggregate.py`, `05-CONTEXT.md`]

现有代码已经具备 CLI 子命令扩展模式（Typer）、结构化模型边界（Pydantic）以及 continue-on-error 执行基线（adapter runner）。因此 Phase 5 规划应优先拆成三个实现面：报告渲染、合成数据生成、批跑编排；并在同一 run 目录落盘全部产物，确保可追溯与可复盘。[VERIFIED: `src/eval_corpus/cli.py`, `src/eval_corpus/adapter_runner.py`, `05-CONTEXT.md`]

测试基础设施已就绪（pytest 可用且配置完成），可以直接为 RPT/DATA 要求添加 unit + CLI contract tests，并将“报告跨格式一致性”设为 Wave gate。[VERIFIED: `pyproject.toml`, `tests/test_metrics_cli.py`, local `pytest --version`]

**Primary recommendation:** 以 `metrics artifact -> report model -> {json,csv,md,html}` 的单向流水线为核心，再并列实现 `synthetic-data` 与 `batch-run` 子命令，全部复用现有 Typer/Pydantic 契约。[VERIFIED: codebase]

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.8 | 运行时与脚本入口 | 本机已安装并可直接执行 CLI 与测试。[VERIFIED: local `python --version`] |
| typer | 0.20.0 | 命令行子命令与参数定义 | 项目当前 CLI 已全面采用 Typer，Phase 5 继续扩展最小迁移成本。[VERIFIED: `src/eval_corpus/cli.py`, local metadata] |
| pydantic | 2.11.10 | 报告中间模型/数据校验 | 现有 IR 与指标模型均基于 Pydantic v2，适合新增 report schema。[VERIFIED: `src/eval_corpus/ir_models.py`, `src/eval_corpus/metrics/models.py`, local metadata] |
| pytest | 9.0.3 | 测试框架 | 项目已配置 pytest testpaths，且现有 CLI/聚合测试风格可复用。[VERIFIED: `pyproject.toml`, `tests/test_metrics_aggregate.py`, local `pytest --version`] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| json/csv/html (stdlib) | Python 3.12 stdlib | 机器可读与基础人读导出 | JSON/CSV/HTML table 可先用标准库实现，减少新增依赖。[VERIFIED: Python stdlib availability] |
| pathlib | Python 3.12 stdlib | `run_id` 目录组织与产物落盘 | 批跑目录递归与 artifact 布局统一使用 Path API。[VERIFIED: codebase usage] |
| random | Python 3.12 stdlib | 可复现合成数据 | DATA-01 通过固定 seed 生成稳定样本。[ASSUMED] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib HTML string builder | Jinja2 模板引擎 | Jinja2 可提升模板可读性，但会引入新依赖与测试面。[ASSUMED] |
| 逐行 CSV 手写映射 | pandas DataFrame | pandas 在复杂透视表更快，但 Phase 5 需求可由 stdlib 满足且更轻量。[ASSUMED] |

**Installation:**
```bash
python -m pip install -e ".[dev]"
```

**Version verification:** 核心版本以“本机已安装且项目正在使用”作为计划基线：Python 3.12.8、typer 0.20.0、pydantic 2.11.10、pytest 9.0.3。[VERIFIED: local runtime + metadata]

## Architecture Patterns

### Recommended Project Structure
```text
src/eval_corpus/
├── reporting/               # report model + exporters (json/csv/md/html)
├── synthetic_data/          # DATA-01 generator (text/scan/table)
├── batch/                   # DATA-02 batch orchestration + retry policy
└── cli.py                   # register report/synthetic/batch subcommands
```

### Pattern 1: Single Intermediate Report Model
**What:** 先将 `per_file/per_tool/overall` 映射到统一 `ReportPayload`，再由格式导出器消费。  
**When to use:** 任何新增导出格式（避免口径漂移）。  
**Example:**
```python
# Source: src/eval_corpus/metrics_io.py
payload = {
    "per_file": per_file,
    "per_tool": per_tool,
    "overall": overall,
}
```

### Pattern 2: CLI Contract + Explicit Exit Codes
**What:** 延续 Typer 子命令风格与参数校验，输入错误返回 exit code 2。  
**When to use:** report/synthetic/batch 三个新入口。  
**Example:**
```python
# Source: src/eval_corpus/cli.py
if not input_path.is_file():
    typer.secho(f"Input file not found: {input_path}", err=True)
    raise typer.Exit(2)
```

### Pattern 3: Continue-on-Error Batch Baseline
**What:** 默认收集错误并继续处理，必要时由阈值触发中止。  
**When to use:** DATA-02 目录递归批跑。  
**Example:**
```python
# Source: src/eval_corpus/adapter_runner.py
except AdapterError as e:
    errors.append(err)
    if fail_fast:
        break
```

### Anti-Patterns to Avoid
- **报告层重算指标:** 会与 Phase 4 聚合逻辑分叉，造成同一 run 多口径。[VERIFIED: `05-CONTEXT.md`]
- **每格式各自拼数据:** 容易让 CSV/HTML/MD 字段不一致，应统一先建中间模型。[VERIFIED: D-57]
- **批跑默认 fail-fast:** 与 D-64 冲突，且会降低批量诊断价值。[VERIFIED: `05-CONTEXT.md`, `adapter_runner.py`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI 参数解析 | 自写 argparse 分发层 | Typer 现有 app 子命令模式 | 现有 CLI 与测试均围绕 Typer，扩展一致性最高。[VERIFIED: `src/eval_corpus/cli.py`] |
| 数据校验 | 手写 dict 校验器 | Pydantic model + TypeAdapter | 当前 IR/metrics 都用 Pydantic，错误信息结构化且可复用。[VERIFIED: `ir_models.py`, `metrics/models.py`, `metrics_io.py`] |
| 批跑错误统计 | 各处 try/except 散落计数 | 统一 error envelope + 汇总 | 现有 runner 已有 results/errors 契约，适配最小。[VERIFIED: `adapter_runner.py`] |

**Key insight:** Phase 5 本质是“编排与呈现层”而非“算法层”；复用 Phase 4 工件与现有 CLI/模型约束，才能保证报告可信与实现可控。[VERIFIED: context + codebase]

## Common Pitfalls

### Pitfall 1: Cross-format Drift
**What goes wrong:** JSON 与 Markdown/HTML 中指标字段或排序不一致。  
**Why it happens:** 每种格式单独从原始 payload 拼接。  
**How to avoid:** 先生成 canonical report model，再做 format adapter。  
**Warning signs:** 同一 run 下四种导出在 `METR-*` 计数或 level 上出现差异。

### Pitfall 2: Runtime Metadata Loss
**What goes wrong:** 报告缺少 tool version / generated_at / git commit。  
**Why it happens:** 只保留 `metrics_summary`，忽略 runtime 元字段。  
**How to avoid:** 将 `overall.runtime_metadata` 原样透传到最终报告附录。  
**Warning signs:** 无法回答“这份报告由哪个版本工具生成”。

### Pitfall 3: Batch Retry Without Determinism
**What goes wrong:** 重试后结果不可复现，难定位回归。  
**Why it happens:** 合成数据未固定 seed 或 run_id。  
**How to avoid:** DATA-01 生成器强制支持 seed，run 目录包含 seed 与参数快照。  
**Warning signs:** 同参数重复运行结果差异明显。[ASSUMED]

## Code Examples

Verified patterns from current codebase:

### 三层指标工件约束
```python
# Source: src/eval_corpus/metrics_io.py
required = {"per_file", "per_tool", "overall"}
if set(payload.keys()) != required:
    raise ValueError("metrics payload must contain per_file/per_tool/overall")
```

### 汇总层自动补齐运行统计
```python
# Source: src/eval_corpus/metrics/aggregate.py
merged_runtime = {
    **(runtime_metadata or {}),
    "tool_count": len(per_tool),
    "file_count": len(per_file),
    "error_count": sum(r["errors"] for r in per_file),
}
```

### CLI 合同测试风格
```python
# Source: tests/test_metrics_cli.py
result = runner.invoke(app, ["metrics", "--input", str(input_path), "--out", str(out_path)])
assert result.exit_code == 0
assert set(payload.keys()) == {"per_file", "per_tool", "overall"}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 多阶段各自产出字段 | Phase 4 统一 JSON 三层接口 | 已在 Phase 4 完成 | Phase 5 可专注导出层与批跑层。[VERIFIED: `STATE.md`, `04/05 context`] |
| 指标层 + 报告层混合 | 指标先收敛，报告后置 | 当前阶段规划 | 降低回归风险，便于验收 RPT-01/02/03。[VERIFIED: roadmap/context] |

**Deprecated/outdated:**
- 在报告阶段重新推导七项指标：与当前阶段边界冲突，应避免。[VERIFIED: `05-CONTEXT.md`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `random` + 固定 seed 足以满足 DATA-01 可复现需求 | Standard Stack / Pitfalls | 若样本构造含外部依赖，可能需要更严格伪随机策略 |
| A2 | Phase 5 无需引入 pandas/Jinja2 即可满足四格式导出 | Alternatives Considered | 若 HTML/表格复杂度升高，开发效率可能下降 |

## Open Questions

1. **RPT-01 总对比表的列排序是否固定为 METR-01..07？**
   - What we know: 七项指标集合已固定，且需跨格式一致。
   - What's unclear: 是否有业务优先顺序（例如先覆盖类再语义类）。
   - Recommendation: 在 PLAN 中锁定一份 canonical sort order 并写入测试。

2. **RPT-03 的 git commit 在“非 git 环境/脏工作区”如何展示？**
   - What we know: 需求要求可追溯元信息。
   - What's unclear: 提交哈希取不到时的降级字段规范。
   - Recommendation: 约定 `git_commit: null` + `git_status: dirty|clean|unavailable`。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | 全部 Phase 5 功能 | ✓ | 3.12.8 | — |
| pip | 安装/锁定依赖 | ✓ | 26.0.1 | — |
| pytest | Validation Architecture | ✓ | 9.0.3 | — |
| typer | CLI 子命令扩展 | ✓ | 0.20.0 | 若缺失则无法运行 CLI（需安装） |
| pydantic | report schema 校验 | ✓ | 2.11.10 | 若缺失则无法执行模型校验（需安装） |

**Missing dependencies with no fallback:**
- None.

**Missing dependencies with fallback:**
- None.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `pytest tests/test_metrics_cli.py -q` |
| Full suite command | `pytest -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RPT-01 | 三工具 x 七指标总表 + 阈值列 | unit + CLI contract | `pytest tests/test_reporting_summary.py -q` | ❌ Wave 0 |
| RPT-02 | 每工具明细导出 JSON/CSV + MD/HTML | unit | `pytest tests/test_reporting_detail.py -q` | ❌ Wave 0 |
| RPT-03 | 报告包含运行元信息与版本追溯 | unit | `pytest tests/test_reporting_metadata.py -q` | ❌ Wave 0 |
| DATA-01 | 合成数据三类型 + 参数化 + 可复现 | unit | `pytest tests/test_synthetic_data.py -q` | ❌ Wave 0 |
| DATA-02 | 目录递归批跑 + continue-on-error + 重试阈值 | integration-lite | `pytest tests/test_batch_runner.py -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_reporting_summary.py -q` (或对应变更最小测试子集)
- **Per wave merge:** `pytest tests/test_metrics_aggregate.py tests/test_metrics_cli.py -q`
- **Phase gate:** `pytest -q`

### Wave 0 Gaps
- [ ] `tests/test_reporting_summary.py` — 覆盖 RPT-01
- [ ] `tests/test_reporting_detail.py` — 覆盖 RPT-02
- [ ] `tests/test_reporting_metadata.py` — 覆盖 RPT-03
- [ ] `tests/test_synthetic_data.py` — 覆盖 DATA-01
- [ ] `tests/test_batch_runner.py` — 覆盖 DATA-02

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | 本 phase 为本地 CLI/离线批处理，无鉴权边界。[VERIFIED: architecture scope] |
| V3 Session Management | no | 同上，无会话状态。[VERIFIED: architecture scope] |
| V4 Access Control | yes | 输出目录白名单 + Path 归一化，避免越权写入。[ASSUMED] |
| V5 Input Validation | yes | Typer 参数校验 + Pydantic 模型校验。[VERIFIED: `cli.py`, `ir_models.py`, `metrics/models.py`] |
| V6 Cryptography | no | 不引入自定义加密；若未来需签名应使用标准库/成熟库。[ASSUMED] |

### Known Threat Patterns for Python CLI reporting stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| 路径穿越写文件 (`../`) | Tampering | `Path.resolve()` 后校验输出根；拒绝越界路径。[ASSUMED] |
| 恶意超大输入导致资源耗尽 | DoS | 批跑并发上限、文件大小阈值、失败阈值中止。[VERIFIED: D-59, D-65] |
| HTML 报告注入未转义文本 | Tampering/XSS | HTML 导出统一 escape 用户内容。[ASSUMED] |

## Sources

### Primary (HIGH confidence)
- `src/eval_corpus/cli.py` - CLI 子命令模式、exit code 约定、metrics 命令契约
- `src/eval_corpus/metrics_io.py` - 三层工件边界与 payload 校验
- `src/eval_corpus/metrics/aggregate.py` - overall/per_tool/per_file 聚合与 runtime_metadata 合并
- `src/eval_corpus/adapter_runner.py` - continue-on-error/fail-fast 运行语义
- `src/eval_corpus/ir_models.py`, `src/eval_corpus/metrics/models.py` - Pydantic 约束模型
- `tests/test_metrics_cli.py`, `tests/test_metrics_aggregate.py` - 既有测试合同
- `pyproject.toml` - 依赖下限与 pytest 配置
- `.planning/phases/05-reporting/05-CONTEXT.md` - Phase 5 锁定决策与边界
- `.planning/config.json` - `workflow.nyquist_validation=true`
- Local environment probes: `python --version`, `python -m pip --version`, `pytest --version`, `importlib.metadata`

### Secondary (MEDIUM confidence)
- None.

### Tertiary (LOW confidence)
- None (所有未验证结论已标记 `[ASSUMED]`)。

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 由仓库依赖声明与本机实际版本双重验证。
- Architecture: HIGH - 由现有 CLI/metrics 边界与 Phase 5 决策直接约束。
- Pitfalls: MEDIUM - 部分风险（如 HTML escape、路径穿越）为业界通用实践，当前仓库尚未实现需后续验证。

**Research date:** 2026-04-13  
**Valid until:** 2026-05-13
