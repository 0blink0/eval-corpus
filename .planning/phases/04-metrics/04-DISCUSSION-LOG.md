# Phase 4: 分块指标引擎 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves alternatives considered.

**Date:** 2026-04-13
**Phase:** 04-metrics
**Areas discussed:** 指标口径精确定义, 语义完整率实现路径, 阈值对照与判定等级, 结果数据模型与 CLI 输出, 异常与缺失数据处理策略

---

## 指标口径精确定义

| Option | Description | Selected |
|--------|-------------|----------|
| 严格口径 | 每项明确定义分子/分母/排除条件，不可判定记 `not_applicable` | ✓ |
| 宽松口径 | 缺失数据按默认值处理，尽量全部纳入计分 | |
| 混合口径 | 核心指标严格，其余宽松 | |

**User's choice:** 严格口径  
**Notes:** 强调结果可解释性，避免口径漂移。

---

## 语义完整率实现路径（METR-07）

| Option | Description | Selected |
|--------|-------------|----------|
| 规则主导 + 固定抽样人工复核 | 自动规则评分，辅以固定样本人工复核 | ✓ |
| 规则 + LLM-as-judge 双轨 | 并行输出规则分与 LLM 裁判分 | |
| 纯规则法 | 不做人工/LLM 抽检 | |

**User's choice:** 规则主导 + 固定抽样人工复核  
**Notes:** 优先可复现与稳定性，先不强依赖 LLM。

---

## 阈值对照与判定等级

| Option | Description | Selected |
|--------|-------------|----------|
| 三档判定 | `pass / warn / fail`，并输出原始分值与阈值 | ✓ |
| 二档判定 | `pass / fail` | |
| 仅原始分值 | 不提供等级标签 | |

**User's choice:** 三档判定  
**Notes:** 标签便于决策，同时保留原值用于复核。

---

## 结果数据模型与 CLI 输出

| Option | Description | Selected |
|--------|-------------|----------|
| 单一 JSON 结果 | 一次运行输出标准 JSON，含 `per_file/per_tool/overall` | ✓ |
| JSON + CSV | 同步输出两种格式 | |
| 分拆多文件 | 按工具/指标拆分输出 | |

**User's choice:** 单一 JSON 结果  
**Notes:** 先稳定程序消费接口，多格式导出后置。

---

## 异常与缺失数据处理策略

| Option | Description | Selected |
|--------|-------------|----------|
| 严格标注并剔除计分 | 缺失或不可判定样本不进分子分母，入统计字段 | ✓ |
| 降级参与计分 | 缺失数据按保守默认值参与计算 | |
| 按指标定制 | 每个指标独立缺失策略 | |

**User's choice:** 严格标注并剔除计分  
**Notes:** 与严格口径一致，强调统计透明。

---

## Claude's Discretion

- 无额外“你决定”项；五个灰区均由用户明确拍板。

## Deferred Ideas

- LLM-as-judge 并行轨道（后续可增量）
- 多格式报告导出（Phase 5）

