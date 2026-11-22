"""Build the CSD358 submission ZIP.

    python scripts/make_zip.py        # -> dist/CSD358_PrateekAgrawal_RuchirKalla_AbhinavJoshi.zip

Everything sits under one top folder of the same name:
  report/        the project report (PDF; LaTeX sources too if they are in the repo)
  GITHUB_LINK.txt, DATA_README.txt
  every git-tracked file (code, tests, docs, results, data/variants.jsonl, data/cache/*)
  data/raw/miracl-v1.0-hi/ (queries + qrels) and data/processed/sample/corpus.jsonl
Left out: .env, venvs, .git, __pycache__, dist/, built indexes and embeddings (*.pkl, *.npy,
*.npz; `make index` rebuilds them) and any file over 50 MB that is not needed data.
"""
from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = "CSD358_PrateekAgrawal_RuchirKalla_AbhinavJoshi"
REPO_URL = "https://github.com/codenewbie09/hinglish-ir"
MAX_BYTES = 50 * 1024 * 1024
# needed data: shipped whatever its size
DATA = ["data/raw/miracl-v1.0-hi", "data/processed/sample/corpus.jsonl"]
NEEDED = {"data/processed/sample/corpus.jsonl"}
REPORT_FILES = ["Project_Report.pdf"]   # repo root -> report/
REPORT_DIRS = ["report", "latex"]        # LaTeX source folders, if present
EXCLUDED_SUFFIXES = (".pkl", ".npy", ".npz", ".pyc")
EXCLUDED_PREFIXES = (".venv", ".git/", "dist/", "data/processed/full", "data/raw/miracl-corpus")

DATA_README = """\
Dataset: MIRACL-Hindi
=====================
MIRACL (Zhang et al., 2023), Hindi subset. License: Apache-2.0.
  Queries + relevance judgments: https://huggingface.co/datasets/miracl/miracl
  Passages (Hindi Wikipedia):    https://huggingface.co/datasets/miracl/miracl-corpus

What this ZIP contains
  data/raw/miracl-v1.0-hi/              train/dev topics and qrels (dev = test set)
  data/processed/sample/corpus.jsonl    the SAMPLE corpus: 63,452 passages (every passage judged
                                        for a train or dev query + 50,000 random passages, seed 42)
  data/variants.jsonl                   romanised / code-mixed query variants (LLM output, cached)
  data/cache/                           every LLM, lexicon and IndicXlit response (llm.jsonl,
                                        lexicon.json, xlit.json), so the evaluation reproduces
                                        offline, without an API key

The full corpus (506,264 passages) is not included because it is too large. To get it:
  python scripts/download_data.py       downloads topics, qrels and the full corpus (data/raw/)
  python -m src.data --full             builds data/processed/full/corpus.jsonl
  (or: make data MODE=--full)

Built artifacts are not included; rebuild them with
  make index                            inverted index for the sample corpus (~10 s; full: ~70 s)
  make index-lucene                     optional Lucene-style index for the sanity check
Dense (multilingual-e5-small) corpus embeddings are computed on first use.

The dense and hybrid results in the report were computed on a GPU with the full corpus
embedded (exhaustive search). On a CPU the code instead reranks the BM25 top-100 per query,
which gives different dense numbers.
"""


def github_link(commit: str) -> str:
    return f"{REPO_URL}\ncommit: {commit}\n"


def zip_path() -> Path:
    return ROOT / "dist" / f"{NAME}.zip"


def _files(rel: str) -> list[Path]:
    p = ROOT / rel
    if p.is_file():
        return [p]
    return sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else []


def members(verbose: bool = False) -> list[tuple[str, Path]]:
    """(path inside the top folder, source file) pairs."""
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True,
                             check=True).stdout.splitlines()
    out: dict[str, Path] = {t: ROOT / t for t in tracked if (ROOT / t).is_file()}
    for rel in DATA:
        out.update({str(f.relative_to(ROOT)): f for f in _files(rel)})
    for rel in REPORT_FILES:
        if (ROOT / rel).is_file():
            out.pop(rel, None)
            out[f"report/{Path(rel).name}"] = ROOT / rel
    for d in REPORT_DIRS:
        for f in _files(d):
            out[f"report/{f.relative_to(ROOT / d)}"] = f
    keep = []
    for arc, src in sorted(out.items()):
        if (arc == ".env" or arc.startswith(EXCLUDED_PREFIXES) or "__pycache__" in arc
                or arc.endswith(EXCLUDED_SUFFIXES)):
            continue
        if src.stat().st_size > MAX_BYTES and arc not in NEEDED:
            if verbose:
                print(f"skipped (over 50 MB): {arc} ({src.stat().st_size / 1e6:.0f} MB)")
            continue
        keep.append((arc, src))
    return keep


def build(out: Path, commit: str) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    files = members(verbose=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, src in files:
            z.write(src, f"{NAME}/{arc}")
        z.writestr(f"{NAME}/GITHUB_LINK.txt", github_link(commit))
        z.writestr(f"{NAME}/DATA_README.txt", DATA_README)
    return out


def main():
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        print("WARNING: uncommitted changes to tracked files; the ZIP will not match", commit)
    out = build(zip_path(), commit)
    print(f"{out} ({out.stat().st_size / 1e6:.1f} MB, commit {commit})")


if __name__ == "__main__":
    main()
