"""Command-line search.

    python -m src.cli search "roth ira pe tax kitna lagta hai" --system full --explain
"""
from __future__ import annotations

import argparse
import textwrap

from src.data import add_mode_flags, apply_mode
from src.engine import ALL_SYSTEMS, Engine


def main():
    ap = argparse.ArgumentParser(prog="python -m src.cli")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--system", default="full", choices=ALL_SYSTEMS)
    s.add_argument("-k", type=int, default=5)
    s.add_argument("--explain", action="store_true")
    add_mode_flags(s)
    args = ap.parse_args()
    mode = apply_mode(args)
    eng = Engine(mode)
    r = eng.search(args.query, args.system, k=args.k, explain=args.explain)
    q = r["repr"]
    print(f"query  : {args.query}\nsystem : {args.system}  (corpus: {mode})")
    if args.explain:
        print("\ntokens :")
        for t in q.tokens:
            extra = []
            if t.get("translit"):
                extra.append(f"translit={t['translit']}")
            if t.get("english"):
                extra.append(f"english -> {'/'.join(t['expansion']) or '?'}")
            if t.get("dropped"):
                extra.append(t["dropped"])
            print(f"  {t['token']:<14} [{t['script']:<5}] {' '.join(extra)}")
        print("\nquery terms per field:")
        for fld, tw in q.terms.items():
            print(f"  {fld:5s}: " + " ".join(f"{t}({w:g})" for t, w in tw))
    print(f"\nnormalised query: {q.normalised_text()}")
    for w in r["warnings"]:
        print("WARNING:", w)
    print()
    for i, h in enumerate(r["hits"], 1):
        print(f"{i}. [{h['docid']}] {h['title']}  score={h['score']:.3f}")
        print(textwrap.indent(textwrap.fill(h["text"][:300], 100), "     "))
        if args.explain and h["terms"]:
            top = sorted(h["terms"].items(), key=lambda x: -x[1])
            print("     terms: " + ", ".join(f"{t}={c:.2f}" for t, c in top))
        print()


if __name__ == "__main__":
    main()
