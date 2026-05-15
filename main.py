# Author:YN
# CreaTime:2026/3/3
# Filename:main
"""
学术论文自动生成 Agent 系统
基于 LangGraph 构建的多 Agent 协作系统
"""

import os
import time
from datetime import datetime
from src import get_paper_flow
from src.utils.file_manager import PaperFileManager
from src.utils.visualization import visualization_manager
from src.utils.logger import get_logger, log_workflow, log_agent_action, log_file_operation

paper_flow = get_paper_flow()


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "="*80)
    print(" "*20 + "🎓 学术论文 Agent 系统 🎓")
    print("="*80)
    print(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("系统架构：Planner → Researcher → Writer → Reviewer (循环)")
    print("搜索源：arXiv, Google Scholar, Semantic Scholar, PubMed, IEEE")
    print("="*80 + "\n")


def run_single_paper(topic: str, max_revisions: int = 3):
    """
    运行单个论文生成任务
    
    Args:
        topic: 论文题目
        max_revisions: 最大修改次数
        
    Returns:
        生成的论文文件路径
    """
    print(f"\n【任务】生成论文：{topic}")
    print(f"【参数】最大修改次数：{max_revisions}\n")
    
    start_time = time.time()
    
    # 初始化日志器
    logger = get_logger()
    log_workflow("start", "running", f"Topic: {topic}")
    
    # 运行工作流
    inputs = {"topic": topic, "revision_count": 0}
    
    try:
        # 使用 stream 模式，实时查看进度
        print("🚀 开始执行工作流...\n")
        
        for output in paper_flow.stream(inputs):
            # stream 输出已经在节点内部处理
            pass
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  执行时间：{elapsed_time:.2f} 秒 ({elapsed_time/60:.2f} 分钟)")
        
        # 获取最终输出
        final_output = paper_flow.invoke(inputs)
        
        print("\n" + "="*80)
        print("🎉 论文生成完成！")
        print("="*80)
        
        # 显示统计信息
        draft = final_output.get("draft", "")
        feedback = final_output.get("feedback", "")
        
        print(f"\n【统计信息】")
        print(f"  - 论文字数：{len(draft)} 字符")
        print(f"  - 修改轮数：{final_output.get('revision_count', 0)}")
        print(f"  - 审稿状态：{final_output.get('feedback', 'Unknown')[:100]}...")
        
        # 保存结果
        file_manager = PaperFileManager()
        filepath_md = file_manager.save_markdown(draft, topic)
        filepath_pdf = file_manager.save_pdf(draft, topic)
        
        log_file_operation("save_markdown", filepath_md)
        if filepath_pdf:
            log_file_operation("save_pdf", filepath_pdf)
        
        print(f"\n【输出文件】")
        print(f"  - Markdown: {filepath_md}")
        if filepath_pdf:
            print(f"  - PDF: {filepath_pdf}")
        
        # 生成工作流图
        workflow图 = visualization_manager.generate_workflow_graph(paper_flow)
        if workflow图:
            print(f"  - Workflow图: {workflow图}")
        
        # 显示输出目录摘要
        summary = file_manager.get_output_summary()
        print(f"  - 总输出文件数：{summary['total_files']}")
        
        # 打印摘要
        summary_data = {
            'topic': topic,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'iterations': final_output.get('revision_count', 0),
            'output_files': {
                'markdown': filepath_md,
                'pdf': filepath_pdf
            }
        }
        visualization_manager.print_summary(summary_data)
        
        log_workflow("complete", "success", f"Topic: {topic}")
        
        return filepath_md
        
    except Exception as e:
        log_error_msg = f"Error: {e}"
        print(f"\n❌ 执行失败：{e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print_banner()
    
    # 用户输入论文主题
    print("\n" + "="*60)
    print(" " * 15 + "📝 请输入论文主题")
    print("="*60)
    print("1. 使用示例主题（快速测试）")
    print("2. 手动输入论文主题（推荐）")
    print("="*60)
    
    choice = input("\n请选择（1-2，默认为 2）：").strip()
    
    if choice == "1":
        # 使用示例论文题目
        test_topics = [
            "基于深度学习的人机协作机械臂装配系统研究",
            "基于大模型的人机协作装配系统研究",
            # "多模态融合的智能机器人感知与决策方法",  # 可以取消注释测试更多题目
        ]
        print(f"\n  [System] 使用示例主题，共 {len(test_topics)} 个")
    else:
        # 用户手动输入主题
        print("\n  [System] 请输入论文主题（输入 'q' 或 'quit' 结束）")
        test_topics = []
        while True:
            topic = input("\n  论文主题：").strip()
            if topic.lower() in ['q', 'quit', 'exit', '']:
                if not test_topics:
                    print("  [System] 未输入任何主题，使用默认主题")
                    test_topics = [
                        "基于深度学习的人机协作机械臂装配系统研究",
                        "基于大模型的人机协作装配系统研究"
                    ]
                break
            test_topics.append(topic)
            print(f"  [System] 已添加主题：{topic}")
        
        print(f"\n  [System] 共 {len(test_topics)} 个主题")
    
    # 运行所有测试题目
    for i, topic in enumerate(test_topics, 1):
        print(f"\n{'='*80}")
        print(f"任务 {i}/{len(test_topics)}")
        print(f"{'='*80}")
        
        run_single_paper(topic)
        
        # 如果是多个任务，中间休息一下
        if i < len(test_topics):
            print("\n⏸️  等待 5 秒后继续下一个任务...")
            time.sleep(5)
    
    print("\n" + "="*80)
    print("🎊 所有任务完成！")
    print("="*80)
    
    # 显示最终输出目录
    file_manager = PaperFileManager()
    summary = file_manager.get_output_summary()
    
    print(f"\n【输出目录】{summary['output_dir']}")
    print(f"【总文件数】{summary['total_files']}")
    print(f"【文件列表】")
    for filename in summary['files']:
        print(f"  - {filename}")
    
    print("\n✨ 提示：输出的 Markdown 文件位于 outputs/ 目录")
    print("✨ 提示：用户反馈保存在 history/ 目录")


if __name__ == "__main__":
    main()