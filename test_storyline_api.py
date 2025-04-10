"""
测试storyline模块的API调用

这个脚本测试调用已有的故事模板，实际使用API生成故事内容。
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

def setup_character():
    """创建一个测试用角色"""
    print("========== 创建角色 ==========")
    
    # 配置存档位置为测试存档
    configure_save_system(save_file="test_storyline_api.json")
    
    # 创建角色基本信息
    create_attribute("name", "李逍遥")
    create_attribute("gender", "男")
    create_attribute("background", "自小在青青的山野长大，性格乐观开朗，身手敏捷。"
                              "在一次上山采药时，偶然发现了一本古籍《御剑术》，"
                              "自此开始修习剑法，并立志成为一名行侠仗义的剑客。")
    
    # 创建角色属性
    create_attribute("strength", 8)       # 力量
    create_attribute("agility", 12)       # 敏捷
    create_attribute("intelligence", 10)  # 智力
    create_attribute("constitution", 9)   # 体质
    create_attribute("charisma", 11)      # 魅力
    
    # 技能和装备
    create_attribute("skills", ["基础剑法", "轻功", "药理知识"])
    create_attribute("equipment", {"weapon": "青锋剑", "armor": "布衣", "accessory": "药草包"})
    
    # 显示角色信息
    print(f"角色创建完成: {get_attribute('name')}")
    print(f"性别: {get_attribute('gender')}")
    print(f"背景: {get_attribute('background')}")
    print("\n属性:")
    print(f"力量: {get_attribute('strength')}")
    print(f"敏捷: {get_attribute('agility')}")
    print(f"智力: {get_attribute('intelligence')}")
    print(f"体质: {get_attribute('constitution')}")
    print(f"魅力: {get_attribute('charisma')}")
    
    print("\n技能:", get_attribute("skills"))
    print("装备:", get_attribute("equipment"))

def generate_adventure():
    """生成冒险故事"""
    print("\n========== 生成冒险故事 ==========")
    
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 加载冒险模板
    template = manager.load_template("adventure_template")
    if not template:
        print("无法加载adventure_template模板")
        return None
    
    print(f"已加载模板: {template['name']}")
    
    # 准备变量
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
    print("开始测试storyline模块API调用\n")
    
    # 设置角色
    setup_character()
    
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