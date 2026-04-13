# Technology Stack

**Analysis Date:** 2026-04-13

## Repository State (Implemented)

**Source code:** Not detected. The workspace at `D:\data` contains Markdown documentation only. There is no `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or other application manifests.

**Languages (implemented):** Not applicable — no runnable application code in repo.

**Runtime (implemented):** Not applicable.

**Package manager / lockfile (implemented):** Not detected.

**Frameworks (implemented):** Not detected.

**Build / dev tooling (implemented):** Not detected.

**Prescriptive note for future implementation:** When code lands here, update this section from manifests and config files at repo root (e.g. `requirements.txt`, `pyproject.toml`) and primary entry modules.

---

## Planned Stack (Documented Only — Not in Repo)

The following is specified in `D:\data\01需求概要设计文档.md` as the **intended** technical architecture. **Status: documented only / not in repo** until manifests and source appear.

### Languages

**Primary (planned):** Python — implied by Streamlit, FastAPI, LangGraph, and “Python Module” for shared Skills (`D:\data\01需求概要设计文档.md` §2.2–2.3).

**Secondary (planned):** Not separately specified beyond Python ecosystem for agents and tools.

### Runtime

**Environment (planned):** Python runtime for Web UI, API gateway, agents, and tools — **documented only / not in repo**.

**Deployment (planned):** B/S architecture; server-side localized / private deployment (`D:\data\01需求概要设计文档.md` §2.1, §4.2).

### Frameworks (Planned — Documented Only / Not in Repo)

**Web UI:** Streamlit — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.2, §4.4).

**API:** FastAPI as REST API / API Gateway — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.2, §2.3.1, §4.4).

**Agent orchestration:** LangGraph (`StateGraph`, specialized Agents) — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.3.1, §4.4, §8).

**Shared capabilities:** Python modules for Skills; Tools exposed via FastAPI — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.3.1).

### AI / OCR (Planned — Documented Only / Not in Repo)

**LLM:** Qwen3.5-35B-A3B, local deployment — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §4.4).

**OCR:** GLM-OCR for scanned PDFs, charts, tables, images — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §3.1.3, §4.4).

**Architecture extension (planned):** LLM Router between API Gateway and agent layer for model-agnostic switching — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` appendix “AI发展预留空间”).

### Data Stores (Planned — Documented Only / Not in Repo)

**Relational:** PostgreSQL or MySQL (compatibility table lists both; architecture diagram emphasizes PostgreSQL) — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.2, §4.3).

**Vector:** Qdrant — semantic retrieval / similarity — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.2, §4.4).

**Graph:** Neo4j — enterprise relations / collusion-style analysis — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.2, §4.4).

**Files:** File storage layer shown in architecture diagram — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.2).

### Optional / Future (Documented Only — Not in Repo)

**Xinchuang (信创) alternates:** e.g. DM8, KingBase, GaussDB; Milvus; NebulaGraph/HugeGraph; optional Java API / Vue3 UI — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` appendix “信创备选方案”).

**Extension concepts:** `KnowledgeBasePlugin`, `KnowledgeBaseEngine` — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §5.3).

### RAG / Quality Targets (Reference Doc — Not Executable in Repo)

RAG chunking, retrieval, answer-quality, latency, and robustness targets are defined in `D:\data\测试指标体系.md` for future test design; **no test runner or implementation exists in repo**.

## Configuration

**Environment:** No application `.env` or config files detected for a runtime; design doc mentions API Key auth for external API consumers — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §4.2).

**Build:** Not applicable until code exists.

## Platform Requirements (From Design Doc — Documented Only / Not in Repo)

**Client:** Modern browsers (Chrome, Edge, Firefox) (`D:\data\01需求概要设计文档.md` §4.3).

**Server:** Localized / private deployment; optional Docker/K8s in 信创 appendix — **documented only / not in repo**.

**Non-functional (planned):** e.g. API ≤5s, UI ≤3s, ≥10 concurrent users, single file ≤500MB (`D:\data\01需求概要设计文档.md` §4.1).

---

*Stack analysis: 2026-04-13*
