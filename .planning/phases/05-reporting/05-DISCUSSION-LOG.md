# Phase 5: 报告、测试数据与批跑 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves alternatives considered.

**Date:** 2026-04-13
**Phase:** 05-reporting
**Areas discussed:** 报告产物优先级, 输出格式策略, 批跑入口与执行模型, 合成数据生成器范围, 运行目录与命名规范, 失败策略与重试机制

---

## 讨论方式

用户选择：**全部按推荐**  
处理策略：按推荐项一次性锁定全部灰区决策并落盘。

---

## 报告产物优先级

| Option | Description | Selected |
|--------|-------------|----------|
| 推荐方案 | 总对比表 + 每工具明细 + 运行元信息三类齐备，先稳机器可读再生成人读视图 | ✓ |
| 备选方案 | 只先做总表，明细与元信息后置 | |
| 备选方案 | 只做人读报告，机器可读后置 | |

**User's choice:** 推荐方案（由“全部按推荐”确定）

---

## 输出格式策略

| Option | Description | Selected |
|--------|-------------|----------|
| 推荐方案 | 一次到位支持 JSON/CSV/Markdown/HTML 四格式 | ✓ |
| 备选方案 | 先 JSON+Markdown，后续再扩展 CSV/HTML | |
| 备选方案 | 仅 JSON，其他格式延后 | |

**User's choice:** 推荐方案（由“全部按推荐”确定）

---

## 批跑入口与执行模型

| Option | Description | Selected |
|--------|-------------|----------|
| 推荐方案 | 单机批跑先落地，预留云端扩跑参数与手册，不引入分布式队列 | ✓ |
| 备选方案 | 立即做复杂云端调度 | |
| 备选方案 | 仅单文件手动运行，不做批入口 | |

**User's choice:** 推荐方案（由“全部按推荐”确定）

---

## 合成数据生成器范围

| Option | Description | Selected |
|--------|-------------|----------|
| 推荐方案 | 覆盖文本/扫描/表格三类，支持可控规模参数 | ✓ |
| 备选方案 | 仅最小 smoke 样本 | |
| 备选方案 | 仅文本样本 | |

**User's choice:** 推荐方案（由“全部按推荐”确定）

---

## 运行目录与命名规范

| Option | Description | Selected |
|--------|-------------|----------|
| 推荐方案 | run_id+时间戳目录，按 tool 与 artifact type 双维组织 | ✓ |
| 备选方案 | 简单平铺目录 | |
| 备选方案 | 仅按 tool 目录 | |

**User's choice:** 推荐方案（由“全部按推荐”确定）

---

## 失败策略与重试机制

| Option | Description | Selected |
|--------|-------------|----------|
| 推荐方案 | 默认 continue-on-error，支持失败阈值中止与可配置重试 | ✓ |
| 备选方案 | 全程 fail-fast | |
| 备选方案 | 固定重试次数且无阈值控制 | |

**User's choice:** 推荐方案（由“全部按推荐”确定）

---

## Claude's Discretion

- 无额外“你决定”项，核心灰区均已由用户“全部按推荐”锁定。

## Deferred Ideas

- 分布式队列调度（不在 Phase 5 v1）
- 自动讲解型报告（不在 Phase 5 v1）

