# Roadmap: 文档解析工具分块指标对比实验

## Overview

从语料与配置规范化出发，建立统一文档块表示与分块策略；依次接入 PaddleOCR、GLM-OCR、MinerU；实现 §1 全部七项分块指标；最后产出对比表、分工具明细与可生成测试数据，并支持批处理迁云。

## Phases

- [x] **Phase 1: 评测基座与语料规范** — 可配置语料路径、清单与黄金统计
- [ ] **Phase 2: 统一 IR 与分块器** — ParsedBlock + 300–1000 字策略与重叠
- [ ] **Phase 3: 三工具解析适配** — PaddleOCR / GLM-OCR / MinerU 归一
- [ ] **Phase 4: 分块指标引擎** — §1 七项指标计算与语义抽检接口
- [ ] **Phase 5: 报告、测试数据与批跑** — 对比表、明细、合成数据、规模化入口

## Phase Details

### Phase 1: 评测基座与语料规范
**Goal**: 任何人克隆仓库后可通过配置指向 **北燃热力宣传品采购归档资料**（或等价目录）并生成可校验的语料清单与黄金统计。  
**Depends on**: Nothing (first phase)  
**Requirements**: CORP-01, CORP-02, CORP-03  
**Success Criteria** (what must be TRUE):
  1. 指定根目录后，工具列出待处理文件且缺失路径时给出明确错误
  2. 输出语料清单工件（JSON/CSV 任一 + 人类可读摘要）
  3. 输出黄金统计（至少含总字符数、文件数；表格/页数在可解析时填入）
**Plans**: 3 plans  
**UI hint**: no

Plans:
- [x] 01-01: 配置模块（CLI/env）与路径校验
- [x] 01-02: 语料扫描与清单生成
- [x] 01-03: 黄金统计与原始全文基准抽取（供后续覆盖率）

### Phase 2: 统一 IR 与分块器
**Goal**: 实现 `ParsedBlock` 与统一分块策略（结构优先、表格原子、句界、10–20% 重叠）。  
**Depends on**: Phase 1  
**Requirements**: CHUNK-01, CHUNK-02, CHUNK-03  
**Success Criteria** (what must be TRUE):
  1. 给定手工构造的 `ParsedBlock[]`，分块输出满足长度与重叠配置的可测用例
  2. 表格块不被非配置策略随意撕开（单元测试覆盖）
  3. 分块结果带齐 chunk 级元数据字段（页、标题路径、tool 占位）
**Plans**: 3 plans  
**UI hint**: no

Plans:
- [ ] 02-01: IR 模型与序列化
- [ ] 02-02: 合并/切分与重叠实现
- [ ] 02-03: 单元测试与固定夹具

### Phase 3: 三工具解析适配
**Goal**: 三条链路从真实文件到 `ParsedBlock[]` 可运行，并记录版本信息。  
**Depends on**: Phase 2  
**Requirements**: ADPT-01, ADPT-02, ADPT-03  
**Success Criteria** (what must be TRUE):
  1. 对至少一份样例（含合成样例），三工具均可跑通至 `ParsedBlock[]`
  2. 各适配器输出记录 parser 名称与版本/模型标识
  3. 失败时错误信息可定位到文件与阶段
**Plans**: 3 plans  
**UI hint**: no

Plans:
- [ ] 03-01: PaddleOCR 适配与样例验证
- [ ] 03-02: GLM-OCR 适配与样例验证
- [ ] 03-03: MinerU 适配与样例验证

### Phase 4: 分块指标引擎
**Goal**: 实现《测试指标体系》§1 全部七项指标及与目标阈值对照。  
**Depends on**: Phase 3  
**Requirements**: METR-01–METR-07  
**Success Criteria** (what must be TRUE):
  1. 每个指标有明确输入、计算公式说明与代码实现
  2. 语义完整率路径包含可复现抽检（规则或可选 LLM）
  3. 对同一批样例输出可重复的数值结果
**Plans**: 3 plans  
**UI hint**: no

Plans:
- [ ] 04-01: 结构类指标（覆盖、长度、边界、表格、重叠、元数据）
- [ ] 04-02: 语义完整率与抽检协议
- [ ] 04-03: 指标聚合与阈值对照表

### Phase 5: 报告、测试数据与批跑
**Goal**: 自动生成总对比表、分工具明细；提供合成数据生成与目录批处理。  
**Depends on**: Phase 4  
**Requirements**: RPT-01, RPT-02, RPT-03, DATA-01, DATA-02  
**Success Criteria** (what must be TRUE):
  1. 一次命令产出对比总表 + 三份工具明细
  2. 合成数据生成器可在无真料时跑通全流水线（烟测）
  3. 文档说明云主机扩跑步骤（依赖安装、批处理入口）
**Plans**: 3 plans  
**UI hint**: no

Plans:
- [ ] 05-01: Markdown/HTML/CSV/JSON 报告模板与导出
- [ ] 05-02: 合成 PDF/扫描样例或轻量生成器
- [ ] 05-03: 批处理 CLI 与运行手册（含迁云说明）

## Progress

**Execution Order:** 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. 评测基座与语料规范 | 3/3 | Complete | 2026-04-13 |
| 2. 统一 IR 与分块器 | 0/3 | Not started | - |
| 3. 三工具解析适配 | 0/3 | Not started | - |
| 4. 分块指标引擎 | 0/3 | Not started | - |
| 5. 报告、测试数据与批跑 | 0/3 | Not started | - |
