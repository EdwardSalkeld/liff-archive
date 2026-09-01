#!/usr/bin/env python3
"""Normalise display-title suffixes introduced by the 2020 page layout."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "intermediate-extract/2020"
PROGRAM_SUFFIXES = {
    "Night-In of the Dead": "Night-in of the Dead",
}
NOTES_SUFFIXES = {"LIFF 2020 Opening Film", "LIFF 2020 Closing Film"}


def main() -> None:
    for path in DIRECTORY.glob("page-*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        title = " ".join(str(data.get("title", "")).split())
        for suffix, program in PROGRAM_SUFFIXES.items():
            if title.endswith(" " + suffix):
                title = title[: -len(suffix)].strip()
                data["program"] = program
        for suffix in NOTES_SUFFIXES:
            if title.endswith(" " + suffix):
                title = title[: -len(suffix)].strip()
                data["notes"] = suffix
        data["title"] = title
        quote = data.get("quote")
        if isinstance(quote, dict):
            for key in ("text", "credit"):
                if isinstance(quote.get(key), str):
                    quote[key] = " ".join(quote[key].split())
            if not quote.get("credit"):
                data.pop("quote")
                data["notes"] = "UNCERTAIN: Standalone quote has no reliably separable credit."
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
