# 2. IndicXlit runs in a separate Python 3.10 environment

Status: accepted (2026-11-20)

## Context
`ai4bharat-transliteration` depends on fairseq, which does not install on Python 3.12.
It does install on 3.10, but torch>=2.6 refuses to load the official checkpoint because
it pickles `argparse.Namespace` (weights_only default).

## Decision
- `.venv-xlit` (Python 3.10) runs `scripts/xlit_worker.py` as a subprocess speaking JSON
  lines; `src/xlit.py` drives it and caches every word in `data/cache/xlit.json`.
- The worker sets `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`. This allows arbitrary pickle
  code in the checkpoint; we accept it because the file is AI4Bharat's official release
  downloaded by their own library.
- If `.venv-xlit` is missing, transliteration falls back to the LLM lexicon (`deva` field).

## Consequences
Two environments to set up (`make setup` does both). Results reported in the README use
IndicXlit; the fallback is for machines where it cannot be installed.
