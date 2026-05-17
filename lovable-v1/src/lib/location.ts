const LOCATION_PATTERNS: [RegExp, string][] = [
  [/Section\s+(\d[\d.]*)/gi, "Section "],
  [/Page\s+(\d+)/gi, "Page "],
  [/Figure\s+(\d[\da-zA-Z]*)/gi, "Figure "],
  [/Table\s+(\d[\da-zA-Z]*)/gi, "Table "],
  [/Chapter\s+(\d[\da-zA-Z]*)/gi, "Chapter "],
  [/第\s*(\d[\d.]*)\s*节/gi, "第"],
  [/第\s*(\d+)\s*页/gi, "第"],
  [/第\s*(\d+)\s*段/gi, "第"],
  [/图\s*(\d[\da-zA-Z]*)/gi, "图"],
  [/表\s*(\d[\da-zA-Z]*)/gi, "表"],
  [/(?:§|Section\s*)(\d+\.?\d*)/gi, "§"],
  [/(?:p\.|page\s*)(\d+)/gi, "p."],
  [/\b(Table\s*\d[\da-zA-Z]*)/gi, ""],
  [/\b(Figure\s*\d[\da-zA-Z]*)/gi, ""],
];

export interface LocatedItem {
  location: string;
  index: number;
}

export function extractLocations(text: string): string[] {
  const seen = new Set<string>();
  const results: string[] = [];
  for (const [pattern] of LOCATION_PATTERNS) {
    pattern.lastIndex = 0;
    let match: RegExpExecArray | null;
    while ((match = pattern.exec(text)) !== null) {
      const loc = match[0].trim();
      const normalized = loc.toLowerCase().replace(/\s+/g, " ");
      if (!seen.has(normalized)) {
        seen.add(normalized);
        results.push(loc);
      }
    }
  }
  return results.slice(0, 30);
}

export function filterValidLocations(locations: string[], paper: string): LocatedItem[] {
  const results: LocatedItem[] = [];
  const normalized = paper.toLowerCase();

  for (const loc of locations) {
    const clean = loc.toLowerCase().replace(/\s+/g, " ").replace(/[§]/g, "");
    const idx = normalized.indexOf(clean);
    if (idx !== -1) {
      results.push({ location: loc, index: idx });
    } else {
      // Try partial match — extract number
      const numMatch = clean.match(/(\d[\d.]*)/);
      if (numMatch) {
        const num = numMatch[1];
        const numIdx = normalized.indexOf(num);
        if (numIdx !== -1) {
          results.push({ location: loc, index: numIdx });
        }
      }
    }
  }
  return results;
}

export function findInPaper(location: string, paper: string): number {
  const clean = location.toLowerCase().replace(/\s+/g, " ").replace(/[§]/g, "");
  const normalized = paper.toLowerCase();

  // Direct match
  const idx = normalized.indexOf(clean);
  if (idx !== -1) return idx;

  // Number-only match
  const numMatch = clean.match(/(\d[\d.]*)/);
  if (numMatch) {
    const numIdx = normalized.indexOf(numMatch[1]);
    if (numIdx !== -1) return numIdx;
  }

  return -1;
}
