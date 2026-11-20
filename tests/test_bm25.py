import math

import numpy as np
import pytest

from src.bm25 import BM25
from src.index import FieldIndex

DOCS = [
    ["भारत", "की", "राजधानी", "दिल्ली", "है"],
    ["दिल्ली", "दिल्ली", "शहर"],
    ["गंगा", "नदी", "भारत", "में", "है"],
]


@pytest.fixture
def bm25():
    return BM25(FieldIndex.build(DOCS), k1=1.2, b=0.75)


def manual(tf, dl, avgdl, df, n, k1=1.2, b=0.75):
    idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
    return idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))


def test_score_matches_formula(bm25):
    s = bm25.score(["दिल्ली"])
    avgdl = (5 + 3 + 5) / 3
    assert s[0] == pytest.approx(manual(1, 5, avgdl, 2, 3))
    assert s[1] == pytest.approx(manual(2, 3, avgdl, 2, 3))
    assert s[2] == 0


def test_ranking_and_unknown_terms(bm25):
    assert [d for d, _ in bm25.search(["दिल्ली", "शहर"], k=3)][:1] == [1]
    assert bm25.search(["अज्ञात"], k=3) == []


def test_explain_sums_to_score(bm25):
    q = ["भारत", "दिल्ली"]
    parts = bm25.explain(q, 0)
    assert sum(parts.values()) == pytest.approx(bm25.score(q)[0])
    assert set(parts) == set(q)


def test_query_weights(bm25):
    base = bm25.score(["भारत"])
    half = bm25.score(["भारत"], weights=[0.5])
    assert np.allclose(half, base * 0.5)
