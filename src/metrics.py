"""IR metrics (binary/graded relevance) and a paired randomisation test."""
from __future__ import annotations

import math

import numpy as np


def _rel(ranked, qrels, k):
    return [qrels.get(d, 0) for d in ranked[:k]]


def precision_at_k(ranked, qrels, k):
    return sum(r > 0 for r in _rel(ranked, qrels, k)) / k


def recall_at_k(ranked, qrels, k):
    n_rel = sum(v > 0 for v in qrels.values())
    return sum(r > 0 for r in _rel(ranked, qrels, k)) / n_rel if n_rel else 0.0


def f1_at_k(ranked, qrels, k):
    p, r = precision_at_k(ranked, qrels, k), recall_at_k(ranked, qrels, k)
    return 2 * p * r / (p + r) if p + r else 0.0


def ndcg_at_k(ranked, qrels, k):
    dcg = sum((2**r - 1) / math.log2(i + 2) for i, r in enumerate(_rel(ranked, qrels, k)))
    ideal = sorted((v for v in qrels.values() if v > 0), reverse=True)[:k]
    idcg = sum((2**r - 1) / math.log2(i + 2) for i, r in enumerate(ideal))
    return dcg / idcg if idcg else 0.0


def mrr_at_k(ranked, qrels, k):
    for i, r in enumerate(_rel(ranked, qrels, k)):
        if r > 0:
            return 1 / (i + 1)
    return 0.0


METRICS = {
    "P@5": lambda r, q: precision_at_k(r, q, 5),
    "P@10": lambda r, q: precision_at_k(r, q, 10),
    "R@10": lambda r, q: recall_at_k(r, q, 10),
    "F1@10": lambda r, q: f1_at_k(r, q, 10),
    "Recall@100": lambda r, q: recall_at_k(r, q, 100),
    "nDCG@10": lambda r, q: ndcg_at_k(r, q, 10),
    "MRR@10": lambda r, q: mrr_at_k(r, q, 10),
}


def evaluate_run(run: dict[str, list[str]], qrels: dict[str, dict[str, int]]) -> dict:
    """run: qid -> ranked doc ids. Queries without a positive judgment are skipped."""
    per_q = {}
    for qid, rels in qrels.items():
        if not any(v > 0 for v in rels.values()):
            continue
        ranked = run.get(qid, [])
        per_q[qid] = {m: f(ranked, rels) for m, f in METRICS.items()}
    mean = {m: float(np.mean([v[m] for v in per_q.values()])) for m in METRICS}
    return {"mean": mean, "per_query": per_q}


def randomisation_test(a: list[float], b: list[float], n: int = 10000, seed: int = 42) -> float:
    """Two-sided paired randomisation (sign-flip) test on per-query scores."""
    d = np.asarray(a) - np.asarray(b)
    obs = abs(d.mean())
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1.0, 1.0], size=(n, len(d)))
    perm = np.abs((signs * d).mean(axis=1))
    return float((np.sum(perm >= obs - 1e-12) + 1) / (n + 1))
