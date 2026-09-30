"""Settings loaded from environment variables or the .env file.

Every other module imports `settings` from here, so there is exactly one place
that knows where configuration comes from.
"""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Also load .env into the process environment. Libraries that read their own environment
# variables (LangSmith: LANGSMITH_API_KEY, LANGSMITH_TRACING, LANGSMITH_PROJECT) need this;
# pydantic-settings alone only fills the Settings object below.
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Default matches docker-compose.yml, so the database works even before .env exists.
    database_url: str = "postgresql://postgres:postgres@localhost:5434/ragmotion"

    # Which LLM to use through OpenRouter. Change here or set LLM_MODEL in .env.
    llm_model: str = "google/gemini-2.5-flash-lite"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Every call to OpenRouter (LLM and embeddings) gives up after this many seconds, and is retried
    # at most this many times. Without a limit, a hung call would wait the library's default 10 minutes.
    # A normal answer takes 2-5 s, so 25 s with 1 retry means a clear error within about a minute.
    # Phase 1F filters (equipment, age group). Only turned off to show the "before" behavior,
    # e.g. for a demo recording: USE_FILTERS=false uv run uvicorn ragmotion.app:app ...
    use_filters: bool = True

    # F7c: expand coach slang before search: "none", "dictionary" or "llm" (see rewrite.py).
    query_rewrite: str = "dictionary"  # chosen 2026-09-30: same quality as the LLM rewrite, free, no added time

    api_timeout_seconds: float = 25.0
    api_max_retries: int = 1

    # Embedding model, also through OpenRouter. Must match the vector(1024) column in
    # db/schema.sql. Changing the model means re-embedding every stored row.
    embedding_model: str = "voyageai/voyage-4-lite"
    embedding_dimensions: int = 1024

    # API keys are optional here; the step that needs a key checks for it.
    openrouter_api_key: str | None = None
    voyage_api_key: str | None = None
    anthropic_api_key: str | None = None


settings = Settings()
