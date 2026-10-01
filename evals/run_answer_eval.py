"""Step 15 / F2: evaluate full RAG answers on the eval set.

Run from the project folder:
    uv run python evals/run_answer_eval.py                 # local run: results saved to evals/results/
    uv run python evals/run_answer_eval.py --langsmith     # also record it as a LangSmith experiment
    uv run python evals/run_answer_eval.py --mode hybrid

By default the eval runs locally with tracing off and saves every answer and score to
evals/results/answers-<timestamp>.json, so it keeps working when LangSmith is unreachable or out of
its monthly trace allowance (hit on 2026-09-30). --langsmith runs the same checks through
LangSmith's evaluate() so the run is also browsable there.

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
import inspect
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from langsmith import Client, evaluate, tracing_context

from ragmotion.config import settings
from ragmotion.evaluation import EVAL_SET, EvalQuestion, load_eval_set, passage_matches
from ragmotion.ingestion import PROJECT_ROOT
from ragmotion.judge import JUDGE_MODEL, RULES, judge_answer
from ragmotion.rag import answer_question
from ragmotion.retrieval import ChunkHit


def dataset_name() -> str:
    """One dataset per version of eval_set.yaml, so editing the file never overwrites old results."""
    digest = hashlib.sha256(EVAL_SET.read_bytes()).hexdigest()[:8]
    return f"rag-motion-eval-{digest}"


def reference(q: EvalQuestion) -> dict:
    """The answer key for one question, in the shape the evaluators read (same for local and LangSmith)."""
    return {
        "id": q.id, "category": q.category, "expected_coverage": q.expected_coverage,
        "expected_exercises": q.expected_exercises, "forbidden_exercises": q.forbidden_exercises,
        "acceptable_exercises": q.acceptable_exercises,
        "expected_passages": q.expected_passages, "forbidden_passages": q.forbidden_passages,
        "reviewed": q.reviewed, "answer_rules": q.answer_rules,
    }


def ensure_dataset(client: Client) -> str:
    name = dataset_name()
    if client.has_dataset(dataset_name=name):
        return name
    ds = client.create_dataset(name, description="rag-motion Step 15 eval set (evals/eval_set.yaml)")
    questions = load_eval_set()
    client.create_examples(
        dataset_id=ds.id,
        inputs=[{"question": q.question} for q in questions],
        outputs=[reference(q) for q in questions],
    )
    return name


def make_target(mode: str, use_filters: bool, k_exercises: int, rewrite: str = "none"):
    def target(inputs: dict) -> dict:
        r = answer_question(inputs["question"], mode=mode, use_filters=use_filters, k_exercises=k_exercises, rewrite=rewrite)
        return {
            "answer": r.answer.answer,
            "general_guidance": r.answer.general_guidance,
            "evidence_coverage": r.answer.evidence_coverage,
            "cited_ids": r.answer.cited_ids,
            "retrieved_exercises": [h.slug for h in r.exercises],
            "search_query": r.search_query,
            "timings_ms": r.timings_ms,
            "cost_usd": sum(u.cost_usd or 0 for u in (r.usage, r.limits_usage) if u),
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


def run_evaluator(evaluator, inputs: dict, outputs: dict, ref: dict) -> list[dict]:
    """Call one evaluator the way LangSmith would (by parameter name) and return its results as a list."""
    available = {"inputs": inputs, "outputs": outputs, "reference_outputs": ref}
    kwargs = {name: available[name] for name in inspect.signature(evaluator).parameters}
    try:
        result = evaluator(**kwargs)
    except Exception as e:  # one broken check shouldn't sink the run; it's reported instead
        return [{"key": evaluator.__name__, "score": None, "comment": f"evaluator error: {type(e).__name__}: {e}",
                 "error": True}]
    return result["results"] if "results" in result else [result]


def run_locally(questions: list[EvalQuestion], target) -> list[dict]:
    """Run the pipeline and every check on each question, without LangSmith. Returns one row per question."""
    def one(q: EvalQuestion) -> dict:
        inputs, ref = {"question": q.question}, reference(q)
        try:
            outputs = target(inputs)
        except Exception as e:
            return {"id": q.id, "category": q.category, "question": q.question, "outputs": None,
                    "error": f"{type(e).__name__}: {e}", "results": []}
        results = [r for ev in EVALUATORS for r in run_evaluator(ev, inputs, outputs, ref)]
        return {"id": q.id, "category": q.category, "question": q.question, "outputs": outputs,
                "error": None, "results": results}

    with tracing_context(enabled=False), ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(one, questions))


def rows_from_langsmith(results) -> list[dict]:
    """LangSmith's result objects, turned into the same rows as a local run."""
    rows = []
    for row in results:
        ref = row["example"].outputs
        rows.append({
            "id": ref["id"], "category": ref["category"], "question": row["example"].inputs["question"],
            "outputs": row["run"].outputs, "error": row["run"].error,
            "results": [{"key": er.key, "score": er.score, "comment": er.comment}
                        for er in row["evaluation_results"]["results"]],
        })
    return rows


