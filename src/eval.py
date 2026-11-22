"""Experiments. Writes CSV/PNG/MD to results/.

    python -m src.eval sanity|baseline|tune|main|significance|examples|all [--sample|--full]
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import pandas as pd

from src.config import ROOT, load_config, path, seed_everything
from src.data import add_mode_flags, apply_mode, load_corpus, load_qrels
from src.bm25 import top_k
from src.fusion import rrf
from src.metrics import evaluate_run, randomisation_test
from src.pipeline import DEFAULTS, SYSTEMS, Searcher, system_config
from src.variants import load_variants, queries_for

RESULTS = ROOT / "results"
LEVELS = ["native", "roman", "mix25", "mix50", "mix75"]
ALL_VARIANTS = LEVELS + ["roman_rule"]
MAIN_METRICS = ["P@5", "P@10", "R@10", "F1@10", "Recall@100", "nDCG@10", "MRR@10"]
TUNED_PATH = RESULTS / "tuned.json"


def tuned() -> dict:
    return json.loads(TUNED_PATH.read_text()) if TUNED_PATH.exists() else {}


class Evaluator:
    def __init__(self, mode: str):
        self.mode = mode
        self.s = Searcher(mode)
        self.qrels = {"dev": load_qrels("dev"), "train": load_qrels("train")}
        self._dense = None
        self._cache: dict = {}

    # ------------------------------------------------------------ runs
    def bm25_run(self, system, split, variant, k=100) -> dict[str, list[str]]:
        cfg = system_config(system)
        key = ("bm25", json.dumps(cfg, sort_keys=True), split, variant)
        if key not in self._cache:
            from src import normalise

            qs = queries_for(split, variant)
            normalise.prefetch(list(qs.values()), cfg)
            self._cache[key] = {qid: [d for d, _ in self.s.search(q, cfg, k)[1]] for qid, q in qs.items()}
        return self._cache[key]

    @property
    def dense(self):
        if self._dense is None:
            from src.dense import Dense

            self._dense = Dense(self.mode, self.s.index.doc_ids)
        return self._dense

    def dense_run(self, split, variant, text="raw", k=100) -> dict[str, list[str]]:
        key = ("dense", text, split, variant)
        if key not in self._cache:
            from src import normalise

            qs = queries_for(split, variant)
            if text == "deva":
                normalise.prefetch(list(qs.values()), {"translit": True})
                qs = {q: normalise.to_devanagari(t) for q, t in qs.items()}
            cands = None
            if not self.dense.full:  # CPU: rerank the full pipeline's BM25 top-100
                full = self.bm25_run("full", split, variant)
                cands = [full[q] for q in qs]
            res = self.dense.search_many(list(qs.values()), k, cands)
            self._cache[key] = {q: [d for d, _ in r] for q, r in zip(qs, res)}
        return self._cache[key]

    def hybrid_run(self, split, variant, p: dict | None = None,
                   bm25_cfg="full") -> dict[str, list[str]]:
        """bm25_cfg: the BM25 side; tuning passes the weights it just chose explicitly."""
        p = p or tuned().get("hybrid", {"k": 60, "w_dense": 1.0, "dense_text": "raw"})
        a = self.bm25_run(bm25_cfg, split, variant)
        b = self.dense_run(split, variant, p["dense_text"])
        return {q: [d for d, _ in rrf([a[q], b.get(q, [])], [1.0, p["w_dense"]], k=p["k"])] for q in a}

    def run(self, system, split, variant):
        if system == "dense":
            return self.dense_run(split, variant, tuned().get("hybrid", {}).get("dense_text", "raw"))
        if system == "hybrid":
            return self.hybrid_run(split, variant)
        return self.bm25_run(system, split, variant)

    def score(self, run, split):
        # evaluate exactly the split's query set (train = the fixed tuning subset)
        return evaluate_run(run, self.qrels[split], qids=queries_for(split, "native"))


# ------------------------------------------------------------------ helpers
def _table(ev: Evaluator, systems, variants, split="dev"):
    rows, per_q = [], {}
    for sysn in systems:
        for v in variants:
            t0 = time.time()
            r = ev.score(ev.run(sysn, split, v), split)
            per_q[(sysn, v)] = r["per_query"]
            rows.append({"system": sysn, "variant": v, **r["mean"]})
            print(f"  {sysn:12s} {v:10s} nDCG@10={r['mean']['nDCG@10']:.3f} "
                  f"R@100={r['mean']['Recall@100']:.3f} ({time.time()-t0:.1f}s)", flush=True)
    return pd.DataFrame(rows), per_q


# system vs baseline pairs for the paired randomisation test
SIG_PAIRS = [("full", "bm25"), ("hybrid", "bm25"), ("hybrid", "dense"), ("hybrid", "full")]


def significance_rows(per_q, pairs, variants, metrics=("nDCG@10", "Recall@100")) -> list[dict]:
    """Paired randomisation test per (system, baseline, variant, metric) on shared queries."""
    rows = []
    for sysn, base in pairs:
        for v in variants:
            a, b = per_q[(sysn, v)], per_q[(base, v)]
            qs = sorted(a.keys() & b.keys())
            for m in metrics:
                xa, xb = [a[q][m] for q in qs], [b[q][m] for q in qs]
                rows.append({"system": sysn, "vs": base, "variant": v, "metric": m,
                             "mean_system": float(np.mean(xa)), "mean_vs": float(np.mean(xb)),
                             "delta": float(np.mean(xa) - np.mean(xb)),
                             "p_value": randomisation_test(xa, xb)})
    return rows


def _pivot(df, metric):
    p = df.pivot(index="system", columns="variant", values=metric)
    return p.loc[list(dict.fromkeys(df["system"])), [c for c in ALL_VARIANTS if c in p.columns]]


def _save(df, name):
    df.to_csv(path("results", name), float_format="%.4f")
    print(f"-> results/{name}")


def plot_degradation(df, name, title):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, metric in zip(axes, ["nDCG@10", "Recall@100"]):
        p = _pivot(df, metric)
        for sysn, row in p.iterrows():
            ax.plot(LEVELS, [row[v] for v in LEVELS], marker="o", label=sysn)
        ax.set_title(metric)
        ax.set_xlabel("query variant (code-mixing level)")
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path("results", name), dpi=150)
    plt.close(fig)
    print(f"-> results/{name}")


# ------------------------------------------------------------------ commands
def lucene_search(searcher: Searcher, query: str, k: int = 100) -> list[str]:
    """BM25 over the Lucene-style index, query analysed by the same Lucene chain."""
    from src.lucene_hindi import analyse
    from src.pipeline import QueryRepr

    q = QueryRepr(raw=query, terms={"tok": [(t, 1.0) for t in analyse(query)]})
    return [searcher.index.doc_ids[d] for d, _ in top_k(searcher.score(q, "bm25"), k)]


def cmd_sanity(ev: Evaluator):
    """Native-script BM25 on dev: our default settings, and the MIRACL paper's k1/b."""
    from src.variants import queries_for

    qs = queries_for("dev", "native")
    paper = Searcher(ev.mode, index=ev.s.index, k1=0.9, b=0.4)
    setups = [("k1=1.2 b=0.75, no stemming (our default)", ev.s, "bm25"),
              ("k1=1.2 b=0.75, stemming", ev.s, {"stemming": True}),
              ("k1=0.9 b=0.4, no stemming (paper k1/b)", paper, "bm25"),
              ("k1=0.9 b=0.4, stemming (paper k1/b)", paper, {"stemming": True})]
    rows, lines = [], [f"mode={ev.mode}: native-script BM25 on MIRACL-hi dev ({len(qs)} queries)"]
    for label, searcher, system in setups:
        run = {q: [d for d, _ in searcher.search(t, system, 100)[1]] for q, t in qs.items()}
        m = ev.score(run, "dev")["mean"]
        rows.append({"setup": label, **m})
        lines.append(f"  {label:42s} nDCG@10={m['nDCG@10']:.3f} Recall@100={m['Recall@100']:.3f}")
    from src.build_index import index_path
    from src.index import InvertedIndex

    if index_path(ev.mode, lucene=True).exists():  # make index-lucene
        lu = Searcher(ev.mode, index=InvertedIndex.load(index_path(ev.mode, lucene=True)), k1=0.9, b=0.4)
        label = "k1=0.9 b=0.4, Lucene Hindi analyser (port)"
        m = ev.score({q: lucene_search(lu, t) for q, t in qs.items()}, "dev")["mean"]
        rows.append({"setup": label, **m})
        lines.append(f"  {label:42s} nDCG@10={m['nDCG@10']:.3f} Recall@100={m['Recall@100']:.3f}")
    lines.append("  MIRACL paper (Zhang et al. 2023), BM25 hi dev  nDCG@10=0.458 Recall@100=0.868"
                 " (Anserini, Lucene Hindi analyser, k1=0.9 b=0.4)")
    print("\n".join(lines))
    path("results", f"sanity_{ev.mode}.txt").write_text("\n".join(lines) + "\n")
    pd.DataFrame(rows).to_csv(path("results", f"sanity_{ev.mode}.csv"), index=False,
                              float_format="%.4f")


