#!/usr/bin/env python3
"""
能力与物品生成器测试 - 测试不同等级和类型的生成效果
"""

import os
import sys
import time
import json

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入必要的模块
from storyline.storyline_manager import StorylineManager
from data.data_manager import create_save, load_save, save_data, delete_save

def test_power_item_generator():
    """测试能力与物品生成器模板"""
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 创建的存档名称列表，用于后续询问用户是否删除
    created_saves = []
    
    # 测试用例列表
    test_cases = [
        {
            "name": "初级武器",
            "level": 1,
            "type": "weapon",
            "detail": "一把简单的剑"
        },
        {
            "name": "中级职业",
            "level": 3,
            "type": "career",
            "detail": "擅长火系魔法的职业"
        },
        {
            "name": "高级武器",
            "level": 5,
            "type": "weapon",
            "detail": "能够操控风暴的远程武器"
        },
        {
            "name": "顶级职业",
            "level": 7,
            "type": "career",
            "detail": "能够跨越时空的职业"
        }
    ]
    
    # 循环测试每个用例
    for test_case in test_cases:
        print(f"\n=== 测试案例：{test_case['name']} ===")
        
        # 创建测试存档
        save_name = f"power_item_test_{int(time.time())}"
        created_saves.append(save_name)  # 添加到创建的存档列表
        
        # 准备存档数据
        save_content = {  # 修改变量名，避免与导入的save_data函数冲突
            "id": save_name,
            "temp_level": test_case["level"],
            "temp_type": test_case["type"],
            "temp_detail": test_case["detail"],
            # 添加一些基本的纪元信息作为背景
            "era": {
                "name": "万象帝国",
                "era_number": 5,
                "key_features_joined": "魔法与科技平衡发展，将前代文明知识整合",
                "magic_system": "综合魔法学院体系",
                "technology_level": "魔法与科技融合"
            }
        }
        
        # 为模板计算添加level_index，避免模板中的数学运算问题
        save_content["temp_level_index"] = test_case["level"] - 1
        
        # 创建存档
        create_save("character", save_name, save_content)
        print(f"创建测试存档：{save_name}")
        
        # 生成内容
        print(f"正在生成 {test_case['type']} (等级 {test_case['level']})...")
        success = manager.generate_story(save_name, "power_item_generator")
        
        if success:
            # 读取结果
            updated_save = load_save("character", save_name)
            
            # 提取结果
            type_key = test_case["type"]
            if type_key in updated_save:
                result = updated_save[type_key]
                
                # 显示结果
                print(f"\n生成结果:")
                print(f"名称: {result.get('name', '未生成')}")
                print(f"描述: {result.get('description', '未生成')}")
                print(f"起源: {result.get('origin', '未生成')}")
                print(f"属性: {', '.join(result.get('attributes', ['未生成']))}")
                print(f"用途: {result.get('usage', '未生成')}")
            else:
                print(f"生成内容类型 '{type_key}' 不存在于存档中")
                print(f"存档包含以下键: {list(updated_save.keys())}")
        else:
            print("生成失败")
    
    # 询问用户是否删除测试存档
    if created_saves:
        print("\n\n测试已完成，是否要删除所有测试存档？")
        print("创建的测试存档：")
        for i, save_name in enumerate(created_saves, 1):
            print(f"{i}. {save_name}")
        
        while True:
            choice = input("\n请选择操作：\n1. 删除所有测试存档\n2. 保留所有测试存档\n3. 选择性删除\n请输入选项 (1/2/3): ").strip()
            
            if choice == "1":
                # 删除所有测试存档
                print("\n正在删除所有测试存档...")
                for save_name in created_saves:
                    delete_save("character", save_name)
                    print(f"已删除存档: {save_name}")
                print("所有测试存档已删除")
                break
            
            elif choice == "2":
                # 保留所有测试存档
                print("\n已保留所有测试存档")
                break
            
            elif choice == "3":
                # 选择性删除
                print("\n请输入要删除的存档编号（多个编号用逗号分隔，例如: 1,3）:")
                delete_choice = input("要删除的存档编号: ").strip()
                try:
                    # 解析用户输入的编号
                    indices = [int(idx.strip()) for idx in delete_choice.split(",") if idx.strip()]
                    # 删除选定的存档
                    for idx in indices:
                        if 1 <= idx <= len(created_saves):
                            save_name = created_saves[idx-1]
                            delete_save("character", save_name)
                            print(f"已删除存档: {save_name}")
                        else:
                            print(f"无效的编号: {idx}")
                    
                    print("选定的测试存档已删除")
                    break
                except ValueError:
                    print("输入无效，请重试")
            
            else:
                print("输入无效，请重试")

if __name__ == "__main__":
    test_power_item_generator() 