#!/usr/bin/env python3
"""
游戏主入口

提供角色创建和能力生成功能的统一入口
"""

import os
import sys

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from gameflow import GameManager

def display_menu():
    """显示主菜单"""
    print("\n===== 文字冒险游戏 =====")
    print("1. 创建新角色")
    print("2. 加载已有角色")
    print("3. 查看角色详情")
    print("4. 生成能力或物品")
    print("5. 查看能力等级")
    print("0. 退出游戏")
    return input("请选择操作: ").strip()

def select_character(game_manager):
    """选择一个角色"""
    characters = game_manager.list_available_characters()
    
    if not characters:
        print("没有可用的角色存档")
        return False
    
    print("\n可用角色列表:")
    for i, char in enumerate(characters, 1):
        print(f"{i}. {char['name']} - {char['race']} {char['career']} (等级: {char['level']}, 纪元: {char['era']})")
    
    try:
        choice = int(input("\n请选择角色 (输入编号): "))
        if 1 <= choice <= len(characters):
            save_id = characters[choice-1]["id"]
            if game_manager.load_character(save_id):
                print(f"已加载角色: {characters[choice-1]['name']}")
                return True
            else:
                print("加载角色失败")
        else:
            print("无效的选择")
    except ValueError:
        print("请输入有效的数字")
    
    return False

def show_character_details(game_manager):
    """显示当前角色的详细信息"""
    character = game_manager.get_current_character()
    
    if not character:
        print("未选择角色")
        return
    
    print("\n===== 角色详情 =====")
    print(f"名称: {character.get('name', '未命名')}")
    print(f"纪元: {character.get('era', {}).get('name', '未知')}")
    print(f"种族: {character.get('race', {}).get('sub_race', '未知')} (主种族: {character.get('race', {}).get('main_race', '未知')})")
    print(f"职业: {character.get('career', {}).get('name', '未知')}")
    
    # 显示角色属性
    stats = character.get('stats', {})
    print("\n属性:")
    print(f"  等级: {stats.get('level', 1)}")
    print(f"  经验: {stats.get('experience', 0)}")
    print(f"  生命: {stats.get('health', 0)}")
    print(f"  能量: {stats.get('energy', 0)}")
    print(f"  魔法: {stats.get('magic', 0)}")
    
    # 显示种族信息
    race = character.get('race', {})
    print("\n种族信息:")
    print(f"  种族描述: {race.get('description', '无')}")
    if race.get('traits'):
        print("  种族特质:")
        for trait in race.get('traits', []):
            print(f"    - {trait}")
    
    # 显示职业信息
    career = character.get('career', {})
    print("\n职业信息:")
    print(f"  职业描述: {career.get('description', '无')}")
    print(f"  成长路径: {career.get('growth_path', '无')}")
    print(f"  特殊能力: {career.get('special_abilities', '无')}")
    
    # 显示武器信息
    weapons = character.get('weapons', [])
    if weapons:
        print(f"\n武器信息 (共{len(weapons)}件):")
        for i, weapon in enumerate(weapons, 1):
            print(f"  {i}. {weapon.get('name', '未知武器')} (等级: {weapon.get('level', '?')})")
            print(f"     描述: {weapon.get('description', '无')}")
            if weapon.get('attributes'):
                print("     属性:")
                for attr in weapon.get('attributes', []):
                    print(f"       - {attr}")
    
    # 显示职业能力信息
    careers = character.get('careers', [])
    if careers:
        print(f"\n职业能力 (共{len(careers)}个):")
        for i, career_item in enumerate(careers, 1):
            print(f"  {i}. {career_item.get('name', '未知职业能力')} (等级: {career_item.get('level', '?')})")
            print(f"     描述: {career_item.get('description', '无')}")
            if career_item.get('attributes'):
                print("     属性:")
                for attr in career_item.get('attributes', []):
                    print(f"       - {attr}")
    
    print("\n===== 角色详情结束 =====")

