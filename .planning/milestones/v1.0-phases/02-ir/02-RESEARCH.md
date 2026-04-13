# Phase 2: 统一 IR 与分块器 - Research

**Researched:** 2026-04-13  
**Domain:** Python 文档统一中间表示（IR）与分块策略实现  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### 用户选择：四个讨论领域初始采用会话内「第一项推荐」；**D-16 后改为 Pydantic**（见 specifics）

### ParsedBlock 建模与序列化（领域 1）

- **D-16:** `ParsedBlock` 与 Phase 2 输出的 **chunk** 模型以 **Pydantic v2 `BaseModel`** 为主；JSON 交换使用 **`TypeAdapter` / `model_validate_json` / `model_dump_json`**（或 `model_dump` + `json.dumps`，`ensure_ascii=False` 与 Phase 1 一致）；在 `pyproject.toml` 中将 **`pydantic>=2`** 列为**运行时依赖**。
- **D-17:** 对外交换格式为 **JSON**；字段名 **snake_case**，与现有 `eval_corpus` / 清单风格一致。
- **D-18:** `type ∈ {title, paragraph, table, other}`（与 PROJECT 一致）；`table` 块 **必须** 提供规范化 **`text`**（表格的线性化/可读文本）；可选扩展字段 **`cells`**（或等价嵌套结构）供后续表格保持率细化，**Phase 2 不强制**解析工具填充 `cells`。
- **D-19:** `parser_tool` 在 Phase 2 允许占位；默认值为 **`"unknown"`**（字符串），Phase 3 适配器写入真实工具名与版本标识。

### 重叠率定义（领域 2）

- **D-20:** 重叠仅应用于 **非 `table`** 的最终文本 chunk（**table 块 0 重叠**）。**title 与紧随其后的正文**若在分块器中合并为同一文本 chunk，该块仍视为文本块，**参与**重叠逻辑。
- **D-21:** 重叠字符数按 **后一块（当前块）Unicode 字符长度**计算：`overlap_chars = ceil(overlap_ratio * len(current_chunk_text))`，`overlap_ratio` 默认 **0.15**，允许配置在 **[0.10, 0.20]**。
- **D-22:** 重叠通过**相邻块间复制**实现：将**前一块尾部** `overlap_chars` 个字符（**按 Unicode 标量/ Python `str` 字符**计数）作为**当前块前缀**（或对称地后缀+前缀组合，实现须在 README 固定一种并写测）；**禁止**在 BMP/代理对上断裂（使用字符索引而非 UTF-16 码元）。
- **D-23:** 若前块长度小于所需重叠，**按实际可取长度**缩短重叠（不抛错），并在元数据或统计钩子中可标记 `overlap_truncated`（可选，供 Phase 4）。

### heading_path 与 page（领域 3）

- **D-24:** `heading_path` 在模型中为 **`list[str]`**（从根到叶的标题链）；JSON 中序列化为 **JSON 数组**；人类可读调试格式可用 `" / "` 拼接，但**规范交换格式为数组**。
- **D-25:** `page` **可空**（`null` / `None`）：未知页码时**显式 `null`**，不用 `0` 冒充。
- **D-26:** chunk 级 **`page`**：默认取该 chunk **主文本来源的页码**；若跨页合并，取 **最小页码** 作为主 `page`；若需保留跨度，可增加可选字段 **`page_span: [int, int]`**（闭区间或 `[min,max]`），**非 Phase 2 必交付**，有则写入、无则仅 `page`。

### 分块器对外接口（领域 4）

- **D-27:** 分块核心实现为 **纯 Python API**（函数或类），输入 **`list[ParsedBlock]`**（可由 JSON 校验得到）与配置，输出 **`list[Chunk]`**（Pydantic 模型）；序列化遵循 D-16。
- **D-28:** 提供 Typer 子命令 **`chunk`**（挂在现有 `corpus-eval` 上）：例如 **`--blocks-in PATH`** 读入 `ParsedBlock[]` JSON，**`--chunks-out PATH`** 写出 chunk JSON；配置项 **`--min-chars` / `--max-chars` / `--overlap-ratio`**（默认值对齐 PROJECT：300、1000、0.15），范围校验与 CONTEXT 一致。
- **D-29:** 单元测试以 **手工构造的 `ParsedBlock[]` 夹具**为主（ROADMAP 成功标准 1–2），不依赖真实 OCR 输出。

