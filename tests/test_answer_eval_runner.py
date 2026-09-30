"""The local answer-eval runner (evals/run_answer_eval.py) works without LangSmith and reports broken checks."""

import sys

from ragmotion.evaluation import EvalQuestion
from ragmotion.ingestion import PROJECT_ROOT

sys.path.insert(0, str(PROJECT_ROOT / "evals"))
import run_answer_eval as runner  # noqa: E402

OUTPUTS = {"answer": "Try the goblet squat [goblet-squat].", "general_guidance": None, "evidence_coverage": "full",
           "cited_ids": ["goblet-squat"], "retrieved_exercises": ["goblet-squat"], "citation_problems": [],
           "cited_passages": []}


def test_evaluators_get_the_arguments_they_ask_for():
    ref = runner.reference(EvalQuestion(id="t", question="q", category="c", expected_exercises=["goblet-squat"]))
    [result] = runner.run_evaluator(runner.exercise_completeness, {"question": "q"}, OUTPUTS, ref)
    assert result["key"] == "exercise_completeness" and result["score"] == 1.0


def test_a_broken_check_is_reported_not_fatal(monkeypatch):
    def judge_down(*args, **kwargs):
        raise RuntimeError("judge unavailable")
    monkeypatch.setattr(runner, "judge_answer", judge_down)
    ref = runner.reference(EvalQuestion(id="t", question="q", category="c", answer_rules=["label-level"]))
    [result] = runner.run_evaluator(runner.coach_rules, {"question": "q"}, OUTPUTS, ref)
    assert result["score"] is None and result["error"] and "judge unavailable" in result["comment"]


def test_local_run_needs_no_langsmith(monkeypatch):
    questions = [EvalQuestion(id="a", question="q1", category="c", expected_exercises=["goblet-squat"]),
                 EvalQuestion(id="b", question="q2", category="c")]
    def target(inputs):
        if inputs["question"] == "q2":
            raise TimeoutError("answer service slow")
        return OUTPUTS
    rows = runner.run_locally(questions, target)
    assert rows[0]["error"] is None and any(r["key"] == "citations_valid" and r["score"] == 1 for r in rows[0]["results"])
    assert rows[1]["error"].startswith("TimeoutError")  # a failed question is recorded, not dropped silently
