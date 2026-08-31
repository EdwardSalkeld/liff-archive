#!/usr/bin/env python3
"""Extract the repeated short-film cells from the 2021 catalogue.

Each shorts spread has independent left/right grids: title and print source in
the outer column, with synopsis and inline metadata in the inner column.
Records are deliberately limited to fields that can be read unambiguously
from that grid; anything unusual is added to the review queue.
"""

from __future__ import annotations

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "print-media/2021-cat-pages"
OUT = ROOT / "intermediate-extract/2021"
LABEL = r"(?:Premiere Status|Running Time|Year|Country|Language|Director|Screenwriter|Producer|Key Cast|Cinematographer|Editor|Sound|Music)"
SHORT_PAGES = {
    **{number: "Cinema Versa" for number in (40, 41)},
    **{number: "Fanomenon" for number in range(61, 66)},
    **{number: "Leeds Short Film Awards" for number in range(70, 93)},
    102: "Rear View",
}


def line_text(node: ET.Element) -> str:
    return " ".join(word.text or "" for word in node.iter() if word.tag.endswith("word")).strip()


def page_blocks(pdf: Path) -> list[tuple[float, float, str]]:
    result = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"], check=True, capture_output=True, text=True)
    xml = re.sub(r"&(?!#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z]+;)", "&amp;", result.stdout)
    xml = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", xml)
    root = ET.fromstring(xml)
    values = []
    for block in root.iter():
        if block.tag.endswith("block"):
            value = " ".join(line_text(line) for line in block.iter() if line.tag.endswith("line"))
            if value:
                values.append((float(block.attrib["xMin"]), float(block.attrib["yMin"]), value))
    return values


def clean_title(value: str) -> str:
    value = re.sub(r"^.*?(?:winner|winner\s+follows)\s+", "", value, flags=re.I)
    value = re.sub(r"\s+The\s+follows.*$", "", value, flags=re.I)
    return value.strip()


def capture(text: str, label: str, following: str = LABEL) -> str:
    match = re.search(rf"\b{label}\s+(.+?)(?=\s+{following}\b|$)", text, re.I)
    return match.group(1).strip(" ,") if match else ""


def metadata(text: str, print_source: str) -> dict[str, object]:
    record: dict[str, object] = {}
    runtime = capture(text, "Running Time")
    runtime_match = re.search(r"(\d+)min", runtime, re.I)
    if runtime_match:
        record["runtime_minutes"] = int(runtime_match.group(1))
    year = capture(text, "Year")
    year_match = re.search(r"\b(?:19|20)\d{2}\b", year)
    if year_match:
        record["year"] = int(year_match.group())
    countries = capture(text, "Country")
    if countries:
        record["countries"] = [item.strip() for item in countries.split(",") if item.strip()]
    language = capture(text, "Language")
    if language:
        record["languages"] = [item.strip() for item in language.split(",") if item.strip()]
    director = capture(text, "Director")
    if director:
        record["directors"] = [item.strip() for item in director.split(",") if item.strip()]
    screenwriter = capture(text, "Screenwriter")
    if screenwriter:
        record["screenwriters"] = [item.strip() for item in screenwriter.split(",") if item.strip()]
    producer = capture(text, "Producer")
    if producer:
        record["producers"] = [item.strip() for item in producer.split(",") if item.strip()]
    cast = capture(text, "Key Cast")
    if cast:
        record["cast"] = [item.strip() for item in cast.split(",") if item.strip()]
    premiere = capture(text, "Premiere Status")
    if premiere:
        record["premiere_status"] = premiere
    if print_source:
        record["print_source"] = print_source
    return record


def program_for(blocks: list[tuple[float, float, str]], left: bool) -> str:
    lo, hi = (0, 520) if left else (520, 930)
    headings = [value for x, y, value in blocks if lo <= x < hi and y < 60 and "Leeds Short Film Awards" not in value]
    return " ".join(headings).strip() or "Leeds Short Film Awards"


def extract_side(number: int, section: str, blocks: list[tuple[float, float, str]], left: bool) -> list[dict[str, object]]:
    title_lo, title_hi = (0, 180) if left else (520, 680)
    body_lo, body_hi = (180, 520) if left else (680, 930)
    candidates = []
    for x, y, value in blocks:
        if not (title_lo <= x < title_hi and 60 <= y < 590):
            continue
        if value.startswith("Print Source") or value.isdigit():
            continue
        if any(abs(py - y) < 55 and px >= title_lo and px < title_hi and pv.startswith("Print Source") for px, py, pv in blocks):
            candidates.append((y, clean_title(value)))
    candidates.sort()
    program = program_for(blocks, left)
    records = []
    for index, (y, title) in enumerate(candidates):
        next_y = candidates[index + 1][0] if index + 1 < len(candidates) else 590
        cell_body = [value for x, by, value in blocks if body_lo <= x < body_hi and y - 25 <= by < next_y]
        inline = " ".join(value for value in cell_body if re.search(r"\bRunning Time\b", value))
        description = " ".join(value for value in cell_body if not re.search(r"\b(?:Premiere Status|Running Time|Year|Country|Language|Director)\b", value)).strip()
        print_sources = [value.removeprefix("Print Source").strip() for x, py, value in blocks if title_lo <= x < title_hi and y <= py < next_y and value.startswith("Print Source")]
        record: dict[str, object] = {"title": title, "page": f"page-{number:02d}.pdf", "section": section, "program": program, "description": description}
        record.update(metadata(inline, print_sources[0] if print_sources else ""))
        records.append(record)
    return records


def slug(title: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", title.lower()))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    review = OUT / "review_queue.md"
    review_lines = review.read_text(encoding="utf-8").splitlines() if review.exists() else ["# 2021 Catalogue Extraction Review Queue", ""]
    log = OUT / "extraction_log.md"
    log_lines = log.read_text(encoding="utf-8").splitlines()
    for number, section in SHORT_PAGES.items():
        blocks = page_blocks(PAGES / f"page-{number:02d}.pdf")
        records = extract_side(number, section, blocks, True)
        records += extract_side(number, section, blocks, False)
        created = []
        seen: dict[str, int] = {}
        for record in records:
            if not record["title"] or not record["description"]:
                review_lines.append(f"- Page {number:03d} - incomplete short-film cell: {record['title'] or 'untitled'}")
                continue
            base = slug(str(record["title"]))
            seen[base] = seen.get(base, 0) + 1
            suffix = "" if seen[base] == 1 else f"-{seen[base]}"
            path = OUT / f"page-{number:02d}-{base}{suffix}.json"
            if not path.exists():
                path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                created.append(str(record["title"]))
        log_lines.append(f"- Page {number:03d} - extracted {', '.join(created)}" if created else f"- Page {number:03d} - review required; no short records created")
    review.write_text("\n".join(review_lines) + "\n", encoding="utf-8")
    log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
