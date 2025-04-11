"""
故事线模块主入口

可通过以下方式启动:
- python -m storyline
"""

def main():
    """故事线模块入口函数，默认启动模板编辑器"""
    
    # 启动模板编辑器
    from storyline.tools.template_editor import run_editor
    run_editor()

if __name__ == "__main__":
    main() 