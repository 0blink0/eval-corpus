# Phase 4: 分块指标引擎 - Research

**Researched:** 2026-04-13
**Domain:** 分块质量指标计算与阈值对照（Python CLI）
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-44:** 采用严格口径：每项指标必须定义分子、分母、排除条件。
- **D-45:** 不可判定样本不强行计分，统一记为 `not_applicable`，并单独统计 `applicable_count / total_count`。
- **D-46:** 采用“规则主导 + 固定抽样人工复核”路径。
- **D-47:** 自动评分与人工抽检分开记录；人工抽检仅用于校准和解释，不覆盖自动分原值。
- **D-48:** 每项指标输出三档等级：`pass / warn / fail`。
- **D-49:** 结果中必须同时保留原始分值与阈值信息，避免只有标签不可追溯。
- **D-50:** 单次运行输出单一 JSON 工件，包含三层聚合：`per_file`、`per_tool`、`overall`。
- **D-51:** 单一 JSON 作为 Phase 4 标准接口；CSV/HTML/Markdown 导出延后至 Phase 5。
- **D-52:** 缺失页码、不可判定表格、解析失败等异常样本对相关指标执行“严格标注并剔除计分”。
- **D-53:** 异常样本统一进入 `not_applicable` / `errors` 统计，保证结果可解释、可审计。

### Claude's Discretion
- 七项指标内部模块拆分、函数命名、以及阈值配置文件的物理位置可由实现阶段决定，但不得改变 D-44~D-53 的口径。
- 若人工抽检样本量需要在实现期微调，可在不改变“固定抽样可复现”前提下调整具体数值，并在 README 记录。

### Deferred Ideas (OUT OF SCOPE)
- 指标结果的 CSV/Markdown/HTML 报告导出（Phase 5）
- 批处理与云端扩跑编排（Phase 5）
- LLM-as-judge 并行评分通道（可在后续阶段增量引入）
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| METR-01 | 覆盖完整率 | 提供文本还原计数 + 缺失诊断结构（分子/分母/排除条件） |
| METR-02 | 块长度达标率 | 复用 `ChunkConfig(min=300,max=1000)` 口径并逐块判定 |
| METR-03 | 边界准确率 | 基于句末标点命中率 + 硬切计数双指标 |
| METR-04 | 表格保持率 | 以 `BlockType.table` 与原表格计数做可适用样本对照 |
| METR-05 | 重叠合理率 | 使用相邻文本块重叠比例落区间 10%-20% 判定 |
| METR-06 | 元数据完整率 | 检查 `page/heading_path` 完整或可解释缺失 |
| METR-07 | 语义完整率 | 规则自动评分 + 固定抽样人工复核接口，分开存档 |
</phase_requirements>

## Summary

Phase 4 本质是“口径工程”而不是“算法探索”：核心价值在于把 7 项指标都落实为可复现、可审计、可追溯的数据结构，并严格执行 `not_applicable` 与 `errors` 分流，而不是追求复杂模型。[VERIFIED: `D:/data/.planning/phases/04-metrics/04-CONTEXT.md`]

当前代码库已经具备 Phase 4 的关键前置条件：统一 `Chunk` / `ParsedBlock` 契约、统一 chunk CLI 入口、统一 adapter 错误模型和 `runtime_metadata`。因此最佳实现路径是新增独立 metrics 模块与 CLI 子命令，在不改动现有分块/适配链路的前提下消费标准化输入并产出单一 JSON 工件。[VERIFIED: `D:/data/src/eval_corpus/ir_models.py`; `D:/data/src/eval_corpus/cli.py`; `D:/data/src/eval_corpus/adapter_runner.py`]

**Primary recommendation:** 采用“指标原子函数 + 统一聚合器 + 阈值判级器 + 语义抽检登记器”四层架构，一次运行输出 `per_file/per_tool/overall` 单 JSON，并为每项指标保留 raw value + threshold + level + applicability。

