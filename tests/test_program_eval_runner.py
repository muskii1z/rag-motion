"""P4: the program-eval scoring is plain code with one right answer per expectation."""

import sys

from ragmotion.ingestion import PROJECT_ROOT

sys.path.insert(0, str(PROJECT_ROOT / "evals"))
import run_program_eval as runner  # noqa: E402

PROGRAM = {"title": "T", "rationale": "Moderate loads [pelland2024-volume-3].", "progression": "Add load [notes-program-design-1].",
           "safety_notes": "Check with a health professional about your knee.", "cited_ids": ["pelland2024-volume-3"],
           "days": [{"name": "Day 1", "exercises": [{"name": "Push-Up", "sets": "3", "reps": "8", "equipment": ["bodyweight"]}]}]}
TURN = {"kind": "program", "text": "T", "passed_checks": True, "checks": [], "program": PROGRAM}


def test_expectations_are_scored_in_code():
    s = runner.score(TURN, {"kind": "program", "passes_checks": True, "has_referral": True, "no_referral": True,
                            "no_adult_research": True, "no_bodyweight_only": True, "mentions_any": ["knee"]})
    assert s == {"kind": True, "passes_checks": True, "has_referral": True, "no_referral": True,
                 "no_adult_research": False, "no_bodyweight_only": False, "mentions_any": True}


def test_question_must_ask_about_each_missing_detail():
    q = {"kind": "question", "text": "What's your goal, and how many days a week?", "checks": [], "program": None}
    assert runner.score(q, {"question_mentions": ["goal", "days", "equipment"]}) == {"question_mentions": False}
