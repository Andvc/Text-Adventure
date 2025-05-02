#!/usr/bin/env python3
"""
简单循环故事生成测试 - 支持玩家选择，无限循环
"""

import os
import sys
import time

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入必要的模块
from storyline.storyline_manager import StorylineManager
from data.data_manager import create_save, load_save, list_saves, save_data

def display_story(current_save):
    """显示当前故事内容"""
    print("\n=== 当前故事 ===")
    print(f"\n故事梗概：\n{current_save['summary']}")
    print(f"\n当前事件：\n{current_save['story']}")
        
    # 显示选项
    print("\n请选择以下选项，或输入自定义选择：")
    choices = [
        current_save['choice1'],
        current_save['choice2'],
        current_save['choice3']
    ]
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    print("0. 退出游戏")
    print("c. 输入自定义选择")

def get_user_choice(current_save):
    """获取用户选择"""
    choices = [
        current_save['choice1'],
        current_save['choice2'],
        current_save['choice3']
    ]
    
    while True:
        try:
            choice = input("\n请输入选择（数字或'c'）：")
            
            if choice == '0':
                return None
            elif choice == 'c':
                custom_choice = input("请输入自定义选择：")
                if custom_choice.strip():
                    return custom_choice
            else:
                index = int(choice) - 1
                if 0 <= index < len(choices):
                    return choices[index]
                
            print("无效的选择，请重试")
        except ValueError:
            print("请输入有效的数字")

def run_story_loop():
    """运行故事循环"""
    # 初始化故事线管理器
    manager = StorylineManager()
        
    # 检查存档是否存在
    save_name = "simple_loop"
    saves = list_saves()
    print(f"当前存档列表: {saves}")
    
    if save_name in saves:
        # 加载现有存档
        current_save = load_save("character", save_name)
        print(f"\n加载现有存档: {save_name}")
        print(f"存档内容: {current_save}")
    else:
        # 创建新存档
        current_save = {
            "id": save_name,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "character": {
                "name": "冒险者",
                "level": "初级魔法师"
            },
            "world": "魔法世界",
            "story": "冒险者站在魔法学院的门口，准备开始他的第一次冒险。",
            "summary": "一位年轻的魔法师开始了他的冒险之旅。",
            "choice1": "探索附近的森林",
            "choice2": "前往魔法图书馆",
            "choice3": "拜访导师",
            "selected_choice": ""
        }
        print(f"\n创建新存档: {save_name}")
        print(f"存档内容: {current_save}")
        create_save("character", save_name, current_save)
    
    # 主循环
    while True:
        # 显示当前故事
        display_story(current_save)
            
        # 获取用户选择
        choice = get_user_choice(current_save)
        if choice is None:
            print("\n游戏结束")
            break
        
        # 更新选择
        current_save['selected_choice'] = choice
        print(f"\n更新选择: {choice}")
        print(f"更新后的存档内容: {current_save}")
        save_result = save_data("character", save_name, current_save)
        print(f"保存结果: {save_result}")
        
        # 生成新故事
        print("\n正在生成新故事...")
        if not manager.generate_story(save_name, "simple_loop"):
            print("故事生成失败")
            break
                
        # 重新加载存档以获取新内容
        current_save = load_save("character", save_name)
        print(f"重新加载的存档内容: {current_save}")

if __name__ == "__main__":
    run_story_loop() 