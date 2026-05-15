import gradio as gr
from src.review_response import run_review_response
from src.utils.file_parser import extract_text

THEME = gr.themes.Soft(
    primary_hue="zinc",
    secondary_hue="stone",
    neutral_hue="stone",
).set(
    body_text_size="15px",
    body_background_fill="#fafaf8",
    block_background_fill="#ffffff",
    block_border_color="#e7e5e4",
    block_border_width="1px",
    block_radius="16px",
    block_shadow="0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04)",
    input_background_fill="#fafaf8",
    input_border_color="#e7e5e4",
    input_border_width="1px",
    input_radius="10px",
    input_placeholder_color="#a8a29e",
    button_border_width="1px",
    button_primary_background_fill="#1c1917",
    button_primary_background_fill_hover="#292524",
    button_primary_text_color="#ffffff",
    button_primary_border_color="#1c1917",
    button_secondary_background_fill="#ffffff",
    button_secondary_background_fill_hover="#fafaf8",
    button_secondary_text_color="#57534e",
    button_secondary_border_color="#e7e5e4",
    button_large_radius="10px",
    button_large_text_size="16px",
    button_small_radius="10px",
    button_small_text_size="14px",
    border_color_primary="#e7e5e4",
    loader_color="#1c1917",
)

CUSTOM_CSS = """
/* ── Global ── */
.gradio-container {
    max-width: 1060px !important;
    margin: 0 auto !important;
    padding: 32px 24px 48px !important;
    background: #fafaf8;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
}

/* ── Header ── */
.app-header {
    text-align: center;
    padding: 40px 0 48px;
}
.app-header .logo {
    font-size: 32px;
    font-weight: 700;
    color: #1c1917;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
}
.app-header .tagline {
    font-size: 16px;
    color: #78716c;
    font-weight: 400;
}

/* ── Section labels ── */
.section-label {
    font-size: 13px;
    font-weight: 600;
    color: #78716c;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 16px;
}

/* ── Gradio component overrides ── */
.gradio-container .wrap {
    box-shadow: none !important;
}
.gradio-container .panel {
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04) !important;
    border: 1px solid #e7e5e4 !important;
    border-radius: 16px !important;
    background: #ffffff !important;
    padding: 24px !important;
    transition: box-shadow 0.2s ease;
}
.gradio-container .panel:hover {
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 6px 20px rgba(0,0,0,0.06) !important;
}
.gradio-container textarea,
.gradio-container input[type="text"] {
    border: 1px solid #e7e5e4 !important;
    border-radius: 10px !important;
    background: #fafaf8 !important;
    padding: 14px 16px !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
    color: #292524 !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.gradio-container textarea:focus,
.gradio-container input[type="text"]:focus {
    border-color: #a8a29e !important;
    box-shadow: 0 0 0 3px rgba(28,25,23,0.06) !important;
    outline: none !important;
}
.gradio-container textarea::placeholder,
.gradio-container input[type="text"]::placeholder {
    color: #a8a29e !important;
}

/* ── File upload ── */
.gradio-container .file-preview {
    border: 1.5px dashed #d6d3d1 !important;
    border-radius: 10px !important;
    background: #fafaf8 !important;
    padding: 20px !important;
    transition: border-color 0.15s ease, background 0.15s ease;
}
.gradio-container .file-preview:hover {
    border-color: #a8a29e !important;
    background: #f5f5f0 !important;
}

/* ── Buttons ── */
.gradio-container button.primary {
    font-weight: 600 !important;
    letter-spacing: -0.2px;
    padding: 14px 32px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(28,25,23,0.12) !important;
}
.gradio-container button.primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(28,25,23,0.18) !important;
}
.gradio-container button.secondary {
    font-weight: 500 !important;
    letter-spacing: -0.2px;
    padding: 10px 20px !important;
    transition: all 0.15s ease !important;
}

/* ── Output text areas ── */
.output-box textarea {
    font-size: 14px !important;
    line-height: 1.7 !important;
    background: #ffffff !important;
    border: 1px solid #e7e5e4 !important;
    border-radius: 12px !important;
}

/* ── Markdown headings in output ── */
.gradio-container .prose h3,
.gradio-container .md h4 {
    font-weight: 600 !important;
    color: #1c1917 !important;
}

/* ── Divider ── */
.section-divider {
    border: none;
    border-top: 1px solid #e7e5e4;
    margin: 40px 0 36px;
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    padding-top: 40px;
    margin-top: 20px;
}
.app-footer .features {
    display: flex;
    justify-content: center;
    gap: 36px;
    flex-wrap: wrap;
    margin-bottom: 36px;
}
.app-footer .feature-item {
    text-align: center;
    max-width: 180px;
}
.app-footer .feature-item .icon {
    font-size: 20px;
    margin-bottom: 8px;
    display: block;
}
.app-footer .feature-item .title {
    font-size: 13px;
    font-weight: 600;
    color: #57534e;
    margin-bottom: 4px;
}
.app-footer .feature-item .desc {
    font-size: 12px;
    color: #a8a29e;
    line-height: 1.5;
}
.app-footer .copyright {
    font-size: 12px;
    color: #c4bdb8;
}
"""


