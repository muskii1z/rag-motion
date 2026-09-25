"""Step 11: extract page text from a source document and report on its quality.

Run from the project folder:
    uv run python scripts/extract_document.py pag2
    uv run python scripts/extract_document.py pag2 --show 25    # also print page 25's cleaned text

Writes data/raw/<source_id>/pages.jsonl (git-ignored), one JSON object per page.
"""

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict

from ragmotion.ingestion import PROJECT_ROOT, extract_pdf_pages, load_sources, verify_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_id")
    parser.add_argument("--show", type=int, help="print the cleaned text of this PDF page number")
    args = parser.parse_args()

    source = load_sources()[args.source_id]
    verify_file(source)
    print(f"Verified {source.path.name} matches the manifest (sha256).")

    pages = extract_pdf_pages(source)

    out_dir = PROJECT_ROOT / "data" / "raw" / source.id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "pages.jsonl"
    with out_file.open("w") as f:
        for p in pages:
            f.write(json.dumps(asdict(p)) + "\n")

    # ---- Quality report: what will cause trouble when we chunk? ----
    words = [p.word_count for p in pages]
    raw_words = sum(len(p.raw_text.split()) for p in pages)
    print(f"\nPAGES: {len(pages)}   WORDS raw: {raw_words:,}  cleaned: {sum(words):,}   "
          f"median cleaned words/page: {sorted(words)[len(words)//2]}")

    sparse = [p for p in pages if p.word_count < 40]
    print(f"\nNEARLY EMPTY PAGES (<40 words): {len(sparse)}")
    print("  " + ", ".join(f"{p.pdf_page}({p.word_count}w)" for p in sparse))

    # Running headers/footers repeat on many pages, but the page number changes each time,
    # so digits are replaced with '#' before counting (lesson from Step 11).
    def repeated_lines(texts: list[str]) -> list[tuple[str, int]]:
        counts = Counter()
        for t in texts:
            counts.update({re.sub(r"\d+", "#", ln.strip()) for ln in t.splitlines() if ln.strip()})
        return [(ln, n) for ln, n in counts.most_common(10) if n >= len(texts) * 0.15]

    for label, texts in (("raw", [p.raw_text for p in pages]), ("cleaned", [p.text for p in pages])):
        rep = repeated_lines(texts)
        print(f"\nLINES ON 15%+ OF PAGES, digits normalized ({label}): {len(rep)}")
        for line, n in rep:
            print(f"  {n:>3} pages: {line[:80]!r}")

    headings = [ln for p in pages for ln in p.text.splitlines() if ln.startswith("## ")]
    print(f"\nHEADINGS DETECTED: {len(headings)}   first 8: {[h[3:40] for h in headings[:8]]}")

    raw_breaks = sum(len(re.findall(r"[a-z]-\n[a-z]", p.raw_text)) for p in pages)
    print(f"LINE-END HYPHENS in raw text: {raw_breaks} (joined in cleaned text, hyphen kept)")

    print(f"\nWrote {out_file.relative_to(PROJECT_ROOT)}")

    if args.show:
        p = pages[args.show - 1]
        print(f"\n===== CLEANED TEXT, PDF page {p.pdf_page} (printed label {p.page_label!r}) =====")
        print(p.text)


if __name__ == "__main__":
    main()
