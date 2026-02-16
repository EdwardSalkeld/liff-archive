Use `$liff-catalog-pdf-extraction` and continue extracting LIFF 2022 catalog data from `print-media/2022-cat-pages`.

Resume behavior:
1. Read `intermediate-extract/2022/extraction_log.md` and detect already-processed pages.
2. Continue from the next unprocessed page (or only process this range: `[PAGE_RANGE_HERE]`).
3. If re-running a page, replace prior outputs for that page.

For each processed page:
- Cache raw text at `intermediate-extract/2022/raw-text/page-XX.txt`
- Write one JSON per film to `intermediate-extract/2022/page-XX-<slug>.json`
- Update `intermediate-extract/2022/extraction_log.md`
- Add any uncertainty items to `intermediate-extract/2022/review_queue.md`

Extraction rules to enforce:
- Include `description` (main blurb, preserve paragraph breaks)
- Include optional `quote` object with `text` + `credit` when present
- Include optional `cinematographers` and `editors` when present
- Ignore subtitle metadata entirely (do not create `subtitles`, do not log subtitle uncertainty)
- Use `notes` with `UNCERTAIN:` prefix only for real ambiguities
- Validate new JSON files with `jq`

At the end, report:
- Pages processed (extracted/skipped)
- JSON files created
- Any `UNCERTAIN:`/review items
