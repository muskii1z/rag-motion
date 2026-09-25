# 0002. Embeddings with Voyage AI voyage-4-lite
**Date:** 2026-09-23 · **Step:** 0 · **Status:** accepted

## Context
RAG needs an embedding model: a model that turns text into a vector (a fixed-length list of numbers) that captures its meaning, so similar exercises can be found. Anthropic does not sell embedding models, so a second provider or a local model is required. See [Why Anthropic doesn't sell embeddings](../concepts.md#why-anthropic-doesnt-sell-embeddings).

## Options considered
- **Voyage AI (hosted).** Anthropic's recommended partner. Needs a free API key.
- **Local sentence-transformers.** Runs on the Mac. No key and no cost. 384 dimensions. Slightly lower quality.
- **OpenAI text-embedding-3-small (hosted).** 1536 dimensions. Adds a second vendor.

Claude initially recommended the local option, because no API keys existed yet. The developer chose Voyage instead, as the production-style option and the better interview story.

## Decision
Use Voyage AI, model `voyage-4-lite`, 1024 dimensions. It supports `input_type` set to `"document"` (for stored exercises) or `"query"` (for user questions). `voyage-4-lite` is the cheapest Voyage 4 model, and its quality is more than enough for 20 to 50 exercises. All embedding code will live in one module, so swapping providers is a one-file change. The key goes in `VOYAGE_API_KEY`.

## Tradeoffs
A second API key and a network dependency.

*Added in Step 1:* the `voyageai` library (0.5.0) brings a large set of [transitive dependencies](../concepts.md#transitive-dependencies) (libraries our libraries need) into the environment. `uv tree` showed voyageai → langchain-text-splitters → langchain-core → langsmith, plus numpy, pillow, tokenizers, aiohttp, requests, and tenacity. So LangChain core and LangSmith packages are installed even though we don't use LangChain. That means a bigger install, more packages to keep patched, and more room for version conflicts. See [Step 1](../build-log.md#step-1-install-uv-create-the-python-project-add-dependencies).

## Revisit when
Retrieval evals show embedding quality is the bottleneck (try `voyage-4` or `voyage-4-large`), or cost matters at scale.

## Note (2026-09-24, Step 6): likely accessed through OpenRouter
Correction: earlier docs said OpenRouter doesn't do embeddings, so Voyage needed its own account and key. That was wrong. OpenRouter lists 33 embedding models, including `voyageai/voyage-4-lite` ($0.02 per million tokens, 32K context), the model chosen here. So this decision's model likely stays the same, but it would be reached through the OpenRouter key instead of `VOYAGE_API_KEY` and the `voyageai` library. **To be confirmed at Step 7.** *(Confirmed at Step 7; see the update below.)*
- **Open check:** Voyage normally embeds queries and documents slightly differently (`input_type`, described above). OpenRouter doesn't list whether that setting passes through. Test at Step 7.
- **Alternatives ruled out for now:** free embedding models on OpenRouter. The free LiquidAI one says requests may be used to train its models, and it and several others stop at 512 tokens, too short for document chunks later.
- **Lock-in reminder:** vectors from different models can't be compared, so switching models means re-embedding everything, and a different vector size (for example OpenAI's 1,536) would also need a table change. See [Embedding model lock-in](../concepts.md#embedding-model-lock-in).
- If this is confirmed, the "second API key" tradeoff above goes away, and the `voyageai` library (with its large set of transitive dependencies) may no longer be needed.

See [Step 6](../build-log.md#before-we-started-choosing-models).

## Update (2026-09-24, Step 7): confirmed through OpenRouter
Both open checks from the Step 6 note are resolved.
- **Access.** `voyage-4-lite` works through OpenRouter as `voyageai/voyage-4-lite`, with the same OpenRouter key and the same `openai` client as the LLM. No Voyage account and no `VOYAGE_API_KEY` needed. The Decision section's "the key goes in `VOYAGE_API_KEY`" no longer applies; it stays above as history.
- **`input_type` passes through.** The same sentence embedded three ways gave cosine similarities of 0.907 (no setting vs query), 0.905 (no setting vs document), and 0.780 (query vs document). If the setting were dropped, all three would match. See [Query vs document embeddings (input_type)](../concepts.md#query-vs-document-embeddings-input_type).
- **Implemented** in `src/ragmotion/embeddings.py`, as planned: one module for all embedding calls. `embed_documents()` always sends `"document"` and `embed_query()` always sends `"query"`, so callers can't mix them up. Every vector is checked for 1,024 numbers. Model and size live in `config.py` (`embedding_model`, `embedding_dimensions`).
- **Measured.** Vectors are normalized (length 1.0). A 7-token sentence cost $0.00000014, matching the listed $0.02 per million tokens.
- **Tradeoffs now.** The "second API key" tradeoff is gone. In its place: both models now depend on one provider, OpenRouter. If it has an outage, the LLM and embeddings stop together, and `input_type` works only because OpenRouter passes it through. The `voyageai` library is still installed but unused; whether to remove it is open.
- **Extra revisit signal.** OpenRouter stops offering `voyageai/voyage-4-lite` or stops passing `input_type` through. Direct Voyage access with `VOYAGE_API_KEY` is the fallback. It is the same model, so stored vectors should stay usable, but that has not been tested.

See [Step 7](../build-log.md#step-7-first-embedding-embed-one-sentence-look-at-the-numbers).

## Note (2026-09-24, Step 8): recording which model made each vector
All 20 exercises are now embedded with `voyageai/voyage-4-lite` in one batch call. A new `embedding_model` text column stores the model name next to each vector. Reason: vectors from different models can't be compared ([Embedding model lock-in](../concepts.md#embedding-model-lock-in)), so if this decision is ever revisited, the column shows exactly which rows still need re-embedding. `scripts/embed_exercises.py` selects rows whose `embedding` is empty or whose `embedding_model` differs from the current `config.py` setting, so changing the model setting and re-running the script re-embeds everything stale. The seed script clears both columns when an exercise's content changes. What text gets embedded is a separate decision: [0014](0014-embedded-text-name-description-labels.md). See [Embedding provenance (embedding_model column)](../concepts.md#embedding-provenance-embedding_model-column) and [Step 8](../build-log.md#step-8-embed-all-exercises-store-vectors-compare-them-by-hand).
