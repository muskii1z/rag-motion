"""Step 15: evaluate full RAG answers as a LangSmith experiment, scored by code (no LLM judge).

Run from the project folder:
    uv run python evals/run_answer_eval.py                 # semantic retrieval (the default pipeline)
    uv run python evals/run_answer_eval.py --mode hybrid

Each question runs the whole pipeline once. Checks, per answer:
  citations_valid         every citation points to retrieved evidence (the Step 10 checker)
  coverage_correct        the answer's evidence_coverage equals the expected one
  used_expected_evidence  it cited at least one expected exercise or passage
  no_forbidden_citations  it cited no forbidden exercise (e.g. needs a bench the client lacks)
                          and no passage about the wrong population
Cost: roughly $0.0005 per question with the default model.
"""

import argparse
import hashlib
from collections import defaultdict

from langsmith import Client, evaluate

from ragmotion.config import settings
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
            "expected_exercises": q.expected_exercises, "forbidden_exercises": q.forbidden_exercises,
            "expected_passages": q.expected_passages, "forbidden_passages": q.forbidden_passages,
            "reviewed": q.reviewed,
        } for q in questions],
    )
    return name


def make_target(mode: str):
    def target(inputs: dict) -> dict:
        r = answer_question(inputs["question"], mode=mode)
        return {
            "answer": r.answer.answer,
            "evidence_coverage": r.answer.evidence_coverage,
            "cited_ids": r.answer.cited_ids,
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


EVALUATORS = [citations_valid, coverage_correct, used_expected_evidence, no_forbidden_citations]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="semantic", choices=["semantic", "keyword", "hybrid"])
    args = parser.parse_args()

    client = Client()
    name = ensure_dataset(client)
    print(f"Dataset: {name}  |  retrieval: {args.mode}  |  model: {settings.llm_model}")

    results = evaluate(
        make_target(args.mode),
        data=name,
        evaluators=EVALUATORS,
        experiment_prefix=f"answers-{args.mode}",
        metadata={"retrieval_mode": args.mode, "llm_model": settings.llm_model,
                  "embedding_model": settings.embedding_model},
        max_concurrency=4,
    )

    # ---- Local summary ----
    totals, by_cat, costs = defaultdict(list), defaultdict(lambda: defaultdict(list)), []
    failures = []
    for row in results:
        ref = row["example"].outputs
        for er in row["evaluation_results"]["results"]:
            if er.score is None:
                continue
            totals[er.key].append(er.score)
            by_cat[ref["category"]][er.key].append(er.score)
            if er.score == 0:
                failures.append((ref["id"], er.key, (row["run"].outputs or {}).get("evidence_coverage")))
    print("\nOverall (share of applicable questions that passed):")
    for key in [e.__name__ for e in EVALUATORS]:
        vals = totals.get(key, [])
        print(f"  {key:<24} {sum(vals)}/{len(vals)}" + (f"  = {sum(vals)/len(vals):.2f}" if vals else ""))
    print("\nFailures (question, check, coverage the answer claimed):")
    for qid, key, cov in sorted(failures):
        print(f"  {qid:<30} {key:<24} {cov}")
    print(f"\nExperiment: {results.experiment_name}  (smith.langchain.com -> Datasets & Experiments -> {name})")


if __name__ == "__main__":
    main()
