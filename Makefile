PY    := .venv/bin/python
MODE  ?= --sample          # make eval MODE=--full

.PHONY: setup setup-xlit data variants index index-lucene eval demo test search zip clean-results

setup:            ## main venv (Python 3.12) + optional IndicXlit venv
	uv venv --python 3.12 .venv
	uv pip install --python $(PY) -r requirements.txt
	-$(MAKE) setup-xlit

setup-xlit:       ## IndicXlit in its own Python 3.10 venv; pipeline falls back to the LLM without it
	uv venv --python 3.10 .venv-xlit
	uv pip install --python .venv-xlit/bin/python -r requirements-xlit.txt

data:             ## download MIRACL-hi and build the corpus file
	$(PY) scripts/download_data.py
	$(PY) -m src.data $(MODE)

variants:         ## LLM query variants (cached in data/variants.jsonl; needs GROQ_API_KEY on first run)
	$(PY) -m src.variants

index:
	$(PY) -m src.build_index $(MODE)

index-lucene:     ## Lucene-style Hindi index, only for the sanity check against the MIRACL paper
	$(PY) -m src.build_index $(MODE) --lucene

eval:             ## sanity, baseline curve, tuning (train), main table, ablation, significance, failures
	$(PY) -m src.eval all $(MODE)

demo:
	$(PY) -m streamlit run app.py

search:
	$(PY) -m src.cli search "roth ira pe tax kitna lagta hai" --system full --explain

test:
	$(PY) -m pytest -q

zip:              ## dist/hinglish-ir.zip: code, caches, results, sample corpus (no indexes)
	$(PY) scripts/make_zip.py
