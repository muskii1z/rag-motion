"""Step 15 / F2: evaluate full RAG answers as a LangSmith experiment.

Run from the project folder:
    uv run python evals/run_answer_eval.py                 # semantic retrieval (the default pipeline)
    uv run python evals/run_answer_eval.py --mode hybrid

Each question runs the whole pipeline once. Checks, per answer:
  citations_valid         every citation points to retrieved evidence (the Step 10 checker)
  coverage_correct        the answer's evidence_coverage equals the expected one
  used_expected_evidence  it cited at least one expected exercise or passage
  no_forbidden_citations  it cited no forbidden exercise (e.g. needs a bench the client lacks)
                          and no passage about the wrong population
  exercise_completeness   F7: share of the expected exercises the answer cited (lists: did it name them all?)
  only_keyed_exercises    F7: every exercise the answer cited is expected or acceptable (did extras sneak in?)
                          Rough: the acceptable lists aren't exhaustive, so read the printed extras.
  rule_<name>             F2: the coach's labeling rules (label-level, label-secondary,
                          label-bodyweight, group-by-muscle), graded by an AI judge
                          (src/ragmotion/judge.py), only on questions tagged with answer_rules
Cost: roughly $0.0005 per question for answers, plus ~$0.005 per judged question.
"""

import argparse
import hashlib
from collections import defaultdict

from langsmith import Client, evaluate

from ragmotion.config import settings
from ragmotion.judge import RULES, judge_answer
from ragmotion.evaluation import EVAL_SET, load_eval_set, passage_matches
from ragmotion.rag import answer_question
from ragmotion.retrieval import ChunkHit


def dataset_name() -> str:
    """One dataset per version of eval_set.yaml, so editing the file never overwrites old results."""
    digest = hashlib.sha256(EVAL_SET.read_bytes()).hexdigest()[:8]
    return f"rag-motion-eval-{digest}"


def ensure_dataset(client: Client) -> str:
    name = dataset_name()
    if client.has_dataset(dataset_name=name):
        return name
    ds = client.create_dataset(name, description="rag-motion Step 15 eval set (evals/eval_set.yaml)")
    questions = load_eval_set()
    client.create_examples(
        dataset_id=ds.id,
        inputs=[{"question": q.question} for q in questions],
        outputs=[{
            "id": q.id, "category": q.category, "expected_coverage": q.expected_coverage,
            "expected_exercises": q.expected_exercises, "forbidden_exercises": q.forbidden_exercises, "acceptable_exercises": q.acceptable_exercises,
            "expected_passages": q.expected_passages, "forbidden_passages": q.forbidden_passages,
            "reviewed": q.reviewed, "answer_rules": q.answer_rules,
        } for q in questions],
    )
    return name


def make_target(mode: str, use_filters: bool, k_exercises: int):
    def target(inputs: dict) -> dict:
        r = answer_question(inputs["question"], mode=mode, use_filters=use_filters, k_exercises=k_exercises)
        return {
            "answer": r.answer.answer,
            "general_guidance": r.answer.general_guidance,
            "evidence_coverage": r.answer.evidence_coverage,
            "cited_ids": r.answer.cited_ids,
            "retrieved_exercises": [h.slug for h in r.exercises],
            "citation_problems": r.citation_problems,
            "cited_passages": [p.model_dump() for p in r.passages if p.passage_id in r.cited],
        }
    return target


# ---- Evaluators: plain functions returning a score, checked by code ----

def citations_valid(outputs: dict) -> dict:
    return {"key": "citations_valid", "score": int(not outputs["citation_problems"])}


def coverage_correct(outputs: dict, reference_outputs: dict) -> dict:
    expected = reference_outputs.get("expected_coverage")
    if expected is None:
        return {"key": "coverage_correct", "score": None}
    return {"key": "coverage_correct", "score": int(outputs["evidence_coverage"] == expected)}


def used_expected_evidence(outputs: dict, reference_outputs: dict) -> dict:
    ex, ps = reference_outputs.get("expected_exercises") or [], reference_outputs.get("expected_passages") or []
    if not ex and not ps:
        return {"key": "used_expected_evidence", "score": None}
    cited = set(outputs["cited_ids"])
    passages = [ChunkHit(**p) for p in outputs["cited_passages"]]
    hit = bool(cited & set(ex)) or any(passage_matches(p, m) for p in passages for m in ps)
    return {"key": "used_expected_evidence", "score": int(hit)}


def no_forbidden_citations(outputs: dict, reference_outputs: dict) -> dict:
    fx, fp = reference_outputs.get("forbidden_exercises") or [], reference_outputs.get("forbidden_passages") or []
    if not fx and not fp:
        return {"key": "no_forbidden_citations", "score": None}
    passages = [ChunkHit(**p) for p in outputs["cited_passages"]]
    bad = bool(set(outputs["cited_ids"]) & set(fx)) or any(passage_matches(p, m) for p in passages for m in fp)
    return {"key": "no_forbidden_citations", "score": int(not bad)}


