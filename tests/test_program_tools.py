"""Phase 2 program agent: the tools filter in code, whatever the agent asks for."""

from ragmotion.agent import TOOLS, _inline_refs
from ragmotion.models import ClientProfile
from ragmotion.program import find_exercises, missing_for_program, population


def profile(**kw) -> ClientProfile:
    base = dict(goal=None, sessions_per_week=None, session_duration_minutes=None, equipment=[], unmapped_equipment=[],
                experience_level=None, age=None, health_issues=[], context_notes=[])
    return ClientProfile(**{**base, **kw})


def test_find_exercises_only_returns_what_the_client_can_use():
    dumbbells = profile(equipment=["dumbbell", "bench"], experience_level="beginner")
    hinges = {e["slug"] for e in find_exercises("hinge", dumbbells)}
    assert "dumbbell-romanian-deadlift" in hinges and "barbell-deadlift" not in hinges  # no barbell
    assert "single-leg-romanian-deadlift" not in hinges  # intermediate, client is a beginner


def test_full_gym_means_everything_and_older_adults_get_no_jumps():
    gym = profile(unmapped_equipment=["full gym"], experience_level="intermediate")
    assert "barbell-bench-press" in {e["slug"] for e in find_exercises("push", gym)}
    older = profile(equipment=["bodyweight"], experience_level="advanced", age=70)
    assert find_exercises("jump", older) == []  # coach rule: no jumps for older adults
    assert population(older) == "older-adults" and population(profile()) == "adults"


def test_missing_details_are_computed_and_the_submit_schema_has_no_refs():
    assert missing_for_program(profile(experience_level="beginner")) == ["goal", "sessions_per_week", "equipment"]
    submit = next(t for t in TOOLS if t["function"]["name"] == "submit_program")["function"]["parameters"]
    assert "$ref" not in str(submit) and "$defs" not in submit
