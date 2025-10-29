# 2024 Film JSON to Markdown Conversion Summary

## Conversion Results
- **Total JSON files processed**: 131
- **Successfully converted**: 131 (100%)
- **Files created**: `/hugo/content/2024/*.md`

## Data Structure Mapping

### JSON Format (Original)
```json
{
    "title": "Film Title",
    "screenings": "Venue, Date Time",
    "info": "Director | Country | Year | Runtime | Language | Rating",
    "description": "Film description text",
    "strand": "Festival strand"
}
```

### Markdown Format (Converted)
```toml
+++
title = "Film Title"
director = "Director Name"
running-time = "120 mins"
production-year = "2024"
country = "Country List"
language = "Language"
premiere-status = "UK Premiere"
bbfc-rating = "15"
strand = "Festival strand"
screenings = "Venue, Date Time"
+++
Film description text
```

## Data Parsing Strategy

### Info Field Parsing
The JSON `info` field was parsed to extract structured metadata:
1. **Premiere Status**: Extracted from prefixes like "UK Premiere |" 
2. **Director**: First segment after status
3. **Country**: Second segment
4. **Production Year**: Third segment  
5. **Running Time**: Extracted from "X minutes" pattern
6. **Language**: Fifth segment, cleaned of subtitle references
7. **BBFC Rating**: Extracted from "BBFC Rating X" pattern

### Special Cases Handled
- **Short Film Collections**: Set director to "Various", year to "2024"
- **Running Time Only**: When info contains only "Approximate running time X minutes"
- **Premiere Status**: Properly extracted and separated from other metadata
- **Language Cleaning**: Removed "with English subtitles" suffix for cleaner language field

## Data Quality Analysis

### Missing Data Summary
- **Files missing director**: 8 (6.1%)
- **Files missing production year**: 3 (2.3%)
- **Files missing country**: 9 (6.9%)
- **Files missing language**: 28 (21.4%)
- **Short film collections**: 6 (4.6%)

### Additional Fields Added
Compared to 2025 format, the 2024 conversion includes:
- **`screenings`**: Preserved from original JSON (venue and time information)
- **`bbfc-rating`**: Extracted where available (not present in 2025 format)

### Fields Not Available in 2024 Data
Compared to 2025 format, the following fields were not available in 2024 JSON:
- **`courtesy-of`**: Not present in any 2024 JSON files

## File Naming
- Generated URL-friendly slugs from film titles
- Handled special characters and spacing
- Resolved duplicate names with numeric suffixes
- Examples:
  - "Bird" → `bird.md`
  - "A Real Pain" → `a-real-pain.md`
  - "We Joined A Cult" → `we-joined-a-cult.md`

## Conversion Quality
The conversion successfully preserved all original data while restructuring it into the Hugo markdown format used by the 2025 films. The additional `screenings` field provides value beyond the 2025 format, and missing data is clearly identified for potential manual review.