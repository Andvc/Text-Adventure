"""
测试storyline模块直接使用角色属性的功能

这个脚本演示storyline模块直接从character模块获取角色数据生成故事
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
    get_all_attributes,
    configure_save_system
)

# 导入故事线模块
from storyline.storyline_manager import StorylineManager

def setup_character():
    """创建一个测试用角色"""
    print("========== 创建角色 ==========")
    
    # 配置存档位置为测试存档
    configure_save_system(save_file="test_character_integration.json")
    
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
    
    # 添加一些自定义属性
    create_attribute("location", "古道森林")
    create_attribute("world_setting", "仙侠世界")
    
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
    print("当前位置:", get_attribute("location"))
    print("世界设定:", get_attribute("world_setting"))

def generate_adventure_from_character():
    """直接从角色属性生成冒险故事"""
    print("\n========== 从角色属性生成冒险故事 ==========")
    
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 直接使用角色属性生成故事
    print("正在使用角色属性生成故事，请稍候...")
    
    story = manager.generate_story_from_character("adventure_template")
    if not story:
        print("故事生成失败")
        return None
    
    return story

def display_story_and_make_choice(story):
    """显示生成的故事和选择，并让用户做出选择"""
    print("\n========== 故事内容 ==========\n")
    print(story.content)
    
    print("\n========== 可用选择 ==========\n")
    for i, choice in enumerate(story.choices, 1):
        print(f"{i}. {choice.text}")
        if choice.outcome:
            print(f"   结果: {choice.outcome}")
        if choice.stat_changes:
            print(f"   属性变化: {choice.stat_changes}")
    
    # 选择选项
    while True:
        try:
            choice = input("\n请选择一个选项 (1-3): ")
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(story.choices):
                return choice_index
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入一个有效的数字")

def continue_adventure(manager, story, choice_index):
    """继续冒险故事"""
    print("\n========== 继续冒险 ==========")
    
    # 使用角色属性和选择继续故事
    print("正在根据你的选择继续故事，请稍候...")
    
    next_story = manager.continue_story_from_character(story, choice_index)
    if not next_story:
        print("继续故事失败")
        return None
    
    return next_story

def main():
    """主函数"""
    print("开始测试storyline模块与角色属性集成\n")
    
    # 设置角色
    setup_character()
    
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 生成故事
    story = generate_adventure_from_character()
    
    # 显示故事并让用户做出选择
    if story:
        # 第一回合
        choice_index = display_story_and_make_choice(story)
        print(f"\n你选择了选项 {choice_index + 1}")
        
        # 获取选择前的角色属性
        print("\n选择前的角色属性:")
        print(f"力量: {get_attribute('strength')}")
        print(f"敏捷: {get_attribute('agility')}")
        print(f"智力: {get_attribute('intelligence')}")
        
        # 继续故事
        next_story = continue_adventure(manager, story, choice_index)
        
        # 显示更新后的角色属性
        print("\n选择后的角色属性:")
        print(f"力量: {get_attribute('strength')}")
        print(f"敏捷: {get_attribute('agility')}")
        print(f"智力: {get_attribute('intelligence')}")
        
        # 显示下一个故事段落
        if next_story:
            display_story_and_make_choice(next_story)
            print("\n测试完成!")
        else:
            print("\n无法继续故事")
    else:
        print("\n测试未完成，无法生成故事")

if __name__ == "__main__":
    main() 