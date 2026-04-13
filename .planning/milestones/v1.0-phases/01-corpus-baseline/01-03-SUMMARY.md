# Plan 01-03 Summary — 黄金统计与 stats CLI

**Phase:** 01-corpus-baseline  
**Status:** Complete  
**Date:** 2026-04-13

## Completed

- `stats.py`：`compute_file_stats`、`aggregate_golden_stats`、`write_stats_json`；PDF `needs_ocr`、xlsx 启发式表格、Unicode 字符。
- CLI：`stats`（`--stats-out` 默认 `golden_stats.json`，摘要 stderr）；输出含扫描错误字段。
- `README.md`：`golden_stats.json` 字段表、`corpus-eval stats` 说明。
- `tests/test_stats.py`：文本、PDF 空白页、`xlsx` 启发式、聚合、CLI 集成。

## Verification

- `python -m pytest -q tests/`
- `corpus-eval stats --help`

## Deviations

- 无。
