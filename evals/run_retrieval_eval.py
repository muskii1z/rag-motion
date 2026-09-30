"""Step 15: score keyword vs semantic vs hybrid retrieval on the eval set.

F4 adds "semantic+filter": the equipment limits are read from each question by the LLM
(one small call per question, ~$0.001 per run), then semantic search skips unusable exercises.

Run from the project folder:
    uv run python evals/run_retrieval_eval.py            # summary tables
    uv run python evals/run_retrieval_eval.py --details  # plus every question's misses

Saves results to evals/results/retrieval-<timestamp>.json.
"""

import argparse
import json
import statistics
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime

from langsmith import tracing_context

from ragmotion.chunking import chunker_label
from ragmotion.config import settings
from ragmotion.evaluation import load_eval_set, score_retrieval
from ragmotion.ingestion import PROJECT_ROOT
from ragmotion.llm import extract_limits
from ragmotion.retrieval import SEARCH_MODES, search_all
from ragmotion.rewrite import rewrite_query

K = 5
METRICS = ["exercise_recall", "exercise_hit", "exercise_mrr", "passage_recall", "passage_hit", "passage_mrr", "forbidden"]


def mean(values: list) -> float | None:
    vals = [v for v in values if v is not None]
    return statistics.mean(vals) if vals else None


def fmt(v: float | None) -> str:
    return "  -  " if v is None else f"{v:5.2f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", action="store_true")
    parser.add_argument("--k", type=int, default=5, help="results per search (F7 test)")
    parser.add_argument("--weight", type=float, default=1.0, help="hybrid: semantic weight vs keyword (F7d)")
    parser.add_argument("--rewrite", default="none", choices=["none", "dictionary", "llm"], help="slang rewriting for the filtered row (F7c)")
    args = parser.parse_args()
    global K
    K = args.k

    questions = load_eval_set()
    reviewed = sum(q.reviewed for q in questions)
    print(f"{len(questions)} questions ({reviewed} reviewed by the coach) | top-{K} | "
          f"chunker {chunker_label()} | embeddings {settings.embedding_model}\n")

    results = {}
    # No LangSmith traces here: this eval makes no LLM calls, and ~87 search-only traces per run
    # buried the real questions in the Tracing list.
    with tracing_context(enabled=False):
        for mode, search in SEARCH_MODES.items():
            results[mode] = []
            for q in questions:
                exercises, passages = search(q.question, k_exercises=K, k_passages=K)
                score = score_retrieval(q, exercises, passages)
                results[mode].append({"id": q.id, "category": q.category, **asdict(score),
                                      "retrieved_exercises": [h.slug for h in exercises],
                                      "retrieved_passages": [p.passage_id for p in passages]})

        # F4/F5: with the filters from the question's limits (read once per question), for the modes
        # the pipeline can use (F7d adds hybrid with a semantic weight, and split: semantic exercises + hybrid passages).
        settings.hybrid_semantic_weight = args.weight
        limits_by_q = {}
        for q in questions:
            search_q = rewrite_query(q.question, args.rewrite)
            limits = extract_limits(search_q)[0]
            limits_by_q[q.id] = (search_q, limits.owned_equipment(), limits.population)
        for mode in ["semantic", "hybrid", "split"]:
            row = f"{mode}+filter"
            results[row] = []
            for q in questions:
                search_q, owned, population = limits_by_q[q.id]
                exercises, passages = SEARCH_MODES[mode](search_q, k_exercises=K, k_passages=K, owned=owned, population=population)
                score = score_retrieval(q, exercises, passages)
                results[row].append({"id": q.id, "category": q.category, **asdict(score), "owned": owned, "population": population,
                                     "retrieved_exercises": [h.slug for h in exercises],
                                     "retrieved_passages": [p.passage_id for p in passages]})

    # ---- Overall table ----
    print(f"{'mode':<16} " + " ".join(f"{m:>15}" for m in METRICS))
    for mode, rows in results.items():
        print(f"{mode:<16} " + " ".join(f"{fmt(mean([r[m] for r in rows])):>15}" for m in METRICS))
    print("\n(recall/hit/MRR: higher is better. forbidden: share of questions where a forbidden item was retrieved, lower is better.)")

    # ---- By category: the main recall number for each ----
    print(f"\nBy category (exercise recall / passage recall), top-{K}:")
    cats = defaultdict(list)
    for q in questions:
        cats[q.category].append(q.id)
    print(f"{'category':<20}{'n':>3}  " + "  ".join(f"{m:>15}" for m in results))
    for cat, ids in cats.items():
        cells = []
        for mode, rows in results.items():
            rs = [r for r in rows if r["id"] in ids]
            cells.append(f"{fmt(mean([r['exercise_recall'] for r in rs]))} / {fmt(mean([r['passage_recall'] for r in rs]))}")
        print(f"{cat:<20}{len(ids):>3}  " + "  ".join(f"{c:>15}" for c in cells))

    if args.details:
        print("\nPer question (semantic | keyword | hybrid): missed exercises, passage recall, forbidden found")
        for i, q in enumerate(questions):
            parts = []
            for mode in results:
                r = results[mode][i]
                parts.append(f"miss={r['missed_exercises'] or '-'} p={fmt(r['passage_recall']).strip()} forb={r['forbidden_found'] or '-'}")
            print(f"  {q.id:<28} " + " | ".join(parts))

    out_dir = PROJECT_ROOT / "evals" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"retrieval-{datetime.now():%Y%m%d-%H%M%S-%f}.json"
    out.write_text(json.dumps({"k": K, "chunker": chunker_label(), "embedding_model": settings.embedding_model,
                               "questions": len(questions), "reviewed": reviewed, "results": results}, indent=2))
    print(f"\nSaved {out.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
