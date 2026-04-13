# Phase 1: 评测基座与语料规范 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-13
**Phase:** 1-评测基座与语料规范
**Areas discussed:** 配置入口与优先级, 清单产物形态, 语料扫描规则, 黄金统计与基准全文

---

## 配置入口与优先级

| Option | Description | Selected |
|--------|-------------|----------|
| A | 首版仅 CLI + 环境变量 | ✓ |
| B | CLI + 环境变量 + 可选配置文件 | |
| C | Claude 裁量 | |

**User's choice:** 全部选每题第一个推荐 → **1A 2A 3A 4A**（会话内选项定义：1=来源范围，2=优先级，3=环境变量名，4=未提供路径行为）

**Notes:**
- 1A：无独立配置文件。
- 2A：CLI > 环境变量（> 未来配置文件）。
- 3A：`EVAL_CORPUS_ROOT`。
- 4A：立即失败 + 明确提示。

---

## 清单产物形态

| Option | Description | Selected |
|--------|-------------|----------|
| A | JSON 为主工件；CSV 非 P1 必交付 | ✓ |
| B | 同时交付 JSON 与 CSV | |
| C | 以 CSV 为主 | |

**User's choice:** [auto] 按「每项第一项推荐」— **JSON 默认 + stderr 人类摘要 + `--manifest-out` 默认 `./corpus_manifest.json`**

**Notes:** 摘要与 JSON 文件分离；stderr 避免与 stdout 管道冲突。

---

## 语料扫描规则

| Option | Description | Selected |
|--------|-------------|----------|
| A | 默认递归；内置扩展名白名单；不跟 symlink；忽略 `~$*` 等 | ✓ |
| B | 用户仅白名单、无默认集 | |
| C | 默认跟随 symlink | |

**User's choice:** [auto] 第一项推荐组合（递归 + 白名单可覆盖 + 不跟 symlink + 忽略临时文件）

---

## 黄金统计与原始全文基准

| Option | Description | Selected |
|--------|-------------|----------|
| A | 页数可解析才填；表格启发式；Unicode 字符；文本层基准 + `needs_ocr` | ✓ |
| B | 更激进的跨格式页数/表格估计 | |
| C | 字节数为主 | |

**User's choice:** [auto] 第一项推荐组合

**Notes:** 与 Phase 3 OCR 边界清晰，避免 Phase 1 伪造全文。

---

## Claude's Discretion

- JSON schema 细节、完整扩展名表、递归技术上限 — 实现与文档化即可。

## Deferred Ideas

- 独立 yaml 配置、CSV 一等输出、跟随 symlink、深度/排除规则 DSL — 未纳入 Phase 1。
