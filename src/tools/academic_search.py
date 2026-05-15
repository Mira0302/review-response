# Author: YN
# CreaTime: 2026/3/4
# Filename: academic_search
"""
学术搜索工具模块
支持多个学术资源 API：arXiv, Google Scholar, Semantic Scholar, PubMed, IEEE
"""

import os
import time
import json
import arxiv
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime
from duckduckgo_search import DDGS


class AcademicSearchManager:
    """
    学术搜索管理器
    统一接口，支持多个学术资源 API
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self.max_retries = 3
        self.retry_delay = 2
        
        # 创建缓存目录
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # 初始化各个 API 客户端
        self.arxiv_client = arxiv.Client()
        self.ddgs = DDGS()
        
        # API 配置
        self.semanticscholar_api = "https://api.semanticscholar.org/graph/v1/paper"
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
        # 搜索结果缓存
        self.cache = {}
    
    def _get_cache_key(self, query: str, source: str) -> str:
        """生成缓存键"""
        return f"search_{source}_{hash(query) & 0xFFFFFFFF}.json"
    
    def _save_cache(self, query: str, source: str, results: List[Dict]):
        """保存搜索结果到缓存"""
        cache_key = self._get_cache_key(query, source)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        data = {
            'query': query,
            'source': source,
            'results': results,
            'timestamp': time.time()
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [Cache] 保存失败：{e}")
    
    def _load_cache(self, query: str, source: str) -> Optional[List[Dict]]:
        """从缓存加载搜索结果"""
        cache_key = self._get_cache_key(query, source)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 检查缓存有效期（24 小时）
                if time.time() - data.get('timestamp', 0) < 86400:
                    return data.get('results', [])
                else:
                    return None
        except Exception:
            return None
    
    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        搜索 arXiv 预印本论文
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            格式化结果列表
        """
        print(f"  [arXiv] 正在检索：{query[:50]}...")
        
        # 检查缓存
        cached = self._load_cache(query, 'arxiv')
        if cached:
            print(f"  [arXiv] 使用缓存，找到 {len(cached)} 条结果")
            return cached
        
        try:
            # 使用 arxiv API
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for paper in self.arxiv_client.results(search):
                results.append({
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'abstract': paper.summary,
                    'pdf_url': paper.pdf_url,
                    'published': paper.published.strftime('%Y-%m-%d') if paper.published else 'Unknown',
                    'source': 'arXiv',
                    'identifier': paper.get_short_id()
                })
            
            print(f"  [arXiv] 成功检索到 {len(results)} 条结果")
            self._save_cache(query, 'arxiv', results)
            
            return results
            
        except Exception as e:
            print(f"  [arXiv] 检索失败：{e}")
            return []
    
    def search_semanticscholar(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        搜索 Semantic Scholar 论文
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            格式化结果列表
        """
        print(f"  [Semantic Scholar] 正在检索：{query[:50]}...")
        
        # 检查缓存
        cached = self._load_cache(query, 'semanticscholar')
        if cached:
            print(f"  [Semantic Scholar] 使用缓存，找到 {len(cached)} 条结果")
            return cached
        
        # Semantic Scholar API 速率限制处理
        max_retries = 3
        retry_delay = 3  # 秒
        
        for attempt in range(max_retries):
            try:
                # 使用 Semantic Scholar API
                url = f"{self.semanticscholar_api}/search"
                params = {
                    'query': query,
                    'limit': max_results,
                    'fields': 'title,authors,abstract,venue,year,publicationDate,citationCount,openAccessPdf'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                # 处理速率限制错误
                if response.status_code == 429:
                    print(f"  [Semantic Scholar] 速率限制（429），等待 {retry_delay} 秒后重试 ({attempt+1}/{max_retries})...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    continue
                
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                for paper in data.get('data', []):
                    results.append({
                        'title': paper.get('title', 'Unknown'),
                        'authors': [author.get('name', 'Unknown') for author in paper.get('authors', [])],
                        'abstract': paper.get('abstract', 'No abstract available'),
                        'venue': paper.get('venue', 'Unknown'),
                        'year': paper.get('year', 'Unknown'),
                        'citation_count': paper.get('citationCount', 0),
                        'pdf_url': paper.get('openAccessPdf', {}).get('url', 'N/A'),
                        'source': 'Semantic Scholar',
                        'paper_id': paper.get('paperId', 'Unknown')
                    })
                
                print(f"  [Semantic Scholar] 成功检索到 {len(results)} 条结果")
                self._save_cache(query, 'semanticscholar', results)
                
                return results
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"  [Semantic Scholar] 请求失败 ({attempt+1}/{max_retries})：{e}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                print(f"  [Semantic Scholar] 检索失败：{e}")
                return []
            except Exception as e:
                print(f"  [Semantic Scholar] 检索失败：{e}")
                return []
        
        print(f"  [Semantic Scholar] 超过最大重试次数，返回空结果")
        return []
    
    def search_pubmed(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        搜索 PubMed 医学文献
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            格式化结果列表
        """
        print(f"  [PubMed] 正在检索：{query[:50]}...")
        
        # 检查缓存
        cached = self._load_cache(query, 'pubmed')
        if cached:
            print(f"  [PubMed] 使用缓存，找到 {len(cached)} 条结果")
            return cached
        
        try:
            # 使用 PubMed API (ESearch)
            esearch_url = f"{self.pubmed_base_url}/esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json'
            }
            
            response = requests.get(esearch_url, params=params, timeout=10)
            response.raise_for_status()
            
            esearch_data = response.json()
            pmids = esearch_data.get('esearchresult', {}).get('idlist', [])
            
            if not pmids:
                print(f"  [PubMed] 未找到相关文献")
                return []
            
            # 使用 EFetch 获取详细信息
            efetch_url = f"{self.pubmed_base_url}/efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'json'
            }
            
            response = requests.get(efetch_url, params=params, timeout=10)
            response.raise_for_status()
            
            efetch_data = response.json()
            
            results = []
            for uid in pmids:
                paper = efetch_data.get('result', {}).get(uid, {})
                results.append({
                    'title': paper.get('title', 'Unknown'),
                    'authors': [author.get('name') for author in paper.get('authors', [])],
                    'abstract': paper.get('abstract', 'No abstract available'),
                    'journal': paper.get('source', 'Unknown'),
                    'year': paper.get('pubdate', {}).get('year', 'Unknown'),
                    'source': 'PubMed',
                    'pmid': uid
                })
            
            print(f"  [PubMed] 成功检索到 {len(results)} 条结果")
            self._save_cache(query, 'pubmed', results)
            
            return results
            
        except Exception as e:
            print(f"  [PubMed] 检索失败：{e}")
            return []
    
    def search_google_scholar(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        搜索 Google Scholar（通过 DuckDuckGo 模拟）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            格式化结果列表
        """
        print(f"  [Google Scholar] 正在检索：{query[:50]}...")
        
        # 检查缓存
        cached = self._load_cache(query, 'googlescholar')
        if cached:
            print(f"  [Google Scholar] 使用缓存，找到 {len(cached)} 条结果")
            return cached
        
        try:
            # 使用 DuckDuckGo 模拟 Google Scholar 搜索
            scholar_query = f"{query} site:scholar.google.com"
            results = self.ddgs.text(scholar_query, max_results=max_results)
            
            formatted_results = []
            for r in results:
                formatted_results.append({
                    'title': r.get('title', 'Unknown'),
                    'abstract': r.get('body', 'No abstract available'),
                    'url': r.get('href', 'N/A'),
                    'source': 'Google Scholar'
                })
            
            print(f"  [Google Scholar] 成功检索到 {len(formatted_results)} 条结果")
            self._save_cache(query, 'googlescholar', formatted_results)
            
            return formatted_results
            
        except Exception as e:
            print(f"  [Google Scholar] 检索失败：{e}")
            return []
    
    def search_ieee(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        搜索 IEEE Xplore（通过 DuckDuckGo 模拟）
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            格式化结果列表
        """
        print(f"  [IEEE Xplore] 正在检索：{query[:50]}...")
        
        # 检查缓存
        cached = self._load_cache(query, 'ieee')
        if cached:
            print(f"  [IEEE Xplore] 使用缓存，找到 {len(cached)} 条结果")
            return cached
        
        try:
            # 使用 DuckDuckGo 模拟 IEEE Xplore 搜索
            ieee_query = f"{query} site:ieeexplore.ieee.org"
            results = self.ddgs.text(ieee_query, max_results=max_results)
            
            formatted_results = []
            for r in results:
                formatted_results.append({
                    'title': r.get('title', 'Unknown'),
                    'abstract': r.get('body', 'No abstract available'),
                    'url': r.get('href', 'N/A'),
                    'source': 'IEEE Xplore'
                })
            
            print(f"  [IEEE Xplore] 成功检索到 {len(formatted_results)} 条结果")
            self._save_cache(query, 'ieee', formatted_results)
            
            return formatted_results
            
        except Exception as e:
            print(f"  [IEEE Xplore] 检索失败：{e}")
            return []
    
    def search_all(self, query: str, sources: List[str] = None, max_results_per_source: int = 3) -> Dict[str, List[Dict]]:
        """
        同时搜索多个学术资源
        
        Args:
            query: 搜索查询
            sources: 要搜索的源列表，默认全部
            max_results_per_source: 每个源的最大结果数
            
        Returns:
            按源分类的搜索结果字典
        """
        if sources is None:
            sources = ['arxiv', 'semanticscholar', 'pubmed', 'googlescholar', 'ieee']
        
        all_results = {}
        
        for source in sources:
            source = source.lower()
            if source == 'arxiv':
                all_results['arxiv'] = self.search_arxiv(query, max_results_per_source)
            elif source == 'semanticscholar':
                all_results['semanticscholar'] = self.search_semanticscholar(query, max_results_per_source)
            elif source == 'pubmed':
                all_results['pubmed'] = self.search_pubmed(query, max_results_per_source)
            elif source == 'googlescholar':
                all_results['googlescholar'] = self.search_google_scholar(query, max_results_per_source)
            elif source == 'ieee':
                all_results['ieee'] = self.search_ieee(query, max_results_per_source)
            else:
                print(f"  [Warning] 未知的搜索源：{source}")
        
        return all_results
    
    def format_results(self, all_results: Dict[str, List[Dict]]) -> str:
        """
        格式化所有搜索结果
        
        Args:
            all_results: 按源分类的搜索结果
            
        Returns:
            格式化后的字符串
        """
        formatted = []
        
        for source, results in all_results.items():
            if not results:
                continue
            
            formatted.append(f"\n{'='*60}")
            formatted.append(f"【{source.upper()} 检索结果】")
            formatted.append(f"{'='*60}")
            
            for i, paper in enumerate(results, 1):
                formatted.append(f"\n[{i}] {paper.get('title', 'Unknown')}")
                formatted.append(f"    作者：{', '.join(paper.get('authors', ['Unknown']))[:100]}...")
                formatted.append(f"    摘要：{paper.get('abstract', 'No abstract')[:200]}...")
                
                if 'pdf_url' in paper:
                    formatted.append(f"    PDF：{paper['pdf_url']}")
                if 'url' in paper:
                    formatted.append(f"    链接：{paper['url']}")
                if 'year' in paper:
                    formatted.append(f"    年份：{paper['year']}")
                if 'citation_count' in paper:
                    formatted.append(f"    引用：{paper['citation_count']}")
        
        return "\n".join(formatted)


# 向后兼容的旧接口
def academic_search(query: str, use_cache: bool = True) -> str:
    """
    学术搜索工具（兼容旧代码）
    """
    manager = AcademicSearchManager()
    
    # 根据查询内容自动选择合适的搜索源
    if 'medical' in query.lower() or 'health' in query.lower() or 'patient' in query.lower():
        sources = ['pubmed', 'arxiv', 'semanticscholar']
    elif 'artificial' in query.lower() or 'ai' in query.lower() or 'machine' in query.lower():
        sources = ['semanticscholar', 'arxiv', 'googlescholar']
    elif 'engineering' in query.lower() or 'electrical' in query.lower():
        sources = ['ieee', 'arxiv', 'semanticscholar']
    else:
        sources = ['googlescholar', 'arxiv', 'semanticscholar']
    
    all_results = manager.search_all(query, sources=sources, max_results_per_source=3)
    return manager.format_results(all_results)
