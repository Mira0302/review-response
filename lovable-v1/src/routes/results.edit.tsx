import { createFileRoute, Link } from "@tanstack/react-router";
import { useRef, useState, useCallback, useEffect } from "react";
import { ResultsLayout, getStoredResult } from "@/components/rr/ResultsShared";
import { Btn } from "@/components/rr/AppLayout";

export const Route = createFileRoute("/results/edit")({ component: EditMode });

const COLORS = [
  { label: "红", code: "#e53e3e" },
  { label: "蓝", code: "#3182ce" },
  { label: "绿", code: "#38a169" },
  { label: "橙", code: "#dd6b20" },
  { label: "紫", code: "#805ad5" },
];

interface AnnotationBadge {
  id: string;
  note: string;
}

function AnnoPopover({ note, onSave, onDelete, onCancel }: { note: string; onSave: (s: string) => void; onDelete: () => void; onCancel: () => void }) {
  const [text, setText] = useState(note);
  return (
    <div
      className="w-64 rounded-lg border border-rule bg-card shadow-lift p-3"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-[11px] text-ink-muted mb-1.5">修改说明</div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        className="w-full h-20 text-[12px] bg-surface border border-rule rounded p-2 resize-none focus:outline-none"
        placeholder="输入修改说明…"
        autoFocus
      />
      <div className="flex items-center justify-between mt-2">
        <button type="button" onClick={onDelete} className="text-[11px] text-rose-ink hover:underline">删除批注</button>
        <div className="flex gap-1.5">
          <button type="button" onClick={onCancel} className="text-[11px] text-ink-muted hover:text-ink px-2 py-0.5">取消</button>
          <button type="button" onClick={() => { if (text.trim()) onSave(text.trim()); }} className="text-[11px] bg-ink text-background px-2 py-0.5 rounded">保存</button>
        </div>
      </div>
    </div>
  );
}

function NewAnnoPopover({ onSave, onClose }: { onSave: (note: string) => void; onClose: () => void }) {
  const [note, setNote] = useState("");
  return (
    <div
      className="w-64 rounded-lg border border-rule bg-card shadow-lift p-3"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-[11px] text-ink-muted mb-1.5">添加批注</div>
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        className="w-full h-20 text-[12px] bg-surface border border-rule rounded p-2 resize-none focus:outline-none"
        placeholder="输入修改说明…"
        autoFocus
      />
      <div className="flex items-center justify-end gap-1.5 mt-2">
        <button type="button" onClick={onClose} className="text-[11px] text-ink-muted hover:text-ink px-2 py-0.5">取消</button>
        <button type="button" onClick={() => { if (note.trim()) onSave(note.trim()); }} className="text-[11px] bg-ink text-background px-2 py-0.5 rounded">标注</button>
      </div>
    </div>
  );
}

