# 0063. JATS tables nested inside paragraphs are read separately, row by row
**Date:** 2026-10-01 · **Step:** Phase 2 quality pass, Q3 · **Status:** accepted

## Context
JATS is the standard XML format for journal articles ([0022](0022-research-papers-europe-pmc-jats-xml-not-pdfs.md)). Most publishers place a table (`table-wrap`) next to paragraphs. Bastos et al. 2024 (SAGE) places two tables *inside* paragraphs (`<p>`). The reader took a paragraph's whole text, so one table became a single 1,649-word run-on chunk with cells glued together: "Studies (%)Samples K (%)SAMPLE SIZE31 total…". The row splitter for big tables never ran, because the table arrived as paragraph text.

## Options considered
- **Leave it.** Pros: no code change. Cons: an unreadable, oversized chunk in the knowledge base.
- **Drop nested tables entirely.** Pros: simplest. Cons: loses the table's content.
- **Read nested tables separately.** Skip them in the paragraph text and yield each one as its own block, the same way top-level tables are read. Pros: the paragraph stays clean and the table is chunked row by row with its caption. Cons: a little more reader code.

## Decision
`_xml_text()` skips `table-wrap` and `fig` children of a paragraph; `jats_blocks()` yields each nested table through `_table_text()` (caption first, then one line per row, cells joined by " | "). Covered by `test_tables_nested_in_a_paragraph_are_read_row_by_row_not_flattened`.

## Tradeoffs
- A nested table now appears after the paragraph that contained it, not in the middle of it.
- Figures nested in a paragraph used to leak their caption text into the paragraph; now they are dropped, which matches how the reader already treats figures at section level (it never reads figures).
- Checked on all 7 XML sources: only Bastos had nested tables (2). Bastos re-chunked to 23 passages, max 446 words.

## Revisit when
- A new source shows another nesting quirk (check the longest and shortest chunks after every new source).
- Nested figure captions turn out to hold content that answers need.
