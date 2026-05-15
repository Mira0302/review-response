# Author:YN
# CreaTime:2026/3/3
# Filename:__init__
"""
学术论文 Agent 系统包
"""


def get_paper_flow():
    """惰性导入，避免加载整个工具链"""
    from src.graph import paper_flow
    return paper_flow


__all__ = ["get_paper_flow"]
