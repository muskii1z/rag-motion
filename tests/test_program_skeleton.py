"""Structure fix: every skeleton satisfies every structural rule by construction.

For each day count (1-6) and a range of clients, code fills each slot with a plain choice and the full checker
runs. If the skeleton is right, nothing fails, without any model involved.
"""

import pytest

from ragmotion.models import ClientProfile
from ragmotion.program import TIMED, ProgramSubmission, SlotFill, assemble, build_skeleton, check_program, failed

CLIENTS = {
    "full gym beginner": dict(unmapped_equipment=["gym"]),
    "full gym intermediate": dict(unmapped_equipment=["gym"], experience_level="intermediate"),
    "dumbbells + bench": dict(equipment=["dumbbell", "bench"]),
    "bodyweight only": dict(equipment=["bodyweight"]),
    "bands + pull-up bar": dict(equipment=["band", "pullup-bar"]),
    "70-year-old, dumbbells + bands": dict(equipment=["dumbbell", "band"], age=70),
    "one kettlebell, fat loss": dict(equipment=["kettlebell"], goal="lose fat"),
}


def profile(**kw) -> ClientProfile:
    base = dict(goal="build muscle", sessions_per_week=3, session_duration_minutes=None, equipment=[], unmapped_equipment=[],
                experience_level="beginner", age=None, health_issues=[], context_notes=[])
    return ClientProfile(**{**base, **kw})


def plain_fill(skeleton):
    fills = []
    for d in skeleton:
        used = set()
        for s in d["slots"]:
            opt = next((o for o in s["options"] if o["slug"] not in used), s["options"][0])
            used.add(opt["slug"])
            fills.append(SlotFill(day=d["day"], slot=s["slot"], slug=opt["slug"], sets="3",
                                  reps="30 s" if opt["slug"] in TIMED else "8-12", rest="90 s"))
    return fills


@pytest.mark.parametrize("client", CLIENTS)
@pytest.mark.parametrize("days", range(1, 7))
def test_every_skeleton_passes_every_structural_check(client, days):
    p = profile(sessions_per_week=days, **CLIENTS[client])
    skeleton = build_skeleton(p)
    rationale = "Nutrition matters for fat loss but isn't covered by these sources [notes-program-design-1]."
    draft, problems = assemble(ProgramSubmission(title="t", fills=plain_fill(skeleton), progression="p [notes-program-design-1]",
                                                 rationale=rationale, cited_ids=["notes-program-design-1"]), skeleton)
    assert problems == []
    assert [f"{c.name} ({c.detail})" for c in failed(check_program(draft, p, {"notes-program-design-1"}))] == []


def test_wrong_picks_are_sent_back_with_the_allowed_options():
    sk = build_skeleton(profile(equipment=["dumbbell", "bench"]))
    fills = plain_fill(sk)
    fills[0] = fills[0].model_copy(update={"slug": "barbell-back-squat"})  # not an option for this client
    draft, problems = assemble(ProgramSubmission(title="t", fills=fills[:-1], progression="p", rationale="r", cited_ids=[]), sk)
    assert draft is None
    assert any("'barbell-back-squat' isn't an option; choose one of" in p for p in problems)
    assert any("is empty: choose one of" in p for p in problems)  # the dropped last fill


def test_no_bodyweight_preference_removes_bodyweight_options_where_alternatives_exist():
    from ragmotion.agent import AVOID_BODYWEIGHT
    assert AVOID_BODYWEIGHT.search("I don't want bodyweight exercises") and AVOID_BODYWEIGHT.search("no body weight stuff")
    assert not AVOID_BODYWEIGHT.search("I'm at home with bodyweight only")
    sk = build_skeleton(profile(equipment=["dumbbell", "bench"]), avoid_bodyweight=True)
    options = [o for d in sk for s in d["slots"] for o in s["options"]]
    assert options and not any(o["equipment"] == ["bodyweight"] for o in options)  # core slots became carries
    # With no equipment there's no alternative, so bodyweight options stay.
    bw = build_skeleton(profile(equipment=["bodyweight"]), avoid_bodyweight=True)
    assert all(s["options"] for d in bw for s in d["slots"])


