# 2022 Catalog Patterns

Use this file when extracting from `print-media/2022-cat-pages`.

## Section Fallback by Page Range

Use heading text first. Use this range table only when heading text is missing or noisy.

- Pages 8-51: `Official Selection`
- Pages 52-77: `Cinema Versa`
- Pages 78-105: `Fanomenon`
- Pages 106-150: `Leeds Short Film Awards`
- Pages 151-163: `LIFF 2022 Spotlights: Films Femmes Afrique`
- Pages 164-175: `LIFF 2022 Spotlights: Disability Futures`
- Pages 176-187: `LIFF 2022 Spotlights: One Love from Jamaica`
- Pages 188-192: `Index` (normally skip)

## Strong Skip Indicators

If these dominate the page and film metadata anchors are absent, classify as `skip`:

- `Contents`
- `Partners`
- `Presented by`
- `Jury`
- `Index`
- `Introduction`
- Page has only section title with page number and no film metadata

## Film Metadata Anchors

Treat a page as likely film-bearing when at least two anchors are present:

- `Running Time`
- `Country` or `Countries`
- `Year`
- `Director`
- `Print Source`

## Common Layouts

### Layout A: Single Feature

Typical signals:

- One large title.
- Right-column labels (`Countries`, `Year`, `Running Time`, `Languages`, etc.).
- Long synopsis paragraph on left.

Common page examples:

- `page-10.pdf`
- `page-34.pdf`
- `page-40.pdf`

### Layout B: Multi Short-Film Page

Typical signals:

- Competition/program heading near top.
- Repeated title + `Print Source` blocks.
- Inline metadata text including `Running Time`.

Common page examples:

- `page-116.pdf`
- `page-120.pdf`
- `page-130.pdf`
- `page-146.pdf`

## Parsing Notes

Runtime parsing:

- `2hr 14min` -> `134`
- `2hr` -> `120`
- `95min` / `95 Minutes` -> `95`

Year parsing:

- One year token -> `year`
- Multiple year tokens -> `years` array

Language parsing:

- Keep language names only in `languages`
- Move subtitle info to `subtitles`

Cast parsing:

- Map both `Leading Cast` and `Key Cast` to `cast`

Crew parsing:

- Map `Cinematographer` to `cinematographers`
- Map `Editor` to `editors`

Description parsing:

- Capture the main film blurb as `description`
- Preserve paragraph breaks where possible
- Exclude director interview quotes from `description`; place them in `notes` when retained