def parse_paper_file(file):
    if file is None:
        return ""
    try:
        path = file if isinstance(file, str) else file.name
        text, label = extract_text(path)
        return f"[已解析 {label}，共 {len(text)} 字符]\n\n{text}"
    except Exception as e:
        return f"[解析失败] {e}"


def parse_review_file(file):
    if file is None:
        return ""
    try:
        path = file if isinstance(file, str) else file.name
        text, label = extract_text(path)
        return f"[已解析 {label}，共 {len(text)} 字符]\n\n{text}"
    except Exception as e:
        return f"[解析失败] {e}"


def handle_generate(paper_content, review_text):
    if not paper_content.strip():
        return (
            "## ⚠️ 请先上传论文\n\n粘贴正文或上传 PDF / Word 文件均可。",
            "等待生成...",
        )
    if len(paper_content.strip()) < 100:
        return (
            "## ⚠️ 论文内容太短\n\n请确保上传了完整的论文正文（至少包含摘要、引言、方法等核心章节）。",
            "等待生成...",
        )
    if not review_text.strip():
        return (
            "## ⚠️ 请先粘贴审稿意见\n\n将期刊或会议的审稿意见邮件原文粘贴到右侧输入框。",
            "等待生成...",
        )

    result = run_review_response(paper_content, review_text, "论文")

    if result.get("error"):
        return f"## ⚠️ {result['error']}", ""

    return result["response_letter"], result["review_points"]


def load_example():
    sample_paper = """# 基于深度学习的人机协作机械臂装配系统研究

## 摘要
本文针对人机协作装配场景中的行为识别与意图理解问题，提出了一种基于多传感器融合的深度学习框架。该框架结合视觉与惯性传感器数据，通过跨模态注意力机制实现装配行为的精确识别。实验结果表明，该方法在自建数据集上达到了94.2%的准确率，优于现有的单模态方法。

## 1. 引言
随着工业4.0的推进，人机协作装配成为智能制造的重要方向。传统装配依赖人工操作，效率低且质量不稳定。近年来，深度学习在行为识别领域取得了显著进展，但大多数方法假设完整的视觉观测。在实际装配场景中，遮挡和视角限制使得单一视觉模态难以满足需求。

## 2. 相关工作
### 2.1 基于视觉的行为识别
基于RGB视频的行为识别方法如I3D、SlowFast等在公开数据集上表现优异。然而，这些方法在工业场景中的泛化能力有限...

### 2.2 多传感器融合
多传感器融合在机器人感知领域广泛应用。现有融合策略包括数据级、特征级和决策级融合...

## 3. 方法
本文提出的框架包含三个核心模块：多模态特征提取、跨模态注意力融合、时序行为识别...

## 4. 实验
### 4.1 数据集
我们收集了10名参与者的装配数据，包含8种装配动作...

### 4.2 实验结果
本文方法在准确率上达到94.2%，相比纯视觉基线提升了12.8%...

## 5. 结论
本文提出了一个面向人机协作装配的多传感器融合框架，实验验证了其有效性。"""

    sample_review = """Dear Authors,

Thank you for submitting your manuscript. The reviewers have provided the following comments:

Reviewer 1:

1. The literature review in Section 2 is somewhat outdated. Please include more recent works from 2024-2025, especially on transformer-based action recognition methods.

2. In Section 3, the description of the cross-modal attention mechanism lacks sufficient detail. How exactly are the attention weights computed? Please provide the mathematical formulation.

3. The experimental setup mentions "visually restricted environments" but does not specify the degree of occlusion or lighting conditions. This makes it difficult to assess the method's robustness. Please add quantitative characterization of the occlusion levels.

4. Table 2 reports accuracy metrics but lacks statistical significance tests. Were the experiments repeated? Please report mean and standard deviation across at least 5 runs.

5. The comparison with baseline methods only includes older approaches (I3D, SlowFast from 2017-2019). More recent methods like VideoMAE or UniFormer should be included.

Reviewer 2:

6. The paper claims "real-time performance" but no inference time measurements are provided. Please report FPS on the target hardware.

7. The writing quality needs improvement. Several paragraphs in the Introduction are overly long and difficult to follow. Consider restructuring.

8. Minor: Figure 3 is referenced in Section 4 but not included in the manuscript."""

    return sample_paper, sample_review


