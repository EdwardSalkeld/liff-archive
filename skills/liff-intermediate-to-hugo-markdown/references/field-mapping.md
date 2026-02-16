# Field Mapping Reference

Use this when converting `intermediate-extract/2022/*.json` to Hugo markdown.

## Output Shape

```toml
+++
title = "Film Title"
director = "Director A, Director B"
running-time = "96 mins"
production-year = "2022"
country = "UK, USA"
language = "English"
strand = "Official Selection"
substrand = "Program Name"
...optional keys...
+++
Body text from description/synopsis.
```

## Core Mapping

- `title` -> `title`
- `directors` -> `director` (join with `, `)
- `runtime_minutes` -> `running-time` (`NN mins`)
- `year` -> `production-year`
- `years` -> `production-year` (max year if `year` absent)
- `countries` -> `country` (join with `, `)
- `languages` -> `language` (join with `, `)
- `section` -> `strand`
- `program` -> `substrand`
- `description` or `synopsis` -> markdown body

## Additional Keys to Preserve

Prefer preserving these as frontmatter when present:

- `subtitles` -> `subtitles`
- `premiere_status` -> `premiere-status`
- `original_title` -> `original-title`
- `screenwriters` -> `screenwriter`
- `producers` -> `producer`
- `cinematographers` -> `cinematographer`
- `editors` -> `editor`
- `cast` -> `cast`
- `print_source` -> `print-source`
- `quote.text` -> `quote`
- `quote.credit` -> `quote-credit`
- `notes` -> `notes`
- `page` -> `page-source`

For unknown keys, convert snake_case to kebab-case and preserve if safely serializable.

## Screenings Formatting (if present)

If `venue_screenings` exists:

- Group by venue in first-seen order.
- First entry: `Venue, Date Time`
- Additional entries at same venue: ` & Date Time`
- Separate venues by ` | `
- If `notes` starts with `Free`, append ` | FREE` or ` | FREE at ...`

Example:

`Vue Screen 12, Sat 4 Nov 20:00 & Mon 6 Nov 18:15 | Cottage Road, Tue 7 Nov 13:00 | FREE at Stockroom Cinema`

## Slug and Filename

- Source `page-10-aftersun.json` -> `aftersun.md`
- On collision, append suffix to later files: `aftersun-2.md`, `aftersun-3.md`

## Uncertainty Rules

Add to review queue when:

- Source `notes` contains `UNCERTAIN:`
- Required content is missing (`title`, body)
- Ambiguous metadata cannot be mapped safely
