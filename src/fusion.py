"""Weighted Reciprocal Rank Fusion."""
from __future__ import annotations


def rrf(runs: list[list[str]], weights: list[float] | None = None, k: int = 60,
        depth: int = 100) -> list[tuple[str, float]]:
    weights = weights or [1.0] * len(runs)
    score: dict[str, float] = {}
    for run, w in zip(runs, weights):
        for r, d in enumerate(run[:depth]):
            score[d] = score.get(d, 0.0) + w / (k + r + 1)
    return sorted(score.items(), key=lambda x: -x[1])[:depth]