with gr.Blocks(title="ReviewResponse — 审稿意见回复助手") as app:
    # ── Header ──
    gr.HTML("""
    <div class="app-header">
        <div class="logo">ReviewResponse</div>
        <div class="tagline">粘贴论文与审稿意见，AI 自动生成逐条回复草稿</div>
    </div>
    """)

    # ── Input Zone ──
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            gr.HTML('<div class="section-label">论文原文</div>')
            paper_file = gr.File(
                label="上传 PDF / Word / Markdown",
                file_types=[".pdf", ".docx", ".doc", ".txt", ".md"],
            )
            paper_content = gr.Textbox(
                label="或直接粘贴正文",
                placeholder="支持 PDF、Word、Markdown 或纯文本上传，也可以直接粘贴论文正文到此处。\n\n建议粘贴完整内容：摘要、引言、方法、实验、结论等章节。",
                lines=13,
                max_lines=18,
            )

        with gr.Column(scale=1):
            gr.HTML('<div class="section-label">审稿意见</div>')
            review_file = gr.File(
                label="上传 PDF / Word / Markdown",
                file_types=[".pdf", ".docx", ".doc", ".txt", ".md"],
            )
            review_text = gr.Textbox(
                label="或直接粘贴审稿意见",
                placeholder="支持 PDF、Word、Markdown 或纯文本上传，也可以直接粘贴审稿意见原文。\n\n可以是：期刊审稿邮件、投稿系统导出意见、导师批注等。",
                lines=13,
                max_lines=18,
            )

    # ── Actions ──
    with gr.Row():
        example_btn = gr.Button(
            "加载示例数据", variant="secondary", size="sm", scale=0, min_width=120
        )
        submit_btn = gr.Button(
            "生成回复信",
            variant="primary",
            size="lg",
            scale=1,
        )

    gr.HTML('<hr class="section-divider">')

    # ── Output Zone ──
    with gr.Row():
        with gr.Column(scale=3):
            gr.HTML('<div class="section-label">回复信 Response Letter</div>')
            output_response = gr.Textbox(
                label=None,
                lines=18,
                max_lines=28,
                placeholder="点击「生成回复信」后，AI 将在此处生成完整的逐条回复草稿，包含致谢开头、逐条回复与结尾致谢。",
                show_label=False,
                elem_classes=["output-box"],
            )
        with gr.Column(scale=2):
            gr.HTML('<div class="section-label">审稿意见解析</div>')
            output_points = gr.Textbox(
                label=None,
                lines=18,
                max_lines=28,
                placeholder="审稿意见将自动拆分为逐条编号，按审稿人分组展示。",
                show_label=False,
                elem_classes=["output-box"],
            )

    # ── Footer ──
    gr.HTML("""
    <div class="app-footer">
        <div class="features">
            <div class="feature-item">
                <span class="icon">&#9701;</span>
                <div class="title">隐私安全</div>
                <div class="desc">数据仅用于本次生成，不会上传至任何第三方服务器</div>
            </div>
            <div class="feature-item">
                <span class="icon">&#9998;</span>
                <div class="title">AI 辅助起草</div>
                <div class="desc">生成结果仅供参考，请逐条审核后提交至期刊</div>
            </div>
            <div class="feature-item">
                <span class="icon">&#9702;</span>
                <div class="title">中英文支持</div>
                <div class="desc">中英文审稿意见均可处理，自动匹配回复语言</div>
            </div>
            <div class="feature-item">
                <span class="icon">&#9889;</span>
                <div class="title">极速生成</div>
                <div class="desc">约 30 秒完成逐条回复与修改位置标注</div>
            </div>
        </div>
        <div class="copyright">ReviewResponse &mdash; 学术审稿意见回复辅助工具 &middot; AI 生成内容仅供参考</div>
    </div>
    """)

    # ── Event Bindings ──
    paper_file.change(
        fn=parse_paper_file,
        inputs=[paper_file],
        outputs=[paper_content],
    )
    review_file.change(
        fn=parse_review_file,
        inputs=[review_file],
        outputs=[review_text],
    )
    submit_btn.click(
        fn=handle_generate,
        inputs=[paper_content, review_text],
        outputs=[output_response, output_points],
    )
    example_btn.click(
        fn=load_example,
        inputs=[],
        outputs=[paper_content, review_text],
    )


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        share=False,
        theme=THEME,
        css=CUSTOM_CSS,
    )
