# Phase 3: 三工具解析适配 - Research

**Researched:** 2026-04-13  
**Domain:** PaddleOCR / GLM-OCR / MinerU 统一适配到 `ParsedBlock[]`  
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- 用户要求“按照推荐的来”，因此以下 5 个讨论领域全部采用推荐项。

### 适配器接口与错误模型

- **D-30:** 三工具统一暴露接口：`parse_to_blocks(file_path: Path, config: AdapterConfig) -> list[ParsedBlock]`。
- **D-31:** 统一错误模型（可序列化）：`stage`, `file`, `tool`, `message`, `raw_error`（可选）; 其中 `stage` 固定枚举（如 `load` / `parse` / `normalize` / `validate`）。
- **D-32:** CLI 层仅负责编排与汇总，不直接处理工具私有输出结构。

### 输出映射到 IR 的策略

- **D-33:** 先定义“最低一致语义”并强制三工具对齐：
  - `type ∈ {title, paragraph, table, other}`
  - `text` 必填（table 为线性化文本）
  - `page` 缺失时 `null`
  - `heading_path` 缺失时 `[]`
- **D-34:** 工具特化逻辑允许存在，但必须在 adapter 内部消化，出口只能是统一 `ParsedBlock[]`。
- **D-35:** `parser_tool` 在 Phase 3 由适配器写入真实工具名（替换 Phase 2 的 `unknown` 占位）。

### 版本与模型标识记录

- **D-36:** 版本/模型标识在**文件级或运行级**强制记录：`tool_name`, `tool_version`, `model_id`。
- **D-37:** block 级保持 `parser_tool` 即可，不强制每个 block 复制 version/model，避免冗余。

### 失败策略与可观测性

- **D-38:** 默认 `continue-on-error`：单文件失败不终止整批，汇总失败清单。
- **D-39:** 提供 `--fail-fast` 开关以支持调试与 CI 快速失败。
- **D-40:** 错误输出至少包含：文件路径、工具名、阶段（stage）、简明消息；debug 模式附 `raw_error`。

### 样例集与验收口径

- **D-41:** 采用最小三件套夹具（每工具至少覆盖同一套输入类型）：
  1) 文本型 PDF
  2) 扫描型 PDF
  3) 含表格样例
- **D-42:** 夹具目录建议固定为 `tests/fixtures/adapters/`，先保证最小覆盖，再扩容。
- **D-43:** 验收以“同一批样例三工具都能产出合法 `ParsedBlock[]` 或可定位错误”为准。

### Claude's Discretion

- 每个工具 adapter 的内部模块命名与文件拆分（如 `adapters/paddle.py` / `adapters/glm.py` / `adapters/mineru.py`）可由实现阶段按代码可维护性决定。
- 版本探测优先级（CLI 命令探测 / SDK 常量 / 手动配置回填）可按工具可用性选最稳方案，但输出字段名须一致。

### Deferred Ideas (OUT OF SCOPE)

