"""Build the submission ZIP: every git-tracked file + the sample corpus + MIRACL queries/qrels.

    python scripts/make_zip.py        # -> dist/hinglish-ir.zip

Indexes and embeddings are left out (make index rebuilds the sample index in ~10 s);
the full corpus is re-downloaded with scripts/download_data.py.
"""
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRA = ["data/raw/miracl-v1.0-hi", "data/processed/sample/corpus.jsonl"]


def members() -> list[str]:
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True,
                             check=True).stdout.split()
    extra = []
    for e in EXTRA:
        p = ROOT / e
        files = [p] if p.is_file() else sorted(f for f in p.rglob("*") if f.is_file())
        extra += [str(f.relative_to(ROOT)) for f in files]
    return sorted(set(tracked) | set(extra))


def main():
    out = ROOT / "dist" / "hinglish-ir.zip"
    out.parent.mkdir(exist_ok=True)
    files = members()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(ROOT / f, f"hinglish-ir/{f}")
    print(f"{out} ({len(files)} files, {out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
