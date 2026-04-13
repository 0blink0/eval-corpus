# Coding Conventions

**Analysis Date:** 2026-04-13

## Scope of This Repository

The project root `D:\data` currently contains **documentation only**. There is **no application source tree** (no `src/`, no `package.json`, no Python packages). Conventions below describe **observed patterns in the Markdown artifacts** and reserve **code-related conventions** until a codebase exists.

**Primary documents:**
- `D:\data\01需求概要设计文档.md`
- `D:\data\测试指标体系.md`

---

## Markdown Document Conventions (Observed)

### Document Title and Metadata

- **H1 (`#`)**: Product or system name as the main title (e.g. 智能招投标审查平台).
- **H2 (`##`)**: Major sections — 文档信息, numbered chapters (1. 项目概述), 附录 blocks.
- **H3 (`###`)**: Subsections under chapters (e.g. 1.1 项目背景).
- **H4 (`####`)**: Deeper nesting (e.g. 2.3.1 Agent 层次结构).

### Horizontal Rules

- Use `---` on its own line to separate major blocks (after 文档信息, between chapters, after tables).

### Tables

- **Pipe tables** with header row and alignment row using `:---` for left-aligned columns.
- Common column patterns:
  - 项目 | 内容 / 说明
  - 指标 | 定义 | 计算方式 | 目标值 | 备注
- **Bold** in cells for emphasis on metric or field names (e.g. **Recall@5**, **语义完整率**).
- Code-like identifiers in backticks in tables where applicable (e.g. `laws_regulations`, `internal_rules` in `01需求概要设计文档.md`).

### Terminology and Naming

- **English identifiers** for technical stack and APIs: LangGraph, FastAPI, Streamlit, Coordinator Agent, skill names (`law_retrieval`, `intent_recognition`).
- **Chinese** for business concepts: 围串标, 弱响应, 偏离项, 合规审查.
- **Priority labels**: P0 / P1 for phased delivery; 一期 / 二期 for roadmap.
- **Knowledge base type keys**: snake_case with optional `custom_*` prefix for extensions.

### Diagrams and Flows

- **ASCII box diagrams** in fenced code blocks (no language tag) for architecture (B/S layers, Agent boxes).
- **Arrow flows** using `→` and vertical `↓` for process descriptions.

### Lists

- **Bold lead-in** for principle bullets (e.g. **合规审查 Agent**：…).
- Unordered lists for principles and appendix notes; ordered steps in 信创/扩展 tables where numbered.

### Emphasis

- **Bold** for problem labels and key terms in prose (e.g. **串标围标**).
- *Italic* used sparingly for document footers (*文档结束*).

---

## Code Conventions (Application Source)

**Status:** **N/A** — no implementation repository is present under `D:\data`.

When code is added, align naming and layering with the **specified or implied** targets in `D:\data\01需求概要设计文档.md`:

| Area | Target from design doc | Implied convention |
|------|------------------------|--------------------|
| Agent orchestration | LangGraph `StateGraph` (Coordinator), LangGraph Agent (specialists) | Python modules; graph/state naming consistent with LangGraph idioms |
| Shared logic | Skill as **Python Module** | Reusable functions/classes under a clear `skills/` or equivalent package |
| HTTP API | FastAPI at API Gateway | REST routes, Pydantic models for request/response where applicable |
| Web UI | Streamlit | Page/scripts colocated or under a `ui/` or `app/` pattern per future project choice |
| Tools | FastAPI Tools (callable from agents) | Thin adapters over DB/OCR/retrieval; avoid business logic duplication in tools |
| Knowledge extension | `KnowledgeBasePlugin`, `KnowledgeBaseEngine` (section 5.3) | Plugin interface + registration pattern for new KB types |

Do **not** treat the above as enforced lint rules until a repo with `pyproject.toml` / `ruff` / `mypy` (or equivalent) exists.

---

## Import Organization / Formatting / Linting (Source Code)

**Not applicable** — no ESLint, Prettier, Ruff, or formatter config detected in `D:\data`.

---

## Comments and Documentation in Code

**Not applicable** until source exists. The design doc implies **traceability**: results should support 原文定位 and 依据说明; future code should preserve provenance fields where the spec calls for them (e.g. thought trace / audit hooks in appendix AI预留).

---

## Function and Module Design (Prescriptive for Future Code)

- **Coordinator**: entry orchestration only; defer domain logic to specialist agents (matches table 2.3.2 in `01需求概要设计文档.md`).
- **Agent boundaries**: respect 职责边界 columns — e.g. 比对分析不做合规性判断, 合规审查不做文件间比对.
- **API-first**: external integration via REST API as in section 2.1.

---

*Convention analysis: 2026-04-13*
