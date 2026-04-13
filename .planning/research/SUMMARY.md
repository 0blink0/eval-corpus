# Research Summary: 文档解析与分块评测（2026）

**Scope:** 支撑「PaddleOCR / GLM-OCR / MinerU + 统一分块」对比实验的栈与风险摘要。

## Stack（实验推荐）

| 层 | 建议 | 说明 |
|----|------|------|
| 语言 | Python 3.10+ | 三工具生态以 Python 为主；Linux 云主机更省心 |
| 编排 | CLI（Typer/argparse）+ 可选 Makefile | 批跑与迁云 |
| OCR/解析 | PaddleOCR、智谱 GLM-OCR、MinerU | 固定版本号写入 lock/requirements |
| 指标 | 自研 + 可选 OpenAI 兼容 API | 语义完整率抽检需 LLM 时走可配置 endpoint |
| 输出 | JSON/CSV + Jinja2/Markdown 模板 | 对比表与明细 |

## Table Stakes（本实验必须具备）

- 可重复运行（固定 seed、记录版本）
- 统一 IR，不在「工具原生 chunk」上直接比
- 原始招投标资料不默认入库

## Pitfalls（需在各 Phase 防范）

1. **版式差异**：MinerU 偏 PDF 结构化；Paddle 偏检测识别；GLM-OCR 偏端到端文档理解——归一时要显式定义表格与标题从何处来。  
2. **分母不一致**：「原表格数」若某工具未检出表格，表格保持率需记录为 N/A 或 0 并单独说明。  
3. **语义完整率**：全自动无金标时，应用「句界 + 抽检」并报告置信区间，避免伪精确。  
4. **性能**：大批量 PDF 优先 GPU Linux；Windows 开发可只做小样本联调。

## Features（对 REQUIREMENTS 的映射提示）

- 表结构保留能力：MinerU/GLM-OCR 往往强于纯 OCR；Paddle 需版面+表格模块组合。  
- 元数据：页码与标题——MinerU/文档模型通常更丰富，应在 IR 中显式字段承载。

---
*Synthesized: 2026-04-13 for new-project bootstrap*
