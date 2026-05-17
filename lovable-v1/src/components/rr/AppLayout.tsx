import { Link, useRouterState } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";

type NavItem = { to: string; label: string; num?: string; hint?: string };
type NavGroup = { label: string; num: string; items: NavItem[]; defaultOpen?: boolean };

const primary: NavItem[] = [
  { to: "/", label: "首页", num: "01", hint: "Overview" },
  { to: "/workspace", label: "工作台", num: "02", hint: "Compose" },
];

const resultsGroup: NavGroup = {
  label: "结果视图",
  num: "03",
  defaultOpen: true,
  items: [
    { to: "/results/letter", label: "回复信" },
    { to: "/results/table", label: "修改对照表" },
    { to: "/results/edit", label: "编辑模式" },
  ],
};

const historyItem: NavItem = { to: "/history", label: "历史记录", num: "04", hint: "Archive" };

export function AppLayout({ children }: { children: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <div className="min-h-screen flex bg-background text-foreground">
      <aside className="w-[252px] shrink-0 border-r border-rule bg-sidebar/70 backdrop-blur sticky top-0 h-screen flex flex-col">
        {/* Workspace switcher */}
        <div className="px-3.5 pt-4 pb-3">
          <button className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-sidebar-accent transition-colors group">
            <div className="w-7 h-7 rounded-md bg-ink text-background grid place-items-center font-semibold text-[13px] leading-none shadow-paper">R</div>
            <div className="flex-1 text-left leading-tight min-w-0">
              <div className="text-[13px] font-semibold tracking-tight truncate">ReviewResponseAssistant</div>
            </div>
            <span className="text-ink-muted text-[10px] group-hover:text-ink">⌄</span>
          </button>
        </div>

        {/* Search */}
        <div className="px-3.5 pb-3">
          <div className="relative">
            <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-ink-muted text-[12px]">⌕</span>
            <input
              placeholder="搜索 论文 / 审稿意见"
              className="w-full h-8 pl-7 pr-10 rounded-md bg-card border border-rule text-[12px] placeholder:text-ink-muted/70 focus:outline-none focus:border-rule-strong"
            />
            <kbd className="absolute right-2 top-1/2 -translate-y-1/2 text-[9.5px] font-mono text-ink-muted bg-surface border border-rule rounded px-1 py-0.5">⌘K</kbd>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-2 py-1 space-y-4">
          <ul className="space-y-px">
            {primary.map((n) => (
              <NavRow key={n.to} item={n} pathname={pathname} />
            ))}
          </ul>

          <NavGroupSection group={resultsGroup} pathname={pathname} />

          <ul className="space-y-px">
            <NavRow item={historyItem} pathname={pathname} />
          </ul>
        </nav>
      </aside>
      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}

function NavRow({ item, pathname }: { item: NavItem; pathname: string }) {
  const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
  return (
    <li>
      <Link
        to={item.to}
        className={`group relative flex items-center gap-2.5 rounded-md pl-3 pr-2 py-1.5 text-[13px] transition-colors ${
          active ? "bg-card text-ink shadow-paper border border-rule" : "text-ink-soft hover:bg-sidebar-accent hover:text-ink border border-transparent"
        }`}
      >
        {active && <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-full bg-ink" />}
        <span className={`font-mono text-[10px] tabular-nums w-5 ${active ? "text-ink-muted" : "text-ink-muted/70"}`}>{item.num}</span>
        <span className="flex-1 font-medium tracking-tight">{item.label}</span>
        {item.hint && <span className="text-[10px] text-ink-muted/60 group-hover:text-ink-muted">{item.hint}</span>}
      </Link>
    </li>
  );
}

function NavGroupSection({ group, pathname }: { group: NavGroup; pathname: string }) {
  const hasActive = group.items.some((i) => pathname.startsWith(i.to));
  const [open, setOpen] = useState(group.defaultOpen || hasActive);
  return (
    <div>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-2.5 px-3 py-1.5 text-[13px] text-ink-soft hover:text-ink rounded-md"
      >
        <span className="font-mono text-[10px] tabular-nums w-5 text-ink-muted/70">{group.num}</span>
        <span className="flex-1 text-left font-medium tracking-tight">{group.label}</span>
        <span className={`text-ink-muted text-[10px] transition-transform ${open ? "rotate-90" : ""}`}>›</span>
      </button>
      {open && (
        <ul className="mt-0.5 space-y-px pl-[34px] pr-1">
          {group.items.map((n) => {
            const active = pathname === n.to;
            return (
              <li key={n.to}>
                <Link
                  to={n.to}
                  className={`flex items-center gap-2 rounded-md px-2.5 py-1.5 text-[12.5px] transition-colors ${
                    active ? "text-ink font-medium bg-card border border-rule shadow-paper" : "text-ink-soft hover:text-ink hover:bg-sidebar-accent border border-transparent"
                  }`}
                >
                  <span className={`w-1 h-1 rounded-full ${active ? "bg-emerald-ink" : "bg-ink-muted/40"}`} />
                  <span className="tracking-tight">{n.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export function TopBar({ title, subtitle, actions, breadcrumb = "Workspace" }: { title: string; subtitle?: string; actions?: ReactNode; breadcrumb?: string }) {
  return (
    <div className="border-b border-rule bg-background/80 backdrop-blur sticky top-0 z-20">
      <div className="px-10 py-5 flex items-end justify-between gap-6">
        <div>
          <div className="text-[10px] uppercase tracking-[0.22em] text-ink-muted mb-1.5 flex items-center gap-2">
            <span>ReviewResponseAssistant</span>
            <span className="text-ink-muted/40">/</span>
            <span>{breadcrumb}</span>
          </div>
          {title && <h1 className="text-[24px] font-semibold leading-none tracking-[-0.02em]">{title}</h1>}
          {subtitle && <p className="text-[13px] text-ink-soft mt-2">{subtitle}</p>}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}

export function Btn({
  children,
  variant = "primary",
  size = "md",
  className = "",
  ...rest
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" | "outline" | "soft"; size?: "sm" | "md" | "lg" }) {
  const base = "inline-flex items-center justify-center gap-2 font-medium tracking-tight transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed";
  const sizes = { sm: "h-8 px-3 text-[12px] rounded-md", md: "h-10 px-4 text-[13px] rounded-lg", lg: "h-12 px-6 text-[14px] rounded-lg" }[size];
  const variants = {
    primary: "bg-ink text-background hover:bg-ink/90 shadow-paper",
    outline: "border border-rule-strong text-ink hover:bg-surface",
    ghost: "text-ink-soft hover:text-ink hover:bg-surface",
    soft: "bg-surface text-ink hover:bg-surface-2 border border-rule",
  }[variant];
  return <button className={`${base} ${sizes} ${variants} ${className}`} {...rest}>{children}</button>;
}

export function Chip({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "emerald" | "amber" | "rose" }) {
  const tones = {
    neutral: "bg-surface text-ink-soft border-rule",
    emerald: "bg-emerald-ink/10 text-emerald-ink border-emerald-ink/20",
    amber: "bg-amber-soft text-amber-ink border-amber-ink/25",
    rose: "bg-rose-soft text-rose-ink border-rose-ink/25",
  }[tone];
  return (
    <span className={`inline-flex items-center gap-1 px-2 h-5 rounded-full border text-[10px] font-medium tracking-wide uppercase ${tones}`}>
      {children}
    </span>
  );
}
