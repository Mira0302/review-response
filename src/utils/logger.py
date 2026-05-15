# Author: YN
# CreaTime: 2026/3/4
# Filename: logger
"""
日志系统模块
提供统一的日志记录功能
"""

import os
import logging
from datetime import datetime
from typing import Optional


class PaperLogger:
    """论文生成日志器"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 生成日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"paper_generation_{timestamp}.log")
        
        # 配置日志格式
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.date_format = '%Y-%m-%d %H:%M:%S'
        
        # 创建 logger
        self.logger = logging.getLogger('PaperGeneration')
        self.logger.setLevel(logging.DEBUG)
        
        # 文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(self.log_format, self.date_format))
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_agent_action(self, agent_name: str, action: str, details: str = ""):
        """
        记录 Agent 动作
        
        Args:
            agent_name: Agent 名称
            action: 动作
            details: 详细信息
        """
        self.logger.info(f"[{agent_name}] {action} - {details}")
    
    def log_search(self, source: str, query: str, results_count: int):
        """
        记录搜索操作
        
        Args:
            source: 搜索源
            query: 搜索查询
            results_count: 结果数量
        """
        self.logger.info(f"[Search] {source}: {query[:50]}... - {results_count} results")
    
    def log_error(self, error_type: str, error_message: str, context: str = ""):
        """
        记录错误
        
        Args:
            error_type: 错误类型
            error_message: 错误信息
            context: 上下文
        """
        self.logger.error(f"[{error_type}] {error_message} - {context}")
    
    def log_workflow(self, step: str, status: str, details: str = ""):
        """
        记录工作流步骤
        
        Args:
            step: 步骤名称
            status: 状态
            details: 详细信息
        """
        self.logger.info(f"[Workflow] {step} - {status} - {details}")
    
    def log_file_operation(self, operation: str, filepath: str, status: str = "success"):
        """
        记录文件操作
        
        Args:
            operation: 操作类型
            filepath: 文件路径
            status: 状态
        """
        self.logger.info(f"[File] {operation}: {filepath} - {status}")
    
    def get_log_file(self) -> str:
        """获取日志文件路径"""
        return self.log_file
    
    def close(self):
        """关闭 logger"""
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)


# 全局日志器实例
_global_logger: Optional[PaperLogger] = None


def get_logger() -> PaperLogger:
    """获取全局日志器实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = PaperLogger()
    return _global_logger


def log_agent_action(agent_name: str, action: str, details: str = ""):
    """便捷函数：记录 Agent 动作"""
    get_logger().log_agent_action(agent_name, action, details)


def log_search(source: str, query: str, results_count: int):
    """便捷函数：记录搜索操作"""
    get_logger().log_search(source, query, results_count)


def log_error(error_type: str, error_message: str, context: str = ""):
    """便捷函数：记录错误"""
    get_logger().log_error(error_type, error_message, context)


def log_workflow(step: str, status: str, details: str = ""):
    """便捷函数：记录工作流步骤"""
    get_logger().log_workflow(step, status, details)


def log_file_operation(operation: str, filepath: str, status: str = "success"):
    """便捷函数：记录文件操作"""
    get_logger().log_file_operation(operation, filepath, status)
