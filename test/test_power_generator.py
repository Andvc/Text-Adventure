#!/usr/bin/env python3
"""
PowerGenerator测试脚本

测试能力生成器的所有功能
"""

import os
import sys
import json
from typing import Dict, Any

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from gameflow.power_generator import PowerGenerator
from gameflow.game_manager import GameManager
from data.data_manager import save_data

def create_test_character() -> str:
    """创建测试角色数据"""
    test_character = {
        "name": "测试角色",
        "era": {
            "name": "测试纪元",
            "description": "这是一个测试纪元",
            "key_features": ["测试特征1", "测试特征2"],
            "key_features_joined": "测试特征1, 测试特征2",
            "magic_system": "测试魔法系统"
        },
        "race": {
            "main_race": "人类",
            "sub_race": "测试人类",
            "description": "这是一个测试种族",
            "traits": ["测试特质1", "测试特质2"]
        },
        "career": {
            "name": "测试职业",
            "description": "这是一个测试职业",
            "growth_path": "测试成长路径",
            "special_abilities": "测试特殊能力"
        },
        "stats": {
            "level": 1,
            "experience": 0,
            "health": 100,
            "energy": 100,
            "magic": 100
        },
        "created_at": "2024-03-20T00:00:00"
    }
    
    # 保存测试角色
    save_id = "test_character"
    save_data("character", save_id, test_character)
    return save_id

def test_power_levels():
    """测试能力等级说明功能"""
    print("\n=== 测试能力等级说明 ===")
    generator = PowerGenerator()
    
    for level in range(0, 8):
        print(f"\n等级 {level} 说明:")
        explanation = generator.explain_power_level(level)
        print(explanation)

def test_generation(game_manager: GameManager, save_id: str):
    """测试各种类型的生成功能"""
    print("\n=== 测试生成功能 ===")
    
    # 测试所有支持的类型
    types = [
        ("ability", "能力"),
        ("item", "物品"),
        ("magic", "魔法"),
        ("artifact", "法器"),
        ("elixir", "丹药"),
        ("technique", "功法"),
        ("cultivation_role", "修炼角色")
    ]
    
    for item_type, type_name in types:
        print(f"\n测试生成{type_name}:")
        
        # 测试不同等级
        for level in [1, 4, 7]:
            print(f"\n生成等级 {level} 的{type_name}:")
            
            # 生成内容
            generator_method = getattr(game_manager, f"generate_{item_type}")
            item = generator_method(level, f"测试{type_name}描述")
            
            if item:
                print(f"生成成功:")
                print(f"名称: {item.get('name', '未知')}")
                print(f"描述: {item.get('description', '无')}")
                print(f"起源: {item.get('origin', '无')}")
                print("特性:")
                for attr in item.get('attributes', []):
                    print(f"  - {attr}")
                print(f"用途: {item.get('usage', '无')}")
            else:
                print(f"生成失败")

def test_item_storage(game_manager: GameManager):
    """测试物品存储功能"""
    print("\n=== 测试物品存储 ===")
    
    # 获取当前角色
    character = game_manager.get_current_character()
    if not character:
        print("未选择角色")
        return
    
    # 检查所有类型的物品存储
    for item_type in PowerGenerator.SUPPORTED_TYPES:
        items = game_manager.get_character_items(item_type)
        print(f"\n{item_type}列表 (共{len(items)}个):")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.get('name', '未知')} (等级: {item.get('level', '?')})")

def main():
    """主测试函数"""
    try:
        # 初始化游戏管理器
        game_manager = GameManager()
        
        # 创建测试角色
        print("创建测试角色...")
        save_id = create_test_character()
        
        # 加载测试角色
        if not game_manager.load_character(save_id):
            print("加载测试角色失败")
            return
        
        print(f"加载测试角色成功")
        
        # 运行测试
        test_power_levels()
        test_generation(game_manager, save_id)
        test_item_storage(game_manager)
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main() 