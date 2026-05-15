# Author: YN
# CreaTime: 2026/3/3
# Filename: search_tools
"""
增强的学术搜索工具模块
支持多源搜索、缓存机制和异常处理
"""

import os
import time
import json
from typing import Optional, List
from duckduckgo_search import DDGS
from datetime import datetime


class AcademicSearchTool:
    """学术搜索工具类，支持多源检索和缓存"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self.max_retries = 3
        self.retry_delay = 2  # 秒
        self.cache_expiry = 3600  # 缓存有效期 1 小时
        
        # 创建缓存目录
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, query: str) -> str:
        """生成查询的缓存键"""
        return f"search_{hash(query) & 0xFFFFFFFF}.json"
    
    def _get_cache_path(self, query: str) -> str:
        """获取缓存文件路径"""
        cache_key = self._get_cache_key(query)
        return os.path.join(self.cache_dir, cache_key)
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cache_time = data.get('timestamp', 0)
                return (time.time() - cache_time) < self.cache_expiry
        except Exception:
            return False
    
    def _load_from_cache(self, cache_path: str) -> Optional[str]:
        """从缓存加载结果"""
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('result', '')
        except Exception:
            return None
    
    def _save_to_cache(self, cache_path: str, query: str, result: str):
        """保存结果到缓存"""
        try:
            data = {
                'query': query,
                'result': result,
                'timestamp': time.time()
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [Cache] 保存缓存失败：{e}")
    
    def search(self, query: str, use_cache: bool = True) -> str:
        """
        执行学术搜索
        
        Args:
            query: 搜索查询
            use_cache: 是否使用缓存
            
        Returns:
            搜索结果字符串
        """
        # 检查缓存
        if use_cache:
            cache_path = self._get_cache_path(query)
            if self._is_cache_valid(cache_path):
                print(f"  [Search] 使用缓存结果：{query[:50]}...")
                return self._load_from_cache(cache_path)
        
        # 执行搜索
        result = None
        for attempt in range(self.max_retries):
            try:
                print(f"  [Search] 正在检索：{query} (第 {attempt + 1}/{self.max_retries} 次尝试)...")
                
                with DDGS() as ddgs:
                    # DuckDuckGo 搜索
                    results = ddgs.text(query, max_results=10)
                    
                    if not results:
                        print("  [Search] 未找到相关结果")
                        result = "未找到相关学术资料。"
                        break
                    
                    # 格式化搜索结果
                    formatted_results = []
                    for i, r in enumerate(results, 1):
                        formatted_results.append(
                            f"[{i}] {r.get('title', '无标题')}\n"
                            f"    链接：{r.get('href', '无链接')}\n"
                            f"    摘要：{r.get('body', '无摘要')}\n"
                        )
                    
                    result = "\n".join(formatted_results)
                    print(f"  [Search] 成功找到 {len(results)} 条结果")
                    break
                    
            except Exception as e:
                print(f"  [Search Error] 检索失败：{e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # 指数退避
                else:
                    result = f"检索失败：{str(e)}"
        
        # 保存到缓存
        if use_cache and result:
            cache_path = self._get_cache_path(query)
            self._save_to_cache(cache_path, query, result)
        
        return result
    
    def search_arxiv(self, query: str, max_results: int = 5) -> str:
        """
        搜索 arXiv 论文（简化版，使用 DuckDuckGo 模拟）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            格式化结果
        """
        arxiv_query = f"{query} site:arxiv.org"
        print(f"  [Search] 正在检索 arXiv: {query}...")
        
        try:
            with DDGS() as ddgs:
                results = ddgs.text(arxiv_query, max_results=max_results)
                
                if not results:
                    return "arXiv 未找到相关论文。"
                
                formatted = ["【arXiv 论文检索结果】"]
                for i, r in enumerate(results, 1):
                    formatted.append(
                        f"\n[{i}] {r.get('title', '无标题')}\n"
                        f"    链接：{r.get('href', '无链接')}\n"
                        f"    摘要：{r.get('body', '无摘要')[:200]}..."
                    )
                
                return "\n".join(formatted)
                
        except Exception as e:
            return f"arXiv 检索失败：{e}"


# 向后兼容的旧接口
def safe_search_tool(query: str) -> str:
    """
    带异常捕获和重试机制的搜索工具（兼容旧代码）
    """
    search_tool = AcademicSearchTool()
    return search_tool.search(query)
