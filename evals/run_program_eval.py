"""Phase 2, P4: evaluate the program builder on fictional clients (evals/program_clients.yaml).

Run from the project folder:
    uv run python evals/run_program_eval.py            # each client once
    uv run python evals/run_program_eval.py --runs 3   # three runs each, to see run-to-run variation

For every client the runner plays the whole conversation with the agent, then scores the last turn:
the program checker's result (src/ragmotion/program.py) plus the client's own expectations. Saves
evals/results/programs-<timestamp>.json and a readable review sheet programs-review-<timestamp>.md
for the coach. Cost: about 0.5-1 cent per client per run.
"""

import argparse
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime

import yaml
from langsmith import tracing_context

from ragmotion.agent import run_turn
from ragmotion.chunking import ADULT_RESEARCH
from ragmotion.config import settings
from ragmotion.ingestion import PROJECT_ROOT
from ragmotion.rag import find_citations

CLIENTS = PROJECT_ROOT / "evals" / "program_clients.yaml"
REFERRAL_CHECK = "client's conditions acknowledged, with a reminder to see a health professional"


def program_summary(program: dict) -> str:
    """What the page sends back as the assistant's turn, so follow-ups have context."""
    return f'Here is your program, "{program["title"]}":\n' + "\n".join(
        f"{d['name']}: " + "; ".join(f"{x['name']} {x['sets']}x{x['reps']}" for x in d["exercises"]) for d in program["days"])


def reply_text(turn: dict) -> str:
    p = turn.get("program") or {}
    return " ".join(filter(None, [turn.get("text"), p.get("rationale"), p.get("progression"), p.get("safety_notes")])).lower()


def score(turn: dict, expect: dict) -> dict[str, bool]:
    """Each expectation -> passed? Only the expectations a client lists are scored."""
    p, checks = turn.get("program") or {}, turn.get("checks") or []
    exercises = [x for d in p.get("days", []) for x in d["exercises"]]
    cited = set(p.get("cited_ids", [])) | find_citations(p.get("rationale", "")) | find_citations(p.get("progression", ""))
    rules = {
        "kind": lambda want: turn["kind"] == want,
        "passes_checks": lambda want: bool(turn.get("passed_checks")) == want,
        "mentions_any": lambda words: any(w.lower() in reply_text(turn) for w in words),
        "no_adult_research": lambda want: not any(c.rsplit("-", 1)[0] in ADULT_RESEARCH for c in cited),
        "no_bodyweight_only": lambda want: not any(x.get("equipment") == ["bodyweight"] for x in exercises),
        "has_referral": lambda want: "professional" in (p.get("safety_notes") or "").lower(),
        "no_referral": lambda want: not any(c["name"] == REFERRAL_CHECK for c in checks),
        "question_mentions": lambda words: all(re.search(w, turn.get("text", ""), re.IGNORECASE) for w in words),
    }
    return {name: rules[name](value) for name, value in expect.items()}


def run_client(client: dict, run: int) -> dict:
    conversation, t0, turn = [], time.time(), None
    try:
        for message in client["messages"]:
            conversation.append({"role": "user", "content": message})
            turn = asdict(run_turn(conversation))
            conversation.append({"role": "assistant",
                                 "content": program_summary(turn["program"]) if turn["kind"] == "program" else turn["text"]})
        error = None
    except Exception as e:  # recorded, never silently dropped
        error = f"{type(e).__name__}: {e}"
    expectations = score(turn, client.get("expect", {})) if turn and not error else {}
    return {"client": client["id"], "run": run, "seconds": round(time.time() - t0, 1), "error": error,
            "kind": turn and turn["kind"], "text": turn and turn["text"], "passed_checks": turn and turn["passed_checks"],
            "failed_checks": [c for c in (turn or {}).get("checks", []) if not c["passed"]],
            "submissions": sum(s["tool"] == "submit_program" for s in (turn or {}).get("steps", [])),
            "cost_usd": turn and turn["cost_usd"], "expectations": expectations,
            "program": turn and turn["program"], "conversation": conversation}


