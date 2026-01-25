# 2023 Film JSON to Markdown Conversion Summary

## Conversion Results
- **Total JSON files processed**: 130
- **Successfully converted**: 130 (100%)
- **Files created**: `hugo/content/films/2023/*.md` plus `hugo/content/films/2023/_index.md`

## Source Data Notes
- Input JSONs live in `intermediate-extract/2023/`.
- Field variability includes: `year` vs `years`, optional `directors`, `certification` strings, `notes`, `runtime_notes`, and occasional `presenter`.

## Markdown Output Shape
```toml
+++
title = "Film Title"
director = "Director A, Director B"
running-time = "90 mins"
production-year = "2023"
country = "Country A, Country B"
language = "Language A, Language B"
subtitles = "English"
presenter = "Presenter Name"
strand = "Program / Section"
bbfc-rating = "15"
notes = "Additional notes"
runtime-notes = "Additional runtime context"
screenings = "Venue, Date Time & Date Time | Other Venue, Date Time | FREE"
+++
Synopsis text...
```

## Key Mapping Rules
- `directors` -> `director` (comma-joined).
- `countries` -> `country` (comma-joined).
- `languages` -> `language` (comma-joined).
- `year` or `years` -> `production-year` (max of `years` when only array exists).
- `runtime_minutes` -> `running-time` (append `(approx)` when `runtime_notes` is `"approx"`).
- `section` / `program` -> `strand` (prefer `program`).
- `certification` -> `bbfc-rating` (normalized from `Cert`/`BBFC Certificate` variants).
- `venue_screenings` -> `screenings` (grouped by venue with `&`, venues separated by ` | `; `notes` starting with “Free” become `FREE` segments).
- `subtitles`, `presenter`, `notes`, and `runtime-notes` are preserved as extra frontmatter fields when present.

## Exceptions / Missing Data
Counts from source JSON:
- Missing `countries`: 1
- Missing `languages`: 2
- Missing `directors`: 20
- Missing `year`: 19
- Missing `venue_screenings`: 5

## Script
- Conversion script: `workbench/convert-2023.js`
- Run: `node workbench/convert-2023.js`
