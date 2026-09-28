"""Data validation and the source manifest."""

import pytest
from pydantic import ValidationError

from ragmotion.ingestion import load_sources, verify_file
from ragmotion.models import ClientProfile, Exercise


def test_exercise_rejects_equipment_outside_the_allowed_list():
    with pytest.raises(ValidationError):
        Exercise(slug="x", name="X", description="d", movement_pattern="pull", equipment=["trx"],
                 difficulty="beginner", laterality="bilateral", body_region="upper", source="s")


def test_exercise_rejects_a_bad_slug():
    with pytest.raises(ValidationError):
        Exercise(slug="Goblet Squat", name="X", description="d", movement_pattern="squat", equipment=["dumbbell"],
                 difficulty="beginner", laterality="bilateral", body_region="lower", source="s")


def test_missing_fields_are_computed_not_generated():
    p = ClientProfile(goal="strength", sessions_per_week=3, session_duration_minutes=None, equipment=[],
                      unmapped_equipment=[], experience_level=None, age=42, context_notes=[])
    assert p.missing_fields() == ["session_duration_minutes", "equipment", "experience_level"]


def test_manifest_licenses_are_allowed_groups():
    sources = load_sources()
    assert sources, "data/sources.toml should list at least one source"
    assert all(s.license_group in ("A", "B", "C") for s in sources.values()), "group D is never ingested"
    assert all(s.sha256 for s in sources.values() if s.type == "document"), "external documents must be pinned"


def test_verify_file_rejects_a_changed_file(tmp_path):
    source = next(s for s in load_sources().values() if s.sha256)
    fake = tmp_path / "changed.pdf"
    fake.write_bytes(b"not the original file")
    source.local_path = str(fake)  # absolute path wins over PROJECT_ROOT joining
    with pytest.raises(ValueError, match="does not match the manifest"):
        verify_file(source)


def test_equipment_filter_always_allows_bodyweight_and_is_off_when_unlimited():
    from ragmotion.models import QuestionLimits

    bands = QuestionLimits(equipment_limited=True, equipment_owned=["band"], limit_phrase="only have bands")
    assert bands.owned_equipment() == ["band", "bodyweight"]
    nothing = QuestionLimits(equipment_limited=True, equipment_owned=[], limit_phrase="no equipment")
    assert nothing.owned_equipment() == ["bodyweight"]
    gym = QuestionLimits(equipment_limited=False, equipment_owned=[], limit_phrase="full gym")
    assert gym.owned_equipment() is None
