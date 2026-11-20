# hinglish-ir: retrieving Hindi passages with romanised and code-mixed queries

How much does retrieval over Hindi Wikipedia (MIRACL-hi, Devanagari passages) degrade when
the *query* is typed in romanised Hindi or in Hindi-English code-mix instead of Devanagari,
and how much of the loss can an IR pipeline recover?

The core IR parts (inverted index, BM25, phonetic keys, query normalisation, fusion, metrics,
significance test) are written from scratch. Libraries are used for data download,
transliteration (IndicXlit), embeddings (multilingual-e5-small), LLM calls and plots.

## Setup

```bash
make setup            # .venv (Python 3.12) + .venv-xlit (Python 3.10, IndicXlit)
cp .env.example .env  # add GROQ_API_KEY (only needed if the LLM caches are missing)
make data             # download MIRACL-hi + build the sample corpus   (MODE=--full for 506k)
make index            # inverted index (sample: ~10 s, full: ~70 s)
make variants         # query variants (cached in data/variants.jsonl -> no API calls)
make eval             # all experiments -> results/
make search           # CLI demo
make demo             # Streamlit app
make test
```

`--sample` (default) = every passage judged for train+dev queries + 50,000 random passages
(63,452 passages). `--full` = all 506,264 passages. `uv` is used for environments.
The ZIP ships the sample only; `python scripts/download_data.py` re-downloads everything.

All LLM output is cached (`data/cache/llm.jsonl`, `data/cache/lexicon.json`,
`data/cache/xlit.json`, `data/variants.jsonl`), so `make eval` reproduces the numbers offline.

## Data and query variants

MIRACL-hi: 1,169 train / 350 dev queries with qrels; dev is the test set (test qrels are
hidden). Tuning uses a fixed random subset of 400 train queries (seed 42), because each
query needs four LLM-generated variants and the free API tier is rate-limited
(see `docs/adr/0003`).

| variant | how it is made |
|---|---|
| native | original Devanagari query |
| roman | casual romanised Hindi as typed on a phone (LLM, `openai/gpt-oss-120b`, T=0) |
| mix25 / mix50 / mix75 | romanised, with ~25/50/75 % of content words replaced by English (LLM) |
| roman_rule | deterministic romanisation (indic_transliteration Harvard-Kyoto, lower-cased, final schwa dropped) |

Examples: `results/variant_examples.md`.

## Pipeline

```
query ─ tokenise (NFC, ZW removal, digits) ─ per-token script detection
        ├─ Devanagari token ──────────────────────────────────────────┐
        └─ Latin token ─ romanised stop word? drop                     │
                       ─ IndicXlit → Devanagari (+ keep Latin form)    │
                       ─ LLM lexicon: English? → add Hindi equivalent  │
                                                                       ▼
        query terms ── field "tok"/"stem" (BM25) + field "phon" (phonetic keys, BM25)
                                         │
             dense e5-small ─────────────┤  weighted RRF (k, w tuned on train)
                                         ▼
                                      ranking
```

* `src/text.py` – NFC normalisation, Devanagari-aware tokeniser (keeps matras), stop words,
  light suffix stemmer (Ramanathan & Rao style). Each step toggleable.
* `src/index.py`, `src/bm25.py` – CSR inverted index with three fields (`tok`, `stem`,
  `phon`), BM25 (k1 = 1.2, b = 0.75) with per-term score breakdown.
* `src/phonetic.py` – Soundex-style key on the Devanagari form: merges vowel length,
  e/ai, o/au, nasalisation (incl. half-nasal consonants), aspiration, nukta,
  retroflex/dental t/d/n and the sibilants; collapses repeats. Indexed as a second field.
* `src/normalise.py` – script detection, IndicXlit transliteration (LLM fallback),
  bilingual expansion via a cached per-token LLM lexicon.
* `src/dense.py` – multilingual-e5-small. With a GPU the whole corpus is embedded once;
  on CPU only the BM25 top-100 per query are embedded and reranked.
* `src/fusion.py` – weighted reciprocal rank fusion.
* `src/eval.py` – all experiments.

## Results

