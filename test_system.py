# Author: YN
# CreaTime: 2026/3/3
# Filename: test_system
"""
系统测试脚本
用于快速验证 Agent 系统的基本功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_api_connection():
    """测试 API 连接"""
    print("\n" + "="*60)
    print("测试 1: API 连接测试")
    print("="*60)
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ 错误：未找到 DEEPSEEK_API_KEY 环境变量")
            return False
        
        # 创建简单的测试请求
        llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
            max_tokens=50
        )
        
        response = llm.invoke([HumanMessage(content="你好，请用一句话介绍你自己")])
        print(f"✅ API 连接成功！")
        print(f"响应：{response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ API 连接失败：{e}")
        return False


def test_search_tool():
    """测试搜索工具"""
    print("\n" + "="*60)
    print("测试 2: 搜索工具测试")
    print("="*60)
    
    try:
        from src.tools.search_tools import AcademicSearchTool
        
        search_tool = AcademicSearchTool()
        
        # 测试简单搜索
        query = "深度学习 机械臂 控制 2024"
        print(f"\n搜索查询：{query}")
        result = search_tool.search(query, use_cache=False)
        
        if result and len(result) > 0:
            print(f"✅ 搜索成功！")
            print(f"结果长度：{len(result)} 字符")
            print(f"结果预览：{result[:200]}...")
            return True
        else:
            print("⚠️  搜索返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 搜索工具测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_manager():
    """测试文件管理器"""
    print("\n" + "="*60)
    print("测试 3: 文件管理器测试")
    print("="*60)
    
    try:
        from src.utils.file_manager import PaperFileManager
        
        file_manager = PaperFileManager()
        
        # 测试保存文件
        test_content = "# 测试论文\n\n这是一个测试内容。"
        test_topic = "测试主题"
        
        filepath = file_manager.save_markdown(test_content, test_topic)
        
        if os.path.exists(filepath):
            print(f"✅ 文件保存成功！")
            print(f"文件路径：{filepath}")
            
            # 验证文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if "测试论文" in content:
                    print(f"✅ 文件内容验证通过！")
                    return True
                else:
                    print("❌ 文件内容验证失败")
                    return False
        else:
            print("❌ 文件保存失败")
            return False
            
    except Exception as e:
        print(f"❌ 文件管理器测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_structure():
    """测试图结构"""
    print("\n" + "="*60)
    print("测试 4: LangGraph 工作流测试")
    print("="*60)
    
    try:
        from src import get_paper_flow as _get_paper_flow
paper_flow = _get_paper_flow()
        
        # 检查图结构
        graph = paper_flow.get_graph()
        
        print(f"✅ 工作流加载成功！")
        print(f"节点数：{len(list(graph.nodes))}")
        print(f"边数：{len(list(graph.edges))}")
        
        # 列出所有节点
        print("\n节点列表:")
        for node in graph.nodes:
            print(f"  - {node}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_mini_workflow():
    """测试迷你工作流（只运行 Planner）"""
    print("\n" + "="*60)
    print("测试 5: 迷你工作流测试（仅 Planner）")
    print("="*60)
    
    try:
        from src import get_paper_flow as _get_paper_flow
paper_flow = _get_paper_flow()
        
        # 只测试第一个节点
        test_input = {"topic": "人工智能在医疗领域的应用"}
        
        print(f"\n测试题目：{test_input['topic']}")
        print("运行 Planner 节点...\n")
        
        # 使用 invoke 运行
        result = paper_flow.invoke(test_input)
        
        if result and "outline" in result:
            print(f"✅ 工作流执行成功！")
            print(f"大纲长度：{len(result['outline'])} 字符")
            print(f"\n大纲预览:\n{result['outline'][:300]}...")
            return True
        else:
            print("❌ 工作流执行失败：未生成大纲")
            return False
            
    except Exception as e:
        print(f"❌ 工作流测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print(" "*25 + "🧪 系统测试套件 🧪")
    print("="*80)
    
    tests = [
        ("API 连接测试", test_api_connection),
        ("搜索工具测试", test_search_tool),
        ("文件管理器测试", test_file_manager),
        ("工作流结构测试", test_graph_structure),
        ("迷你工作流测试", test_mini_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 [{test_name}] 异常：{e}")
            results.append((test_name, False))
        
        # 测试之间稍作停顿
        import time
        time.sleep(1)
    
    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计：{passed}/{total} 个测试通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查相关配置和代码")
        return 1


if __name__ == "__main__":
    sys.exit(main())
