import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useRef, useState, useCallback } from "react";
import { AppLayout, TopBar, Btn, Chip } from "@/components/rr/AppLayout";
import { startGeneration, streamGeneration, parseFile } from "@/lib/api";
import { extractLocations, filterValidLocations, type LocatedItem } from "@/lib/location";
import { addHistory } from "@/lib/history";

export const Route = createFileRoute("/workspace/")({ component: Workspace });

const STAGES = [
  { t: "解析论文上下文", d: "提取章节结构、图表索引、引用列表" },
  { t: "拆解审稿意见", d: "按审稿人分组，识别问题类别与重点" },
  { t: "逐条生成回复草稿", d: "含修改位置标注与对照表" },
  { t: "组装质量报告", d: "三维度校验 · 结构化输出" },
];

const WS_KEY = "rr_workspace_state";

function loadWorkspace(): { paper: string; review: string; language: string } {
  try {
    const raw = sessionStorage.getItem(WS_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return { paper: "", review: "", language: "auto" };
}

function saveWorkspace(state: { paper: string; review: string; language: string }) {
  sessionStorage.setItem(WS_KEY, JSON.stringify(state));
}

const PLACEHOLDER_PAPER = `粘贴论文全文，或将文件拖拽到此处…

建议至少 200 字符以获得最佳上下文匹配。`;

const PLACEHOLDER_REVIEW = `粘贴审稿意见原文，例如：

Reviewer #1:
1. The sample size justification (n=128) is unclear. Please add a power analysis.
2. Figure 3 lacks error bars across runs. Consider 3-5 seeds.

Reviewer #2:
3. Why is depthwise convolution chosen over standard 3x3? Ablation needed.`;

const SAMPLE_PAPER = `Title: A Lightweight Vision Transformer for Edge-Device Plant Disease Recognition

1. Introduction
Plant disease recognition has long benefited from deep convolutional networks. Yet on-device deployment remains constrained by latency and memory budgets. We propose LiteLeaf-ViT, a 4-stage hybrid architecture combining depthwise convolutions with linearized self-attention, optimized for edge deployment.

2. Related Work
Recent ViT variants (MobileViT, EfficientFormer, MobileFormer, CMT) reduce parameter count via hybrid designs. However, they typically target ImageNet-scale classification rather than fine-grained plant disease recognition on field-collected images. Our work bridges this gap by introducing leaf-specific inductive biases into the attention mechanism.

3. Method
We propose LiteLeaf-ViT, a 4-stage hybrid architecture combining depthwise convolutions with linearized self-attention. Section 3.2 details the sample selection strategy used for the field dataset (n=128, balanced across 7 disease categories including rust, blight, and powdery mildew). Section 3.3 describes the depthwise convolution blocks and their parameter efficiency. Table 4 provides an ablation study comparing depthwise vs standard 3x3 convolutions.

4. Experiments
On PlantVillage and our self-collected FieldLeaf-7 dataset, LiteLeaf-ViT achieves 94.1% top-1 accuracy at 12.4ms latency on Jetson Nano. Figure 3 shows accuracy-latency trade-offs across 5 random seeds. Table 5 reports latency on Snapdragon 8 Gen 2. Our model outperforms MobileViT by 1.3% while reducing parameters by 40%.

5. Conclusion
We presented an efficient ViT tailored to edge plant-disease scenarios. Our approach is effective across the evaluated edge-device benchmarks, offering a practical solution for real-world agricultural deployment.`;

const SAMPLE_REVIEW = `Reviewer #1:
1. The sample size justification (n=128) is unclear. Please add a power analysis or rationale.
2. Figure 3 lacks error bars across runs. Consider 3-5 seeds.
3. The related-work section overlooks MobileFormer (CVPR'22) and CMT.
4. Writing in §3.2 is dense; consider splitting paragraph 2.

Reviewer #2:
5. Why is depthwise convolution chosen over standard 3x3? Ablation needed.
6. Reported latency is on Jetson Nano only — provide Snapdragon 8 Gen 2 numbers.
7. Some references are missing DOIs.
8. The Conclusion overstates generalization; please soften the claim.`;

export interface ParsedItem {
  id: string;
  reviewer: string;
  n: number;
  category: string;
  question: string;
  location: string;
  summary: string;
  status: "ok" | "warn";
  body: string;
}

export interface ResultData {
  paper: string;
  review: string;
  language: string;
  responseLetter: string;
  reviewPoints: string;
  changeTable: string;
  locations: LocatedItem[];
  items: ParsedItem[];
}

function parseResponseItems(responseLetter: string): ParsedItem[] {
  const commentBlocks: { n: number; question: string; response: string }[] = [];
  const fullRegex = /\*\*(?:Reviewer Comment|审稿意见)\s*#(\d+)[：:]*\*\*\s*([\s\S]*?)\*\*(?:Response|回复)\s*#\1[：:]*\*\*\s*([\s\S]*?)(?=\*\*(?:Reviewer Comment|审稿意见)\s*#|\*\*$|$)/gi;
  let match: RegExpExecArray | null;
  while ((match = fullRegex.exec(responseLetter)) !== null) {
    commentBlocks.push({ n: parseInt(match[1]), question: match[2].trim(), response: match[3].trim() });
  }
  if (commentBlocks.length === 0) {
    const zhRegex = /\*\*审稿意见\s*#(\d+)[：:]*\*\*\s*([\s\S]*?)\*\*回复\s*#\1[：:]*\*\*\s*([\s\S]*?)(?=\*\*审稿意见\s*#|\*\*$|$)/gi;
    while ((match = zhRegex.exec(responseLetter)) !== null) {
      commentBlocks.push({ n: parseInt(match[1]), question: match[2].trim(), response: match[3].trim() });
    }
  }
  if (commentBlocks.length === 0) {
    const lines = responseLetter.split("\n");
    let currentN = 0, currentQuestion = "", currentResponse = "", inResponse = false;
    for (const line of lines) {
      const cm = line.match(/(?:Reviewer Comment|审稿意见|Comment)\s*#(\d+)/i);
      const rm = line.match(/(?:Response|回复)\s*#(\d+)/i);
      if (cm) {
        if (currentN > 0 && currentResponse) commentBlocks.push({ n: currentN, question: currentQuestion.trim(), response: currentResponse.trim() });
        currentN = parseInt(cm[1]); currentQuestion = ""; currentResponse = ""; inResponse = false;
      } else if (rm) { inResponse = true; }
      else if (currentN > 0) { if (inResponse) currentResponse += line + "\n"; else currentQuestion += line + "\n"; }
    }
    if (currentN > 0 && currentResponse) commentBlocks.push({ n: currentN, question: currentQuestion.trim(), response: currentResponse.trim() });
  }

  const categories = ["方法", "实验", "文献", "写作", "格式", "方法", "实验", "文献"];
  return commentBlocks.map((block, i) => {
    const reviewer = block.n <= 4 ? "R1" : block.n <= 8 ? "R2" : "R3";
    const locMatch = block.response.match(/(?:§\s*\d[\d.]*|Section\s+\d[\d.]*|第\s*\d[\d.]*\s*节|p\.\s*\d+|Page\s+\d+|Figure\s+\d+|Table\s+\d+|图\s*\d+|表\s*\d+)/i);
    const location = locMatch ? locMatch[0] : "详见回复信";
    const hasLocation = location !== "详见回复信";
    const hasSubstance = block.response.length > 80;
    return {
      id: `${reviewer.toLowerCase()}c${block.n}`,
      reviewer,
      n: block.n,
      category: categories[i % categories.length],
      question: block.question.slice(0, 200),
      location,
      summary: block.response.replace(/\*\*/g, ""),
      status: (hasLocation && hasSubstance ? "ok" : "warn") as "ok" | "warn",
      body: block.response,
    };
  });
}

function Workspace() {
  const saved = loadWorkspace();
  const [paper, setPaper] = useState(saved.paper);
  const [review, setReview] = useState(saved.review);
  const [language, setLanguage] = useState(saved.language);
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stageIdx, setStageIdx] = useState(0);
  const [stageMsg, setStageMsg] = useState("");
  const [locations, setLocations] = useState<LocatedItem[]>([]);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const paperRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const hasInput = paper.trim().length > 0 && review.trim().length > 0;

  const persist = useCallback((p: string, r: string, l: string) => {
    saveWorkspace({ paper: p, review: r, language: l });
  }, []);

  const handlePaper = useCallback((v: string) => {
    setPaper(v);
    persist(v, review, language);
  }, [review, language, persist]);

  const handleReview = useCallback((v: string) => {
    setReview(v);
    persist(paper, v, language);
  }, [paper, language, persist]);

  const handleLanguage = useCallback((v: string) => {
    setLanguage(v);
    persist(paper, review, v);
  }, [paper, review, persist]);

  const reviewCount = review.trim()
    ? (review.match(/\d+\.\s/g) || review.match(/^\d+[\.\)、]\s?/gm) || []).length ||
      review.split("\n").filter(l => l.trim() && l.trim().length > 3).length
    : 0;

  const doGenerate = useCallback(async () => {
    if (!hasInput || generating) return;
    setGenerating(true); setProgress(0); setStageIdx(0); setStageMsg(""); setError(""); setLocations([]);
    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const taskId = await startGeneration(paper, review, language);
      await streamGeneration(taskId, (event) => {
        if (controller.signal.aborted) return;
        switch (event.type) {
          case "stage":
            if (event.stage !== undefined) { setStageIdx(event.stage); setStageMsg(event.message || ""); setProgress((event.stage / (STAGES.length - 1)) * 90); }
            break;
          case "progress": setProgress((prev) => Math.min(prev + 2, 90)); break;
          case "result":
            if (event.data) {
              setProgress(100);
              const locs = extractLocations(event.data.response_letter);
              const valid = filterValidLocations(locs, paper);
              setLocations(valid);
              const items = parseResponseItems(event.data.response_letter);
              const title = paper.trim().split("\n")[0].replace(/^#+\s*/, "").slice(0, 80) || "论文";
              const result: ResultData = { paper, review, language, responseLetter: event.data.response_letter, reviewPoints: event.data.review_points, changeTable: event.data.change_table, locations: valid, items };
              sessionStorage.setItem("rr_latest_result", JSON.stringify(result));
              addHistory({ title, date: new Date().toLocaleDateString("zh-CN", { month: "long", day: "numeric" }), language, reviewCount: items.length, paper, review, responseLetter: event.data.response_letter, changeTable: event.data.change_table, reviewPoints: event.data.review_points });
              setTimeout(() => navigate({ to: "/results/letter" }), 300);
            }
            break;
          case "error": setError(event.message || "生成失败"); setGenerating(false); break;
        }
      }, controller.signal);
    } catch (err: any) {
      if (err.name !== "AbortError") setError(err.message || "网络错误，请检查后端是否启动");
      setGenerating(false);
    }
  }, [paper, review, language, hasInput, generating, navigate]);

  const doAbort = () => { abortRef.current?.abort(); setGenerating(false); setProgress(0); };

  const scrollToLocation = (idx: number) => {
    const ta = paperRef.current;
    if (!ta) return;
    const textBefore = paper.slice(0, idx);
    const lineNum = textBefore.split("\n").length;
    ta.scrollTop = Math.max(0, (lineNum - 5) * 22);
    ta.focus();
    ta.setSelectionRange(idx, idx + 30);
    ta.classList.add("ring-2", "ring-emerald-ink/50");
    setTimeout(() => ta.classList.remove("ring-2", "ring-emerald-ink/50"), 1500);
  };

  const handleFileUpload = async (file: File, target: "paper" | "review") => {
    try {
      const result = await parseFile(file);
      if (target === "paper") {
        const v = (paper ? paper + "\n\n" + result.text : result.text);
        setPaper(v); persist(v, review, language);
      } else {
        const v = (review ? review + "\n\n" + result.text : result.text);
        setReview(v); persist(paper, v, language);
      }
    } catch (err: any) { setError(err.message); }
  };

  const clearAll = () => {
    setPaper(""); setReview(""); setLocations([]); setError("");
    saveWorkspace({ paper: "", review: "", language });
  };

  const loadSample = () => {
    setPaper(SAMPLE_PAPER); setReview(SAMPLE_REVIEW);
    saveWorkspace({ paper: SAMPLE_PAPER, review: SAMPLE_REVIEW, language });
  };

  return (
    <AppLayout>
      <TopBar
        title="工作台"
        subtitle="上传论文原文与审稿意见，开始生成回复"
        actions={
          <div className="flex items-center gap-2">
            <Btn variant="ghost" size="sm" disabled={generating} onClick={clearAll}>清空全部</Btn>
            <Btn size="sm" variant="outline" disabled={generating} onClick={loadSample}>⚡ 加载示例数据</Btn>
          </div>
        }
      />
      <div className="px-10 py-10 max-w-[1180px] mx-auto">
        <ol className="flex items-center gap-4 text-[12px] mb-8">
          {[{ n: "01", t: "输入" }, { n: "02", t: "生成" }, { n: "03", t: "审核" }, { n: "04", t: "复制" }].map((s, i) => {
            const idx = i + 1;
            const step = generating ? 2 : 1;
            const done = idx < step;
            const active = idx === step;
            return (
              <li key={s.n} className="flex items-center gap-4">
                <span className={`flex items-center gap-2 ${active || done ? "text-ink" : "text-ink-muted"}`}>
                  <span className={`w-6 h-6 grid place-items-center rounded-full font-mono text-[10px] ${done ? "bg-emerald-ink text-background" : active ? "bg-ink text-background" : "border border-rule"}`}>{done ? "✓" : s.n}</span>
                  {s.t}
                </span>
                {i < 3 && <span className="w-10 h-px bg-rule" />}
              </li>
            );
          })}
        </ol>

        <div className="grid grid-cols-2 gap-6">
          <InputCard label="论文原文" hint="支持 PDF / DOCX / MD / TXT，单文件 ≤ 20MB" chip={paper ? `已就绪 · ${paper.length.toLocaleString()} 字` : "等待输入"} value={paper} onChange={handlePaper} disabled={generating} placeholder={PLACEHOLDER_PAPER} textareaRef={paperRef} onFileSelect={(f) => handleFileUpload(f, "paper")} />
          <InputCard label="审稿意见" hint="粘贴审稿邮件全文，或上传 .txt / .md 文件" chip={review ? `自动解析 · ${reviewCount} 条` : "等待输入"} value={review} onChange={handleReview} disabled={generating} placeholder={PLACEHOLDER_REVIEW} onFileSelect={(f) => handleFileUpload(f, "review")} />
        </div>

        {locations.length > 0 && !generating && (
          <div className="mt-4 flex items-center gap-2 flex-wrap">
            <span className="text-[11px] text-ink-muted">📌 原文定位:</span>
            {locations.map((loc, i) => (
              <button key={i} onClick={() => scrollToLocation(loc.index)} className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-emerald-ink/10 text-emerald-ink text-[11px] font-mono hover:bg-emerald-ink/20 border border-emerald-ink/20 transition-colors">
                {loc.location}
              </button>
            ))}
          </div>
        )}

        <div className="mt-6 rounded-xl border border-rule bg-paper">
          {!generating ? (
            <div className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-4 text-[12px]">
                <span className="text-ink-muted">回复语言:</span>
                <div className="flex items-center gap-1">
                  {[{ v: "auto", label: "自动" }, { v: "zh", label: "中文" }, { v: "en", label: "English" }].map((opt) => (
                    <button key={opt.v} onClick={() => handleLanguage(opt.v)} className={`h-8 px-3 rounded-md text-[12px] transition-colors ${language === opt.v ? "bg-ink text-background" : "border border-rule text-ink-soft hover:text-ink"}`}>{opt.label}</button>
                  ))}
                </div>
                <div className="w-px h-5 bg-rule" />
                {hasInput ? <><Chip tone="emerald">就绪</Chip><span className="text-ink-soft">预计时长 <b className="text-ink">~20 秒</b></span></> : <><Chip>等待</Chip><span className="text-ink-muted">等待输入。完整流程平均耗时 15-45s。</span></>}
              </div>
              <div className="flex items-center gap-2">
                {error && <span className="text-[12px] text-rose-ink">{error}</span>}
                <Btn disabled={!hasInput} onClick={doGenerate}>生成回复信 →</Btn>
              </div>
            </div>
          ) : (
            <div className="px-6 py-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Chip tone="emerald">生成中 · {Math.round(progress)}%</Chip>
                  <span className="text-[13px] text-ink"><b>{STAGES[stageIdx].t}</b><span className="text-ink-soft"> · {STAGES[stageIdx].d}</span></span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-[12px] text-ink-muted tabular-nums">{(progress / 100 * 20).toFixed(1)}s</span>
                  <Btn size="sm" variant="ghost" onClick={doAbort}>中止</Btn>
                </div>
              </div>
              <div className="mt-4 h-1.5 rounded-full bg-surface overflow-hidden">
                <div className="h-full bg-gradient-to-r from-emerald-ink/70 to-emerald-ink rounded-full transition-[width] duration-100" style={{ width: `${progress}%` }} />
              </div>
              <div className="mt-3 grid grid-cols-4 gap-2 text-[11px]">
                {STAGES.map((s, i) => (
                  <div key={s.t} className={`flex items-center gap-1.5 ${i < stageIdx ? "text-emerald-ink" : i === stageIdx ? "text-ink" : "text-ink-muted"}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${i < stageIdx ? "bg-emerald-ink" : i === stageIdx ? "bg-ink animate-pulse" : "bg-ink-muted/40"}`} />
                    {s.t}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="mt-10 grid grid-cols-3 gap-4">
          {[
            ["上下文越完整，标注越精准", "建议上传含图表的完整 PDF，以获取完整论文内容。"],
            ["保留审稿人编号格式", "保持 Reviewer #N / Comment N 等原文结构，解析准确率更高。"],
            ["可在生成后直接编辑", "回复信与对照表均支持纯文本编辑，复制始终复制最新内容。"],
          ].map(([t, d]) => (
            <div key={t} className="rounded-lg border border-rule p-5">
              <div className="text-[11px] uppercase tracking-wider text-emerald-ink mb-2">提示</div>
              <div className="text-[16px] font-semibold text-ink">{t}</div>
              <p className="text-[12px] text-ink-soft leading-[1.7] mt-2">{d}</p>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}

function InputCard({
  label, hint, chip, value, onChange, placeholder, disabled, textareaRef, onFileSelect,
}: {
  label: string; hint: string; chip: string;
  value: string; onChange: (v: string) => void; placeholder: string; disabled?: boolean;
  textareaRef?: React.RefObject<HTMLTextAreaElement>;
  onFileSelect?: (file: File) => void;
}) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  return (
    <section className={`rounded-xl border border-rule bg-card shadow-paper overflow-hidden ${disabled ? "opacity-60" : ""}`}>
      <header className="px-6 pt-5 pb-3 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-[18px] font-semibold">{label}</h2>
            <Chip tone={value ? "emerald" : "neutral"}>{chip}</Chip>
          </div>
          <p className="text-[11px] text-ink-muted mt-1">{hint}</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => fileRef.current?.click()} disabled={disabled} className="text-[11px] text-ink-muted hover:text-ink underline underline-offset-2 disabled:opacity-40">↑ 上传文件</button>
          <input ref={fileRef} type="file" accept=".pdf,.docx,.doc,.md,.txt,.markdown" onChange={(e) => { const f = e.target.files?.[0]; if (f) onFileSelect?.(f); if (fileRef.current) fileRef.current.value = ""; }} className="hidden" />
          <button onClick={() => onChange("")} disabled={disabled} className="text-[11px] text-ink-muted hover:text-ink underline underline-offset-2 disabled:opacity-40">清空</button>
          <span className="font-mono text-[10px] text-ink-muted tabular-nums">{value.length.toLocaleString()} / 50,000</span>
        </div>
      </header>
      <div className="px-6 pb-5">
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) onFileSelect?.(f); }}
          className={`rounded-lg border border-dashed transition-all ${dragOver ? "border-emerald-ink bg-emerald-ink/5" : "border-rule-strong bg-paper/60"} p-5`}
        >
          {!value && (
            <div className="flex items-center gap-3 text-[12px] text-ink-soft mb-3">
              <span className="w-9 h-9 rounded-md bg-surface grid place-items-center">↑</span>
              <div>
                <div className="text-ink"><b>拖拽文件到这里</b> 或 <a onClick={() => fileRef.current?.click()} className="underline underline-offset-2 cursor-pointer">浏览文件</a></div>
                <div className="text-ink-muted text-[11px] mt-0.5">最大 20MB · 单文件</div>
              </div>
            </div>
          )}
          <textarea
            ref={textareaRef as React.Ref<HTMLTextAreaElement>}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            className="w-full min-h-[260px] bg-transparent text-[13px] leading-[1.7] text-ink placeholder:text-ink-muted/70 resize-none focus:outline-none font-sans transition-all rounded"
            placeholder={placeholder}
          />
        </div>
      </div>
    </section>
  );
}
