"""Friendly error messages for the web app and scripts."""

import httpx2
import openai

from ragmotion.errors import DatabaseUnavailable, friendly_message


def test_database_down_says_how_to_fix_it():
    status, message = friendly_message(DatabaseUnavailable("Can't reach the database. Is Docker running?"))
    assert status == 503 and "Docker" in message


def test_bad_api_key_points_at_env_file():
    request = httpx2.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    exc = openai.AuthenticationError("bad key", response=httpx2.Response(401, request=request), body=None)
    status, message = friendly_message(exc)
    assert status == 502 and "OPENROUTER_API_KEY" in message


def test_unknown_errors_dont_leak_internals():
    status, message = friendly_message(ZeroDivisionError("secret internals"))
    assert status == 500 and "secret internals" not in message
