# 0019. Structure-aware chunking with size limits (150–450 words), contextual labels, no overlap
**Date:** 2026-09-25 · **Step:** 12 · **Status:** accepted

## Context
Step 12 splits the knowledge sources into chunks: passages small enough to be embedded and retrieved one at a time. The sources are the Physical Activity Guidelines for Americans, 2nd ed. (cleaned page text from [Step 11](../build-log.md#step-11-document-ingestion-extract-clean-page-text-from-the-physical-activity-guidelines-pdf)) and three original NSCA notes in Markdown. See [Step 12](../build-log.md#step-12-chunking-split-sources-into-passages-and-store-them-in-a-second-table-with-metadata).

Chunk size matters in both directions. Too small, and a chunk loses its context ("2 or more days a week" of what?). Too large, and its embedding blurs into an average of several topics, and each retrieved chunk fills more of the prompt.

Before choosing, the Guidelines' own section sizes were measured. 256 sections contain text. Median 116 words. 54 are under 50 words (including infographic scraps such as "YOUR WAY" and a lone "2"), 106 are 50–150, 71 are 150–300, 23 are 300–600, and 2 are over 600 (the Glossary at 1,341 words and the "Anytown, USA" case study at 905).

## Options considered
- **Fixed size** (for example 300 or 800 words), usually with overlap (the end of one chunk repeated at the start of the next). The industry default is roughly 500–1,000 tokens with 10–20% overlap. Simple and predictable. But it cuts mid-sentence and mixes unrelated topics in one chunk.
- **Section by section** (one chunk per heading). One topic per chunk. But sizes vary wildly: on this document it would give 54 fragments under 50 words and a 1,341-word glossary.
- **Structure-aware with size limits.** Split at headings, merge tiny neighboring sections, and split huge ones at paragraph breaks. Keeps topics together and sizes in a band. The common upgrade over fixed size for documents with clear headings. More rules to write and tune.
- **Semantic.** Embed every sentence and split where the meaning shifts. Adapts to the text. But it costs one embedding call per sentence, is harder to debug, and usually gives only a small gain.

## Decision
Structure-aware chunking with size limits, in `src/ragmotion/chunking.py`, recorded on every row as `structure-v1(min=150,max=450)`:
- Split at headings. Never cross a chapter ("Chapter N.", "Appendix N.", and "Glossary" are chapter-level; everything before Chapter 1 is "Front matter and summary").
- Merge small neighboring sections within a chapter until about 150 words (`MIN_WORDS`).
- Split sections over about 450 words (`MAX_WORDS`) at paragraph breaks, or at sentence breaks if one paragraph is too long. Never mid-sentence.
- **No overlap.** Instead, each chunk's embedded text starts with a label, "title > chapter > sections", so the context overlap would supply is carried by the label.
- Skip junk: noise pages listed in the manifest (`skip_pages`) and fragments under 4 words (`MIN_PARAGRAPH_WORDS`).
- Store metadata on every chunk: source, type, chapter, headings, pages, license, word count, and chunker settings.

The numbers are a first guess. Plain fixed-size chunking is kept as a comparison for the Step 15 evaluation.

## Tradeoffs
- **Tuned to heading-rich documents.** The rules rely on clear headings. Research papers and drill manuals may be structured differently.
- **Depends on Step 11's heading detection.** Headings come from the font-size rule (12 pt and up, [0018](0018-pdf-extraction-pymupdf-layout-cleaning.md)). If that rule misfires, chunk boundaries move with it. One known case: on page 108, some Appendix 1 subsection headings come before the "Appendix 1." heading in reading order, so a few may be filed under the previous chapter (Glossary).
- **Some chunks fall outside the bounds.** 3 of 133 are under 150 words (a short section at a chapter end with nothing to merge with). 7 are over 450 (heading lines add words, and a tiny tail piece is folded into the piece before it); the maximum is 519.
- **Figures reduce to captions.** Chart data is drawn as graphics, so only the caption text survives. The smallest chunk (83 words) is a figure caption plus its source line.
- **No overlap** means a sentence that depends on the previous chunk's last paragraph has only the label for context.

## Revisit when
- Step 15's evaluation compares this against fixed-size chunking (and other size settings), and a variant retrieves better.
- Documents with different structure are added (research papers, the US Army drill manual), and the heading rules don't fit them.
- Appendix questions retrieve oddly (check the page 108 heading-order issue).
