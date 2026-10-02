"""Phase 2, step 2: the program checker, and the agent-loop guardrails driven by a scripted fake model."""

import json
from types import SimpleNamespace

from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall, Function

from ragmotion import agent
from ragmotion.models import ClientProfile
from ragmotion.program import ProgramDraft, check_program, failed


def profile(**kw) -> ClientProfile:
    base = dict(goal="build muscle", sessions_per_week=2, session_duration_minutes=None, equipment=["dumbbell", "bench"],
                unmapped_equipment=[], experience_level="beginner", age=None, health_issues=[], context_notes=[])
    return ClientProfile(**{**base, **kw})


def x(slug, reps="8-12"):
    return {"slug": slug, "sets": "3", "reps": reps, "rest": "90 s"}


GOOD_DAY = [x("goblet-squat"), x("dumbbell-romanian-deadlift"), x("push-up"), x("one-arm-dumbbell-row"), x("front-plank", "30 s")]
GOOD = {"title": "Two-day beginner", "days": [{"name": "Day 1", "exercises": GOOD_DAY}, {"name": "Day 2", "exercises": GOOD_DAY}],
        "progression": "Add load after hitting 12 reps [notes-program-design-1].",
        "rationale": "8-12 reps for muscle [notes-program-design-1].", "cited_ids": ["notes-program-design-1"], "safety_notes": None}


def test_a_good_program_passes_every_check():
    checks = check_program(ProgramDraft.model_validate(GOOD), profile(), {"notes-program-design-1"})
    assert failed(checks) == []


def test_the_checker_catches_what_the_agent_got_wrong_in_step_1():
    bad = json.loads(json.dumps(GOOD))
    bad["days"][0]["exercises"] += [x("dumbbell-reverse-lunge"), x("farmer-carry", "8")]  # 7 exercises; carry in reps
    bad["days"][1]["exercises"][0] = x("barbell-back-squat")  # needs barbell + rack
    bad["rationale"] = "Trust me [made-up-source-3]."
    names = {c.name for c in failed(check_program(ProgramDraft.model_validate(bad), profile(), {"notes-program-design-1"}))}
    assert "4 to 6 exercises per day" in names
    assert "planks and carries in seconds or metres, not reps" in names
    assert "only equipment the client has" in names
    assert "citations come from the agent's own searches" in names


def test_injuries_need_a_referral_reminder():
    checks = check_program(ProgramDraft.model_validate(GOOD), profile(context_notes=["sore knee"]), {"notes-program-design-1"})
    assert [c.name for c in failed(checks)] == ["client's conditions acknowledged, with a reminder to see a health professional"]


# ---- Agent loop guardrails, with a fake model that follows a script ----

def call(name, **args):
    return ChatCompletionMessageToolCall(id=f"call-{name}", type="function", function=Function(name=name, arguments=json.dumps(args)))


class ScriptedModel:
    """Returns the scripted replies in order: a list of tool calls, or a text string."""
    def __init__(self, script):
        self.script, self.seen = list(script), []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.seen.append(kwargs["messages"][-1])
        assert not isinstance(kwargs.get("tool_choice"), dict), "named tool_choice isn't supported by every provider"
        self.tools_offered = getattr(self, "tools_offered", []) + [[t["function"]["name"] for t in kwargs["tools"]]]
        step = self.script.pop(0)
        msg = SimpleNamespace(content=step if isinstance(step, str) else "", tool_calls=None if isinstance(step, str) else step)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)], usage=None)


def run(monkeypatch, script, prof):
    model = ScriptedModel(script)
    monkeypatch.setattr(agent, "get_client", lambda: model)
    monkeypatch.setattr(agent, "read_profile", lambda conversation: prof)
    monkeypatch.setattr(agent, "search_sources", lambda q, p: [{"id": "notes-program-design-1", "text": "..."}])
    return agent.run_turn([{"role": "user", "content": "beginner program please"}]), model


# The agent now submits slot fills (structure fix); code assembles the program from the skeleton.
def _submission(prof, bad=False):
    from ragmotion.program import TIMED, build_skeleton
    fills = []
    for d in build_skeleton(prof):
        used = set()
        for s in d["slots"]:
            opt = next((o for o in s["options"] if o["slug"] not in used), s["options"][0])
            used.add(opt["slug"])
            fills.append({"day": d["day"], "slot": s["slot"], "slug": opt["slug"], "sets": "3",
                          "reps": "30 s" if opt["slug"] in TIMED else "8-12", "rest": "90 s"})
    if bad:
        fills[0]["slug"] = "barbell-back-squat"  # not an option for a dumbbell client
    return {"title": "Two-day beginner", "fills": fills, "progression": "Add load [notes-program-design-1].",
            "rationale": "8-12 reps for muscle [notes-program-design-1].", "cited_ids": ["notes-program-design-1"]}


