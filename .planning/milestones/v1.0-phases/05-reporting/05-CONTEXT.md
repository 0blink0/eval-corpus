# Phase 5: 报告、测试数据与批跑 - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

基于 Phase 4 已产出的标准指标 JSON，交付 Phase 5 的三类能力：
1) 自动报告产出（总对比表 + 每工具明细 + 运行元信息）  
2) 合成测试数据生成能力（用于无真料场景下的 smoke/回归）  
3) 批处理入口与运行手册（含云端扩跑说明）  

不包含：新增指标定义、修改 Phase 4 指标口径、扩展 §2~§6 指标体系。

</domain>

<decisions>
## Implementation Decisions

### 报告交付优先级

- **D-54:** 优先保证三类核心输出齐备：总对比表、每工具明细、运行元信息附录。
- **D-55:** 机器可读与人读结果并重，但先确保机器可读结构稳定，再生成人读视图。

### 输出格式策略

- **D-56:** 本阶段推荐一次到位支持 `JSON / CSV / Markdown / HTML` 四种导出格式。
- **D-57:** 所有格式共享同一份中间报告数据模型，避免各格式口径漂移。

### 批跑入口与执行模型

- **D-58:** 先落地单机可用批跑入口，并预留云端扩跑参数与文档说明。
- **D-59:** 调度复杂度控制在 v1：不引入分布式队列，仅提供可配置并行度与目录批处理。

### 合成数据生成器范围

- **D-60:** 覆盖三类样本：文本型、扫描型、表格型。
- **D-61:** 支持可控规模（样本数量/长度/比例）生成，便于 CI smoke 与回归复现。

### 产物目录与命名规范

- **D-62:** 每次运行使用 `run_id` + 时间戳目录，统一保存报告、明细、日志与中间文件。
- **D-63:** 目录按 tool 与 artifact type 双维组织，保证可追溯与可比对。

### 失败策略与重试

- **D-64:** 默认 `continue-on-error`（单文件失败不中止整批），并汇总失败清单。
- **D-65:** 提供失败阈值与重试开关：超过阈值可中止；重试次数可配置。

### Claude's Discretion

- 报告模板样式（表头文案、配色、排序）可由实现阶段决定，但必须保持与 D-54~D-57 一致。
- 合成样本具体文本内容可轻量实现，重点是结构类型覆盖与可复现参数化。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 路线图与需求

- `.planning/ROADMAP.md` — Phase 5 目标、成功标准与 05-01~05-03 计划边界
- `.planning/REQUIREMENTS.md` — RPT-01, RPT-02, RPT-03, DATA-01, DATA-02
- `.planning/PROJECT.md` — 项目范围、约束与已验证决策

### 前置阶段产物契约

- `.planning/phases/04-metrics/04-CONTEXT.md` — 指标输出口径与 JSON 三层结构来源
- `.planning/phases/04-metrics/04-VERIFICATION.md` — 已通过的 Phase 4 目标验收结果
- `src/eval_corpus/metrics/` — Phase 4 指标实现与聚合逻辑
- `src/eval_corpus/metrics_io.py` — 指标结果 I/O 边界

### 指标与业务背景

- `测试指标体系.md` — §1 指标语义与阈值背景
- `01需求概要设计文档.md` — 业务语境（仅背景，不扩展为平台功能）

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `src/eval_corpus/cli.py` 已具备扩展子命令模式，可新增报告/批跑/数据生成入口
- `src/eval_corpus/metrics/aggregate.py` 与 `metrics_io.py` 可作为报告层唯一数据上游
- `tests/test_metrics_*.py` 现有测试风格可复用到 Phase 5 报告与批跑测试

### Established Patterns

- 输入输出以 Pydantic 模型与 JSON schema 边界为主，便于多格式导出
- 错误处理采用结构化 envelope，适合批跑统计 `errors/not_applicable`

### Integration Points

- Phase 5 报告模块消费 Phase 4 `overall/per_tool/per_file`，不得直接重算指标
- 合成数据生成器输出应可直接喂给现有解析-分块-指标流水线

</code_context>

<specifics>
## Specific Ideas

- 用户明确“全部按推荐”，本次讨论直接锁定全部推荐项，避免往返提问。
- 报告层一次到位支持四格式，后续 Phase 完整性验收以“同一运行目录下多格式一致性”作为关键检查点。

</specifics>

<deferred>
## Deferred Ideas

- 分布式调度/任务队列（如 Celery/Ray）不纳入 Phase 5 v1
- LLM 驱动自动讲解报告（Narrative generation）不纳入 Phase 5 v1

</deferred>

---

*Phase: 05-reporting*
*Context gathered: 2026-04-13*
