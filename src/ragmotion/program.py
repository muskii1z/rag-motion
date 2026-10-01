"""Phase 2: the program agent's tools (step 1). The program checker is added in step 2.

The agent (agent.py) decides what to do; these functions are what it can do. The guardrail lives
here, in code: find_exercises() only ever returns exercises the client can use (equipment, level,
age rules), whatever the agent asks for. The client profile comes from extract_profile(), which
reads the conversation separately from the agent.
"""

import json
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
