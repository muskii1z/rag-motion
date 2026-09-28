"""Step 9: ask a question, get the closest exercises from the database.

Run from the project folder:
    uv run python scripts/search.py "single leg exercises for balance"
    uv run python scripts/search.py "explosive lower body" --k 8
"""

import argparse
import time

from ragmotion.retrieval import search_exercises


def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic search over the exercise table.")
    parser.add_argument("question", help="Your question, in quotes")
    parser.add_argument("--k", type=int, default=5, help="How many results to show (default 5)")
    args = parser.parse_args()

    start = time.perf_counter()
    hits = search_exercises(args.question, k=args.k)
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f'QUESTION: "{args.question}"   ({len(hits)} results in {elapsed_ms:.0f} ms)\n')
    print(f"{'#':>2}  {'score':>5}  {'exercise':<30} {'pattern':<8} {'level':<12} equipment")
    for i, h in enumerate(hits, start=1):
        print(f"{i:>2}  {h.similarity:5.3f}  {h.name:<30} {h.movement_pattern:<8} "
              f"{h.difficulty:<12} {', '.join(h.equipment)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # one clear line instead of a traceback
        from ragmotion.errors import friendly_message
        raise SystemExit(f"Error: {friendly_message(e)[1]}")
