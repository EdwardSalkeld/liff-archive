#!/usr/bin/env python3
"""Rebuild concise, page-complete extraction and review logs for 2021."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "intermediate-extract/2021"
SKIP_REASONS = {
    1: "introduction and contents", 2: "partners", 3: "team", 4: "Official Selection introduction",
    26: "Cinema Versa introduction", 42: "Fanomenon introduction", 66: "Leeds Short Film Awards introduction",
    67: "jury page", 68: "jury page", 69: "jury page", 93: "Rear View introduction",
    103: "index", 104: "index", 105: "index",
}


def main() -> None:
    by_page: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    records = []
    for path in sorted(DIRECTORY.glob("page-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        by_page[str(data["page"])].append(data)
        records.append((path.name, data))

    log_lines = ["# 2021 Catalogue Extraction Log", ""]
    for page in range(1, 106):
        name = f"page-{page:02d}.pdf"
        titles = [str(record["title"]) for record in by_page[name]]
        if titles:
            log_lines.append(f"- Page {page:03d} - extracted {', '.join(titles)}")
        else:
            log_lines.append(f"- Page {page:03d} - skipped, {SKIP_REASONS.get(page, 'non-film page')}")
    (DIRECTORY / "extraction_log.md").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    review_lines = ["# 2021 Catalogue Extraction Review Queue", ""]
    for name, record in records:
        notes = record.get("notes")
        if isinstance(notes, str) and "UNCERTAIN:" in notes:
            review_lines.append(f"- {name}: {notes}")
    if len(review_lines) == 2:
        review_lines.append("- None")
    (DIRECTORY / "review_queue.md").write_text("\n".join(review_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
