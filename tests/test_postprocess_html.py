"""Tests for HTML table extraction in adapter postprocess."""

from __future__ import annotations

from eval_corpus.adapters.postprocess import extract_html_tables_as_markdown, matrix_to_pipe_markdown


def test_matrix_to_pipe_markdown_basic() -> None:
    md = matrix_to_pipe_markdown([["H1", "H2"], ["a", "b"]])
    assert "| H1 | H2 |" in md
    assert "| a | b |" in md


def test_extract_html_tables_strips_and_returns_pipe_tables() -> None:
    text = "前言<table><tr><td>列1</td><td>列2</td></tr><tr><td>x</td><td>y</td></tr></table>后记"
    clean, tabs = extract_html_tables_as_markdown(text)
    assert "<table" not in clean.lower()
    assert len(tabs) == 1
    assert "列1" in tabs[0] and "x" in tabs[0]


def test_extract_html_tables_noop_without_table_tag() -> None:
    clean, tabs = extract_html_tables_as_markdown("plain **markdown** only")
    assert clean == "plain **markdown** only"
    assert tabs == []
