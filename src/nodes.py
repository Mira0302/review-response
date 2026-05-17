# Author:YN
# CreaTime:2026/3/3
# Filename:nodes
import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.state import PaperState
from src.tools.academic_search import AcademicSearchManager
from src.utils.file_manager import PaperFileManager
from src.utils.user_input import get_user_review_feedback
from dotenv import load_dotenv

load_dotenv()

# 初始化 DeepSeek 模型
API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing API key. Set DEEPSEEK_API_KEY or OPENAI_API_KEY environment variable.")

llm = ChatOpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    max_tokens=3000,
    temperature=0.7
)

# 初始化工具
search_manager = AcademicSearchManager()
file_manager = PaperFileManager()


def planner_node(state: PaperState):
    """
    规划器节点：生成详细的学术论文大纲
    """
    print("\n" + "="*60)
    print("▶ 1. Planner 正在规划论文大纲...")
    print("="*60)
    
    system_prompt = """你是一个经验丰富的学术规划师，擅长为各种研究主题设计清晰、逻辑严密的论文结构。
    请生成一个标准的学术论文大纲，必须包含以下部分：
    1. 摘要 (Abstract)
    2. 引言 (Introduction) - 研究背景、问题陈述、研究目标
    3. 相关工作 (Related Work) - 现有研究综述
    4. 方法 (Methodology) - 提出的方法/系统架构
    5. 实验 (Experiments) - 实验设置、评估指标、对比实验
    6. 结果与分析 (Results and Analysis)
    7. 结论 (Conclusion) - 总结与未来工作
    8. 参考文献 (References)
    
    请使用中文输出，结构清晰，层次分明。"""
    
    user_prompt = f"""请为以下研究题目生成详细的论文大纲：

题目：《{state['topic']}》

要求：
- 每个章节要有 2-3 个小节的详细说明
- 说明每个部分应该包含的核心内容
- 总字数控制在 800-1000 字"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    outline = response.content
    print(f"\n{outline}\n")
    print(f"  [Planner] 大纲生成完成，字数：{len(outline)}")
    
    return {"outline": outline, "revision_count": 0}


def researcher_node(state: PaperState):
    """
    研究员节点：多源学术资料检索（支持 arXiv, Google Scholar, Semantic Scholar, PubMed, IEEE）
    """
    print("\n" + "="*60)
    print("▶ 2. Researcher 正在搜集学术资料...")
    print("="*60)
    
    # 根据主题自动选择合适的搜索源
    topic_lower = state['topic'].lower()
    
    if 'medical' in topic_lower or 'health' in topic_lower or 'patient' in topic_lower:
        sources = ['pubmed', 'arxiv', 'semanticscholar']
        print(f"  [Researcher] 检测到医学主题，使用 PubMed, arXiv, Semantic Scholar")
    elif 'artificial' in topic_lower or 'ai' in topic_lower or 'machine' in topic_lower:
        sources = ['semanticscholar', 'arxiv', 'googlescholar']
        print(f"  [Researcher] 检测到 AI 主题，使用 Semantic Scholar, arXiv, Google Scholar")
    elif 'engineering' in topic_lower or 'electrical' in topic_lower:
        sources = ['ieee', 'arxiv', 'semanticscholar']
        print(f"  [Researcher] 检测到工程主题，使用 IEEE, arXiv, Semantic Scholar")
    else:
        sources = ['googlescholar', 'arxiv', 'semanticscholar']
        print(f"  [Researcher] 通用主题，使用 Google Scholar, arXiv, Semantic Scholar")
    
    # 生成多个搜索查询以获取更全面的资料
    # 优化查询：缩短长度，避免特殊字符，添加中英文关键词
    topic = state['topic']
    
    # 提取主题关键词（避免过长）
    keywords = topic.split()[:5]  # 只取前5个词
    short_topic = " ".join(keywords)
    
    search_queries = [
        f"{short_topic} latest research 2024 2025",  # 英文查询
        f"{short_topic} key technology method",       # 英文查询
        f"{topic} 最新研究进展",                      # 中文查询
    ]
    
    all_results = []
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n  [Search {i}/3] 查询：{query[:40]}...")
        all_results_dict = search_manager.search_all(query, sources=sources, max_results_per_source=3)
        formatted_result = search_manager.format_results(all_results_dict)
        all_results.append(f"【搜索查询 {i}】{query}\n{formatted_result}\n")
        print(f"  [Search {i}/3] 完成，获取 {len(formatted_result)} 字符\n")
    
    # 整合搜索结果
    full_context = "\n".join(all_results)
    
    print(f"  [Researcher] 资料收集完成，总计 {len(full_context)} 字符")
    
    return {"research_context": full_context}


def writer_node(state: PaperState):
    """
    写作者节点：根据大纲和文献撰写/修改论文
    """
    revision_num = state.get('revision_count', 0)
    print("\n" + "="*60)
    print(f"▶ 3. Writer 正在撰写草稿 (第 {revision_num} 次修改)...")
    print("="*60)
    
    system_prompt = """你是一位经验丰富的学术论文作者，擅长撰写结构严谨、逻辑清晰、引用规范的高质量学术论文。
    你的写作风格应该：
    - 使用正式的学术语言
    - 逻辑严密，论证充分
    - 结构清晰，层次分明
    - 适当引用相关研究"""
    
    # 根据是否有反馈来决定提示词
    if state.get('feedback') and state['feedback'] != "APPROVED":
        # 显示用户反馈（如果有）
        if state.get('user_feedback'):
            print(f"\n  [Writer] 用户反馈：{state['user_feedback'][:200]}...")
        
        user_prompt = f"""请根据以下要求修改论文：

