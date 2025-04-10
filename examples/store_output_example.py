"""
存储模板输出到角色属性示例

这个示例演示如何使用storyline_manager的增强API将模板输出直接存储到角色属性中。
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
    """主函数，演示模板输出存储功能"""
    # 初始化角色属性
    setup_character()
    
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 显示欢迎信息
    print("=== 模板输出存储示例 ===")
    print("本示例展示如何将模板执行的结果直接存储到角色属性中\n")
    
    # 定义要存储的输出字段
    store_fields = {
        "story": "current_story",  # 将story字段存储到current_story属性
        "choice1": "option1",      # 将choice1字段存储到option1属性
        "choice2": "option2",      # 将choice2字段存储到option2属性
        "choice3": "option3",      # 将choice3字段存储到option3属性
        "content": "story_content" # 将格式化后的故事内容存储到story_content属性
    }
    
    # 显示当前角色属性
    print("\n=== 执行模板前的角色属性 ===")
    display_selected_attributes(["current_story", "option1", "option2", "option3", "story_content"])
    
    # 运行模板并存储输出
    template_id = "adventure_template"  # 确保这个模板已在templates目录中存在
    print(f"\n运行模板并存储输出: {template_id}")
    
    story_content, choices = manager.run_template_and_store(template_id, store_fields=store_fields)
    
    # 显示故事内容
    print("\n=== 生成的故事内容 ===")
    print(story_content)
    
    print("\n=== 生成的选项 ===")
    for choice in choices:
        print(f"{choice['id'] + 1}. {choice['text']}")
    
    # 显示更新后的角色属性
    print("\n=== 执行模板后的角色属性 ===")
    display_selected_attributes(["current_story", "option1", "option2", "option3", "story_content"])
    
    # 选择一个选项并继续故事，同时存储结果
    if choices:
        # 获取当前故事ID
        story_id = next(iter(manager.story_segments))
        choice_idx = 0  # 选择第一个选项
        
        print(f"\n选择选项 {choice_idx + 1}: {choices[choice_idx]['text']}")
        
        # 定义下一步要存储的字段
        next_store_fields = {
            "story": "next_story",
            "choice1": "next_option1",
            "choice2": "next_option2",
            "content": "next_content"
        }
        
        # 执行选择并存储结果
        next_content, next_choices = manager.make_choice_and_store(
            story_id, choice_idx, store_fields=next_store_fields
        )
        
        # 显示下一个故事内容
        print("\n=== 下一段故事内容 ===")
        print(next_content)
        
        # 显示最终的角色属性
        print("\n=== 最终角色属性 ===")
        display_selected_attributes([
            "current_story", "option1", "option2", "option3",
            "next_story", "next_option1", "next_option2", 
            "story_content", "next_content"
        ])
    
    print("\n=== 示例结束 ===")

def setup_character():
    """设置角色属性用于示例"""
    # 创建基本属性
    create_attribute("name", "李逍遥")
    create_attribute("background", "自小在山野长大的少年，性格乐观开朗")
    create_attribute("strength", 8, "basic_stats")
    create_attribute("agility", 12, "basic_stats")
    create_attribute("intelligence", 10, "basic_stats")
    create_attribute("constitution", 9, "basic_stats")
    create_attribute("charisma", 11, "basic_stats")
    
    # 创建技能
    create_attribute("skills", ["基础剑法", "轻功", "药理知识"], "abilities")
    
    # 创建装备
    create_attribute("equipment", {
        "weapon": "青锋剑",
        "armor": "布衣",
        "accessory": "玉佩"
    }, "inventory")
    
    # 添加一些其他属性
    create_attribute("location", "南疆边境")
    create_attribute("quest_active", "寻找神秘药师")

def display_selected_attributes(attr_names):
    """显示选定的角色属性"""
    all_attrs = get_all_attributes()
    
    for name in attr_names:
        if name in all_attrs:
            value = all_attrs[name]
            # 处理长文本显示
            if isinstance(value, str) and len(value) > 50:
                value_display = value[:47] + "..."
            else:
                value_display = value
            print(f"{name}: {value_display}")
        else:
            print(f"{name}: <未设置>")

if __name__ == "__main__":
    main() 