def review_sheet(rows: list[dict]) -> str:
    """A readable page for the coach: each program with its checks, ready to mark ok / fix."""
    out = [f"# Program review ({datetime.now():%Y-%m-%d}): agent {settings.agent_model}\n",
           "For each program: ok, or what a coach would change.\n"]
    for r in rows:
        out.append(f"\n## {r['client']} (run {r['run']}): {r['kind']}, {'all checks passed' if r['passed_checks'] else 'see failures'}, "
                   f"{r['seconds']} s, ${r['cost_usd'] or 0:.4f}\n")
        out.append("> " + " / ".join(m["content"] for m in r["conversation"] if m["role"] == "user") + "\n")
        if r["error"]:
            out.append(f"\nERROR: {r['error']}\n")
            continue
        missed = [k for k, v in r["expectations"].items() if not v]
        if missed:
            out.append(f"\nMissed expectations: {', '.join(missed)}\n")
        for c in r["failed_checks"]:
            out.append(f"\nFailed check: {c['name']} ({c['detail']})\n")
        p = r["program"]
        if not p:
            out.append(f"\nReply: {r['text']}\n")
            continue
        out.append(f"\n**{p['title']}**\n")
        for d in p["days"]:
            out.append(f"\n*{d['name']}*\n")
            out += [f"- {x['name']}: {x['sets']} x {x['reps']}, rest {x['rest']} ({x.get('level')}, {', '.join(x.get('equipment', []))})"
                    + (f". {x['note']}" if x.get("note") else "") for x in d["exercises"]]
        out.append("\nWeekly sets (code): " + ", ".join(f"{g} {n}" for g, n in p.get("weekly_sets", {}).items()))
        out.append(f"\n\nProgression: {p['progression']}\n\nWhy: {p['rationale']}\n")
        if p.get("safety_notes"):
            out.append(f"\nSafety: {p['safety_notes']}\n")
        out.append("\nCoach verdict: ______\n")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()
    clients = yaml.safe_load(CLIENTS.read_text())["clients"]
    jobs = [(c, r) for r in range(1, args.runs + 1) for c in clients]
    print(f"{len(clients)} clients x {args.runs} run(s) | agent {settings.agent_model} | fallback {settings.agent_fallback_model}\n")

    with tracing_context(enabled=False), ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda job: run_client(*job), jobs))

    print(f"{'client':<28}{'run':>4}  {'kind':<9}{'checks':<8}{'expectations':<14}{'subm':>5}{'secs':>7}{'cost':>9}")
    for r in rows:
        exp = r["expectations"]
        print(f"{r['client']:<28}{r['run']:>4}  {str(r['kind']):<9}{('pass' if r['passed_checks'] else '-' if r['kind'] != 'program' else 'FAIL'):<8}"
              f"{sum(exp.values())}/{len(exp):<12}{r['submissions']:>5}{r['seconds']:>7}{(r['cost_usd'] or 0):>9.4f}"
              + (f"  ERROR {r['error'][:60]}" if r["error"] else "")
              + (f"  missed: {', '.join(k for k, v in exp.items() if not v)}" if exp and not all(exp.values()) else ""))
    programs = [r for r in rows if r["kind"] == "program"]
    met = sum(all(r["expectations"].values()) for r in rows if r["expectations"])
    print(f"\nClients meeting every expectation: {met}/{len(rows)}"
          f" | programs passing every check: {sum(bool(r['passed_checks']) for r in programs)}/{len(programs)}"
          f" | errors: {sum(bool(r['error']) for r in rows)}"
          f" | median time {sorted(r['seconds'] for r in rows)[len(rows) // 2]} s"
          f" | total cost ${sum(r['cost_usd'] or 0 for r in rows):.3f}")

    stamp = f"{datetime.now():%Y%m%d-%H%M%S}"
    out_dir = PROJECT_ROOT / "evals" / "results"
    (out_dir / f"programs-{stamp}.json").write_text(json.dumps({"agent_model": settings.agent_model, "runs": args.runs,
                                                                "rows": rows}, indent=2, default=str))
    (out_dir / f"programs-review-{stamp}.md").write_text(review_sheet(rows))
    print(f"Saved evals/results/programs-{stamp}.json and programs-review-{stamp}.md")


if __name__ == "__main__":
    main()
