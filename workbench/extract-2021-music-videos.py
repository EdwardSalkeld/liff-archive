#!/usr/bin/env python3
"""Create the 2021 music-video records listed in the catalogue grid."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "intermediate-extract/2021"
VIDEOS = [
    ("Alexis Marshall", "Open Mouth", ["John Bradburn"]),
    ("Blake Mills", "Money Is The One True God", ["Lachlan Turczan"]),
    ("Brotech", "Dis House", ["Joy Sahyoun Cameron"]),
    ("Kuba Kawalec", "I Died", ["Zuzanna Plisz"]),
    ("The Line", "Heads", ["Alexander Kuribayashi"]),
    ("Mary Ocher", "For All We Know", ["Yann les Jours"]),
    ("Gola", "The Line", ["Hanna Marshal"]),
    ("Golden Ears", "Fortaleza", ["Evan Bourque"]),
    ("GusGus & Bjarki", "Chernobyl", ["Valeriy Korshunov"]),
    ("Naomi Alligator", "Concession Stand Girl", ["Corrinne James"]),
    ("So Loki", "West", ["Blake Davey"]),
    ("Tova Gertner", "Good and Better", ["Gil Alkabetz"]),
    ("Hak Baker", "Irrelevant Elephant", ["Jon E Price"]),
    ("Jordan Adetunji", "Angel", ["Shannon Greer", "Carl Quinn"]),
    ("Jordan Klassen", "Identivacation", ["John Voth"]),
    ("Twin Atlantic", "Asynchronous", ["Nicholas Afchain"]),
]


def slug(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    created = []
    for artist, track, directors in VIDEOS:
        title = f"{artist} — {track}"
        record = {
            "title": title,
            "page": "page-92.pdf",
            "section": "Leeds Short Film Awards",
            "program": "Leeds Music Video Competition",
            "directors": directors,
            "description": f"Music video for {track} by {artist}.",
            "notes": "UNCERTAIN: The catalogue lists only artist, track, and director; no synopsis or production metadata is provided.",
        }
        path = OUT / f"page-92-{slug(title)}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created.append(title)
    with (OUT / "extraction_log.md").open("a", encoding="utf-8") as log:
        log.write(f"- Page 092 - extracted {', '.join(created)}\n")
    with (OUT / "review_queue.md").open("a", encoding="utf-8") as review:
        for title in created:
            review.write(f"- Page 092 - {title}: catalogue grid contains no synopsis or production metadata\n")


if __name__ == "__main__":
    main()
