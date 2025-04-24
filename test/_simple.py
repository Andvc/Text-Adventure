#!/usr/bin/env python3
"""
数据访问测试脚本 - 测试新的数据管理功能
"""

import os
import sys

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入数据管理模块
from data import data_manager
from character import character_manager

def test_data_manager_direct():
    """测试直接使用data_manager模块"""
    print("===== 测试直接使用data_manager模块 =====")
    
    # 1. 读取物品数据文件
    items = data_manager.read_data_file('text', 'items')
    if items:
        print(f"成功读取物品数据文件，包含 {len(items)} 个物品")
        
        # 输出前两个物品的详细信息
        count = 0
        for item_id, item_data in items.items():
            if count < 2:
                print(f"\n物品ID: {item_id}")
                print(f"名称: {item_data['name']}")
                print(f"描述: {item_data['description']}")
                print(f"类型: {item_data['type']}")
                if 'base_attack' in item_data:
                    print(f"基础攻击力: {item_data['base_attack']}")
                count += 1
            else:
                break
    else:
        print("读取物品数据文件失败")
    
    # 2. 获取特定物品数据
    sword = data_manager.get_data_value('text', 'items', 'steel_sword', None)
    if sword:
        print(f"\n直接获取特定物品: {sword['name']}")
        print(f"价值: {sword['value']} 金币")
    else:
        print("\n获取钢剑数据失败")

def test_character_manager_data_access():
    """测试通过character_manager访问数据"""
    print("\n===== 测试通过character_manager访问数据 =====")
    
    # 1. 读取NPC数据文件
    npcs = character_manager.read_data_file('text', 'npcs')
    if npcs:
        print(f"成功读取NPC数据文件，包含 {len(npcs)} 个NPC")
        
        # 输出第一个NPC的详细信息
        first_npc_id = next(iter(npcs))
        npc_data = npcs[first_npc_id]
        print(f"\nNPC ID: {first_npc_id}")
        print(f"名称: {npc_data['name']}")
        print(f"描述: {npc_data['description']}")
        print(f"职业: {npc_data['occupation']}")
        print(f"问候语: {npc_data['greeting']}")
    else:
        print("读取NPC数据文件失败")
    
    # 2. 获取特定NPC数据
    innkeeper = character_manager.get_data('text', 'npcs', 'innkeeper', None)
    if innkeeper:
        print(f"\n直接获取特定NPC: {innkeeper['name']}")
        print(f"位置: {innkeeper['location']}")
        
        # 显示闲聊内容
        print(f"闲聊内容:")
        for i, gossip in enumerate(innkeeper.get('gossip', []), 1):
            print(f"  {i}. {gossip}")
    else:
        print("\n获取旅店老板数据失败")

def main():
    """主函数"""
    print("数据访问测试开始\n")
    
    # 测试直接使用data_manager
    test_data_manager_direct()
    
    # 测试通过character_manager访问数据
    test_character_manager_data_access()
    
    print("\n数据访问测试结束")

if __name__ == "__main__":
    main() 