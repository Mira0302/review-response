# Author:YN
# CreaTime:2026/3/3
# Filename:tools
from langchain_community.tools import DuckDuckGoSearchRun
import time


def safe_search_tool(query: str) -> str:
    """
    带异常捕获和重试机制的搜索工具
    """
    search = DuckDuckGoSearchRun()
    max_retries = 2

    for attempt in range(max_retries):
        try:
            # 模拟超时控制和参数打印
            print(f"  [Tool] 正在检索: {query} (第 {attempt + 1} 次尝试)...")
            result = search.invoke(query)
            return result
        except Exception as e:
            print(f"  [Tool Error] 检索失败: {e}")
            time.sleep(2)  # 失败重试等待

    return "检索失败，未找到相关文献资料。"