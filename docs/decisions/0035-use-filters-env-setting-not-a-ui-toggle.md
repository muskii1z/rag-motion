# 0035. USE_FILTERS environment setting for demo recordings, not a UI toggle
**Date:** 2026-09-30 · **Step:** eval resilience and demo recordings (after Phase 1F F7b) · **Status:** accepted

## Context
The developer's portfolio needs a before-and-after recording of the filters: the same question with filters off, then on. The pipeline already had a `use_filters` switch (used by the evals), but the web app always ran with filters on. The developer asked, "How hard is it to turn the filters off and on?"

## Options considered
- **A toggle in the web page.** Pros: switch live while recording. Cons: a new UI feature to build and test; it would let any user switch off the safety filters.
- **An environment setting read at startup.** Pros: a few lines (`use_filters: bool = True` in `config.py`, overridable with `USE_FILTERS`, passed by `app.py` to `answer_question`); no UI change. Cons: switching needs a server restart.

## Decision
An environment setting. `USE_FILTERS=false uv run uvicorn ragmotion.app:app --host 127.0.0.1 --port 8010` starts the app without filters; the default stays on. The developer's reason: "I just need a before clip." Commit `23e6c73`. See [Feature flag](../concepts.md#feature-flag-config-switch).

## Tradeoffs
- A restart between the "before" and "after" recordings.
- The setting exists in production code. If someone started the app with `USE_FILTERS=false` by mistake, the filters would be off with nothing on the page to show it.

## Revisit when
- A live comparison is wanted for a demo or a coach review: then a developer-only toggle might be worth building.
- The app is deployed: consider removing the setting, or refusing `USE_FILTERS=false` outside local development.
