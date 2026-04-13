"""Synthetic sample generation for smoke/regression use."""

from __future__ import annotations

import random
from pathlib import Path

from eval_corpus.synthetic_data.models import (
    SyntheticDataConfig,
    SyntheticManifest,
    SyntheticSample,
)

_WORDS = [
    "招标",
    "评审",
    "采购",
    "合同",
    "热费",
    "宣传品",
    "归档",
    "合规",
    "执行",
    "通知",
]


def _allocate_counts(config: SyntheticDataConfig) -> dict[str, int]:
    kinds = ("text", "scan", "table")
    raw = {
        kind: config.total_samples * config.type_ratio[kind] / sum(config.type_ratio.values())
        for kind in kinds
    }
    counts = {kind: int(raw[kind]) for kind in kinds}
    remain = config.total_samples - sum(counts.values())
    for kind in sorted(kinds, key=lambda k: raw[k] - counts[k], reverse=True):
        if remain <= 0:
            break
        counts[kind] += 1
        remain -= 1
    return counts


def _build_text(rng: random.Random, min_len: int, max_len: int) -> str:
    target = rng.randint(min_len, max_len)
    chunks: list[str] = []
    while len("".join(chunks)) < target:
        chunks.append(rng.choice(_WORDS))
    return "".join(chunks)[:target]


def _sample_content(sample_type: str, idx: int, rng: random.Random, config: SyntheticDataConfig) -> str:
    if sample_type == "text":
        return f"[TEXT]\n样本{idx}\n{_build_text(rng, config.min_text_length, config.max_text_length)}\n"
    if sample_type == "scan":
        return (
            "[SCAN]\n"
            f"PAGE:1\nOCR_BLOCK:{_build_text(rng, config.min_text_length, config.max_text_length)}\n"
        )
    return (
        "[TABLE]\n"
        "col_a,col_b,col_c\n"
        f"{idx},{rng.randint(100, 999)},{rng.choice(_WORDS)}\n"
        f"{idx+1},{rng.randint(100, 999)},{rng.choice(_WORDS)}\n"
    )


def generate_synthetic_dataset(output_dir: Path, config: SyntheticDataConfig) -> SyntheticManifest:
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(config.seed)
    counts = _allocate_counts(config)
    items: list[SyntheticSample] = []
    running_idx = 0

    for sample_type in ("text", "scan", "table"):
        kind_dir = output_dir / sample_type
        kind_dir.mkdir(parents=True, exist_ok=True)
        for _ in range(counts[sample_type]):
            running_idx += 1
            file_name = f"{sample_type}_{running_idx:04d}.txt"
            path = kind_dir / file_name
            path.write_text(
                _sample_content(sample_type, running_idx, rng, config),
                encoding="utf-8",
            )
            items.append(
                SyntheticSample(
                    sample_id=f"{sample_type}-{running_idx:04d}",
                    sample_type=sample_type,
                    relative_path=path.relative_to(output_dir).as_posix(),
                )
            )

    return SyntheticManifest(seed=config.seed, total_samples=config.total_samples, items=items)
