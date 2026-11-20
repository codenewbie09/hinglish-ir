"""Okapi BM25 over a FieldIndex, with per-term score breakdown."""
from __future__ import annotations

import math

import numpy as np

from src.index import FieldIndex


class BM25:
    def __init__(self, index: FieldIndex, k1: float = 1.2, b: float = 0.75):
        self.ix, self.k1, self.b = index, k1, b
        # per-document length normaliser, precomputed once
        self._norm = k1 * (1 - b + b * index.doc_len / max(index.avgdl, 1e-9))

    def idf(self, term: str) -> float:
        n, df = self.ix.n_docs, self.ix.df(term)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def score(self, terms: list[str], weights: list[float] | None = None) -> np.ndarray:
        scores = np.zeros(self.ix.n_docs, dtype=np.float32)
        weights = weights or [1.0] * len(terms)
        for term, w in zip(terms, weights):
            p = self.ix.postings(term)
            if p is None or w == 0:
                continue
            docs, tf = p
            scores[docs] += w * self.idf(term) * tf * (self.k1 + 1) / (tf + self._norm[docs])
        return scores

    def search(self, terms, k=100, weights=None) -> list[tuple[int, float]]:
        return top_k(self.score(terms, weights), k)

    def explain(self, terms, doc: int, weights=None) -> dict[str, float]:
        """Contribution of each query term to `doc`'s score (sums to the score)."""
        weights = weights or [1.0] * len(terms)
        out: dict[str, float] = {}
        for term, w in zip(terms, weights):
            p = self.ix.postings(term)
            c = 0.0
            if p is not None:
                docs, tf = p
                hit = np.searchsorted(docs, doc)
                if hit < len(docs) and docs[hit] == doc:
                    t = float(tf[hit])
                    c = w * self.idf(term) * t * (self.k1 + 1) / (t + float(self._norm[doc]))
            out[term] = out.get(term, 0.0) + c
        return out


def top_k(scores: np.ndarray, k: int) -> list[tuple[int, float]]:
    nz = np.flatnonzero(scores)
    if len(nz) == 0:
        return []
    k = min(k, len(nz))
    sel = nz[np.argpartition(-scores[nz], k - 1)[:k]]
    sel = sel[np.argsort(-scores[sel], kind="stable")]
    return [(int(d), float(scores[d])) for d in sel]