def generate_power_item(game_manager):
    """生成能力或物品"""
    if not game_manager.current_save_id:
        print("未选择角色")
        return
    
    try:
        # 选择物品类型
        print("\n请选择要生成的内容类型:")
        print("1. 能力")
        print("2. 物品")
        print("3. 魔法")
        print("4. 法器")
        print("5. 丹药")
        print("6. 功法")
        print("7. 修炼角色")
        type_choice = input("请选择 (1-7): ").strip()
        
        # 映射选择到类型和名称
        type_mapping = {
            "1": ("ability", "能力"),
            "2": ("item", "物品"),
            "3": ("magic", "魔法"),
            "4": ("artifact", "法器"),
            "5": ("elixir", "丹药"),
            "6": ("technique", "功法"),
            "7": ("cultivation_role", "修炼角色")
        }
        
        if type_choice not in type_mapping:
            print("无效的选择")
            return
        
        item_type, item_type_name = type_mapping[type_choice]
        
        level = int(input(f"请输入{item_type_name}等级 (1-7): "))
        if not (1 <= level <= 7):
            print("无效的等级，必须在1-7之间")
            return
        
        detail = input(f"请输入{item_type_name}描述 (可选): ")
        
        print(f"\n正在生成{item_type_name}...")
        
        # 根据类型调用相应的生成方法
        generator_method = getattr(game_manager, f"generate_{item_type}")
        item = generator_method(level, detail)
        
        if item:
            print("\n生成成功!")
            print(f"名称: {item.get('name', '未知')}")
            print(f"描述: {item.get('description', '无')}")
            print(f"起源: {item.get('origin', '无')}")
            print("特性:")
            for attr in item.get('attributes', []):
                print(f"  - {attr}")
            print(f"用途: {item.get('usage', '无')}")
            
            # 显示当前物品总数
            items = game_manager.get_character_items(item_type)
            print(f"\n当前角色拥有 {len(items)} 个{item_type_name}")
        else:
            print(f"生成{item_type_name}失败")
    
    except ValueError:
        print("请输入有效的数字")

def show_power_level(game_manager):
    """显示能力等级信息"""
    try:
        level = int(input("请输入要查看的能力等级 (1-7): "))
        if not (1 <= level <= 7):
            print("无效的等级，必须在1-7之间")
            return
        
        if game_manager.power_generator:
            explanation = game_manager.power_generator.explain_power_level(level)
            print(explanation)
        else:
            print("能力生成器未初始化")
    
    except ValueError:
        print("请输入有效的数字")

def main():
    """主函数"""
    try:
        # 初始化游戏管理器
        game_manager = GameManager()
        
        while True:
            # 显示当前角色状态
            if game_manager.current_save_id:
                char = game_manager.get_current_character()
                print(f"\n当前角色: {char.get('name', '未知')} - {char.get('race', {}).get('sub_race', '未知')} {char.get('career', {}).get('name', '未知')}")
            else:
                print("\n当前未选择角色")
            
            # 显示菜单并获取用户选择
            choice = display_menu()
            
            if choice == "0":
                print("感谢使用，再见!")
                break
                
            elif choice == "1":
                # 创建新角色
                print("\n=== 开始创建新角色 ===")
                result = game_manager.create_new_character()
                
                if result.get("success"):
                    print(f"\n角色创建成功! {result.get('character_name')} - {result.get('race')} {result.get('career')}")
                else:
                    print(f"\n角色创建失败: {result.get('error', '未知错误')}")
            
            elif choice == "2":
                # 加载已有角色
                select_character(game_manager)
            
            elif choice == "3":
                # 查看角色详情
                show_character_details(game_manager)
            
            elif choice == "4":
                # 生成能力或物品
                generate_power_item(game_manager)
            
            elif choice == "5":
                # 查看能力等级
                show_power_level(game_manager)
            
            else:
                print("无效的选择，请重试")
    
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断。")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        print("请重新启动程序。")

if __name__ == "__main__":
    main() 