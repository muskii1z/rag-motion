# rag-motion

An AI-native movement and exercise programming application, built step by step as an AI engineering portfolio project.

**Current phase:** Phase 1, Production RAG Fundamentals. The goal is a small, fully understood retrieval-augmented generation (RAG) system over an exercise knowledge base:

```
question → embedding → pgvector search → retrieved exercises → Claude → grounded answer + sources
```

**Stack:** Python 3.12 (uv) · PostgreSQL 16 + pgvector · Voyage AI embeddings · Claude

The build is documented as it happens:

- [Build log](docs/build-log.md): what was built at each step, and what went wrong
- [Decisions](docs/decisions/README.md): each technical choice, the alternatives, and the tradeoffs
- [Concepts](docs/concepts.md): everything learned along the way, in plain language
