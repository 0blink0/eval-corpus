# Plan 02-03 Summary — chunk CLI 与夹具测试

**Phase:** 02-ir  
**Status:** Complete  
**Date:** 2026-04-13

## Completed

- `src/eval_corpus/cli.py` 新增 `chunk` 子命令：
  - `--blocks-in` / `--chunks-out`
  - `--min-chars` / `--max-chars` / `--overlap-ratio`
  - overlap ratio 区间校验 `[0.10, 0.20]`
- 新增手工夹具：`tests/fixtures/chunking/manual_blocks.json`。
- 新增 `tests/test_chunker_cli.py`：命令 roundtrip 与非法 ratio 分支。

## Verification

- `python -m pytest -q tests/test_chunker_cli.py -x`
- 全量：`python -m pytest -q tests/`

## Deviations

- 无功能偏离；输出 JSON 顶层封装为 `{schema_version, chunks}` 以对齐 Phase 1 产物风格。
