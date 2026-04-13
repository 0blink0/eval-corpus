---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: Executing Phase 5
stopped_at: Completed 05-reporting-02-PLAN.md
last_updated: "2026-04-13T09:59:56.335Z"
progress:
  total_phases: 5
  completed_phases: 4
  total_plans: 15
  completed_plans: 14
  percent: 93
---

# Project State

## Current Phase

Phase 5 — Ready to plan

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-13)

**Core value:** 同一套分块与评测口径下对比 PaddleOCR / GLM-OCR / MinerU 的分块质量，产出可复现的对比表与分项结果。  
**Current focus:** Phase 5 — reporting

## Notes

- 语料目录：**北燃热力宣传品采购归档资料**（由用户在配置中提供实际路径）
- 指标口径：`测试指标体系.md` §1 全部七项
- 当前进度：Phase 1~4 已完成执行；Phase 5 待 discuss/plan/execute

## Decisions

- [04-metrics] 语义完整率首版采用规则评分以保证可复现与可审计。
- [04-metrics] 人工复核记录与 `auto_score` 分离存储，避免覆盖自动分值。
- [Phase 04-metrics]: 语义完整率首版采用规则评分以保证可复现与可审计。
- [Phase 04-metrics]: 人工复核记录与 auto_score 分离存储，避免覆盖自动分值。
- [Phase 04-metrics]: Phase 4 输出统一为单一 JSON 工件，仅暴露 per_file/per_tool/overall 三层接口。
- [Phase 04-metrics]: 聚合层保留 raw_value/threshold/level 与 applicable/not_applicable/errors 统计，避免下游丢失审计信息。
- [Phase 05-reporting]: 报告层只消费 per_file/per_tool/overall 工件，不在报告层重算指标。
- [Phase 05-reporting]: 四格式导出统一复用同一行级数据集并对 HTML 文本做 escape。
- [Phase 05-reporting]: 批跑失败阈值按 total 失败占比判定并达到阈值即终止
- [Phase 05-reporting]: 目录递归批跑保持单机模型并通过 worker/retry 参数扩展

## Performance Metrics

- Phase `04-metrics` Plan `02`: duration `20min`, tasks `3`, files `3`

## Session Continuity

Last session: 2026-04-13T09:59:56.328Z
Stopped at: Completed 05-reporting-02-PLAN.md
Resume file: None