【论文题目】{state['topic']}

【论文大纲】
{state['outline']}

【参考资料】
{state['research_context'][:3000]}...（已截断）

【审稿人意见】
{state['feedback']}

请根据审稿人的意见进行针对性修改，重点解决审稿人提出的问题。
保持论文的完整性和学术性，字数控制在 3000-4000 字。"""
    else:
        user_prompt = f"""请撰写一篇完整的学术论文：

【论文题目】{state['topic']}

【论文大纲】
{state['outline']}

【参考资料】
{state['research_context'][:3000]}...（已截断）

请根据大纲撰写完整的论文，包含摘要、引言、方法、实验、结论等完整结构。
使用正式的学术语言，字数控制在 3000-4000 字。"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    draft = response.content
    print(f"\n  [Writer] 草稿完成，字数：{len(draft)}")
    
    # 保存草稿供用户查阅
    revision_num = state.get('revision_count', 0)
    if revision_num == 0:
        filepath = file_manager.save_markdown(draft, f"{state['topic']}_初稿")
    else:
        filepath = file_manager.save_markdown(draft, f"{state['topic']}_修订_{revision_num}")
    
    print(f"\n  [System] 草稿已保存到：{filepath}")
    print(f"  [System] 请查阅 outputs/ 目录中的 Markdown 文件")
    
    return {"draft": draft}


