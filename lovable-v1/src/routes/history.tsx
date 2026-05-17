import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { AppLayout, TopBar, Btn, Chip } from "@/components/rr/AppLayout";
import { loadHistory, removeHistory, type HistoryEntry } from "@/lib/history";
import type { ResultData } from "@/routes/workspace.index";

export const Route = createFileRoute("/history")({ component: History });

function History() {
  const [entries, setEntries] = useState<HistoryEntry[]>(() => loadHistory());
  const [filter, setFilter] = useState("全部");
  const [search, setSearch] = useState("");

  const filtered = entries.filter((e) => {
    if (filter !== "全部" && e.status !== filter) return false;
    if (search && !e.title.toLowerCase().includes(search.toLowerCase()) && !e.journal.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const openResult = (entry: HistoryEntry) => {
    // Reconstruct ResultData and store in sessionStorage
    const result: ResultData = {
      paper: entry.paper,
      review: entry.review,
      language: entry.language,
      responseLetter: entry.responseLetter,
      reviewPoints: entry.reviewPoints,
      changeTable: entry.changeTable,
      locations: [],
      items: [],
    };
    sessionStorage.setItem("rr_latest_result", JSON.stringify(result));
  };

  const handleDelete = (id: string) => {
    removeHistory(id);
    setEntries(loadHistory());
  };

  return (
    <AppLayout>
      <TopBar
        title="我的回复历史"
        subtitle={`累计 ${entries.length} 次生成`}
        actions={
          <Link to="/workspace"><Btn size="sm">+ 新建回复</Btn></Link>
        }
      />
      <div className="px-10 py-10 max-w-[1180px] mx-auto">
        {entries.length > 0 && (
          <div className="mb-10">
            <div className="rounded-xl border border-rule bg-card p-5 max-w-xs">
              <div className="text-[11px] uppercase tracking-wider text-ink-muted">总生成次数</div>
              <div className="font-serif text-[40px] leading-none mt-3 tabular-nums">{entries.length}</div>
              <div className="text-[11px] text-emerald-ink mt-2">
                最近: {entries[0]?.date || "—"}
              </div>
            </div>
          </div>
        )}

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <input
              className="h-9 px-3 rounded-md border border-rule bg-card text-[13px] w-72"
              placeholder="搜索论文标题 / 期刊 / 关键词"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {["全部", "完成", "草稿"].map((t) => (
              <button
                key={t}
                onClick={() => setFilter(t)}
                className={`h-9 px-3 rounded-md text-[12px] transition-colors ${
                  filter === t ? "bg-ink text-background" : "border border-rule text-ink-soft hover:text-ink"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
          <span className="text-[12px] text-ink-muted">按时间倒序</span>
        </div>

        {filtered.length === 0 ? (
          <div className="rounded-xl border border-rule bg-card p-16 text-center text-ink-muted text-[13px]">
            {entries.length === 0
              ? "暂无生成记录。去工作台生成第一条回复吧。"
              : "没有匹配的记录。"}
          </div>
        ) : (
          <div className="rounded-xl border border-rule bg-card overflow-hidden">
            {filtered.map((it) => (
              <div key={it.id} className="grid grid-cols-[1fr_180px_120px_80px_24px] gap-4 items-center px-6 py-4 border-b border-rule last:border-b-0 hover:bg-paper">
                <Link
                  to="/results/letter"
                  onClick={() => openResult(it)}
                  className="block"
                >
                  <div className="font-serif text-[18px] text-ink leading-tight">{it.title}</div>
                  <div className="text-[11px] text-ink-muted mt-1">{it.journal} · {it.date} · {it.language === "zh" ? "中文" : it.language === "en" ? "English" : "自动"}</div>
                </Link>
                <div className="text-[12px] text-ink-soft">
                  <span className="text-ink-muted">审稿意见 </span>
                  <b className="text-ink tabular-nums">{it.reviewCount}</b> 条
                </div>
                <Chip tone={it.status === "草稿" ? "amber" : "emerald"}>{it.status}</Chip>
                <div className="flex gap-1.5">
                  <Link
                    to="/results/letter"
                    onClick={() => openResult(it)}
                    className="w-7 h-7 rounded-md border border-rule text-ink-soft hover:bg-surface text-[12px] grid place-items-center"
                  >
                    ⧉
                  </Link>
                  <button
                    onClick={() => handleDelete(it.id)}
                    className="w-7 h-7 rounded-md border border-rule text-ink-soft hover:bg-surface text-[12px] grid place-items-center"
                  >
                    ✕
                  </button>
                </div>
                <span className="text-ink-muted">›</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
