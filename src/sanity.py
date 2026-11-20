"""Stage-1 sanity check: native-script BM25 on dev."""
import argparse
import time

from src.data import add_mode_flags, apply_mode, load_qrels, load_queries
from src.metrics import evaluate_run
from src.pipeline import Searcher

ap = argparse.ArgumentParser()
add_mode_flags(ap)
mode = apply_mode(ap.parse_args())
s = Searcher(mode)
qs, qrels = load_queries("dev"), load_qrels("dev")
t0 = time.time()
run = {qid: [d for d, _ in s.search(q, "bm25")[1]] for qid, q in qs.items()}
dt = time.time() - t0
m = evaluate_run(run, qrels)["mean"]
print(f"[{mode}] native BM25 dev ({len(qs)} q, {dt/len(qs)*1000:.1f} ms/q):",
      {k: round(v, 3) for k, v in m.items()})
