"""Document ingestion, stage 2: cut extracted text into chunks for retrieval (Step 12).

Method: structure-aware chunking with size limits.
  1. Read the document as blocks in reading order: headings and paragraphs (with page numbers).
  2. Group them into sections: a chapter-level heading starts a new chapter; other headings start
     a new section inside it.
  3. Pack sections into chunks:
       - a chunk never spans two chapters
       - small neighboring sections are merged until the chunk reaches MIN_WORDS
       - sections longer than MAX_WORDS are split at paragraph breaks (sentences if one paragraph
         is itself too long), never mid-sentence
       - no overlap: every chunk is labeled with "title > chapter > sections" instead
  4. Fragments under MIN_PARAGRAPH_WORDS (infographic scraps like "2" or "YOUR WAY") are dropped.

The size limits are a first guess for this corpus (median section ~116 words); Step 15's evaluation
can compare variants. Every chunk records `chunker_label()` so variants can coexist in the table.
"""

import json
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from dataclasses import dataclass, field

import yaml

from ragmotion.ingestion import PROJECT_ROOT, Source

MIN_WORDS = 150
MAX_WORDS = 450
MIN_PARAGRAPH_WORDS = 4
CHAPTER_HEADING = re.compile(r"^(Chapter \d+\.|Appendix \d+\.|Glossary$)")
SKIP_NOTE_SECTIONS = {"Sources", "Not covered by these sources"}
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9“\"(])")


def chunker_label() -> str:
    return f"structure-v1(min={MIN_WORDS},max={MAX_WORDS})"


def _words(text: str) -> int:
    return len(text.split())


@dataclass
class Block:
    text: str
    is_heading: bool
    level: int  # 1 = chapter-level heading, 2 = section heading, 0 = paragraph
    page: int | None


@dataclass
class Section:
    chapter: str
    heading: str | None
    paragraphs: list[tuple[str, int | None]] = field(default_factory=list)

    @property
    def words(self) -> int:
        return sum(_words(t) for t, _ in self.paragraphs)


@dataclass
class Chunk:
    source_id: str
    chunk_index: int
    chapter: str
    headings: list[str]
    text: str
    page_start: int | None
    page_end: int | None

    @property
    def word_count(self) -> int:
        return _words(self.text)


# ---- 1. Read blocks -------------------------------------------------------------------------


def pdf_blocks(source: Source) -> Iterator[Block]:
    """Blocks from the cleaned pages written by scripts/extract_document.py (Step 11)."""
    pages_file = PROJECT_ROOT / "data" / "raw" / source.id / "pages.jsonl"
    if not pages_file.exists():
        raise FileNotFoundError(f"{pages_file} missing: run scripts/extract_document.py {source.id} first")
    skip = set(source.skip_pages or [])
    for line in pages_file.open():
        page = json.loads(line)
        if page["pdf_page"] in skip:
            continue
        for part in page["text"].split("\n\n"):
            part = part.strip()
            if part.startswith("## "):
                heading = part[3:].strip()
                level = 1 if CHAPTER_HEADING.match(heading) else 2
                yield Block(heading, True, level, page["pdf_page"])
            elif part:
                yield Block(part, False, 0, page["pdf_page"])


def note_blocks(source: Source) -> Iterator[Block]:
    """Blocks from a Markdown note: '# Title' is chapter-level, '## Section' a section."""
    _, frontmatter, body = source.path.read_text().split("---", 2)
    yaml.safe_load(frontmatter)  # fail loudly on broken frontmatter; metadata comes from the manifest
    for part in re.split(r"\n\s*\n", body):
        lines = part.strip().splitlines()
        if not lines:
            continue
        match = re.match(r"^(#{1,3})\s+(.*)", lines[0])
        if match:
            yield Block(match.group(2).strip(), True, 1 if len(match.group(1)) == 1 else 2, None)
            lines = lines[1:]
        if lines:
            yield Block("\n".join(lines).strip(), False, 0, None)


