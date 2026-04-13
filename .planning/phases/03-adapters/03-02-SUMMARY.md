# Plan 03-02 Summary — GLM 适配与运行级元数据

**Phase:** 03-adapters  
**Status:** Complete  
**Date:** 2026-04-13

## Completed

- 新增 `src/eval_corpus/adapters/glm.py`
- 注册 GLM 适配器到 registry
- Runner 统一输出运行级元数据：`tool_name/tool_version/model_id`
- GLM 缺失 `GLM_API_KEY` 时返回标准化 `stage=parse` 错误
- 扩充 contract 测试覆盖 GLM 的 continue/fail-fast 模式

## Verification

- `python -m pytest -q tests/test_adapters_glm.py -x`
- `python -m pytest -q tests/test_adapters_contract.py::test_glm_in_runner_modes -x`

## Deviations

- 当前实现使用 `GLM_API_KEY` 是否存在作为可运行判据，真实在线调用留给环境具备时执行。