def test_building_is_refused_until_the_details_are_known(monkeypatch):
    turn, model = run(monkeypatch, [[call("get_plan_skeleton")], "What equipment do you have?"],
                      profile(equipment=[]))
    assert turn.steps[0]["result"] == "refused: ask about equipment"
    assert turn.kind == "question" and "equipment" in turn.text  # details missing: a text reply is a question


def test_an_empty_reply_gets_one_nudge_then_a_clear_error(monkeypatch):
    turn, _ = run(monkeypatch, ["", ""], profile())
    assert turn.kind == "error" and turn.text == "The program builder didn't respond. Please try again."


def test_the_checker_sends_a_bad_program_back_and_accepts_the_fix(monkeypatch):
    too_big = json.loads(json.dumps(GOOD))
    too_big["days"][0]["exercises"] += [x("dumbbell-reverse-lunge"), x("dumbbell-hip-thrust")]
    script = [[call("search_sources", query="sets and reps for muscle")],
              [call("submit_program", **_submission(profile(), bad=True))], [call("submit_program", **_submission(profile()))]]
    turn, _ = run(monkeypatch, script, profile())
    assert turn.steps[1]["result"].startswith("rejected: slot picks")
    assert turn.kind == "program" and turn.passed_checks


def test_non_health_notes_dont_demand_a_referral():
    checks = check_program(ProgramDraft.model_validate(GOOD), profile(context_notes=["little lifting experience"]), {"notes-program-design-1"})
    assert failed(checks) == []


def test_backup_word_check_catches_casual_complaints_but_not_coming_back():
    from ragmotion.program import HEALTH_PATTERN
    for complaint in ["bad knee", "lower back pain", "had shoulder surgery", "hurt my back", "my back hurts",
                      "tweaked my back", "strained my hamstring", "herniated disc"]:
        assert HEALTH_PATTERN.search(complaint), complaint
    for fine in ["coming back to lifting after a break", "little lifting experience", "getting back into training"]:
        assert not HEALTH_PATTERN.search(fine), fine


def test_ai_read_health_issues_trigger_the_referral():
    checks = check_program(ProgramDraft.model_validate(GOOD), profile(health_issues=["type 2 diabetes"]), {"notes-program-design-1"})
    assert [c.name for c in failed(checks)] == ["client's conditions acknowledged, with a reminder to see a health professional"]


def test_a_guessed_bodyweight_is_ignored_unless_the_client_said_it(monkeypatch):
    guessed = profile(equipment=["bodyweight"])
    monkeypatch.setattr(agent, "extract_profile", lambda text: (guessed.model_copy(), None))
    assert agent.read_profile([{"role": "user", "content": "beginner to the gym, build muscle"}]).equipment == []
    assert agent.read_profile([{"role": "user", "content": "I have no equipment"}]).equipment == ["bodyweight"]


def test_a_pattern_with_no_usable_exercises_isnt_required():
    day = [x("split-squat"), x("glute-bridge"), x("push-up"), x("dead-bug"), x("front-plank", "30 s")]
    draft = {**GOOD, "days": [{"name": "Day 1", "exercises": day}, {"name": "Day 2", "exercises": day}]}
    checks = check_program(ProgramDraft.model_validate(draft), profile(equipment=["bodyweight"]), {"notes-program-design-1"})
    pull = next(c for c in checks if c.name.startswith("pull"))
    assert pull.passed and "no exercises available" in pull.detail


def test_forcing_a_submission_offers_only_the_submit_tool(monkeypatch):
    too_big = json.loads(json.dumps(GOOD))
    too_big["days"][0]["exercises"] += [x("dumbbell-reverse-lunge"), x("dumbbell-hip-thrust")]
    script = [[call("search_sources", query="sets and reps for muscle")],
              [call("submit_program", **_submission(profile(), bad=True))], "Could you remove an exercise?", [call("submit_program", **_submission(profile()))]]
    turn, model = run(monkeypatch, script, profile())
    assert model.tools_offered[2] == ["submit_program"]  # after the rejection: submit only, chatting nudged away
    assert turn.kind == "program" and turn.passed_checks


# ---- Q1: program quality ----

def ex(slug, sets="3", reps="8-12"):
    return {"slug": slug, "sets": sets, "reps": reps, "rest": "90 s"}


