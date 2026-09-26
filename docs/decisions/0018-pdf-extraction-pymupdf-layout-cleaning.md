# 0018. PDF extraction with PyMuPDF and layout-based cleaning
**Date:** 2026-09-25 · **Step:** 11 · **Status:** accepted

## Context
Step 11 is the first real document: the Physical Activity Guidelines for Americans, 2nd ed. (118-page PDF, public domain). A PDF stores characters at positions on a page, not paragraphs, so text extraction has to rebuild reading order. The first raw extraction had problems that would silently damage chunking, embeddings, and retrieval: a running header with the page number on 54 pages, hard line breaks mid-sentence, no blank lines between paragraphs, 60 line-end hyphens (some of them real compound words such as "moderate-to-vigorous"), and bullet points run together. We needed a library, and a way to clean its output. See [Step 11](../build-log.md#step-11-document-ingestion-extract-clean-page-text-from-the-physical-activity-guidelines-pdf).

## Options considered
Library:
- **pypdf.** Pure Python (no compiled parts) and simple. Weaker on complex layouts.
- **pdfplumber.** Very good at tables. Slower.
- **PyMuPDF.** Fast. Returns each line with its position and font size, which allows dropping headers and footers by position and detecting headings by size (useful for section-based chunking in Step 12). Named in the master context document. AGPL-licensed.

Cleaning:
- **Text patterns** (for example, delete lines that repeat on many pages). Missed the running header at first, because each copy had a different page number; it works only after normalizing digits, and it can't rebuild paragraphs.
- **Layout-based cleaning using positions and font sizes, measured on this document.** Drops headers and footers by where they sit, rebuilds paragraphs from line gaps, marks headings by font size.
- **Keep the raw text.** Fastest, but every problem above flows into chunks.

## Decision
Use **PyMuPDF** (1.28.2), and clean each page by layout in `clean_page()` (`src/ragmotion/ingestion.py`), with thresholds measured on this PDF and documented as constants:
- `FOOTER_BAND_PT = 50`, `HEADER_BAND_PT = 36`: drop lines near the bottom or top edge (footers sit at y ≈ 747–761 on a 792-pt page).
- `HEADING_MIN_SIZE = 12.0`: lines of 12 pt or more become `## ` headings (body text is 10 pt, about 90% of words).
- `PARAGRAPH_GAP_PT = 6.0`: a bigger vertical gap starts a new paragraph (normal line gap ~3 pt, paragraph gap ~12 pt).
- `SAME_COLUMN_PT = 20.0`: a left-edge shift larger than this means a different column or sidebar.
- Line-end hyphen followed by a lowercase word: join without a space and keep the hyphen. Bullets ("•") keep their own lines.
- Keep the PDF's internal content order rather than re-sorting by position.
- Store `raw_text` next to the cleaned `text` for every page.

## Tradeoffs
- **Thresholds are document-specific.** They were tuned on one PDF and may need retuning for each new source. A general-purpose parser would need less tuning, but would be less transparent about what it removed.
- **Stray hyphens.** Truly split words keep a hyphen ("cardio-respiratory"). Accepted, because a stray hyphen hurts retrieval less than a mangled compound.
- **Reading order is the PDF's, not visual.** On page 56 a lower "Key Guidelines" box comes before the intro text above it. Fine for this document; could be wrong for others.
- **Tables.** This document's tables are mostly list-style and came out well. Numeric grid tables were not examined and would be harder (pdfplumber is stronger there).
- **AGPL license.** PyMuPDF is fine for an open portfolio project, but needs review before any closed commercial product.
- The PDF is tagged (it has structure labels), and the tags are not used.

## Revisit when
- A new source extracts badly with these thresholds (check the quality report: repeated lines, sparse pages, heading count, word difference between raw and cleaned).
- A source has important numeric grid tables.
- The project heads toward closed commercial use (AGPL review).
- The same thresholds need retuning for several sources in a row. Then consider per-source settings in the manifest, using the PDF's tags, or a general document parser.

## Note 2026-09-25 (Step 12): headings now drive chunk boundaries
- The `## ` headings marked by the font-size rule are now where chunks split ([0019](0019-structure-aware-chunking-150-450-labels-no-overlap.md)). A heading-detection error now moves a chunk boundary, not just a line of formatting.
- The first per-source setting moved into the manifest: `skip_pages` for `pag2` (inside cover, table of contents, credits, infographic, and the Appendix 2 agency directory). This is the "per-source settings in the manifest" direction named above.
- Reading-order consequence seen: on page 108, some Appendix 1 subsection headings come before the "Appendix 1." heading, so a few subsections may be filed under the previous chapter (Glossary). Not fixed.
- Figures: chart data is drawn as graphics and doesn't extract; only captions survive (the smallest chunk, 83 words, is a figure caption plus its source line).

## Note 2026-09-25 (after Step 15): research papers bypass PDF extraction
The first two research papers were ingested from Europe PMC's JATS XML instead of their two-column PDFs ([0022](0022-research-papers-europe-pmc-jats-xml-not-pdfs.md)), so these thresholds have still only been tested on the Physical Activity Guidelines. The Guidelines' 133 chunks were unchanged by the new code.
