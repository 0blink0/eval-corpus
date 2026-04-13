# Phase 2: 统一 IR 与分块器 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.

**Date:** 2026-04-13
**Phase:** 2-统一 IR 与分块器
**Areas discussed:** ParsedBlock 建模与序列化, 重叠率定义, heading_path 与 page, 分块器对外接口

---

## ParsedBlock 建模与序列化

**User's choice:** 全部 → 采用推荐项 **dataclass + json、snake_case、table 必含 text 可选 cells、parser_tool 默认 `"unknown"`**

**Notes:** 不强制 Pydantic。

---

## 重叠率定义

**User's choice:** 全部 → 推荐项 **后块长度比例、Unicode 字符边界、table 不参与、合并 title+正文参与**

---

## heading_path 与 page

**User's choice:** 全部 → 推荐项 **heading_path 为 list[str] / JSON 数组、page 可 null、chunk page 取 min、可选 page_span**

---

## 分块器对外接口

**User's choice:** 全部 → 推荐项 **库 API + `corpus-eval chunk`（--blocks-in / --chunks-out）**

---

## Claude's Discretion

- chunk_id、句界标点细节、page_span 是否在本期落盘。

## Deferred Ideas

- Pydantic、独立包、流式分块、三工具映射（Phase 3）。
