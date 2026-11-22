"""Render results/*.csv into the README between the results markers (no hand-copied numbers).

    python scripts/render_results.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
START, END = "<!-- results:start -->", "<!-- results:end -->"
COLS = ["native", "roman", "mix25", "mix50", "mix75", "roman_rule"]


def table(csv: Path, index: str) -> str:
    df = pd.read_csv(csv).set_index(index)[COLS]
    best = df.max()
    head = f"| {index} | " + " | ".join(COLS) + " |\n|---|" + "---|" * len(COLS) + "\n"
    rows = []
    for name, r in df.iterrows():
        cells = [f"**{v:.3f}**" if abs(v - best[c]) < 1e-9 else f"{v:.3f}" for c, v in r.items()]
        rows.append(f"| {name} | " + " | ".join(cells) + " |")
    return head + "\n".join(rows) + "\n"


def significance(csv: Path) -> str:
    df = pd.read_csv(csv)
    df = df[df.metric == "nDCG@10"]
    if "vs" not in df:  # older CSVs compared everything against bm25
        df = df.assign(vs="bm25")
    out = "| system vs baseline | " + " | ".join(COLS) + " |\n|---|" + "---|" * len(COLS) + "\n"
    for (s, vs), g in df.groupby(["system", "vs"], sort=False):
        g = g.set_index("variant")
        out += f"| {s} vs {vs} | " + " | ".join(
            f"{g.loc[c, 'delta']:+.3f} (p={g.loc[c, 'p_value']:.4f})" for c in COLS) + " |\n"
    return out


def section(mode: str, title: str) -> str:
    parts = [f"### {title}\n"]
    sanity = RES / f"sanity_{mode}.txt"
    if sanity.exists():
        parts.append("Sanity check:\n\n```\n" + sanity.read_text().strip() + "\n```\n")
    for metric, label in [("nDCG10", "nDCG@10"), ("Recall100", "Recall@100")]:
        f = RES / f"main_{metric}_{mode}.csv"
        if f.exists():
            parts.append(f"**{label}** (best per column in bold)\n\n" + table(f, "system"))
    if (RES / f"degradation_{mode}.png").exists():
        parts.append(f"![degradation](results/degradation_{mode}.png)\n")
    f = RES / f"ablation_nDCG10_{mode}.csv"
    parts.append("**Ablation, nDCG@10** (full pipeline minus one component)\n\n"
                 + (table(f, "ablation") if f.exists() else "_pending_\n"))
    f = RES / f"significance_{mode}.csv"
    parts.append("**Paired randomisation test, nDCG@10 delta** (10,000 permutations; p=0.0001 is the smallest reportable value)\n\n"
                 + (significance(f) if f.exists() else "_pending_\n"))
    parts.append(f"Other metrics (P@5, P@10, F1@10, MRR@10, R@10): `results/main_long_{mode}.csv`. "
                 f"Failure analysis: `results/failures_{mode}.md`.\n")
    return "\n".join(parts)


def main():
    body = "\n".join(section(m, t) for m, t in [("full", "Full corpus (506,264 passages)"),
                                                ("sample", "Sample corpus (63,452 passages)")]
                     if (RES / f"main_nDCG10_{m}.csv").exists())
    readme = ROOT / "README.md"
    text = readme.read_text()
    pre, rest = text.split(START, 1)
    _, post = rest.split(END, 1)
    readme.write_text(pre + START + "\n" + body + END + post)
    print("README results updated")


if __name__ == "__main__":
    main()
