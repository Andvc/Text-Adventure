"""
文字冒险游戏的故事线管理模块

本模块提供故事线创建、编辑和管理功能，
支持与AI模块和角色属性模块集成。
"""

import os
from pathlib import Path

# 定义模块路径
MODULE_PATH = Path(__file__).parent.absolute()
TEMPLATES_PATH = Path(os.path.join(os.path.dirname(__file__), "templates"))
TOOLS_PATH = MODULE_PATH / "tools"

# 确保目录存在
TEMPLATES_PATH.mkdir(exist_ok=True)
TOOLS_PATH.mkdir(exist_ok=True)

# 从模块中导出核心类和函数
from .storyline_manager import StorylineManager

__all__ = ["StorylineManager"] 