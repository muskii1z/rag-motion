"""Phase 2, step 2: the program checker, and the agent-loop guardrails driven by a scripted fake model."""

import json
from types import SimpleNamespace

from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall, Function

from ragmotion import agent
from ragmotion.models import ClientProfile
from ragmotion.program import ProgramDraft, check_program, failed


def profile(**kw) -> ClientProfile:
    base = dict(goal="build muscle", sessions_per_week=2, session_duration_minutes=None, equipment=["dumbbell", "bench"],
                unmapped_equipment=[], experience_level="beginner", age=None, context_notes=[])
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
        step = self.script.pop(0)
        msg = SimpleNamespace(content=step if isinstance(step, str) else "", tool_calls=None if isinstance(step, str) else step)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)], usage=None)


def run(monkeypatch, script, prof):
    model = ScriptedModel(script)
    monkeypatch.setattr(agent, "get_client", lambda: model)
    monkeypatch.setattr(agent, "read_profile", lambda conversation: prof)
    monkeypatch.setattr(agent, "search_sources", lambda q, p: [{"id": "notes-program-design-1", "text": "..."}])
    return agent.run_turn([{"role": "user", "content": "beginner program please"}]), model


def test_building_is_refused_until_the_details_are_known(monkeypatch):
    turn, model = run(monkeypatch, [[call("find_exercises", pattern="squat")], "What equipment do you have?"],
                      profile(equipment=[]))
    assert turn.steps[0]["result"] == "refused: ask about equipment"
    assert turn.kind == "message" and "equipment" in turn.text


def test_an_empty_reply_gets_one_nudge_then_a_clear_error(monkeypatch):
    turn, _ = run(monkeypatch, ["", ""], profile())
    assert turn.kind == "error" and turn.text == "The program builder didn't respond. Please try again."


def test_the_checker_sends_a_bad_program_back_and_accepts_the_fix(monkeypatch):
    too_big = json.loads(json.dumps(GOOD))
    too_big["days"][0]["exercises"] += [x("dumbbell-reverse-lunge"), x("dumbbell-hip-thrust")]
    script = [[call("search_sources", query="sets and reps for muscle")],
              [call("submit_program", **too_big)], [call("submit_program", **GOOD)]]
    turn, _ = run(monkeypatch, script, profile())
    assert turn.steps[1]["result"].startswith("rejected: 4 to 6 exercises per day")
    assert turn.kind == "program" and turn.passed_checks


def test_non_health_notes_dont_demand_a_referral():
    checks = check_program(ProgramDraft.model_validate(GOOD), profile(context_notes=["little lifting experience"]), {"notes-program-design-1"})
    assert failed(checks) == []
