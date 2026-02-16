#!/usr/bin/env python3
"""Convert LIFF intermediate JSON files into Hugo markdown files."""

from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any


def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def to_kebab(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", name)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned.lower().replace("_", "-")


def join_list(values: Any) -> str | None:
    if not isinstance(values, list) or not values:
        return None
    if all(isinstance(v, (str, int, float, bool)) for v in values):
        return ", ".join(str(v) for v in values)
    return json.dumps(values, ensure_ascii=False)


def derive_year(data: dict[str, Any]) -> str | None:
    year = data.get("year")
    if isinstance(year, int):
        return str(year)
    years = data.get("years")
    if isinstance(years, list) and years:
        ints = [y for y in years if isinstance(y, int)]
        if ints:
            return str(max(ints))
    return None


def parse_bbfc(certification: Any) -> str | None:
    if not isinstance(certification, str) or not certification.strip():
        return None
    match = re.search(r"(?:BBFC\s+)?Cert(?:ificate)?\s*([A-Z0-9]+)", certification, re.I)
    if match:
        return match.group(1).upper()
    return None


def normalize_free_note(note: Any) -> str | None:
    if not isinstance(note, str):
        return None
    trimmed = note.strip().rstrip(".")
    lower = trimmed.lower()
    if not lower.startswith("free"):
        return None
    if lower == "free screening":
        return "FREE"
    if lower.startswith("free screening"):
        return "FREE" + trimmed[len("free screening") :]
    if lower.startswith("free at "):
        return "FREE at " + trimmed[len("free at ") :]
    if lower.startswith("free "):
        return "FREE " + trimmed[len("free ") :]
    return "FREE"


def build_screenings(data: dict[str, Any]) -> str | None:
    venue_screenings = data.get("venue_screenings")
    parts: list[str] = []

    if isinstance(venue_screenings, list):
        grouped: OrderedDict[str, list[str]] = OrderedDict()
        for item in venue_screenings:
            if not isinstance(item, dict):
                continue
            venue = str(item.get("venue", "")).strip()
            if not venue:
                continue
            date_text = str(item.get("date_text", "")).strip()
            time = str(item.get("time", "")).strip()
            when = (date_text + " " + time).strip()
            if venue not in grouped:
                grouped[venue] = []
            if when:
                grouped[venue].append(when)

        for venue, whens in grouped.items():
            if not whens:
                parts.append(venue)
                continue
            formatted = f"{venue}, {whens[0]}"
            if len(whens) > 1:
                formatted += "".join(f" & {w}" for w in whens[1:])
            parts.append(formatted)

    free_note = normalize_free_note(data.get("notes"))
    if free_note:
        parts.append(free_note)

    if not parts:
        return None
    return " | ".join(parts)


def slug_from_json_name(filename: str) -> str:
    slug = re.sub(r"^page-\d+-", "", filename)
    slug = re.sub(r"\.json$", "", slug)
    return slug


def format_quote_block(text: str) -> str:
    lines = text.strip().splitlines()
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            out.append(f"> {stripped}")
        else:
            out.append(">")
    return "\n".join(out)


def convert_one(data: dict[str, Any], source_filename: str) -> tuple[str, str, list[str]]:
    review_items: list[str] = []

    running_time = None
    runtime_minutes = data.get("runtime_minutes")
    if isinstance(runtime_minutes, int) and runtime_minutes > 0:
        running_time = f"{runtime_minutes} mins"
        if data.get("runtime_notes") == "approx":
            running_time += " (approx)"

    notes_value = data.get("notes")
    notes_field = None
    if isinstance(notes_value, str) and notes_value.strip() and not normalize_free_note(notes_value):
        notes_field = notes_value.strip()

    quote = data.get("quote") if isinstance(data.get("quote"), dict) else {}
    quote_text = quote.get("text") if isinstance(quote, dict) else None
    quote_credit = quote.get("credit") if isinstance(quote, dict) else None

    mapped: OrderedDict[str, str] = OrderedDict()
    mapped["title"] = str(data.get("title", "")).strip()
    mapped["director"] = join_list(data.get("directors")) or ""
    mapped["running-time"] = running_time or ""
    mapped["production-year"] = derive_year(data) or ""
    mapped["country"] = join_list(data.get("countries")) or ""
    mapped["language"] = join_list(data.get("languages")) or ""
    mapped["subtitles"] = str(data.get("subtitles", "")).strip()
    mapped["premiere-status"] = str(data.get("premiere_status", "")).strip()
    mapped["strand"] = str(data.get("section", "")).strip()
    mapped["substrand"] = str(data.get("program", "")).strip()
    mapped["original-title"] = str(data.get("original_title", "")).strip()
    mapped["screenwriter"] = join_list(data.get("screenwriters")) or ""
    mapped["producer"] = join_list(data.get("producers")) or ""
    mapped["cinematographer"] = join_list(data.get("cinematographers")) or ""
    mapped["editor"] = join_list(data.get("editors")) or ""
    mapped["cast"] = join_list(data.get("cast")) or ""
    mapped["print-source"] = str(data.get("print_source", "")).strip()
    mapped["page-source"] = str(data.get("page", "")).strip()
    mapped["bbfc-rating"] = parse_bbfc(data.get("certification")) or ""
    mapped["presenter"] = str(data.get("presenter", "")).strip()
    mapped["notes"] = notes_field or ""
    mapped["runtime-notes"] = (
        str(data.get("runtime_notes", "")).strip()
        if data.get("runtime_notes") not in (None, "", "approx")
        else ""
    )
    mapped["screenings"] = build_screenings(data) or ""
    body = ""
    if isinstance(data.get("description"), str) and data["description"].strip():
        body = data["description"].strip()
    elif isinstance(data.get("synopsis"), str) and data["synopsis"].strip():
        body = data["synopsis"].strip()

    quote_text_value = str(quote_text).strip() if isinstance(quote_text, str) else ""
    quote_credit_value = str(quote_credit).strip() if isinstance(quote_credit, str) else ""
    if quote_text_value:
        quote_block = format_quote_block(quote_text_value)
        if body:
            body = f"{body}\n\n{quote_block}"
        else:
            body = quote_block
        if quote_credit_value:
            body = f"{body}\n{quote_credit_value}"
    elif quote_credit_value:
        body = f"{body}\n\n{quote_credit_value}" if body else quote_credit_value

    handled = {
        "title",
        "directors",
        "runtime_minutes",
        "runtime_notes",
        "year",
        "years",
        "countries",
        "languages",
        "subtitles",
        "premiere_status",
        "section",
        "program",
        "original_title",
        "screenwriters",
        "producers",
        "cinematographers",
        "editors",
        "cast",
        "print_source",
        "page",
        "certification",
        "presenter",
        "notes",
        "venue_screenings",
        "quote",
        "description",
        "synopsis",
    }

    extras: dict[str, str] = {}
    for key, value in data.items():
        if key in handled:
            continue
        out_key = to_kebab(key)
        if not out_key:
            continue
        if isinstance(value, list):
            out_val = join_list(value)
        elif isinstance(value, dict):
            out_val = json.dumps(value, ensure_ascii=False)
        elif value is None:
            out_val = None
        else:
            out_val = str(value).strip()
        if out_val:
            extras[out_key] = out_val

    if not mapped["title"]:
        review_items.append(f"{source_filename}: missing title")
    if not body:
        review_items.append(f"{source_filename}: missing description/synopsis body")

    if isinstance(notes_value, str) and "UNCERTAIN:" in notes_value:
        review_items.append(f"{source_filename}: {notes_value.strip()}")

    lines = ["+++"]
    for key, value in mapped.items():
        if not value:
            continue
        lines.append(f'{key} = "{toml_escape(value)}"')
    for key in sorted(extras):
        lines.append(f'{key} = "{toml_escape(extras[key])}"')
    lines.append("+++")

    markdown = "\n".join(lines) + "\n"
    markdown += body + "\n"
    return mapped["title"], markdown, review_items


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert intermediate JSON to Hugo markdown")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--index-title", required=True)
    parser.add_argument("--log-file", required=True)
    parser.add_argument("--review-file", required=True)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    log_file = Path(args.log_file)
    review_file = Path(args.review_file)

    output_dir.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    review_file.parent.mkdir(parents=True, exist_ok=True)

    source_files = sorted(input_dir.glob("page-*.json"))

    slug_seen: defaultdict[str, int] = defaultdict(int)
    log_lines: list[str] = ["# Hugo Conversion Log", ""]
    review_lines: list[str] = ["# Hugo Conversion Review Queue", ""]

    converted = 0
    for src in source_files:
        raw = src.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            review_lines.append(f"- {src.name}: JSON parse error: {exc}")
            continue

        base_slug = slug_from_json_name(src.name)
        slug_seen[base_slug] += 1
        suffix = slug_seen[base_slug]
        out_slug = base_slug if suffix == 1 else f"{base_slug}-{suffix}"
        out_name = f"{out_slug}.md"

        title, markdown, issues = convert_one(data, src.name)
        out_path = output_dir / out_name
        out_path.write_text(markdown, encoding="utf-8")

        converted += 1
        if suffix == 1:
            log_lines.append(f"- {src.name} -> {out_name} ({title})")
        else:
            log_lines.append(
                f"- {src.name} -> {out_name} ({title}) [slug collision with {base_slug}]"
            )
            review_lines.append(
                f"- {src.name}: slug collision on '{base_slug}', wrote '{out_name}'."
            )

        for item in issues:
            review_lines.append(f"- {item}")

    index_content = f"+++\ntitle = \"{toml_escape(args.index_title)}\"\n+++\n"
    (output_dir / "_index.md").write_text(index_content, encoding="utf-8")

    log_lines.insert(2, f"- Input files: {len(source_files)}")
    log_lines.insert(3, f"- Converted files: {converted}")
    log_file.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    if len(review_lines) == 2:
        review_lines.append("- None")
    review_file.write_text("\n".join(review_lines) + "\n", encoding="utf-8")

    print(f"Converted {converted} files from {input_dir} to {output_dir}")
    print(f"Wrote log: {log_file}")
    print(f"Wrote review: {review_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
