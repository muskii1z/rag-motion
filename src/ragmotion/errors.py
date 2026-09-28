"""Turn low-level failures into one plain sentence that says what's wrong and how to fix it.

Used by the web app and the command-line scripts. The original exception is still logged
(web app) or available with --debug-style tracebacks, so nothing is hidden from debugging.
"""

import openai


class DatabaseUnavailable(RuntimeError):
    """Postgres can't be reached (usually: Docker isn't running or the container is stopped)."""


def friendly_message(exc: BaseException) -> tuple[int, str]:
    """(HTTP status, message) for an exception raised while answering a question."""
    if isinstance(exc, DatabaseUnavailable):
        return 503, str(exc)
    if isinstance(exc, openai.AuthenticationError):
        return 502, "OpenRouter rejected the API key. Check OPENROUTER_API_KEY in .env."
    if isinstance(exc, openai.RateLimitError):
        return 503, "OpenRouter is rate-limiting requests or the key is out of credit. Wait a moment, or check the key's limit on openrouter.ai."
    if isinstance(exc, (openai.APIConnectionError, openai.APITimeoutError)):
        return 503, "Couldn't reach OpenRouter. Check the internet connection and try again."
    if isinstance(exc, openai.APIStatusError):
        return 502, f"OpenRouter returned an error (HTTP {exc.status_code}). Try again, or try another model with LLM_MODEL in .env."
    if isinstance(exc, RuntimeError):  # our own errors already explain themselves (e.g. missing API key)
        return 500, str(exc)
    return 500, f"Unexpected error ({type(exc).__name__}). Details are in the server log."
