# Decision records

One file per real decision, numbered in order. Each records the context, options, choice, tradeoffs, and when to revisit.

- [0001. Packaging with uv](0001-packaging-uv.md) (Step 0)
- [0002. Embeddings with Voyage AI voyage-4-lite](0002-embeddings-voyage-4-lite.md) (Step 0, note in Step 6: likely accessed through OpenRouter; confirmed in Step 7, same key, `input_type` passes through; Step 8 note on the `embedding_model` provenance column)
- [0003. LLM: Claude Opus 5](0003-llm-claude-opus-5.md) (Step 0, superseded by 0013 in Step 6)
- [0004. Database: PostgreSQL 16 + pgvector in Docker](0004-database-postgres-pgvector.md) (Step 0, deployment and Pinecone note added between Steps 4 and 5)
- [0005. Database access: psycopg 3 with raw SQL](0005-database-access-psycopg-raw-sql.md) (Step 0)
- [0006. Interface: CLI first, thin FastAPI at Step 12](0006-interface-cli-first.md) (Step 0, amended in Step 5: minimal local UI at Step 10, FastAPI now Step 16; amended in Step 10: FastAPI built in Step 10, Step 16 hardens it)
- [0007. Version control: git and a private GitHub repo](0007-version-control-git-github.md) (Step 0, implemented in Step 2)
- [0008. Documentation with a build-scribe subagent](0008-documentation-build-scribe.md) (Step 0)
- [0009. Local database on port 5434, bound to 127.0.0.1](0009-local-db-port-5434-localhost-only.md) (Step 3)
- [0010. Exercise table: metadata columns with CHECK constraints](0010-exercise-table-check-constraints.md) (Step 4, note on the mirrored Pydantic lists added in Step 5)
- [0011. Phase 1 plan revision: ingestion and LangSmith get concrete steps](0011-phase-1-plan-revision-ingestion-and-langsmith.md) (Step 5, Step 15 and Phase 1F scope extended by 0012; order amended after Step 10: ingestion Steps 11 to 13, LangSmith Step 14)
- [0012. Evaluate keyword search as a baseline; add query rewriting to Phase 1F](0012-keyword-baseline-and-query-rewriting.md) (between Steps 5 and 6; note after Step 10: its step numbers are unaffected by the reorder)
- [0013. LLM via OpenRouter with the openai SDK; default Qwen3 235B](0013-llm-openrouter-openai-sdk-qwen.md) (Step 6, supersedes 0003; default switched to Gemini 2.5 Flash-Lite in Step 10)
- [0014. Embedded text: name + description + labeled facts, no instructions](0014-embedded-text-name-description-labels.md) (Step 8)
- [0015. Local web UI: FastAPI + one static HTML page](0015-local-web-ui-fastapi-static-html.md) (Step 10)
- [0016. Answer grounding: evidence-only answer plus labeled general guidance](0016-answer-grounding-evidence-plus-labeled-general-guidance.md) (after Step 10)
- [0017. Knowledge source licensing policy (groups A–D)](0017-knowledge-source-licensing-policy.md) (before Step 11, **accepted** 2026-09-25; NSCA enters only as original notes, drafted from locally extracted position statements)