### Claude's Discretion

- `chunk_id` 生成策略（UUID / 确定性哈希）、`source_file` 与 Phase 1 路径字符串的对应方式、句界标点白名单的具体集合，由实现与 README 固定即可。
- `page_span` 是否在 Phase 2 落地：若工期紧可仅文档化字段预留，**必须**保证 `page` 与 `heading_path` 行为满足 D-24–D-26。

### Deferred Ideas (OUT OF SCOPE)

- 独立分包 / 实时流式分块：未纳入 Phase 2。
- 三工具具体映射规则：属 Phase 3。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CHUNK-01 | 定义并实现统一中间表示 `ParsedBlock`（类型、文本/表格序列化、页码、标题路径） | 用 Pydantic v2 `BaseModel` 建模 + `TypeAdapter(list[ParsedBlock])` 入站校验；`heading_path: list[str]`、`page: int \\| None`、`table.text` 强制必填 [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`] [CITED: https://docs.pydantic.dev/latest/concepts/models/] [CITED: https://docs.pydantic.dev/latest/concepts/type_adapter/] |
| CHUNK-02 | 实现统一分块器（300–1000、表格原子、句界优先、10–20% 重叠默认 15%） | 采用“两阶段分块”：先结构分段（table 原子），再文本句界切分与 hard-cut 回退；重叠按 `ceil(ratio * len(current_chunk))`，仅文本 chunk 生效 [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`] [CITED: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str] |
| CHUNK-03 | 同一分块器对三套工具归一后的 `ParsedBlock[]` 执行，保证对比公平 | 分块器入口仅接受统一 `ParsedBlock[]`，禁止读取工具私有字段；`parser_tool` 在 Phase 2 固定可占位 `"unknown"` [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`] |
</phase_requirements>

## Project Constraints (from .cursor/rules/)

- 未发现 `.cursor/rules/` 目录，当前无额外仓库级硬约束文件可继承 [VERIFIED: glob `.cursor/rules/**/*.md` returned 0 files]。

## Summary

Phase 2 已有清晰的“锁定决策”边界：核心不是探索框架，而是把 `ParsedBlock -> Chunk` 的统一契约严格落地，并确保后续 Phase 3/4 能直接复用该契约 [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`].  
当前仓库已具备可复用模式：Typer CLI 入口、`schema_version` 字段习惯、`ensure_ascii=False` 的 JSON 输出与 pytest 基础设施均已存在，因此本阶段主要是“在既有骨架上新增 IR 与 chunk 模块”，不是重构 CLI 基座 [VERIFIED: `src/eval_corpus/cli.py`, `src/eval_corpus/manifest.py`, `src/eval_corpus/stats.py`, `pyproject.toml`].

规划上最关键的是先固定可验证行为：长度约束、重叠算法、table 原子块、元数据完整性与边界回退策略。若这些在 Phase 2 未被测试钉死，Phase 3 接入多工具后会放大歧义并削弱公平对比 [ASSUMED].

**Primary recommendation:** 以“Pydantic 模型 + 纯函数分块核心 + Typer 薄适配 + 手工夹具测试”作为唯一实现路径，并在 Wave 0 先补齐 CHUNK-01~03 的测试骨架 [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`] [VERIFIED: `tests/` exists].

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.8 (env) | 运行分块核心与 CLI | 项目要求 `>=3.11`，当前环境满足 [VERIFIED: `python --version`, `pyproject.toml`] |
| pydantic | `>=2.7.0` (declared), 2.11.10 (env) | `ParsedBlock`/`Chunk` 校验、序列化、JSON schema | D-16 明确锁定；`BaseModel`/`model_validate_json`/`model_dump_json` 为官方能力 [VERIFIED: `pyproject.toml`, `.planning/phases/02-ir/02-CONTEXT.md`] [CITED: https://docs.pydantic.dev/latest/concepts/models/] |
| typer | `>=0.9.0` (declared), 0.20.0 (env) | 暴露 `corpus-eval chunk` 命令 | 当前 CLI 已全面使用 Typer，增量扩展成本最低 [VERIFIED: `pyproject.toml`, `src/eval_corpus/cli.py`] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | `>=7.0` (declared), 9.0.3 (env) | 行为验证（长度/重叠/table 原子/元数据） | 用手工 `ParsedBlock[]` 夹具做单元+CLI 烟测 [VERIFIED: `pyproject.toml`, `tests/test_stats.py`, `pytest --version`] |
| json (stdlib) | Python stdlib | 输出 UTF-8 JSON | 与 Phase 1 一致：`ensure_ascii=False` [VERIFIED: `src/eval_corpus/manifest.py`, `src/eval_corpus/stats.py`] |
| math (stdlib) | Python stdlib | `ceil` 计算重叠字符数 | 实现 D-21 公式 [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pydantic v2 models | `dataclass` + 手写校验 | 与 D-16 冲突，且 JSON 入站校验/错误报告一致性较差 [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`] |
| Typer 子命令 | 独立脚本入口 | 增加维护面，违背现有 `corpus-eval` 单入口习惯 [VERIFIED: `src/eval_corpus/cli.py`] |

