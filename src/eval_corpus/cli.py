"""Typer CLI entrypoint for corpus-eval."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

import typer

from eval_corpus.adapter_runner import run_adapter_on_files
from eval_corpus.batch import BatchRunConfig, run_batch
from eval_corpus.chunk_io import read_parsed_blocks_json, write_chunks_json
from eval_corpus.chunker import chunk_blocks
from eval_corpus.config import ConfigError, resolve_corpus_root
from eval_corpus.ir_models import ChunkConfig
from eval_corpus.manifest import build_manifest_payload, write_manifest
from eval_corpus.metrics_io import build_metrics_artifact, read_adapter_summary_json, write_metrics_json
from eval_corpus.reporting import (
    build_report_payload,
    collect_runtime_metadata,
    create_run_layout,
    ensure_tool_artifact_paths,
    export_csv,
    export_html,
    export_json,
    export_markdown,
)
from eval_corpus.scan import collect_corpus_files, normalize_extra_exts
from eval_corpus.stats import aggregate_golden_stats, write_stats_json
from eval_corpus.synthetic_data.generator import generate_synthetic_dataset
from eval_corpus.synthetic_data.models import SyntheticDataConfig

app = typer.Typer(
    help="Corpus evaluation CLI: manifest + golden stats for parsing experiments.",
    no_args_is_help=True,
)


def _exit_config_error(exc: ConfigError) -> None:
    typer.secho(str(exc), err=True)
    raise typer.Exit(2)


@app.command()
def version() -> None:
    """Print CLI version."""
    typer.echo("eval-corpus 0.1.0")


@app.command("check-config")
def check_config(
    root: Optional[str] = typer.Option(
        None,
        "--root",
        help="Corpus root directory (overrides EVAL_CORPUS_ROOT).",
    ),
) -> None:
    """Verify corpus root resolves and is a directory."""
    try:
        path = resolve_corpus_root(root)
    except ConfigError as e:
        _exit_config_error(e)
    typer.echo(f"OK {path}")


@app.command()
def manifest(
    root: Optional[str] = typer.Option(
        None,
        "--root",
        help="Corpus root directory (overrides EVAL_CORPUS_ROOT).",
    ),
    manifest_out: Path = typer.Option(
        Path("corpus_manifest.json"),
        "--manifest-out",
        help="Output JSON path (default: ./corpus_manifest.json).",
    ),
    extra_ext: Optional[List[str]] = typer.Option(
        None,
        "--extra-ext",
        help="Additional file extensions (with or without leading dot).",
    ),
) -> None:
    """Scan corpus tree and write manifest JSON; summary on stderr."""
    try:
        corpus_root = resolve_corpus_root(root)
    except ConfigError as e:
        _exit_config_error(e)

    extras = normalize_extra_exts(tuple(extra_ext or ()))
    files, errors, unreadable_count = collect_corpus_files(corpus_root, extras)
    payload = build_manifest_payload(corpus_root, files, errors, unreadable_count)
    write_manifest(manifest_out, payload)

    total_bytes = sum(f["size_bytes"] for f in payload["files"])
    typer.secho(
        f"root={corpus_root} files={len(payload['files'])} bytes={total_bytes} "
        f"errors={len(errors)} unreadable={unreadable_count}",
        err=True,
    )


@app.command()
def stats(
    root: Optional[str] = typer.Option(
        None,
        "--root",
        help="Corpus root directory (overrides EVAL_CORPUS_ROOT).",
    ),
    stats_out: Path = typer.Option(
        Path("golden_stats.json"),
        "--stats-out",
        help="Output JSON path (default: ./golden_stats.json).",
    ),
    extra_ext: Optional[List[str]] = typer.Option(
        None,
        "--extra-ext",
        help="Additional file extensions (with or without leading dot).",
    ),
) -> None:
    """Compute golden statistics JSON; summary on stderr."""
    try:
        corpus_root = resolve_corpus_root(root)
    except ConfigError as e:
        _exit_config_error(e)

    extras = normalize_extra_exts(tuple(extra_ext or ()))
    files, errors, unreadable_count = collect_corpus_files(corpus_root, extras)
    payload = aggregate_golden_stats(corpus_root, files)
    payload["scan_errors"] = errors
    payload["unreadable_count"] = unreadable_count
    write_stats_json(stats_out, payload)

    totals = payload["totals"]
    typer.secho(
        f"root={corpus_root} files={totals['total_files']} "
        f"unicode_chars={totals['total_unicode_chars']} "
        f"needs_ocr={totals['needs_ocr_files']} "
        f"scan_errors={len(errors)} unreadable={unreadable_count}",
        err=True,
    )


@app.command()
def chunk(
    blocks_in: Path = typer.Option(
        ...,
        "--blocks-in",
        help="Input ParsedBlock[] JSON path.",
    ),
    chunks_out: Path = typer.Option(
        ...,
        "--chunks-out",
        help="Output Chunk[] JSON path.",
    ),
    min_chars: int = typer.Option(300, "--min-chars", help="Minimum target chars."),
    max_chars: int = typer.Option(1000, "--max-chars", help="Maximum target chars."),
    overlap_ratio: float = typer.Option(
        0.15,
        "--overlap-ratio",
        help="Text overlap ratio in [0.10, 0.20].",
    ),
) -> None:
    """Chunk ParsedBlock JSON into normalized chunk JSON."""
    if min_chars <= 0 or max_chars < min_chars:
        typer.secho("Invalid min/max chars: require 0 < min_chars <= max_chars.", err=True)
        raise typer.Exit(2)
    if not (0.10 <= overlap_ratio <= 0.20):
        typer.secho("Invalid --overlap-ratio: must be within [0.10, 0.20].", err=True)
        raise typer.Exit(2)

    blocks = read_parsed_blocks_json(blocks_in)
    cfg = ChunkConfig(min_chars=min_chars, max_chars=max_chars, overlap_ratio=overlap_ratio)
    chunks = chunk_blocks(blocks, cfg)
    write_chunks_json(chunks_out, chunks)
    typer.secho(
        f"blocks={len(blocks)} chunks={len(chunks)} "
        f"min_chars={min_chars} max_chars={max_chars} overlap_ratio={overlap_ratio}",
        err=True,
    )


@app.command("adapt")
def adapt(
    tool: str = typer.Option(..., "--tool", help="Adapter tool: paddle|glm|mineru"),
    inputs: List[Path] = typer.Option(..., "--input", help="Input file path (repeatable)."),
    fail_fast: bool = typer.Option(False, "--fail-fast", help="Stop on first error."),
    debug: bool = typer.Option(False, "--debug", help="Include raw_error details."),
    summary_out: Path | None = typer.Option(
        None, "--summary-out", help="Optional path to write adapter run summary JSON."
    ),
) -> None:
    """Run one adapter against multiple files with unified error summary."""
    result = run_adapter_on_files(tool, inputs, fail_fast=fail_fast, debug=debug)
    if summary_out is not None:
        import json

        summary_out.parent.mkdir(parents=True, exist_ok=True)
        summary_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.secho(
        f"tool={tool} files={len(inputs)} results={len(result['results'])} errors={len(result['errors'])}",
        err=True,
    )
    if result["errors"] and fail_fast:
        raise typer.Exit(1)


@app.command("metrics")
def metrics(
    input_path: Path = typer.Option(..., "--input", help="Adapter summary JSON input path."),
    out_path: Path = typer.Option(..., "--out", help="Metrics artifact JSON output path."),
) -> None:
    """Build one metrics JSON artifact from adapter summary."""
    if not input_path.is_file():
        typer.secho(f"Input file not found: {input_path}", err=True)
        raise typer.Exit(2)

    adapter_summary = read_adapter_summary_json(input_path)
    payload = build_metrics_artifact(adapter_summary)
    write_metrics_json(out_path, payload)

    typer.secho(
        f"tools={len(payload['per_tool'])} files={len(payload['per_file'])} "
        f"errors={payload['overall']['runtime_metadata']['error_count']}",
        err=True,
    )


@app.command("report")
def report(
    input_path: Path = typer.Option(..., "--input", help="Metrics artifact JSON input path."),
    out_dir: Path = typer.Option(Path("runs"), "--out-dir", help="Base output directory for run artifacts."),
    run_id: str = typer.Option("run-report", "--run-id", help="Run identifier."),
) -> None:
    """Export report artifacts (json/csv/md/html) into run layout."""
    if not input_path.is_file():
        typer.secho(f"Input file not found: {input_path}", err=True)
        raise typer.Exit(2)
    try:
        metrics_payload = json.loads(input_path.read_text(encoding="utf-8-sig"))
        report_payload = build_report_payload(metrics_payload)
    except (json.JSONDecodeError, ValueError) as exc:
        typer.secho(f"Invalid metrics artifact: {exc}", err=True)
        raise typer.Exit(2)
    except Exception as exc:  # noqa: BLE001
        typer.secho(f"Report build failed: {exc}", err=True)
        raise typer.Exit(1)

    layout = create_run_layout(base_dir=out_dir, run_id=run_id)
    tool_names = sorted({str(item.row_key) for item in report_payload.summary_rows if item.row_type == "tool"})
    ensure_tool_artifact_paths(layout=layout, tools=(tool_names or ["all"]), artifact_types=["reports"])

    reports_dir = layout.by_artifact_dir / "reports" / "all"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "report.json").write_text(export_json(report_payload), encoding="utf-8")
    (reports_dir / "report.csv").write_text(export_csv(report_payload), encoding="utf-8")
    (reports_dir / "report.md").write_text(export_markdown(report_payload), encoding="utf-8")
    (reports_dir / "report.html").write_text(export_html(report_payload), encoding="utf-8")

    runtime = collect_runtime_metadata(run_id=run_id)
    (layout.by_artifact_dir / "runtime" / "all").mkdir(parents=True, exist_ok=True)
    (layout.by_artifact_dir / "runtime" / "all" / "runtime.json").write_text(
        json.dumps(runtime, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    typer.secho(f"run={layout.root} outputs=4", err=True)


@app.command("batch")
def batch(
    input_dir: Path = typer.Option(..., "--input-dir", help="Directory to batch-process recursively."),
    out_dir: Path = typer.Option(Path("runs"), "--out-dir", help="Base output directory for run artifacts."),
    run_id: str = typer.Option("run-batch", "--run-id", help="Run identifier."),
    max_workers: int = typer.Option(1, "--max-workers", help="Worker concurrency."),
    failure_threshold: float = typer.Option(1.0, "--failure-threshold", help="Abort if failed/total >= threshold."),
    max_retries: int = typer.Option(0, "--max-retries", help="Per-file retry count."),
) -> None:
    """Run local recursive batch processing with retry and threshold controls."""
    if not input_dir.is_dir():
        typer.secho(f"Input directory not found: {input_dir}", err=True)
        raise typer.Exit(2)
    try:
        cfg = BatchRunConfig(
            max_workers=max_workers,
            continue_on_error=True,
            max_retries=max_retries,
            failure_threshold=failure_threshold,
        )
    except ValueError as exc:
        typer.secho(f"Invalid batch arguments: {exc}", err=True)
        raise typer.Exit(2)

    layout = create_run_layout(base_dir=out_dir, run_id=run_id)
    ensure_tool_artifact_paths(layout=layout, tools=["all"], artifact_types=["batch"])

    result = run_batch(
        input_dir,
        cfg,
        processor=lambda file_path: {"file": str(file_path), "size_bytes": file_path.stat().st_size},
    )
    out = layout.by_artifact_dir / "batch" / "all" / "batch_result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    typer.secho(
        f"run={layout.root} total={result.total} succeeded={result.succeeded} failed={result.failed}",
        err=True,
    )
    if result.aborted and result.failed > 0:
        raise typer.Exit(1)


@app.command("synthetic-data")
def synthetic_data(
    out_dir: Path = typer.Option(Path("runs"), "--out-dir", help="Base output directory for run artifacts."),
    run_id: str = typer.Option("run-synthetic", "--run-id", help="Run identifier."),
    total_samples: int = typer.Option(30, "--total-samples", help="Total synthetic sample count."),
    seed: int = typer.Option(42, "--seed", help="Random seed for deterministic generation."),
) -> None:
    """Generate text/scan/table synthetic dataset for downstream batch runs."""
    try:
        cfg = SyntheticDataConfig(total_samples=total_samples, seed=seed)
    except ValueError as exc:
        typer.secho(f"Invalid synthetic arguments: {exc}", err=True)
        raise typer.Exit(2)

    layout = create_run_layout(base_dir=out_dir, run_id=run_id)
    ensure_tool_artifact_paths(layout=layout, tools=["all"], artifact_types=["synthetic_data"])
    dataset_root = layout.by_artifact_dir / "synthetic_data" / "all" / "dataset"
    manifest = generate_synthetic_dataset(dataset_root, cfg)
    (layout.by_artifact_dir / "synthetic_data" / "all" / "manifest.json").write_text(
        json.dumps(manifest.model_dump(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    typer.secho(
        f"run={layout.root} samples={manifest.total_samples} seed={manifest.seed}",
        err=True,
    )


def run() -> None:
    app()


if __name__ == "__main__":
    app()
