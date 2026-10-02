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
    found = mentioned_exercises([{"role": "user", "content": "I love back squats and hip thrusts"}])
    assert "barbell-back-squat" in found and "dumbbell-hip-thrust" in found
