#!/usr/bin/env python3
"""Restore 2020 catalogue quotes whose credit wrapped across PDF blocks."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "intermediate-extract/2020"
QUOTES = {
    "page-15-76-days.json": (
        "‘We had a lot of discussions about how to tell the story. The pandemic is continuing to evolve. News analysis of what happened in the past can flip flop. It depends on how each country is reacting, not just in the past, but also in the current and upcoming phases. I decided not to include any news clips or statistics… By making it “smaller,” or just focusing on the human emotions in the edit, I hope my film will last longer. Instead of news analysis or political analysis, I want this film to show how human beings help each other live through catastrophes. I would like future generations to be able to watch this. The story can still resonate with them because every once in a while, we all have to live through a crisis whether it’s a pandemic, a war, or something else. How can we see a glimmer of hope? How can we live through this together?’",
        "Hao Wu, Co-director",
    ),
    "page-24-chop-chop-night-in-of-the-dead.json": (
        "‘With Chop Chop, we always knew we wanted to do a genre mash-up. And I think along the way somewhere my own taste in movies spilled into the mix. I’m a huge Pulp Fiction, Breaking Bad, Guy Ritchie, and [Steven] Soderbergh fan. And I particularly love crime thrillers with dark humour. [We were influenced by] a lot of industry self-starters and their DIY films; Duplass Brothers, Adam Wingard’s A Horrible Way To Die (this was a big one for me)(LIFF 2010), Sean Baker, etc. We did not have a clear path or any real connections in ‘the business’, plain and simple. All we had was this idea that ‘we want to make a feature film, so let’s write something up and find a way to shoot it.’ Hence began our Chop Chop journey.’",
        "Taken from a Rue Morgue interview with Director, Rony Patel",
    ),
    "page-27-the-old-man-movie-night-in-of-the-dead.json": (
        "‘Baltic country-bumpkin shock comedy The Old Man Movie is not a film for the faint of heart, the squeamish, easily nauseated, lactose-intolerant, or humour-impaired. It’s a feature-length expansion of Peeter Ritso and Mikk Mägi’s animated webseries, initiated in 2012 as little more than a wry joke while in school. It became hugely successful, which prompts some very serious concerns about the moral and psychological health of the Estonian people. In any case, the derisive look at life out in farm country is pretty universal, as are the assorted bodily functions and effluvia that soon enough stain the screen. Written and directed by Mägi and Oskar Lehemaa, The Old Man Movie is a high-water mark for stop-motion animation, and a glorious new low in lowbrow laughs!’",
        "Rupert Bottenberg for Fantasia Festival",
    ),
    "page-28-the-twentieth-century.json": (
        "‘[The inspiration] began with the diary of Mackenzie King. I read it as a university student and I was really affected by it. I felt personally connected to his most extreme outpourings. I was really amazed by how maudlin, how hypersensitive and confused and bewildered and panic-stricken the diary was. I would say a diary as a historical document is not an authoritative, factual chronology. I think of it as a parallel consciousness, somewhere between a dream and a highly subjective processing of the chaos of your life. So I really wanted the movie to feel like this. I describe it as kind of a nightmare that King would have had in 1899. The people and events of his life are re-processed into this surreal order, much like when we dream.’",
        "Taken from a Slashfilm interview with Director, Matthew Rankin",
    ),
    "page-76-sheep-and-wolves-pig-deal.json": (
        "‘It’s important that a film is made about Alzheimer’s disease, as the subject is still taboo. People are ashamed of this disease, afraid that they will be considered ‘crazy’. If we break the taboo and talk about it more as a disease then a lot of people will feel less lonely. It’s just a part of life.’",
        "Director, Mischa Kamp",
    ),
    "page-77-snow-white-and-the-magic-of-the-dwarfs.json": (
        "‘This film adaptation borrows heavily from the fantasy genre, with convincing special effects and with characters that brush against the classic fairytale line. This Snow White [is not only] beautiful, [but also] strong and courageous. Fortunately, the times when the heroines of such stories were attractive, but otherwise primarily victims, are over. A big hit, additionally, are the dwarfs, a collection of daring lads who tend to have a certain belligerence but are otherwise a compassionate bunch.’",
        "Tilmann P. Gangloff, Frankfurter Rundschau newspaper",
    ),
}


def main() -> None:
    for filename, (text, credit) in QUOTES.items():
        path = OUT / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        data["quote"] = {"text": text, "credit": credit}
        if data.get("notes", "").startswith("UNCERTAIN: Standalone quote"):
            data.pop("notes")
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
