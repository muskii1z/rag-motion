"""Step 10: ask a question, get a grounded answer with citations.

Prints every stage (manual tracing until LangSmith arrives in Step 11):
what was retrieved, the answer, the sources, the checks, time, and cost.

Run from the project folder:
    uv run python scripts/ask.py "what exercises can I do for biceps"
"""

import argparse

from ragmotion.rag import answer_question


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the exercise database a question (RAG).")
    parser.add_argument("question", help="Your question, in quotes")
    parser.add_argument("--k", type=int, default=5, help="How many exercises to retrieve (default 5)")
    args = parser.parse_args()

    r = answer_question(args.question, k=args.k)
    cited = set(r.answer.cited_slugs)

    print(f'QUESTION: "{r.question}"\n')
    print("1. RETRIEVED (sent to the LLM as evidence):")
    for i, h in enumerate(r.hits, start=1):
        mark = "cited" if h.slug in cited else "not used"
        print(f"   {i}. {h.similarity:.3f}  {h.name:<30} [{mark}]")

    print(f"\n2. ANSWER (evidence coverage: {r.answer.evidence_coverage}):\n")
    print("   " + r.answer.answer.replace("\n", "\n   "))
    if r.answer.gaps:
        print(f"\n   Gaps: {r.answer.gaps}")
    if r.answer.general_guidance:
        print(f"\n   GENERAL GUIDANCE (from the model's general knowledge, NOT from your sources):\n"
              f"   {r.answer.general_guidance}")

    print("\n3. SOURCES:")
    for h in r.cited_hits:
        print(f"   [{h.slug}] {h.name}: {h.difficulty}, {', '.join(h.equipment)}. Source: {h.source}")
    if not r.cited_hits:
        print("   (none cited)")

    print("\n4. CITATION CHECKS (done in Python, not by the LLM):")
    print("   all citations valid" if not r.citation_problems else "\n".join(f"   PROBLEM: {p}" for p in r.citation_problems))

    t, u = r.timings_ms, r.usage
    cost = f"${u.cost_usd:.6f}" if u.cost_usd is not None else "not reported"
    print(f"\n5. COST AND TIME: retrieval {t['retrieval']:.0f} ms, generation {t['generation']:.0f} ms | "
          f"{u.model}: {u.prompt_tokens} in / {u.completion_tokens} out tokens, {cost}")


if __name__ == "__main__":
    main()