All numbers are on the 350 MIRACL-hi **dev** queries. Weights were tuned on train only
(`results/tuned.json`). Files in `results/` carry a `_sample` or `_full` suffix.

| file | content |
|---|---|
| `sanity_*.txt` | native BM25 vs the MIRACL paper |
| `main_nDCG10_*.csv`, `main_Recall100_*.csv`, `main_P10_*.csv`, `main_F110_*.csv`, `main_MRR10_*.csv` | systems × variants |
| `main_long_*.csv` | every metric, long format |
| `degradation_*.png`, `baseline_degradation_*.png` | metric vs code-mixing level |
| `ablation_nDCG10_*.csv`, `ablation_long_*.csv` | full pipeline minus one component |
| `significance_*.csv` | paired randomisation test (10k permutations) vs BM25 |
| `failures_*.md` | 15 queries the pipeline still fails, with the normalised query |
| `tuning_*.csv`, `tuned.json` | train-set tuning log and chosen weights |
| `variant_examples.md` | example variants per level |

RESULTS_TABLES

## Demo

```bash
python -m src.cli search "roth ira pe tax kitna lagta hai" --system full --explain
streamlit run app.py      # HIR_MODE=full streamlit run app.py for the full corpus
```

The CLI prints the detected script per token, the transliteration / expansion of each
Latin token, the normalised query, the top passages and each term's BM25 contribution.
The app shows BM25 and a chosen system side by side, with the per-token analysis.
If the LLM is unreachable for a new word, the demo still answers, without expansion,
and shows a warning.

## Tests

`make test`: BM25 against the formula on a toy corpus, score breakdown, phonetic key
merges/separations, script detection and tokenisation, metrics, RRF, normalisation.

## Design decisions

`docs/adr/`: LLM provider/models (0001), IndicXlit in a separate Python 3.10 venv (0002),
evaluation protocol (0003).

## Limitations and threats to validity

* **Synthetic queries.** Roman and code-mixed variants are LLM-generated, not real user
  queries. To reduce circularity, variants come from `gpt-oss-120b`, transliteration from
  IndicXlit (a separate seq2seq model) and the lexicon from `gpt-oss-20b`. `roman_rule`
  is a deterministic check that involves no LLM.
* **Mixing levels are approximate.** The LLM was asked for ~25/50/75 % English content
  words; the actual ratio per query was not verified token by token.
* **Context-free lexicon.** Each Latin token is looked up on its own, so ambiguous tokens
  (`me`, `ira`) can be mis-expanded. Example: "ira" → आईआरए (the Irish Republican Army).
* **Sample corpus is easier** than the full corpus (fewer distractors), so sample numbers
  are higher. Compare systems within one corpus, and use the full-corpus sanity check
  against the MIRACL paper.
* **Tuning on 400 train queries**, not all 1,169 (API rate limits, ADR 0003).
* **BM25 settings.** k1 = 1.2, b = 0.75 as specified. The MIRACL paper's Anserini setup
  (k1 = 0.9, b = 0.4, Lucene Hindi analyser) scores higher on native queries; see the
  sanity check.

## AI use

* **Code.** The project was built with Claude Code (Claude Opus 5.5) as a pair programmer,
  following a written specification (components, experiments, order of work). Every stage
  was run and checked against its output before moving on: unit tests, the BM25 sanity
  check against the MIRACL paper, and inspection of variants and transliterations.
  Bugs found that way (rule-based romaniser dropping long vowels, an IndicXlit batch-API
  shape mismatch, a stop word swallowing the expansion "कर" = tax) were fixed and are
  covered by the tests or the git history.
* **Inside the pipeline.** LLMs are used only for judgments that exact code cannot make,
  and every call is commented with the judgment it makes:
  - generating the romanised / code-mixed query variants (`src/variants.py`, `gpt-oss-120b`)
  - deciding whether a Latin token is English and giving its Hindi equivalent
    (`src/normalise.py`, `gpt-oss-20b`)

  Indexing, BM25, phonetic keys, fusion, metrics and the significance test are plain code.
* **Reproducibility.** Every LLM response is cached and shipped (temperature 0), so the
  reported numbers reproduce without an API key.
