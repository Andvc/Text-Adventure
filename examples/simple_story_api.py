"""
简单故事生成API示例

这个示例演示如何使用storyline_manager的简化API来生成和管理故事。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入相关模块
from storyline.storyline_manager import StorylineManager
from character.character_manager import create_attribute, set_attribute, get_attribute

def main():
    """主函数，演示API的使用"""
    # 初始化角色属性
    setup_character()
    
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 显示欢迎信息
    print("=== 文字冒险游戏示例 ===")
    print("这个示例展示了如何使用简化的故事线API\n")
    
    # 运行模板（自动从角色管理器加载属性）
    template_id = "adventure_template"  # 确保这个模板已在templates目录中存在
    print(f"运行模板: {template_id}")
    
    story_content, choices = manager.run_template(template_id)
    
    # 显示故事内容
    print("\n=== 故事开始 ===")
    print(story_content)
    print("\n=== 可用选择 ===")
    for choice in choices:
        print(f"{choice['id'] + 1}. {choice['text']}")
    
    # 模拟用户选择
    print("\n请选择一个选项(1-3)：")
    try:
        choice_idx = int(input()) - 1
        if choice_idx < 0 or choice_idx >= len(choices):
            print("无效选择，默认选择第一项")
            choice_idx = 0
    except:
        print("无效输入，默认选择第一项")
        choice_idx = 0
    
    # 查找对应故事片段的ID（在实际应用中，你需要追踪这个ID）
    # 这里我们使用manager中最近生成的故事片段
    story_id = next(iter(manager.story_segments))
    
    # 根据选择继续故事
    print(f"\n您选择了: {choices[choice_idx]['text']}")
    
    next_content, next_choices = manager.make_choice(story_id, choice_idx)
    
    # 显示下一个故事片段
    print("\n=== 故事继续 ===")
    print(next_content)
    
    if next_choices:
        print("\n=== 新的选择 ===")
        for choice in next_choices:
            print(f"{choice['id'] + 1}. {choice['text']}")
    else:
        print("\n=== 故事结束 ===")
    
    print("\n感谢使用文字冒险游戏引擎!")

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
    create_attribute("gold", 50, "resources")
    create_attribute("reputation", 5, "social")
    create_attribute("quest_active", "寻找仙草", "quests")

if __name__ == "__main__":
    main() 