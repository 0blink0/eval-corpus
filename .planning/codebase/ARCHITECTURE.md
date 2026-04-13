# Architecture

**Analysis Date:** 2026-04-13

## Pattern Overview

**Overall (planned):** B/S 分层 + 可扩展多 Agent 编排（Coordinator 调度专业 Agent，共享 Skill/Tools，多类数据存储）。

**Key Characteristics (planned):**
- API-first：对外 REST API，便于第三方集成与后续 C/S 客户端替换 UI。
- 编排层：主控 Agent 负责任务分解与结果汇总，专业 Agent 按职责边界处理业务。
- 数据与检索：关系数据、向量检索、图查询与文件存储分工；知识库类型与 Agent 映射明确。

**Repository reality:** 当前仓库无可运行应用；架构仅以需求文档形式存在于 `D:\data\01需求概要设计文档.md`。实现与部署形态尚未落地。

## Layers

**Presentation (planned):**
- Purpose: 浏览器端人机交互。
- Location: 规划中为 Streamlit Web UI（文档图示为 `Web UI (Streamlit)`）。
- Contains: 页面、上传与结果展示、与后端 API 的交互。
- Depends on: `API Gateway (FastAPI)` 暴露的 REST 接口。
- Used by: 终端用户（Chrome、Edge、Firefox 等现代浏览器）。

**API / Gateway (planned):**
- Purpose: 统一 HTTP 入口、鉴权（如 API Key）、路由到 Agent 编排与工具。
- Location: 规划中为 `FastAPI`（`D:\data\01需求概要设计文档.md` 第 2.2、4.4 节）。
- Contains: REST 端点、与 Coordinator 的衔接。
- Depends on: 编排层与共享工具实现。
- Used by: Web UI、外部第三方系统。

**Orchestration (planned):**
- Purpose: 意图识别、任务分解、专业 Agent 调度、结果汇总。
- Location: 概念上位于 API Gateway 之下；技术选型为 LangGraph `StateGraph`（Coordinator）。
- Contains: Coordinator Agent 工作流、状态与分支。
- Depends on: 各专业 Agent、共享 Skill、Tools。
- Used by: 所有经网关进入的业务请求。

**Specialist Agents (planned):**
- Purpose: 按职责边界完成子任务（文档解析、合规审查、比对分析、资质核验、风险识别、辅助评标、专家抽取、档案管理、统计分析等；扩展含制度合规）。
- Location: 规划中为 LangGraph Agent 实例（`D:\data\01需求概要设计文档.md` 第 2.3 节）。
- Contains: 各 Agent 的节点逻辑与调用序列。
- Depends on: 共享 Skill、Tools、知识库与存储。
- Used by: Coordinator Agent。

**Shared Skills & Tools (planned):**
- Purpose: 可复用能力与底层调用封装。
- Location: Skill 为 Python 模块；Tools 为 FastAPI Tools（同文档 2.3.1）。
- Contains: 如 `law_retrieval`、`report_generation`、`notification`、`policy_retrieval`、`similarity_calculation`、`graph_query` 等（文档 2.3.3）。
- Depends on: 数据库、向量库、图库、文件存储、外部 API。
- Used by: 多个专业 Agent。

**Data & Knowledge (planned):**
- Purpose: 持久化、检索与证据支撑。
- Location: PostgreSQL（关系）、Qdrant（向量）、Neo4j（图）、文件存储（文档 2.2 图）；知识库类型与 Agent 映射见文档 2.3.4。
- Contains: 业务实体、向量索引、关联图谱、原始与解析文件。
- Depends on: 部署环境与网络策略（私有化、信创备选见文档附录）。
- Used by: Skills/Tools 与各 Agent。

## Data Flow

**典型解析与分发流（文档 3.1.5）：**

1. 用户经 **Web UI** 上传文件 → 请求到达 **API Gateway**。
2. **文档解析 Agent** 完成格式识别、OCR/结构化解析 → 产出结构化文本与定位信息。
3. **Coordinator Agent** 接收结构化结果 → 按意图分解并分发给合规审查、比对分析、资质核验、风险识别等 **专业 Agent**。
4. 专业 Agent 通过 **共享 Skill**（检索、相似度、图查询等）访问 **PostgreSQL / Qdrant / Neo4j / 文件存储** 与知识库。
5. 结果经 Coordinator 汇总 → 经 API 返回 UI；报告类能力可走 `report_generation` 等 Skill。

