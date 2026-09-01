#!/usr/bin/env python3
"""Create the 2020 music-video records listed in the catalogue grid."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "intermediate-extract/2020"
VIDEOS = [
    ("Monster Rally", "Adventure", ["Zak Marx"]),
    ("The Real Tuesday Weld", "Bathwell in Clerkentime", ["Alex Budovsky"]),
    ("Joya Mooi", "Bitter Parts", ["Michael Middelkoop"]),
    ("Idles", "Never Fight A Man with a Perm", ["Al Brown"]),
    ("Heart Bones", "Open Relations", ["Ed Dougherty"]),
    ("Max Cooper", "Repetition", ["Kevin McGloughlin"]),
    ("Garrett Kato ft Julia Stone", "Breathe It In", ["Emily Dynes"]),
    ("Black Pumas", "Colors", ["Kristian Mercado"]),
    ("Solo Ansamblis", "Dansingas", ["Titas Sūdžius"]),
    ("Peejay", "Seoul Sori", ["Kim Kyoung-bae"]),
    ("Yola", "Shady Grove", ["Jessie Craig"]),
    ("The Cool Greenhouse", "The Sticks", ["Simon Nunn"]),
    ("Marika Hackman", "Hand Solo", ["Sam Bailey"]),
    ("Justin Lacy", "I Don’t Need Another", ["Justin Lacy", "J. Noel Sullivan"]),
    ("Onoe Caponoe", "The Message", ["Tochka"]),
    ("Harry Hanson", "Tinnies with The Reaper", ["Ben G. Brown"]),
    ("The Breeders", "Walking with a Killer", ["Ben G. Brown"]),
    ("Heinrich Himalaya", "Wückis Zam", ["Marcos Sánchez", "Kilian Immervoll", "Anna Sophia Rußmann"]),
    ("Dynoro", "Zver", ["Taisia Deeva"]),
]

STANDALONE_SHORT = {
    "title": "Sins of a Werewolf",
    "page": "page-32.pdf",
    "section": "Fanomenon",
    "program": "Night-in of the Dead",
    "countries": ["Ireland"],
    "year": 2020,
    "runtime_minutes": 22,
    "languages": ["English"],
    "directors": ["David Prendeville"],
    "screenwriters": ["David Prendeville"],
    "producers": ["Michael Byrne", "Eoin Canny", "David Prendeville"],
    "cast": ["Paul Kennedy", "Lalor Roddy", "Elva Trill", "Rynagh O’Grady"],
    "print_source": "prendevd@tcd.ie",
    "description": "Sins of a Werewolf is a darkly comic, tongue-in-cheek send-up of the Catholic church, in the vein of Father Ted, only with more blood and guts. When a seasoned parish priest is bitten on the arse by a mysterious animal, he begins transforming into a werewolf every full moon. The ensuing bloodshed leads to a resurgence in Mass attendances from fearful locals, much to the delight of his senior colleagues.",
}


def slug(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    created = []
    for artist, track, directors in VIDEOS:
        title = f"{artist} — {track}"
        record = {
            "title": title, "page": "page-57.pdf", "section": "Leeds Short Film Awards",
            "program": "Leeds Music Video Competition", "directors": directors,
            "description": f"Music video for {track} by {artist}.",
            "notes": "UNCERTAIN: The catalogue lists only artist, track, and director; no synopsis or production metadata is provided.",
        }
        (OUT / f"page-57-{slug(title)}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created.append(title)
    standalone = OUT / f"page-32-{slug(STANDALONE_SHORT['title'])}.json"
    standalone.write_text(json.dumps(STANDALONE_SHORT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    created.append(STANDALONE_SHORT["title"])
    with (OUT / "shorts_log.md").open("a", encoding="utf-8") as log:
        log.write(f"- Page 057 - extracted {', '.join(created)}\n")
    with (OUT / "review_queue.md").open("a", encoding="utf-8") as review:
        review.write("# 2020 Catalogue Extraction Review Queue\n\n")
        for title in created:
            review.write(f"- Page 057 - {title}: catalogue grid contains no synopsis or production metadata\n")


if __name__ == "__main__":
    main()