def test_gym_means_all_equipment_even_if_the_reader_listed_some(monkeypatch):
    from ragmotion import agent
    partial = profile(equipment=["barbell", "machine"])
    monkeypatch.setattr(agent, "extract_profile", lambda text: (partial.model_copy(), None))
    p = agent.read_profile([{"role": "user", "content": "I love back squats. 4 days, full gym, intermediate"}])
    assert "gym" in p.unmapped_equipment
    home = agent.read_profile([{"role": "user", "content": "I have a home gym with dumbbells"}])
    assert "gym" not in home.unmapped_equipment


def test_exercises_the_client_names_are_found():
    from ragmotion.agent import mentioned_exercises
    liked, _ = mentioned_exercises([{"role": "user", "content": "I love back squats and hip thrusts"}])
    assert "barbell-back-squat" in liked and "dumbbell-hip-thrust" in liked


@pytest.mark.parametrize("text, gym", [
    ("I love back squats. 4 days, full gym, intermediate", True),
    ("I train at the gym 3 days a week", True),
    ("I have gym access", True),
    ("Beginner to the gym, I train at home with dumbbells", False),
    ("I quit the gym", False),
    ("gym at home with a rack", False),
    ("home-gym setup", False),
    ("Home  gym", False),
    ("I work out at home but have gym access", True),
    ("I have a gym at work", True),
    ("I use my work gym", True),
    ("I train at home, no gym access", False),
    ("I cancelled my gym membership", False),
    ("I used to have gym access", False),
    ("My work gym closed, so I train at home now", False),
    ("I have gym access but I also train at home", True),
])
def test_gym_access_phrases(text, gym):
    from ragmotion.agent import mentions_gym
    assert mentions_gym(text) == gym


def test_liked_and_avoided_exercises_are_told_apart():
    from ragmotion.agent import mentioned_exercises
    liked, avoided = mentioned_exercises([{"role": "user", "content": "I love back squats and hip thrusts. I hate deadlifts."}])
    assert {"barbell-back-squat", "dumbbell-hip-thrust"} <= set(liked) and "bodyweight-squat" not in liked
    assert {"barbell-deadlift", "kettlebell-deadlift"} <= set(avoided) and not set(avoided) & set(liked)


def test_avoided_exercises_are_removed_where_alternatives_exist():
    sk = build_skeleton(profile(unmapped_equipment=["gym"], experience_level="intermediate"), avoid={"barbell-deadlift", "kettlebell-deadlift"})
    hinge_options = [o["slug"] for d in sk for s in d["slots"] if s["label"] == "hinge" for o in s["options"]]
    assert hinge_options and not {"barbell-deadlift", "kettlebell-deadlift"} & set(hinge_options)


@pytest.mark.parametrize("goal, vague", [("workout program", True), ("a training plan", True), ("Routine", True),
                                         ("build muscle", False), ("strength program for soccer", False)])
def test_a_goal_that_restates_the_request_counts_as_missing(goal, vague):
    from ragmotion.program import missing_for_program
    assert ("goal" in missing_for_program(profile(goal=goal))) == vague


@pytest.mark.parametrize("text, avoided", [
    ("I don't like RDLs", {"dumbbell-romanian-deadlift", "single-leg-romanian-deadlift"}),
    ("I hate Romanian deadlifts", {"dumbbell-romanian-deadlift", "single-leg-romanian-deadlift"}),
    ("I hate deadlifts", {"barbell-deadlift", "kettlebell-deadlift", "dumbbell-romanian-deadlift", "single-leg-romanian-deadlift"}),
])
def test_shorthand_and_variants_of_disliked_exercises(text, avoided):
    from ragmotion.agent import mentioned_exercises
    assert set(mentioned_exercises([{"role": "user", "content": text}])[1]) == avoided
