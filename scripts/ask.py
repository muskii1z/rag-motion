"""Ask a question, get a grounded answer citing exercises and document passages (Steps 10 and 13).

Prints every stage (manual tracing until LangSmith in Step 14): what was retrieved, the answer,
the sources, the checks, time, and cost.

Run from the project folder:
    uv run python scripts/ask.py "how much strength training should a beginner do, and which exercises?"
"""

import argparse
import os

from ragmotion.rag import answer_question


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the knowledge base a question (RAG).")
    parser.add_argument("question", help="Your question, in quotes")
    parser.add_argument("--k", type=int, default=5, help="How many exercises and passages to retrieve (default 5 each)")
    args = parser.parse_args()

    r = answer_question(args.question, k_exercises=args.k, k_passages=args.k)
    mark = lambda cid: "cited" if cid in r.cited else "not used"  # noqa: E731

    print(f'QUESTION: "{r.question}"\n')
    print("1. RETRIEVED (sent to the LLM as evidence):")
    print("   Exercises:")
    for h in r.exercises:
        print(f"     {h.similarity:.3f}  {h.name:<30} [{mark(h.slug)}]")
    print("   Passages:")
    for p in r.passages:
        where = f"p.{p.page_start}" if p.page_start else "notes"
        print(f"     {p.similarity:.3f}  {p.passage_id:<28} {where:<6} {(p.headings or [p.chapter])[0][:45]:<45} [{mark(p.passage_id)}]")

    print(f"\n2. ANSWER (evidence coverage: {r.answer.evidence_coverage}):\n")
    print("   " + r.answer.answer.replace("\n", "\n   "))
    if r.answer.gaps:
        print(f"\n   Gaps: {r.answer.gaps}")
    if r.answer.general_guidance:
        print(f"\n   GENERAL GUIDANCE (from the model's general knowledge, NOT from your sources):\n"
              f"   {r.answer.general_guidance}")

    print("\n3. SOURCES:")
    for p in r.passages:
        if p.passage_id in r.cited:
            where = f"{p.chapter}, pages {p.page_start}-{p.page_end}" if p.page_start else ", ".join(p.headings)
            print(f"   [{p.passage_id}] {p.source_title}: {where}")
    for h in r.exercises:
        if h.slug in r.cited:
            print(f"   [{h.slug}] {h.name} (exercise catalog). Source: {h.source}")

    print("\n4. CITATION CHECKS (done in Python, not by the LLM):")
    print("   all citations valid" if not r.citation_problems else "\n".join(f"   PROBLEM: {p}" for p in r.citation_problems))

    t, u = r.timings_ms, r.usage
    cost = f"${u.cost_usd:.6f}" if u.cost_usd is not None else "not reported"
    print(f"\n5. COST AND TIME: retrieval {t['retrieval']:.0f} ms, generation {t['generation']:.0f} ms | "
          f"{u.model}: {u.prompt_tokens} in / {u.completion_tokens} out tokens, {cost}")
    if os.environ.get("LANGSMITH_TRACING", "").lower() == "true":
        project = os.environ.get("LANGSMITH_PROJECT", "default")
        print(f"\n6. TRACE: recorded in LangSmith project '{project}' (smith.langchain.com -> Tracing Projects)")


if __name__ == "__main__":
    main()
