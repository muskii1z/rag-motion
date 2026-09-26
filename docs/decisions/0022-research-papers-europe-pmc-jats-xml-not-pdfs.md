# 0022. Research papers via Europe PMC JATS XML, not PDFs
**Date:** 2026-09-25 · **Step:** after 15 · **Status:** accepted

## Context
Step 15's eval showed plyometrics and sprinting as gaps in the corpus (the collection of searchable texts). Two open-access, CC BY research papers fill them: Kons et al. 2023 (plyometric umbrella review, PMC9832201) and Haugen et al. 2019 (elite sprint performance, PMC6872694), both in *Sports Medicine – Open*. Step 15 had warned that two-column research PDFs might break the extractor, which was tuned on one PDF, the Physical Activity Guidelines ([0018](0018-pdf-extraction-pymupdf-layout-cleaning.md)). Both papers are also available from Europe PMC (a public archive of biomedical papers) as JATS XML. JATS (Journal Article Tag Suite) is a standard XML format for journal articles: sections, titles, paragraphs, lists, tables, and in-text references are all labeled with tags. See the [build log](../build-log.md#after-step-15-trace-cleanup-two-research-papers-eval-set-v2).

## Options considered
- **PDFs through the existing PyMuPDF extractor.** One reader for everything. But the papers are two-column, so reading order would need new layout rules and fresh checking. Tables would need their own handling.
- **Europe PMC JATS XML (chosen).** Structure comes labeled: no layout guessing, tables arrive as rows and cells, and bibliography markers are tagged so they can be removed cleanly. Cons: a second reader in the code (`jats_blocks()`); no page numbers, so passages are located by chapter and section; only works for articles the archive holds as XML.

## Decision
Research articles are read from Europe PMC's JATS XML (`format = "jats-xml"` in `data/sources.toml`), not from their PDFs. The reader keeps sections, paragraphs, lists (as bullets), and tables (caption plus one line per row, cells joined by " | "); it skips administrative sections and strips in-text bibliography markers like `[12]`. Oversized tables and lists are split by rows with the caption repeated. Passages without pages are labeled "research article" in the prompt, terminal, and web page. Same lesson as Step 11: prefer a structured source when one exists.

## Tradeoffs
- Two ingestion paths to maintain (PDF and XML), plus Markdown for notes.
- No page numbers in citations for these papers; a reader locates a passage by its section title.
- The reader handles paragraphs, lists, and tables. What happens to figures (Kons has 6) was not recorded; chart data can't be read as text either way.
- The skip list of administrative section titles is written by hand and may miss unusual titles in other papers.
- Relies on Europe PMC having the article as XML. Many papers (for example non-open-access ones, which are also excluded by [0017](0017-knowledge-source-licensing-policy.md)) won't be available this way.

## Revisit when
- A needed source exists only as a PDF (for example the Army ATP 7-22.02, if it is added): it goes through the PDF path, and two-column layout may still need work.
- Citations need page numbers for research papers.
- The skip list or the table handling misfires on a new paper (check chunk counts, sizes, and a sample table chunk, as done here).
