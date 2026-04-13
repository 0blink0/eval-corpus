# Plan 02-02 Summary — 分块核心与重叠

**Phase:** 02-ir  
**Status:** Complete  
**Date:** 2026-04-13

## Completed

- 新增 `src/eval_corpus/chunker.py`：
  - 结构优先分段（table 原子）
  - 句界优先切分 + hard-cut 回退
  - 文本块重叠逻辑（D-21：`ceil(ratio * len(current_chunk_text))`）
  - 仅非 table 块应用重叠，短前块截短不报错（D-23）
- 新增 `tests/test_chunker_core.py` 核心规则测试。

## Verification

- `python -m pytest -q tests/test_chunker_core.py::test_chunking_rules -x`
- `python -m pytest -q tests/test_chunker_core.py::test_overlap_formula_and_truncation -x`

## Deviations

- 文本拼接保留换行分隔，相关断言按 `replace("\n", "")` 归一后校验重叠结果。
