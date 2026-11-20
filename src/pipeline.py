"""Systems = named combinations of query-processing components over the BM25 index.

A query is turned into a QueryRepr: weighted terms per index field. Scoring is
sum_f field_weight[f] * BM25_f(terms_f, weights_f).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from src import text
from src.bm25 import BM25, top_k
from src.config import corpus_mode, load_config
from src.index import InvertedIndex

COMPONENTS = ("translit", "phonetic", "expansion", "stemming")

# Cumulative systems for the main table; "full" = all components.
SYSTEMS: dict[str, dict] = {
    "bm25": {},
    "+translit": {"translit": True},
    "+phonetic": {"translit": True, "phonetic": True},
    "+expansion": {"translit": True, "phonetic": True, "expansion": True},
    "full": {"translit": True, "phonetic": True, "expansion": True, "stemming": True},
}
DEFAULTS = {
    "translit": False, "phonetic": False, "expansion": False, "stemming": False,
    "stopwords": True,
    "phon_weight": 0.3,      # weight of the phonetic field (tuned on train)
    "latin_keep_weight": 1.0,  # original Latin token when transliterated
    "expansion_weight": 0.5,   # Hindi equivalent of an English token
    "english_keep_weight": 1.0,  # original token when the lexicon says it is English
    "translit_top2_weight": 0.0,  # second IndicXlit candidate
}


def system_config(name_or_cfg) -> dict:
    """Defaults < tuned weights (results/tuned.json, fitted on train) < system/explicit cfg."""
    import json

    from src.config import ROOT

    cfg = dict(DEFAULTS)
    tuned = ROOT / "results" / "tuned.json"
    if tuned.exists():
        cfg.update(json.loads(tuned.read_text()).get("pipeline", {}))
    cfg.update(SYSTEMS[name_or_cfg] if isinstance(name_or_cfg, str) else name_or_cfg)
    return cfg


@dataclass
class QueryRepr:
    raw: str
    tokens: list[dict] = field(default_factory=list)  # per-token trace for --explain
    terms: dict[str, list[tuple[str, float]]] = field(default_factory=dict)  # field -> [(term, w)]

    def add(self, fld: str, term: str, w: float) -> None:
        self.terms.setdefault(fld, []).append((term, w))

    def normalised_text(self) -> str:
        main = "stem" if "stem" in self.terms else "tok"
        return " ".join(t for t, _ in self.terms.get(main, []))


class Searcher:
    def __init__(self, mode: str | None = None, index: InvertedIndex | None = None):
        from src.build_index import index_path

        cfg = load_config()
        self.mode = mode or corpus_mode()
        self.index = index or InvertedIndex.load(index_path(self.mode))
        k1, b = cfg["bm25"]["k1"], cfg["bm25"]["b"]
        self.bm25 = {f: BM25(ix, k1, b) for f, ix in self.index.fields.items()}

    # ---- query side -------------------------------------------------
    def represent(self, query: str, system="bm25") -> QueryRepr:
        from src import normalise

        cfg = system_config(system)
        q = QueryRepr(raw=query)
        toks = text.tokenize(query)
        if cfg["stopwords"]:
            toks = text.remove_stopwords(toks)
        main = "stem" if cfg["stemming"] else "tok"

        def emit(term: str, w: float):
            if cfg["stopwords"] and term in text.STOPWORDS:
                return
            q.add(main, text.stem(term) if cfg["stemming"] else term, w)
            if cfg["phonetic"]:
                from src.phonetic import phonetic_key

                q.add("phon", phonetic_key(term), w)

        for tok in toks:
            info = normalise.normalise_token(tok, cfg)
            q.tokens.append(info)
            for term, w in info["terms"]:
                for sub in text.tokenize(term):  # expansions may be multi-word
                    emit(sub, w)
        return q

    # ---- scoring ----------------------------------------------------
    def score(self, q: QueryRepr, system="bm25") -> np.ndarray:
        cfg = system_config(system)
        total = np.zeros(len(self.index.doc_ids), dtype=np.float32)
        for fld, tw in q.terms.items():
            fw = cfg["phon_weight"] if fld == "phon" else 1.0
            terms, ws = [t for t, _ in tw], [w * fw for _, w in tw]
            total += self.bm25[fld].score(terms, ws)
        return total

    def search(self, query: str, system="bm25", k: int = 100):
        q = self.represent(query, system)
        hits = top_k(self.score(q, system), k)
        return q, [(self.index.doc_ids[d], s) for d, s in hits]

    def explain(self, q: QueryRepr, docid: str, system="bm25") -> dict[str, float]:
        cfg = system_config(system)
        d = self.index.doc_ids.index(docid)
        out: dict[str, float] = {}
        for fld, tw in q.terms.items():
            fw = cfg["phon_weight"] if fld == "phon" else 1.0
            for term, c in self.bm25[fld].explain([t for t, _ in tw], d, [w * fw for _, w in tw]).items():
                out[f"{fld}:{term}"] = c
        return out
