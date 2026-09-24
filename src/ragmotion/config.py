"""Settings loaded from environment variables or the .env file.

Every other module imports `settings` from here, so there is exactly one place
that knows where configuration comes from.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Default matches docker-compose.yml, so the database works even before .env exists.
    database_url: str = "postgresql://postgres:postgres@localhost:5434/ragmotion"

    # API keys are optional here; the step that needs a key checks for it.
    openrouter_api_key: str | None = None
    voyage_api_key: str | None = None
    anthropic_api_key: str | None = None


settings = Settings()
