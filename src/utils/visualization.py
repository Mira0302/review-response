# Author: YN
# CreaTime: 2026/3/4
# Filename: visualization
"""
可视化工具模块
支持 LangGraph 流程图生成和运行时可视化
"""

import os
from datetime import datetime
from typing import Optional


class VisualizationManager:
    """可视化管理器"""
    
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_workflow_graph(self, graph, filename: str = None) -> Optional[str]:
        """
        生成 LangGraph 工作流图
        
        Args:
            graph: LangGraph 对象
            filename: 输出文件名
            
        Returns:
            文件路径，如果 graphviz 未安装则返回 None
        """
        try:
            from graphviz import Digraph
        except ImportError:
            print("  [Visual] graphviz 未安装，跳过流程图生成")
            print("  [Visual] 请运行：pip install graphviz")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_{timestamp}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            dot = Digraph(comment='学术论文生成系统工作流')
            dot.attr(rankdir='TB', size='12,16')
            dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
            
            # 定义节点
            nodes = {
                'start': {'label': 'START', 'fillcolor': '#90EE90'},
                'planner': {'label': 'Planner\n规划者', 'fillcolor': '#87CEEB'},
                'researcher': {'label': 'Researcher\n研究员', 'fillcolor': '#87CEEB'},
                'writer': {'label': 'Writer\n写作者', 'fillcolor': '#87CEEB'},
                'reviewer': {'label': 'Reviewer\n审稿人', 'fillcolor': '#FFB6C1'},
                'end': {'label': 'END', 'fillcolor': '#FFD700'}
            }
            
            # 添加节点
            for node_id, node_info in nodes.items():
                dot.node(node_id, node_info['label'], **node_info)
            
            # 定义边
            edges = [
                ('start', 'planner'),
                ('planner', 'researcher'),
                ('researcher', 'writer'),
                ('writer', 'reviewer'),
                ('reviewer', 'end'),
                ('reviewer', 'writer', '需要修改'),
                ('writer', 'reviewer', '再次审稿')
            ]
            
            # 添加边
            for edge in edges:
                if len(edge) == 2:
                    dot.edge(edge[0], edge[1])
                else:
                    dot.edge(edge[0], edge[1], label=edge[2])
            
            # 渲染图形
            dot.render(filepath, view=False, format='png', cleanup=True)
            
            print(f"  [Visual] 工作流图已生成：{filepath}.png")
            return f"{filepath}.png"
            
        except Exception as e:
            print(f"  [Visual] 流程图生成失败：{e}")
            return None
    
    def print_progress(self, current_step: str, total_steps: int, step_name: str = ""):
        """
        打印进度条
        
        Args:
            current_step: 当前步骤
            total_steps: 总步骤数
            step_name: 步骤名称
        """
        progress = (current_step / total_steps) * 100
        bar_length = 40
        filled_length = int(bar_length * current_step // total_steps)
        
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        if step_name:
            print(f"\n  [{current_step}/{total_steps}] {step_name}")
        else:
            print(f"\n  [{current_step}/{total_steps}]")
        
        print(f"  {bar} {progress:.1f}%")
    
    def print_agent_status(self, agent_name: str, status: str, details: str = ""):
        """
        打印 Agent 状态
        
        Args:
            agent_name: Agent 名称
            status: 状态
            details: 详细信息
        """
        status_icons = {
            'running': '▶',
            'completed': '✓',
            'pending': '○',
            'error': '✗'
        }
        
        icon = status_icons.get(status, '●')
        
        print(f"\n  {icon} [{agent_name}] {details}")
    
    def print_summary(self, summary_data: dict):
        """
        打印系统运行摘要
        
        Args:
            summary_data: 摘要数据
        """
        print("\n" + "="*60)
        print(" " * 20 + "📊 系统运行摘要")
        print("="*60)
        
        print(f"\n  📝 论文主题：{summary_data.get('topic', 'N/A')}")
        print(f"  📅 生成时间：{summary_data.get('timestamp', 'N/A')}")
        print(f"  🔄 迭代次数：{summary_data.get('iterations', 0)}")
        
        # 搜索统计
        search_stats = summary_data.get('search_stats', {})
        if search_stats:
            print(f"\n  🔍 搜索统计：")
            for source, count in search_stats.items():
                print(f"    - {source}: {count} 次")
        
        # 文件输出
        output_files = summary_data.get('output_files', {})
        if output_files:
            print(f"\n  📂 输出文件：")
            for file_type, filepath in output_files.items():
                if filepath:
                    print(f"    - {file_type.upper()}: {filepath}")
        
        print("\n" + "="*60)


# 创建全局实例
visualization_manager = VisualizationManager()
