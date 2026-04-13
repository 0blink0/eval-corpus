# Plan 03-01 Summary — 统一契约与 Paddle 适配

**Phase:** 03-adapters  
**Status:** Complete  
**Date:** 2026-04-13

## Completed

- 新增 `src/eval_corpus/adapters/base.py`：
  - 统一协议 `parse_to_blocks(...) -> list[ParsedBlock]`
  - `AdapterStage`（`load/parse/normalize/validate`）
  - `AdapterError` 统一异常结构
  - `AdapterConfig`、`RuntimeMetadata`
- 新增 `src/eval_corpus/adapters/registry.py` 与 `src/eval_corpus/adapters/paddle.py`
- 新增 `src/eval_corpus/adapter_runner.py`（continue-on-error / fail-fast）
- 新增 `adapt` CLI 编排入口（工具无关）
- 新增 `tests/test_adapters_contract.py`、`tests/test_adapters_paddle.py`
- 新增 `tests/fixtures/adapters/README.md`（最小三件套规范）

## Verification

- `python -m pytest -q tests/test_adapters_contract.py::test_adapter_contract_and_error_schema -x`
- `python -m pytest -q tests/test_adapters_paddle.py -x`

## Deviations

- 当 Paddle 依赖缺失时，返回标准化 `stage=load` 错误（符合 D-31/D-40）。
