# 0011. Phase 1 plan revision: ingestion and LangSmith get concrete steps
**Date:** 2026-09-24 · **Step:** 5 · **Status:** accepted

## Context
The developer's goal is to learn RAG (retrieval-augmented generation: look up relevant data first, then hand it to the LLM) properly. That includes ingestion (getting outside documents into the system: extracting their text and splitting it into chunks, meaning passages of a few paragraphs) and being able to see where things go wrong. The original 13-step plan left ingestion vague: it was only "suggested after Step 10" and was not in the step table. The master context document put LangSmith (a hosted service for tracing requests and running evaluations) in Phase 4. At the start of Step 5 the developer asked when document extraction and chunking would come, and whether LangSmith should come earlier. Claude agreed the plan had a real gap. See [Step 5, Before we started](../build-log.md#before-we-started-four-questions-and-a-plan-change).

## Options considered
- **Ingestion first.** Reaches the part the developer most wants to learn fastest. But it is harder to debug: ingestion adds its own failure points (garbled PDF text, chunks cut mid-sentence, wrong chunk sizes, lost metadata), and with nothing simpler built first you can't tell which layer broke. It also needs a source document picked immediately.
- **A smaller catalog, then ingestion.** Less time on exercises, but keeps the same debugging problem, and the catalog is still needed later for filterable rows.
- **Catalog first, then LangSmith (Step 11) and ingestion (Steps 12 to 14) before evaluation.** Learn embeddings and search on clean, known data; get a working RAG pipeline; add tracing so failures are visible; then add documents; then measure the whole system.

## Decision
The third option. New Phase 1 sequence: 5 exercise catalog; 6 first LLM call via OpenRouter (model chosen there); 7 first embedding; 8 embed all exercises; 9 similarity search CLI; 10 RAG with citations plus a minimal local UI; 11 LangSmith tracing on the RAG pipeline; 12 document ingestion (extract text from a real, openly licensed document, for example a PDF); 13 chunking into a second table with metadata; 14 embed chunks, search exercises and documents together, answers cite both; 15 evaluation set (own scoring script first, then viewed in LangSmith); 16 FastAPI endpoint, tests, README. Phase 1F (metadata filters, hybrid search, reranking) comes after Step 16 and is measured against the Step 15 baseline.

Supporting choices:
- Evaluation moved from Step 11 to Step 15, after ingestion, so the baseline measures the whole system, not just the catalog.
- LangSmith goes right after basic RAG and before ingestion, so when chunked answers go wrong the trace shows whether the right chunk was never retrieved or was retrieved and ignored.
- Manual first: scripts print every stage until Step 11, and we write our own eval scoring before viewing it in LangSmith, so the developer knows what the tool is showing.
- Candidate first document: the U.S. Physical Activity Guidelines for Americans (a government publication, free to use and redistribute). The developer's own notes on NSCA power principles could be a second. Not chosen yet.
- The step table in `CLAUDE.md` was updated in commit `408130e`.

## Tradeoffs
- Ingestion starts about six steps later than "ingestion first" would.
- The plan grew from 13 steps (0 to 12) to 17 (0 to 16).
- LangSmith is a hosted service: it needs a free account and API key, and traces, including prompts, are stored on LangSmith's servers. Acceptable because only fictional client data is used.
- Old step numbers in earlier docs changed meaning (old Step 11 evaluation is now Step 15; old Step 12 FastAPI is now Step 16). Earlier build-log entries keep their original wording with notes.

## Revisit when
The catalog steps (6 to 10) drag on and the developer's focus on ingestion is lost. Then consider pulling ingestion earlier.

## Note (2026-09-24, between Steps 5 and 6)

Step 15 and Phase 1F were extended by [0012](0012-keyword-baseline-and-query-rewriting.md): Step 15 now compares keyword-only, semantic-only, and combined retrieval on the same questions, and Phase 1F adds a query-rewriting experiment. The step order in this record is unchanged.
