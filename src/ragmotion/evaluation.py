"""Evaluation helpers (Step 15): load the eval set, match retrieved items, compute metrics.

Retrieval metrics, per question, on the top-k results:
  - recall@k     fraction of expected items that were retrieved
  - hit@k        1 if at least one expected item was retrieved, else 0
  - MRR          1 / rank of the first expected item (0 if none): rewards putting it near the top
  - forbidden    1 if any forbidden item was retrieved (wrong population / unusable exercise)
"""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ragmotion.ingestion import PROJECT_ROOT
from ragmotion.retrieval import ChunkHit, ExerciseHit

EVAL_SET = PROJECT_ROOT / "evals" / "eval_set.yaml"


@dataclass
class EvalQuestion:
    id: str
    question: str
    category: str
    expected_exercises: list[str] = field(default_factory=list)
    forbidden_exercises: list[str] = field(default_factory=list)
    acceptable_exercises: list[str] = field(default_factory=list)  # fine if labeled; not scored
    expected_passages: list[dict] = field(default_factory=list)
    forbidden_passages: list[dict] = field(default_factory=list)
    expected_coverage: str | None = None
    answer_rules: list[str] = field(default_factory=list)  # coach's labeling rules, graded by the AI judge
    reviewed: bool = False
    notes: str | None = None


def load_eval_set(path: Path = EVAL_SET) -> list[EvalQuestion]:
    data = yaml.safe_load(path.read_text())
    return [EvalQuestion(**q) for q in data["questions"]]


def passage_matches(p: ChunkHit, matcher: dict) -> bool:
    """True if a retrieved passage satisfies an expected/forbidden matcher (see eval_set.yaml)."""
    if p.source_id != matcher["source"]:
        return False
    checks = []
    if "pages" in matcher:
        pages = set(range(p.page_start, p.page_end + 1)) if p.page_start else set()
        checks.append(bool(pages & set(matcher["pages"])))
    if "heading" in matcher:
        checks.append(any(matcher["heading"].lower() in h.lower() for h in p.headings))
    if "chapter" in matcher:
        checks.append(p.chapter.startswith(matcher["chapter"]))
    return any(checks) if checks else True  # source-only matcher


@dataclass
class RetrievalScore:
    exercise_recall: float | None = None
    exercise_hit: float | None = None
    exercise_mrr: float | None = None
    passage_recall: float | None = None
    passage_hit: float | None = None
    passage_mrr: float | None = None
    forbidden: float = 0.0
    missed_exercises: list[str] = field(default_factory=list)
    forbidden_found: list[str] = field(default_factory=list)


def _mrr(flags: list[bool]) -> float:
    return next((1.0 / rank for rank, ok in enumerate(flags, start=1) if ok), 0.0)


def score_retrieval(q: EvalQuestion, exercises: list[ExerciseHit], passages: list[ChunkHit]) -> RetrievalScore:
    s = RetrievalScore()
    slugs = [h.slug for h in exercises]
    if q.expected_exercises:
        found = set(slugs) & set(q.expected_exercises)
        s.exercise_recall = len(found) / len(q.expected_exercises)
        s.exercise_hit = float(bool(found))
        s.exercise_mrr = _mrr([slug in q.expected_exercises for slug in slugs])
        s.missed_exercises = sorted(set(q.expected_exercises) - found)
    if q.expected_passages:
        satisfied = [any(passage_matches(p, m) for p in passages) for m in q.expected_passages]
        s.passage_recall = sum(satisfied) / len(satisfied)
        s.passage_hit = float(any(satisfied))
        s.passage_mrr = _mrr([any(passage_matches(p, m) for m in q.expected_passages) for p in passages])
    bad = [slug for slug in slugs if slug in q.forbidden_exercises]
    bad += [p.passage_id for p in passages if any(passage_matches(p, m) for m in q.forbidden_passages)]
    s.forbidden_found = bad
    s.forbidden = float(bool(bad))
    return s