function EditMode() {
  const result = getStoredResult();
  const editorRef = useRef<HTMLDivElement>(null);
  const initRef = useRef(false);
  const savedRangeRef = useRef<Range | null>(null);
  const [annoMap, setAnnoMap] = useState<Record<string, AnnotationBadge>>({});
  const [activeAnno, setActiveAnno] = useState<string | null>(null);
  const [newAnnoPos, setNewAnnoPos] = useState<{ top: number; left: number } | null>(null);

  // Convert plain text to basic HTML paragraphs once
  const initialHtml = result?.responseLetter
    ?.split(/\n\n+/)
    ?.map((p) => `<p>${p.replace(/\n/g, "<br/>")}</p>`)
    ?.join("") || "";

  // Initialize contentEditable once, don't clobber on re-renders
  useEffect(() => {
    if (editorRef.current && !initRef.current) {
      editorRef.current.innerHTML = initialHtml;
      initRef.current = true;
    }
  }, []);

  if (!result) {
    return (
      <ResultsLayout>
        <div className="mt-8 text-center text-ink-muted py-20">暂无生成结果。请先在工作台生成回复。</div>
      </ResultsLayout>
    );
  }

  // Toggle annotation highlight when activeAnno changes
  useEffect(() => {
    document.querySelectorAll("[data-anno-highlight].anno-active").forEach((el) => el.classList.remove("anno-active"));
    if (activeAnno) {
      const hl = document.querySelector(`[data-anno-highlight="${activeAnno}"]`);
      if (hl) hl.classList.add("anno-active");
    }
  }, [activeAnno]);

  const execCmd = useCallback((cmd: string, value?: string) => {
    editorRef.current?.focus();
    document.execCommand(cmd, false, value);
  }, []);

  const getCleanHtml = () => {
    const html = editorRef.current?.innerHTML || "";
    const temp = document.createElement("div");
    temp.innerHTML = html;
    temp.querySelectorAll("[data-anno-id]").forEach((el) => el.remove());
    temp.querySelectorAll("[data-anno-highlight]").forEach((el) => {
      const parent = el.parentNode;
      while (el.firstChild) parent?.insertBefore(el.firstChild, el);
      parent?.removeChild(el);
    });
    return temp.innerHTML;
  };

  const handleCopy = () => {
    const clean = getCleanHtml();
    const ta = document.createElement("textarea");
    ta.innerHTML = clean;
    navigator.clipboard.writeText(ta.textContent || ta.value || "");
  };

  const handleExportWord = () => {
    const clean = getCleanHtml();
    const wordHtml = `<!DOCTYPE html>
<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">
<head><meta charset="utf-8"/><title>审稿意见回复信</title></head>
<body style="font-family: serif; font-size: 14px; line-height: 1.9; max-width: 720px; margin: 40px auto;">
${clean}
</body></html>`;
    const blob = new Blob(["﻿" + wordHtml], { type: "application/msword;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "审稿意见回复信.doc";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleUndo = () => {
    editorRef.current?.focus();
    document.execCommand("undo");
  };

  // ── Annotation ──

  const addAnnotation = (note: string) => {
    const range = savedRangeRef.current;
    if (!range || !editorRef.current) return;

    const id = "a" + Date.now().toString(36);
    setAnnoMap((prev) => ({ ...prev, [id]: { id, note } }));

    // Wrap selected text in highlight span
    const hl = document.createElement("span");
    hl.setAttribute("data-anno-highlight", id);
    try {
      range.surroundContents(hl);
    } catch {
      // Fallback: extract + wrap + re-insert (handles partial element selections)
      hl.appendChild(range.extractContents());
      range.insertNode(hl);
    }

    // Insert badge after the highlight span
    const badge = document.createElement("sup");
    badge.setAttribute("data-anno-id", id);
    badge.setAttribute("contenteditable", "false");
    badge.className =
      "inline-flex items-center justify-center w-4 h-4 rounded-full bg-amber-ink text-white text-[9px] cursor-pointer align-top -mt-1 ml-0.5 hover:scale-110 transition-transform select-none";
    badge.textContent = "💬";
    badge.title = note;
    badge.onclick = (e) => {
      e.stopPropagation();
      setActiveAnno(id);
    };

    const afterRange = document.createRange();
    afterRange.setStartAfter(hl);
    afterRange.collapse(true);
    afterRange.insertNode(badge);

    savedRangeRef.current = null;
    setNewAnnoPos(null);
  };

  const updateAnnotation = (id: string, note: string) => {
    setAnnoMap((prev) => ({ ...prev, [id]: { ...prev[id], note } }));
    // Update the badge title
    const badge = editorRef.current?.querySelector(`[data-anno-id="${id}"]`);
    if (badge) badge.setAttribute("title", note);
    setActiveAnno(null);
  };

  const deleteAnnotation = (id: string) => {
    setAnnoMap((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
    // Unwrap highlight span (keep text)
    const hl = editorRef.current?.querySelector(`[data-anno-highlight="${id}"]`);
    if (hl) {
      const parent = hl.parentNode;
      while (hl.firstChild) parent?.insertBefore(hl.firstChild, hl);
      parent?.removeChild(hl);
    }
    // Remove badge
    const badge = editorRef.current?.querySelector(`[data-anno-id="${id}"]`);
    badge?.remove();
    setActiveAnno(null);
  };

  const captureSelection = () => {
    const sel = window.getSelection();
    if (sel && !sel.isCollapsed) {
      savedRangeRef.current = sel.getRangeAt(0).cloneRange();
    } else {
      savedRangeRef.current = null;
    }
  };

  const openNewAnno = () => {
    const range = savedRangeRef.current;
    if (!range) return;
    const rect = range.getBoundingClientRect();
    setNewAnnoPos({ top: rect.bottom + 4, left: rect.left });
  };

  // ── Render ──

  return (
    <ResultsLayout
      action={
        <div className="flex items-center gap-2">
          <Btn variant="outline" size="sm" onClick={handleUndo}>↺ 撤销</Btn>
          <Btn size="sm" onClick={handleExportWord}>📄 导出 Word</Btn>
          <Btn size="sm" onClick={handleCopy}>💾 保存并复制</Btn>
        </div>
      }
    >
      <div className="px-10 py-8 max-w-[1180px] mx-auto">
        <article className="rounded-xl border-2 border-amber-ink/30 bg-card shadow-paper relative">
          <div className="absolute -top-px left-6 -translate-y-1/2 bg-background px-2 text-[10px] uppercase tracking-[0.2em] text-amber-ink">
            编辑中
          </div>

          {/* Editor area */}
          <div className="p-10 relative">
            <div
              ref={editorRef}
              contentEditable
              suppressContentEditableWarning
              className="min-h-[600px] font-serif text-[14px] leading-[1.9] text-ink focus:outline-none"
              onKeyDown={(e) => {
                // Close popovers on Escape
                if (e.key === "Escape") {
                  setActiveAnno(null);
                  setNewAnnoPos(null);
                }
              }}
            />

            {/* New annotation popover */}
            {newAnnoPos && (
              <div style={{ position: "fixed", top: newAnnoPos.top, left: newAnnoPos.left, zIndex: 50 }}>
                <NewAnnoPopover onSave={addAnnotation} onClose={() => setNewAnnoPos(null)} />
              </div>
            )}

            {/* Active annotation popover */}
            {activeAnno && annoMap[activeAnno] && (() => {
              const badge = typeof document !== "undefined" ? document.querySelector(`[data-anno-id="${activeAnno}"]`) : null;
              const rect = badge?.getBoundingClientRect();
              if (!rect) return null;
              return (
                <div style={{ position: "fixed", top: rect.top - 8, left: rect.right + 8, zIndex: 50 }}>
                  <AnnoPopover
                    note={annoMap[activeAnno].note}
                    onSave={(note) => updateAnnotation(activeAnno, note)}
                    onDelete={() => deleteAnnotation(activeAnno)}
                    onCancel={() => setActiveAnno(null)}
                  />
                </div>
              );
            })()}
          </div>

          {/* Floating toolbar */}
          <div className="sticky bottom-6 mx-10 mb-6 rounded-full bg-ink text-background shadow-lift px-3 h-11 flex items-center gap-1 text-[12px]">
            <button onClick={() => execCmd("bold")} className="px-2 hover:bg-background/10 rounded-full h-8 font-bold">B</button>
            <button onClick={() => execCmd("italic")} className="px-2 hover:bg-background/10 rounded-full h-8 italic">I</button>
            <button onClick={() => execCmd("underline")} className="px-2 hover:bg-background/10 rounded-full h-8 underline">U</button>
            <div className="w-px h-5 bg-background/20 mx-1" />
            {COLORS.map((c) => (
              <button
                key={c.code}
                onClick={() => execCmd("foreColor", c.code)}
                className="w-6 h-6 rounded-full border border-background/20 hover:scale-110 transition-transform"
                style={{ backgroundColor: c.code }}
                title={c.label}
              />
            ))}
            <div className="w-px h-5 bg-background/20 mx-1" />
            <button onMouseDown={captureSelection} onClick={openNewAnno} className="px-3 hover:bg-background/10 rounded-full h-8">
              💬 批注
            </button>
          </div>
        </article>

        {/* Stats */}
        <div className="mt-6 flex items-center gap-6 text-[12px] text-ink-muted">
          <span>编辑提示：选中文字后点击底部工具栏按钮进行格式标记，或点击「💬 批注」添加修改说明。</span>
          <span>{Object.keys(annoMap).length} 条批注</span>
        </div>

        <Link to="/workspace" className="mt-6 inline-block">
          <Btn variant="outline" size="sm">⟲ 重新生成（会覆盖编辑）</Btn>
        </Link>
      </div>
    </ResultsLayout>
  );
}
