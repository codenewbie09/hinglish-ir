"""Variants, LLM parsing, transliteration cache and dense reranking, with fakes (no network/model)."""
import json

import numpy as np
import pytest

from src import dense, llm, variants, xlit


# ---- variants ------------------------------------------------------------------------
def test_rule_roman_is_deterministic_casual_romanisation():
    assert variants.rule_roman("कांग्रेस दल का नेता कौन है ?") == "kangres dal ka neta kaun hai"
    assert variants.rule_roman("ज़मीन") == variants.rule_roman("जमीन")  # nukta dropped


def test_llm_batch_keeps_only_complete_items(monkeypatch):
    reply = {"items": [
        {"id": "q1", "roman": "neta kaun", "mix25": "a", "mix50": "b", "mix75": "c"},
        {"id": "q2", "roman": "x", "mix25": "", "mix50": "b", "mix75": "c"},   # empty field
        {"id": "q3", "roman": "x"},                                            # missing fields
    ]}
    monkeypatch.setattr(variants, "chat", lambda *a, **k: json.dumps(reply))
    got = variants._llm_batch([("q1", "नेता कौन"), ("q2", "..."), ("q3", "...")], "m")
    assert list(got) == ["q1"] and got["q1"]["roman"] == "neta kaun"


def test_tuning_subset_is_fixed_and_sized_by_config(monkeypatch):
    monkeypatch.setattr(variants, "load_queries", lambda split: {f"t{i}": "" for i in range(1000)})
    a, b = variants.tuning_qids(), variants.tuning_qids()
    assert a == b and len(a) == variants.load_config()["tune_queries"] and a == sorted(a)


# ---- llm.parse_json ------------------------------------------------------------------
@pytest.mark.parametrize("raw,expected", [
    ('{"a": 1}', {"a": 1}),
    ('Sure! here it is:\n{"a": 1}\nthanks', {"a": 1}),   # prose around the object
    ("[1, 2]", {}),                                      # not an object
    ("no json at all", {}),
])
def test_parse_json_is_best_effort(raw, expected):
    assert llm.parse_json(raw) == expected


# ---- xlit cache ----------------------------------------------------------------------
def test_xlit_serves_cache_and_returns_empty_without_backend(monkeypatch):
    monkeypatch.setattr(xlit, "_cache", {"neta": ["नेता", "नीता"]})
    monkeypatch.setattr(xlit, "available", lambda: False)
    monkeypatch.setattr(xlit, "_worker", lambda: pytest.fail("worker must not start"))
    assert xlit.transliterate(["neta", "zzz"]) == {"neta": ["नेता", "नीता"], "zzz": []}


# ---- dense, CPU rerank path ----------------------------------------------------------
def test_dense_cpu_reranks_candidates_and_caches_embeddings(monkeypatch, tmp_path):
    vecs = {"query: q": [1, 0], "passage: A a": [0, 1], "passage: B b": [1, 0],
            "passage: C c": [0.6, 0.8]}
    calls = []

    def fake_encode(texts, prefix, bs=None):
        calls.append(len(texts))
        return np.array([vecs[prefix + t] for t in texts], dtype=np.float16)

    corpus = [{"docid": d, "title": d, "text": d.lower()} for d in "ABC"]
    monkeypatch.setattr(dense, "device", lambda: "cpu")
    monkeypatch.setattr(dense, "encode", fake_encode)
    monkeypatch.setattr(dense, "load_corpus", lambda mode: corpus)
    monkeypatch.setattr(dense, "path", lambda *p: tmp_path / p[-1])

    d = dense.Dense("toy", ["A", "B", "C"])
    assert not d.full
    (hits,) = d.search_many(["q"], k=2, candidates=[["A", "B", "C"]])
    assert [h[0] for h in hits] == ["B", "C"]               # cosine with the query vector
    assert (tmp_path / "e5_cands.npz").exists()
    # a second instance loads the cached passage embeddings: only the query is encoded
    calls.clear()
    dense.Dense("toy", ["A", "B", "C"]).search_many(["q"], k=1, candidates=[["C"]])
    assert calls == [1]


def test_dense_cpu_needs_candidates(monkeypatch, tmp_path):
    monkeypatch.setattr(dense, "device", lambda: "cpu")
    monkeypatch.setattr(dense, "encode", lambda t, p, bs=None: np.zeros((len(t), 2), np.float16))
    monkeypatch.setattr(dense, "path", lambda *p: tmp_path / p[-1])
    with pytest.raises(AssertionError):
        dense.Dense("toy", []).search_many(["q"])
