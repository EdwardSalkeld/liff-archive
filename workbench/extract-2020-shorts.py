#!/usr/bin/env python3
"""Extract the structured short-film grids from the 2020 LIFF catalogue."""

from __future__ import annotations

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "print-media/2020-cat-pages"
OUT = ROOT / "intermediate-extract/2020"
SHORT_PAGES = tuple([20, 21, 29, 30, 31, *range(37, 57), *range(58, 71)])
LABEL = r"(?:Form|Original Title|Premiere Status|Running Time|Year|Country|Language|Director|Screenwriter|Producer|Key Cast|Director of Photography|Editor|Sound|Music)"


def text(node: ET.Element) -> str:
    return " ".join(word.text or "" for word in node.iter() if word.tag.endswith("word")).strip()


def blocks(pdf: Path) -> list[tuple[float, float, str]]:
    result = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"], check=True, capture_output=True, text=True)
    xml = re.sub(r"&(?!#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z]+;)", "&amp;", result.stdout)
    root = ET.fromstring(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", xml))
    return [
        (float(block.attrib["xMin"]), float(block.attrib["yMin"]), " ".join(text(line) for line in block.iter() if line.tag.endswith("line")))
        for block in root.iter() if block.tag.endswith("block")
        if " ".join(text(line) for line in block.iter() if line.tag.endswith("line"))
    ]


def capture(value: str, label: str, following: str = LABEL) -> str:
    match = re.search(rf"\b{label}\s+(.+?)(?=\s+{following}\b|$)", value, re.I)
    return match.group(1).strip(" ,") if match else ""


def split_values(value: str) -> list[str]:
    return [part.strip() for part in re.split(r",\s*", value) if part.strip()]


def metadata(value: str, print_source: str) -> dict[str, object]:
    record: dict[str, object] = {}
    runtime = capture(value, "Running Time")
    if match := re.search(r"(\d+)min", runtime, re.I):
        record["runtime_minutes"] = int(match.group(1))
    if match := re.search(r"\b(?:19|20)\d{2}\b", capture(value, "Year")):
        record["year"] = int(match.group())
    for label, key in (("Country", "countries"), ("Language", "languages"), ("Director", "directors"),
                       ("Screenwriter", "screenwriters"), ("Producer", "producers"), ("Key Cast", "cast"),
                       ("Editor", "editors"), ("Sound", "sound"), ("Music", "music")):
        if captured := capture(value, label):
            record[key] = split_values(captured)
    if captured := capture(value, "Original Title"):
        record["original_title"] = captured
    if captured := capture(value, "Premiere Status"):
        record["premiere_status"] = captured
    if print_source:
        record["print_source"] = print_source
    return record


def program_for(items: list[tuple[float, float, str]], left: bool) -> str:
    lo, hi = (0, 520) if left else (520, 930)
    headings = [value for x, y, value in items if lo <= x < hi and y < 60 and "Leeds Short Film Awards" not in value]
    return " ".join(headings).strip() or "Leeds Short Film Awards"


def extract_side(number: int, items: list[tuple[float, float, str]], left: bool) -> list[dict[str, object]]:
    title_lo, title_hi = (0, 180) if left else (520, 680)
    body_lo, body_hi = (180, 520) if left else (680, 930)
    candidates = []
    for x, y, value in items:
        if title_lo <= x < title_hi and 60 <= y < 590 and not value.startswith("Print Source"):
            if any(abs(py - y) < 55 and title_lo <= px < title_hi and pv.startswith("Print Source") for px, py, pv in items):
                candidates.append((y, " ".join(value.split())))
    candidates.sort()
    records = []
    for index, (y, title) in enumerate(candidates):
        next_y = candidates[index + 1][0] if index + 1 < len(candidates) else 590
        body = [value for x, by, value in items if body_lo <= x < body_hi and y - 25 <= by < next_y]
        combined = " ".join(body)
        description = re.split(r"\s+Form\s+", combined, maxsplit=1, flags=re.I)[0].strip()
        sources = [value.removeprefix("Print Source").strip() for x, py, value in items if title_lo <= x < title_hi and y <= py < next_y and value.startswith("Print Source")]
        if title and description:
            record: dict[str, object] = {"title": title, "page": f"page-{number:02d}.pdf", "section": "Leeds Short Film Awards", "program": program_for(items, left), "description": description}
            record.update(metadata(combined, sources[0] if sources else ""))
            records.append(record)
    return records


def slug(title: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", title.lower()))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log = OUT / "shorts_log.md"
    lines = ["# 2020 Shorts Extraction Log", ""]
    for number in SHORT_PAGES:
        items = blocks(PAGES / f"page-{number:02d}.pdf")
        records = extract_side(number, items, True) + extract_side(number, items, False)
        created, seen = [], {}
        for record in records:
            base = slug(str(record["title"]))
            seen[base] = seen.get(base, 0) + 1
            suffix = "" if seen[base] == 1 else f"-{seen[base]}"
            path = OUT / f"page-{number:02d}-{base}{suffix}.json"
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            created.append(str(record["title"]))
        lines.append(f"- Page {number:03d} - extracted {', '.join(created)}" if created else f"- Page {number:03d} - review required")
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
