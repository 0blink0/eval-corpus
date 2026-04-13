# Milestones

## v1.0 MVP (Shipped: 2026-04-13)

**Phases completed:** 5 phases, 15 plans, 16 tasks

**Key accomplishments:**

- Phase:
- Phase:
- Phase:
- 建立了可审计的 METR-01~06 指标引擎核心层：六项口径测试、统一结果契约与原子计算函数全部落地并通过回归测试。
- 交付了 METR-07 的规则自动评分、固定抽样复核接口与分离审计结构，保证同输入同 seed 下结果可重复且人工记录不覆盖自动分。
- 交付了可一键执行的 metrics 标准接口：从适配器结果构建三层聚合并输出单一 JSON 工件，且通过 CLI 端到端回归测试验证。
- 基于 Phase 4 指标工件交付了可审计的统一报告模型，并一次性导出 JSON/CSV/Markdown/HTML 四种一致格式。
- 交付了可复现三类型合成数据生成器与支持失败阈值/重试的目录递归批跑器，可直接用于 smoke 与扩跑。
- 交付了 report/synthetic-data/batch 三个可执行 CLI 入口，并将报告、明细、日志与运行元信息统一落盘到 run_id+时间戳目录以支持本地与云主机扩跑。

---
