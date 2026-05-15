# Author:YN
# CreaTime:2026/3/3
# Filename:state
"""
状态定义模块
定义 Agent 系统在各节点之间传递的状态结构
"""

from typing import TypedDict, Annotated, Optional, List
import operator


class PaperState(TypedDict):
    """
    论文生成状态机
    
    这个状态类在各个 Agent 节点之间传递，包含：
    - 输入信息（topic）
    - 中间结果（outline, research_context）
    - 输出结果（draft, feedback）
    - 控制信息（revision_count, execution_log）
    """
    
    # === 输入信息 ===
    topic: str  # 论文题目
    
    # === 中间结果 ===
    outline: str  # 论文大纲（Planner 输出）
    research_context: str  # 检索到的文献参考资料（Researcher 输出）
    
    # === 输出结果 ===
    draft: str  # 当前生成的论文草稿（Writer 输出）
    feedback: str  # 审阅人给出的修改意见（Reviewer 输出）
    
    # === 控制信息 ===
    # 记录重写次数，防止无限循环（对应简历里的：打回重试机制）
    revision_count: Annotated[int, operator.add]
    
    # 执行日志（可选，用于调试和可视化）
    execution_log: Annotated[List[str], operator.add]
    
    # 输出文件路径（Reviewer 通过后保存的文件）
    output_file: Optional[str]
    
    # 审稿决策（Accept/Revision/Reject）
    review_decision: Optional[str]
    
    # 用户自定义审稿意见（用户可以覆盖自动生成的意见）
    user_feedback: Optional[str]