import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    max_tokens=4000,
    temperature=0.5
)


def parse_review_points(review_text: str) -> str:
    """将审稿意见解析为逐条列表"""
    system_prompt = """你是一个学术审稿意见解析助手。请将以下审稿意见拆解为逐条独立的问题点。

规则：
- 每个问题点一行，以"• "开头
- 尽量保留审稿人的原始措辞
- 如果审稿意见本身已经是逐条格式，保持原样并标注序号
- 区分"必须修改的问题"和"建议性意见"（如果审稿人有暗示的话）"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"请解析以下审稿意见：\n\n{review_text}")
    ])
    return response.content


def clean_response(text: str) -> str:
    """Strip Chinese formal letter closings and signatures from LLM output."""
    import re
    # Remove "此致敬礼" in all spacing variants
    text = re.sub(r'\n{0,2}此致\s*\n+\s*敬礼\s*', '', text)
    text = re.sub(r'\n{0,2}此致\s*\n+\s*敬礼\s*\n*', '\n', text)
    # Remove Chinese signature / placeholder blocks
    text = re.sub(r'\n{0,2}作者[：:][^\n]*', '', text)
    text = re.sub(r'\n{0,2}日期[：:][^\n]*', '', text)
    text = re.sub(r'\n{0,2}\[您的姓名\][^\n]*', '', text)
    text = re.sub(r'\n{0,2}\[通讯作者[^\]]*\][^\n]*', '', text)
    text = re.sub(r'\n{0,2}\[日期\][^\n]*', '', text)
    # Remove lines that are only whitespace at the very end
    text = re.sub(r'\n{2,}$', '', text)
    return text.strip()


def generate_response_letter(
    paper_content: str,
    review_text: str,
    paper_title: str = "论文",
    language: str = "auto"
) -> str:
    """生成完整的审稿意见回复信。language: auto/zh/en"""

    # Auto-detect language from review text
    if language == "auto":
        # Count Chinese characters vs English words
        chinese_chars = len([c for c in review_text if '一' <= c <= '鿿'])
        english_words = len([w for w in review_text.split() if w.isascii() and w.isalpha()])
        detected = "zh" if chinese_chars > english_words else "en"
    else:
        detected = language

    if detected == "zh":
        system_prompt = """你是一位经验丰富的学术论文作者，擅长撰写专业的审稿意见回复信。

【铁律 — 语言要求】整封回复信的每一个字都必须是中文。包括开头称呼（禁止写 Dear Editor）、所有逐条回复、以及结尾（禁止写 Sincerely / Best regards / We hope...）。即使审稿意见原文是英文，你的回复也必须是中文。全文不允许出现任何一个英文单词或句子。

格式要求：
- 开头：必须写"尊敬的编辑和审稿人："
- 逐条回复：每条审稿意见对应一条回复，标注"审稿意见 #N"和"回复 #N"
- 引用审稿意见原文时可保留原语言，但你的回复必须是中文
- 每条回复包含：(1) 感谢审稿人的意见 (2) 说明你做了什么修改 (3) 标注修改在论文中的具体位置（如第X节、第Y页、第Z段）
- 结尾：必须写"希望修改后的论文达到发表标准。"
- 禁止使用"此致敬礼"、"敬礼"、"作者："、"日期："等措辞
- 禁止添加签名块或日期行
- 禁止在开头使用"Dear Editor"或"Dear Editor and Reviewers"
- 禁止在结尾使用"Sincerely"、"Best regards"、"Yours sincerely"等英文落款

内容要求：
- 每条回复必须具体，不能只说"已修改"。要说清楚改了什么、怎么改的、在哪里
- 即使不同意审稿人，也要先感谢再礼貌反驳，给出充分理由
- 语气谦卑但不卑微，专业但不傲慢"""

    else:
        system_prompt = """You are an experienced academic author skilled at writing professional, well-reasoned response letters to peer reviewers.

【IRON RULE — Language】Every single word of the response letter must be in English. The salutation, all point-by-point responses, and the closing must all be in English. Even if the review comments are in Chinese, your responses MUST be in English. Do NOT use any Chinese characters or phrases anywhere in the letter — not even the salutation or closing.

Format requirements:
- Opening: Start with "Dear Editor and Reviewers,"
- Point-by-point: Label each comment and response as "Reviewer Comment #N" and "Response #N"
- Quote review comments in their original language, but your responses MUST be in English
- Each response must include: (1) Acknowledge the reviewer's concern (2) Describe what changes you made (3) Specify the exact location in the manuscript (Section X, Page Y, Paragraph Z)
- Closing: End with "We hope the revised manuscript meets the standards for publication."
- Do NOT add signature blocks, date lines, or Chinese-style closings
- Do NOT use "尊敬的编辑" or "此致敬礼" or any Chinese salutation/closing

Content requirements:
- Every response must be specific — describe what was changed, how, and where
- Even when disagreeing, first thank the reviewer, then politely explain your reasoning
- Tone: humble but not subservient, professional but not arrogant"""

    user_prompt = f"""Please generate a complete response letter for the following peer review.

【Paper Title】{paper_title}

【Manuscript Content】
{paper_content[:8000]}...

【Review Comments】
{review_text}

Generate a complete response letter including opening acknowledgment, point-by-point responses, and closing."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return clean_response(response.content)


def run_review_response(
    paper_content: str,
    review_text: str,
    paper_title: str = "论文"
) -> dict:
    """
    主入口：输入论文和审稿意见，输出回复信

    Returns:
        {"response_letter": str, "review_points": str}
    """
    if not paper_content.strip():
        return {"response_letter": "", "review_points": "", "error": "请粘贴论文正文"}
    if not review_text.strip():
        return {"response_letter": "", "review_points": "", "error": "请粘贴审稿意见"}
    if len(paper_content) < 100:
        return {"response_letter": "", "review_points": "", "error": "论文正文太短（少于100字），请粘贴完整论文"}

    review_points = parse_review_points(review_text)
    response_letter = generate_response_letter(paper_content, review_text, paper_title)

    return {
        "response_letter": response_letter,
        "review_points": review_points,
        "error": None
    }