## Project Constraints (from .cursor/rules/)

`.cursor/rules/` 未发现项目规则文件。[VERIFIED: workspace glob `.cursor/rules/**`]

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.8 | 指标计算与 CLI 执行环境 | 项目当前运行时已验证，且满足 `>=3.11` 要求 |
| Pydantic | 2.11.10 | 指标结果 schema、阈值 schema、校验逻辑 | 现有 IR/adapter 已用 Pydantic v2，一致性最高 |
| Typer | 0.20.0 | `metrics` 子命令入口与参数校验 | 现有 CLI 已采用 Typer，扩展成本最低 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 9.0.3 | 指标公式与聚合行为测试 | Phase 4 每项指标都需可重复回归 |
| json (stdlib) | Python stdlib | 单工件输出与持久化 | 直接输出审计友好的结构化结果 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Typer command | 独立脚本入口 | 会破坏现有 `corpus-eval` 一致体验 |
| Pydantic schema | dataclass + 手写校验 | 更轻但会降低输入/输出契约稳定性 |

**Installation:**
```bash
pip install -e ".[dev]"
```

**Version verification:**  
- Python 3.12.8 / Typer 0.20.0 / Pydantic 2.11.10 / pytest 9.0.3 已通过本机导入命令验证。[VERIFIED: shell `python --version` + `import typer,pydantic,pytest`]
- `pyproject.toml` 中最小版本约束为 `typer>=0.9.0`、`pydantic>=2.7.0`、`pytest>=7.0`。[VERIFIED: `D:/data/pyproject.toml`]

## Architecture Patterns

### Recommended Project Structure
```
src/eval_corpus/
├── metrics/
│   ├── models.py          # 指标结果与阈值 schema
│   ├── calculators.py     # METR-01~07 原子计算
│   ├── semantic_review.py # 固定抽样与人工复核登记接口
│   └── aggregate.py       # per_file/per_tool/overall 聚合
├── metrics_io.py          # 读写 metrics JSON
└── cli.py                 # 新增 metrics 子命令
tests/
├── test_metrics_core.py
├── test_metrics_aggregate.py
└── test_metrics_cli.py
```

### Pattern 1: 指标原子函数（One Metric One Function）
**What:** 每个 METR 指标单独函数，统一返回 `MetricResult`（含 numerator/denominator/excluded/raw/threshold/level）。  
**When to use:** 七项指标任一计算、或后续增加指标。  
**Example:** 复用现有“输入先校验再计算”的模式（`ChunkConfig` / `ParsedBlock`）。[VERIFIED: `D:/data/src/eval_corpus/ir_models.py`]

### Pattern 2: 适用性先判定，再计分
**What:** 先计算 `applicable_count/total_count`，再在适用样本上计算 raw score。  
**When to use:** 缺页码、解析失败、不可判定表格等场景。  
**Example:** 复用当前 adapter `errors` 分离结构，避免把错误混入成功样本。[VERIFIED: `D:/data/src/eval_corpus/adapter_runner.py`]

### Pattern 3: CLI 只做编排，指标模块纯函数化
**What:** CLI 解析参数与 I/O；核心计算放在独立模块以便测试。  
**When to use:** 需要回归测试和二次调用（Phase 5 报告层）。  
**Example:** 现有 `chunk` 命令把逻辑委托给 `chunk_blocks`，CLI 只负责参数检查和输出。[VERIFIED: `D:/data/src/eval_corpus/cli.py`; `D:/data/src/eval_corpus/chunker.py`]

### Anti-Patterns to Avoid
- **把不可判定样本当 0 分计入:** 会导致指标系统性偏低且不可解释，违反 D-45/D-52。
- **只输出 pass/warn/fail 不输出 raw value:** 会失去可追溯性，违反 D-49。
- **在 CLI 里堆砌公式逻辑:** 会显著增加测试难度与回归成本。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 输入输出校验 | 手写嵌套 if 校验器 | Pydantic models | 现有项目已统一采用，错误信息一致 |
| CLI 参数解析 | 自写 argv parser | Typer | 现有命令体系已成型 |
| 测试执行框架 | 自写断言脚本 | pytest | 已有测试基础设施与用例风格 |

