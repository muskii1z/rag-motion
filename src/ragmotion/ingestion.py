"""Document ingestion, stage 1: from a source file to page-level text (Step 11).

    data/sources.toml  ->  verify the downloaded file (sha256)  ->  extract text per page

Chunking (Step 12) and embedding (Step 13) build on the pages produced here.
"""

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = PROJECT_ROOT / "data" / "sources.toml"


@dataclass
class Source:
    id: str
    title: str
    publisher: str
    year: int
    url: str
    license: str
    license_group: str
    attribution: str
    local_path: str
    sha256: str

    @property
    def path(self) -> Path:
        return PROJECT_ROOT / self.local_path


@dataclass
class PageText:
    source_id: str
    pdf_page: int  # 1-based position in the PDF file
    page_label: str  # the page number printed on the page, if the PDF defines one
    text: str  # cleaned: paragraphs separated by blank lines, headings as "## ..."
    raw_text: str = ""  # exactly what PyMuPDF returned, kept for comparison and debugging

    @property
    def word_count(self) -> int:
        return len(self.text.split())


# Layout settings for clean_page(). Measured on the Physical Activity Guidelines PDF in Step 11
# (letter-size pages, 792 pt tall): page footers sit at y ~747-761, body text is 10 pt,
# headings are 12 pt and larger, normal line gap ~3 pt, paragraph gap ~12 pt.
FOOTER_BAND_PT = 50  # drop lines starting within this distance of the bottom edge
HEADER_BAND_PT = 36  # drop lines ending within this distance of the top edge
HEADING_MIN_SIZE = 12.0  # lines whose largest font is at least this size are headings
PARAGRAPH_GAP_PT = 6.0  # vertical gap between lines that starts a new paragraph
SAME_COLUMN_PT = 20.0  # lines whose left edges differ by more than this are in different columns/boxes


def _join_lines(lines: list[str]) -> str:
    """Join wrapped lines into one paragraph.

    A line ending in "-" followed by a lowercase word is joined WITHOUT a space and the hyphen is
    kept: "moderate-to-" + "vigorous" -> "moderate-to-vigorous". Deleting the hyphen would be
    right for split words ("cardio-" + "respiratory") but wrong for real compounds, and a stray
    hyphen harms retrieval far less than a mangled term.
    """
    out = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if out.endswith("-") and line[:1].islower():
            out += line
        elif out and line[:1] in "•▪◦":  # bullet points keep their own line
            out += "\n" + line
        else:
            out = f"{out} {line}" if out else line
    return out


def clean_page(page: pymupdf.Page) -> str:
    """Rebuild readable paragraphs and headings from a PDF page's positioned text lines."""
    height = page.rect.height
    blocks: list[str] = []  # finished paragraphs and headings
    current: list[str] = []  # lines of the paragraph being built
    prev = None  # (x0, y0, y1) of the previous body line
    heading: list[str] = []

    def flush_paragraph() -> None:
        if current:
            blocks.append(_join_lines(current))
            current.clear()

    def flush_heading() -> None:
        if heading:
            blocks.append("## " + _join_lines(heading))
            heading.clear()

    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if not text:
                continue
            x0, y0, _, y1 = line["bbox"]
            if y0 > height - FOOTER_BAND_PT or y1 < HEADER_BAND_PT:
                continue  # running footer/header (page number + title)
            size = max(span["size"] for span in line["spans"])

            if size >= HEADING_MIN_SIZE:
                flush_paragraph()
                heading.append(text)  # multi-line headings are merged
                prev = None
                continue
            flush_heading()

            new_paragraph = (
                prev is None
                or abs(x0 - prev[0]) > SAME_COLUMN_PT  # different column or sidebar
                or y0 - prev[2] > PARAGRAPH_GAP_PT  # bigger gap than normal line spacing
                or y0 < prev[1]  # jumped back up the page: a new region
            )
            if new_paragraph:
                flush_paragraph()
            current.append(text)
            prev = (x0, y0, y1)

    flush_heading()
    flush_paragraph()
    return "\n\n".join(blocks)


def load_sources() -> dict[str, Source]:
    data = tomllib.loads(MANIFEST.read_text())
    fields = Source.__dataclass_fields__
    return {s["id"]: Source(**{k: v for k, v in s.items() if k in fields}) for s in data["source"]}


def verify_file(source: Source) -> None:
    """Fail loudly if the file is missing or isn't the exact file recorded in the manifest."""
    if not source.path.exists():
        raise FileNotFoundError(f"{source.path} is missing. Download it from {source.url}")
    digest = hashlib.sha256(source.path.read_bytes()).hexdigest()
    if digest != source.sha256:
        raise ValueError(
            f"{source.path.name} does not match the manifest (sha256 {digest[:12]}… vs {source.sha256[:12]}…). "
            "The upstream file may have changed; review it before updating the manifest."
        )


def extract_pdf_pages(source: Source) -> list[PageText]:
    """Every page's cleaned text, plus the raw text PyMuPDF returned."""
    pages = []
    with pymupdf.open(source.path) as doc:
        for i, page in enumerate(doc, start=1):
            pages.append(
                PageText(
                    source_id=source.id,
                    pdf_page=i,
                    page_label=page.get_label() or str(i),
                    text=clean_page(page),
                    raw_text=page.get_text("text"),
                )
            )
    return pages
