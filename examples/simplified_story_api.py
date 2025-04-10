"""
简化故事API示例

这个示例演示了如何使用简化版的故事线管理器API
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入相关模块
from storyline.storyline_manager import StorylineManager
from character.character_manager import create_attribute, set_attribute, get_attribute, get_all_attributes

def main():
    """主函数，演示简化版故事API的使用方法"""
    # 创建角色属性
    setup_character()
    
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 显示欢迎信息
    print("=== 简化故事API示例 ===")
    print("本示例展示如何使用新的简化故事API\n")
    
    # 显示当前角色属性
    print("\n=== 当前角色属性 ===")
    display_attributes()
    
    # 生成故事
    template_id = "adventure_template"  # 确保这个模板已在templates目录中存在
    print(f"\n运行模板: {template_id}")
    
    story_content, choices, story_id = manager.generate_story(template_id)
    
    # 显示故事内容
    print("\n=== 生成的故事内容 ===")
    print(story_content)
    
    print("\n=== 生成的选项 ===")
    for choice in choices:
        print(f"{choice['id'] + 1}. {choice['text']}")
    
    # 在角色属性被更新后显示
    print("\n=== 更新后的角色属性 ===")
    display_attributes()
    
    # 选择一个选项并更新属性
    if choices:
        choice_idx = 0  # 选择第一个选项
        
        print(f"\n选择选项 {choice_idx + 1}: {choices[choice_idx]['text']}")
        
        # 执行选择，应用属性变化
        manager.make_choice(story_id, choice_idx)
        
        # 显示最终属性
        print("\n=== 选择后的角色属性 ===")
        display_attributes()
    
    print("\n=== 示例结束 ===")

def setup_character():
    """初始化角色属性"""
    # 基本属性
    create_attribute("name", "李逍遥")
    create_attribute("gender", "男")
    create_attribute("background", "自小在山野长大的少年，性格乐观开朗")
    
    # 基础属性值
    create_attribute("力量", 8)
    create_attribute("敏捷", 12)
    create_attribute("智力", 10)
    create_attribute("体质", 9)
    create_attribute("魅力", 11)
    
    # 装备
    create_attribute("equipment", {
        "weapon": "青铜短剑",
        "armor": "布衣",
        "accessory": "护身符"
    })
    
    # 所在位置
    create_attribute("location", "青石镇")
    create_attribute("world_setting", "东方幻想世界")

def display_attributes():
    """显示角色的关键属性"""
    attrs = get_all_attributes()
    
    # 显示基本信息
    print(f"姓名: {attrs.get('name', '未知')}")
    print(f"背景: {attrs.get('background', '未知')}")
    
    # 显示属性值
    for attr in ["力量", "敏捷", "智力", "体质", "魅力"]:
        if attr in attrs:
            print(f"{attr}: {attrs[attr]}")
    
    # 显示存储的故事和选择
    if "last_story" in attrs:
        print(f"\n最后故事: {attrs['last_story'][:50]}...")
    
    if "last_choice" in attrs:
        print(f"最后选择: {attrs['last_choice']}")

if __name__ == "__main__":
    main() 