**Key insight:** Phase 4 风险主要来自“口径漂移”而非“框架不足”，沿用现有栈能把实现风险聚焦在指标定义本身。[VERIFIED: tests 与 src 现状]

## Common Pitfalls

### Pitfall 1: 覆盖完整率分母取错
**What goes wrong:** 用 chunk 字符总数当分母，导致与 golden 文本不可比。  
**Why it happens:** 忽略 Phase 1 的基准统计来源。  
**How to avoid:** 分母固定绑定 golden 原文字符数，分子使用“可还原文本长度”。  
**Warning signs:** 同一语料在不同工具下出现异常高/低且无解释差异。

### Pitfall 2: 边界准确率与硬切比例互相矛盾
**What goes wrong:** 两个指标分母不同导致结论冲突。  
**Why it happens:** 未统一“边界事件”定义。  
**How to avoid:** 统一边界事件集合，并同源计算句末命中率与硬切率。  
**Warning signs:** 边界准确率高但硬切率也高。

### Pitfall 3: 语义完整率不可复现
**What goes wrong:** 人工抽检样本每次不同，结果不可比较。  
**Why it happens:** 未固定采样种子/规则。  
**How to avoid:** 固定采样算法 + 种子 + 样本索引落盘。  
**Warning signs:** 同一输入重复运行抽检样本集合变化。

## Code Examples

### 配置校验模式（用于指标阈值与输入契约）
```python
from pydantic import BaseModel, model_validator

class MetricThreshold(BaseModel):
    warn_min: float
    pass_min: float

    @model_validator(mode="after")
    def validate_order(self):
        if self.warn_min > self.pass_min:
            raise ValueError("warn_min must be <= pass_min")
        return self
```

Source pattern: 项目现有 `ChunkConfig` 的 Pydantic v2 校验写法。[VERIFIED: `D:/data/src/eval_corpus/ir_models.py`]

### CLI 委托模式（用于新增 metrics 命令）
```python
@app.command("metrics")
def metrics(...):
    payload = run_metrics(...)
    write_metrics_json(out_path, payload)
```

Source pattern: 项目现有 `chunk/adapt/stats` 命令结构。[VERIFIED: `D:/data/src/eval_corpus/cli.py`]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 工具各自产出、各自评测 | 统一 IR + 统一 chunk 后统一评测 | Phase 2/3 完成后 | 对比结果可解释、公平 |
| 仅标签化结论 | raw + threshold + level 并存 | Phase 4 决策 D-49 | 可追溯、可审计 |

