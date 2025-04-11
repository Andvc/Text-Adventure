#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：用于测试adventure_template模板

这个脚本会创建一些角色属性，然后使用adventure_template模板生成一个故事。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

# 导入必要的模块
from character.character_manager import create_attribute, get_attribute, get_all_attributes
from storyline.storyline_manager import StorylineManager

def main():
    """主函数：测试adventure_template模板"""
    print("===== 开始测试 adventure_template 模板 =====")
    
    # 清空并设置角色属性
    setup_character()
    
    # 显示当前角色属性
    print("\n当前角色属性:")
    display_attributes()
    
    # 初始化故事管理器
    manager = StorylineManager()
    
    # 列出可用模板
    templates = manager.list_templates()
    print(f"\n可用模板: {[t['id'] for t in templates]}")
    
    # 检查adventure_template是否存在
    if not any(t['id'] == 'adventure_template' for t in templates):
        print("错误: adventure_template模板不存在！")
        return
    
    print("\n使用adventure_template生成故事...\n")
    
    try:
        # 生成故事
        story_content, choices, story_id = manager.generate_story("adventure_template")
        
        # 显示故事内容
        print("生成的故事：")
        print("=" * 50)
        print(story_content)
        print("=" * 50)
        
        # 显示选择选项
        print("\n可用选择：")
        for i, choice in enumerate(choices):
            print(f"{i+1}. {choice['text']}")
        
        # 做出选择
        choice_index = 0  # 选择第一个选项
        print(f"\n选择选项 {choice_index+1}")
        
        # 执行选择
        manager.make_choice(story_id, choice_index)
        
        # 显示更新后的角色属性
        print("\n选择后的角色属性:")
        display_attributes()
        
        print("\n测试成功完成！")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

def setup_character():
    """设置角色属性"""
    # 基本信息
    create_attribute("name", "李逍遥")
    create_attribute("background", "一位生活在边远山村的少年，向往冒险与精彩的生活")
    create_attribute("world_setting", "一个融合了古代中国与奇幻元素的世界，充满神秘力量和古老传说")
    create_attribute("location", "古老的迷雾森林")
    
    # 属性值
    create_attribute("力量", 8)
    create_attribute("敏捷", 12)
    create_attribute("智力", 10)
    create_attribute("体质", 9)
    create_attribute("魅力", 11)
    
    # 装备和物品
    create_attribute("武器", "青铜短剑")
    create_attribute("防具", "轻便皮甲")
    create_attribute("背包物品", ["干粮", "水袋", "火石", "短绳", "药草"])

def display_attributes():
    """显示当前所有角色属性"""
    attributes = get_all_attributes()
    for key, value in attributes.items():
        if isinstance(value, list):
            value_str = ", ".join(str(item) for item in value)
            print(f"{key}: [{value_str}]")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    main() 