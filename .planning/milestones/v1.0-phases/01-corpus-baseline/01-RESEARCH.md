# Phase 01 — Technical Research: 评测基座与语料规范

**Date:** 2026-04-13  
**Question answered:** What do we need to know to plan Phase 1 well?

---

## User Constraints

（自 `01-CONTEXT.md` 锁定 — planner 必须遵守）

- **D-01–D-04:** 仅 CLI + 环境变量 `EVAL_CORPUS_ROOT`；优先级 CLI > env；无路径则非零退出并明确提示。
- **D-05–D-07:** 清单主工件 JSON；人类摘要走 **stderr**；`--manifest-out` 缺省 `./corpus_manifest.json`。
- **D-08–D-11:** 递归扫描；内置扩展名白名单 + CLI 覆盖；默认不跟随 symlink；忽略 `~$*`、`.DS_Store` 等。
- **D-12–D-15:** PDF 等可解析才填页数；表格数启发式并标注；Unicode 字符计数；文本层基准 + `needs_ocr` 标注，不伪造长度。

---

## Standard Stack

| Concern | Recommendation | Confidence |
|---------|----------------|--------------|
| 语言与打包 | **Python 3.11+**，`pyproject.toml` + `[project.scripts]` 控制台入口 | HIGH [ASSUMED: 生态与 PROJECT 计划栈一致] |
| CLI | **`typer`**（或标准库 `argparse` 若零依赖优先）— typer 对子命令与 `--help` 友好 | MEDIUM [ASSUMED] |
| 路径与扫描 | **`pathlib`**；`os.walk`/`Path.rglob`；显式 `follow_symlinks=False` | HIGH [VERIFIED: stdlib] |
| PDF 页数与文本探测 | **`pypdf`**（轻量）或 **PyMuPDF (`fitz`)**（更准但依赖更重）；首版推荐 **pypdf** 读页数 + 抽取文本判断空层 | MEDIUM [CITED: pypdf.readthedocs.io — 常见选择] |
| 纯文本字符 | `path.read_text(encoding=..., errors="replace")` + `len(text)` 对 str 为 Unicode 字符长度 | HIGH [VERIFIED: Python str 语义] |
| 测试 | **pytest**；临时目录用 `tmp_path` | HIGH [ASSUMED] |

---

## Architecture Patterns

1. **包布局（建议）:** `src/eval_corpus/` 或 `src/corpus_eval/` 下分 `cli.py`、`config.py`、`scan.py`、`stats.py`、`models.py`（清单与统计的 dataclass/TypedDict + JSON schema 文档）。
2. **单一 CLI 多子命令:** `corpus-eval manifest …`、`corpus-eval stats …` 或单命令带 `manifest`/`stats` 子模式 — 与 ROADMAP 三计划对齐时可先统一入口再分模块。
3. **JSON schema 版本字段:** 清单与统计 JSON 顶层含 `schema_version`（如 `"1.0"`），满足 CONTEXT 中「版本化 schema」。

---

## Don't Hand-Roll

| Problem | Use |
|---------|-----|
| CLI 帮助与参数解析 | typer / argparse，不要手写 argv |
| PDF 结构 | pypdf（或 PyMuPDF），不要按魔数猜页数 |
| 递归与过滤 | pathlib + 明确忽略列表，不要 shell-out `find` |

---

## Common Pitfalls

- **Symlink 环:** 不跟随 symlink 仍可能遇挂载问题 — 记录已访问 inode/路径深度上限并日志说明 [ASSUMED]。
- **大文件:** 统计字符时对超大二进制误当文本 — 仅对白名单扩展名做文本读取，其余只记元数据 [ASSUMED]。
- **PDF 扫描件:** 文本层为空 ≠ 页数为 0 — 页数可读，文本长度 0，`needs_ocr: true`（per D-15）。
- **编码:** 非 UTF-8 文本用 `errors="replace"` 并记录 `encoding_detected` 或 `encoding: utf-8-with-replacement` [ASSUMED]。

---

## Code Examples

（说明性 — 非落盘代码）

```python
# 解析根路径：CLI 覆盖 env
root = cli_root or os.environ.get("EVAL_CORPUS_ROOT")
if not root:
    typer.secho("Set --root or EVAL_CORPUS_ROOT", err=True)
    raise typer.Exit(2)
```

```python
from pypdf import PdfReader
reader = PdfReader(path)
page_count = len(reader.pages)
text = "".join(p.extract_text() or "" for p in reader.pages)
needs_ocr = len(text.strip()) == 0 and page_count > 0
```

---

## Validation Architecture

**Framework:** pytest 8.x  
**Config:** `pyproject.toml` `[tool.pytest.ini_options]` 或 `pytest.ini`  
**Quick command:** `pytest -q tests/`  
**Full command:** `pytest tests/`  

**Sampling:**

- 每个实现任务完成后：运行 `pytest -q`（目标 &lt; 60s）。
- Wave 完成：全量 `pytest tests/`。

**Dimension 8 (Nyquist):** 每个生产代码任务必须有可自动化 `<automated>` 命令；首版无测试时 Wave 0 先建 `tests/` 桩与固定夹具（临时目录下合成小 PDF/txt）。

---

## RESEARCH COMPLETE

Researcher notes: 仓库当前无 `src/`；Phase 1 为绿场初始化。依赖版本锁定在 `pyproject.toml` / lock 由执行阶段写入。
