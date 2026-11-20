import pytest

from src.metrics import evaluate_run, ndcg_at_k


def test_ndcg_perfect_and_partial():
    qrels = {"d1": 1, "d2": 1}
    assert ndcg_at_k(["d1", "d2", "x"], qrels, 10) == pytest.approx(1.0)
    assert 0 < ndcg_at_k(["x", "d1"], qrels, 10) < 1


def test_evaluate_run():
    run = {"q": ["x", "d1", "d2"]}
    qrels = {"q": {"d1": 1, "d2": 1, "d3": 0}}
    m = evaluate_run(run, qrels)["mean"]
    assert m["MRR@10"] == pytest.approx(0.5)
    assert m["P@5"] == pytest.approx(2 / 5)
    assert m["Recall@100"] == pytest.approx(1.0)


def test_evaluate_run_restricted_to_query_subset():
    qrels = {"q1": {"d": 1}, "q2": {"d": 1}}
    run = {"q1": ["d"]}
    assert evaluate_run(run, qrels)["mean"]["nDCG@10"] == pytest.approx(0.5)  # missing q2 = 0
    assert evaluate_run(run, qrels, qids=["q1"])["mean"]["nDCG@10"] == pytest.approx(1.0)