**Deprecated/outdated:**
- “直接比较不同工具原生分块质量”已不再可接受，会引入口径偏差。[VERIFIED: `D:/data/.planning/PROJECT.md`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | 语义完整率首版可采用“规则自动评分 + 人工抽检登记”且不强依赖 LLM 在线接口 | Summary / Architecture | 若后续要求强制 LLM 自动裁判，需要补充依赖与成本评估 |

## Open Questions (RESOLVED)

1. **METR-07 规则评分细则阈值是否在 Phase 4 锁定？**  
   **RESOLVED:** 在 Phase 4 锁定“最小可行规则集 + 固定抽样最小样本量”，并写入实现常量与 README。  
   - 规则权重：首版采用等权重（便于可解释与复现），后续若调整需通过配置显式声明。  
   - 抽样量：采用固定下限（例如每工具每批次至少 N 个样本）并与随机种子一起落盘。  
   - 人工复核记录仅用于校准与审计，不覆盖自动规则得分原值。

## Environment Availability

Step 2.6: SKIPPED（本阶段为代码/配置内计算与聚合，不新增外部服务依赖；仅需本地 Python 运行时，已可用）。[VERIFIED: phase scope + local runtime check]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pyproject.toml` (`tool.pytest.ini_options`) |
| Quick run command | `pytest tests/test_metrics_core.py -q -x` |
| Full suite command | `pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| METR-01 | 覆盖完整率计算与缺失诊断 | unit | `pytest tests/test_metrics_core.py::test_coverage_completeness -q -x` | ❌ Wave 0 |
| METR-02 | 300-1000 长度达标率 | unit | `pytest tests/test_metrics_core.py::test_length_compliance -q -x` | ❌ Wave 0 |
| METR-03 | 边界准确率与硬切比例 | unit | `pytest tests/test_metrics_core.py::test_boundary_accuracy_and_hardcut -q -x` | ❌ Wave 0 |
| METR-04 | 表格保持率 | unit | `pytest tests/test_metrics_core.py::test_table_retention -q -x` | ❌ Wave 0 |
| METR-05 | 重叠合理率 10-20% | unit | `pytest tests/test_metrics_core.py::test_overlap_compliance -q -x` | ❌ Wave 0 |
| METR-06 | 元数据完整率与可解释缺失 | unit | `pytest tests/test_metrics_core.py::test_metadata_completeness -q -x` | ❌ Wave 0 |
| METR-07 | 规则评分 + 固定抽样复核接口 | integration | `pytest tests/test_metrics_semantic.py -q -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_metrics_core.py -q -x`
- **Per wave merge:** `pytest tests/test_metrics_*.py -q`
- **Phase gate:** `pytest -q`

### Wave 0 Gaps
- [ ] `tests/test_metrics_core.py` — covers METR-01~06
- [ ] `tests/test_metrics_semantic.py` — covers METR-07
- [ ] `tests/test_metrics_cli.py` — covers `metrics` command I/O
- [ ] `tests/fixtures/metrics/` — fixed sampling fixtures

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A（离线本地评测 CLI） |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A（不含服务端多租户接口） |
| V5 Input Validation | yes | Pydantic schema + CLI 参数边界校验 |
| V6 Cryptography | no | N/A（本阶段不实现密码学能力） |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| 路径注入/越权读取 | Information Disclosure | 只接受显式输入路径、限制输出目录、记录 source_file |
| 恶意超大输入导致资源耗尽 | Denial of Service | 分文件处理 + 长度上限 + fail-fast 可选策略 |
| 指标结果被误解为“绝对质量” | Repudiation | 输出 raw + threshold + level + applicable_count |

## Sources

### Primary (HIGH confidence)
- `D:/data/.planning/phases/04-metrics/04-CONTEXT.md` - Phase 4 锁定决策与边界
- `D:/data/.planning/REQUIREMENTS.md` - METR-01~07 需求范围
- `D:/data/.planning/PROJECT.md` - 项目全局约束与统一口径
- `D:/data/src/eval_corpus/ir_models.py` - `ParsedBlock/Chunk/ChunkConfig` 契约
- `D:/data/src/eval_corpus/chunker.py` - 边界切分、重叠策略、表格原子块
- `D:/data/src/eval_corpus/cli.py` - Typer CLI 扩展点
- `D:/data/src/eval_corpus/adapter_runner.py` - `results/errors/runtime_metadata` 聚合模型
- `D:/data/pyproject.toml` - 依赖约束与 pytest 配置
- Shell runtime check (`python --version`; import versions) - 本机依赖可用性

### Secondary (MEDIUM confidence)
- 无（本次研究未依赖外部二级来源）

### Tertiary (LOW confidence)
- 无（仅保留一条显式假设 A1）

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 全部来自仓库与本机运行时验证
- Architecture: HIGH - 与现有代码组织和契约完全对齐
- Pitfalls: MEDIUM - 主要基于指标工程经验，已与当前口径交叉验证

**Research date:** 2026-04-13
**Valid until:** 2026-05-13
