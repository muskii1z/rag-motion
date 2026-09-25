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
Correction: earlier docs said OpenRouter doesn't do embeddings, so Voyage needed its own account and key. That was wrong. OpenRouter lists 33 embedding models, including `voyageai/voyage-4-lite` ($0.02 per million tokens, 32K context), the model chosen here. So this decision's model likely stays the same, but it would be reached through the OpenRouter key instead of `VOYAGE_API_KEY` and the `voyageai` library. **To be confirmed at Step 7.**
- **Open check:** Voyage normally embeds queries and documents slightly differently (`input_type`, described above). OpenRouter doesn't list whether that setting passes through. Test at Step 7.
- **Alternatives ruled out for now:** free embedding models on OpenRouter. The free LiquidAI one says requests may be used to train its models, and it and several others stop at 512 tokens, too short for document chunks later.
- **Lock-in reminder:** vectors from different models can't be compared, so switching models means re-embedding everything, and a different vector size (for example OpenAI's 1,536) would also need a table change. See [Embedding model lock-in](../concepts.md#embedding-model-lock-in).
- If this is confirmed, the "second API key" tradeoff above goes away, and the `voyageai` library (with its large set of transitive dependencies) may no longer be needed.

See [Step 6](../build-log.md#before-we-started-choosing-models).
