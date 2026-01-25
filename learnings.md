Step 1 notes:
- `intermediate-extract/2023/` contains 130 JSON files.
- JSON entries vary: some use `year`, others `years` arrays; `directors` can be missing; `certification` appears as strings like "BBFC Cert U"; `notes` appears (e.g., free screenings).
- 2024 Hugo files use TOML frontmatter with `+++` delimiters and a single-paragraph synopsis body.

Step 2 notes:
- Some JSON entries include `program` (often a sub-strand label) alongside `section`.
- `runtime_notes` appears (`"approx"` or a full sentence), which may need special handling in `running-time` or synopsis.
- `presenter` appears at least once (`Nature Matters`), so decide whether to preserve it as frontmatter or fold into synopsis.

Step 3 notes:
- 2024 screening strings group times by venue using `&`, then separate venues with ` | `; FREE notices appear as their own ` | FREE` segment.
- Preserve venue ordering based on first appearance in `venue_screenings` when grouping.

Step 4 notes:
- No duplicate slugs found after stripping `page-XX-` prefixes in `intermediate-extract/2023/`.
- Created `hugo/content/films/2023/_index.md` with title "2023".

Step 5 notes:
- Added conversion script at `workbench/convert-2023.js`.
- Script writes TOML frontmatter, preserves optional fields like `subtitles`, `presenter`, `notes`, and `runtime-notes`, and normalizes FREE notes into `screenings`.

Step 6 notes:
- Ran `node workbench/convert-2023.js` and generated 130 Markdown files in `hugo/content/films/2023/` plus `_index.md` (total 131).
- Spot checks look consistent with expected formatting, including FREE notes, BBFC ratings, and runtime notes.

Step 7 notes:
- Missing fields (counts): `countries` 1, `languages` 2, `directors` 20, `year` 19, `venue_screenings` 5.
- Nonstandard certification values found: `page-19-this-is-going-to-be-big.json` ("Cert PG"), `page-30-yorkshire-short-film-competition.json` ("Cert 15"), `page-44-the-zone-of-interest.json` ("BBFC Certificate 12A").

Step 8 notes:
- Updated cert parsing in `workbench/convert-2023.js` to normalize `Cert`/`BBFC Certificate` variants to clean ratings (e.g., `PG`, `15`, `12A`).
