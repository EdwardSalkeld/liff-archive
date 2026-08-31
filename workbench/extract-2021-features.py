#!/usr/bin/env python3
"""Create initial LIFF 2021 feature records from catalogue-page PDFs.

The 2021 catalogue uses two feature entries per landscape PDF.  This script
uses Poppler's positioned XHTML output to keep the description and metadata
columns separate.  It intentionally leaves the shorts section for the
shorts-grid extraction pass.
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

# The physical PDF-page ranges omit the four section-introduction spreads.
FEATURE_RANGES = (
    (5, 25, "Official Selection"),
    (27, 41, "Cinema Versa"),
    (43, 65, "Fanomenon"),
    (94, 102, "Rear View"),
)

FIELD_LABELS = {
    "Original Title": "original_title",
    "Country": "countries",
    "Countries": "countries",
    "Year": "year",
    "Running Time": "runtime_minutes",
    "Language": "languages",
    "Languages": "languages",
    "Director": "directors",
    "Screenwriter": "screenwriters",
    "Producer": "producers",
    "Leading Cast": "cast",
    "Cinematographer": "cinematographers",
    "Editor": "editors",
    "Print Source": "print_source",
}


def text(node: ET.Element) -> str:
    return " ".join(word.text or "" for word in node.iter() if word.tag.endswith("word")).strip()


def blocks(pdf: Path) -> list[tuple[float, float, str]]:
    result = subprocess.run(
        ["pdftotext", "-bbox-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    # A few PDF text layers contain bare ampersands/control characters, which
    # Poppler passes through despite advertising XHTML output.
    xml = re.sub(r"&(?!#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z]+;)", "&amp;", result.stdout)
    xml = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", xml)
    root = ET.fromstring(xml)
    out = []
    for block in root.iter():
        if not block.tag.endswith("block"):
            continue
        line_values = [text(line) for line in block.iter() if line.tag.endswith("line")]
        value = "\n".join(value for value in line_values if value)
        if value:
            out.append((float(block.attrib["xMin"]), float(block.attrib["yMin"]), value))
    return out


def side_blocks(all_blocks: list[tuple[float, float, str]], side: str) -> tuple[str, list[str], list[str]]:
    if side == "left":
        title_x, title_limit, metadata_min, metadata_max = 0, 320, 320, 520
        body_min, body_max = 0, 320
    else:
        title_x, title_limit, metadata_min, metadata_max = 520, 820, 820, 930
        body_min, body_max = 520, 820

    titles = [value for x, y, value in all_blocks if title_x <= x < title_limit and y < 60]
    title = " ".join(titles).strip()
    metadata = [value for x, y, value in all_blocks if metadata_min <= x < metadata_max and y < 590]
    body = [value for x, y, value in all_blocks if body_min <= x < body_max and 55 <= y < 590]
    return title, metadata, body


def parse_metadata(items: list[str]) -> dict[str, object]:
    lines: list[str] = []
    for item in items:
        lines.extend(part.strip() for part in item.splitlines() if part.strip())
    # bbox output normally gives one whole metadata column as a single block;
    # split its individual lines before identifying field labels.
    if len(lines) == len(items):
        lines = []
        for item in items:
            lines.extend(re.split(r"\s{2,}", item))
    parsed: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        line = line.strip()
        if line in FIELD_LABELS:
            current = FIELD_LABELS[line]
            parsed.setdefault(current, [])
        elif current:
            parsed[current].append(line)

    record: dict[str, object] = {}
    for key, values in parsed.items():
        if not values:
            continue
        if key == "year":
            years = [int(y) for y in re.findall(r"\b(?:18|19|20)\d{2}\b", " ".join(values))]
            if len(years) == 1:
                record["year"] = years[0]
            elif years:
                record["years"] = years
        elif key == "runtime_minutes":
            match = re.search(r"(?:(\d+)hr\s*)?(\d+)min", " ".join(values), re.I)
            if match:
                record[key] = int(match.group(1) or 0) * 60 + int(match.group(2))
        elif key in {"original_title", "print_source"}:
            record[key] = " ".join(values)
        else:
            record[key] = values
    return record


def parse_body(items: list[str]) -> tuple[str, dict[str, str] | None]:
    description_parts: list[str] = []
    quote_parts: list[str] = []
    in_quote = False
    for item in items:
        if item.startswith("‘"):
            in_quote = True
        (quote_parts if in_quote else description_parts).append(item)
    description = "\n\n".join(description_parts).strip()
    if not quote_parts:
        return description, None
    quote_text = " ".join(quote_parts).strip()
    credit_match = re.search(r"(?:’|\.)\s*((?:Director|[A-Z][\w’'\-]+(?:\s+[A-Z][\w’'\-]+){1,3}),?.*)$", quote_text)
    credit = ""
    if credit_match:
        credit = credit_match.group(1).strip()
        quote_text = quote_text[: credit_match.start() + 1].strip()
    return description, {"text": quote_text, "credit": credit}


def slug(title: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", title.lower()))


def extract_page(number: int, section: str) -> list[Path]:
    source = PAGES / f"page-{number:02d}.pdf"
    page_blocks = blocks(source)
    created: list[Path] = []
    for side in ("left", "right"):
        title, metadata, body = side_blocks(page_blocks, side)
        if not title or not metadata or not body:
            continue
        record: dict[str, object] = {"title": title, "page": source.name, "section": section}
        record.update(parse_metadata(metadata))
        description, quote = parse_body(body)
        if not description:
            continue
        record["description"] = description
        if quote and quote["text"]:
            record["quote"] = quote
        output = OUT / f"page-{number:02d}-{slug(title)}.json"
        if output.exists():
            continue
        output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created.append(output)
    return created


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log = OUT / "extraction_log.md"
    log_lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else ["# 2021 Catalogue Extraction Log", ""]
    for start, end, section in FEATURE_RANGES:
        for number in range(start, end + 1):
            created = extract_page(number, section)
            if created:
                titles = [json.loads(path.read_text(encoding="utf-8"))["title"] for path in created]
                log_lines.append(f"- Page {number:03d} - extracted {', '.join(titles)}")
            else:
                log_lines.append(f"- Page {number:03d} - review required; no feature records created")
    log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
