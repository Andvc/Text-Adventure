"""
JSON编辑器配置文件

存储编辑器的全局配置和路径信息
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# 编辑器相关路径
EDITOR_DIR = Path(__file__).parent.absolute()

# 数据文件目录
DATA_TEXT_DIR = PROJECT_ROOT / "data" / "text"
SAVE_CHARACTERS_DIR = PROJECT_ROOT / "save" / "characters"
STORYLINE_TEMPLATES_DIR = PROJECT_ROOT / "storyline" / "templates"

# 确保所有目录存在
DATA_TEXT_DIR.mkdir(exist_ok=True, parents=True)
SAVE_CHARACTERS_DIR.mkdir(exist_ok=True, parents=True)
STORYLINE_TEMPLATES_DIR.mkdir(exist_ok=True, parents=True)

# 编辑器UI设置
DEFAULT_WINDOW_SIZE = (1200, 800)
DEFAULT_FONT = ("Arial", 11)
HEADER_FONT = ("Arial", 12, "bold")
CODE_FONT = ("Courier New", 12)

# JSON缩进设置
JSON_INDENT = 2

# 文件类型定义
FILE_TYPES = {
    "data": {
        "name": "游戏数据",
        "dir": DATA_TEXT_DIR,
        "pattern": "*.json",
        "icon": "📝"
    },
    "save": {
        "name": "存档数据",
        "dir": SAVE_CHARACTERS_DIR,
        "pattern": "*.json",
        "icon": "💾"
    },
    "template": {
        "name": "故事模板",
        "dir": STORYLINE_TEMPLATES_DIR,
        "pattern": "*.json",
        "icon": "📋"
    }
} 