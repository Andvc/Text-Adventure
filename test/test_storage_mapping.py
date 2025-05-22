#!/usr/bin/env python3
"""
存储映射测试脚本

测试多重嵌套情况下的存储映射功能
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入必要的模块
from storyline.storyline_manager import StorylineManager
from data.data_manager import create_save, load_save, save_data

def test_nested_storage():
    """测试多重嵌套存储映射"""
    print("\n=== 测试多重嵌套存储映射 ===")
    
    # 创建测试存档
    save_name = "test_nested_storage"
    test_data = {
        "temp_type": "era",
        "current_level": 1,
        "active_skill": "fireball"
    }
    create_save("character", save_name, test_data)
    
    # 创建测试模板
    template = {
        "template_id": "test_nested",
        "name": "测试多重嵌套",
        "output_storage": {
            # 变量替换映射
            "name": "{temp_type}.details.name",
            "feature": "{temp_type}.details.features.main",
            "event": "{temp_type}.history.events[0].description",
            
            # 多重嵌套路径映射
            "level_name": "character.stats.level.name",
            "skill_power": "character.skills.{active_skill}.power",
            "nested_value": "deeply.nested.path.to.value"
        }
    }
    
    # 创建StorylineManager实例
    manager = StorylineManager()
    
    # 生成测试结果
    test_result = {
        "name": "测试时代",
        "feature": "灵气充沛",
        "event": "天地异变",
        "level_name": "炼气期",
        "skill_power": 100,
        "nested_value": "最终值"
    }
    
    # 应用存储映射
    current_save = load_save("character", save_name)
    manager._apply_storage_mapping(test_result, template["output_storage"], current_save, save_name)
    
    # 验证结果
    print("\n存储映射结果：")
    print(json.dumps(current_save, ensure_ascii=False, indent=2))
    
    # 验证各个路径
    print("\n验证各个路径：")
    paths_to_check = [
        "era.details.name",
        "era.details.features.main",
        "era.history.events[0].description",
        "character.stats.level.name",
        "character.skills.fireball.power",
        "deeply.nested.path.to.value"
    ]
    
    for path in paths_to_check:
        parts = path.split(".")
        current = current_save
        for part in parts:
            if "[" in part:
                # 处理数组索引
                key, index = part.split("[")
                index = int(index.rstrip("]"))
                current = current[key][index]
            else:
                current = current[part]
        print(f"{path}: {current}")

if __name__ == "__main__":
    test_nested_storage() 