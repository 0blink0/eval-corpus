# Requirements: 文档解析工具分块指标对比实验

**Defined:** 2026-04-13  
**Core Value:** 同一套分块与评测口径下对比 PaddleOCR、GLM-OCR、MinerU 的分块质量，产出可复现的对比表与分项结果。

## v1 Requirements

### 语料与配置 (CORP)

- [x] **CORP-01**: 实验可通过配置（CLI 参数或环境变量）指定语料根目录，默认文档中约定支持 **北燃热力宣传品采购归档资料** 的实际路径
- [x] **CORP-02**: 生成语料清单（文件路径、格式、页数/大小哈希可选），运行前校验可读
- [x] **CORP-03**: 提供「黄金统计」输出：原文字符数、表格数量（若可检测）、页数等，供覆盖完整率与表格保持率分母使用

### 统一表示与分块 (CHUNK)

- [ ] **CHUNK-01**: 定义并实现统一中间表示 `ParsedBlock`（类型、文本/表格序列化、页码、标题路径）
- [ ] **CHUNK-02**: 实现统一分块器：目标块长 300–1000 字符、表格优先原子块、句界优先切分、可配置重叠 10–20%（默认 15% 于文本块）
- [ ] **CHUNK-03**: 同一分块器对三套工具归一后的 `ParsedBlock[]` 执行，保证对比公平

### 工具适配 (ADPT)

- [ ] **ADPT-01**: PaddleOCR 链路：从语料到 `ParsedBlock[]` 的可运行适配（版本与依赖写入 README/lock）
- [ ] **ADPT-02**: GLM-OCR 链路：同上
- [ ] **ADPT-03**: MinerU 链路：同上

### 指标计算 (METR)

- [ ] **METR-01**: **覆盖完整率**：分块还原文本与原提取全文长度比及缺失诊断
- [ ] **METR-02**: **块长度达标率**：300–1000 字符占比统计
- [ ] **METR-03**: **边界准确率** / 硬切比例：边界落在句末/段末 vs 硬切
- [ ] **METR-04**: **表格保持率**：完整表格块数 / 原表格数（原表格数来自归一阶段标注）
- [ ] **METR-05**: **重叠合理率**：相邻文本块重叠比例落在 10–20% 的占比
- [ ] **METR-06**: **元数据完整率**：chunk 同时具备页码与标题路径（或可解释缺失原因）的占比
- [ ] **METR-07**: **语义完整率**：按 PROJECT 约定执行（规则近似 + 可复现抽检脚本，支持接入 LLM-as-Judge 可选）

### 报告与产物 (RPT)

- [ ] **RPT-01**: 生成**总对比表**（三工具 × 七指标，附目标阈值列）
- [ ] **RPT-02**: 生成**每工具明细**（原始指标 JSON/CSV + Markdown 或 HTML 摘要）
- [ ] **RPT-03**: 单次运行写入时间戳、工具版本、Git commit（若有），保证可追溯

### 测试数据与规模化 (DATA)

- [ ] **DATA-01**: 提供合成或小样本生成器，用于无真料时的回归与 CI 烟测
- [ ] **DATA-02**: 支持批处理模式（目录递归），便于云主机上扩跑

## v2 Requirements

### 自动化增强

- **AUTO-01**: 一键 Docker/Poetry 镜像锁定各解析依赖
- **AUTO-02**: 与 §2 检索指标打通的导出格式（chunk 元数据兼容向量库）

## Out of Scope

| Feature | Reason |
|---------|--------|
| 完整审查平台业务 | 见 PROJECT.md；本实验仅为解析+分块评测 |
| §2–§6 全量指标 | 本轮聚焦 §1；其余另立项 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CORP-01 | Phase 1 | Done |
| CORP-02 | Phase 1 | Done |
| CORP-03 | Phase 1 | Done |
| CHUNK-01 | Phase 2 | Pending |
| CHUNK-02 | Phase 2 | Pending |
| CHUNK-03 | Phase 2 | Pending |
| ADPT-01 | Phase 3 | Pending |
| ADPT-02 | Phase 3 | Pending |
| ADPT-03 | Phase 3 | Pending |
| METR-01 | Phase 4 | Pending |
| METR-02 | Phase 4 | Pending |
| METR-03 | Phase 4 | Pending |
| METR-04 | Phase 4 | Pending |
| METR-05 | Phase 4 | Pending |
| METR-06 | Phase 4 | Pending |
| METR-07 | Phase 4 | Pending |
| RPT-01 | Phase 5 | Pending |
| RPT-02 | Phase 5 | Pending |
| RPT-03 | Phase 5 | Pending |
| DATA-01 | Phase 5 | Pending |
| DATA-02 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-13*  
*Last updated: 2026-04-13 after initial definition*
