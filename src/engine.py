"""One search entry point for the CLI and the Streamlit demo (all systems)."""
from __future__ import annotations

import json

from src.config import ROOT
from src.data import load_corpus
from src.fusion import rrf
from src.pipeline import SYSTEMS, Searcher, system_config

ALL_SYSTEMS = list(SYSTEMS) + ["dense", "hybrid"]


def _hybrid_params() -> dict:
    p = ROOT / "results" / "tuned.json"
    default = {"k": 60, "w_dense": 1.0, "dense_text": "raw"}
    return json.loads(p.read_text()).get("hybrid", default) if p.exists() else default


class Engine:
    def __init__(self, mode: str = "sample"):
        self.mode = mode
        self.searcher = Searcher(mode)
        self.corpus = {d["docid"]: d for d in load_corpus(mode)}
        self._dense = None

    @property
    def dense(self):
        if self._dense is None:
            from src.dense import Dense

            self._dense = Dense(self.mode, self.searcher.index.doc_ids)
        return self._dense

    def _dense_hits(self, query: str, k: int, cands: list[str] | None):
        from src import normalise

        text = query
        if _hybrid_params()["dense_text"] == "deva":
            text = normalise.to_devanagari(query)
        return self.dense.search_many([text], k, [cands] if cands is not None else None)[0]

    def search(self, query: str, system: str = "full", k: int = 5, explain: bool = True) -> dict:
        """Returns {'repr': QueryRepr, 'hits': [{docid, score, title, text, terms}], 'warnings': [..]}"""
        bm25_sys = "full" if system in ("dense", "hybrid") else system
        warnings: list[str] = []
        q, bm = self.searcher.search(query, bm25_sys, k=100)
        for t in q.tokens:
            if t.get("warning"):
                warnings.append(f"{t['token']}: {t['warning']}")
        if system == "dense":
            hits = self._dense_hits(query, k, None if self.dense.full else [d for d, _ in bm])
        elif system == "hybrid":
            p = _hybrid_params()
            dn = self._dense_hits(query, 100, None if self.dense.full else [d for d, _ in bm])
            hits = rrf([[d for d, _ in bm], [d for d, _ in dn]], [1.0, p["w_dense"]], k=p["k"])
        else:
            hits = bm
        out = []
        for docid, score in hits[:k]:
            d = self.corpus[docid]
            terms = self.searcher.explain(q, docid, bm25_sys) if explain else {}
            out.append({"docid": docid, "score": score, "title": d["title"], "text": d["text"],
                        "terms": {t: c for t, c in terms.items() if c > 0}})
        return {"repr": q, "hits": out, "system": system, "config": system_config(bm25_sys),
                "warnings": warnings}