def cmd_baseline(ev: Evaluator):
    df, _ = _table(ev, ["bm25"], ALL_VARIANTS)
    _save(df.set_index(["system", "variant"]), f"baseline_{ev.mode}.csv")
    plot_degradation(df, f"baseline_degradation_{ev.mode}.png", "BM25 baseline vs query variant")


def cmd_tune(ev: Evaluator):
    """Coordinate ascent on the train subset; objective = mean nDCG@10 over all levels."""
    def obj(fn):
        return float(np.mean([ev.score(fn(v), "train")["mean"]["nDCG@10"] for v in LEVELS]))

    best = {k: {**DEFAULTS, **SYSTEMS["full"]}[k] for k in
            ("phon_weight", "latin_keep_weight", "expansion_weight", "translit_top2_weight")}
    best.setdefault("translit_top2_weight", 0.0)
    grid = {"latin_keep_weight": [0.0, 0.3, 0.6, 1.0], "phon_weight": [0.0, 0.1, 0.2, 0.3, 0.5],
            "expansion_weight": [0.25, 0.5, 1.0], "translit_top2_weight": [0.0, 0.3]}
    log = []
    for _ in range(2):
        for param, values in grid.items():
            scores = {}
            for val in values:
                cfg = {**DEFAULTS, **SYSTEMS["full"], **best, param: val}
                scores[val] = obj(lambda v: ev.bm25_run(cfg, "train", v))
                log.append({"stage": "bm25", "param": param, "value": val, "nDCG@10": scores[val]})
                print(f"  {param}={val}: {scores[val]:.4f}", flush=True)
            best[param] = max(scores, key=scores.get)
    # hybrid is tuned on top of the BM25 weights chosen above, never on tuned.json from disk
    full_cfg = {**DEFAULTS, **SYSTEMS["full"], **best}
    hy, hy_scores = None, {}
    for text in ["raw", "deva"]:
        for k in [10, 30, 60, 100]:
            for w in [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]:
                p = {"k": k, "w_dense": w, "dense_text": text}
                sc = obj(lambda v: ev.hybrid_run("train", v, p, bm25_cfg=full_cfg))
                log.append({"stage": "hybrid", "param": json.dumps(p), "value": None, "nDCG@10": sc})
                hy_scores[json.dumps(p)] = sc
    hy = json.loads(max(hy_scores, key=hy_scores.get))
    print("  best hybrid", hy, f"{max(hy_scores.values()):.4f}")
    out = {"pipeline": best, "hybrid": hy, "objective": "mean train nDCG@10 over " + ",".join(LEVELS),
           "train_queries": load_config()["tune_queries"], "mode": ev.mode}
    TUNED_PATH.write_text(json.dumps(out, indent=2))
    _save(pd.DataFrame(log), f"tuning_{ev.mode}.csv")
    print("tuned:", out)


