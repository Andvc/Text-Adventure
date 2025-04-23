"""
数据管理模块包
"""

from .data_manager import (
    configure_data_system,
    get_data_file_path,
    read_data_file,
    get_data_value,
    save_data_file,
    clear_cache
)

__all__ = [
    'configure_data_system',
    'get_data_file_path',
    'read_data_file',
    'get_data_value',
    'save_data_file',
    'clear_cache'
] 