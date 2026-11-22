"""The submission ZIP: tracked files + sample data, never secrets or environments."""
import importlib.util

from src.config import ROOT

spec = importlib.util.spec_from_file_location("make_zip", ROOT / "scripts" / "make_zip.py")
make_zip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_zip)


def test_zip_members_cover_code_caches_and_sample_data():
    m = set(make_zip.members())
    assert {"README.md", "src/pipeline.py", "data/variants.jsonl", "data/cache/llm.jsonl",
            "results/tuned.json"} <= m
    assert any(p.startswith("data/raw/miracl-v1.0-hi/") for p in m)    # queries + qrels
    if (ROOT / "data/processed/sample/corpus.jsonl").exists():
        assert "data/processed/sample/corpus.jsonl" in m


def test_zip_never_contains_secrets_environments_or_full_corpus():
    for p in make_zip.members():
        assert p != ".env" and not p.startswith((".venv", ".git/", "data/processed/full",
                                                 "data/raw/miracl-corpus", "dist/"))
        assert not p.endswith((".pkl", ".npy", ".npz"))   # rebuilt by make index / dense
