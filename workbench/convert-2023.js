const fs = require('fs');
const path = require('path');

const inputDir = path.join(__dirname, '..', 'intermediate-extract', '2023');
const outputDir = path.join(__dirname, '..', 'hugo', 'content', 'films', '2023');

function tomlEscape(value) {
  return String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

function normalizeFreeNote(note) {
  if (!note) return null;
  const trimmed = note.trim().replace(/[.]+$/, '');
  const lower = trimmed.toLowerCase();
  if (!lower.startsWith('free')) return null;
  if (lower === 'free screening') return 'FREE';
  if (lower.startsWith('free screening')) {
    return 'FREE' + trimmed.slice('free screening'.length);
  }
  if (lower.startsWith('free at ')) {
    return 'FREE at ' + trimmed.slice('free at '.length);
  }
  if (lower.startsWith('free ')) {
    return 'FREE ' + trimmed.slice('free '.length);
  }
  return 'FREE';
}

function buildScreenings(venueScreenings, notes) {
  const byVenue = new Map();
  const order = [];

  (venueScreenings || []).forEach((entry) => {
    const venue = entry.venue || '';
    if (!venue) return;
    if (!byVenue.has(venue)) {
      byVenue.set(venue, []);
      order.push(venue);
    }
    const dateTime = `${entry.date_text || ''} ${entry.time || ''}`.trim();
    if (dateTime) {
      byVenue.get(venue).push(dateTime);
    }
  });

  const venueParts = order.map((venue) => {
    const times = byVenue.get(venue) || [];
    if (times.length === 0) return venue;
    return `${venue}, ${times[0]}${times.slice(1).map((t) => ` & ${t}`).join('')}`;
  });

  const freeNote = normalizeFreeNote(notes);
  if (freeNote) {
    venueParts.push(freeNote);
  }

  return venueParts.join(' | ');
}

function parseBbfc(certification) {
  if (!certification) return null;
  const match = certification.match(/(?:BBFC\s+)?Cert(?:ificate)?\s*([A-Z0-9]+)/i);
  if (match) return match[1].toUpperCase();
  return null;
}

function joinList(values) {
  if (!Array.isArray(values) || values.length === 0) return null;
  return values.join(', ');
}

function deriveProductionYear(data) {
  if (data.year) return String(data.year);
  if (Array.isArray(data.years) && data.years.length > 0) {
    return String(Math.max(...data.years));
  }
  return null;
}

function slugFromFilename(filename) {
  return filename.replace(/^page-\d+-/, '').replace(/\.json$/, '');
}

function buildFrontmatter(data, screenings, notesField) {
  const director = joinList(data.directors);
  const country = joinList(data.countries);
  const language = joinList(data.languages);
  const productionYear = deriveProductionYear(data);
  const runningTimeBase = data.runtime_minutes ? `${data.runtime_minutes} mins` : null;
  const runningTime = runningTimeBase && data.runtime_notes === 'approx'
    ? `${runningTimeBase} (approx)`
    : runningTimeBase;
  const strand = data.program || data.section || null;
  const bbfcRating = parseBbfc(data.certification);
  const subtitles = data.subtitles || null;
  const presenter = data.presenter || null;
  const runtimeNotes = data.runtime_notes && data.runtime_notes !== 'approx'
    ? data.runtime_notes
    : null;

  const fields = [
    ['title', data.title],
    ['director', director],
    ['running-time', runningTime],
    ['production-year', productionYear],
    ['country', country],
    ['language', language],
    ['subtitles', subtitles],
    ['presenter', presenter],
    ['strand', strand],
    ['bbfc-rating', bbfcRating],
    ['notes', notesField],
    ['runtime-notes', runtimeNotes],
    ['screenings', screenings]
  ];

  const lines = ['+++'];
  fields.forEach(([key, value]) => {
    if (value === null || value === undefined || value === '') return;
    lines.push(`${key} = "${tomlEscape(value)}"`);
  });
  lines.push('+++');
  return lines.join('\n');
}

function main() {
  fs.mkdirSync(outputDir, { recursive: true });

  const files = fs.readdirSync(inputDir).filter((file) => file.endsWith('.json')).sort();
  const slugCounts = new Map();

  files.forEach((file) => {
    const inputPath = path.join(inputDir, file);
    const raw = fs.readFileSync(inputPath, 'utf8');
    const data = JSON.parse(raw);

    let slug = slugFromFilename(file);
    const count = (slugCounts.get(slug) || 0) + 1;
    slugCounts.set(slug, count);
    if (count > 1) {
      slug = `${slug}-${count}`;
    }

    const notesField = data.notes && !normalizeFreeNote(data.notes)
      ? data.notes.trim()
      : null;
    const screenings = buildScreenings(data.venue_screenings, data.notes);
    const frontmatter = buildFrontmatter(data, screenings, notesField);
    const synopsis = (data.synopsis || '').trim();

    const output = `${frontmatter}\n${synopsis}\n`;
    const outputPath = path.join(outputDir, `${slug}.md`);
    fs.writeFileSync(outputPath, output, 'utf8');
  });

  console.log(`Converted ${files.length} JSON files into ${outputDir}`);
}

main();
