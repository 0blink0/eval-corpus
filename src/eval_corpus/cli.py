"""Typer CLI entrypoint for corpus-eval."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from eval_corpus.config import ConfigError, resolve_corpus_root
from eval_corpus.manifest import build_manifest_payload, write_manifest
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


def run() -> None:
    app()


if __name__ == "__main__":
    app()
