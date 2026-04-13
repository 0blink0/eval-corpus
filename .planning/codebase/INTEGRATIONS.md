# External Integrations

**Analysis Date:** 2026-04-13

## Implementation Status

**In repository:** No application code, HTTP clients, SDK wiring, database drivers, or CI/deploy configs are present under `D:\data`. Integration points below are **specified in design documentation only**; nothing is connected in code until implementation exists.

**Primary design reference:** `D:\data\01需求概要设计文档.md`.

**RAG / evaluation reference (for future integration & test design):** `D:\data\测试指标体系.md` (retrieval metrics e.g. Recall@5/MRR, latency SLOs, OCR/robustness targets — not bound to any live service in repo).

---

## APIs & External Services

**REST API exposure (outbound from product perspective — offered to third parties):**

- Third-party systems consume **REST APIs** from this platform — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.1: “提供REST API供第三方系统调用”).
- **API authentication:** API Key for external callers — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §4.2).

**LLM / OCR (vendor or local stack):**

- **Qwen3.5-35B-A3B** — local deployment — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §4.4).
- **GLM-OCR** — scanning, charts, tables, images — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §3.1.3, §4.4).

**External data for qualification verification:**

- **External data cross-check** for enterprises / certificates — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §3.5.3: “对接合法合规外部数据源”).
- **Reserved public API:** national construction market supervision platform (“四库一平台”) for live verification — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` appendix “AI发展预留空间” §针对特定违法违规).

**Notification:**

- **notification** skill — push / notify — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.3.3); concrete channel (email, SMS, IM) not fixed in excerpt.

**Future / optional (信创):**

- Alternate LLM APIs (e.g. ChatGLM, Wenxin, Pangu) — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` appendix 信创).

---

## Data Storage

**Relational database:**

- **PostgreSQL** and/or **MySQL** per compatibility — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §4.3; diagram shows PostgreSQL).

**Vector database:**

- **Qdrant** — document semantic search, similarity — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.2, §4.4).

**Graph database:**

- **Neo4j** — enterprise / personnel relationship analysis — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.2, §4.4).

**File storage:**

- Dedicated **file storage** tier in architecture — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.2). No object-store product name mandated in the reviewed sections.

**Knowledge bases (logical integrations):**

- Multiple typed knowledge bases (`laws_regulations`, `internal_rules`, `qualifications`, `cases`, `experts`, `templates`, `sensitive_words`, `custom_*`, etc.) — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.3.4, §3.11).

**Caching:**

- Not explicitly named in the architecture summary — **not specified** as a named component in `D:\data\01需求概要设计文档.md` §2.2.

---

## Authentication & Identity

**Application security (planned):**

- **RBAC** — role-based access control — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §4.2).
- **API Key** for external API access — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §4.2).

**OAuth/OIDC/SAML:** Not specified in the sections reviewed; treat as **not documented** unless added in later revisions.

---

## Monitoring & Observability

**Audit / logging:**

- **Audit logs** for operations and traceability — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §4.2).

**Error tracking / APM:** Not named in the reviewed architecture — **not specified**.

**AI traceability (future):**

- **Thought trace / provenance** and possible blockchain or strong audit linkage — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` appendix “可解释性与溯源存证”).

---

## CI/CD & Deployment

**Hosting:** Localized / private deployment — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §2.1, §4.2).

**Container orchestration (optional 信创 note):** Docker/K8s — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` appendix 信创).

**CI pipeline:** Not described in repo — **not detected**.

---

## Environment Configuration

**Required env vars:** None codified; implementation should derive from future `pyproject.toml`/`requirements.txt` and deployment docs. Design mentions **API keys**, **DB connections**, and **model/OCR endpoints** only at concept level — **documented only / not in repo**.

**Secrets:** Design requires protection for sensitive data in transit and at rest — **documented only / not in repo** (`D:\data\01需求概要设计文档.md` §4.2). Do not commit secrets; no `.env` content is analyzed here.

---

## Webhooks & Callbacks

**Incoming:** Not specified in the reviewed sections — **none documented**.

**Outgoing:** Notification skill implies outbound notifications; exact protocols **not specified** in detail — **documented only / not in repo**.

---

## RAG Testing Context (`D:\data\测试指标体系.md`)

When vector DB and LLM are implemented, the metrics doc defines **target thresholds** for chunk quality, retrieval (Recall@k, MRR, NDCG), answer grounding (citation recall/precision, hallucination rate), task-specific checks (compliance, risk), and performance (latency percentiles, QPS). These inform **integration test / eval harness design** — **reference only / not wired in repo**.

---

*Integration audit: 2026-04-13*
