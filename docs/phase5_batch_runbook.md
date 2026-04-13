# Phase 5 Batch Runbook

## 1. 依赖安装

```bash
python -m pip install -e ".[dev]"
```

## 2. 命令入口概览

- `report`：将 metrics 工件导出为 JSON/CSV/Markdown/HTML 四种报告。
- `synthetic-data`：生成 text/scan/table 三类可复现合成样本。
- `batch`：按目录递归批量处理输入文件，支持并发、失败阈值与重试。

所有命令都会按 `run_id-UTC时间戳` 创建运行目录，并在 `by_tool` 与 `by_artifact` 双维结构下落盘工件。

## 3. report 命令

```bash
python -m eval_corpus.cli report \
  --input .\artifacts\metrics.json \
  --out-dir .\runs \
  --run-id report-local
```

预期输出：

- `runs/<run>/by_artifact/reports/all/report.json`
- `runs/<run>/by_artifact/reports/all/report.csv`
- `runs/<run>/by_artifact/reports/all/report.md`
- `runs/<run>/by_artifact/reports/all/report.html`
- `runs/<run>/by_artifact/runtime/all/runtime.json`

## 4. synthetic-data 命令

```bash
python -m eval_corpus.cli synthetic-data \
  --out-dir .\runs \
  --run-id synth-smoke \
  --total-samples 60 \
  --seed 2026
```

预期输出：

- `runs/<run>/by_artifact/synthetic_data/all/dataset/text/`
- `runs/<run>/by_artifact/synthetic_data/all/dataset/scan/`
- `runs/<run>/by_artifact/synthetic_data/all/dataset/table/`
- `runs/<run>/by_artifact/synthetic_data/all/manifest.json`

## 5. batch 命令

```bash
python -m eval_corpus.cli batch \
  --input-dir .\runs\<synthetic-run>\by_artifact\synthetic_data\all\dataset \
  --out-dir .\runs \
  --run-id batch-local \
  --max-workers 4 \
  --failure-threshold 0.4 \
  --max-retries 1
```

参数说明：

- `--max-workers`：单机并发 worker 数量。
- `--failure-threshold`：当 `failed / total >= threshold` 时提前中止。
- `--max-retries`：单文件失败后的重试次数。

> 边界：本阶段仅支持单机并发与目录切分，不包含分布式队列、远端调度 SDK 或多节点任务编排。

## 6. 常见故障排查

- 输入路径不存在：命令返回 exit code `2`，请检查 `--input` 或 `--input-dir`。
- 参数非法（并发、阈值、样本量）：命令返回 exit code `2`，按提示修正参数范围。
- 运行过程中异常：命令返回 exit code `1`，查看对应 run 下的 JSON 工件定位失败文件。
- Git 信息缺失：`runtime.json` 会记录 `git_commit: null` 与 `git_status: unavailable`，不影响命令执行。

## 7. 云主机扩跑步骤

1. 在云主机同步仓库并安装依赖。
2. 上传待处理目录（或先执行 `synthetic-data` 生成测试集）。
3. 提升 `--max-workers` 并按机器资源设置 `--failure-threshold` 与 `--max-retries`。
4. 分目录切分批次执行多个 `batch` run（例如按日期/工具拆分目录）。
5. 汇总各批次 run 目录中的 `batch_result.json` 与 `report.*` 工件进行对比分析。
