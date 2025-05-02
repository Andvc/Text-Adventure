"""
游戏数据管理模块
"""

from .data_manager import (
    configure_data_system,
    get_save_path,
    load_save,
    get_save_value,
    save_data,
    clear_cache,
    get_nested_save_value,
    get_indexed_save,
    list_saves,
    create_save,
    delete_save,
    rename_save,
)

__all__ = [
    'configure_data_system',
    'get_save_path',
    'load_save',
    'get_save_value',
    'save_data',
    'clear_cache',
    'get_nested_save_value',
    'get_indexed_save',
    'list_saves',
    'create_save',
    'delete_save',
    'rename_save',
] 