**RAG / 检索相关质量边界（来自 `D:\data\测试指标体系.md`，指导实现与测试分层）：**
- **摄入与分块**：语义完整率、覆盖完整率、边界准确率、块长度、元数据、表格保持、重叠率等指标约束文档解析与向量化前的管道设计。
- **检索**：Recall@K、MRR、NDCG、场景召回等约束 Qdrant（及混合检索）与查询构造，与 **比对分析 / 风险识别 / 合规审查** 等依赖检索的 Agent 的验收基线一致。
- **生成与引用**：答案正确率、引用召回/精确率、幻觉率、拒答准确率等约束 LLM 输出与 **原文定位、可解释性** 需求（需求文档 4.7、6.1）的衔接。
- **任务级**：对比分析、合规审查、风险识别等复杂任务指标映射到多 Agent 协作输出的评测维度，而非单一 REST 端点。

**State Management (planned):**
- LangGraph 状态图承载会话与任务状态；跨请求持久化细节需在实现阶段定义（当前仓库无代码）。

## Key Abstractions

**Coordinator Agent:**
- Purpose: 唯一编排入口，避免 UI 直接调用多个专业 Agent。
- Examples: 规划中实现位置待定（建议未来代码置于类似 `src/agents/coordinator/` 或项目约定目录）。
- Pattern: StateGraph 驱动的分解-调度-汇总。

**专业 Agent（职责边界示例）：**
- Purpose: 文档解析仅做文件→结构化文本；合规审查侧重规则符合性；比对侧重内容一致性与招标-投标映射；资质核验侧重有效性；风险识别侧重异常线索而非定性（`D:\data\01需求概要设计文档.md` 2.3.2）。
- Examples: 同上，实现路径待定。
- Pattern: 每个 Agent 绑定明确 Skill/知识库，减少职责重叠。

**Knowledge base typing:**
- Purpose: 法规、内部规则、制度、资质、案例、模板、专家等类型与 Agent 优先级映射（文档 2.3.4、支持扩展 `custom_*`）。
- Examples: 概念模型在需求文档；物理实现应对应 PostgreSQL/Qdrant 等。
- Pattern: 可插拔知识库（文档 5.3 `KnowledgeBasePlugin` 思路）。

## Entry Points

**Web UI (planned):**
- Location: 未在仓库中创建；规划技术为 Streamlit（`D:\data\01需求概要设计文档.md`）。
- Triggers: 用户浏览器访问部署后的 Web 服务。
- Responsibilities: 上传、配置、展示审查/比对/风险结果与原文定位链接。

**API Gateway (planned):**
- Location: 未在仓库中创建；规划为 FastAPI 应用入口模块（具体路径待项目初始化）。
- Triggers: HTTP 客户端（UI、第三方、脚本）。
- Responsibilities: 路由、认证、超时与错误封装、调用编排层。

**Current repository entry points:**
- 无 `main.py`、`app.py` 或 `package.json` 等可执行入口；仅有需求与测试指标文档，见 `D:\data\STRUCTURE.md`（本目录姊妹文档）。

## Error Handling

**Strategy (planned):** API 层统一错误模型与 HTTP 状态码；Agent 层将可恢复失败返回 Coordinator 做重试或分支；不可逆失败记录审计日志（需求 4.2）。

**Patterns:**
- 文档级：损坏页、乱码等应不中断全流程（`D:\data\测试指标体系.md` 鲁棒性指标与需求大文件/解析性能）。
- 检索/生成：拒答与低置信度路径与测试指标中的拒答准确率、幻觉率告警阈值对齐。

## Cross-Cutting Concerns

**Logging:** 审计日志覆盖操作与关键决策；预留 thought trace / 溯源与监管要求（需求附录「可解释性与溯源存证」）。

**Validation:** 输入文件类型与大小（如单文件 ≤500MB）、RBAC（需求 4.2）。

**Authentication:** API Key + 角色权限；外部系统集成边界在 API Gateway。

**LLM routing (planned extension):** 需求附录建议在 Gateway 与编排层间增加 LLM Router，实现模型无关切换。

---

*Architecture analysis: 2026-04-13*
