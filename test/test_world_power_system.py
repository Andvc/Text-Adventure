#!/usr/bin/env python3
"""
世界等级制度测试脚本

测试世界等级制度模板的生成功能
"""

import os
import sys
import json
import time

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_manager import create_save, load_save
from storyline.storyline_manager import StorylineManager

def load_era(era_id):
    """加载纪元数据
    
    Args:
        era_id (str): 纪元ID
        
    Returns:
        dict: 纪元数据
    """
    try:
        era_data_path = os.path.join('data', 'text', 'eras.json')
        with open(era_data_path, 'r', encoding='utf-8') as f:
            era_data = json.load(f)
        
        # 查找指定纪元
        for era in era_data.get('eras', []):
            if era.get('id') == era_id:
                return era
        
        print(f"未找到ID为{era_id}的纪元")
        return None
    except Exception as e:
        print(f"加载纪元数据时出错: {str(e)}")
        return None

def generate_power_system(era_id):
    """为指定纪元生成等级制度
    
    Args:
        era_id (str): 纪元ID
        
    Returns:
        bool: 是否成功生成
    """
    # 加载纪元数据
    era = load_era(era_id)
    if not era:
        return False
    
    # 创建临时存档
    temp_save_id = f"temp_power_system_{int(time.time())}"
    
    temp_save_data = {
        "id": temp_save_id,
        "era": {
            "id": era.get('id'),
            "name": era.get('name'),
            "era_number": era.get('era_number'),
            "key_features_joined": ", ".join(era.get('key_features', [])),
            "dominant_races_joined": ", ".join(era.get('dominant_races', [])),
            "magic_system": era.get('magic_system'),
            "technology_level": era.get('technology_level'),
            "history": era.get('era_background')
        }
    }
    
    # 创建临时存档
    create_save("character", temp_save_id, temp_save_data)
    
    # 使用模板生成等级制度
    manager = StorylineManager()
    success = manager.generate_story(temp_save_id, "world_power_system")
    
    if success:
        # 加载生成的内容
        updated_save = load_save("character", temp_save_id)
        
        # 显示生成的内容
        print(f"\n=== {era.get('name')}的等级制度 ===")
        
        # 显示等级体系概述
        power_system = updated_save.get("power_system", {})
        print(f"\n## 体系名称: {power_system.get('name', '未知')}")
        print(f"核心理念: {power_system.get('core_concept', '未知')}")
        print(f"历史渊源: {power_system.get('origin', '未知')}")
        print(f"基本规则: {power_system.get('basic_rules', '未知')}")
        
        # 显示等级详情
        power_levels = updated_save.get("power_levels", [])
        print("\n## 七大等级:")
        for level in power_levels:
            print(f"\n等级 {level.get('level', '?')}: {level.get('name', '未知')}")
            print(f"描述: {level.get('description', '未知')}")
            print(f"社会地位: {level.get('status', '未知')}")
            if level.get('advancement'):
                print(f"进阶方法: {level.get('advancement', '未知')}")
        
        # 显示种族特性
        racial_traits = updated_save.get("racial_traits", {})
        print("\n## 种族特性:")
        for race, traits in racial_traits.items():
            print(f"\n{race}: {traits}")
        
        # 显示著名人物
        notable_figures = updated_save.get("notable_figures", [])
        print("\n## 著名人物:")
        for figure in notable_figures:
            print(f"\n{figure.get('name', '未知')} - {figure.get('level', '未知')}级 {figure.get('title', '未知')}")
            print(f"背景: {figure.get('background', '未知')}")
        
        return True
    else:
        print(f"为{era.get('name')}生成等级制度失败")
        return False

def main():
    """主函数"""
    # 可以测试不同的纪元
    era_ids = [
        "crystal_forge_era",  # 晶铸文明
        "grand_empire_era",   # 万象帝国
        "mind_harmony_era"    # 思维和声文明
    ]
    
    for era_id in era_ids:
        print(f"\n正在为 {era_id} 生成等级制度...")
        generate_power_system(era_id)
        
        # 在测试多个纪元时暂停
        if era_id != era_ids[-1]:
            input("\n按回车继续下一个纪元的测试...")

if __name__ == "__main__":
    main() 