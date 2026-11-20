"""Dense retrieval with intfloat/multilingual-e5-small.

GPU: embed the whole corpus once (cached .npy) and search exhaustively.
CPU: only embed each query's BM25 top-N candidates (embeddings cached per passage)
     and rerank them, so the corpus is never embedded on CPU.
"""
from __future__ import annotations

import numpy as np

from src.config import load_config, path
from src.data import doc_text, load_corpus

_model = None


def device() -> str:
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(load_config()["dense"]["model"], device=device())
        if device() == "cuda":
            _model.half()
    return _model


def encode(texts: list[str], prefix: str, bs: int | None = None) -> np.ndarray:
    bs = bs or load_config()["dense"]["batch_size"]
    return model().encode([prefix + t for t in texts], batch_size=bs, normalize_embeddings=True,
                          convert_to_numpy=True, show_progress_bar=len(texts) > 5000).astype(np.float16)


class Dense:
    def __init__(self, mode: str, doc_ids: list[str]):
        self.mode, self.doc_ids = mode, doc_ids
        self.full = device() == "cuda"
        self.emb_path = path("data", "processed", mode, "e5_corpus.npy")
        self.cand_path = path("data", "processed", mode, "e5_cands.npz")
        self.emb = None
        self._cand: dict[str, np.ndarray] = {}
        if self.full:
            if self.emb_path.exists():
                self.emb = np.load(self.emb_path)
            else:
                corpus = load_corpus(mode)
                assert [d["docid"] for d in corpus] == doc_ids
                self.emb = encode([doc_text(d) for d in corpus], "passage: ")
                np.save(self.emb_path, self.emb)
            self._emb_t = None
        elif self.cand_path.exists():
            z = np.load(self.cand_path)
            self._cand = dict(zip(z["ids"].tolist(), z["emb"]))

    def search_many(self, queries: list[str], k: int = 100,
                    candidates: list[list[str]] | None = None) -> list[list[tuple[str, float]]]:
        q = encode(queries, "query: ")
        if self.full:
            import torch

            if self._emb_t is None:
                self._emb_t = torch.from_numpy(self.emb).to("cuda")
            out = []
            qt = torch.from_numpy(q).to("cuda")
            for i in range(0, len(queries), 256):
                s = qt[i:i + 256] @ self._emb_t.T
                v, ix = torch.topk(s.float(), k, dim=1)
                for vv, ii in zip(v.cpu().numpy(), ix.cpu().numpy()):
                    out.append([(self.doc_ids[j], float(x)) for j, x in zip(ii, vv)])
            return out
        assert candidates is not None, "CPU mode needs BM25 candidates to rerank"
        self._embed_candidates({d for c in candidates for d in c})
        out = []
        for qi, cands in zip(q, candidates):
            if not cands:
                out.append([])
                continue
            m = np.stack([self._cand[d] for d in cands]).astype(np.float32)
            s = m @ qi.astype(np.float32)
            order = np.argsort(-s)[:k]
            out.append([(cands[j], float(s[j])) for j in order])
        return out

    def _embed_candidates(self, ids: set[str]) -> None:
        todo = sorted(ids - self._cand.keys())
        if not todo:
            return
        by_id = {d["docid"]: d for d in load_corpus(self.mode)}
        embs = encode([doc_text(by_id[d]) for d in todo], "passage: ")
        self._cand.update(zip(todo, embs))
        np.savez(self.cand_path, ids=np.array(list(self._cand)), emb=np.stack(list(self._cand.values())))
