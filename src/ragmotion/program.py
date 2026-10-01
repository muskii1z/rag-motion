"""Phase 2: the program agent's tools (step 1). The program checker is added in step 2.

The agent (agent.py) decides what to do; these functions are what it can do. The guardrail lives
here, in code: find_exercises() only ever returns exercises the client can use (equipment, level,
age rules), whatever the agent asks for. The client profile comes from extract_profile(), which
reads the conversation separately from the agent.
"""

import json
import re
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field

from ragmotion.ingestion import PROJECT_ROOT
from ragmotion.models import ClientProfile, MovementPattern
from ragmotion.retrieval import search_all

LEVELS = ["beginner", "intermediate", "advanced"]
REQUIRED_PROFILE = ["goal", "sessions_per_week", "equipment", "experience_level"]


# ---- What the agent submits ----

class ProgramExercise(BaseModel):
    slug: str = Field(description="Exercise id exactly as returned by find_exercises, e.g. 'goblet-squat'.")
    sets: str = Field(description="e.g. '3'")
    reps: str = Field(description="e.g. '8-12' or '30 s'")
    rest: str = Field(description="e.g. '90 s'")
    note: str | None = Field(default=None, description="Optional coaching note, e.g. a progression or a label like 'intermediate'.")


class ProgramDay(BaseModel):
    name: str = Field(description="e.g. 'Day 1: Full body A'")
    exercises: list[ProgramExercise]


class ProgramDraft(BaseModel):
    title: str
    days: list[ProgramDay] = Field(description="One entry per training day in the week.")
    progression: str = Field(description="How to progress week to week, with citations like [notes-program-design-1].")
    rationale: str = Field(description="Why these sets, reps, rest and frequency, citing passages from search_sources inline by id in square brackets.")
    cited_ids: list[str] = Field(description="Every passage id cited in progression and rationale.")
    safety_notes: str | None = Field(default=None, description="Injuries or conditions mentioned by the client and a reminder to check with a health professional; null if none.")


# ---- Client limits (derived from the profile, never from the agent) ----

@lru_cache(maxsize=1)
def catalog() -> dict[str, dict]:
    return {e["slug"]: e for e in json.loads((PROJECT_ROOT / "data" / "exercises.json").read_text())}


def owned_equipment(profile: ClientProfile) -> set[str]:
    owned = set(profile.equipment) | {"bodyweight"}
    if any("gym" in u.lower() for u in profile.unmapped_equipment):  # "full gym" -> everything
        owned |= {e for ex in catalog().values() for e in ex["equipment"]}
    return owned


def max_level(profile: ClientProfile) -> str:
    level = profile.experience_level or "beginner"
    if profile.age is not None and profile.age >= 65:  # coach: no jumps, no advanced work for older adults
        level = "beginner" if level == "beginner" else "intermediate"
    return level


def population(profile: ClientProfile) -> str | None:
    if profile.age is None:  # a program client with no stated age is treated as an adult (no youth/older-adult sources)
        return "adults"
    return "older-adults" if profile.age >= 65 else "youth" if profile.age < 18 else "adults"


def banned_patterns(profile: ClientProfile, goal_is_power: bool = False) -> set[str]:
    banned = set() if goal_is_power else {"sprint"}
    if profile.age is not None and profile.age >= 65:
        banned |= {"jump", "sprint"}
    return banned


def usable(ex: dict, profile: ClientProfile) -> bool:
    return (set(ex["equipment"]) <= owned_equipment(profile)
            and LEVELS.index(ex["difficulty"]) <= LEVELS.index(max_level(profile))
            and ex["movement_pattern"] not in banned_patterns(profile))


def missing_for_program(profile: ClientProfile) -> list[str]:
    return [f for f in REQUIRED_PROFILE if getattr(profile, f) in (None, [])]


# ---- Tools ----

def find_exercises(pattern: MovementPattern, profile: ClientProfile) -> list[dict]:
    """Catalog exercises for one movement pattern, already filtered to what this client can use."""
    return [
        {"slug": s, "name": e["name"], "level": e["difficulty"], "equipment": e["equipment"],
         "primary_muscles": e["primary_muscles"], "region": e["body_region"]}
        for s, e in catalog().items() if e["movement_pattern"] == pattern and usable(e, profile)
    ]


def search_sources(query: str, profile: ClientProfile, k: int = 5) -> list[dict]:
    """RAG search over the guidelines, research and notes, filtered to the client's age group."""
    _, passages = search_all(query, k_exercises=1, k_passages=k, population=population(profile))
    return [{"id": p.passage_id, "source": p.source_title, "where": p.chapter, "text": p.text[:1200]} for p in passages]


# ---- Step 2: the program checker (the guardrail on the agent's output) ----

