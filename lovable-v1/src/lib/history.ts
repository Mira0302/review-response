export interface HistoryEntry {
  id: string;
  title: string;
  journal: string;
  date: string;
  language: string;
  reviewCount: number;
  status: "完成" | "草稿";
  paper: string;
  review: string;
  responseLetter: string;
  changeTable: string;
  reviewPoints: string;
  createdAt: number;
}

const STORAGE_KEY = "rr_history";

export function loadHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const data = JSON.parse(raw);
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

function saveHistory(entries: HistoryEntry[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries.slice(0, 50)));
}

export function addHistory(entry: Omit<HistoryEntry, "id" | "createdAt" | "status" | "journal"> & { journal?: string }): HistoryEntry {
  const entries = loadHistory();
  const newEntry: HistoryEntry = {
    ...entry,
    id: crypto.randomUUID?.() ?? Math.random().toString(36).slice(2, 10),
    status: "完成",
    journal: entry.journal || "—",
    createdAt: Date.now(),
  };
  entries.unshift(newEntry);
  saveHistory(entries);
  return newEntry;
}

export function removeHistory(id: string): void {
  const entries = loadHistory().filter((e) => e.id !== id);
  saveHistory(entries);
}

export function clearHistory(): void {
  localStorage.removeItem(STORAGE_KEY);
}
