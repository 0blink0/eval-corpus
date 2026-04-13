# 文档解析工具分块指标对比实验

## What This Is

在招投标归档类真实语料（**北燃热力宣传品采购归档资料**）上，对 **PaddleOCR**、**GLM-OCR**、**MinerU** 三条解析链路进行对比实验：将各工具输出归一为同一中间表示后，套用**统一的分块策略**，按《RAG系统测试指标体系（高标准版）》**§1 分块质量**中的**全部七项指标**自动计算与汇总，产出**总对比表**与**各工具分项测试结果**。实验代码需支持在一台机器上可复现运行，并在性能不足时可迁移至云服务器批跑；同时提供**可生成的测试数据/黄金统计**能力，便于回归与扩展语料。

## Core Value

用**同一套分块与评测口径**回答「哪条解析链路更利于后续 RAG/审查类场景」，避免「工具自带分块不一致」导致的假对比。

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] 建立可复现的语料目录约定与清单（含北燃归档资料；若路径不在仓库内则记录绝对路径或挂载说明）
- [ ] 实现统一中间表示（段落/标题/表格/页码等）与**统一分块器**（见下节策略摘要）
- [ ] 接入 PaddleOCR、GLM-OCR、MinerU 三套解析，并归一到中间表示
- [ ] 按 §1 实现七项分块指标：**语义完整率、覆盖完整率、边界准确率、块长度达标率、元数据完整率、表格保持率、重叠合理率**（含目标阈值对照）
- [ ] 自动生成**对比总表** + **每工具明细结果**（可机器可读 JSON/CSV + 人类可读 Markdown/HTML）
- [ ] 提供测试数据生成能力（合成样例或统计用基准，用于回归与小规模压测）
- [ ] 记录运行环境与耗时，便于迁云扩缩

### Out of Scope

- **不交付**《01需求概要设计文档》中的完整「智能招投标审查平台」业务功能（该文档仅作**领域背景与远期系统参照**）
- **本轮不测**《测试指标体系》§2–§6（检索、答案质量、复杂任务、生产性能、鲁棒性全量）——除非后续单独立项；但若解析输出被下游复用，可在此实验中记录**解析阶段耗时**作为附录
- **不承诺**替用户完成商业 API 账号、许可证合规与脱敏审批——由使用方自备

## Context

- **指标体系**：`测试指标体系.md`（§1 分块质量为目标口径）
- **业务背景**：`01需求概要设计文档.md`（智能招投标审查、扫描件/表格/原文定位等需求语境）
- **评测语料**：用户指定文件夹 **北燃热力宣传品采购归档资料**（当前若未同步到 `d:\data`，需在实验配置中写明实际路径或通过环境变量传入）
- **工具说明**：GLM-OCR 为智谱系 OCR/文档理解能力；MinerU 多为 PDF/文档结构化解析；PaddleOCR 为通用 OCR/版面体系——三者输出形态不同，**必须以统一 IR + 统一分块**再比指标

## 统一分块策略（v0 实验口径）

**原则**：结构边界优先，长度目标其次，句子级回退，表格尽量原子化；重叠仅作用于可滑动的正文类 chunk。

1. **解析归一**  
   各工具输出映射为 `ParsedBlock[]`：`type ∈ {title, paragraph, table, other}`，`text` 或表格结构化文本、`page`（未知则标记）、可选 `heading_path`（由标题层级推断）。

2. **块装配**  
   - 目标长度 **300–1000 字符**（中文按字符计）。  
   - 在不超过 1000 的前提下合并相邻 `paragraph`/`title` 片段；遇 `table` 默认**单独成块**（利于「表格保持率」）；`title` 可与紧随其后的少量正文合并以保留语义。  
   - 超长段落：优先在句末标点断句；其次逗号/分号；最后硬切并计入「硬切」统计（服务「边界准确率」）。

3. **重叠**  
   对纯文本类 chunk 施加 **15%** 目标重叠（允许落入 10–20% 区间配置），以相邻 chunk 后缀/前缀复制实现；表格块默认 **0 重叠**（避免重复计表格）。

4. **元数据**  
   每个输出 chunk 附带：`chunk_id`、`source_file`、`page`、`heading_path`（或最近标题）、`parser_tool`；用于「元数据完整率」与追溯。

5. **语义完整率（自动化近似）**  
   默认：**规则 + 抽样 LLM 评判**可插拔——首版可用「句界比例 + 人工/LLM 抽检协议」在 REQUIREMENTS 中固定操作步骤，避免指标无法落地。

## Constraints

- **环境**：开发机 Windows；解析与训练类依赖可能需 Linux 云主机——代码应容器化或文档化一键迁移
- **合规**：招投标资料可能涉密；**默认不将原始文件提交 git**；仅提交哈希、目录说明与脱敏样例
- **可复现**：固定随机种子、记录各工具版本与模型权重标识

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 统一 IR + 统一分块后再比指标 | 消除各工具原生分块差异带来的不公平 | — Pending |
| 文本 chunk 15% 重叠、表格块原子 | 对齐 §1「重叠合理率」「表格保持率」 | — Pending |
| 语料路径可配置（env/CLI） | 北燃资料未必在仓库内 | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-13 after initialization*
