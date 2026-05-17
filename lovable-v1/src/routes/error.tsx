import { createFileRoute, Link } from "@tanstack/react-router";
import { AppLayout, TopBar, Btn, Chip } from "@/components/rr/AppLayout";

export const Route = createFileRoute("/error")({ component: ErrorStates });

const errors = [
  { code: "S7a", title: "论文为空", desc: "请粘贴论文正文或上传文件后再生成。", tone: "rose", cta: "回到输入" },
  { code: "S7b", title: "论文过短 (<100 字符)", desc: "上下文不足可能影响位置标注精度。", tone: "amber", cta: "继续生成 (不阻断)" },
  { code: "S7c", title: "审稿意见为空", desc: "请粘贴或上传审稿意见。", tone: "rose", cta: "回到输入" },
  { code: "S7d", title: "PDF 解析失败", desc: "无法读取该文件,可能为扫描件或加密 PDF。请手动粘贴文本。", tone: "rose", cta: "粘贴文本" },
  { code: "S7e", title: "生成超时 (>60s)", desc: "建议缩短论文长度或稍后重试。", tone: "amber", cta: "重试" },
  { code: "S7f", title: "API 暂时不可用", desc: "DeepSeek 服务返回 503。我们正在自动切换备用模型。", tone: "rose", cta: "重试" },
  { code: "S7g", title: "Token 超额", desc: "本次输入约 64,000 tokens,超出单次上限 50,000。", tone: "amber", cta: "拆分输入" },
];

function ErrorStates() {
  return (
    <AppLayout>
      <TopBar title="错误状态总览" subtitle="S7a — S7g · 所有可能的错误状态与恢复操作" />
      <div className="px-10 py-10 max-w-[1180px] mx-auto">
        {/* Hero example */}
        <section className="rounded-2xl border border-rose-ink/25 bg-rose-soft/40 p-8 mb-10">
          <div className="grid grid-cols-[80px_1fr_auto] items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-rose-ink/15 text-rose-ink grid place-items-center text-4xl">⚠</div>
            <div>
              <div className="flex items-center gap-2">
                <Chip tone="rose">S7d · 文件解析失败</Chip>
                <span className="font-mono text-[10px] text-ink-muted">ERR_PDF_OCR_REQUIRED</span>
              </div>
              <h2 className="font-serif text-[32px] mt-2 leading-tight">无法读取这份 PDF 的文字</h2>
              <p className="text-[13px] text-ink-soft mt-2 max-w-[640px] leading-[1.7]">
                该文件可能是扫描件 (图片型 PDF) 或受密码保护。我们建议:
                先用 Adobe / Mac 预览另存为「可搜索 PDF」,或直接将正文粘贴到右侧文本框。
              </p>
            </div>
            <div className="flex flex-col gap-2">
              <Btn>选择其他文件</Btn>
              <Btn variant="outline">粘贴文本</Btn>
              <Link to="/" className="text-[11px] text-ink-muted hover:text-ink text-center">需要帮助 ↗</Link>
            </div>
          </div>
        </section>

        <div className="text-[10px] uppercase tracking-[0.2em] text-ink-muted mb-4">7 种错误状态</div>
        <div className="grid grid-cols-2 gap-4">
          {errors.map((e) => (
            <div key={e.code} className={`rounded-xl border p-5 bg-card flex gap-4 ${
              e.tone === "rose" ? "border-rose-ink/20" : "border-amber-ink/25"
            }`}>
              <div className={`w-10 h-10 rounded-md grid place-items-center text-xl shrink-0 ${
                e.tone === "rose" ? "bg-rose-soft text-rose-ink" : "bg-amber-soft text-amber-ink"
              }`}>{e.tone === "rose" ? "✕" : "⚠"}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <Chip tone={e.tone as "rose" | "amber"}>{e.code}</Chip>
                </div>
                <div className="font-serif text-[18px] mt-2">{e.title}</div>
                <p className="text-[12px] text-ink-soft mt-1 leading-[1.7]">{e.desc}</p>
                <div className="mt-3">
                  <button className="text-[12px] text-ink underline underline-offset-2 hover:text-emerald-ink">{e.cta} →</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
