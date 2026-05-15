import gradio as gr
from src.review_response import run_review_response
from src.utils.file_parser import extract_text

THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate",
).set(
    body_text_size="15px",
    block_title_text_size="17px",
    button_large_text_size="15px",
    button_large_radius="10px",
    block_radius="12px",
    input_radius="8px",
    checkbox_label_text_size="14px",
)

CUSTOM_CSS = """
.gradio-container { max-width: 1200px !important; margin: 0 auto !important; }
.header-title { text-align: center; margin-bottom: 8px; }
.header-title h1 { font-size: 2rem; font-weight: 700; margin-bottom: 4px; color: #1e293b; }
.header-title p { font-size: 1rem; color: #64748b; margin: 0; }
.step-indicator { display: flex; justify-content: center; gap: 12px; margin: 20px 0 28px; flex-wrap: wrap; }
.step-badge { display: inline-flex; align-items: center; gap: 6px; background: #f1f5f9; border-radius: 20px; padding: 6px 16px; font-size: 13px; color: #475569; font-weight: 500; }
.step-badge.active { background: #dbeafe; color: #1d4ed8; }
.step-badge.done { background: #dcfce7; color: #16a34a; }
.step-num { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; font-size: 12px; font-weight: 700; background: #e2e8f0; color: #64748b; }
.step-badge.active .step-num { background: #2563eb; color: white; }
.step-badge.done .step-num { background: #16a34a; color: white; }
.section-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 12px; }
.output-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.output-header h3 { margin: 0; font-size: 1rem; font-weight: 600; }
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 28px 0; }
footer { text-align: center; color: #94a3b8; font-size: 12px; margin-top: 32px; }
"""


def parse_paper_file(file):
    """处理论文文件上传"""
    if file is None:
        return ""
    try:
        path = file if isinstance(file, str) else file.name
        text, label = extract_text(path)
        return f"[已解析 {label}，共 {len(text)} 字符]\n\n{text}"
    except Exception as e:
        return f"[解析失败] {e}"


def parse_review_file(file):
    """处理审稿意见文件上传"""
    if file is None:
        return ""
    try:
        path = file if isinstance(file, str) else file.name
        text, label = extract_text(path)
        return f"[已解析 {label}，共 {len(text)} 字符]\n\n{text}"
    except Exception as e:
        return f"[解析失败] {e}"


def handle_generate(paper_content, review_text):
    """生成回复信"""
    if not paper_content.strip():
        return "### ⚠️ 请先上传论文\n\n粘贴正文或上传 PDF/Word 文件均可。", "等待生成..."
    if len(paper_content.strip()) < 100:
        return "### ⚠️ 论文内容太短\n\n请确保上传了完整的论文正文（至少包含摘要、引言、方法等核心章节）。", "等待生成..."
    if not review_text.strip():
        return "### ⚠️ 请先粘贴审稿意见\n\n将期刊/会议的审稿意见邮件原文粘贴到右侧输入框。", "等待生成..."

    result = run_review_response(paper_content, review_text, "论文")

    if result.get("error"):
        return f"### ⚠️ {result['error']}", ""

    return result["response_letter"], result["review_points"]


def load_example():
    """加载示例数据"""
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


with gr.Blocks(title="ReviewResponse - 审稿意见回复助手") as app:
    # ===== Header =====
    gr.HTML("""
    <div class="header-title">
      <h1>ReviewResponse</h1>
      <p>粘贴论文 + 审稿意见，AI 自动生成逐条回复草稿</p>
    </div>
    <div class="step-indicator">
      <div class="step-badge active"><span class="step-num">1</span> 上传论文</div>
      <div class="step-badge"><span class="step-num">2</span> 粘贴审稿意见</div>
      <div class="step-badge"><span class="step-num">3</span> 一键生成回复信</div>
    </div>
    """)

    # ===== Input Zone =====
    with gr.Row(equal_height=True):
        # Left: Paper
        with gr.Column(scale=1):
            gr.Markdown("#### 📄 论文原文")
            paper_file = gr.File(
                label="上传论文文件",
                file_types=[".pdf", ".docx", ".doc", ".txt", ".md"],
            )
            paper_content = gr.Textbox(
                label="或直接粘贴论文正文",
                placeholder="支持 PDF / Word / Markdown / 纯文本上传，\n也可以直接粘贴论文正文到这里...\n\n建议粘贴完整内容：摘要、引言、方法、实验、结论等",
                lines=14,
                max_lines=20,
            )

        # Right: Review
        with gr.Column(scale=1):
            gr.Markdown("#### 📋 审稿意见")
            review_file = gr.File(
                label="上传审稿意见文件",
                file_types=[".pdf", ".docx", ".doc", ".txt", ".md"],
            )
            review_text = gr.Textbox(
                label="或直接粘贴审稿意见",
                placeholder="支持 PDF / Word / Markdown / 纯文本上传，\n也可以直接粘贴审稿意见...\n\n可以是：期刊邮件原文、审稿系统导出、导师批注等",
                lines=14,
                max_lines=20,
            )

    # ===== Actions =====
    with gr.Row():
        example_btn = gr.Button("📥 加载示例数据", variant="secondary", size="sm", scale=0)
        submit_btn = gr.Button("生成回复信", variant="primary", size="lg", scale=1, min_width=200)

    gr.HTML('<hr class="divider">')

    # ===== Output Zone =====
    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("#### ✉️ 回复信（Response Letter）")
            output_response = gr.Textbox(
                label=None,
                lines=20,
                max_lines=30,
                placeholder="点击「生成回复信」后，AI 将在这里生成完整的逐条回复...",
                show_label=False,
            )
        with gr.Column(scale=2):
            gr.Markdown("#### 🔍 审稿意见解析")
            output_points = gr.Textbox(
                label=None,
                lines=20,
                max_lines=30,
                placeholder="审稿意见将自动拆分并编号...",
                show_label=False,
            )

    # ===== Footer =====
    gr.HTML("""
    <hr class="divider">
    <div style="display:flex; gap:24px; justify-content:center; flex-wrap:wrap;">
      <div style="max-width:200px; text-align:center;">
        <div style="font-size:24px; margin-bottom:6px;">🔒</div>
        <div style="font-weight:600; font-size:14px; color:#334155;">隐私安全</div>
        <div style="font-size:12px; color:#94a3b8;">数据仅用于本次生成<br>不会上传至任何服务器</div>
      </div>
      <div style="max-width:200px; text-align:center;">
        <div style="font-size:24px; margin-bottom:6px;">📝</div>
        <div style="font-weight:600; font-size:14px; color:#334155;">AI 辅助起草</div>
        <div style="font-size:12px; color:#94a3b8;">生成结果仅供参考<br>请逐条审核后提交</div>
      </div>
      <div style="max-width:200px; text-align:center;">
        <div style="font-size:24px; margin-bottom:6px;">🌐</div>
        <div style="font-weight:600; font-size:14px; color:#334155;">中英文支持</div>
        <div style="font-size:12px; color:#94a3b8;">中文/英文审稿意见均可<br>自动匹配回复语言</div>
      </div>
      <div style="max-width:200px; text-align:center;">
        <div style="font-size:24px; margin-bottom:6px;">⚡</div>
        <div style="font-weight:600; font-size:14px; color:#334155;">极速生成</div>
        <div style="font-size:12px; color:#94a3b8;">约30秒完成<br>逐条回复+修改位置标注</div>
      </div>
    </div>
    <footer>
      ReviewResponse — 学术论文审稿意见回复辅助工具 · AI 起草仅供参考
    </footer>
    """)

    # ===== Event Bindings =====
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
