"""Pure helpers of the experiment driver (no index or model needed)."""
import pytest

from src.eval import significance_rows


def _pq(scores):
    return {f"q{i}": {"nDCG@10": s, "Recall@100": s} for i, s in enumerate(scores)}


def test_significance_rows_compare_each_pair_on_the_same_queries():
    per_q = {("hybrid", "roman"): _pq([0.9] * 30),
             ("dense", "roman"): _pq([0.1] * 30),
             ("bm25", "roman"): _pq([0.1] * 29 + [0.2])}
    rows = significance_rows(per_q, [("hybrid", "dense"), ("hybrid", "bm25")], ["roman"],
                             ["nDCG@10"])
    assert [(r["system"], r["vs"]) for r in rows] == [("hybrid", "dense"), ("hybrid", "bm25")]
    r = rows[0]
    assert r["variant"] == "roman" and r["metric"] == "nDCG@10"
    assert r["mean_system"] == pytest.approx(0.9) and r["mean_vs"] == pytest.approx(0.1)
    assert r["delta"] == pytest.approx(0.8)
    assert r["p_value"] < 0.001


def test_significance_identical_systems_is_not_significant():
    per_q = {("a", "native"): _pq([0.3, 0.5, 0.7]), ("b", "native"): _pq([0.3, 0.5, 0.7])}
    (r,) = significance_rows(per_q, [("a", "b")], ["native"], ["Recall@100"])
    assert r["delta"] == 0 and r["p_value"] == 1.0
