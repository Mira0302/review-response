import { createFileRoute, Link } from "@tanstack/react-router";
import { AppLayout, Btn, Chip } from "@/components/rr/AppLayout";

export const Route = createFileRoute("/")({ component: Landing });

const features = [
  {
    icon: "🔍",
    title: "审稿意见拆解",
    desc: "粘贴审稿意见，自动按审稿人分组、编号、识别问题类别（方法/实验/文献/写作），拆解为逐条可追踪的任务。",
    chip: "自动解析",
    highlight: "支持中英文意见",
  },
  {
    icon: "✍️",
    title: "逐条回复生成",
    desc: "针对每条意见生成学术规范的回复，自动标注修改位置（§3.2 / p.7 / Table 2），支持中文/英文输出。",
    chip: "中英双语",
    highlight: "8 条意见 ~20s",
  },
  {
    icon: "📊",
    title: "对照表 & 历史管理",
    desc: "一键导出 Markdown / CSV 修改对照表，支持在线编辑回复内容，所有生成记录自动保存至本地浏览器。",
    chip: "可导出",
    highlight: "数据仅存储于本地",
  },
];

const steps = [
  { n: "01", title: "粘贴论文与审稿意见", desc: "支持 PDF/Word/Markdown/TXT 上传或直接粘贴文本。" },
  { n: "02", title: "一键生成回复草稿", desc: "选择输出语言，AI 逐条生成带位置标注的回复与修改对照表，平均 20 秒完成。" },
  { n: "03", title: "审核、编辑、复制", desc: "在线预览回复信与对照表，支持直接编辑。一键复制到期刊投稿系统。" },
];

const stats = [
  { value: "~20s", label: "8 条意见平均耗时" },
  { value: "中/英", label: "双语生成" },
  { value: "本地", label: "数据不上传服务器" },
];

