# Author: YN
# CreaTime: 2026/3/4
# Filename: user_input
"""
用户输入工具模块
支持多种方式的审稿意见输入
"""

import os
from typing import Optional


def get_user_review_feedback() -> Optional[str]:
    """
    获取用户的审稿意见
    
    支持多种输入方式：
    1. 键盘输入（适合短文本，<500 字）
    2. 文件上传（支持 .txt/.md 文件）
    3. 粘贴输入（适合长文本）
    4. 使用自动生成的意见（默认）
    
    Returns:
        用户输入的审稿意见，如果选择使用自动生成的意见则返回 None
    """
    print("\n" + "="*70)
    print(" " * 20 + "📝 请输入您的审稿意见")
    print("="*70)
    print("1. 键盘输入（适合短文本，<500 字）")
    print("2. 文件上传（支持 .txt/.md 文件，建议放在 inputs/ 目录）")
    print("3. 粘贴输入（适合长文本，可直接复制期刊/导师意见）")
    print("4. 使用自动生成的意见（推荐用于快速测试）")
    print("="*70)
    
    choice = input("请选择输入方式（1-4，默认为 4）：").strip()
    
    if choice == "1":
        return keyboard_input()
    elif choice == "2":
        return file_upload()
    elif choice == "3":
        return paste_input()
    elif choice == "" or choice == "4":
        print("  [System] 使用自动生成的审稿意见")
        return None
    else:
        print("  [System] 无效选项，默认使用自动生成的意见")
        return None


def keyboard_input() -> str:
    """
    键盘输入审稿意见（适合短文本）
    
    Returns:
        用户输入的审稿意见
    """
    print("\n" + "-"*70)
    print("请输入您的审稿意见（输入 'END' 单独一行结束）：")
    print("-"*70)
    
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    
    feedback = "\n".join(lines)
    
    if len(feedback) < 10:
        print("  [Warning] 输入内容过短，可能不足以指导修改")
    
    print(f"  [Input] 已接收 {len(feedback)} 字符的审稿意见")
    
    return feedback


def file_upload() -> Optional[str]:
    """
    从文件上传审稿意见
    
    Returns:
        文件内容，如果文件不存在或读取失败则返回 None
    """
    print("\n" + "-"*70)
    print("文件上传模式")
    print("-"*70)
    
    # 提示用户将文件放在 inputs/ 目录
    print("\n请将审稿意见文件放在 inputs/ 目录中")
    print("支持的文件格式：.txt, .md")
    
    # 创建 inputs 目录（如果不存在）
    inputs_dir = "inputs"
    if not os.path.exists(inputs_dir):
        os.makedirs(inputs_dir)
        print(f"  [System] 已创建 inputs/ 目录")
    
    # 列出可用文件
    if os.path.exists(inputs_dir):
        files = [f for f in os.listdir(inputs_dir) if f.endswith(('.txt', '.md'))]
        if files:
            print(f"\n  可用文件：{', '.join(files)}")
    
    filename = input("\n请输入文件名（包括扩展名）：").strip()
    
    if not filename:
        print("  [Warning] 未输入文件名，使用自动生成的意见")
        return None
    
    filepath = os.path.join(inputs_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"  [Error] 文件不存在：{filepath}")
        print("  [System] 使用自动生成的意见")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"  [File] 已读取 {len(content)} 字符的审稿意见")
        print(f"  [File] 文件路径：{filepath}")
        
        return content
        
    except Exception as e:
        print(f"  [Error] 读取文件失败：{e}")
        print("  [System] 使用自动生成的意见")
        return None


def paste_input() -> str:
    """
    粘贴输入审稿意见（适合长文本）
    
    Returns:
        用户粘贴的审稿意见
    """
    print("\n" + "-"*70)
    print("粘贴输入模式")
    print("-"*70)
    print("\n请将您的审稿意见复制到剪贴板，然后粘贴到下方")
    print("输入完成后，输入 'END' 单独一行结束：")
    print("-"*70)
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        except EOFError:
            print("\n  [Warning] 检测到 EOF，结束输入")
            break
    
    feedback = "\n".join(lines)
    
    if len(feedback) < 10:
        print("  [Warning] 输入内容过短，可能不足以指导修改")
    
    print(f"  [Input] 已接收 {len(feedback)} 字符的审稿意见")
    
    return feedback


def get_user_custom_modification(draft: str, feedback: str) -> Optional[str]:
    """
    获取用户对论文的自定义修改
    
    Args:
        draft: 当前论文草稿
        feedback: 审稿意见
        
    Returns:
        用户的自定义修改内容，如果不需要自定义修改则返回 None
    """
    print("\n" + "="*70)
    print(" " * 20 + "🔧 是否需要自定义修改？")
    print("="*70)
    print("1. 是，我有具体的修改要求（请描述）")
    print("2. 否，使用 Writer 节点自动修改")
    print("="*70)
    
    choice = input("请选择（1-2，默认为 2）：").strip()
    
    if choice == "1":
        print("\n请输入您的具体修改要求（输入 'END' 单独一行结束）：")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            except EOFError:
                break
        
        return "\n".join(lines)
    else:
        return None


def save_user_feedback(feedback: str, topic: str):
    """
    保存用户反馈到历史记录
    
    Args:
        feedback: 用户反馈内容
        topic: 论文主题
    """
    history_dir = "history"
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_feedback_{topic[:20]}_{timestamp}.txt"
    filepath = os.path.join(history_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"主题：{topic}\n")
            f.write(f"时间：{timestamp}\n")
            f.write("="*70 + "\n\n")
            f.write(feedback)
        
        print(f"  [History] 用户反馈已保存到：{filepath}")
    except Exception as e:
        print(f"  [Warning] 保存用户反馈失败：{e}")
