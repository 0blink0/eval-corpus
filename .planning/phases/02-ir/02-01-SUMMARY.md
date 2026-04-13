# Plan 02-01 Summary — IR 模型与序列化

**Phase:** 02-ir  
**Status:** Complete  
**Date:** 2026-04-13

## Completed

- 新增 `src/eval_corpus/ir_models.py`：`ParsedBlock`、`Chunk`、`ChunkConfig`（Pydantic v2）。
- 锁定字段语义：`type` 枚举、`heading_path: list[str]`、`page: int | null`、`parser_tool` 默认 `"unknown"`。
- 新增 `src/eval_corpus/chunk_io.py`：`ParsedBlock[]` JSON 入站校验、`Chunk[]` JSON 导出（`schema_version: 1.0`）。
- `pyproject.toml` 运行时依赖确认含 `pydantic>=2.7.0`。

## Verification

- `python -m pytest -q tests/test_chunker_core.py::test_parsed_block_schema -x`
- `python -m pytest -q tests/test_chunker_core.py::test_parsed_block_json_roundtrip -x`

## Deviations

- 为兼容 PowerShell UTF-8 BOM，JSON 入站读取使用 `utf-8-sig`。
