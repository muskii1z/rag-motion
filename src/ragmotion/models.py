"""Data shapes used across the app, validated with Pydantic.

The allowed values here mirror the CHECK constraints in db/schema.sql.
Pydantic checks data in Python *before* it reaches the database, so a bad
entry in data/exercises.json is reported with its slug and field name.
The database constraints remain the final safety net.
"""

from typing import Literal

from pydantic import BaseModel, Field

MovementPattern = Literal["squat", "hinge", "lunge", "push", "pull", "carry", "core", "jump"]
Equipment = Literal["bodyweight", "dumbbell", "band", "kettlebell", "barbell", "bench", "box"]
Difficulty = Literal["beginner", "intermediate", "advanced"]
Laterality = Literal["bilateral", "unilateral"]
BodyRegion = Literal["lower", "upper", "core", "full"]


class Exercise(BaseModel):
    """One exercise as stored in data/exercises.json and the exercise table."""

    # Lowercase words joined by hyphens, e.g. "goblet-squat".
    slug: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    instructions: str | None = None
    primary_muscles: list[str] = []
    movement_pattern: MovementPattern
    equipment: list[Equipment] = Field(min_length=1)
    difficulty: Difficulty
    laterality: Laterality
    body_region: BodyRegion
    source: str = Field(min_length=1)


class ClientProfile(BaseModel):
    """Structured version of a coach's plain-English client description.

    Filled in by the LLM (Step 6). Fields the coach didn't mention must be null
    or empty, never guessed. Every field is required-but-nullable because strict
    structured output needs the model to address each field explicitly.

    Which fields are missing is computed in Python (missing_fields), not asked
    of the LLM: code can answer that exactly, so the model shouldn't guess it.
    """

    goal: str | None = Field(description="Main training goal as a short plain-English phrase, e.g. 'general strength'. Null if not stated.")
    sessions_per_week: int | None = Field(description="Training sessions per week. Null if not stated.")
    session_duration_minutes: int | None = Field(description="Length of one session in minutes. Null if not stated.")
    equipment: list[Equipment] = Field(
        description="Available equipment mapped to the allowed names only. 'resistance bands' -> 'band', 'dumbbells' -> 'dumbbell'. Empty if not stated."
    )
    unmapped_equipment: list[str] = Field(
        description="Equipment mentioned that does not fit any allowed name, in the coach's words, e.g. 'TRX', 'rower'."
    )
    experience_level: Difficulty | None = Field(description="beginner, intermediate, or advanced. Null unless clearly stated or implied.")
    age: int | None = Field(description="Client age in years. Null if not stated.")
    context_notes: list[str] = Field(
        description="Short facts stated in the text that fit no other field, e.g. 'recreational runner', 'age given as early 30s'. No inferences, advice, or diagnoses."
    )

    def missing_fields(self) -> list[str]:
        """Core fields the coach didn't provide. Deterministic: computed, not generated."""
        core = ["goal", "sessions_per_week", "session_duration_minutes", "equipment", "experience_level", "age"]
        return [name for name in core if getattr(self, name) in (None, [])]


class GroundedAnswer(BaseModel):
    """The LLM's answer to a question, built only from retrieved exercises (Step 10)."""

    answer: str = Field(
        description="Answer for a coach, in plain text. Use only the provided evidence. "
        "Cite each exercise you mention inline as [slug], e.g. [goblet-squat]."
    )
    cited_slugs: list[str] = Field(description="The slug of every exercise cited in the answer.")
    evidence_coverage: Literal["full", "partial", "none"] = Field(
        description="full: the evidence answers the question. partial: it answers only part. "
        "none: the evidence does not answer the question."
    )
    gaps: str | None = Field(
        description="If coverage is partial or none, what the evidence is missing, in one sentence. Otherwise null."
    )
    general_guidance: str | None = Field(
        description="Optional, brief practical guidance from general training knowledge that is NOT in the evidence "
        "(e.g. typical sets, reps, rest, progression). No [slug] citations here. Null if nothing useful to add."
    )