def cmd_main(ev: Evaluator):
    systems = list(SYSTEMS) + ["dense", "hybrid"]
    df, per_q = _table(ev, systems, ALL_VARIANTS)
    _save(df.set_index(["system", "variant"]), f"main_long_{ev.mode}.csv")
    for m in ["nDCG@10", "Recall@100", "P@10", "F1@10", "MRR@10"]:
        _save(_pivot(df, m), f"main_{m.replace('@', '')}_{ev.mode}.csv")
    plot_degradation(df, f"degradation_{ev.mode}.png", "Retrieval vs code-mixing level")

    # ablation: drop one component from full
    rows = []
    for comp in ["translit", "phonetic", "expansion", "stemming", "stopwords"]:
        cfg = {**SYSTEMS["full"], comp: False}
        for v in ALL_VARIANTS:
            m = ev.score(ev.bm25_run(cfg, "dev", v), "dev")["mean"]
            rows.append({"ablation": f"full - {comp}", "variant": v, **m})
    for v in ALL_VARIANTS:
        rows.append({"ablation": "full", "variant": v, **ev.score(ev.bm25_run("full", "dev", v), "dev")["mean"]})
    ab = pd.DataFrame(rows)
    _save(ab.set_index(["ablation", "variant"]), f"ablation_long_{ev.mode}.csv")
    _save(ab.pivot(index="ablation", columns="variant", values="nDCG@10")[ALL_VARIANTS],
          f"ablation_nDCG10_{ev.mode}.csv")

    _save(pd.DataFrame(significance_rows(per_q, SIG_PAIRS, ALL_VARIANTS)),
          f"significance_{ev.mode}.csv")
    cmd_failures(ev, per_q)


