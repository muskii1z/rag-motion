# 0012. Evaluate keyword search as a baseline; add query rewriting to Phase 1F
**Date:** 2026-09-24 · **Step:** between 5 and 6 · **Status:** accepted

## Context
The developer shared the article "RAG Is Simpler Than You Think" by Rafael Pierre (Lighthouse newsletter, June 2026). It argues that most teams over-engineer RAG (retrieval-augmented generation: look up relevant data first, then hand it to the LLM), and that keyword search plus query rewriting (an LLM rewriting the question into better search terms) covers many use cases before embeddings are needed. This project's plan was semantic search (embeddings compared with pgvector) first, with keyword search only arriving as part of hybrid search in Phase 1F. The plan assumed embeddings help; nothing was set up to test that assumption. Coaching jargon (RDL, BSS, SL RDL, Pallof) is also a known weak spot for general embedding models. See [the build log entry](../build-log.md#between-steps-5-and-6-api-keys-openrouter-setup-and-the-rag-is-simpler-than-you-think-article).

## Options considered
- **Adopt the article's order: keyword search first, embeddings later.** Simplest system, and a strong baseline. But the project's learning goal includes embeddings and pgvector, and the article's case against pre-computed embeddings is about scale (millions of documents) that doesn't apply here.
- **Keep the plan as is: semantic first, hybrid in Phase 1F.** No extra work. But "embeddings beat keyword search on this data" stays an assumption, with no number behind it.
- **Keep semantic first, but measure keyword-only as a baseline and add query rewriting as an experiment.** Step 15 scores keyword only (Postgres full-text search), semantic only (pgvector), and both combined on the same test questions. Phase 1F adds an LLM query-rewriting step with a small glossary of exercise abbreviations (RDL, BSS, SL RDL, KB), measured against the Step 15 baseline. Postgres already has full-text search, so the extra cost is small.

## Decision
The third option, approved by the developer. Semantic search stays the main path, but Step 15 compares all three retrieval modes, and query rewriting joins metadata filtering, hybrid search, and reranking as a Phase 1F experiment. Planned implementation for the keyword side: a full-text index (`tsvector`) over name and description, and a `keyword_search()` function next to the semantic one. The Step 15 row and the Phase 1F note in `CLAUDE.md` were updated. Step 6 is not affected.

## Tradeoffs
- The evaluation step (Step 15) gets slightly larger: three modes to run and compare instead of one.
- Phase 1F gets one more experiment, and query rewriting adds an LLM call (time and cost) to every question if it is kept.
- Not adopted from the article: its keyword-first "hybrid" (keyword search picks candidates, embeddings only reorder them). It can't recover what keyword search missed, so this project keeps the parallel hybrid (run both, merge). See [Retrieve-then-rerank vs parallel hybrid](../concepts.md#retrieve-then-rerank-vs-parallel-hybrid).

## Revisit when
Keyword-only search matches or beats semantic search in the Step 15 results. Then simplify: consider dropping or demoting the embedding path for this data.

## Note (2026-09-25, after Step 10)

The plan was reordered: document ingestion is now Steps 11 to 13 and LangSmith tracing Step 14 (see the [0011 update](0011-phase-1-plan-revision-ingestion-and-langsmith.md#update-2026-09-25-after-step-10-ingestion-moved-before-langsmith)). The step numbers in this record are unaffected: evaluation is still Step 15 and Phase 1F still comes after Step 16. LangSmith still arrives before the Step 15 eval.
