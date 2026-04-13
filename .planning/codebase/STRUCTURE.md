# Codebase Structure

**Analysis Date:** 2026-04-13

## Directory Layout

```
D:\data\
├── 01需求概要设计文档.md    # 需求与计划架构（B/S、Agent、模块、存储）
├── 测试指标体系.md          # RAG/检索/生成评测维度与阈值
└── .planning\
    └── codebase\
        ├── ARCHITECTURE.md   # 计划架构 vs 仓库现状
        └── STRUCTURE.md     # 本文件
```

当前仓库根目录下**仅**上述两份业务 Markdown 与 `.planning/codebase` 下的映射产物；无 `src/`、`tests/`、`pyproject.toml`、`package.json` 等源码树。

## Directory Purposes

**`D:\data\`（仓库根）:**
- Purpose: 存放项目级需求与质量基线文档。
- Contains: `*.md` 文件；未来可并列增加源码目录。
- Key files: `D:\data\01需求概要设计文档.md`, `D:\data\测试指标体系.md`

**`D:\data\.planning\codebase\`:**
- Purpose: GSD / 规划流程消费的代码库映射说明（架构、结构、约定等）。
- Contains: 分析用 Markdown，非运行时产物。
- Key files: `D:\data\.planning\codebase\ARCHITECTURE.md`, `D:\data\.planning\codebase\STRUCTURE.md`

## Key File Locations

**Entry Points:**
- 无代码入口。计划中的入口见 `D:\data\.planning\codebase\ARCHITECTURE.md`（Streamlit UI、FastAPI Gateway）。

**Configuration:**
- 未检出；未来环境配置建议仅列存在性于文档，不将密钥写入仓库（参考 GSD 禁止读取 `.env` 内容的原则）。

**Core Logic:**
- 当前仅在 `D:\data\01需求概要设计文档.md` 中以文字与图示描述；无对应源码路径。

**Testing / Quality Baseline:**
- `D:\data\测试指标体系.md`：分块、检索、答案质量、复杂任务、性能、鲁棒性及告警阈值，用于定义 **解析管道、向量检索、Agent 输出** 的测试边界（与 `ARCHITECTURE.md` 中数据流呼应）。

## Naming Conventions

**Files:**
- 需求文档：中文文件名，版本与日期在文档信息表内维护（如 `D:\data\01需求概要设计文档.md` 文档信息节）。
- 指标体系：`D:\data\测试指标体系.md` 为独立评测规格。

**Directories:**
- `.planning/codebase/`：全小写，与 GSD 映射输出约定一致。

## Where to Add New Code

以下路径为 **建议约定（非当前仓库事实）**，实施前应在仓库中初始化 Python 项目结构并与团队对齐。

**New Feature（建议）:**
- Primary code: `src/` 下按域划分，例如 `src/api/`（FastAPI）、`src/agents/`（LangGraph 编排与各 Agent）、`src/skills/`、`src/integrations/`。
- Tests: `tests/` 下镜像结构或使用 `tests/unit/`、`tests/integration/`，评测对齐 `D:\data\测试指标体系.md` 中的阶段与指标。

**New Component/Module:**
- Coordinator：`src/agents/coordinator/`（或等价命名）。
- 专业 Agent：`src/agents/specialists/<agent_name>/`。
- 共享 Skill：`src/skills/<skill_name>.py` 或包目录。

**Utilities:**
- Shared helpers: `src/common/` 或 `src/lib/`，避免与 Agent 业务逻辑耦合。

**Frontend（与需求一致时）:**
- Streamlit：常见为 `src/ui/app.py` 或仓库根 `app.py`；若未来信创切换 Vue/React，单独 `frontend/` 目录（需求附录信创对照表）。

## Special Directories

**`.planning/`:**
- Purpose: 规划、映射与流程产物，服务 GSD 等工具链。
- Generated: 部分文件由映射/规划命令写入。
- Committed: 按团队策略；映射文档通常纳入版本控制以便 Planner/Executor 引用。

**未来可能新增的 `infra/` 或 `deploy/`:**
- Purpose: Docker、K8s、数据库初始化脚本等（需求 4.2、私有化部署）。
- Generated: 否（手写维护）。
- Committed: 是（不含密钥）。

---

*Structure analysis: 2026-04-13*