# Research articles (JATS XML): administrative sections that carry no training content.
SKIP_ARTICLE_SECTIONS = {
    "acknowledgements", "acknowledgments", "abbreviations", "author contributions", "authors’ contributions",
    "authors' contributions", "funding", "availability of data and materials", "declarations", "footnotes",
    "references", "associated data", "supplementary information", "ethics approval and consent to participate",
    "consent for publication", "competing interests",
}


def _xml_text(elem: ET.Element) -> str:
    """Paragraph text without in-text reference markers like [12] (xref to the bibliography)."""
    parts = [elem.text or ""]
    for child in elem:
        if not (child.tag == "xref" and child.get("ref-type") == "bibr"):
            parts.append(_xml_text(child))
        parts.append(child.tail or "")
    text = "".join(parts)
    text = re.sub(r"\[\s*[,;–-]*\s*\]|\(\s*[,;–-]*\s*\)", "", text)  # brackets left empty by removed refs
    return re.sub(r"\s+", " ", text).strip()


def _table_text(wrap: ET.Element) -> str:
    """A table as plain text: its caption, then one line per row with cells joined by ' | '."""
    lines = []
    caption = " ".join(filter(None, [(wrap.findtext("label") or "").strip(), _xml_text(wrap.find("caption")) if wrap.find("caption") is not None else ""]))
    if caption:
        lines.append(caption)
    for row in wrap.iter("tr"):
        cells = [_xml_text(c) for c in row if c.tag in ("td", "th")]
        if any(cells):
            lines.append(" | ".join(cells))
    return "\n".join(lines)


def jats_blocks(source: Source) -> Iterator[Block]:
    """Blocks from a JATS XML research article: top-level section titles are chapter-level,
    nested section titles are sections; paragraphs and tables become text. No page numbers."""
    body = ET.parse(source.path).getroot().find(".//body")

    def walk(sec: ET.Element, depth: int) -> Iterator[Block]:
        title = _xml_text(sec.find("title")) if sec.find("title") is not None else ""
        if depth == 1 and title.lower() in SKIP_ARTICLE_SECTIONS:
            return
        if title:
            yield Block(title, True, 1 if depth == 1 else 2, None)
        for child in sec:
            if child.tag == "p":
                text = _xml_text(child)
                if text:
                    yield Block(text, False, 0, None)
            elif child.tag == "table-wrap":
                yield Block(_table_text(child), False, 0, None)
            elif child.tag == "list":
                items = [_xml_text(li) for li in child.iter("list-item")]
                yield Block("\n".join(f"• {i}" for i in items if i), False, 0, None)
            elif child.tag == "sec":
                yield from walk(child, depth + 1)

    for sec in body.findall("sec"):
        yield from walk(sec, 1)


# ---- 2. Group into sections -----------------------------------------------------------------


def build_sections(blocks: Iterator[Block], first_chapter: str, skip_sections: set[str]) -> list[Section]:
    sections: list[Section] = []
    chapter = first_chapter
    current = Section(chapter, None)
    for block in blocks:
        if block.is_heading:
            if current.paragraphs:
                sections.append(current)
            if block.level == 1:
                chapter = block.text
            current = Section(chapter, None if block.level == 1 else block.text)
        elif _words(block.text) >= MIN_PARAGRAPH_WORDS:
            current.paragraphs.append((block.text, block.page))
    if current.paragraphs:
        sections.append(current)
    return [s for s in sections if s.heading not in skip_sections]


# ---- 3. Pack into chunks --------------------------------------------------------------------

Item = tuple[str | None, str, int | None]  # (section heading, paragraph text, page)


