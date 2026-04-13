# Phase 2: 统一 IR 与分块器 - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

实现 **`ParsedBlock` 统一中间表示**与**统一分块器**：结构优先、表格原子块、句界优先切分与硬切回退、文本块目标长度 **300–1000 Unicode 字符**、重叠 **10–20% 可配置（默认 15%）** 且仅作用于文本类 chunk；输出 **chunk** 带齐元数据（`chunk_id`、`source_file`、`page`、`heading_path`、`parser_tool` 等）。**不包含** Phase 3 三工具解析适配、Phase 4 指标计算。

</domain>

<decisions>
## Implementation Decisions

### 用户选择：四个讨论领域全部采用会话内「第一项推荐」

### ParsedBlock 建模与序列化（领域 1）

- **D-16:** `ParsedBlock` 以 **Python `dataclass`** 为主模型；序列化使用 **标准库 `json`**（可辅以小型 `asdict`/转换函数），**不引入 Pydantic** 为硬依赖（除非后续阶段统一引入）。
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

- **D-27:** 分块核心实现为 **纯 Python API**（函数或类），输入 `ParsedBlock` 序列与配置，输出 chunk 列表（dataclass 或 Typed 结构 + JSON 序列化）。
- **D-28:** 提供 Typer 子命令 **`chunk`**（挂在现有 `corpus-eval` 上）：例如 **`--blocks-in PATH`** 读入 `ParsedBlock[]` JSON，**`--chunks-out PATH`** 写出 chunk JSON；配置项 **`--min-chars` / `--max-chars` / `--overlap-ratio`**（默认值对齐 PROJECT：300、1000、0.15），范围校验与 CONTEXT 一致。
- **D-29:** 单元测试以 **手工构造的 `ParsedBlock[]` 夹具**为主（ROADMAP 成功标准 1–2），不依赖真实 OCR 输出。

### Claude's Discretion

- `chunk_id` 生成策略（UUID / 确定性哈希）、`source_file` 与 Phase 1 路径字符串的对应方式、句界标点白名单的具体集合，由实现与 README 固定即可。
- `page_span` 是否在 Phase 2 落地：若工期紧可仅文档化字段预留，**必须**保证 `page` 与 `heading_path` 行为满足 D-24–D-26。

### Folded Todos

（无 — `todo match-phase` 无匹配项）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 路线图与需求

- `.planning/ROADMAP.md` — Phase 2 目标、成功标准、02-01～02-03
- `.planning/REQUIREMENTS.md` — CHUNK-01、CHUNK-02、CHUNK-03
- `.planning/PROJECT.md` — 统一分块策略 v0（块长、表格原子、重叠、元数据）
- `.planning/phases/01-corpus-baseline/01-CONTEXT.md` — Phase 1 与 Unicode、schema 版本等衔接约定

### 指标与背景

- `测试指标体系.md` — §1 分块质量（边界、重叠、表格保持、元数据等）为 Phase 4 对照口径；Phase 2 输出字段需**可支撑**后续指标，不在本阶段实现指标计算

### 实现代码

- `src/eval_corpus/` — Phase 1 包布局；Phase 2 在同一包内扩展 IR/分块模块

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `src/eval_corpus/cli.py` — 可注册 `chunk` 子命令，与 `manifest` / `stats` 并列
- `pyproject.toml` — 已定义 `corpus-eval` 入口与 pytest

### Established Patterns

- JSON 产物含 `schema_version`（Phase 1）；chunk 输出建议同样带 **`schema_version`**

### Integration Points

- Phase 3 适配器产出 `ParsedBlock[]` 后调用同一分块 API；Phase 4 读取 chunk JSON

</code_context>

<specifics>
## Specific Ideas

- 用户采用 **「全部」** 表示四个领域均讨论；选项一律取会话内已声明的 **第一项推荐**（见 DISCUSSION-LOG）。

</specifics>

<deferred>
## Deferred Ideas

- 引入 Pydantic / 独立分包 / 实时流式分块：未纳入 Phase 2。
- 三工具具体映射规则：属 Phase 3。

### Reviewed Todos (not folded)

（无）

</deferred>

---

*Phase: 02-ir*
*Context gathered: 2026-04-13*
