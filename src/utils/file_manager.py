# Author: YN
# CreaTime: 2026/3/3
# Filename: file_manager
"""
文件管理工具：负责论文输出、格式化、保存
"""

import os
from datetime import datetime
from typing import Optional


class PaperFileManager:
    """论文文件管理器"""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_filename(self, topic: str, extension: str = "md") -> str:
        """
        生成文件名
        
        Args:
            topic: 论文主题
            extension: 文件扩展名
            
        Returns:
            完整文件路径
        """
        # 清理主题中的非法字符
        safe_topic = "".join(c for c in topic if c.isalnum() or c in " _-")
        safe_topic = safe_topic[:50]  # 限制长度
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_topic}_{timestamp}.{extension}"
        
        return os.path.join(self.output_dir, filename)
    
    def save_markdown(self, content: str, topic: str) -> str:
        """
        保存为 Markdown 格式
        
        Args:
            content: 论文内容
            topic: 论文主题
            
        Returns:
            保存的文件路径
        """
        filepath = self.generate_filename(topic, "md")
        
        # 添加 Markdown 头部
        markdown_content = f"""---
title: {topic}
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

# {topic}

{content}

---
*此论文由 AI Agent 系统自动生成*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"  [File] 已保存 Markdown: {filepath}")
        return filepath
    
    def save_pdf(self, content: str, topic: str) -> Optional[str]:
        """
        保存为 PDF 格式（需要安装 reportlab）
        
        Args:
            content: 论文内容
            topic: 论文主题
            
        Returns:
            保存的文件路径，如果报告库未安装则返回 None
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
        except ImportError:
            print("  [PDF] reportlab 未安装，跳过 PDF 生成")
            print("  [PDF] 请运行：pip install reportlab")
            return None
        
        filepath = self.generate_filename(topic, "pdf")
        
        try:
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            
            # 标题
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, height - 2*cm, topic)
            
            # 作者和日期
            c.setFont("Helvetica", 10)
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.drawCentredString(width / 2, height - 3*cm, f"生成时间：{current_date}")
            
            # 内容（分页处理）
            c.setFont("Helvetica", 11)
            y_position = height - 5*cm
            
            # 简单的文本分页处理
            lines = content.split('\n')
            for line in lines:
                if y_position < 2*cm:
                    c.showPage()
                    c.setFont("Helvetica", 11)
                    y_position = height - 2*cm
                
                # 简单的换行处理
                if len(line) > 80:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line) + len(word) < 80:
                            current_line += word + " "
                        else:
                            c.drawString(2*cm, y_position, current_line.strip())
                            y_position -= 0.5*cm
                            current_line = word + " "
                    if current_line:
                        c.drawString(2*cm, y_position, current_line.strip())
                        y_position -= 0.5*cm
                else:
                    c.drawString(2*cm, y_position, line)
                    y_position -= 0.5*cm
            
            # 页脚
            c.setFont("Helvetica", 8)
            c.drawCentredString(width / 2, 1*cm, "此论文由 AI Agent 系统自动生成")
            
            c.save()
            
            print(f"  [File] 已保存 PDF: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"  [File] PDF 生成失败：{e}")
            return None
    
    def save_plain_text(self, content: str, topic: str) -> str:
        """
        保存为纯文本格式
        
        Args:
            content: 论文内容
            topic: 论文主题
            
        Returns:
            保存的文件路径
        """
        filepath = self.generate_filename(topic, "txt")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  [File] 已保存文本：{filepath}")
        return filepath
    
    def get_output_summary(self) -> dict:
        """
        获取输出目录摘要
        
        Returns:
            包含文件统计信息的字典
        """
        if not os.path.exists(self.output_dir):
            return {"total_files": 0, "files": []}
        
        files = [f for f in os.listdir(self.output_dir) if f.endswith(('.md', '.txt'))]
        
        return {
            "total_files": len(files),
            "files": files,
            "output_dir": self.output_dir
        }
    
    def list_outputs(self) -> list:
        """列出所有输出文件"""
        return self.get_output_summary()["files"]
