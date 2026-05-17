import { createFileRoute, Link } from "@tanstack/react-router";
import { AppLayout, TopBar, Btn, Chip } from "@/components/rr/AppLayout";

export const Route = createFileRoute("/workspace/generating")({ component: Generating });

const stages = [
  { n: "01", t: "解析论文上下文", d: "提取章节结构、图表索引、引用列表", status: "done", time: "1.4s" },
  { n: "02", t: "拆解审稿意见", d: "按审稿人分组、识别问题类别与重点要素", status: "done", time: "0.9s" },
  { n: "03", t: "逐条生成回复草稿", d: "GPT-4 / DeepSeek-R · 含修改位置标注", status: "active", time: "进行中…" },
  { n: "04", t: "组装对照表与质量报告", d: "结构化输出 + 三维度校验", status: "pending", time: "等待" },
];

function Generating() {
  return (
    <AppLayout>
      <TopBar
        title="正在生成回复信"
        subtitle="S2 · 第 2 步 · 已从工作台自动跳转 — 平均 22 秒，请勿关闭页面"
        actions={<Btn variant="outline" size="sm">中止</Btn>}
      />
      <div className="px-10 py-10 max-w-[1180px] mx-auto">
        {/* Step indicator */}
        <ol className="flex items-center gap-4 text-[12px] mb-8">
          {[
            { n: "01", t: "输入", done: true },
            { n: "02", t: "生成", active: true },
            { n: "03", t: "审核" },
            { n: "04", t: "复制" },
          ].map((s, i) => (
            <li key={s.n} className="flex items-center gap-4">
              <span className={`flex items-center gap-2 ${s.active || s.done ? "text-ink" : "text-ink-muted"}`}>
                <span className={`w-6 h-6 grid place-items-center rounded-full font-mono text-[10px] ${
                  s.done ? "bg-emerald-ink text-background" :
                  s.active ? "bg-ink text-background" :
                  "border border-rule"
                }`}>{s.done ? "✓" : s.n}</span>
                {s.t}
              </span>
              {i < 3 && <span className="w-10 h-px bg-rule" />}
            </li>
          ))}
        </ol>
        {/* Progress hero */}
        <div className="rounded-2xl border border-rule bg-card shadow-paper overflow-hidden">
          <div className="grid grid-cols-[1fr_auto] items-center px-8 py-7 border-b border-rule">
            <div>
              <Chip tone="emerald">生成中 · 75%</Chip>
              <div className="font-serif text-[36px] mt-3 leading-tight">正在为 8 条审稿意见<br/>生成结构化回复…</div>
            </div>
            <div className="text-right">
              <div className="font-mono text-[44px] tabular-nums text-ink">00:14</div>
              <div className="text-[11px] text-ink-muted">已耗时 / 预计 22s</div>
            </div>
          </div>

          {/* progress bar */}
          <div className="px-8 py-5 border-b border-rule">
            <div className="h-1.5 rounded-full bg-surface overflow-hidden">
              <div className="h-full bg-gradient-to-r from-emerald-ink/70 to-emerald-ink rounded-full" style={{ width: "62%" }} />
            </div>
            <div className="mt-2 flex justify-between text-[10px] text-ink-muted font-mono">
              <span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span>
            </div>
          </div>

          {/* stages */}
          <ol className="divide-y divide-rule">
            {stages.map((s) => (
              <li key={s.n} className="px-8 py-5 flex items-start gap-5">
                <div className={`w-9 h-9 rounded-full grid place-items-center font-mono text-[11px] shrink-0 ${
                  s.status === "done" ? "bg-emerald-ink text-background" :
                  s.status === "active" ? "bg-ink text-background animate-pulse" :
                  "border border-rule text-ink-muted"
                }`}>
                  {s.status === "done" ? "✓" : s.n}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="font-serif text-[20px] text-ink">{s.t}</div>
                    <span className={`text-[11px] font-mono ${s.status === "done" ? "text-emerald-ink" : "text-ink-muted"}`}>{s.time}</span>
                  </div>
                  <p className="text-[12px] text-ink-soft mt-1">{s.d}</p>
                  {s.status === "active" && (
                    <div className="mt-3 rounded-md bg-paper border border-rule p-3 font-mono text-[11px] text-ink-soft">
                      <div className="flex items-center gap-2 text-emerald-ink">
                        <span className="w-1.5 h-1.5 bg-emerald-ink rounded-full animate-pulse" />
                        Reviewer #1 · Comment 3 of 8
                      </div>
                      <div className="mt-1.5 text-ink-muted">▌ Drafting response with reference to §2 paragraph 2…</div>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </div>

        {/* Skeleton preview */}
        <div className="mt-10">
          <div className="text-[10px] uppercase tracking-[0.2em] text-ink-muted mb-4">输出区预览 · 骨架占位</div>
          <div className="rounded-xl border border-rule bg-card p-8 space-y-4">
            {[100, 88, 72, 95, 60, 90, 75].map((w, i) => (
              <div
                key={i}
                className="h-3 rounded-full bg-gradient-to-r from-surface via-surface-2 to-surface animate-pulse"
                style={{ width: `${w}%` }}
              />
            ))}
          </div>
        </div>

        <div className="mt-8 flex items-center justify-between text-[12px] text-ink-muted">
          <span>本次调用 · DeepSeek-R · context 8,420 tokens</span>
          <Link to="/results/letter" className="underline underline-offset-2 hover:text-ink">完成时跳转到结果 →</Link>
        </div>
      </div>
    </AppLayout>
  );
}
