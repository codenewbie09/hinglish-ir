# 1. LLM provider and models

Status: accepted (2026-11-20)

## Context
Query variants, the English->Hindi lexicon and the transliteration fallback need an LLM.
The brief asks for a provider-agnostic wrapper with Groq as default. Groq no longer serves
Llama 3.3; it serves `openai/gpt-oss-120b`, `openai/gpt-oss-20b` and `qwen/qwen3.8-27b`.
Free tier: 8k tokens/min per model.

## Decision
- `src/llm.py` talks to any OpenAI-compatible endpoint (`PROVIDERS` table, `LLM_BASE_URL`).
- Variants are generated with `openai/gpt-oss-120b` (reasoning_effort=low).
- The normalisation lexicon (English? -> Hindi equivalent; transliteration fallback) uses
  `openai/gpt-oss-20b`, a different model from the variant generator. Transliteration itself
  is done by IndicXlit (ADR 2), so the pipeline does not invert the generator's own
  romanisation. `qwen/qwen3.8-27b` was tried first but Groq caps it at 1k output tokens/min.
- Every response is cached forever in `data/cache/llm.jsonl` (key: model, messages,
  temperature). The cache ships with the project so results reproduce offline.

## Consequences
Re-running never re-calls the API. A different provider gives different variants: delete
`data/variants.jsonl` and the cache to regenerate.
