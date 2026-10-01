"""Phase 2, step 1: talk to the program agent in the terminal.

Run from the project folder:
    uv run python scripts/program_chat.py
Type your answers; an empty line quits. Each turn shows the tools the agent called.
"""

from ragmotion.agent import run_turn


def show(turn) -> None:
    for s in turn.steps:
        print(f"   [tool] {s['tool']}({', '.join(f'{k}={v}' for k, v in s['args'].items())}) -> {s['result'][:110]}")
    if turn.kind == "program":
        p = turn.program
        print(f"\n== {p['title']} ==")
        for day in p["days"]:
            print(f"\n{day['name']}")
            for x in day["exercises"]:
                print(f"  - {x['name']:<30} {x['sets']} x {x['reps']:<8} rest {x['rest']:<8} ({x['level']}, {', '.join(x['equipment'])})"
                      + (f"  {x['note']}" if x.get("note") else ""))
        print(f"\nProgression: {p['progression']}\nWhy: {p['rationale']}")
        if p.get("safety_notes"):
            print(f"Safety: {p['safety_notes']}")
        bad = [c for c in turn.checks if not c["passed"]]
        print(f"\nProgram checks: {len(turn.checks) - len(bad)}/{len(turn.checks)} passed")
        for c in bad:
            print(f"  FAILED: {c['name']} ({c['detail']})")
    else:
        print(f"\nAgent: {turn.text}")
    print(f"   (cost ${turn.cost_usd:.4f})\n")


def main() -> None:
    conversation = []
    while True:
        text = input("You: ").strip()
        if not text:
            return
        conversation.append({"role": "user", "content": text})
        turn = run_turn(conversation)
        show(turn)
        conversation.append({"role": "assistant", "content": turn.text})


if __name__ == "__main__":
    main()
