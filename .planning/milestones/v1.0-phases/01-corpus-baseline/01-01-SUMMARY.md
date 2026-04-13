# Plan 01-01 Summary — 配置模块与路径校验

**Phase:** 01-corpus-baseline  
**Status:** Complete  
**Date:** 2026-04-13

## Completed

- `pyproject.toml`：Python 3.11+、`typer`、`pypdf`、`pytest` dev、`corpus-eval` 入口。
- `src/eval_corpus/`：`config.resolve_corpus_root`（CLI > `EVAL_CORPUS_ROOT`）、`ConfigError`。
- CLI：`version`、`check-config`。
- `README.md`：安装、`EVAL_CORPUS_ROOT`、**北燃热力宣传品采购归档资料**、`corpus-eval --help`。
- `tests/test_config.py`：环境-only、CLI 覆盖 env、双缺失、不存在、非目录。

## Verification

- `python -m pip install -e ".[dev]"`
- `python -m pytest -q tests/test_config.py`
- `corpus-eval --help`

## Deviations

- 无。