MAIN_PATTERNS = {"squat or lunge": {"squat", "lunge"}, "hinge": {"hinge"}, "push": {"push"}, "pull": {"pull"}}
CORE_PATTERNS = {"core", "carry"}
TIMED = {"front-plank", "farmer-carry"}  # prescribed in seconds or metres, not reps
# Backup for the AI-read health_issues field: broad on purpose. For a safety reminder a false alarm
# (an extra "check with a professional" line) costs little; a miss skips a warning someone needed.
# Phrases where "back" means returning ("coming back to lifting") are excluded.
HEALTH_PATTERN = re.compile(
    r"\b(pain\w*|hurt\w*|ache\w*|injur\w*|sore\w*|strain\w*|sprain\w*|tweak\w*|pull(ed)? (a|my) \w+|tear|torn|"
    r"disc|hernia\w*|surgery|operation|condition|arthritis|diabet\w*|asthma|blood pressure|hypertension|heart|"
    r"pregnan\w*|rehab\w*|physio\w*|osteo\w*|knee|shoulder|hip|ankle|wrist|neck|elbow|hamstring|"
    r"(?<!coming )(?<!getting )(?<!get )(?<!come )back(?! to\b| into\b| in\b))\b",
    re.IGNORECASE)


class Check(BaseModel):
    name: str
    passed: bool
    detail: str = ""
    fix: str = ""  # an exact instruction for the agent when the check fails


def check_program(draft: ProgramDraft, profile: ClientProfile, retrieved_ids: set[str]) -> list[Check]:
    """Every rule a program must pass, checked in code against the profile read from the client's words."""
    from ragmotion.rag import find_citations  # local import: rag imports retrieval, which this module also uses

    cat, checks = catalog(), []
    used = [x for d in draft.days for x in d.exercises]
    known = [(x, cat[x.slug]) for x in used if x.slug in cat]
    add = lambda name, bad, detail="": checks.append(Check(name=name, passed=not bad, detail=detail or ", ".join(sorted(set(bad)))))

    want = min(profile.sessions_per_week or len(draft.days), 6)
    checks.append(Check(name="days match what the client asked for", passed=len(draft.days) == want,
                        detail=f"{len(draft.days)} days in the program, client asked for {profile.sessions_per_week}"))
    add("every exercise is in the catalog", [x.slug for x in used if x.slug not in cat])
    add("only equipment the client has", [x.slug for x, e in known if not set(e["equipment"]) <= owned_equipment(profile)])
    add(f"nothing above {max_level(profile)} level",
        [x.slug for x, e in known if LEVELS.index(e["difficulty"]) > LEVELS.index(max_level(profile))])
    add("no movements excluded for this client (e.g. jumps for older adults)",
        [x.slug for x, e in known if e["movement_pattern"] in banned_patterns(profile)])

    need = min(2, len(draft.days))
    def days_with(patterns):
        return sum(any(x.slug in cat and cat[x.slug]["movement_pattern"] in patterns for x in d.exercises) for d in draft.days)
    for label, patterns in MAIN_PATTERNS.items():
        n = days_with(patterns)
        checks.append(Check(name=f"{label} on {need}+ days", passed=n >= need, detail=f"on {n} days"))
    n = days_with(CORE_PATTERNS)
    checks.append(Check(name="core or carry at least once a week", passed=n >= 1, detail=f"on {n} days"))

    lo, hi = (4, 6) if max_level(profile) == "beginner" else (3, 8)
    sizes = {d.name: len(d.exercises) for d in draft.days}
    checks.append(Check(name=f"{lo} to {hi} exercises per day", passed=all(lo <= n <= hi for n in sizes.values()),
                        detail=", ".join(f"{k}: {v}" for k, v in sizes.items()),
                        fix="; ".join(f"'{k}' has {n} exercises: remove {n - hi}" if n > hi else f"'{k}' has {n} exercises: add {lo - n}"
                                      for k, n in sizes.items() if not lo <= n <= hi)))
    add("no exercise repeated within a day", [d.name for d in draft.days if len({x.slug for x in d.exercises}) != len(d.exercises)])
    add("every exercise has sets, reps and rest", [x.slug for x in used if not (x.sets.strip() and x.reps.strip() and x.rest.strip())])
    untimed = sorted({x.slug for x in used if x.slug in TIMED and not any(u in x.reps.lower() for u in ("s", "sec", "m"))})
    checks.append(Check(name="planks and carries in seconds or metres, not reps", passed=not untimed, detail=", ".join(untimed),
                        fix="; ".join(f"{slug}: change reps to a time such as '20-30 s' on every day it appears" for slug in untimed)))

    cited = find_citations(draft.rationale) | find_citations(draft.progression) | set(draft.cited_ids)
    invented = sorted(cited - retrieved_ids)
    checks.append(Check(name="citations come from the agent's own searches", passed=bool(cited) and not invented,
                        detail=", ".join(invented) if invented else ("" if cited else "no citations")))
    health = list(profile.health_issues) + [n for n in profile.context_notes if HEALTH_PATTERN.search(n)]
    if health:
        ok = "professional" in (draft.safety_notes or "").lower()
        checks.append(Check(name="client's conditions acknowledged, with a reminder to see a health professional",
                            passed=ok, detail="; ".join(health),
                            fix="Add safety_notes that mention the condition and say to check with a health professional."))
    return checks


def failed(checks: list[Check]) -> list[Check]:
    return [c for c in checks if not c.passed]
