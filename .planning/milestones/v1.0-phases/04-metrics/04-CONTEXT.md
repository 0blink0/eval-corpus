# Phase 4: 分块指标引擎 - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

实现《测试指标体系》§1 的七项分块指标（METR-01~07）计算与阈值对照，形成可复现的指标结果数据结构与 CLI 输出。范围包含：指标输入契约、计算公式、适用性判定、聚合逻辑、语义完整率抽检接口。  
不包含：报告模板与多格式导出（Phase 5）、批处理编排（Phase 5）。

</domain>

<decisions>
## Implementation Decisions

### 指标口径与适用性

- **D-44:** 采用严格口径：每项指标必须定义分子、分母、排除条件。
- **D-45:** 不可判定样本不强行计分，统一记为 `not_applicable`，并单独统计 `applicable_count / total_count`。

### 语义完整率（METR-07）

- **D-46:** 采用“规则主导 + 固定抽样人工复核”路径。
- **D-47:** 自动评分与人工抽检分开记录；人工抽检仅用于校准和解释，不覆盖自动分原值。

### 阈值对照与等级

- **D-48:** 每项指标输出三档等级：`pass / warn / fail`。
- **D-49:** 结果中必须同时保留原始分值与阈值信息，避免只有标签不可追溯。

### 结果模型与输出

- **D-50:** 单次运行输出单一 JSON 工件，包含三层聚合：`per_file`、`per_tool`、`overall`。
- **D-51:** 单一 JSON 作为 Phase 4 标准接口；CSV/HTML/Markdown 导出延后至 Phase 5。

### 异常与缺失数据策略

- **D-52:** 缺失页码、不可判定表格、解析失败等异常样本对相关指标执行“严格标注并剔除计分”。
- **D-53:** 异常样本统一进入 `not_applicable` / `errors` 统计，保证结果可解释、可审计。

### Claude's Discretion

- 七项指标内部模块拆分、函数命名、以及阈值配置文件的物理位置可由实现阶段决定，但不得改变 D-44~D-53 的口径。
- 若人工抽检样本量需要在实现期微调，可在不改变“固定抽样可复现”前提下调整具体数值，并在 README 记录。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 路线图与需求

- `.planning/ROADMAP.md` — Phase 4 的目标、成功标准与 04-01~04-03 计划边界
- `.planning/REQUIREMENTS.md` — METR-01~METR-07 需求条目与追踪关系
- `.planning/PROJECT.md` — 统一评测口径、范围边界与约束

### 前置阶段契约

- `.planning/phases/02-ir/02-CONTEXT.md` — 统一分块与元数据契约（长度、重叠、page、heading_path）
- `.planning/phases/03-adapters/03-CONTEXT.md` — 三工具归一输出与错误模型约定

### 指标与业务背景

- `测试指标体系.md` — §1 七项分块指标定义与目标阈值依据
- `01需求概要设计文档.md` — 业务语境（仅背景，不扩展平台业务范围）

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `src/eval_corpus/chunker.py` — 统一分块行为，可直接作为多项结构类指标输入来源
- `src/eval_corpus/ir_models.py` — `ParsedBlock` / `Chunk` 契约，供指标输入校验
- `src/eval_corpus/adapter_runner.py` 与 `src/eval_corpus/adapters/` — 工具维度聚合所需的 `parser_tool` 与错误信息来源
- `src/eval_corpus/cli.py` — 可扩展 `metrics` 子命令并对接 JSON 输出

### Established Patterns

- 现有实现偏向 Python + Pydantic 模型边界，适合先建稳定 JSON schema 再扩展多格式输出
- 失败场景已采用结构化错误封装，便于并入 `errors` / `not_applicable` 统计

### Integration Points

- 指标引擎读取统一 chunk 结果，不读取工具私有格式
- Phase 4 JSON 结果将作为 Phase 5 报告层唯一上游输入

</code_context>

<specifics>
## Specific Ideas

- 用户对五个灰区均选择了推荐项，并明确偏好“严格口径 + 可解释统计”。
- 语义完整率先走规则与人工抽检可复现流程，暂不强制引入 LLM 裁判分。

</specifics>

<deferred>
## Deferred Ideas

- 指标结果的 CSV/Markdown/HTML 报告导出（Phase 5）
- 批处理与云端扩跑编排（Phase 5）
- LLM-as-judge 并行评分通道（可在后续阶段增量引入）

</deferred>

---

*Phase: 04-metrics*
*Context gathered: 2026-04-13*
