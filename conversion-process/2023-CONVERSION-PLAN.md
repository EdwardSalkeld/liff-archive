# 2023 JSON -> Hugo Markdown Conversion Plan

Goal: Convert every JSON file in `intermediate-extract/2023/` into a Hugo content file under `hugo/content/films/2023/` that matches the 2024 frontmatter/body structure (TOML `+++` frontmatter, synopsis as body).

## Step 1: Audit inputs and expected outputs
Status: completed
1. List the JSON source files in `intermediate-extract/2023/` and count them to set a conversion target (expected number of Markdown files).
2. Open 3–5 representative JSON files to confirm field variations:
   - Feature film entries with `directors`, `year`, `certification`, `subtitles`.
   - Shorts/competition entries with `years` array and no `directors`.
   - Entries with `notes` and/or `program` fields.
3. Open 3–5 2024 Markdown files to lock in the output shape and formatting:
   - Standard feature with all fields.
   - Shorts program (often no director/language).
   - Example with `bbfc-rating` and `premiere-status` if present.

## Step 2: Define field mapping rules
Status: completed
4. Map JSON fields to Hugo frontmatter keys (omit keys when data is missing):
   - `title` -> `title` (string as-is).
   - `directors` -> `director` (join with ", ").
   - `countries` -> `country` (join with ", ").
   - `year` or `years` -> `production-year`.
     - If `year` is present, use it.
     - If only `years` array exists, use the max year as a single value.
   - `runtime_minutes` -> `running-time` formatted as `"NN mins"`.
     - If `runtime_notes` is `"approx"`, append `" (approx)"` to `running-time`.
     - If `runtime_notes` is a sentence, consider appending it to the synopsis instead of the frontmatter.
   - `languages` -> `language` (join with ", ").
   - `section`/`program` -> `strand`.
     - If `program` exists, use it; else use `section`.
   - `certification` -> `bbfc-rating`.
     - Extract the rating from strings like `"BBFC Cert U"` -> `"U"`.
   - `venue_screenings` + optional `notes` -> `screenings` (see step 3).
   - `presenter` -> optionally add `presenter` frontmatter or append to synopsis if a new field is not desired.
   - `synopsis` -> Markdown body (plain text paragraph).
5. Decide how to handle `subtitles`:
   - Default to omitting it from frontmatter to match 2024 output.
   - If preserving is desired, add `subtitles = "English"` as an optional field, but only if required by stakeholders.

## Step 3: Define screening string formatting
Status: completed
6. Build a deterministic format that mirrors 2024:
   - Group screenings by `venue`.
   - Preserve venue group ordering based on first appearance in the JSON list.
   - For each venue group, format entries as:
     - `Venue, Date Time` for the first entry.
     - Additional entries at the same venue appended as ` & Date Time`.
     - Example: `Vue Screen 12, Sat 4 Nov 20:00 & Mon 6 Nov 18:15`.
   - Join multiple venue groups with ` | `.
7. Merge `notes` into `screenings`:
   - If `notes` exists, trim trailing punctuation.
   - Append as a final segment separated by ` | `.
   - Normalize “Free …” to `FREE …` to match 2024 style (e.g., `"Free at Chapel FM."` -> `| FREE at Chapel FM`, `"Free screening."` -> `| FREE`).

## Step 4: File naming and directory structure
Status: completed
8. Ensure `hugo/content/films/2023/_index.md` exists with:
   ```
   +++
   title = "2023"
   +++
   ```
9. Derive each output filename (slug) from the JSON filename suffix:
   - `page-10-anatomy-of-a-fall.json` -> `anatomy-of-a-fall.md`.
   - This matches existing slugging in the 2023 intermediate extract.
10. Detect collisions (same slug appearing twice) and append `-2`, `-3`, etc. to the later duplicates, matching the 2024 approach.

## Step 5: Implement the conversion script
Status: completed
11. Pick a scripting environment (Node or Python) already in the repo:
    - Read all JSON files under `intermediate-extract/2023/`.
    - Parse and map fields using rules above.
    - Render TOML frontmatter with `+++` delimiters.
    - Write files to `hugo/content/films/2023/`.
12. Ensure the script preserves ASCII-only output where possible (titles/bodies may include Unicode if present in source).

## Step 6: Validate output parity and spot-checks
Status: completed
13. Verify count parity: number of Markdown files equals JSON input count (+ `_index.md`).
14. Spot-check at least 6 files:
    - 3 feature films with directors/languages.
    - 2 shorts programs with `years` arrays.
    - 1 entry with `notes` and `certification`.
15. Confirm frontmatter ordering aligns with 2024 style (title first; other fields in a sensible, stable order).

## Step 7: Log exceptions for manual review
Status: completed
16. Generate a report of any missing or ambiguous fields:
    - Missing `countries`, `languages`, `runtime_minutes`, or `synopsis`.
    - Any unparsed `certification` values.
17. Record any slug collisions and the chosen resolution.
18. If any JSON fields don’t map cleanly, document the decision and the affected titles for follow-up.

## Step 8: Finish and handoff
Status: completed
19. Summarize total converted files, exceptions, and any manual follow-ups in a short conversion summary (optional but recommended to mirror `CONVERSION_SUMMARY.md`).
20. If requested, provide the conversion script path and usage so it can be rerun or adjusted later.