**Installation:**
```bash
pip install -e ".[dev]"
```

**Version verification:** 已通过本地环境确认 Python/pytest/pydantic/typer 版本；Phase 2 规划不依赖 npm 包 [VERIFIED: shell commands on 2026-04-13].

## Architecture Patterns

### Recommended Project Structure
```text
src/eval_corpus/
├── ir_models.py        # ParsedBlock / Chunk / ChunkConfig (Pydantic)
├── chunker.py          # 纯 Python 分块核心（结构优先 + 句界 + 重叠）
├── chunk_io.py         # JSON 读写与 TypeAdapter 校验封装
└── cli.py              # 新增 chunk 子命令（薄封装）
tests/
├── test_chunker_core.py
└── test_chunker_cli.py
```
[ASSUMED]

### Pattern 1: Typed IR Boundary
**What:** 以 `ParsedBlock` 作为唯一输入边界，所有分块逻辑只消费该结构，不读取工具特定字段。  
**When to use:** 需要公平对比多解析工具输出时。  
**Example:**
```python
from pydantic import BaseModel, TypeAdapter

class ParsedBlock(BaseModel):
    type: str
    text: str
    page: int | None = None
    heading_path: list[str] = []
    parser_tool: str = "unknown"

blocks = TypeAdapter(list[ParsedBlock]).validate_python(raw_blocks)
```
Source: [CITED: https://docs.pydantic.dev/latest/concepts/models/] [CITED: https://docs.pydantic.dev/latest/concepts/type_adapter/]

### Pattern 2: Two-Pass Chunking
**What:** 先做结构切分（table 原子保留），再对文本序列做句界优先切分，不满足长度时 hard-cut。  
**When to use:** 目标块长有硬边界，同时要尽量语义完整。  
**Example:**
```python
def chunk_blocks(blocks, cfg):
    # pass-1: structural segmentation (table atomic)
    segments = structural_partition(blocks)
    # pass-2: sentence-first sizing with fallback hard cut
    text_chunks = size_by_sentence(segments, cfg.min_chars, cfg.max_chars)
    return apply_overlap(text_chunks, ratio=cfg.overlap_ratio)
```
Source: [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`] [ASSUMED]

### Anti-Patterns to Avoid
- **按字符流直接切全部块：** 会撕裂 table，违背 D-20 与成功标准 2 [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`]。
- **在 UTF-16 码元层计算重叠：** 可能破坏 Unicode 字符边界；应基于 Python `str` 字符索引 [CITED: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str] [VERIFIED: D-22]。
- **CLI 中实现业务算法：** 降低可测试性，应保持 CLI 薄封装 [VERIFIED: `src/eval_corpus/cli.py`] [ASSUMED]。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON 数组到模型列表校验 | 手写字段循环校验器 | `TypeAdapter(list[ParsedBlock])` | 官方提供一致错误模型与序列化能力 [CITED: https://docs.pydantic.dev/latest/concepts/type_adapter/] |
| 模型 JSON 转换协议 | 自定义 `to_dict/from_dict` 体系 | `model_validate_json` / `model_dump_json` | 降低协议漂移与维护成本 [CITED: https://docs.pydantic.dev/latest/concepts/models/] |
| CLI 参数解析 | `argparse` 重写一套 | Typer command/Option | 项目已有成熟模式 [VERIFIED: `src/eval_corpus/cli.py`] |

**Key insight:** 本阶段复杂度主要在“边界定义一致性”，不是算法炫技；越靠近官方/现有模式，越能保证 Phase 3/4 对齐成本可控 [ASSUMED].

## Common Pitfalls

### Pitfall 1: 重叠比例按前块算导致统计偏移
**What goes wrong:** 相邻块重叠比例在评测时偏离 10–20%。  
**Why it happens:** 误把公式写成 `len(prev_chunk)` 基数。  
**How to avoid:** 固定实现 D-21：按当前块长度计算并 `ceil`。  
**Warning signs:** 同一输入在块大小变化后重叠比例波动异常。  
[VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`]

### Pitfall 2: table 与 paragraph 混切
**What goes wrong:** 表格被句界切分器拆开。  
**Why it happens:** 未做结构优先的 pass-1。  
**How to avoid:** `table` 先进入“原子段”通道，重叠始终 0。  
**Warning signs:** 输出中单个 table 行跨多个 chunk。  
[VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`]

### Pitfall 3: 元数据继承规则不一致
**What goes wrong:** `page`、`heading_path` 在聚合块中缺失或不稳定。  
**Why it happens:** 未定义“主文本来源页码/跨页最小页码”规则。  
**How to avoid:** 固化 D-24~D-26，并用夹具覆盖跨页场景。  
**Warning signs:** 同一输入重复运行得到不同 `page`。  
[VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`] [ASSUMED]

## Code Examples

Verified patterns from authoritative sources:

### Pydantic 列表校验与 JSON 导出
```python
from pydantic import BaseModel, TypeAdapter

class Chunk(BaseModel):
    chunk_id: str
    text: str

ta = TypeAdapter(list[Chunk])
chunks = ta.validate_python([{"chunk_id": "c1", "text": "abc"}])
payload = ta.dump_json(chunks)
```
Source: [CITED: https://docs.pydantic.dev/latest/concepts/type_adapter/]

### 现有项目 JSON 输出约定（UTF-8 可读）
```95:100:src/eval_corpus/stats.py
def write_stats_json(out_path: Path, payload: dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
```
[VERIFIED: `src/eval_corpus/stats.py`]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `dataclass` + 纯 json（早期讨论草案） | Pydantic v2 `BaseModel` + `TypeAdapter` | 2026-04-13（D-16 修订） | 入站校验、导出、schema 更一致 [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`] |

**Deprecated/outdated:**
- “Phase 2 继续沿用 dataclass 方案”已过时，必须按 D-16 改为 Pydantic [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`].

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | 推荐 `ir_models.py/chunker.py/chunk_io.py` 文件拆分 | Architecture Patterns | 仅影响任务拆分粒度，不影响功能正确性 |
| A2 | 句界优先 + hard-cut 可先用规则法，不引入 NLP 依赖 | Architecture Patterns | 若规则集过弱，边界准确率可能偏低 |
| A3 | `chunk_id` 可先用确定性哈希策略 | User Constraints / Implementation detail | 若后续要求全局可追溯，可能需迁移 ID 方案 |

## Open Questions (RESOLVED)

1. **句界标点白名单是否要覆盖中英文混排全量符号？（RESOLVED）**
   - What we know: 该项在 Claude discretion 内，可由实现固定 [VERIFIED: `.planning/phases/02-ir/02-CONTEXT.md`]
   - What's unclear: 是否需要与后续 METR-03 口径完全一致
   - Recommendation: 在 Phase 2 README 显式列出规则，并在 Phase 4 指标实现时复用同一集合 [ASSUMED]
   - **RESOLVED:** Phase 2 先落地一套固定的中英文句界标点白名单并在测试中钉死；Phase 4 复用该集合计算边界指标，避免口径漂移。

2. **`page_span` 是否纳入 Phase 2 交付？（RESOLVED）**
   - What we know: 非必交付，允许仅 `page` [VERIFIED: D-26]
   - What's unclear: Phase 4 是否需要跨度字段做统计
   - Recommendation: 先预留字段定义，默认不写出，避免拖延主线 [ASSUMED]
   - **RESOLVED:** 仅在模型层预留可选字段，不作为 Phase 2 必交付输出；主流程以 `page` 语义达成 CHUNK-01/02/03。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | 分块核心与 CLI | ✓ | 3.12.8 | — |
| pytest | CHUNK-01~03 自动化验证 | ✓ | 9.0.3 | 若缺失可用 `python -m pytest` 安装后执行 |
| pydantic | IR/Chunk 模型与校验 | ✓ | 2.11.10 | 无（阻塞） |
| typer | `corpus-eval chunk` 子命令 | ✓ | 0.20.0 | 无（阻塞） |
| corpus-eval CLI entry | 端到端命令验证 | ✓ | 0.1.0 | `python -m eval_corpus.cli`（若入口脚本缺失） |

Evidence: [VERIFIED: `python --version`, `pytest --version`, `corpus-eval version`, Python import version checks on 2026-04-13]

**Missing dependencies with no fallback:**
- None [VERIFIED].

**Missing dependencies with fallback:**
- None [VERIFIED].

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 [VERIFIED: `pytest --version`] |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options] testpaths = ["tests"]`) [VERIFIED: `pyproject.toml`] |
| Quick run command | `pytest -q tests/test_chunker_core.py -x` [ASSUMED: file to be added in Phase 2] |
| Full suite command | `pytest -q` [VERIFIED: pytest convention + existing tests directory] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CHUNK-01 | `ParsedBlock` 字段与 JSON 交换行为正确 | unit | `pytest -q tests/test_chunker_core.py::test_parsed_block_schema -x` | ❌ Wave 0 |
| CHUNK-02 | 长度 300–1000、table 原子、句界+hard-cut、重叠 10–20% | unit | `pytest -q tests/test_chunker_core.py::test_chunking_rules -x` | ❌ Wave 0 |
| CHUNK-03 | 同一分块器对统一 `ParsedBlock[]` 输入稳定输出 | unit/integration | `pytest -q tests/test_chunker_cli.py::test_chunk_command_roundtrip -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest -q tests/test_chunker_core.py -x` [ASSUMED]
- **Per wave merge:** `pytest -q` [VERIFIED]
- **Phase gate:** Full suite green before `/gsd-verify-work` [VERIFIED: workflow expectation]

### Wave 0 Gaps
- [ ] `tests/test_chunker_core.py` — covers CHUNK-01, CHUNK-02
- [ ] `tests/test_chunker_cli.py` — covers CHUNK-03
- [ ] `src/eval_corpus/ir_models.py` — 提供可测试模型边界
- [ ] `src/eval_corpus/chunker.py` — 提供可测试纯函数核心

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A（本 phase 无鉴权入口） [ASSUMED] |
| V3 Session Management | no | N/A（本 phase 为离线 CLI） [ASSUMED] |
| V4 Access Control | no | N/A（本 phase 无多角色访问面） [ASSUMED] |
| V5 Input Validation | yes | Pydantic v2 模型校验（`BaseModel`/`TypeAdapter`） [VERIFIED: D-16] [CITED: https://docs.pydantic.dev/latest/concepts/models/] |
| V6 Cryptography | no | N/A（本 phase 无加密设计） [ASSUMED] |

### Known Threat Patterns for Python CLI + JSON pipeline

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| 恶意/畸形 JSON 导致解析失败或字段污染 | Tampering | 使用 `TypeAdapter(list[ParsedBlock])` 严格校验并显式报错 [CITED: https://docs.pydantic.dev/latest/concepts/type_adapter/] |
| 路径参数误写导致覆盖意外文件 | Tampering | `Path` 参数 + 明确 `--blocks-in/--chunks-out`，测试覆盖 I/O 边界 [ASSUMED] |
| 超长文本导致内存峰值升高 | DoS | 分块过程线性处理 + 限制 `max_chars` + 大样本压测 [ASSUMED] |

## Sources

### Primary (HIGH confidence)
- Repository code and planning docs:
  - `.planning/phases/02-ir/02-CONTEXT.md`
  - `.planning/REQUIREMENTS.md`
  - `.planning/STATE.md`
  - `.planning/config.json`
  - `pyproject.toml`
  - `src/eval_corpus/cli.py`
  - `src/eval_corpus/manifest.py`
  - `src/eval_corpus/stats.py`
  - `tests/test_stats.py`
- Official docs:
  - https://docs.pydantic.dev/latest/concepts/models/
  - https://docs.pydantic.dev/latest/concepts/type_adapter/
  - https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str

### Secondary (MEDIUM confidence)
- None.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 锁定决策 + 本地代码/环境双重验证。
- Architecture: MEDIUM - 核心规则已锁定，但模块拆分与句界细节仍有实现自由度。
- Pitfalls: HIGH - 均可直接映射到 D-20~D-26 与成功标准。

**Research date:** 2026-04-13  
**Valid until:** 2026-05-13（30 天）
