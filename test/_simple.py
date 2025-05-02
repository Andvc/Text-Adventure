#!/usr/bin/env python3
"""
数据访问测试脚本 - 测试新的数据管理功能
"""

import os
import sys

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入数据管理模块
from data.data_manager import data_manager

def test_read_items():
    """测试读取物品数据"""
    items = data_manager.load_save('text', 'items')
    if items:
        print("物品数据读取成功:")
        for item_id, item_info in items.items():
            print(f"- {item_id}: {item_info}")
    else:
        print("物品数据读取失败")

def test_get_item():
    """测试获取特定物品数据"""
    sword = data_manager.get_save_value('text', 'items', 'steel_sword', None)
    if sword:
        print("获取物品成功:")
        print(f"- 铁剑: {sword}")
    else:
        print("获取物品失败")

def test_read_npcs():
    """测试读取NPC数据"""
    npcs = data_manager.load_save('text', 'npcs')
    if npcs:
        print("NPC数据读取成功:")
        for npc_id, npc_info in npcs.items():
            print(f"- {npc_id}: {npc_info}")
    else:
        print("NPC数据读取失败")

def main():
    """主测试函数"""
    print("=== 测试物品数据读取 ===")
    test_read_items()
    print("\n=== 测试获取特定物品 ===")
    test_get_item()
    print("\n=== 测试NPC数据读取 ===")
    test_read_npcs()

if __name__ == "__main__":
    main() 