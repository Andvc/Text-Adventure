#!/usr/bin/env python3
"""
文字冒险游戏主程序入口
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入游戏流程控制器
from gameflow.core import GameFlow

def main():
    """主函数"""
    # 初始化游戏流程控制器
    game = GameFlow()
    
    # 运行游戏
    game.run()

if __name__ == "__main__":
    main() 