def cmd_significance(ev: Evaluator):
    """Only the significance table (reuses cached runs; no full main table)."""
    systems = list(dict.fromkeys(x for pair in SIG_PAIRS for x in pair))
    _, per_q = _table(ev, systems, ALL_VARIANTS)
    _save(pd.DataFrame(significance_rows(per_q, SIG_PAIRS, ALL_VARIANTS)),
          f"significance_{ev.mode}.csv")


def cmd_failures(ev: Evaluator, per_q, n=15):
    corpus = {d["docid"]: d for d in load_corpus(ev.mode)}
    variants = load_variants()
    rng = np.random.default_rng(load_config()["seed"])
    cands = [(q, v) for v in ["roman", "mix50", "mix75"] for q, m in per_q[("full", v)].items()
             if m["nDCG@10"] == 0 and per_q[("bm25", "native")][q]["nDCG@10"] > 0]
    pick = [cands[i] for i in rng.choice(len(cands), size=min(n, len(cands)), replace=False)]
    out = [f"# Failure analysis ({ev.mode})\n",
           f"{len(cands)} (query, variant) pairs where the full pipeline gets nDCG@10 = 0 but native "
           f"BM25 succeeds; {len(pick)} sampled.\n"]
    for qid, v in pick:
        cfg = system_config("full")
        q, hits = ev.s.search(variants[qid][v], cfg, 3)
        rel = [d for d, r in ev.qrels["dev"][qid].items() if r > 0 and d in corpus]
        out += [f"## {qid} ({v})", f"- native: {variants[qid]['native']}",
                f"- query: `{variants[qid][v]}`",
                f"- normalised: `{q.normalised_text()}`",
                "- tokens: " + ", ".join(f"{t['token']}→{t.get('translit') or '-'}"
                                         + (f" (+{'/'.join(t['expansion'])})" if t['expansion'] else "")
                                         for t in q.tokens if t["script"] == "latin"),
                "- top-3 retrieved: " + " | ".join(corpus[d]["title"] for d, _ in hits),
                "- relevant: " + " | ".join(corpus[d]["title"] for d in rel[:3]), ""]
    path("results", f"failures_{ev.mode}.md").write_text("\n".join(out))
    print(f"-> results/failures_{ev.mode}.md")


def cmd_examples():
    v = load_variants()
    rng = np.random.default_rng(load_config()["seed"])
    dev = [r for r in v.values() if r["split"] == "dev"]
    lines = ["# Query variant examples (dev)\n", "| variant | text |", "|---|---|"]
    for i in rng.choice(len(dev), 5, replace=False):
        for k in ALL_VARIANTS:
            lines.append(f"| {k} | {dev[i][k]} |")
        lines.append("| | |")
    path("results", "variant_examples.md").write_text("\n".join(lines) + "\n")
    print("-> results/variant_examples.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sanity", "baseline", "tune", "main", "significance", "examples", "all"])
    add_mode_flags(ap)
    args = ap.parse_args()
    mode = apply_mode(args)
    seed_everything()
    RESULTS.mkdir(exist_ok=True)
    if args.cmd == "examples":
        return cmd_examples()
    ev = Evaluator(mode)
    if args.cmd in ("sanity", "all"):
        cmd_sanity(ev)
    if args.cmd in ("baseline", "all"):
        cmd_baseline(ev)
    if args.cmd in ("tune", "all") and (args.cmd == "tune" or not TUNED_PATH.exists()):
        cmd_tune(ev)
    if args.cmd == "significance":
        cmd_significance(ev)
    if args.cmd in ("main", "all"):
        cmd_examples()
        cmd_main(ev)


if __name__ == "__main__":
    main()
