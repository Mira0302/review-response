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


def generate_response_letter(
    paper_content: str,
    review_text: str,
    paper_title: str = "论文"
) -> str:
    """生成完整的审稿意见回复信"""
    system_prompt = """你是一位经验丰富的学术论文作者，擅长撰写专业、得体、有理有据的审稿意见回复信。

你的回复信必须遵循以下规范：

**格式要求：**
- 开头：感谢审稿人和编辑的时间和宝贵意见
- 逐条回复：每条审稿意见对应一条回复，明确标注"Reviewer Comment #N"和"Response #N"
- 每条回复包含：(1) 感谢/认可审稿人的意见 (2) 说明你做了什么修改 (3) 标注修改在论文中的位置
- 结尾：再次感谢，并表达希望修改后达到发表标准

**语气要求：**
- 谦卑但不卑微，专业但不傲慢
- 即使不同意审稿人的观点，也要先感谢再礼貌反驳，并给出充分理由
- 对每条意见都要正面回应，不要回避

**内容要求：**
- 审稿人要求补充实验 → 说明补充了什么实验、结果如何、在哪里
- 审稿人指出错误 → 感谢指正，说明已修改，标注位置
- 审稿人意见模糊 → 先给出你的理解，然后说明你据此做了哪些修改
- 审稿人观点你不同意 → 感谢提出的角度，礼貌说明你的理由，如有补充佐证更好

**关键：每条回复必须具体，不能只说"已修改"。要说清楚改了什么、怎么改的、在论文的哪个位置。**"""

    user_prompt = f"""请为以下审稿意见生成完整的回复信。

【论文标题】{paper_title}

【论文正文】
{paper_content[:8000]}...

【审稿意见】
{review_text}

请生成完整的回复信，包含开头致谢、逐条回复、结尾。"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    return response.content


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
