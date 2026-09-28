"""Text cleaning and chunking rules (Steps 11-13)."""

import xml.etree.ElementTree as ET

import pytest

from ragmotion import chunking
from ragmotion.chunking import Section, _split_long, _xml_text, embed_text_for, pack
from ragmotion.ingestion import Source, _join_lines


# ---- Joining wrapped PDF lines (Step 11) ----

def test_real_hyphenated_compound_is_kept():
    assert _join_lines(["adults who do moderate-to-", "vigorous activity"]) == "adults who do moderate-to-vigorous activity"


def test_wrapped_lines_join_with_a_space():
    assert _join_lines(["Adults should move more", "and sit less."]) == "Adults should move more and sit less."


def test_bullets_keep_their_own_lines():
    assert _join_lines(["Walking briskly", "• Swimming", "• Tennis"]) == "Walking briskly\n• Swimming\n• Tennis"


# ---- Packing sections into chunks (Step 12) ----

def words(n: int, word: str = "word") -> str:
    return " ".join([word] * n) + "."


@pytest.fixture
def small_limits(monkeypatch):
    monkeypatch.setattr(chunking, "MIN_WORDS", 10)
    monkeypatch.setattr(chunking, "MAX_WORDS", 30)


def test_small_sections_are_merged_until_the_minimum(small_limits):
    sections = [Section("Ch 1", "A", [(words(4), 1)]), Section("Ch 1", "B", [(words(4), 1)]), Section("Ch 1", "C", [(words(4), 2)])]
    chunks = pack("doc", sections)
    assert len(chunks) == 1
    assert chunks[0].headings == ["A", "B", "C"]
    assert (chunks[0].page_start, chunks[0].page_end) == (1, 2)


def test_chunks_never_span_two_chapters(small_limits):
    sections = [Section("Ch 1", "A", [(words(12), 1)]), Section("Ch 2", "B", [(words(12), 2)])]
    assert [c.chapter for c in pack("doc", sections)] == ["Ch 1", "Ch 2"]


def test_long_sections_split_at_paragraph_breaks(small_limits):
    paragraphs = [(words(12, f"p{i}"), 1) for i in range(5)]  # 5 x 13 words, max 30
    chunks = pack("doc", [Section("Ch 1", "Long", paragraphs)])
    assert len(chunks) > 1
    assert all(c.word_count <= 40 for c in chunks)  # headings add a few words
    for c in chunks:  # no paragraph was cut in half
        for part in c.text.split("\n\n"):
            if not part.startswith("## "):
                assert part.count(".") == 1


def test_big_tables_split_by_rows_with_the_caption_repeated(small_limits):
    table = "Table 1 Sprint splits\n" + "\n".join(f"row {i} | 3.8 | 6.3 | 8.0 | 9.9" for i in range(20))
    pieces = _split_long([("Results", table, None)])
    assert len(pieces) > 1
    for piece in pieces:
        assert piece[0][1].startswith("Table 1 Sprint splits")


# ---- Research-article XML (after Step 15) ----

def test_bibliography_markers_are_stripped_from_xml_text():
    p = ET.fromstring('<p>Plyometrics improve sprinting [<xref ref-type="bibr" rid="b1">12</xref>, '
                      '<xref ref-type="bibr" rid="b2">13</xref>] in athletes.</p>')
    assert _xml_text(p) == "Plyometrics improve sprinting in athletes."


# ---- The label that gets embedded (Step 12) ----

def test_note_label_does_not_repeat_the_title():
    source = Source(id="notes-x", title="Notes: Older Adults", publisher="p", year=2026, license="l",
                    license_group="A", attribution="a", local_path="x", type="notes", format="markdown")
    chunk = chunking.Chunk("notes-x", 0, "Older Adults", ["Programming guidelines"], "Text.", None, None)
    assert embed_text_for(source, chunk).splitlines()[0] == "Notes: Older Adults > Programming guidelines"
