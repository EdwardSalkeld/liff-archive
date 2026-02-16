---
name: liff-catalog-pdf-extraction
description: "Extract structured per-film JSON from LIFF catalogue page PDFs when pages are a mix of film entries and non-film content (intro, index, schedules, adverts, juries). Use for single-page or batch workflows that require multi-pass extraction: text extraction, film-page detection, film block segmentation, JSON normalization, and sanity checks. Default dataset: print-media/2022-cat-pages."
---

# LIFF Catalog PDF Extraction

## Overview

Extract zero or more film records from one catalog page PDF and write one JSON file per film. Skip non-film pages explicitly and log the reason.

Process pages independently so work can be parallelized with low shared context.

Use `references/2022-patterns.md` for 2022-specific section ranges, skip hints, and examples.

## Output Contract

Use these paths by default:

- Input pages: `print-media/2022-cat-pages/page-XX.pdf`
- Film JSON output: `intermediate-extract/2022/page-XX-<slug>.json`
- Raw text cache (optional but recommended): `intermediate-extract/2022/raw-text/page-XX.txt`
- Extraction log: `intermediate-extract/2022/extraction_log.md`
- Manual review queue: `intermediate-extract/2022/review_queue.md`

Write one JSON file per film. If a page has no films, write no JSON files and add a skip log line.

## Dependencies and Tooling

Default extraction should work with CLI tools already used in this repo:

- `pdftotext` (required)
- `jq` (recommended for JSON validation)

If additional Python packages are needed for parsing or validation, install them only in the repo-local `tooling/` environment using `uv`. Do not install globally.

Example:

```bash
cd tooling
uv add <package-name>
```

## Workflow

### Pass 1: Extract Page Text

Run:

```bash
pdftotext -layout "print-media/2022-cat-pages/page-XX.pdf" -
```

Preserve layout mode because column alignment is useful for parsing metadata labels and film blocks.

Normalize minimally:

- Strip trailing spaces.
- Keep line breaks.
- Keep original capitalization.

### Pass 2: Classify Page (`film_page` or `skip`)

Mark as `film_page` when at least two film metadata anchors exist:

- `Running Time`
- `Country` or `Countries`
- `Year`
- `Director`
- `Print Source`

Mark as `skip` when anchors are absent and text matches non-film patterns:

- Contents, intro pages, partners, juries, adverts, schedules, index.
- Very low text signal (blank/near-blank extraction).

Log every page decision.

### Pass 3: Choose Layout Parser

Use one parser per page.

Layout A (`feature_page`):

- Usually one film per page.
- Metadata labels in a right column (`Countries`, `Year`, `Running Time`, etc.).
- Main description paragraph(s) on the left.

Layout B (`shorts_grid_page`):

- Multiple films on one page.
- Repeated `Print Source` lines and repeated inline metadata strings containing `Running Time`.
- One block per short film.

### Pass 4: Segment Into Film Blocks

For `feature_page`:

- Extract one film block for the whole page.

For `shorts_grid_page`:

- Split by repeated title + `Print Source` pattern.
- Keep each block isolated before field parsing.

### Pass 5: Parse Fields Into Structured JSON

Emit this schema (omit absent fields):

```json
{
  "title": "Aftersun",
  "page": "page-10.pdf",
  "section": "Official Selection",
  "program": "International Short Film Competition",
  "countries": ["UK", "USA"],
  "year": 2022,
  "years": [2021, 2022],
  "runtime_minutes": 96,
  "languages": ["English", "German"],
  "directors": ["Charlotte Wells"],
  "screenwriters": ["July Jung"],
  "producers": ["Dong-ha Kim", "Ji-yeon Kim"],
  "cinematographers": ["Gregory Oke"],
  "editors": ["Blair McClendon"],
  "cast": ["Paul Mescal", "Frankie Corio"],
  "premiere_status": "UK",
  "original_title": "Die unsichtbare Grenze",
  "print_source": "MUBI",
  "description": "Main blurb text with paragraph breaks preserved.",
  "quote": {
    "text": "Quoted text from the page.",
    "credit": "Director Li Ruijun, from an interview with Screen Daily"
  },
  "notes": "Optional presenter note, ambiguity note, or unstructured remainder."
}
```

Rules:

- Parse `Country`/`Countries` into `countries` array.
- Parse year values from 4-digit tokens.
- Use `year` when exactly one 4-digit value exists.
- Use `years` when multiple years exist.
- Parse runtime into integer minutes (`2hr 14min` => `134`, `95min` => `95`).
- Parse language list into `languages`.
- Ignore subtitle metadata entirely (for example `with subtitles`); do not emit a `subtitles` field.
- Parse `Director`, `Screenwriter`, `Producer`, `Cinematographer`, `Editor`, and `Leading Cast`/`Key Cast` into arrays.
- Keep `section` from page heading; infer from page range only when heading is missing.
- Keep `program` for competition names (for example `International Short Film Competition`).
- Keep `description` as plain text only; preserve paragraph breaks where possible.
- Put only the main film blurb in `description`.
- When a page includes a standalone quote block, store it in `quote`.
- Use `quote.text` for the quote body text.
- Use `quote.credit` for the plain-text attribution exactly as shown (for example `Director Li Ruijun, from an interview with Screen Daily`).
- Keep quote text out of `description` to avoid mixing editorial voice and film blurb.
- Use `notes` to capture uncertainty or ambiguity (for example unclear names, uncertain segmentation).
- Prefix uncertainty notes with `UNCERTAIN:` so they can be found in a post-extraction review pass.

### Pass 6: Write Deterministic Filenames

Use:

- `page-XX-<slug>.json` for first film.
- `page-XX-<slug>-2.json`, `-3`, etc. for same-page duplicates.

Slug rules:

- Lowercase.
- Replace non-alphanumeric runs with `-`.
- Trim leading/trailing `-`.

### Pass 7: Sanity Checks

Run syntax checks:

```bash
jq empty intermediate-extract/2022/*.json
```

Run content checks and add failures to `review_queue.md`:

- Missing `title`, `section`, or `description`.
- `runtime_minutes` outside 1-400.
- Year values outside 1888-2100.
- Description still contains obvious metadata tokens like `Running Time`, `Director`, `Print Source`.
- Very short description (`<40` chars) unless clearly valid.
- If `quote` exists, ensure both `quote.text` and `quote.credit` are present.
- If `notes` contains `UNCERTAIN:`, add a matching item to `review_queue.md`.

### Pass 8: Log Outcome

Append one line per page to `extraction_log.md`:

- `- Page 010 - extracted Aftersun`
- `- Page 120 - extracted The Water Murmurs, Tremor, Tsutsue`
- `- Page 107 - skipped, jury page`

## Parallelization Pattern

Assign one worker per page PDF. Require each worker to output:

- Classification result (`extracted` or `skipped`).
- List of created JSON files.
- Any review-queue issues.

Avoid cross-page assumptions except for section-range fallback from `references/2022-patterns.md`.

## Batch Completion Checks

After all pages are processed:

- Confirm every `print-media/2022-cat-pages/page-*.pdf` has one log line.
- Confirm every extracted page has at least one JSON.
- Confirm no invalid JSON files (`jq empty`).
- Deduplicate accidental repeats by `(title, year, section)` and verify manually before deleting anything.
