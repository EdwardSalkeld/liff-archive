#!/usr/bin/env python3
"""Extract paired feature-film entries from the 2020 LIFF catalogue."""

from __future__ import annotations

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "print-media/2020-cat-pages"
OUT = ROOT / "intermediate-extract/2020"

# Pages containing a full feature entry in the paired-page layout.  Page 20
# includes The Republics at left and the first documentary-short cells at right.
FEATURE_RANGES = (
    (5, 13, "Official Selection"),
    (15, 20, "Cinema Versa"),
    (23, 29, "Fanomenon"),
    (72, 77, "Leeds Young Film Festival"),
)

FIELD_LABELS = {
    "Original Title": "original_title", "Country": "countries", "Countries": "countries",
    "Year": "year", "Running Time": "runtime_minutes", "Language": "languages",
    "Languages": "languages", "Director": "directors", "Screenwriter": "screenwriters",
    "Producer": "producers", "Leading Cast": "cast", "Cinematographer": "cinematographers",
    "Editor": "editors", "Print Source": "print_source",
}


def node_text(node: ET.Element) -> str:
    return " ".join(word.text or "" for word in node.iter() if word.tag.endswith("word")).strip()


def blocks(pdf: Path) -> list[tuple[float, float, str]]:
    result = subprocess.run(["pdftotext", "-bbox-layout", str(pdf), "-"], check=True, capture_output=True, text=True)
    xml = re.sub(r"&(?!#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z]+;)", "&amp;", result.stdout)
    xml = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", xml)
    root = ET.fromstring(xml)
    return [
        (float(block.attrib["xMin"]), float(block.attrib["yMin"]), value)
        for block in root.iter()
        if block.tag.endswith("block")
        if (value := "\n".join(node_text(line) for line in block.iter() if line.tag.endswith("line")))
    ]


def side_blocks(items: list[tuple[float, float, str]], side: str) -> tuple[str, list[str], list[str]]:
    if side == "left":
        title_min, title_max, meta_min, meta_max, body_min, body_max = 0, 320, 320, 520, 0, 320
    else:
        title_min, title_max, meta_min, meta_max, body_min, body_max = 520, 820, 820, 930, 520, 820
    title = " ".join(" ".join(value.split()) for x, y, value in items if title_min <= x < title_max and y < 60).strip()
    metadata = [value for x, y, value in items if meta_min <= x < meta_max and y < 590]
    body = [value for x, y, value in items if body_min <= x < body_max and 55 <= y < 590]
    return title, metadata, body


def parse_metadata(items: list[str]) -> dict[str, object]:
    parsed: dict[str, list[str]] = {}
    current: str | None = None
    for item in items:
        for line in (line.strip() for line in item.splitlines()):
            if line in FIELD_LABELS:
                current = FIELD_LABELS[line]
                parsed.setdefault(current, [])
            elif current and line:
                parsed[current].append(line)
    record: dict[str, object] = {}
    for key, values in parsed.items():
        joined = " ".join(values)
        if key == "year":
            years = [int(year) for year in re.findall(r"\b(?:18|19|20)\d{2}\b", joined)]
            if len(years) == 1:
                record["year"] = years[0]
            elif years:
                record["years"] = years
        elif key == "runtime_minutes":
            match = re.search(r"(?:(\d+)hr\s*)?(\d+)min", joined, re.I)
            if match:
                record[key] = int(match.group(1) or 0) * 60 + int(match.group(2))
        elif key in {"original_title", "print_source"}:
            record[key] = joined
        elif values:
            record[key] = values
    return record


def parse_body(items: list[str]) -> tuple[str, dict[str, str] | None]:
    description, quote = [], []
    in_quote = False
    for item in items:
        if item.startswith(("‘", "“")):
            in_quote = True
        (quote if in_quote else description).append(item)
    if not quote:
        return "\n\n".join(description).strip(), None
    flattened = " ".join(" ".join(quote).split())
    match = re.search(r"(?:[.’”])\s+(?P<credit>(?:(?:Co-)?Director\b|[A-Z][^,.]{1,80},\s*(?:Co-)?Director\b).*)$", flattened)
    return "\n\n".join(description).strip(), {
        "text": flattened[: match.start() + 1].strip() if match else flattened,
        "credit": match.group("credit").strip() if match else "",
    }


def slug(title: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", title.lower()))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log_lines = ["# 2020 Catalogue Extraction Log", ""]
    for start, end, section in FEATURE_RANGES:
        for number in range(start, end + 1):
            page = PAGES / f"page-{number:02d}.pdf"
            created = []
            for side in ("left", "right"):
                title, metadata, body = side_blocks(blocks(page), side)
                record = parse_metadata(metadata)
                description, quote = parse_body(body)
                if not title or not record or not description:
                    continue
                record.update({"title": title, "page": page.name, "section": section, "description": description})
                if quote and quote["text"]:
                    record["quote"] = quote
                path = OUT / f"page-{number:02d}-{slug(title)}.json"
                path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                created.append(title)
            log_lines.append(f"- Page {number:03d} - extracted {', '.join(created)}" if created else f"- Page {number:03d} - review required")
    (OUT / "extraction_log.md").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
