# Adapter Fixtures (Phase 3)

本目录用于 Phase 3 的最小三件套样例（D-41/D-42）：

1. `text`：文本型 PDF 或等价文本输入
2. `scan`：扫描型 PDF（可为占位样例）
3. `table`：包含表格结构的样例

验收标准（D-43）：
- 对每个工具与每个样例，输出必须是以下二选一：
  - 合法 `ParsedBlock[]`
  - 标准化错误（含 `file/tool/stage/message`）

说明：当前仓库测试可用轻量样例或临时文件模拟，重点是适配器出口契约一致性。
