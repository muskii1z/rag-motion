"""The web API (POST /api/ask), tested like the browser uses it, with every outside service faked.

"Mocking": the real Gemini, Voyage and database calls are swapped for fakes that return fixed
answers or pretend to fail. The tests are free, take milliseconds, and give the same result every
time. What they check has one right answer: the response shape, and the exact message for each
failure. Whether an answer is *good* is the evals' job, not these tests'.
"""

import httpx2
import openai
import pytest
from conftest import make_exercise, make_passage
from fastapi.testclient import TestClient

from ragmotion import embeddings, llm, rag, retrieval
from ragmotion.app import MAX_QUESTION_CHARS, app
from ragmotion.config import settings
from ragmotion.errors import DatabaseUnavailable
from ragmotion.llm import LLMUsage
from ragmotion.models import GroundedAnswer, QuestionLimits

QUESTION = "I only have dumbbells. Good lower-body exercises?"
USAGE = LLMUsage(model="fake-model", prompt_tokens=10, completion_tokens=5, cost_usd=0.0)
FAKE_REQUEST = httpx2.Request("POST", "https://openrouter.ai/api/v1/fake")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def calls():
    """Records which fake services were called, so tests can check nothing was called at all."""
    return []


@pytest.fixture
def fake_limits(monkeypatch, calls):
    """Fake 'read the limits' call (Gemini): the question states no limits."""
    def fake(question):
        calls.append("limits")
        return QuestionLimits(equipment_limited=False, equipment_owned=[], limit_phrase=None, population=None), USAGE
    monkeypatch.setattr(rag, "extract_limits", fake)


@pytest.fixture
def fake_search(monkeypatch, calls):
    """Fake search (Voyage + database): one exercise and one passage."""
    def fake(question, k_exercises=5, k_passages=5, owned=None, population=None):
        calls.append("search")
        return [make_exercise("goblet-squat")], [make_passage("pag2", 57)]
    monkeypatch.setitem(retrieval.SEARCH_MODES, "semantic", fake)


@pytest.fixture
def fake_answer(monkeypatch, calls):
    """Fake answer call (Gemini): a valid answer citing both retrieved items."""
    def fake(system_prompt, user_content, response_model, **kwargs):
        calls.append("answer")
        return GroundedAnswer(
            answer="Start with the goblet squat [goblet-squat]. Train major muscle groups 2+ days a week [pag2-57].",
            cited_ids=["goblet-squat", "pag2-57"], evidence_coverage="full", gaps=None, general_guidance=None,
        ), USAGE
    monkeypatch.setattr(rag, "structured_completion", fake)


# ---- Normal use ----

def test_a_normal_question_returns_an_answer_with_its_sources(client, fake_limits, fake_search, fake_answer):
    res = client.post("/api/ask", json={"question": QUESTION})
    assert res.status_code == 200
    body = res.json()
    assert "goblet squat" in body["answer"]
    assert body["citation_problems"] == []  # the real citation checker ran on the fake answer
    assert [e["id"] for e in body["exercises"]] == ["goblet-squat"] and body["exercises"][0]["cited"]
    assert [p["id"] for p in body["passages"]] == ["pag2-57"] and body["passages"][0]["cited"]


# ---- Bad questions: rejected with a plain sentence before any paid call ----

@pytest.mark.parametrize("question", ["", "   ", "hi"])
def test_an_empty_question_gets_a_clear_message(client, calls, fake_limits, fake_search, fake_answer, question):
    res = client.post("/api/ask", json={"question": question})
    assert res.status_code == 400
    assert res.json()["detail"] == "Please type a question."
    assert calls == []  # never reached Gemini, Voyage or the database


def test_a_very_long_question_gets_a_clear_message(client, calls, fake_limits, fake_search, fake_answer):
    res = client.post("/api/ask", json={"question": "squat " * 200})
    assert res.status_code == 400
    assert f"up to {MAX_QUESTION_CHARS} characters" in res.json()["detail"]
    assert calls == []


# ---- Outside services failing ----

def test_gemini_too_slow_says_try_again(client, monkeypatch, fake_limits, fake_search):
    def slow(*args, **kwargs):
        raise openai.APITimeoutError(request=FAKE_REQUEST)
    monkeypatch.setattr(rag, "structured_completion", slow)
    res = client.post("/api/ask", json={"question": QUESTION})
    assert res.status_code == 503
    assert res.json()["detail"] == "The answer service took too long to respond. Try again in a minute."


def test_gemini_down_says_temporarily_unavailable(client, monkeypatch, fake_limits, fake_search):
    def down(*args, **kwargs):
        raise openai.InternalServerError("upstream error", response=httpx2.Response(502, request=FAKE_REQUEST), body=None)
    monkeypatch.setattr(rag, "structured_completion", down)
    res = client.post("/api/ask", json={"question": QUESTION})
    assert res.status_code == 503
    assert "temporarily unavailable" in res.json()["detail"]


def test_broken_json_twice_gives_a_clear_message_after_one_retry(client, monkeypatch, fake_limits, fake_search):
    # Fake only the single model call, so the real retry logic in structured_completion runs.
    attempts = []
    def broken(*args, **kwargs):
        attempts.append(1)
        GroundedAnswer.model_validate_json('{"answer": "Start with the gob')  # cut off mid-string, like a real failure
    monkeypatch.setattr(llm, "_structured_completion_once", broken)
    monkeypatch.setattr(rag, "structured_completion", llm.structured_completion)
    res = client.post("/api/ask", json={"question": QUESTION})
    assert len(attempts) == 2  # first try + one retry
    assert res.status_code == 502
    assert res.json()["detail"] == "The AI sent back an unreadable answer 2 times in a row. Please ask again."


def test_voyage_down_says_search_is_unavailable(client, monkeypatch, fake_limits):
    # Real search_all and real embedding code; only the network call to Voyage fails.
    class DeadEmbeddings:
        def create(self, **kwargs):
            raise openai.APIConnectionError(request=FAKE_REQUEST)
    class DeadClient:
        embeddings = DeadEmbeddings()
    monkeypatch.setattr(embeddings, "get_client", lambda: DeadClient())
    res = client.post("/api/ask", json={"question": QUESTION})
    assert res.status_code == 503
    assert "search service" in res.json()["detail"]


def test_database_down_says_start_docker(client, monkeypatch, fake_limits):
    monkeypatch.setattr(retrieval, "embed_query", lambda text: [0.0] * 1024)  # Voyage works
    def no_db():
        raise DatabaseUnavailable("Can't reach the database. Is Docker running? Start it with: docker compose up -d --wait")
    monkeypatch.setattr(retrieval, "get_connection", no_db)
    res = client.post("/api/ask", json={"question": QUESTION})
    assert res.status_code == 503
    assert "docker compose up" in res.json()["detail"]


def test_unexpected_errors_dont_leak_internals(client, monkeypatch, fake_limits, fake_search):
    def bug(*args, **kwargs):
        raise KeyError("internal detail")
    monkeypatch.setattr(rag, "structured_completion", bug)
    res = client.post("/api/ask", json={"question": QUESTION})
    assert res.status_code == 500
    assert "internal detail" not in res.json()["detail"]


# ---- Every outside call has a time limit ----

def test_every_openrouter_call_has_a_time_limit(monkeypatch):
    monkeypatch.setattr(settings, "openrouter_api_key", "test-key")  # no real key needed; nothing is sent
    c = llm.get_client()
    assert c.timeout == settings.api_timeout_seconds and c.max_retries == settings.api_max_retries
