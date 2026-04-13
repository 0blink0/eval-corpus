# Plan 03-03 Summary — MinerU 适配与跨工具验收

**Phase:** 03-adapters  
**Status:** Complete  
**Date:** 2026-04-13

## Completed

- 新增 `src/eval_corpus/adapters/mineru.py`
- 完成三工具统一接口接入（Paddle / GLM / MinerU）
- 新增 `tests/test_adapters_mineru.py`
- `tests/test_adapters_contract.py` 增加跨三工具最小三件套验收（D-43）
- CLI `adapt` 在批处理模式支持 continue-on-error 与 `--fail-fast`

## Verification

- `python -m pytest -q tests/test_adapters_mineru.py -x`
- `python -m pytest -q tests/test_adapters_contract.py::test_three_tool_runtime_metadata_and_modes -x`
- `python -m pytest -q tests/test_adapters_contract.py::test_cross_tool_minimal_fixture_acceptance -x`

## Deviations

- 若工具依赖缺失，按标准错误模型返回并保持批处理可继续（符合 D-38）。
