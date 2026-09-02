#!/usr/bin/env python3
"""Rebuild complete per-page extraction and review logs for 2020."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "intermediate-extract/2020"
SKIPS = {
    1: "blank cover", 2: "introduction", 3: "festival team", 4: "Official Selection introduction",
    14: "Cinema Versa introduction", 22: "Fanomenon introduction", 33: "short-film awards introduction",
    34: "jury page", 35: "jury page", 36: "jury page", 71: "Leeds Young Film Festival introduction",
    78: "feature index", 79: "short-film index", 80: "short-film index", 81: "blank back cover",
}


def main() -> None:
    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    records = []
    for path in sorted(OUT.glob("page-*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        records.append(record)
        by_page[str(record["page"])].append(record)
    lines = ["# 2020 Catalogue Extraction Log", ""]
    for number in range(1, 82):
        page = f"page-{number:02d}.pdf"
        if page in by_page:
            titles = ", ".join(str(record["title"]) for record in by_page[page])
            lines.append(f"- Page {number:03d} - extracted {titles}")
        else:
            lines.append(f"- Page {number:03d} - skipped, {SKIPS.get(number, 'non-film page')}")
    (OUT / "extraction_log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    review = ["# 2020 Catalogue Extraction Review Queue", ""]
    for record in records:
        note = record.get("notes")
        if isinstance(note, str) and note.startswith("UNCERTAIN:"):
            review.append(f"- {record['page']} - {record['title']}: {note.removeprefix('UNCERTAIN: ').strip()}")
    (OUT / "review_queue.md").write_text("\n".join(review) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
