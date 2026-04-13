# Codebase Concerns

**Analysis Date:** 2026-04-13

## Tech Debt

**Documentation-only repository vs. planned system scale:**
- Issue: The workspace under `D:\data` currently contains only `01需求概要设计文档.md` and `测试指标体系.md`; there is no application source tree (`package.json`, `pyproject.toml`, `src/`, services, or infrastructure as code). The design describes a full B/S stack (Streamlit, FastAPI, LangGraph, PostgreSQL, Qdrant, Neo4j, file storage) and many agents—none of this is implementable or verifiable from the repo alone.
- Files: `01需求概要设计文档.md`, `测试指标体系.md`
- Impact: Schedule, integration risk, and operational readiness cannot be grounded in code; reviews may treat aspirational architecture as delivered capability.
- Fix approach: Initialize a versioned codebase aligned with the documented layers; trace requirements in `01需求概要设计文档.md` to modules, APIs, and deployment artifacts.

**Design document status "待确认":**
- Issue: `01需求概要设计文档.md` lists 文档状态 as 待确认 while specifying concrete stacks (e.g. Qwen3.5-35B-A3B, GLM-OCR, Qdrant, Neo4j). Downstream planning may proceed on unstable baselines.
- Files: `01需求概要设计文档.md` (文档信息 table)
- Impact: Scope churn, rework of integrations, and ambiguous acceptance criteria.
- Fix approach: Formalize document sign-off, version freeze for tech choices, and change-control for appendix items (信创备选、AI预留).

## Known Bugs

Not applicable — no runnable system exists in this repository to exhibit runtime bugs.

## Security Considerations

**Design-time security and compliance (to be validated in implementation):**
- Risk: Sensitive bid/tender data, RBAC, API Key exposure, audit logs, encryption at rest/transit, and export/download controls are specified in `01需求概要设计文档.md` §4.2 but not enforced by code here.
- Files: `01需求概要设计文档.md`
- Current mitigation: Requirements text only.
- Recommendations: Threat model per deployment mode (私有化); secrets management; network segmentation for LLM/OCR services; immutable audit trail design; data retention and cross-border/供应商合规 review if external APIs are used.

**External cognition dependencies (LLM / OCR):**
- Risk: `01需求概要设计文档.md` mandates GLM-OCR for scan/PDF (§3.1.3, §4.4) and local Qwen for reasoning; traffic to third-party or vendor-hosted models may conflict with 私有化/信创 boundaries unless explicitly air-gapped or contractually approved.
- Files: `01需求概要设计文档.md`
- Current mitigation: Stated preference for 本地化部署 and optional 信创附录.
- Recommendations: Document data residency, call paths, fallback when OCR/LLM unavailable, and redaction before outbound calls.

## Performance Bottlenecks

**Planned SLAs without implementation baseline:**
- Problem: Targets such as 1000 pages ≤ 30 minutes, OCR ≥85%, API ≤5s, and RAG latency tiers in `测试指标体系.md` assume a built pipeline.
- Files: `01需求概要设计文档.md` §4.1, `测试指标体系.md` §5
- Cause: No profiling, queueing, or GPU/CPU capacity model in repo.
- Improvement path: Establish benchmarks once parsers, vector index, and agents exist; align `测试指标体系.md` thresholds with contractual SLOs.

## Fragile Areas

**RAG, hallucination, and evidentiary use in regulated procurement:**
- Files: `01需求概要设计文档.md` (RAG/knowledge use, 结果可解释, 原文定位), `测试指标体系.md` §3–4 (幻觉率、引用召回率、合规审查检出率)
- Why fragile: High-stakes decisions (围串标线索、合规判断辅助) amplify harm from retrieval misses or LLM hallucination; `测试指标体系.md` sets 幻觉率 red zone >10% and tight citation metrics—achieving these requires citation-grounded generation and human-in-the-loop disclaimers as in the design’s 职责边界.
- Safe modification: Treat all model outputs as 线索/建议; enforce citation checks (design appendix mentions FactScore/Citation Check direction).
- Test coverage: No automated tests exist; `测试指标体系.md` defines evaluation regimes that are not yet executable.

**信创 / 私有化 variability:**
- Files: `01需求概要设计文档.md` (信创要求、附录：信创备选方案)
- Why fragile: CPU/OS/DB/向量库/图库/前端栈 may need replacement (达梦、Milvus、NebulaGraph、Vue3 等); GLM-OCR vs 全栈国产 OCR 未在主线设计中闭合。
- Safe modification: Isolate adapters (DB, vector, graph, LLM router per §5 预留) before business logic.
- Test coverage: Compatibility matrix unimplemented.

## Scaling Limits

**Concurrency and large files (design-only):**
- Current capacity: Not measurable in repo.
- Limit: Design states ≥10 concurrent users, single file ≤500MB (`01需求概要设计文档.md` §4.1); RAG index and OCR throughput may become bottlenecks first.
- Scaling path: Horizontal workers for parsing/OCR, async job queues, and tiered storage for `File Storage` layer in the architecture diagram.

## Dependencies at Risk

**GLM-OCR and named model stack:**
- Risk: Tight coupling to GLM-OCR branding/API and Qwen3.5-35B-A3B in `01需求概要设计文档.md` §4.4; vendor roadmap, license, and 信创认证 may change.
- Impact: Parsing quality (tables/charts) and downstream compliance features depend on OCR fidelity; similarity and RAG quality depend on embeddings and chunking.
- Migration plan: Abstract OCR and LLM behind internal interfaces (aligned with document’s LLM Router idea); maintain golden-file regression sets once code exists.

## Missing Critical Features

**Executable product and operations:**
- Problem: No services, containers, CI, migrations, or admin UIs—only requirements in `01需求概要设计文档.md`.
- Blocks: End-to-end 审查、比对、风险识别、知识库治理、审计导出 cannot be demonstrated.

**Traceability / XAI storage (forward-looking):**
- Problem: Appendix proposes thought trace and possible blockchain/强审计对接—no schema or storage implementation present.
- Blocks: Regulatory-grade reproducibility of AI conclusions.

## Test Coverage Gaps

**Entire system untested in this repo:**
- What's not tested: All functional modules in `01需求概要设计文档.md` §3; all metrics in `测试指标体系.md` (分块、检索、答案质量、复杂任务、性能、鲁棒性).
- Files: `01需求概要设计文档.md`, `测试指标体系.md`
- Risk: Acceptance disputes; silent regressions when code eventually lands.
- Priority: High — define a minimal automated evaluation harness mapped to `测试指标体系.md` Week 1–4 plan before feature freeze.

---

*Concerns audit: 2026-04-13*