function Landing() {
  return (
    <AppLayout>
      {/* ── Top utility bar ── */}
      <div className="border-b border-rule">
        <div className="px-10 h-14 flex items-center justify-between max-w-[1240px] mx-auto">
          <div className="flex items-center gap-6 text-[12px] text-ink-soft">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-ink" />
              面向硕士 / 博士 / 青年学者
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Link to="/workspace"><Btn size="sm">开始使用 →</Btn></Link>
          </div>
        </div>
      </div>

      <div className="min-h-screen">
        {/* ── HERO ── */}
        <section className="px-10 pt-20 pb-16 max-w-[1240px] mx-auto">
          <div className="grid grid-cols-12 gap-10 items-center">
            <div className="col-span-7">
              <Chip tone="emerald">AI-Powered · 学术专用</Chip>
              <h1 className="text-[56px] leading-[1.08] mt-5 text-balance font-semibold tracking-[-0.03em]">
                你的论文<br />
                <span className="text-emerald-ink">审稿意见回复助手</span>
              </h1>
              <p className="text-[17px] leading-[1.7] text-ink-soft mt-6 max-w-[520px]">
                上传论文与审稿意见，自动拆解为逐条任务，生成带修改位置标注的回复草稿与对照表。
              </p>
              <div className="mt-8 flex items-center gap-3">
                <Link to="/workspace">
                  <Btn size="lg">⚡ 用示例数据试一次</Btn>
                </Link>
                <Link to="/workspace">
                  <Btn size="lg" variant="outline">上传我的论文 →</Btn>
                </Link>
              </div>
              <div className="mt-6 flex items-center gap-6 text-[12px] text-ink-muted">
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-ink" />
                  无需注册
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-ink" />
                  数据仅存储于本地浏览器
                </span>
              </div>
            </div>

            {/* Hero preview card */}
            <div className="col-span-5">
              <div className="rounded-2xl border border-rule bg-card shadow-lift overflow-hidden">
                <div className="px-5 h-10 border-b border-rule flex items-center gap-2 bg-paper">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-ink/40" />
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-ink/40" />
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-ink/40" />
                  <span className="ml-3 text-[11px] font-mono text-ink-muted">response-letter.md</span>
                </div>
                <div className="p-5 text-[13px] leading-[1.7] text-ink">
                  <p className="font-serif text-[15px]">Dear Editor and Reviewers,</p>
                  <div className="mt-3 rounded-md border-l-2 border-emerald-ink bg-emerald-ink/5 p-3">
                    <div className="text-[10px] uppercase tracking-wider text-emerald-ink mb-1">Reviewer 1 · Comment 2</div>
                    <div className="text-[12px] text-ink-soft italic">Please clarify the sample size justification (n=128).</div>
                  </div>
                  <p className="mt-3 text-ink-soft text-[12px] leading-[1.8]">
                    We have <mark className="bg-amber-soft px-1 rounded-sm not-italic">expanded Section 3.2 (p.7)</mark> with a power analysis using G*Power 3.1, demonstrating n=128 yields power=0.82 at α=0.05.
                  </p>
                </div>
                <div className="px-5 py-2.5 border-t border-rule bg-paper flex items-center justify-between">
                  <Chip tone="emerald">✓ 位置已标注</Chip>
                  <span className="text-[11px] text-ink-muted font-mono">14:32</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── STATS ── */}
        <section className="border-y border-rule bg-paper/50">
          <div className="px-10 py-10 max-w-[1240px] mx-auto">
            <div className="grid grid-cols-3 gap-8 max-w-[720px] mx-auto">
              {stats.map((s) => (
                <div key={s.label} className="text-center">
                  <div className="font-serif text-[36px] text-ink leading-none">{s.value}</div>
                  <div className="text-[12px] text-ink-muted mt-2">{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── FEATURES ── */}
        <section className="px-10 pt-20 pb-8 max-w-[1240px] mx-auto">
          <div className="text-center mb-12">
            <h2 className="font-serif text-[36px]">三大核心功能模块</h2>
          </div>

          <div className="grid grid-cols-3 gap-5">
            {features.map((f) => (
              <div
                key={f.title}
                className="rounded-xl border border-rule bg-card p-6 hover:border-rule-strong hover:shadow-paper transition-all duration-200 group"
              >
                <div className="w-12 h-12 rounded-xl bg-surface grid place-items-center text-2xl group-hover:scale-110 transition-transform mb-4">
                  {f.icon}
                </div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-serif text-[18px] text-ink">{f.title}</h3>
                  <Chip>{f.chip}</Chip>
                </div>
                <p className="text-[13px] text-ink-soft leading-[1.7] mt-2">{f.desc}</p>
                <div className="mt-3 flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-emerald-ink" />
                  <span className="text-[12px] text-emerald-ink font-medium">{f.highlight}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── HOW IT WORKS ── */}
        <section className="px-10 py-16 max-w-[1240px] mx-auto">
          <div className="rounded-2xl border border-rule bg-card shadow-paper overflow-hidden">
            <div className="px-10 py-10 border-b border-rule bg-paper/50">
              <h2 className="font-serif text-[32px]">三步完成，不超过 5 分钟</h2>
            </div>
            <div className="px-10 py-8 grid grid-cols-3 gap-8">
              {steps.map((s, i) => (
                <div key={s.n} className="relative">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="w-10 h-10 rounded-full bg-ink text-background grid place-items-center font-mono text-[13px] font-semibold">
                      {s.n}
                    </span>
                    {i < 2 && (
                      <div className="flex-1 h-px bg-rule relative">
                        <span className="absolute right-0 top-1/2 -translate-y-1/2 text-ink-muted text-[10px]">→</span>
                      </div>
                    )}
                  </div>
                  <h3 className="font-serif text-[20px] text-ink">{s.title}</h3>
                  <p className="text-[13px] text-ink-soft leading-[1.7] mt-3">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA ── */}
        <section className="px-10 pb-20 max-w-[1240px] mx-auto">
          <div className="rounded-2xl bg-ink text-background p-12 text-center shadow-lift">
            <h2 className="font-serif text-[36px]">准备好试试了吗？</h2>
            <p className="text-[15px] text-background/70 mt-3 max-w-[480px] mx-auto leading-[1.7]">
              无需注册，示例数据一键加载。你的论文与审稿意见仅存储于本地浏览器。
            </p>
            <div className="mt-8 flex items-center justify-center gap-3">
              <Link to="/workspace">
                <Btn size="lg" className="!bg-background !text-ink hover:!bg-background/90">
                  ⚡ 用示例数据试一次
                </Btn>
              </Link>
              <Link to="/history">
                <Btn size="lg" variant="ghost" className="!text-background/80 hover:!text-background hover:!bg-background/10">
                  查看历史记录 →
                </Btn>
              </Link>
            </div>
          </div>
        </section>

      </div>
    </AppLayout>
  );
}