- 更高级的模型路由与多模型 fallback 策略（可在后续 phase 增强）。
- 工具侧性能优化与并发调度细化（本阶段先保证正确性与可观测性）。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADPT-01 | PaddleOCR 链路从语料到 `ParsedBlock[]` 可运行 | 定义 Paddle 适配器边界、输出映射、错误分层与版本记录策略；对齐现有 `ParsedBlock` 模型字段 [VERIFIED: `src/eval_corpus/ir_models.py`] [CITED: https://paddlepaddle.github.io/PaddleOCR/latest/en/quick_start.html] |
| ADPT-02 | GLM-OCR 链路从语料到 `ParsedBlock[]` 可运行 | 使用 `model="glm-ocr"` 的标准调用，封装 API 输出到统一 IR，并保留 `tool/model` 元数据 [CITED: https://docs.z.ai/guides/vlm/glm-ocr] |
| ADPT-03 | MinerU 链路从语料到 `ParsedBlock[]` 可运行 | 使用 `mineru -p <input> -o <output>` 或 `mineru-api` 输出，适配器内做结构归一化 [CITED: https://opendatalab.github.io/MinerU/usage/quick_usage/] |
</phase_requirements>

## Project Constraints (from .cursor/rules/)

- 未发现 `.cursor/rules/` 目录，当前无额外仓库级硬约束文件 [VERIFIED: glob `.cursor/rules/**/*.md` returned 0 files]。
- 未发现 `.cursor/skills/` 与 `.agents/skills/` 项目级技能索引 [VERIFIED: glob `.cursor/skills/*/SKILL.md` and `.agents/skills/*/SKILL.md` returned 0 files]。

## Summary

Phase 3 的计划核心不是“再造一套解析框架”，而是把三种工具的异构输出统一压平到既有 `ParsedBlock` 契约，并确保失败可观测、批处理可继续、元数据可追溯 [VERIFIED: `.planning/phases/03-adapters/03-CONTEXT.md`] [VERIFIED: `src/eval_corpus/ir_models.py`]。仓库已经具备统一 IR/chunk 管线：`ParsedBlock` 模型、`chunk_blocks`、`chunk` CLI 命令都已存在，可直接作为 adapter 出口约束 [VERIFIED: `src/eval_corpus/ir_models.py`, `src/eval_corpus/chunker.py`, `src/eval_corpus/cli.py`]。

三工具接入建议采用“端口-适配器”模式：每个工具单独适配模块，仅输出 `list[ParsedBlock]` 或标准化错误对象；CLI 仅做编排、聚合与退出码管理（满足 D-32, D-38, D-39）[VERIFIED: `.planning/phases/03-adapters/03-CONTEXT.md`]。这样可避免工具私有结构泄漏到下游，从而保护 Phase 4 指标口径的一致性 [ASSUMED]。

环境审计显示当前开发机尚未安装 `paddleocr`、`zai-sdk`、`mineru`，因此 Phase 3 计划必须把“依赖安装 + 可用性探测 + 失败降级路径（至少可报可定位错误）”放到 Wave 0，不能默认依赖可用 [VERIFIED: local probe `importlib.util.find_spec` results on 2026-04-13]。

**Primary recommendation:** 采用“统一接口 + 统一错误模型 + 统一 fixture + 运行级元数据记录”的最小闭环先打通 ADPT-01~03，再逐步增强性能和高级路由 [VERIFIED: D-30..D-43].

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.12.8 | 适配器与 CLI 运行时 | 与项目 `>=3.11` 要求兼容 [VERIFIED: `python --version`, `pyproject.toml`] |
| pydantic | 2.11.10 (env), `>=2.7.0` (project) | `ParsedBlock` 校验和 IR 边界收口 | 现有 IR 已使用 BaseModel，复用成本最低 [VERIFIED: `src/eval_corpus/ir_models.py`, `pyproject.toml`] |
| Typer | 0.20.0 (env), `>=0.9.0` (project) | 扩展 adapter 子命令与参数 | 现有 CLI 已采用 Typer [VERIFIED: `src/eval_corpus/cli.py`, `pyproject.toml`] |
| PaddleOCR | 3.4.0 (PyPI latest) | 本地 OCR / 文档解析链路 | 官方提供 Python API 与 CLI；适合本地批处理 [VERIFIED: `pip index versions paddleocr`] [CITED: https://paddlepaddle.github.io/PaddleOCR/latest/en/quick_start.html] |
| GLM-OCR API | model=`glm-ocr` | 云端 OCR / 布局解析链路 | 官方 API 明确模型名和 layout parsing 接口 [CITED: https://docs.z.ai/guides/vlm/glm-ocr] |
| MinerU | 3.0.9 (PyPI latest) | 文档解析到结构化输出链路 | 官方提供 CLI 与 API 两种模式 [VERIFIED: `pip index versions mineru`] [CITED: https://opendatalab.github.io/MinerU/usage/quick_usage/] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| zai-sdk | 0.2.2 (PyPI latest) | GLM-OCR Python SDK 调用 | 选择 SDK 方式接入 GLM-OCR 时 [VERIFIED: `pip index versions zai-sdk`] [CITED: https://docs.z.ai/guides/vlm/glm-ocr] |
| pytest | 9.0.3 | 适配器行为与错误模型测试 | 夹具回归、fail-fast/continue-on-error 验证 [VERIFIED: `pytest --version`] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 每工具独立输出格式 | 强制统一 `ParsedBlock[]` 出口 | 统一出口实现成本更高，但保证跨工具公平对比（D-34）[VERIFIED: D-34] |
| 仅保存 `parser_tool` | block 级额外存 `tool_version/model_id` | 更易追溯但冗余更高；D-37 已锁定不强制 [VERIFIED: D-36, D-37] |
| CLI 直接消费工具原始 JSON | adapter 内吸收工具差异再输出 IR | 前者快但耦合重；后者维护性更高 [VERIFIED: D-32, D-34] |

**Installation:**
```bash
pip install paddleocr mineru zai-sdk
```

**Version verification:**  
- `pip index versions paddleocr` -> `3.4.0` [VERIFIED: command output on 2026-04-13]  
- `pip index versions mineru` -> `3.0.9` [VERIFIED: command output on 2026-04-13]  
- `pip index versions zai-sdk` -> `0.2.2` [VERIFIED: command output on 2026-04-13]

## Architecture Patterns

### Recommended Project Structure
```text
src/eval_corpus/
├── adapters/
│   ├── base.py            # Adapter protocol + AdapterConfig + AdapterError
│   ├── paddle.py          # PaddleOCR -> ParsedBlock[]
│   ├── glm.py             # GLM-OCR API -> ParsedBlock[]
│   └── mineru.py          # MinerU CLI/API -> ParsedBlock[]
├── adapter_registry.py    # tool name -> adapter factory
├── adapter_runner.py      # batch orchestration, continue-on-error/fail-fast
└── cli.py                 # add parse/adapt command, only orchestration
tests/
├── fixtures/adapters/     # text/scanned/table minimal triad
└── test_adapters_*.py
```
[ASSUMED]

### Pattern 1: Adapter Port + Normalizer
**What:** 每个工具实现同一 `parse_to_blocks()`，内部做工具输出到 `ParsedBlock` 的映射。  
**When to use:** 需要稳定比较不同解析器质量时。  
**Example:**
```python
class ParserAdapter(Protocol):
    def parse_to_blocks(self, file_path: Path, config: AdapterConfig) -> list[ParsedBlock]:
        ...
```
Source: [VERIFIED: D-30]

### Pattern 2: Stage-based Error Envelope
**What:** 所有失败转换为统一 `AdapterError(stage,file,tool,message,raw_error?)`。  
**When to use:** 批处理场景要定位故障并可继续执行时。  
**Example:**
```python
try:
    raw = call_tool(file_path)
except Exception as e:
    raise AdapterError(stage="parse", file=str(file_path), tool="paddleocr", message=str(e), raw_error=repr(e))
```
Source: [VERIFIED: D-31, D-40]

### Pattern 3: Runtime-level Metadata Record
**What:** 每次运行记录 `tool_name/tool_version/model_id`，block 只保留 `parser_tool`。  
**When to use:** 需要可追溯且避免 IR 冗余时。  
**Example:**
```python
run_meta = {"tool_name": tool, "tool_version": ver, "model_id": model}
block = ParsedBlock(..., parser_tool=tool)
```
Source: [VERIFIED: D-35, D-36, D-37]

### Anti-Patterns to Avoid
- **在 CLI 中写工具私有解析逻辑：** 违背 D-32，测试与维护会失控 [VERIFIED: D-32]。
- **把工具原始异常直接外抛：** 会破坏统一可观测性与批处理汇总 [VERIFIED: D-31, D-40]。
- **fixture 只测单工具或单文档类型：** 无法满足 D-41~D-43 的可比性验收 [VERIFIED: D-41, D-43]。

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OCR 引擎 | 自研 OCR 识别和布局模型 | PaddleOCR / GLM-OCR / MinerU 官方能力 | 领域复杂度高，维护成本不可控 [CITED: 官方文档链接见 Sources] |
| JSON 字段校验 | 手写 if/try 校验树 | `ParsedBlock` Pydantic 校验 | 现有 IR 已标准化，错误信息一致 [VERIFIED: `src/eval_corpus/ir_models.py`] |
| 多工具失败追踪 | 各工具各自错误格式 | 统一 `stage/file/tool/message/raw_error` | 支持批处理汇总和 CI 判定 [VERIFIED: D-31, D-38, D-40] |

**Key insight:** 这阶段最容易“手搓过度”的点是私有输出映射和错误处理；应最大化复用既有 IR/CLI 骨架，把复杂性关在 adapter 内 [VERIFIED: `src/eval_corpus/cli.py`, `src/eval_corpus/ir_models.py`] [ASSUMED].

## Common Pitfalls

### Pitfall 1: 工具版本不可追溯
**What goes wrong:** 结果可复现性差，后续对比无法解释偏差。  
**Why it happens:** 只记录 `parser_tool`，未记录 `tool_version/model_id`。  
**How to avoid:** 每次运行输出 run-level 元数据清单（D-36, D-37）。  
**Warning signs:** 同文件复跑结果变化但无版本证据。  
[VERIFIED: D-36, D-37]

### Pitfall 2: continue-on-error 实现成“静默吞错”
**What goes wrong:** 批处理继续了，但不知道哪些文件失败。  
**Why it happens:** 未落实 D-40 的最小错误字段。  
**How to avoid:** 失败项必须落盘并包含 `file/tool/stage/message`，debug 时附 `raw_error`。  
**Warning signs:** 汇总只给失败数量，无明细。  
[VERIFIED: D-38, D-40]

### Pitfall 3: 三工具 mapping 语义不一致
**What goes wrong:** 指标阶段对比失真（同类内容映射到不同 `type`）。  
**Why it happens:** 未先定义最低一致语义（D-33）。  
**How to avoid:** 先写 mapping contract，再实现各 adapter。  
**Warning signs:** 同 fixture 在不同工具中 `type/page/heading_path` 差异异常。  
[VERIFIED: D-33, D-34]

## Code Examples

Verified patterns from official and local sources:

### 现有 `ParsedBlock` 契约（适配器出口必须对齐）
```17:24:src/eval_corpus/ir_models.py
class ParsedBlock(BaseModel):
    type: BlockType
    text: str
    page: int | None = None
    heading_path: list[str] = Field(default_factory=list)
    parser_tool: str = "unknown"
    source_file: str = "unknown"
    cells: list[list[str]] | None = None
```

### PaddleOCR Python quick start pattern
```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False)
result = ocr.predict("doc.png")
```
Source: [CITED: https://paddlepaddle.github.io/PaddleOCR/latest/en/quick_start.html]

### GLM-OCR API pattern
```bash
curl --request POST 'https://api.z.ai/api/paas/v4/layout_parsing' \
  --header 'Authorization: Bearer <api-key>' \
  --header 'Content-Type: application/json' \
  --data-raw '{"model":"glm-ocr","file":"https://.../input.png"}'
```
Source: [CITED: https://docs.z.ai/guides/vlm/glm-ocr]

### MinerU CLI pattern
```bash
mineru -p <input_path> -o <output_path>
```
Source: [CITED: https://opendatalab.github.io/MinerU/usage/quick_usage/]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase 2 使用 `parser_tool="unknown"` 占位 | Phase 3 适配器写入真实工具名并记录运行级 version/model | 2026-04-13（D-35~D-37） | 评测结果可追溯、可复现 [VERIFIED: D-35, D-36, D-37] |
| 单工具脚本式处理 | 三工具统一 adapter 合同 + 统一错误模型 | 2026-04-13（D-30~D-31） | 计划可并行推进且对齐验收口径 [VERIFIED: D-30, D-31, D-43] |

**Deprecated/outdated:**
- “直接在 CLI 里分支处理每个工具原始输出”不再推荐，违背 D-32/D-34 [VERIFIED: D-32, D-34]。

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | 推荐 `adapters/base.py + registry + runner` 的模块拆分 | Architecture Patterns | 仅影响任务拆分与维护性，不影响功能目标 |
| A2 | 运行级元数据可落在 manifest/report JSON 而非 chunk 文件 | Architecture Patterns | 若后续要求单文件自包含，需补充输出字段 |
| A3 | GLM-OCR 在项目环境中优先走 HTTP API 而非本地推理 | Standard Stack | 若网络/鉴权受限，需改为 mock 或跳过策略 |

## Open Questions (RESOLVED)

1. **GLM-OCR 的企业网络访问与鉴权策略（RESOLVED）**
   - What we know: 官方接口与模型名已明确（`glm-ocr`）[CITED: https://docs.z.ai/guides/vlm/glm-ocr]
   - What's unclear: 当前执行环境是否有可用 API key 与出网权限
   - Recommendation: 计划中加入 `GLM_API_KEY` 检查与“缺失即可定位失败”路径
   - **RESOLVED:** 规划中固定：无 `GLM_API_KEY` 或网络不可达时，返回标准化 `AdapterError(stage=parse, tool=glm-ocr, file=...)`，并遵循 D-38 continue-on-error；`--fail-fast` 时立即停止。

2. **MinerU 输出 JSON 的字段稳定性（RESOLVED）**
   - What we know: 官方支持 CLI/API，多种输出形态 [CITED: https://opendatalab.github.io/MinerU/usage/quick_usage/]
   - What's unclear: 当前锁定版本的字段是否与适配器映射假设一致
   - Recommendation: Wave 0 先用最小 fixture 固化样例并写 golden mapping test
   - **RESOLVED:** 以 `tests/fixtures/adapters/` 三件套样例先固化当前版本输出映射；字段漂移统一在 adapter 内兜底，不允许泄漏到 `ParsedBlock[]` 出口（D-34）。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | 所有 adapter/CLI 逻辑 | ✓ | 3.12.8 | — |
| pydantic | `ParsedBlock` 统一校验 | ✓ | 2.11.10 | 无（阻塞） |
| Typer | CLI 编排 | ✓ | 0.20.0 | 无（阻塞） |
| paddleocr | ADPT-01 | ✗ | — | 若缺失：输出标准化 `load` 阶段错误并继续批处理 |
| zai-sdk / GLM API 访问条件 | ADPT-02 | ✗（SDK 未安装；API key 未验证） | — | 若缺失：输出标准化 `load/parse` 错误并继续批处理 |
| mineru | ADPT-03 | ✗ | — | 若缺失：输出标准化 `load` 阶段错误并继续批处理 |

Evidence: [VERIFIED: local probes `python --version`, `pytest --version`, importlib `find_spec` for `paddleocr/zai/mineru` on 2026-04-13]

**Missing dependencies with no fallback:**
- 无“完全阻塞”项；因 D-38 锁定了 continue-on-error，可先完成框架与错误模型 [VERIFIED: D-38]。

**Missing dependencies with fallback:**
- `paddleocr`, `zai-sdk`(或 GLM API 鉴权), `mineru` 均可先走“可定位失败”路径，待环境补齐后启用真实解析。

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 [VERIFIED: `pytest --version`] |
| Config file | `pyproject.toml` [VERIFIED: `pyproject.toml`] |
| Quick run command | `pytest -q tests/test_adapters_contract.py -x` [ASSUMED: new file] |
| Full suite command | `pytest -q` [VERIFIED: existing project test layout] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ADPT-01 | Paddle adapter 对同一 fixture 输出合法 `ParsedBlock[]` 或标准化错误 | unit/integration | `pytest -q tests/test_adapters_paddle.py -x` | ❌ Wave 0 |
| ADPT-02 | GLM adapter 对同一 fixture 输出合法 `ParsedBlock[]` 或标准化错误 | unit/integration | `pytest -q tests/test_adapters_glm.py -x` | ❌ Wave 0 |
| ADPT-03 | MinerU adapter 对同一 fixture 输出合法 `ParsedBlock[]` 或标准化错误 | unit/integration | `pytest -q tests/test_adapters_mineru.py -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest -q tests/test_adapters_contract.py -x` [ASSUMED]
- **Per wave merge:** `pytest -q`
- **Phase gate:** 适配器相关测试 + 全量测试均为 green，再进入 `/gsd-verify-work` [ASSUMED]

### Wave 0 Gaps
- [ ] `tests/fixtures/adapters/` 三件套最小样例（文本 PDF / 扫描 PDF / 表格样例）— D-41/D-42
- [ ] `tests/test_adapters_contract.py` — 统一接口、错误模型、continue-on-error/fail-fast
- [ ] `tests/test_adapters_paddle.py` / `tests/test_adapters_glm.py` / `tests/test_adapters_mineru.py`
- [ ] `src/eval_corpus/adapters/` 模块骨架与注册机制

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes (GLM API key) | 环境变量注入，不硬编码密钥 [ASSUMED] |
| V3 Session Management | no | N/A（非长会话系统） [ASSUMED] |
| V4 Access Control | no | N/A（本 phase 为本地 CLI/批处理） [ASSUMED] |
| V5 Input Validation | yes | `ParsedBlock`/config 走 Pydantic 校验 [VERIFIED: `src/eval_corpus/ir_models.py`] |
| V6 Cryptography | yes (传输层) | 使用官方 HTTPS API，不自实现加密 [CITED: https://docs.z.ai/guides/vlm/glm-ocr] |

### Known Threat Patterns for Python adapter stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| 恶意文档触发解析器异常 | DoS | 超时/异常归一化到 `stage` 错误，批处理中断策略可控 [VERIFIED: D-31, D-38, D-39] |
| API key 泄漏到日志 | Information Disclosure | 默认日志不输出敏感字段，debug 仅输出脱敏 raw_error [ASSUMED] |
| 工具输出结构漂移导致误映射 | Tampering | 以 fixture + schema 测试锁定映射，未知字段忽略或告警 [ASSUMED] |

## Sources

### Primary (HIGH confidence)
- Repo/planning artifacts:
  - `.planning/phases/03-adapters/03-CONTEXT.md`
  - `.planning/phases/02-ir/02-CONTEXT.md`
  - `.planning/phases/02-ir/02-RESEARCH.md`
  - `.planning/REQUIREMENTS.md`
  - `.planning/config.json`
  - `src/eval_corpus/ir_models.py`
  - `src/eval_corpus/chunker.py`
  - `src/eval_corpus/chunk_io.py`
  - `src/eval_corpus/cli.py`
  - `pyproject.toml`
- Tool/runtime verification:
  - `python --version`
  - `pytest --version`
  - `pip index versions paddleocr`
  - `pip index versions mineru`
  - `pip index versions zai-sdk`

### Secondary (MEDIUM confidence)
- [PaddleOCR Quick Start](https://paddlepaddle.github.io/PaddleOCR/latest/en/quick_start.html)
- [GLM-OCR Guide](https://docs.z.ai/guides/vlm/glm-ocr)
- [MinerU Quick Usage](https://opendatalab.github.io/MinerU/usage/quick_usage/)

### Tertiary (LOW confidence)
- 无。

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - 版本已核验，但三工具在本机尚未安装。
- Architecture: HIGH - D-30..D-43 已锁定核心设计边界。
- Pitfalls: MEDIUM - 风险明确，但需实际接入后验证细节。

**Research date:** 2026-04-13  
**Valid until:** 2026-05-13（30 天）

