"""Inverted index (CSR layout) built from scratch.

One FieldIndex per field ("tok", "stem", "phon"); postings are stored as
contiguous numpy arrays so BM25 scoring of a term is a vectorised slice.
"""
from __future__ import annotations

import pickle
from array import array
from collections import Counter
from pathlib import Path
from typing import Iterable

import numpy as np


class FieldIndex:
    def __init__(self, vocab, ptr, docs, tfs, doc_len):
        self.vocab: dict[str, int] = vocab
        self.ptr: np.ndarray = ptr  # term id -> slice start; len V+1
        self.docs: np.ndarray = docs
        self.tfs: np.ndarray = tfs
        self.doc_len: np.ndarray = doc_len
        self.n_docs = len(doc_len)
        self.avgdl = float(doc_len.mean()) if self.n_docs else 0.0

    @classmethod
    def build(cls, token_lists: Iterable[list[str]]) -> "FieldIndex":
        vocab: dict[str, int] = {}
        t_ids, d_ids, tfs, lens = array("i"), array("i"), array("i"), array("i")
        for d, toks in enumerate(token_lists):
            lens.append(len(toks))
            for term, tf in Counter(toks).items():
                tid = vocab.setdefault(term, len(vocab))
                t_ids.append(tid)
                d_ids.append(d)
                tfs.append(tf)
        t = np.frombuffer(t_ids, dtype=np.int32)
        order = np.argsort(t, kind="stable")  # keeps doc ids sorted within a term
        counts = np.bincount(t, minlength=len(vocab))
        ptr = np.zeros(len(vocab) + 1, dtype=np.int64)
        np.cumsum(counts, out=ptr[1:])
        return cls(
            vocab,
            ptr,
            np.frombuffer(d_ids, dtype=np.int32)[order].copy(),
            np.frombuffer(tfs, dtype=np.int32)[order].copy(),
            np.frombuffer(lens, dtype=np.int32).astype(np.float32),
        )

    def postings(self, term: str):
        tid = self.vocab.get(term)
        if tid is None:
            return None
        s, e = self.ptr[tid], self.ptr[tid + 1]
        return self.docs[s:e], self.tfs[s:e]

    def df(self, term: str) -> int:
        tid = self.vocab.get(term)
        return 0 if tid is None else int(self.ptr[tid + 1] - self.ptr[tid])


class InvertedIndex:
    """A set of named fields over the same document id space."""

    def __init__(self, doc_ids: list[str], fields: dict[str, FieldIndex]):
        self.doc_ids = doc_ids
        self.fields = fields

    def save(self, path: Path) -> None:
        with open(path, "wb") as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(path: Path) -> "InvertedIndex":
        with open(path, "rb") as f:
            return pickle.load(f)
