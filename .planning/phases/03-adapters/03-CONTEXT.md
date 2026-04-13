# Phase 3: 三工具解析适配 - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

实现 PaddleOCR / GLM-OCR / MinerU 三条链路，将真实文件解析并统一输出为 `ParsedBlock[]`，记录 parser 名称与版本/模型标识；失败时可定位到文件与阶段。沿用 Phase 2 的 IR 契约（Pydantic、字段语义），不扩展到 Phase 4 指标计算。

</domain>

<decisions>
## Implementation Decisions

### 用户选择

- 用户要求“按照推荐的来”，因此以下 5 个讨论领域全部采用推荐项。

### 适配器接口与错误模型

- **D-30:** 三工具统一暴露接口：`parse_to_blocks(file_path: Path, config: AdapterConfig) -> list[ParsedBlock]`。
- **D-31:** 统一错误模型（可序列化）：`stage`, `file`, `tool`, `message`, `raw_error`（可选）; 其中 `stage` 固定枚举（如 `load` / `parse` / `normalize` / `validate`）。
- **D-32:** CLI 层仅负责编排与汇总，不直接处理工具私有输出结构。

### 输出映射到 IR 的策略

- **D-33:** 先定义“最低一致语义”并强制三工具对齐：
  - `type ∈ {title, paragraph, table, other}`
  - `text` 必填（table 为线性化文本）
  - `page` 缺失时 `null`
  - `heading_path` 缺失时 `[]`
- **D-34:** 工具特化逻辑允许存在，但必须在 adapter 内部消化，出口只能是统一 `ParsedBlock[]`。
- **D-35:** `parser_tool` 在 Phase 3 由适配器写入真实工具名（替换 Phase 2 的 `unknown` 占位）。

### 版本与模型标识记录

- **D-36:** 版本/模型标识在**文件级或运行级**强制记录：`tool_name`, `tool_version`, `model_id`。
- **D-37:** block 级保持 `parser_tool` 即可，不强制每个 block 复制 version/model，避免冗余。

### 失败策略与可观测性

- **D-38:** 默认 `continue-on-error`：单文件失败不终止整批，汇总失败清单。
- **D-39:** 提供 `--fail-fast` 开关以支持调试与 CI 快速失败。
- **D-40:** 错误输出至少包含：文件路径、工具名、阶段（stage）、简明消息；debug 模式附 `raw_error`。

### 样例集与验收口径

- **D-41:** 采用最小三件套夹具（每工具至少覆盖同一套输入类型）：
  1) 文本型 PDF
  2) 扫描型 PDF
  3) 含表格样例
- **D-42:** 夹具目录建议固定为 `tests/fixtures/adapters/`，先保证最小覆盖，再扩容。
- **D-43:** 验收以“同一批样例三工具都能产出合法 `ParsedBlock[]` 或可定位错误”为准。

### Claude's Discretion

- 每个工具 adapter 的内部模块命名与文件拆分（如 `adapters/paddle.py` / `adapters/glm.py` / `adapters/mineru.py`）可由实现阶段按代码可维护性决定。
- 版本探测优先级（CLI 命令探测 / SDK 常量 / 手动配置回填）可按工具可用性选最稳方案，但输出字段名须一致。

### Folded Todos

（无 — `todo match-phase` 无匹配项）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 路线图与需求

- `.planning/ROADMAP.md` — Phase 3 目标、成功标准、03-01~03-03
- `.planning/REQUIREMENTS.md` — ADPT-01, ADPT-02, ADPT-03
- `.planning/phases/02-ir/02-CONTEXT.md` — IR 契约与字段语义（D-16~D-29）
- `.planning/phases/02-ir/02-RESEARCH.md` — Phase 2 的建模/验证策略，可复用边界定义

### 指标与背景

- `.planning/PROJECT.md` — 统一口径与公平对比原则
- `测试指标体系.md` — 后续指标口径背景（本阶段不实现指标）

### 现有实现基础

- `src/eval_corpus/ir_models.py` — ParsedBlock/Chunk Pydantic 模型
- `src/eval_corpus/chunk_io.py` — JSON 边界处理
- `src/eval_corpus/chunker.py` — 统一分块核心
- `src/eval_corpus/cli.py` — 现有 CLI 基座，可继续扩展 adapter 命令

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- 已有 Pydantic IR 模型与 JSON I/O，可直接作为 adapter 输出目标。
- 现有 CLI 框架可承载三工具统一入口与批处理参数。

### Established Patterns

- 产物 JSON 使用 `schema_version` 与 UTF-8（`ensure_ascii=False`）
- 测试以 fixtures + pytest 为主，适配器阶段继续沿用。

### Integration Points

- Phase 3 的 adapter 输出 `ParsedBlock[]` 直接进入 `chunk_blocks`。
- Phase 4 指标引擎应消费 Phase 3 的统一输出，不读取工具私有格式。

</code_context>

<specifics>
## Specific Ideas

- 用户明确要求按推荐项执行，已将推荐项全部锁定为 D-30~D-43。

</specifics>

<deferred>
## Deferred Ideas

- 更高级的模型路由与多模型 fallback 策略（可在后续 phase 增强）。
- 工具侧性能优化与并发调度细化（本阶段先保证正确性与可观测性）。

### Reviewed Todos (not folded)

（无）

</deferred>

---

*Phase: 03-adapters*
*Context gathered: 2026-04-13*
