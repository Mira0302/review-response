# Author:YN
# CreaTime:2026/3/3
# Filename:graph
"""
LangGraph 工作流定义
实现学术论文生成的多 Agent 协作流程
"""

from langgraph.graph import StateGraph, START, END
from src.state import PaperState
from src.nodes import planner_node, researcher_node, writer_node, reviewer_node


def should_continue(state: PaperState):
    """
    决策函数：决定工作流的下一步
    
    逻辑：
    1. 如果审稿通过 → 结束
    2. 如果达到最大修改次数 → 结束
    3. 否则 → 返回 Writer 继续修改
    """
    feedback = state.get("feedback", "")
    revision_count = state.get("revision_count", 0)
    
    # 检查审稿决策
    review_decision = state.get("review_decision", "")
    
    if review_decision == "Accept":
        print("\n  [System] ✅ 审稿通过，工作流结束")
        return END
    
    # 检查是否达到最大修改次数
    if revision_count >= 3:
        print(f"\n  [System] ⚠️  已达到最大修改次数 ({revision_count}/3)，强制结束")
        return END
    
    # 需要继续修改
    print(f"\n  [System] 🔄 需要修改，返回 Writer (第 {revision_count + 1} 轮)")
    return "writer"


# 1. 初始化图结构
builder = StateGraph(PaperState)

# 2. 添加节点
builder.add_node("planner", planner_node)
builder.add_node("researcher", researcher_node)
builder.add_node("writer", writer_node)
builder.add_node("reviewer", reviewer_node)

# 3. 添加基础边（线性流转部分）
builder.add_edge(START, "planner")
builder.add_edge("planner", "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer", "reviewer")

# 4. 添加条件分支（循环机制）
builder.add_conditional_edges(
    "reviewer",
    should_continue,
    {
        END: END,
        "writer": "writer"
    }
)

# 5. 编译图
paper_flow = builder.compile()

# 6. 可视化支持（可选）
# 使用 paper_flow.get_graph().draw_mermaid_png() 生成流程图