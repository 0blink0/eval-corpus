# eval-corpus

语料清单与黄金统计 CLI，服务于「文档解析工具分块指标对比实验」Phase 1（CORP-01～CORP-03）。

## 安装

```bash
python -m pip install -e ".[dev]"
```

## 语料路径（EVAL_CORPUS_ROOT）

示例语料目录名：**北燃热力宣传品采购归档资料**。实际路径由你在本机配置，**勿假设在仓库内**。

- 环境变量：`EVAL_CORPUS_ROOT` 指向语料根目录。
- 或每个子命令传入：`--root <绝对或相对路径>`（**优先于**环境变量）。

## corpus-eval --help

```bash
corpus-eval --help
corpus-eval manifest --help
corpus-eval stats --help
```

## 子命令摘要

| 命令 | 说明 |
|------|------|
| `manifest` | 扫描语料根，写出 `corpus_manifest.json`（默认），摘要走 stderr |
| `stats` | 计算黄金统计，写出 `golden_stats.json`（默认），摘要走 stderr |
| `check-config` | 校验根路径可解析且为目录 |
| `version` | 打印版本 |

## golden_stats 输出字段（`golden_stats.json`）

| 路径 | 说明 |
|------|------|
| `schema_version` | 固定 `"1.0"` |
| `root` | 语料根绝对路径 |
| `generated_at` | UTC ISO8601 时间 |
| `totals.total_files` | 参与统计的文件数 |
| `totals.total_unicode_chars` | Unicode 字符合计（D-14） |
| `totals.needs_ocr_files` | `needs_ocr: true` 的文件数 |
| `files[].path` | 相对根的路径 |
| `files[].unicode_chars` | 该文件字符数 |
| `files[].page_count` | PDF 页数（可解析时） |
| `files[].page_count_reason` | 无法解析页数时的原因 |
| `files[].needs_ocr` | PDF 有页但无文本层时为 true（D-15） |
| `files[].table_count_heuristic` | xls/xlsx 启发式表格数 |
| `files[].heuristic` | 表格统计为启发式时为 true（D-13） |
| `scan_errors` | 扫描阶段不可读/错误项 |
| `unreadable_count` | 不可读文件计数 |

## 输出约定

- 清单与统计 JSON 均含顶层 `schema_version: "1.0"`。
- 人类可读摘要始终打印到 **stderr**，便于 stdout 管道。
