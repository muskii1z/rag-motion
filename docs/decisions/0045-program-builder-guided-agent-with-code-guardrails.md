# 0045. Program builder: a guided agent with guardrails in code
**Date:** 2026-10-01 · **Step:** Phase 2, step 1 · **Status:** accepted

## Context
The RAG app does one search and one answer. Asked for a program, it returned 5 exercises with no hinge, listed strength, hypertrophy, and endurance schemes instead of choosing one, and gave no week layout. A program needs several searches (one per movement pattern, plus dosage), a conversation to collect missing details (goal, days per week, equipment, experience), and a final structured result. The developer wanted the system to talk with the client the way a coach would ("I want a beginner program, it asks what are their goals...").

## Options considered
- **Workflow (code decides every step).** A fixed sequence: read profile, ask for missing fields, search each pattern, search dosage, assemble. Pros: predictable, easy to test, cheap. Cons: rigid; every branch (what to ask, which patterns, how many searches) has to be written by hand.
- **Fully autonomous agent.** The model gets a goal and broad tools and decides everything. Pros: flexible. Cons: less predictable, harder to test, slower and costlier per decision, and it can "decide" a check passed when it didn't. The developer ruled this out: "not a fully autonomous agent, it's going to be prompted and then use the sources it has and come up with the exercise plans."
- **Guided agent with guardrails.** The model chooses tool calls and when to ask the client, but the prompt sets the order of work, the tools filter in code, and checks run in code. Pros: conversational and flexible where it helps; the rules that must not break stay deterministic. Cons: still less predictable than a workflow; needs loop limits ([0047](0047-agent-loop-guardrails-repeat-refusal-nudge-forced-submit.md)).

## Decision
A guided agent (`src/ragmotion/agent.py`) with four tools (`find_exercises`, `search_sources`, `ask_user`, `submit_program`), a prompt with a fixed order of work, and guardrails in code. Built in 4 steps: agent loop, checker, page, test set. This was the developer's direction after Claude had started building before being asked.

## Tradeoffs
- Runs vary: run 1 looped and never submitted; run 2 finished. A workflow wouldn't loop.
- Testing is harder: the tools have unit tests, but the agent's choices can only be judged by running it (planned: a test set of about 10 fictional clients in step 4).
- Prompt rules are followed loosely (7 exercises a day against a 4–6 rule), so a code checker (step 2) is required.
- A plain Python loop, no agent framework (LangGraph or similar), per the project rule not to add frameworks before a step needs them.

## Revisit when
- The step 4 test set shows the agent's choices vary too much to trust: move more steps into fixed code (closer to a workflow).
- The loop gains branches (checker feedback, coach approval) that are hard to follow in plain Python: consider a graph framework such as LangGraph.

## Update 2026-10-02 (Phase 2 structure fix): the first "revisit when" signal happened
The P4 eval showed the agent's week designs varied too much to trust: about 1 in 4 programs failed a structural rule after 3 tries. As this record planned, more steps moved into fixed code: code now lays out the week's days and slots, and the agent fills them ([0073](0073-code-builds-the-program-skeleton-agent-fills-slots.md)). The agent still chooses which tools to call, asks for missing details, searches sources, and picks exercises and dosage, so it is still a guided agent, now closer to a workflow.
