"""Typer CLI entrypoint for corpus-eval."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from eval_corpus.adapter_runner import run_adapter_on_files
from eval_corpus.chunk_io import read_parsed_blocks_json, write_chunks_json
from eval_corpus.chunker import chunk_blocks
from eval_corpus.config import ConfigError, resolve_corpus_root
from eval_corpus.ir_models import ChunkConfig
from eval_corpus.manifest import build_manifest_payload, write_manifest
from eval_corpus.metrics_io import build_metrics_artifact, read_adapter_summary_json, write_metrics_json
from eval_corpus.scan import collect_corpus_files, normalize_extra_exts
from eval_corpus.stats import aggregate_golden_stats, write_stats_json

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


def run() -> None:
    app()


if __name__ == "__main__":
    app()
