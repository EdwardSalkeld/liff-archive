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
MANUAL_CREDITS = {
    "page-100-throne-of-blood.json": (" – Jeremy Robinson, Filmotomy", "Jeremy Robinson, Filmotomy"),
    "page-101-the-witness.json": ("", "Péter Bacsó"),
    "page-101-tokyo-story.json": (" – Jaspar Sharp, BFI", "Jaspar Sharp, BFI"),
    "page-28-beijing-spring.json": (" Co-director Andy Cohen, from an interview with the Jerusalem Post.", "Co-director Andy Cohen, from an interview with the Jerusalem Post."),
    "page-31-final-account.json": (" Associate producer Sam Pope, from an interview with NPR.", "Associate producer Sam Pope, from an interview with NPR."),
    "page-35-narcissus-off-duty.json": (" Caetano Veloso, from an interview with Variety.", "Caetano Veloso, from an interview with Variety."),
    "page-35-the-new-corporation-the-unfortunately-necessary-sequel.json": (" Co- director Jennifer Abbott, from an interview with Filmmaker Magazine.", "Co-director Jennifer Abbott, from an interview with Filmmaker Magazine."),
    "page-36-the-nowhere-inn.json": (" Co-writer Carrie Brownstein, from an interview with Indiewire.", "Co-writer Carrie Brownstein, from an interview with Indiewire."),
    "page-37-on-our-doorstep.json": (" Jerry Rothwell, director of The Reason I Jump.", "Jerry Rothwell, director of The Reason I Jump."),
    "page-38-soa.json": (" KMRU, sound artist.", "KMRU, sound artist."),
    "page-45-cube.json": (" Vincenzo Natali, director of the original Cube (1997).", "Vincenzo Natali, director of the original Cube (1997)."),
    "page-47-funky-forest-the-first-contact.json": (" From a review by Todd Brown in Screen Anarchy.", "From a review by Todd Brown in Screen Anarchy."),
    "page-48-the-haunting.json": (" George E. Turner, American Cinematographer magazine.", "George E. Turner, American Cinematographer magazine."),
    "page-56-summer-ghost.json": (" loundraw, Director", "loundraw, Director"),
    "page-57-summer-time-machine-blues.json": (" From a review by Adam Campbell in Midnight Eye.", "From a review by Adam Campbell in Midnight Eye."),
    "page-58-the-town-of-headcounts.json": (" VIFF review – Awesome Friday", "VIFF review – Awesome Friday"),
    "page-60-tokyo-revengers.json": (" Panos Kotzathanasis – Asian Movie Pulse", "Panos Kotzathanasis – Asian Movie Pulse"),
    "page-94-the-afterlight-on-35mm.json": (" – Charlie Shackleton, Director", "Charlie Shackleton, Director"),
    "page-96-de-cierta-manera.json": (" Roberto Zurbano Torres: Essayist and cultural critic, Havana in conversation with Havana Glasgow Film Festival.", "Roberto Zurbano Torres: Essayist and cultural critic, Havana in conversation with Havana Glasgow Film Festival."),
    "page-97-funeral-parade-of-roses.json": (" – Tamsin Cleary, BFI", "Tamsin Cleary, BFI"),
    "page-99-seven-samurai.json": (" – Jaspar Sharp, BFI", "Jaspar Sharp, BFI"),
}


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
        manual = MANUAL_CREDITS.get(path.name)
        if manual:
            marker, credit = manual
            raw_quote = " ".join((quote or {"text": ""})["text"].split())
            quote = {"text": raw_quote.removesuffix(marker).strip() if marker else raw_quote, "credit": credit}
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