def _split_long(items: list[Item]) -> list[list[Item]]:
    """Split an oversized section at paragraph breaks (or sentences) into pieces <= MAX_WORDS."""
    units: list[Item] = []
    for heading, text, page in items:
        if _words(text) <= MAX_WORDS:
            units.append((heading, text, page))
        elif "\n" in text:  # a big table or list: split by rows, repeating the first line (caption)
            first, *rows = text.split("\n")
            piece: list[str] = []
            for row in rows:
                if piece and _words(first) + sum(_words(r) for r in piece) + _words(row) > MAX_WORDS:
                    units.append((heading, "\n".join([first, *piece]), page))
                    piece = []
                piece.append(row)
            if piece:
                units.append((heading, "\n".join([first, *piece]), page))
        else:  # a single huge paragraph: fall back to sentence boundaries
            units.extend((heading, s, page) for s in SENTENCE_END.split(text))
    pieces: list[list[Item]] = [[]]
    for unit in units:
        if pieces[-1] and sum(_words(t) for _, t, _ in pieces[-1]) + _words(unit[1]) > MAX_WORDS:
            pieces.append([])
        pieces[-1].append(unit)
    if len(pieces) > 1 and sum(_words(t) for _, t, _ in pieces[-1]) < MIN_WORDS:
        pieces[-2].extend(pieces.pop())  # don't leave a tiny tail; slightly over MAX is acceptable
    return pieces


def _make_chunk(source_id: str, chapter: str, items: list[Item]) -> Chunk:
    lines, headings, last_heading = [], [], None
    for heading, text, _ in items:
        if heading and heading != last_heading:
            lines.append(f"## {heading}")
            if heading not in headings:
                headings.append(heading)
            last_heading = heading
        lines.append(text)
    pages = [p for _, _, p in items if p is not None]
    return Chunk(source_id, -1, chapter, headings, "\n\n".join(lines), min(pages, default=None), max(pages, default=None))


def pack(source_id: str, sections: list[Section]) -> list[Chunk]:
    """Pack sections into chunks. Works on lists of paragraphs; Chunk objects are built at the end."""
    groups: list[tuple[str, list[Item]]] = []  # (chapter, paragraphs) per finished chunk
    buffer: list[Item] = []
    chapter: str | None = None

    def words(items: list[Item]) -> int:
        return sum(_words(t) for _, t, _ in items)

    def flush() -> None:
        if not buffer:
            return
        prev = groups[-1] if groups else None
        # A leftover smaller than MIN_WORDS joins the previous chunk if same chapter and it still fits.
        if words(buffer) < MIN_WORDS and prev and prev[0] == chapter and words(prev[1]) + words(buffer) <= MAX_WORDS:
            prev[1].extend(buffer)
        else:
            groups.append((chapter, list(buffer)))
        buffer.clear()

    for section in sections:
        if section.chapter != chapter:
            flush()
            chapter = section.chapter
        items = [(section.heading, t, p) for t, p in section.paragraphs]
        if section.words > MAX_WORDS:
            flush()
            groups.extend((chapter, piece) for piece in _split_long(items))
            continue
        if words(buffer) + section.words > MAX_WORDS:
            flush()
        buffer.extend(items)
        if words(buffer) >= MIN_WORDS:
            flush()
    flush()

    chunks = [_make_chunk(source_id, ch, items) for ch, items in groups]
    for i, chunk in enumerate(chunks):
        chunk.chunk_index = i
    return chunks


# ---- 4. Entry points ------------------------------------------------------------------------


def chunk_source(source: Source) -> list[Chunk]:
    if source.format == "markdown":
        sections = build_sections(note_blocks(source), source.title, SKIP_NOTE_SECTIONS)
    elif source.format == "jats-xml":
        sections = build_sections(jats_blocks(source), "Article", set())
    else:  # pdf
        sections = build_sections(pdf_blocks(source), "Front matter and summary", set())
    return pack(source.id, sections)


def embed_text_for(source: Source, chunk: Chunk) -> str:
    """The exact text that gets embedded: a location label, then the chunk text."""
    label = source.title
    if chunk.chapter not in source.title:  # a note's "# Title" repeats the source title; skip it
        label += f" > {chunk.chapter}"
    if chunk.headings:
        label += " > " + "; ".join(chunk.headings)
    return f"{label}\n\n{chunk.text}"
