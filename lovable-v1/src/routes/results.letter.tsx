import { createFileRoute } from "@tanstack/react-router";
import { ResultsLayout, getStoredResult, type ParsedItem } from "@/components/rr/ResultsShared";
import { Btn, Chip } from "@/components/rr/AppLayout";

export const Route = createFileRoute("/results/letter")({ component: Letter });

function Letter() {
  const result = getStoredResult();

  if (!result) {
    return (
      <ResultsLayout action={<Btn size="sm">📋 复制回复信</Btn>}>
        <div className="mt-8 text-center text-ink-muted py-20">
          暂无生成结果。请先在工作台生成回复。
        </div>
      </ResultsLayout>
    );
  }

  const { items, responseLetter: letter } = result;

  // Group items by reviewer
  const byReviewer: Record<string, ParsedItem[]> = {};
  for (const item of items) {
    (byReviewer[item.reviewer] ||= []).push(item);
  }

  const okCount = items.filter((i) => i.status === "ok").length;
  const warnCount = items.filter((i) => i.status === "warn").length;
  const locOk = items.filter((i) => i.location !== "详见回复信").length;

  // If we have structured items, render them; otherwise render the raw markdown
  const hasItems = items.length > 0;

  return (
    <ResultsLayout action={<Btn size="sm" onClick={() => navigator.clipboard.writeText(letter)}>📋 复制回复信</Btn>}>
      <div className="grid grid-cols-[1fr_280px] gap-8 mt-8">
        <article className="rounded-xl border border-rule bg-card shadow-paper">
          <header className="px-10 pt-10 pb-6 border-b border-rule">
            <div className="text-[10px] uppercase tracking-[0.25em] text-ink-muted">Response Letter · Markdown</div>
            <h2 className="font-serif text-[36px] mt-3 leading-tight">Response to Reviewers</h2>
            <p className="text-[13px] text-ink-soft mt-3 leading-[1.8]">
              Dear Editor and Reviewers,<br />
              We sincerely thank you for the thoughtful and constructive comments on our manuscript.
              Below we address each comment point-by-point. Revised text is highlighted in the manuscript.
            </p>
          </header>

          <div className="px-10 py-8 space-y-10">
            {hasItems ? (
              Object.entries(byReviewer).map(([rv, rvItems]) => (
                <section key={rv}>
                  <div className="flex items-center gap-3 mb-5">
                    <div className="w-8 h-8 rounded-full bg-ink text-background grid place-items-center font-mono text-[11px]">{rv}</div>
                    <h3 className="font-serif text-[24px]">Reviewer {rv}</h3>
                    <div className="flex-1 h-px bg-rule" />
                  </div>
                  <ol className="space-y-7">
                    {rvItems.map((r) => (
                      <li key={r.id} className="grid grid-cols-[28px_1fr] gap-4">
                        <span className="font-mono text-[12px] text-ink-muted pt-1">{String(r.n).padStart(2, "0")}</span>
                        <div>
                          <div className="rounded-md bg-paper border-l-2 border-ink/30 px-4 py-2.5 text-[12px] text-ink-soft italic">
                            {r.question}
                          </div>
                          <div className="mt-3 flex items-center gap-2">
                            <span className="text-[10px] uppercase tracking-wider text-emerald-ink font-medium">Our Response</span>
                            <Chip>{r.category}</Chip>
                            {r.status === "warn" && <Chip tone="amber">⚠ 建议复核</Chip>}
                          </div>
                          <p
                            className="mt-2 text-[14px] leading-[1.85] text-ink font-serif"
                            dangerouslySetInnerHTML={{
                              __html: r.body
                                .replace(/\*\*(.+?)\*\*/g, '<mark class="bg-amber-soft rounded-sm px-1 not-italic font-sans text-[13px]">$1</mark>')
                                .replace(/\*(.+?)\*/g, "<em>$1</em>"),
                            }}
                          />
                        </div>
                      </li>
                    ))}
                  </ol>
                </section>
              ))
            ) : (
              <div
                className="prose prose-sm max-w-none font-serif text-[14px] leading-[1.85] text-ink"
                dangerouslySetInnerHTML={{
                  __html: letter
                    .replace(/\*\*(.+?)\*\*/g, '<mark class="bg-amber-soft rounded-sm px-1 not-italic font-sans text-[13px]">$1</mark>')
                    .replace(/\*(.+?)\*/g, "<em>$1</em>")
                    .replace(/\n\n/g, "</p><p class='mt-4'>")
                    .replace(/\n/g, "<br/>"),
                }}
              />
            )}

            <section className="border-t border-rule pt-8">
              <p className="text-[14px] font-serif italic text-ink-soft leading-[1.8]">
                We hope these revisions adequately address all concerns. We are grateful for the
                reviewers' time and look forward to your further comments.<br /><br />
                Sincerely,<br />
                The Authors
              </p>
            </section>

            <aside className="rounded-lg border border-emerald-ink/20 bg-emerald-ink/5 p-5">
              <div className="flex items-center gap-2">
                <span className="text-emerald-ink">✓</span>
                <div className="font-serif text-[18px]">质量摘要</div>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-4 text-[12px]">
                <div><div className="text-ink-muted">位置标注</div><div className="font-mono text-ink mt-1">{locOk} / {items.length} ✓</div></div>
                <div><div className="text-ink-muted">语气适宜</div><div className="font-mono text-ink mt-1">{okCount} / {items.length} ✓</div></div>
                <div><div className="text-ink-muted">内容完整</div><div className="font-mono text-ink mt-1">{items.length} / {items.length} ✓</div></div>
              </div>
            </aside>
          </div>
        </article>

        <aside className="sticky top-32 self-start">
          <div className="text-[10px] uppercase tracking-[0.2em] text-ink-muted mb-3">大纲</div>
          <ol className="space-y-1 text-[12px]">
            {items.map((r) => (
              <li key={r.id}>
                <a className="group flex items-center gap-2 py-1.5 px-2 rounded-md hover:bg-surface cursor-pointer">
                  <span className="font-mono text-[10px] text-ink-muted w-6">{r.reviewer}.{r.n}</span>
                  <span className="text-ink-soft group-hover:text-ink truncate flex-1">{r.summary}</span>
                  {r.status === "warn" ? <span className="text-amber-ink">⚠</span> : <span className="text-emerald-ink">✓</span>}
                </a>
              </li>
            ))}
          </ol>
          <div className="mt-6 rounded-lg border border-rule bg-paper p-4 text-[11px] text-ink-soft leading-[1.7]">
            <div className="text-[10px] uppercase tracking-wider text-ink-muted mb-2">统计</div>
            <div className="font-mono text-ink text-[18px] tabular-nums">{letter.length.toLocaleString()} 字符</div>
            <div className="mt-3 flex items-center justify-between">
              <span>读时</span><span className="text-ink">~{Math.max(1, Math.round(letter.split(/\s+/).length / 200))} 分钟</span>
            </div>
            <div className="mt-1 flex items-center justify-between">
              <span>语言</span><span className="text-ink">{result.language === "zh" ? "中文" : result.language === "en" ? "English" : "自动"}</span>
            </div>
          </div>
        </aside>
      </div>
    </ResultsLayout>
  );
}
