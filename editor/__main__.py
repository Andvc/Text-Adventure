"""
JSON编辑器主入口

提供命令行运行入口点
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 导入编辑器主类
from editor.json_editor import JsonEditor


def main():
    """编辑器主函数"""
    editor = JsonEditor()
    editor.run()


if __name__ == "__main__":
    main() 