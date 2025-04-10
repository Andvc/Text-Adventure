"""
变量直接引用示例

这个示例展示了优化后的模板系统如何直接引用和修改角色属性，
无需通过中间变量的转换和映射过程。
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
    """主函数，演示变量直接引用功能"""
    # 初始化角色属性
    setup_character()
    
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 显示欢迎信息
    print("=== 变量直接引用示例 ===")
    print("本示例展示了优化后的模板系统如何直接引用和修改角色属性\n")
    
    # 显示当前角色属性
    print("\n=== 当前角色属性 ===")
    display_attributes(["name", "location", "gold", "inventory.weapon", "current_quest"])
    
    # 运行模板 - 不需要显式传递变量，会自动获取角色属性
    template_id = "adventure_template"  # 确保模板存在
    print(f"\n运行模板: {template_id}")
    
    # 直接运行模板，无需指定变量或映射
    story_content, choices = manager.run_template(template_id)
    
    # 显示故事内容
    print("\n=== 生成的故事内容 ===")
    print(story_content)
    
    print("\n=== 生成的选项 ===")
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice['text']}")
    
    # 显示更新后的角色属性 - 注意属性已经被自动更新
    print("\n=== 模板执行后的角色属性 ===")
    display_attributes(["name", "location", "gold", "inventory.weapon", "current_quest", 
                        "current_story", "option1", "option2", "option3"])
    
    # 执行选择 - 同样会自动更新角色属性
    if choices:
        # 获取当前故事ID
        story_id = next(iter(manager.story_segments))
        choice_idx = 0  # 选择第一个选项
        
        print(f"\n选择选项 {choice_idx + 1}: {choices[choice_idx]['text']}")
        
        # 执行选择 - 不需要指定存储映射
        next_content, next_choices = manager.make_choice(story_id, choice_idx)
        
        # 显示下一个故事内容
        print("\n=== 下一段故事内容 ===")
        print(next_content)
        
        # 显示最终的角色属性 - 注意last_choice_index属性记录了玩家的选择
        print("\n=== 选择后的角色属性 ===")
        display_attributes(["name", "location", "gold", "inventory.weapon", "current_quest",
                          "current_story", "last_choice_index", "story_content"])
    
    print("\n=== 示例结束 ===")

def setup_character():
    """设置初始角色属性"""
    # 基本信息
    create_attribute("name", "李逍遥")
    create_attribute("background", "自小在山野长大的少年，性格乐观开朗")
    create_attribute("location", "大理城")
    
    # 基础属性
    create_attribute("strength", 8)     # 力量
    create_attribute("agility", 12)     # 敏捷
    create_attribute("intelligence", 10)  # 智力
    create_attribute("constitution", 9)   # 体质
    create_attribute("charisma", 11)      # 魅力
    
    # 资源
    create_attribute("gold", 50)         # 金币
    create_attribute("reputation", 0)    # 声望
    
    # 技能
    create_attribute("skills", ["剑术", "轻功", "医术"])
    
    # 物品
    create_attribute("inventory", {
        "weapon": "青锋剑",
        "potion": 3,
        "map": "大理地图"
    })
    
    # 任务
    create_attribute("current_quest", "寻找神秘的仙草")
    create_attribute("quest_progress", 0)

def display_attributes(attr_list):
    """显示指定的角色属性
    
    Args:
        attr_list: 要显示的属性名列表
    """
    for attr_name in attr_list:
        if "." in attr_name:
            # 处理嵌套属性
            parts = attr_name.split(".")
            parent = get_attribute(parts[0])
            if parent and isinstance(parent, dict) and parts[1] in parent:
                value = parent[parts[1]]
                print(f"{attr_name}: {value}")
        else:
            # 处理普通属性
            value = get_attribute(attr_name)
            if value is not None:
                print(f"{attr_name}: {value}")
            else:
                print(f"{attr_name}: [未设置]")

if __name__ == "__main__":
    main() 