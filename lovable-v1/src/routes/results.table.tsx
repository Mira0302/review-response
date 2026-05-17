import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { ResultsLayout, getStoredResult } from "@/components/rr/ResultsShared";
import { Btn, Chip } from "@/components/rr/AppLayout";

export const Route = createFileRoute("/results/table")({ component: TablePage });

function TablePage() {
  const result = getStoredResult();
  const [filter, setFilter] = useState("all");

  if (!result) {
    return (
      <ResultsLayout action={<Btn size="sm">📋 复制对照表</Btn>}>
        <div className="mt-8 text-center text-ink-muted py-20">
          暂无生成结果。请先在工作台生成回复。
        </div>
      </ResultsLayout>
    );
  }

  const { items, changeTable } = result;

  const filtered = (() => {
    let list = items;
    if (filter === "r1") list = items.filter((i) => i.reviewer === "R1");
    if (filter === "r2") list = items.filter((i) => i.reviewer === "R2");
    if (filter === "warn") list = items.filter((i) => i.status === "warn");
    return list;
  })();

  const [downloaded, setDownloaded] = useState("");

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob(["﻿" + content], { type }); // BOM for Excel UTF-8 compat
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadMD = () => {
    const md = changeTable || buildTableMarkdown(items);
    downloadFile(md, "修改对照表.md", "text/markdown;charset=utf-8");
    setDownloaded("md");
    setTimeout(() => setDownloaded(""), 1500);
  };

  const downloadCSV = () => {
    const header = "#,审稿人,类别,审稿意见要点,修改位置,修改内容摘要,状态";
    const rows = items.map((r, i) =>
      [`${i + 1}`, r.reviewer, r.category, `"${r.question.replace(/"/g, '""')}"`, r.location, `"${r.summary.replace(/"/g, '""')}"`, r.status === "ok" ? "✓" : "⚠"].join(",")
    );
    const csv = [header, ...rows].join("\n");
    downloadFile(csv, "修改对照表.csv", "text/csv;charset=utf-8");
    setDownloaded("csv");
    setTimeout(() => setDownloaded(""), 1500);
  };

  if (items.length === 0 && changeTable) {
    // Parse change table markdown
    return (
      <ResultsLayout action={<Btn size="sm" onClick={downloadMD}>📋 复制对照表</Btn>}>
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-[12px]">
              <span className="text-ink-muted">导出:</span>
              <Btn size="sm" variant="outline" onClick={downloadMD}>{downloaded === "md" ? "✓ 已复制" : "Markdown"}</Btn>
              <Btn size="sm" variant="outline" onClick={downloadCSV}>{downloaded === "csv" ? "✓ 已复制" : "CSV"}</Btn>
            </div>
          </div>
          <div
            className="rounded-xl border border-rule bg-card overflow-hidden shadow-paper p-6 font-mono text-[13px] leading-[1.8] whitespace-pre-wrap"
            dangerouslySetInnerHTML={{ __html: changeTable.replace(/\|/g, '<span class="text-ink-muted">|</span>') }}
          />
        </div>
      </ResultsLayout>
    );
  }

  return (
    <ResultsLayout action={<Btn size="sm" onClick={downloadMD}>📋 复制对照表</Btn>}>
      <div className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-[12px]">
            <span className="text-ink-muted">筛选:</span>
            {[
              { k: "all", label: `全部 ${items.length}` },
              { k: "r1", label: `R1 · ${items.filter((i) => i.reviewer === "R1").length}` },
              { k: "r2", label: `R2 · ${items.filter((i) => i.reviewer === "R2").length}` },
              { k: "warn", label: `⚠ 复核 ${items.filter((i) => i.status === "warn").length}` },
            ].map((f) => (
              <button
                key={f.k}
                onClick={() => setFilter(f.k)}
                className={`h-8 px-3 rounded-md border text-[12px] transition-colors ${
                  filter === f.k
                    ? "bg-ink text-background border-ink"
                    : "border-rule text-ink-soft hover:text-ink"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2 text-[12px] text-ink-muted">
            <span>导出:</span>
            <Btn size="sm" variant="outline" onClick={downloadMD}>{downloaded === "md" ? "✓ 已复制" : "Markdown"}</Btn>
            <Btn size="sm" variant="outline" onClick={downloadCSV}>{downloaded === "csv" ? "✓ 已复制" : "CSV"}</Btn>
          </div>
        </div>

        <div className="rounded-xl border border-rule bg-card overflow-hidden shadow-paper">
          <div className="grid grid-cols-[60px_80px_1fr_120px_1.4fr_90px] bg-paper border-b border-rule text-[10px] uppercase tracking-[0.15em] text-ink-muted">
            <div className="px-4 py-3.5">序号</div>
            <div className="px-4 py-3.5 border-l border-rule">审稿人</div>
            <div className="px-4 py-3.5 border-l border-rule">审稿意见要点</div>
            <div className="px-4 py-3.5 border-l border-rule">修改位置</div>
            <div className="px-4 py-3.5 border-l border-rule">修改内容</div>
            <div className="px-4 py-3.5 border-l border-rule text-center">状态</div>
          </div>
          {filtered.map((r, i) => (
            <div
              key={r.id}
              className={`grid grid-cols-[60px_80px_1fr_120px_1.4fr_90px] text-[13px] border-b border-rule last:border-b-0 hover:bg-paper/60 cursor-pointer ${
                r.status === "warn" ? "bg-amber-soft/30" : ""
              }`}
            >
              <div className="px-4 py-4 font-mono text-ink-muted">{String(i + 1).padStart(2, "0")}</div>
              <div className="px-4 py-4 border-l border-rule">
                <span className="inline-flex items-center gap-1.5">
                  <span className="w-5 h-5 rounded-full bg-ink text-background grid place-items-center font-mono text-[9px]">{r.reviewer}</span>
                  <span className="text-ink-muted font-mono text-[11px]">#{r.n}</span>
                </span>
              </div>
              <div className="px-4 py-4 border-l border-rule text-ink leading-[1.6]">
                <div className="flex items-center gap-2 mb-1">
                  <Chip>{r.category}</Chip>
                </div>
                {r.question.length > 80 ? r.question.slice(0, 80) + "…" : r.question}
              </div>
              <div className="px-4 py-4 border-l border-rule">
                <code className="text-[11px] font-mono text-emerald-ink bg-emerald-ink/8 px-2 py-1 rounded">{r.location}</code>
              </div>
              <div className="px-4 py-4 border-l border-rule text-ink-soft leading-[1.6]">{r.summary}</div>
              <div className="px-4 py-4 border-l border-rule text-center">
                {r.status === "ok" ? (
                  <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-emerald-ink/10 text-emerald-ink">✓</span>
                ) : (
                  <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-amber-soft text-amber-ink">⚠</span>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 flex items-center gap-6 text-[11px] text-ink-muted">
          <div className="flex items-center gap-2"><span className="w-4 h-4 rounded-full bg-emerald-ink/10 text-emerald-ink grid place-items-center text-[10px]">✓</span> 已通过自动校验</div>
          <div className="flex items-center gap-2"><span className="w-4 h-4 rounded-full bg-amber-soft text-amber-ink grid place-items-center text-[10px]">⚠</span> 建议人工复核 (位置标注模糊 / 语气过强 / 内容不完整)</div>
        </div>
      </div>
    </ResultsLayout>
  );
}

function buildTableMarkdown(items: import("@/components/rr/ResultsShared").ParsedItem[]): string {
  let md = "| # | 审稿意见要点 | 修改位置 | 修改内容摘要 | 状态 |\n";
  md += "|:--:|------------|---------|------------|:--:|\n";
  for (let i = 0; i < items.length; i++) {
    const r = items[i];
    md += `| ${i + 1} | ${r.question.slice(0, 60)} | ${r.location} | ${r.summary} | ${r.status === "ok" ? "✓" : "⚠"} |\n`;
  }
  return md;
}
