"""The CSD358 submission ZIP: report, code, results and sample data under one top folder;
never secrets, environments, built indexes or embeddings."""
import importlib.util
import zipfile

import pytest

from src.config import ROOT

spec = importlib.util.spec_from_file_location("make_zip", ROOT / "scripts" / "make_zip.py")
make_zip = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_zip)

NAME = "CSD358_PrateekAgrawal_RuchirKalla_AbhinavJoshi"


def test_zip_name_and_top_folder():
    assert make_zip.NAME == NAME
    assert make_zip.zip_path().name == f"{NAME}.zip" and make_zip.zip_path().parent.name == "dist"


def test_members_cover_code_results_caches_and_sample_data():
    m = dict(make_zip.members())          # archive path (inside the top folder) -> source path
    for p in ["README.md", "app.py", "Makefile", "requirements.txt", "requirements-xlit.txt",
              "config.yaml", ".env.example", "src/pipeline.py", "scripts/make_zip.py",
              "tests/test_bm25.py", "docs/adr/0005-expansion-gate.md", "results/tuned.json",
              "results/degradation_full.png", "results/failures_full.md",
              "data/variants.jsonl", "data/cache/llm.jsonl", "data/cache/lexicon.json",
              "data/cache/xlit.json",
              "data/raw/miracl-v1.0-hi/topics/topics.miracl-v1.0-hi-dev.tsv",
              "data/raw/miracl-v1.0-hi/qrels/qrels.miracl-v1.0-hi-train.tsv"]:
        assert p in m, p
    if (ROOT / "data/processed/sample/corpus.jsonl").exists():
        assert "data/processed/sample/corpus.jsonl" in m


def test_report_goes_under_report_folder():
    if not (ROOT / "Project_Report.pdf").exists():
        pytest.skip("no report in the working tree")
    m = dict(make_zip.members())
    assert "report/Project_Report.pdf" in m and "Project_Report.pdf" not in m


def test_members_never_include_secrets_envs_indexes_or_full_corpus():
    for p, _ in make_zip.members():
        assert p != ".env" and not p.startswith((".venv", ".git/", "dist/", "data/processed/full",
                                                 "data/raw/miracl-corpus"))
        assert "__pycache__" not in p and not p.endswith((".pkl", ".npy", ".npz", ".pyc"))


def test_generated_texts():
    link = make_zip.github_link("abc1234")
    assert "https://github.com/codenewbie09/hinglish-ir" in link and "abc1234" in link
    d = make_zip.DATA_README
    for s in ["MIRACL", "Zhang et al., 2023", "Apache-2.0", "huggingface.co/datasets/miracl/miracl",
              "miracl/miracl-corpus", "63,452", "506,264", "scripts/download_data.py",
              "make index", "GPU"]:
        assert s in d, s


def test_build_writes_one_top_folder(tmp_path, monkeypatch):
    src = tmp_path / "a.txt"
    src.write_text("x")
    monkeypatch.setattr(make_zip, "members", lambda verbose=False: [("a.txt", src)])
    out = make_zip.build(tmp_path / "t.zip", "deadbee")
    names = zipfile.ZipFile(out).namelist()
    assert {n.split("/")[0] for n in names} == {NAME}
    assert {f"{NAME}/a.txt", f"{NAME}/GITHUB_LINK.txt", f"{NAME}/DATA_README.txt"} <= set(names)