def reviewer_node(state: PaperState):
    """
    审稿人节点：多维度论文质量审查
    """
    print("\n" + "="*60)
    print("▶ 4. Reviewer 正在进行质量审查...")
    print("="*60)
    
    system_prompt = """你是一位严格但公正的学术论文审稿人，具有 20 年以上的学术审稿经验。
    你的审稿标准包括：
    1. 结构完整性（25%）- 是否包含所有必要章节
    2. 逻辑连贯性（25%）- 论证是否严密，前后是否一致
    3. 学术规范性（20%）- 语言是否正式，引用是否规范
    4. 内容深度（20%）- 是否有足够的技术细节和分析
    5. 字数要求（10%）- 是否在 3000 字以上
    
    请给出详细的审稿意见，包括：
    - 总体评价
    - 具体优点
    - 需要改进的问题（按重要性排序）
    - 明确的审稿结论（Accept/Minor Revision/Major Revision/Reject）"""
    
    user_prompt = f"""请审阅以下论文：

【论文题目】{state['topic']}

【论文草稿】
{state['draft']}

请按照学术审稿标准进行详细评审，给出具体的修改意见。
如果是第一轮审稿（revision_count=0），标准可以适当放宽。
如果是后续审稿，请重点检查之前的问题是否已解决。

当前是第 {state.get('revision_count', 0)} 轮修改。"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    feedback = response.content
    
    # 智能判断是否通过
    feedback_lower = feedback.lower()
    
    # 检查是否包含接受或 minor revision 的关键词
    accept_keywords = ["accept", "接受", "minor revision", "小修", "通过", "publish"]
    reject_keywords = ["reject", "拒绝", "major revision", "大修", "不通过"]
    
    is_approved = False
    
    # 优先判断明确的接受/拒绝
    if any(keyword in feedback_lower for keyword in accept_keywords):
        # 检查是否有强烈的拒绝信号
        if not any(keyword in feedback_lower for keyword in reject_keywords):
            is_approved = True
            print("\n  [Reviewer] ✅ 审查通过！")
        else:
            print("\n  [Reviewer] ⚠️  需要修改")
    elif "revision" in feedback_lower or "修改" in feedback_lower:
        print("\n  [Reviewer] ⚠️  需要修改")
    else:
        # 默认需要修改
        print("\n  [Reviewer] ⚠️  需要修改")
    
    # 保存论文到文件
    if is_approved:
        filepath_md = file_manager.save_markdown(state['draft'], state['topic'])
        filepath_pdf = file_manager.save_pdf(state['draft'], state['topic'])
        print(f"  [Reviewer] 论文已保存到：{filepath_md}")
        if filepath_pdf:
            print(f"  [Reviewer] PDF 已生成：{filepath_pdf}")
    else:
        # 需要修改，保存草稿供用户查阅
        filepath_md = file_manager.save_markdown(state['draft'], f"{state['topic']}_待修改")
        print(f"  [Reviewer] 草稿已保存到：{filepath_md}")
    
    print(f"\n【审稿意见】\n{feedback[:500]}...")
    
    # 新增：获取用户输入的审稿意见
    print("\n" + "="*60)
    print(" " * 15 + "📝 请输入您的审稿意见")
    print("="*60)
    print("1. 键盘输入（适合短文本，<500 字）")
    print("2. 文件上传（支持 .txt/.md 文件）")
    print("3. 粘贴输入（适合长文本）")
    print("4. 确认终稿（直接生成 PDF）")
    print("5. 使用自动生成的意见")
    print("="*60)
    
    choice = input("\n请选择输入方式（1-5，默认为 5）：").strip()
    
    if choice == "1":
        user_feedback = get_user_review_feedback()
        if user_feedback:
            final_feedback = user_feedback
            print(f"\n  [System] 使用用户提供的审稿意见（{len(user_feedback)} 字符）")
        else:
            final_feedback = feedback
            print(f"\n  [System] 使用自动生成的审稿意见")
    elif choice == "2":
        user_feedback = get_user_review_feedback()
        if user_feedback:
            final_feedback = user_feedback
            print(f"\n  [System] 使用用户提供的审稿意见（{len(user_feedback)} 字符）")
        else:
            final_feedback = feedback
            print(f"\n  [System] 使用自动生成的审稿意见")
    elif choice == "3":
        user_feedback = get_user_review_feedback()
        if user_feedback:
            final_feedback = user_feedback
            print(f"\n  [System] 使用用户提供的审稿意见（{len(user_feedback)} 字符）")
        else:
            final_feedback = feedback
            print(f"\n  [System] 使用自动生成的审稿意见")
    elif choice == "4":
        # 确认终稿，直接生成 PDF
        print(f"\n  [System] 确认终稿，生成 PDF...")
        filepath_md = file_manager.save_markdown(state['draft'], state['topic'])
        filepath_pdf = file_manager.save_pdf(state['draft'], state['topic'])
        print(f"  [Reviewer] 论文已保存到：{filepath_md}")
        if filepath_pdf:
            print(f"  [Reviewer] PDF 已生成：{filepath_pdf}")
        # 设置为通过状态
        final_feedback = "APPROVED"
        is_approved = True
        review_decision = "Accept"
    elif choice == "" or choice == "5":
        final_feedback = feedback
        print(f"\n  [System] 使用自动生成的审稿意见")
        review_decision = "Accept" if is_approved else "Revision"
    else:
        print(f"  [System] 无效选项，默认使用自动生成的意见")
        final_feedback = feedback
        review_decision = "Accept" if is_approved else "Revision"
    
    return {
        "feedback": final_feedback,
        "user_feedback": user_feedback if choice in ["1", "2", "3"] else None,
        "review_decision": review_decision,
        "revision_count": 1 if not is_approved else state.get('revision_count', 0)
    }