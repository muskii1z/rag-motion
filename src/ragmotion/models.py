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
