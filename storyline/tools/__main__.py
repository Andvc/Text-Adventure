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
                       choices=["template_editor", "simplified_template_editor"],
                       help="要运行的工具")
    
    args = parser.parse_args()
    
    if args.tool == "template_editor":
        # 提供一个使用旧版编辑器的选项，但不推荐
        print("注意: 正在启动旧版模板编辑器，建议使用简化版模板编辑器，可通过 --tool simplified_template_editor 启动")
        from storyline.tools.template_editor import run_editor
        run_editor()
    elif args.tool == "simplified_template_editor":
        # 默认使用简化版编辑器
        from storyline.tools.simplified_template_editor import run_editor
        run_editor()

if __name__ == "__main__":
    main() 