def print_summary(rows: list[dict]) -> None:
    totals, failures, verdicts = defaultdict(list), [], []
    for row in rows:
        for r in row["results"]:
            if r["key"].startswith("rule_") and r.get("comment"):
                verdicts.append((row["id"], r["key"], r["comment"]))
            if r["score"] is None:
                continue
            totals[r["key"]].append(r["score"])
            if r["score"] == 0:
                detail = r.get("comment") if r["key"] == "only_keyed_exercises" else (row["outputs"] or {}).get("evidence_coverage")
                failures.append((row["id"], r["key"], detail))
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
    errors = [(row["id"], row["error"]) for row in rows if row["error"]]
    errors += [(row["id"], r["comment"]) for row in rows for r in row["results"] if r.get("error")]
    if errors:
        print(f"\nERRORS ({len(errors)}): these questions or checks didn't run, so the totals above leave them out")
        for qid, err in errors:
            print(f"  {qid:<30} {err}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="semantic", choices=["semantic", "keyword", "hybrid", "split"])
    parser.add_argument("--k-exercises", type=int, default=5, help="exercises retrieved per question (F7 test)")
    parser.add_argument("--no-filters", action="store_true", help="skip the F4/F5 filters (the F2 baseline)")
    parser.add_argument("--weight", type=float, default=1.0, help="hybrid/split: semantic weight vs keyword (F7d)")
    parser.add_argument("--rewrite", default=settings.query_rewrite, choices=["none", "dictionary", "llm"], help="slang rewriting (F7c); default = what the app uses")
    parser.add_argument("--no-judge", action="store_true", help="skip the AI judge (saves ~8c when rules aren't being measured)")
    parser.add_argument("--langsmith", action="store_true", help="also record the run as a LangSmith experiment")
    args = parser.parse_args()
    use_filters = not args.no_filters
    settings.hybrid_semantic_weight = args.weight
    if args.no_judge:
        EVALUATORS.remove(coach_rules)
    run_name = f"answers-{args.mode}" + ("-filtered" if use_filters else "") + (f"-k{args.k_exercises}" if args.k_exercises != 5 else "") + (f"-rw-{args.rewrite}" if args.rewrite != "none" else "") + (f"-w{args.weight:g}" if args.mode in ("hybrid", "split") else "")
    metadata = {"retrieval_mode": args.mode, "use_filters": use_filters, "k_exercises": args.k_exercises,
                "llm_model": settings.llm_model, "embedding_model": settings.embedding_model,
                "judge_model": None if args.no_judge else JUDGE_MODEL, "rewrite": args.rewrite, "hybrid_semantic_weight": args.weight, "eval_set": dataset_name()}
    print(f"Eval set: {dataset_name()}  |  retrieval: {args.mode}  |  filters: {use_filters}  |  "
          f"k_exercises: {args.k_exercises}  |  model: {settings.llm_model}  |  "
          f"{'LangSmith experiment' if args.langsmith else 'local run'}")

    target = make_target(args.mode, use_filters, args.k_exercises, args.rewrite)
    experiment = None
    if args.langsmith:
        results = evaluate(target, data=ensure_dataset(Client()), evaluators=EVALUATORS,
                           experiment_prefix=run_name, metadata=metadata, max_concurrency=4)
        rows, experiment = rows_from_langsmith(results), results.experiment_name
    else:
        rows = run_locally(load_eval_set(), target)

    print_summary(rows)

    out_dir = PROJECT_ROOT / "evals" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{run_name}-{datetime.now():%Y%m%d-%H%M%S-%f}.json"
    out.write_text(json.dumps({"run": run_name, "metadata": metadata, "langsmith_experiment": experiment,
                               "rows": rows}, indent=2, default=str))
    print(f"\nSaved {out.relative_to(PROJECT_ROOT)}" + (f"  |  LangSmith experiment: {experiment}" if experiment else ""))


if __name__ == "__main__":
    main()
