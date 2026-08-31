#!/usr/bin/env python3
"""Normalise line-broken titles and programme labels in generated 2021 JSON."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "intermediate-extract/2021"
PROGRAM_SUFFIXES = (
    "LIFF 2021 Opening Film",
    "LIFF 2021 Closing Film",
    "Cinema Versa Opening Film",
    "Cinema Versa Closing Film",
    "Fanomenon Opening Film",
    "Fanomenon Closing Film",
    "Fanorama",
    "Fanathons: Day of the Dead",
    "Fanathons: Night of the Dead",
    "Planet Japan",
    "Queer Fear",
    "Kafkaesque Cinema",
    "BFI Japan 2021",
    "Stanisław Lem Centenary",
)


def main() -> None:
    for path in DIRECTORY.glob("page-*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        title = " ".join(str(data.get("title", "")).split())
        for suffix in PROGRAM_SUFFIXES:
            if title.endswith(" " + suffix):
                title = title[: -len(suffix)].strip()
                if suffix not in {"LIFF 2021 Opening Film", "LIFF 2021 Closing Film"}:
                    data["program"] = suffix
                else:
                    data["notes"] = suffix
                break
        data["title"] = title
        quote = data.get("quote")
        if isinstance(quote, dict):
            for key in ("text", "credit"):
                if isinstance(quote.get(key), str):
                    quote[key] = " ".join(quote[key].split())
            if not quote.get("credit"):
                data.pop("quote", None)
                data["notes"] = "UNCERTAIN: Standalone quote has no reliably separable credit."
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
