# 0016. Answer grounding: evidence-only answer plus labeled general guidance
**Date:** 2026-09-25 · **Step:** after 10 · **Status:** accepted

## Context
After Step 10, RAG answers (retrieval-augmented generation: the model answers from data looked up first) came strictly from the database. The prompt forbade exercises that weren't retrieved and, after a Step 10 fix, any programming advice (sets, reps, frequency, rest) that the evidence didn't state. The developer asked whether the system could combine the LLM's general ability with the database exercises to make informed decisions. The catalog holds exercises, not programming principles, and no documents are ingested yet. So a strict answer could never say how many sets or how much rest to use. The master context document's principle is to separate observed facts from AI interpretation. See [the build log entry](../build-log.md#after-step-10-grounding-mode-labeled-general-guidance-and-moving-documents-earlier).

## Options considered
- **Strict (the Step 10 behavior).** Every statement is traceable to a retrieved exercise. But less helpful: no programming advice until documents supply it.
- **Grounded answer + labeled general knowledge.** Cited database facts in the answer, plus a separate, clearly marked "General guidance, not from your sources" section. More useful, and the coach sees what is verified and what isn't. But unverified content does reach the coach, and the label only works if it is kept separate everywhere and actually read.
- **Free blend.** The model mixes its own knowledge into the answer. Most fluent. But nobody can tell which parts are grounded, which defeats the point of RAG.

## Decision
The middle option, chosen by the developer (it was Claude's recommendation). The `answer` field stays evidence-only and cited. The model may add brief, conservative, mainstream training knowledge in a separate `general_guidance` field (text or null), which is never cited and is always shown labeled "not from your sources".

Implementation (commit `6e90764`):
- `GroundedAnswer.general_guidance` in `src/ragmotion/models.py`.
- System prompt in `src/ragmotion/rag.py`: the answer holds only what the evidence supports; general knowledge goes briefly in `general_guidance`; never cite slugs there; never name exercises that aren't in the evidence; null if nothing useful.
- `check_citations()` flags any `[slug]` inside `general_guidance`.
- Shown labeled in `scripts/ask.py` and in a dashed box on the web page.
- New rule in `CLAUDE.md`: "Answers: facts only from retrieved evidence, cited. General LLM knowledge only in the separate, labeled `general_guidance` field, never blended into the answer."

## Tradeoffs
- **Unverified advice reaches the coach.** The first test showed the risk. For "explosive exercises to help me run faster", the guidance said 3-5 sets of 3-6 reps, "Rest periods typically range from 60-120 seconds between sets to allow for full recovery and maximal power output." Power training is usually programmed with longer rest (often 2–5 minutes) precisely for full recovery, so this is doubtful. A browser run gave 60–90 seconds, so the advice also varies between runs. The label makes the doubt visible; it doesn't make the advice right.
- **Code can't check accuracy.** Code only checks that no `[slug]` citation appears in the guidance. An exercise named in plain words there, or wrong advice, is caught only by the prompt and by a human. Accuracy needs an expert-judged eval check (Step 15).
- **The label depends on the reader.** A coach who skims past it could treat general guidance as verified.
- The Step 10 prompt clause that sent missing programming advice to `gaps` is no longer in the prompt, so gaps no longer list missing sets and reps by rule.

## Revisit when
- Documents supplying programming principles are ingested (Steps 11 to 13). Then advice such as "power work: low reps, full rest" should come from cited chunks, and `general_guidance` should shrink or be dropped where sources cover it.
- The Step 15 eval, judged by the domain expert, shows general guidance is often wrong.
- There are signs that readers treat the labeled section as verified.

## Update 2026-09-25 (Step 13): passages now supply programming numbers
Document passages (the Physical Activity Guidelines and the NSCA notes) are now retrieved next to exercises. The prompt in `src/ragmotion/rag.py` now says: give programming numbers only if a passage states them, and cite the passage; use `general_guidance` only when no passage covers the point. In Step 13's tests, dose questions were answered with cited numbers (for example "one set of 8 to 12 repetitions... 2 or 3 sets may be more beneficial" from a Guidelines passage; 70–85% of 1RM for strength from the older-adults notes). So `general_guidance` should be needed less, as the "Revisit when" section expected. The decision stands; the field stays for points no passage covers.

New risk this exposes: cited numbers can be real and still wrong for the person asking. Numbers from an older-adults passage were given as beginner-adult advice ([population mixing](../concepts.md#population-mixing-context-bleed-across-populations)). Citation checks can't catch that. See [Step 13](../build-log.md#step-13-embed-chunks-search-exercises-and-documents-together-answers-cite-both) and the [0019 update](0019-structure-aware-chunking-150-450-labels-no-overlap.md#update-2026-09-25-step-13-population-tags-planned-page-118-skipped).
