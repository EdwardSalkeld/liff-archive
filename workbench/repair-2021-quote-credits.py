#!/usr/bin/env python3
"""Restore quote blocks whose wrapped credits are recoverable from page PDFs."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "intermediate-extract/2021"
FEATURE_EXTRACTOR = ROOT / "workbench/extract-2021-features.py"
PROGRAM_SUFFIXES = (
    "LIFF 2021 Opening Film", "LIFF 2021 Closing Film", "Cinema Versa Opening Film",
    "Cinema Versa Closing Film", "Fanomenon Opening Film", "Fanomenon Closing Film",
    "Fanorama", "Fanathons: Day of the Dead", "Fanathons: Night of the Dead",
    "Planet Japan", "Queer Fear", "Kafkaesque Cinema", "BFI Japan 2021", "Stanisław Lem Centenary",
)


def canonical_title(value: str) -> str:
    value = " ".join(value.split())
    for suffix in PROGRAM_SUFFIXES:
        if value.endswith(" " + suffix):
            return value[: -len(suffix)].strip()
    return value


def main() -> None:
    spec = importlib.util.spec_from_file_location("feature_extractor", FEATURE_EXTRACTOR)
    extractor = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(extractor)
    repaired: list[str] = []
    unresolved: list[str] = []
    for path in sorted(DIRECTORY.glob("page-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("notes") != "UNCERTAIN: Standalone quote has no reliably separable credit.":
            continue
        number = int(str(data["page"])[5:7])
        blocks = extractor.blocks(ROOT / "print-media/2021-cat-pages" / str(data["page"]))
        quote = None
        for side in ("left", "right"):
            source_title, _, body = extractor.side_blocks(blocks, side)
            if canonical_title(source_title) == data["title"]:
                _, quote = extractor.parse_body(body)
                break
        if quote and quote.get("credit"):
            data["quote"] = quote
            data.pop("notes", None)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            repaired.append(path.name)
        else:
            unresolved.append(path.name)
    print(f"repaired={len(repaired)} unresolved={len(unresolved)}")
    for name in unresolved:
        print(f"unresolved: {name}")


if __name__ == "__main__":
    main()
