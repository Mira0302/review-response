import { Link, useRouterState } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { AppLayout, TopBar, Btn, Chip } from "./AppLayout";
import type { ResultData, ParsedItem } from "@/routes/workspace.index";

export type { ResultData, ParsedItem };

export function getStoredResult(): ResultData | null {
  try {
    const raw = sessionStorage.getItem("rr_latest_result");
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

const tabs = [
  { to: "/results/letter", label: "回复信", n: "01" },
  { to: "/results/table", label: "修改对照表", n: "02" },
  { to: "/results/edit", label: "编辑模式", n: "03" },
];

export function ResultsLayout({ children, action }: { children: ReactNode; action?: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const result = getStoredResult();
  const items = result?.items || [];
  const okCount = items.filter((i) => i.status === "ok").length;
  const warnCount = items.filter((i) => i.status === "warn").length;

  return (
    <AppLayout>
      <TopBar
        breadcrumb="Result"
        title={`生成完成 · ${items.length} 条回复`}
        subtitle={`质量评分 ${okCount}/${items.length} · ${warnCount} 条建议复核 · 生成耗时 ~20s`}
        actions={
          <>
            <Btn variant="ghost" size="sm">⟲ 重新生成</Btn>
            <Link to="/workspace"><Btn variant="outline" size="sm">← 修改输入</Btn></Link>
            {action}
          </>
        }
      />
      <div className="px-10 pt-6 pb-4 max-w-[1180px] mx-auto">
        <div className="flex items-end justify-between border-b border-rule">
          <div className="flex items-center gap-1">
            {tabs.map((t) => {
              const active = pathname === t.to;
              return (
                <Link
                  key={t.to}
                  to={t.to}
                  className={`relative px-5 py-3 text-[13px] flex items-center gap-2 ${active ? "text-ink" : "text-ink-muted hover:text-ink"}`}
                >
                  <span className="font-mono text-[10px] text-ink-muted">{t.n}</span>
                  {t.label}
                  {active && <span className="absolute left-0 right-0 -bottom-px h-0.5 bg-ink" />}
                </Link>
              );
            })}
          </div>
          <div className="flex items-center gap-2 pb-2">
            <Chip tone="emerald">✓ {okCount} 条通过</Chip>
            {warnCount > 0 && <Chip tone="amber">⚠ {warnCount} 条复核</Chip>}
          </div>
        </div>
      </div>
      <div className="px-10 pb-16 max-w-[1180px] mx-auto">{children}</div>

      <div className="border-t border-rule bg-paper">
        <div className="px-10 py-6 max-w-[1180px] mx-auto flex items-center justify-between">
          <div className="text-[12px] text-ink-soft">这次的结果对你<b className="text-ink">有帮助</b>吗？反馈会用于改进生成质量。</div>
          <div className="flex items-center gap-2">
            <Btn size="sm" variant="outline">👍 有用</Btn>
            <Btn size="sm" variant="outline">😐 一般</Btn>
            <Btn size="sm" variant="outline">👎 无帮助</Btn>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
