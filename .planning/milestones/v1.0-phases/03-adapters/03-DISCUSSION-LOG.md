# Phase 3: 三工具解析适配 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-04-13
**Phase:** 3-三工具解析适配
**Areas discussed:** 适配器接口与错误模型, IR 映射策略, 版本记录粒度, 失败策略与可观测性, 样例集与验收口径

---

## 用户决策

**User's choice:** 按照推荐的来

因此以下均采用推荐项并写入 CONTEXT：

- 统一接口 `parse_to_blocks(...) -> ParsedBlock[]`
- 统一错误模型（stage/file/tool/message/raw_error）
- 最低一致语义映射 + adapter 内部消化工具特化
- 文件级/运行级记录 `tool_name/tool_version/model_id`
- 默认 continue-on-error + `--fail-fast`
- 最小三件套夹具（文本 PDF / 扫描 PDF / 表格样例）

---

## Claude's Discretion

- adapter 文件拆分与模块组织
- 版本探测来源优先级（SDK/CLI/config fallback）

## Deferred Ideas

- 多模型 fallback 路由
- 适配器并发性能优化