def exercise_completeness(outputs: dict, reference_outputs: dict) -> dict:
    expected = reference_outputs.get("expected_exercises") or []
    if not expected:
        return {"key": "exercise_completeness", "score": None}
    named = set(outputs["cited_ids"]) & set(expected)
    return {"key": "exercise_completeness", "score": len(named) / len(expected),
            "comment": f"named {len(named)} of {len(expected)}"}


def only_keyed_exercises(outputs: dict, reference_outputs: dict) -> dict:
    expected = reference_outputs.get("expected_exercises") or []
    if not expected:
        return {"key": "only_keyed_exercises", "score": None}
    allowed = set(expected) | set(reference_outputs.get("acceptable_exercises") or [])
    extras = sorted(set(outputs["cited_ids"]) & set(outputs.get("retrieved_exercises") or []) - allowed)
    return {"key": "only_keyed_exercises", "score": int(not extras), "comment": ", ".join(extras)}


def coach_rules(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    """AI judge: one call per question, one score per rule the coach attached (None if not tagged)."""
    rules = reference_outputs.get("answer_rules") or []
    scores = {r: (None, "") for r in RULES}
    if rules:
        result, _ = judge_answer(inputs["question"], outputs["answer"], outputs.get("general_guidance"), rules)
        for v in result.verdicts:
            if v.rule in rules:
                scores[v.rule] = (None if v.verdict == "not_applicable" else int(v.verdict == "pass"),
                                  f"{v.verdict}: {v.reason}")
    return {"results": [{"key": f"rule_{r.replace('-', '_')}", "score": sc, "comment": why}
                        for r, (sc, why) in scores.items()]}


EVALUATORS = [citations_valid, coverage_correct, used_expected_evidence, no_forbidden_citations,
              exercise_completeness, only_keyed_exercises, coach_rules]
CHECK_KEYS = ["citations_valid", "coverage_correct", "used_expected_evidence", "no_forbidden_citations",
              "exercise_completeness", "only_keyed_exercises",
              *[f"rule_{r.replace('-', '_')}" for r in RULES]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="semantic", choices=["semantic", "keyword", "hybrid"])
    parser.add_argument("--k-exercises", type=int, default=5, help="exercises retrieved per question (F7 test)")
    parser.add_argument("--no-filters", action="store_true", help="skip the F4 equipment filter (the F2 baseline)")
    args = parser.parse_args()
    use_filters = not args.no_filters

    client = Client()
    name = ensure_dataset(client)
    print(f"Dataset: {name}  |  retrieval: {args.mode}  |  filters: {use_filters}  |  k_exercises: {args.k_exercises}  |  model: {settings.llm_model}")

    results = evaluate(
        make_target(args.mode, use_filters, args.k_exercises),
        data=name,
        evaluators=EVALUATORS,
        experiment_prefix=f"answers-{args.mode}" + ("-filtered" if use_filters else "") + (f"-k{args.k_exercises}" if args.k_exercises != 5 else ""),
        metadata={"retrieval_mode": args.mode, "use_filters": use_filters, "k_exercises": args.k_exercises, "llm_model": settings.llm_model,
                  "embedding_model": settings.embedding_model},
        max_concurrency=4,
    )

    # ---- Local summary ----
    totals, by_cat, costs = defaultdict(list), defaultdict(lambda: defaultdict(list)), []
    failures, verdicts = [], []
    for row in results:
        ref = row["example"].outputs
        for er in row["evaluation_results"]["results"]:
            if er.key.startswith("rule_") and er.comment:
                verdicts.append((ref["id"], er.key, er.comment))
            if er.score is None:
                continue
            totals[er.key].append(er.score)
            by_cat[ref["category"]][er.key].append(er.score)
            if er.score == 0:
                detail = er.comment if er.key == "only_keyed_exercises" else (row["run"].outputs or {}).get("evidence_coverage")
                failures.append((ref["id"], er.key, detail))
    print("\nOverall (share of applicable questions that passed):")
    for key in CHECK_KEYS:
        vals = totals.get(key, [])
        if vals and any(isinstance(v, float) and not v.is_integer() for v in vals):
            print(f"  {key:<24} mean {sum(vals)/len(vals):.2f} over {len(vals)}")
        else:
            print(f"  {key:<24} {int(sum(vals))}/{len(vals)}" + (f"  = {sum(vals)/len(vals):.2f}" if vals else ""))
    print("\nFailures (question, check, coverage claimed / extra exercises):")
    for qid, key, cov in sorted(failures):
        print(f"  {qid:<30} {key:<24} {cov}")
    print("\nAI judge verdicts (coach: do you agree?):")
    for qid, key, comment in sorted(verdicts):
        print(f"  {qid:<30} {key:<22} {comment}")
    print(f"\nExperiment: {results.experiment_name}  (smith.langchain.com -> Datasets & Experiments -> {name})")


if __name__ == "__main__":
    main()
