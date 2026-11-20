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
- Normalisation (lexicon/transliteration fallback) uses `qwen/qwen3.8-27b`, a different
  model family, so the pipeline is not simply inverting its own model's romanisation.
- Every response is cached forever in `data/cache/llm.jsonl` (key: model, messages,
  temperature). The cache ships with the project so results reproduce offline.

## Consequences
Re-running never re-calls the API. A different provider gives different variants: delete
`data/variants.jsonl` and the cache to regenerate.
