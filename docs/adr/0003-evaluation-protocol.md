# 3. Evaluation protocol choices

Status: accepted (2026-11-20)

## Decisions
1. **Tuning set**: a fixed random subset of 400 train queries (seed 42), not all 1,169.
   Reason: generating 4 LLM variants per query is rate-limited (8k tokens/min).
2. **Sample corpus** includes passages judged for *train and dev* (+50k random), so
   tuning on train is meaningful on the sample index.
3. **Stop words** are removed on the query side only; documents keep them (one index
   serves the with/without stop words ablation; BM25 IDF makes them near-zero anyway).
4. **Cumulative systems** in the main table (bm25 -> +translit -> +phonetic ->
   +expansion -> full = +stemming); the ablation removes one component at a time.
5. **Dense on GPU** embeds the whole corpus (allowed by the brief when a GPU exists);
   on CPU it reranks the full pipeline's BM25 top-100.
