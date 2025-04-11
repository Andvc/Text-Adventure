"""
故事线工具模块主入口

可通过以下方式启动:
- python -m storyline.tools
- python -m storyline.tools template_editor
"""

import sys
import argparse

def main():
    """故事线工具入口函数"""
    parser = argparse.ArgumentParser(description="故事线模块工具集")
    parser.add_argument("tool", nargs="?", default="template_editor", 
                       choices=["template_editor"],
                       help="要运行的工具")
    
    args = parser.parse_args()
    
    # 加载并运行编辑器
    from storyline.tools.template_editor import run_editor
    run_editor()

if __name__ == "__main__":
    main() 