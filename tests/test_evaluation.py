"""Eval scoring (Step 15): matchers and retrieval metrics must compute exactly what we say they do."""

from conftest import make_exercise, make_passage

from ragmotion.evaluation import EvalQuestion, load_eval_set, passage_matches, score_retrieval


def test_passage_matcher_by_pages_heading_chapter_and_source():
    p = make_passage("pag2", 57, page_start=56, page_end=57, headings=["Key Guidelines for Adults"])
    assert passage_matches(p, {"source": "pag2", "pages": [57]})
    assert not passage_matches(p, {"source": "pag2", "pages": [72]})
    assert passage_matches(p, {"source": "pag2", "heading": "key guidelines"})  # case-insensitive
    assert passage_matches(p, {"source": "pag2", "chapter": "Chapter 4"})
    assert passage_matches(p, {"source": "pag2"})  # source-only matches anything from that source
    assert not passage_matches(p, {"source": "notes-nsca-older-adults"})


def test_scores_match_the_hand_graded_lesson_2_example():
    # Lesson 2: expected 4, retrieved 5 with the 4 expected in positions 1-4.
    q = EvalQuestion(id="t", question="q", category="exercise-selection",
                     expected_exercises=["hip-thrust", "goblet-squat", "rdl", "reverse-lunge"])
    hits = [make_exercise(s) for s in ["hip-thrust", "goblet-squat", "rdl", "reverse-lunge", "step-up"]]
    s = score_retrieval(q, hits, [])
    assert (s.exercise_recall, s.exercise_hit, s.exercise_mrr) == (1.0, 1.0, 1.0)


def test_recall_and_mrr_with_misses():
    q = EvalQuestion(id="t", question="q", category="c", expected_exercises=["a", "b", "c", "d"])
    hits = [make_exercise(s) for s in ["x", "b", "y", "d", "z"]]  # first correct at rank 2
    s = score_retrieval(q, hits, [])
    assert s.exercise_recall == 0.5
    assert s.exercise_mrr == 0.5
    assert s.missed_exercises == ["a", "c"]


def test_forbidden_items_are_caught():
    q = EvalQuestion(id="t", question="q", category="constraint", expected_exercises=["goblet-squat"],
                     forbidden_exercises=["dumbbell-step-up"],
                     forbidden_passages=[{"source": "notes-nsca-older-adults"}])
    s = score_retrieval(q, [make_exercise("goblet-squat"), make_exercise("dumbbell-step-up")],
                        [make_passage("notes-nsca-older-adults", 1)])
    assert s.forbidden == 1.0
    assert set(s.forbidden_found) == {"dumbbell-step-up", "notes-nsca-older-adults-1"}


def test_the_real_eval_set_loads_and_is_fully_reviewed():
    questions = load_eval_set()
    assert len(questions) == 40
    assert len({q.id for q in questions}) == len(questions), "question ids must be unique"
    assert all(q.reviewed for q in questions)
    assert all(q.expected_coverage in ("full", "partial", "none") for q in questions)


def test_answer_key_only_uses_real_exercises_and_never_contradicts_itself():
    import json

    from ragmotion.ingestion import PROJECT_ROOT

    catalog = {e["slug"] for e in json.loads((PROJECT_ROOT / "data" / "exercises.json").read_text())}
    for q in load_eval_set():
        for field_name in ("expected_exercises", "forbidden_exercises", "acceptable_exercises"):
            unknown = set(getattr(q, field_name)) - catalog
            assert not unknown, f"{q.id}.{field_name} names exercises not in the catalog: {unknown}"
        assert not set(q.expected_exercises) & set(q.forbidden_exercises), f"{q.id}: expected and forbidden overlap"
        assert not set(q.acceptable_exercises) & set(q.forbidden_exercises), f"{q.id}: acceptable and forbidden overlap"


def test_answer_rules_name_real_judge_rules():
    from ragmotion.judge import RULES

    for q in load_eval_set():
        assert set(q.answer_rules) <= set(RULES), f"{q.id} has unknown answer_rules: {set(q.answer_rules) - set(RULES)}"
