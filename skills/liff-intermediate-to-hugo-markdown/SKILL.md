---
name: liff-intermediate-to-hugo-markdown
description: "Convert LIFF intermediate extraction JSON into Hugo film markdown with deterministic field mapping, per-file conversion logging, uncertainty review notes, and build verification. Use for intermediate-extract/2022 to hugo/content/films/2022 and resume-safe reruns."
---

# LIFF Intermediate JSON to Hugo Markdown

## Overview

Convert each JSON file in `intermediate-extract/2022/` into one Hugo content file in `hugo/content/films/2022/`.

This skill is for the post-extraction phase after the PDF-to-JSON skill. It standardizes frontmatter, preserves useful metadata, writes a running conversion log, records uncertainties for review, and requires a final `make build` pass.

## Default Paths

- Input JSON: `intermediate-extract/2022/page-*.json`
- Output Markdown: `hugo/content/films/2022/*.md`
- Year index page: `hugo/content/films/2022/_index.md`
- Conversion log: `intermediate-extract/2022/hugo_conversion_log.md`
- Review queue: `intermediate-extract/2022/hugo_conversion_review.md`

## Dependencies and Tooling

The bundled script uses Python standard library only.

If additional packages are needed in future, install them only in the repo-local `tooling/` environment via `uv`:

```bash
cd tooling
uv add <package>
```

## Workflow

### 1. Audit Inputs

Count source files first:

```bash
find intermediate-extract/2022 -maxdepth 1 -name 'page-*.json' | wc -l
```

If count is `0`, stop and log the issue.

### 2. Run Conversion

Use the bundled script (deterministic and rerunnable):

```bash
python3 skills/liff-intermediate-to-hugo-markdown/scripts/convert_json_to_hugo.py \
  --input-dir intermediate-extract/2022 \
  --output-dir hugo/content/films/2022 \
  --index-title 2022 \
  --log-file intermediate-extract/2022/hugo_conversion_log.md \
  --review-file intermediate-extract/2022/hugo_conversion_review.md
```

Reruns replace previously generated markdown and rewrite log/review files so recovery is straightforward.

### 3. Mapping Rules

Read `references/field-mapping.md` for complete rules. Core mapping:

- `title` -> `title`
- `directors` -> `director` (comma-joined)
- `runtime_minutes` -> `running-time` (`"NN mins"`)
- `year` or `years` -> `production-year`
- `countries` -> `country`
- `languages` -> `language`
- `section` -> `strand`
- `program` -> `substrand`
- `description` or `synopsis` -> markdown body

Preserve additional useful keys (for example `screenwriter`, `producer`, `cast`, `premiere-status`, `original-title`, `print-source`, `notes`) when present.

Quote rendering rule:

- If source has `quote.text`, append it below the blurb as a markdown blockquote.
- If source has `quote.credit`, place it on the line immediately after the quote block.
- Pattern:
  - `blurb`
  - blank line
  - `> quote.text`
  - `quote.credit`

### 4. Running Log Requirements

`hugo_conversion_log.md` must contain:

- Total input count
- Total converted count
- One line per source JSON file with output filename
- Any slug-collision suffixing decisions (`-2`, `-3`, ...)

### 5. Uncertainty and Review Requirements

`hugo_conversion_review.md` must include every uncertainty, including:

- Source `notes` containing `UNCERTAIN:`
- Missing `title` or empty body
- Parse errors or malformed fields
- Any dropped/ambiguous mapping decisions

Do not silently discard ambiguous data.

### 6. Quality Review Phase

Run all checks after conversion:

```bash
# Count parity (excluding _index.md)
json_count=$(find intermediate-extract/2022 -maxdepth 1 -name 'page-*.json' | wc -l)
md_count=$(find hugo/content/films/2022 -maxdepth 1 -name '*.md' ! -name '_index.md' | wc -l)
printf "json=%s md=%s\n" "$json_count" "$md_count"

# Basic frontmatter presence
for f in hugo/content/films/2022/*.md; do
  head -n 1 "$f" | grep -q '^+++\s*$' || echo "missing-frontmatter-start: $f"
  grep -q '^+++\s*$' "$f" || echo "missing-frontmatter-delimiter: $f"
done
```

Then run the required final test:

```bash
make build
```

Conversion is only complete when `make build` succeeds.

## Resume Pattern

To resume after interruption:

1. Re-run the conversion command above.
2. Re-run quality checks.
3. Confirm `make build` still passes.

Because outputs are deterministic, rerun-and-replace is preferred over partial manual patching.
