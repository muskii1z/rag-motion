"""The citation checker: the code that catches invented or inconsistent citations (Steps 10 and 13)."""

from ragmotion.models import GroundedAnswer
from ragmotion.rag import check_citations, find_citations


def answer(text: str, cited: list[str], general: str | None = None) -> GroundedAnswer:
    return GroundedAnswer(answer=text, cited_ids=cited, evidence_coverage="full", gaps=None, general_guidance=general)


def test_find_citations_reads_single_and_grouped_ids():
    text = "Squat [goblet-squat]. Two days a week [pag2-57, pag2-63]. Not a citation: [Figure 2]."
    assert find_citations(text) == {"goblet-squat", "pag2-57", "pag2-63"}


def test_clean_answer_has_no_problems():
    a = answer("Do goblet squats [goblet-squat] twice a week [pag2-57].", ["goblet-squat", "pag2-57"])
    assert check_citations(a, {"goblet-squat", "pag2-57", "push-up"}) == []


def test_invented_citation_is_flagged():
    # The real Step 13 failure: the model glued the tag name onto the id.
    a = answer("Try push-ups [exercise-push-up].", ["exercise-push-up"])
    problems = check_citations(a, {"push-up"})
    assert any("exercise-push-up" in p and "not in the retrieved evidence" in p for p in problems)


def test_typo_citation_is_flagged():
    # The real eval failure: "haugen219" instead of "haugen2019".
    a = answer("Sprint with full recovery [haugen219-sprint-17].", ["haugen219-sprint-17"])
    assert check_citations(a, {"haugen2019-sprint-17"})


def test_listed_but_not_cited_in_text_is_flagged():
    a = answer("Do goblet squats [goblet-squat].", ["goblet-squat", "push-up"])
    problems = check_citations(a, {"goblet-squat", "push-up"})
    assert any("'push-up' is in cited_ids but never cited in the text" in p for p in problems)


def test_general_guidance_must_not_cite_sources():
    a = answer("Do goblet squats [goblet-squat].", ["goblet-squat"], general="Rest 2 minutes [goblet-squat].")
    problems = check_citations(a, {"goblet-squat"})
    assert any("general guidance" in p for p in problems)