# The developer's real 4-day program (2026-10-01): passed the old checks, but a coach spotted
# almost no chest work and a glute bridge + hip thrust on the same day.
DEVELOPERS_PROGRAM = {**GOOD, "title": "Beginner 4-Day Upper/Lower", "days": [
    {"name": "Day 1: Upper Body A", "exercises": [ex("dumbbell-overhead-press"), ex("one-arm-dumbbell-row"), ex("dead-bug", reps="10-15"), ex("dumbbell-biceps-curl", "2")]},
    {"name": "Day 2: Lower Body A", "exercises": [ex("goblet-squat"), ex("dumbbell-romanian-deadlift"), ex("farmer-carry", reps="30 m"), ex("dumbbell-step-up")]},
    {"name": "Day 3: Upper Body B", "exercises": [ex("push-up"), ex("band-pull-apart"), ex("front-plank", reps="30 s"), ex("hammer-curl", "2")]},
    {"name": "Day 4: Lower Body B", "exercises": [ex("dumbbell-reverse-lunge"), ex("glute-bridge"), ex("pallof-press"), ex("dumbbell-hip-thrust")]},
]}


def test_the_developers_chest_light_program_is_now_rejected_with_exact_fixes():
    gym = profile(sessions_per_week=4, equipment=[], unmapped_equipment=["full gym"], goal="build muscle and get stronger")
    bad = {c.name: c for c in failed(check_program(ProgramDraft.model_validate(DEVELOPERS_PROGRAM), gym, {"notes-program-design-1"}))}
    assert "chest: 3" in bad["at least 6 weekly sets per major muscle group"].detail
    assert "add 3 more" in bad["at least 6 weekly sets per major muscle group"].fix
    assert "glute-bridge, dumbbell-hip-thrust" in bad["one exercise per movement pattern (and push/pull direction) per day"].fix


def test_an_upper_day_with_a_squat_is_flagged():
    draft = json.loads(json.dumps(GOOD))
    draft["days"][0]["name"] = "Day 1: Upper"
    names = {c.name for c in failed(check_program(ProgramDraft.model_validate(draft), profile(), {"notes-program-design-1"}))}
    assert "day names match their exercises (upper/lower/push/pull/legs)" in names


def test_weekly_sets_use_the_lower_bound_and_skip_unreachable_groups():
    from ragmotion.program import weekly_sets
    draft = json.loads(json.dumps(GOOD))
    draft["days"][0]["exercises"][2]["sets"] = "2-3"  # push-up: counts as 2
    assert weekly_sets(ProgramDraft.model_validate(draft))["chest"] == 5
    # No equipment: no back exercise exists in the catalog, so back volume isn't required.
    day = [x("split-squat"), x("glute-bridge"), x("push-up"), x("dead-bug"), x("front-plank", "30 s")]
    bw = {**GOOD, "days": [{"name": "Day 1", "exercises": day}, {"name": "Day 2", "exercises": day}]}
    volume = next(c for c in check_program(ProgramDraft.model_validate(bw), profile(equipment=["bodyweight"]), {"notes-program-design-1"})
                  if c.name.startswith("at least"))
    assert volume.passed and "back: 0" in volume.detail


def test_push_and_pull_count_per_direction_and_push_pull_days_are_checked():
    upper = [ex("dumbbell-bench-press"), ex("dumbbell-overhead-press"), ex("seated-cable-row"), ex("lat-pulldown")]
    two_flat = [ex("dumbbell-bench-press"), ex("incline-dumbbell-press"), ex("seated-cable-row"), ex("lat-pulldown")]
    gym = profile(sessions_per_week=2, equipment=[], unmapped_equipment=["full gym"])
    def failures(day, name="Day 1: Upper"):
        draft = {**GOOD, "days": [{"name": name, "exercises": day}, {"name": "Day 2", "exercises": GOOD_DAY}]}
        return {c.name: c for c in failed(check_program(ProgramDraft.model_validate(draft), gym, {"notes-program-design-1"}))}
    assert "one exercise per movement pattern (and push/pull direction) per day" not in failures(upper)  # flat + overhead: fine
    assert "horizontal push x2" in failures(two_flat)["one exercise per movement pattern (and push/pull direction) per day"].detail
    assert "day names match their exercises (upper/lower/push/pull/legs)" in failures(upper, "Day 1: Push")  # rows on a push day


def test_every_push_and_pull_exercise_has_a_direction():
    from ragmotion.program import catalog
    for slug, e in catalog().items():
        assert (e["movement_pattern"] in ("push", "pull")) == ("direction" in e), slug


def test_narrating_instead_of_submitting_forces_a_submission(monkeypatch):
    script = [[call("search_sources", query="sets and reps for muscle")],
              "</think>\n\nPerfect! I have the information I need. Let me summarize...", [call("submit_program", **_submission(profile()))]]
    turn, model = run(monkeypatch, script, profile())
    assert model.tools_offered[2] == ["submit_program"]
    assert turn.kind == "program" and turn.passed_checks


def test_leaked_reasoning_is_never_shown():
    assert agent._visible("<think>plan plan</think>What equipment do you have?") == "What equipment do you have?"
    assert agent._visible("</think>\n\nWhat equipment do you have?") == "What equipment do you have?"


