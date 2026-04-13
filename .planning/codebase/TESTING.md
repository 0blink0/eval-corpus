# Testing Patterns

**Analysis Date:** 2026-04-13

## Critical Clarification

The metrics in this document are **specification targets** defined in `D:\data\测试指标体系.md`. They describe **how RAG and related pipelines should be evaluated** once built. They are **not** descriptions of:

- an existing automated test suite,
- CI jobs,
- or production monitoring dashboards in this workspace.

The repository `D:\data` currently holds **requirements and test-metric documentation only** (`D:\data\01需求概要设计文档.md`, `D:\data\测试指标体系.md`). **No test runner config** (e.g. `pytest.ini`, `vitest.config.*`, `jest.config.*`) is present.

---

## Specification Source

**Authoritative metric document:** `D:\data\测试指标体系.md` (RAG系统测试指标体系 · 高标准版).

**Related product context:** `D:\data\01需求概要设计文档.md` — modules (文件解析, 合规审查, 知识库) imply RAG/retrieval usage (e.g. Qdrant, `law_retrieval`, `policy_retrieval`); non-functional requirements (OCR ≥85%, 1000页 ≤30分钟) overlap thematically with robustness/performance rows below but are **product NFRs**, not the same table as `测试指标体系.md`.

---

## 1. Chunking Quality Metrics (Specification Targets)

Grounded in section **「1. 分块质量指标」** of `D:\data\测试指标体系.md`:

| Metric (as in spec) | Role | Target (spec) |
|---------------------|------|----------------|
| 语义完整率 | Chunk does not split mid-sentence/meaning | >95% |
| 覆盖完整率 | Content preserved after chunking | >99% |
| 边界准确率 | Boundaries at paragraph/sentence ends | >92% |
| 块长度达标率 | Share of chunks in 300–1000 characters | >90% |
| 元数据完整率 | Chapter title, page metadata present | >95% |
| 表格保持率 | Tables structurally preserved | >98% |
| 重叠合理率 | Overlap in 10–20% band | >85% |

**Evaluation methods (per spec):** LLM evaluation + human sampling where noted; ratio formulas as defined in the source table.

---

## 2. Retrieval Metrics (Specification Targets)

From **「2. 检索效果指标」** in `D:\data\测试指标体系.md`:

| Metric | Meaning (spec) | Target |
|--------|----------------|--------|
| Recall@3 / Recall@5 | Relevant chunk in top-K | >90% / >95% |
| MRR | Mean reciprocal rank of first relevant hit | >0.75 |
| NDCG@5 | Ranking quality at 5 | >0.85 |
| SRR | Same-section recall for chapter-aligned queries | >92% |
| Query-Diversity | Cross-query-type recall stability (lower spread = better) | <15% variation |

These are **offline evaluation** targets for retrieval quality, not unit-test assertions unless explicitly implemented as golden-set checks later.

---

## 3. Answer Quality Metrics (Specification Targets)

From **「3. 答案质量指标（LLM评估）」** in `D:\data\测试指标体系.md`:

| Metric | Target (spec) | Notes |
|--------|----------------|--------|
| 答案正确率 | >90% | LLM-as-Judge vs reference |
| 引用召回率 | >95% | Required citations covered |
| 引用精确率 | >90% | Citations relevant |
| 幻觉率 | <5% | Critical facts stricter in ops |
| 拒答准确率 | >80% | Correct abstention when unanswerable |
| 立场一致性 | <5% contradiction | Multi-turn |
| 结构化程度 | >85% | Readability scoring |

---

## 4. Complex Task Metrics (Specification Targets)

From **「4. 复杂任务指标」** in `D:\data\测试指标体系.md` — task-type rows include 对比分析, 合规审查, 风险识别, 摘要生成, 问答匹配 with coverage/detection targets (e.g. 违规点检出率 >95% for 合规审查). Map future automated tests or UAT checklists to these **business-scenario** goals when the product implements those modules.

---

## 5. Performance Metrics (Specification Targets)

From **「5. 性能指标（生产级）」** in `D:\data\测试指标体系.md`:

| Metric | P50 / P95 / P99 or target | Interpretation |
|--------|---------------------------|----------------|
| 分块延迟/页 | <50ms / <200ms / <500ms | Per PDF page |
| 单次检索延迟 | <100ms / <300ms / <500ms | Hybrid vector + keyword |
| 端到端延迟 | <2s / <4s / <8s | Question to answer |
| 并发能力 | 50 QPS @ 95% success | Load target |
| 向量插入吞吐 | >500 chunks/s | Bulk ingest |

These are **SLO-style** targets for load/perf testing when infrastructure exists.

---

## 6. Robustness Metrics (Specification Targets)

From **「6. 鲁棒性指标」** in `D:\data\测试指标体系.md`:

| Scenario | Target (spec) |
|----------|----------------|
| OCR after scan preprocessing | 识别率 >80% |
| Tables (merged cells, cross-page) | 准确率 >85% |
| Corrupt single page | 100% 不中断全流程 |
| Empty / image-only / oversized docs | 异常文档处理 >95% |
| Mixed Chinese/English bid text | 多语言混排 >90% |

---

## 7. Rollout and Alerting (From Spec, Not Implemented Here)

`D:\data\测试指标体系.md` also defines:

- **测试优先级** — Week 1–4 focus (chunking → recall → hybrid tuning → end-to-end RAG report).
- **指标告警阈值** — green/yellow/red bands for 分块完整率, Recall@5, 幻觉率, 引用召回率, 端到端P95.

Treat these as **evaluation and release-governance checklists** when implementing CI or staging gates; they are not executable in the doc-only tree.

---

## Test Framework (Repository Reality)

**Runner:** Not detected.

**Run commands:** N/A until a codebase and `pyproject.toml` / `package.json` with test scripts exist.

**Prescriptive next step for implementers:** When adding code under a future repo root, wire **golden-set retrieval tests**, **chunking regression fixtures**, and **LLM-judge harnesses** to the tables in `D:\data\测试指标体系.md`, and keep product NFRs in `D:\data\01需求概要设计文档.md` section 4.1 aligned but separately tracked.

---

*Testing analysis: 2026-04-13*
