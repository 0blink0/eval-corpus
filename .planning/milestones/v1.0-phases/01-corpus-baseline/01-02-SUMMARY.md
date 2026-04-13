# Plan 01-02 Summary — 语料扫描与清单

**Phase:** 01-corpus-baseline  
**Status:** Complete  
**Date:** 2026-04-13

## Completed

- `scan.py`：`DEFAULT_EXTENSIONS`、`collect_corpus_files`（`os.walk(..., followlinks=False)`）、忽略 `~$*` / `.DS_Store`、扩展名白名单、`--extra-ext`。
- 不可读文件：`stat` 失败记入 `errors` 与 `unreadable_count`（CORP-02）。
- `manifest.py`：`build_manifest_payload`、`write_manifest`；顶层 `schema_version`、`scan_errors`、`unreadable_count`。
- CLI：`manifest`（`--manifest-out` 默认 `corpus_manifest.json`，摘要 stderr）。
- `tests/test_scan.py`、`tests/test_manifest.py`（含 `test_collect_unreadable_permission`）。

## Verification

- `python -m pytest -q tests/test_scan.py tests/test_manifest.py`

## Deviations

- 无。
