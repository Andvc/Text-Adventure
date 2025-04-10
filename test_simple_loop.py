"""
测试简单循环
"""

import os
import sys
import json
from pathlib import Path

# 导入角色模块
from character.character_manager import (
    create_attribute,
    get_attribute,
    set_attribute,
    configure_save_system
)

# 导入故事线模块
from storyline.storyline_manager import StorylineManager

def generate_adventure():
    """生成冒险故事"""
    print("\n========== 生成冒险故事 ==========")
    
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 加载冒险模板
    template = manager.load_template("simple_loop")
    if not template:
        print("无法加载simple_loop模板")
        return None
    
    print(f"已加载模板: {template['name']}")

    variables = {
        "world_setting": "奇幻世界",
        "character.name": get_attribute("name"),
        "character.background": get_attribute("background"),
        "character.strength": get_attribute("strength"),
        "character.agility": get_attribute("agility"),
        "character.intelligence": get_attribute("intelligence"),
        "character.constitution": get_attribute("constitution"),
        "character.charisma": get_attribute("charisma"),
        "character.skills": get_attribute("skills"),
        "location": "神秘古洞"
    }
    
    print("正在生成故事，请稍候...")
    
    # 生成故事
    story = manager.generate_story(template, variables)
    if not story:
        print("故事生成失败")
        return None
    
    return story

def display_story(story):
    """显示生成的故事和选择"""
    print("\n========== 故事内容 ==========\n")
    print(story.content)
    
    print("\n========== 可用选择 ==========\n")
    for i, choice in enumerate(story.choices, 1):
        print(f"{i}. {choice.text}")
        if choice.outcome:
            print(f"   结果: {choice.outcome}")
        if choice.stat_changes:
            print(f"   属性变化: {choice.stat_changes}")

def main():
    """主函数"""
    print("开始测试\n")
    # 生成故事
    story = generate_adventure()
    
    # 显示故事
    if story:
        display_story(story)
        print("\n测试完成!")
    else:
        print("\n测试未完成，无法生成故事")

if __name__ == "__main__":
    main() 