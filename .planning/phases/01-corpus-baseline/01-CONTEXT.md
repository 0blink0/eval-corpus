# Phase 1: 评测基座与语料规范 - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

在可配置语料根目录的前提下，交付：**路径校验与明确错误**、**语料清单工件**（机器可读 + 人类可读摘要）、**黄金统计**（至少总字符数、文件数；页数/表格等在可解析或启发式可判定时填入）。不扩展 Phase 2+ 能力（统一 IR、OCR 链路、指标引擎等）。

</domain>

<decisions>
## Implementation Decisions

### 配置入口与优先级（用户：全部选每题第一项推荐）

- **D-01:** 首版仅支持 **CLI 参数 + 环境变量**，不引入独立配置文件（后续若需要再扩展）。
- **D-02:** 优先级为 **CLI > 环境变量**（若未来增加配置文件，则为 **CLI > 环境变量 > 配置文件**，与本阶段一致）。
- **D-03:** 语料根目录环境变量名为 **`EVAL_CORPUS_ROOT`**。
- **D-04:** 未提供可用根路径时 **立即失败**：非零退出码 + 明确提示如何设置 CLI/环境变量（不提供静默默认路径）。

### 清单产物形态（默认：每项取讨论中的第一项推荐）

- **D-05:** 机器可读清单默认 **JSON** 单主工件即满足阶段成功标准；CSV 可作为后续可选开关，**非 Phase 1 必交付**。
- **D-06:** 人类可读摘要输出到 **终端**；与机器可读文件分离，**摘要走 stderr**（stdout 保留给管道/可选 JSON 流式扩展）。
- **D-07:** 清单 JSON 输出路径通过 **`--manifest-out <path>`** 指定；未给出时默认 **`./corpus_manifest.json`**（当前工作目录，文档中说明可复现性依赖工作目录或显式传绝对路径）。

### 语料扫描规则（默认：每项取第一项推荐）

- **D-08:** 默认 **递归** 扫描子目录（不设过低深度上限；若需防环或极深目录，实现侧可用合理技术上限并写入日志，不改变「递归」语义）。
- **D-09:** 内置 **常见文档扩展名白名单**（如 pdf、Office 系列、txt、md、常见图片格式等），并提供 CLI 覆盖/追加扩展名的能力（具体列表由实现与 README 固定）。
- **D-10:** 默认 **不跟随** 符号链接（`symlink_follow=false`），避免不可复现与环；若未来需要，以显式 flag 开启。
- **D-11:** 默认 **忽略** Office 临时锁文件（如 `~$*`）及明显无关项（如 `.DS_Store`）；其它忽略规则可在实现中补充并在文档列出。

### 黄金统计与原始全文基准（默认：每项取第一项推荐）

- **D-12:** **页数** 仅对 **能可靠解析页数** 的格式填写（如 PDF 使用页数 API）；无法解析时字段为 **`null` 或省略**，并附 **`page_count_reason`**（或等价）说明。
- **D-13:** **表格数量** 在 Phase 1 采用 **启发式**（扩展名 + 轻量探测）；精确表格计数留给后续解析/IR 阶段，统计字段中注明 **`heuristic: true`**（或文档说明）。
- **D-14:** **字符统计** 使用 **Unicode 字符粒度**（中文按字计），非 UTF-8 字节数。
- **D-15:** **原始全文基准** 在 Phase 1 仅抽取 **可读文本层**（如 PDF 文本层、纯文本等）；对明显 **需 OCR** 的扫描件，在清单/统计中 **标注 `needs_ocr: true`（或等价）**，**不伪造**正文长度；与 Phase 3 三工具解析衔接。

### Claude's Discretion

- 内置扩展名白名单的具体集合、递归防环策略、JSON schema 字段命名风格，由实现与 `README` 统一即可，无需再征询，除非与上述决策冲突。

### Folded Todos

（无 — `todo match-phase` 无匹配项）

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 路线图与需求追溯

- `.planning/ROADMAP.md` — Phase 1 目标、成功标准、01-01～01-03 计划边界
- `.planning/REQUIREMENTS.md` — CORP-01、CORP-02、CORP-03 验收条目
- `.planning/PROJECT.md` — 语料合规（不提交原始语料）、北燃目录可配置、指标口径引用

### 指标与领域背景

- `测试指标体系.md` — §1 分块质量为后续阶段指标依据；Phase 1 统计为其提供分母/基准语境
- `01需求概要设计文档.md` — 业务背景与远期架构参照；**本阶段实现不扩展其中平台功能**

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- 当前仓库 **无 `src/` 与包清单**；Phase 1 为 **绿场** 初始化 CLI/模块的时机。

### Established Patterns

- 无已落地代码模式；建议与 `.planning/codebase/CONVENTIONS.md`、`STACK.md` 中「计划栈」对齐时更新映射文档。

### Integration Points

- 清单与黄金统计输出应 **版本化 schema**（字段名稳定），便于 Phase 2 `ParsedBlock` 与 Phase 4 指标消费。

</code_context>

<specifics>
## Specific Ideas

- 用户偏好：讨论中采用 **「全部选每题第一个推荐」** 加速收敛；领域 2–4 的「第一项」按会话内已声明的推荐语义落盘（见 DISCUSSION-LOG）。

</specifics>

<deferred>
## Deferred Ideas

- CSV 作为与 JSON 并列的一等输出、跟随符号链接、独立 `yaml` 配置文件：未纳入 Phase 1，可在后续阶段或配置增强阶段引入。

### Reviewed Todos (not folded)

（无）

</deferred>

---

*Phase: 01-corpus-baseline*
*Context gathered: 2026-04-13*
