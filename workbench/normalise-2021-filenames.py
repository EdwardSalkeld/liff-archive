#!/usr/bin/env python3
"""Align 2021 intermediate filenames with their normalised JSON titles."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "intermediate-extract/2021"


def slug(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def main() -> None:
    sources = sorted(DIRECTORY.glob("page-*.json"))
    destination_counts: defaultdict[str, int] = defaultdict(int)
    planned: list[tuple[Path, Path]] = []
    for path in sources:
        data = json.loads(path.read_text(encoding="utf-8"))
        page = str(data["page"]).removesuffix(".pdf")
        base = f"{page}-{slug(str(data['title']))}"
        destination_counts[base] += 1
        suffix = "" if destination_counts[base] == 1 else f"-{destination_counts[base]}"
        planned.append((path, DIRECTORY / f"{base}{suffix}.json"))
    for source, destination in planned:
        if source == destination:
            continue
        if destination.exists():
            raise SystemExit(f"refusing to overwrite {destination}")
    for source, destination in planned:
        if source != destination:
            source.rename(destination)


if __name__ == "__main__":
    main()