def test_stated_volume_numbers_are_rejected_but_citing_research_is_fine():
    claimed = {**GOOD, "rationale": "Each major muscle group receives at least 6 weekly sets (chest: 6, back: 6, shoulders: 9, "
               "glutes/hamstrings: 15) [notes-program-design-1]."}
    bad = {c.name: c for c in failed(check_program(ProgramDraft.model_validate(claimed), profile(), {"notes-program-design-1"}))}
    assert "chest: 6" in bad["no weekly-set totals stated in the text (code shows the real ones)"].detail
    ranged = {**GOOD, "rationale": "This averages 10-13 sets per muscle group [notes-program-design-1]."}
    assert "no weekly-set totals stated in the text (code shows the real ones)" in {c.name for c in failed(
        check_program(ProgramDraft.model_validate(ranged), profile(), {"notes-program-design-1"}))}
    research = {**GOOD, "rationale": "Research suggests at least 6 weekly sets per muscle for growth [notes-program-design-1]."}
    assert failed(check_program(ProgramDraft.model_validate(research), profile(), {"notes-program-design-1"})) == []


def test_asking_for_details_it_already_has_gets_one_nudge(monkeypatch):
    script = ["Which equipment would you like me to focus on?", [call("search_sources", query="sets for strength")],
              [call("submit_program", **_submission(profile()))]]
    turn, model = run(monkeypatch, script, profile())
    assert turn.kind == "program" and turn.passed_checks


def test_a_stalled_model_call_falls_back_then_gives_a_clear_error(monkeypatch):
    import time
    from ragmotion.config import settings
    monkeypatch.setattr(settings, "agent_call_deadline_seconds", 0.2)
    calls = []
    def create(**kwargs):
        calls.append(kwargs["model"])
        if kwargs["model"] == "slow/model":
            time.sleep(1)
        return "ok"
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(settings, "agent_fallback_model", "fast/model")
    assert agent._call_model(client, model="slow/model") == "ok" and calls == ["slow/model", "fast/model"]
    monkeypatch.setattr(settings, "agent_fallback_model", "slow/model")
    import pytest
    with pytest.raises(agent.AgentModelTimeout):
        agent._call_model(client, model="slow/model")


def test_a_gym_mentioned_but_dropped_by_the_reader_counts_as_a_full_gym(monkeypatch):
    dropped = profile(equipment=[])
    monkeypatch.setattr(agent, "extract_profile", lambda text: (dropped.model_copy(), None))
    p = agent.read_profile([{"role": "user", "content": "Get stronger, 4 days, full gym, intermediate"}])
    assert p.unmapped_equipment == ["gym"]


def test_exercise_names_are_not_injuries_but_real_complaints_still_are():
    from ragmotion.program import HEALTH_PATTERN
    for name in ["loves back squats and hip thrusts", "likes the shoulder press", "knee raises are easy", "back extensions"]:
        assert not HEALTH_PATTERN.search(name), name
    for complaint in ["sore knee from running", "my hip hurts", "bad shoulder", "lower back pain", "tweaked my back"]:
        assert HEALTH_PATTERN.search(complaint), complaint


def test_fat_loss_programs_must_say_nutrition_isnt_covered():
    fat = profile(goal="lose fat")
    names = {c.name for c in failed(check_program(ProgramDraft.model_validate(GOOD), fat, {"notes-program-design-1"}))}
    assert "fat-loss program says nutrition isn't covered by the sources" in names
    said = {**GOOD, "rationale": GOOD["rationale"] + " Nutrition matters for fat loss but isn't covered by these sources."}
    assert not failed(check_program(ProgramDraft.model_validate(said), fat, {"notes-program-design-1"}))


def test_volume_fix_names_exercises_the_client_can_use():
    light = json.loads(json.dumps(GOOD))
    light["days"][1]["exercises"][2] = x("dumbbell-overhead-press")  # chest only on day 1: 3 sets
    fix = next(c.fix for c in failed(check_program(ProgramDraft.model_validate(light), profile(), {"notes-program-design-1"}))
               if c.name.startswith("at least"))
    assert "chest has 3 weekly sets: add 3 more" in fix and "Push-Up" in fix and "Machine Chest Press" not in fix


def test_missing_core_gets_a_fix_naming_usable_exercises():
    no_core = json.loads(json.dumps(GOOD))
    for d in no_core["days"]:
        d["exercises"] = [e for e in d["exercises"] if e["slug"] != "front-plank"] + [x("dumbbell-reverse-lunge")]
    fix = next(c.fix for c in failed(check_program(ProgramDraft.model_validate(no_core), profile(), {"notes-program-design-1"}))
               if c.name == "core or carry at least once a week")
    assert "Farmer Carry" in fix
