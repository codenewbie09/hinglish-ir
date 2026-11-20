"""Download MIRACL Hindi (topics, qrels, corpus) from Hugging Face into data/raw/.

    python scripts/download_data.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

FILES = {
    "miracl/miracl": [
        "miracl-v1.0-hi/topics/topics.miracl-v1.0-hi-train.tsv",
        "miracl-v1.0-hi/topics/topics.miracl-v1.0-hi-dev.tsv",
        "miracl-v1.0-hi/qrels/qrels.miracl-v1.0-hi-train.tsv",
        "miracl-v1.0-hi/qrels/qrels.miracl-v1.0-hi-dev.tsv",
    ],
    "miracl/miracl-corpus": [
        "miracl-corpus-v1.0-hi/docs-0.jsonl.gz",
        "miracl-corpus-v1.0-hi/docs-1.jsonl.gz",
    ],
}


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    for repo, files in FILES.items():
        for f in files:
            p = hf_hub_download(repo, f, repo_type="dataset", local_dir=RAW)
            print("ok", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
