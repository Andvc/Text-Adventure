#!/usr/bin/env python3
"""
示例功能测试脚本

测试高级功能：嵌套占位符系统、文本数据引用和数组处理
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入必要的模块
from storyline.storyline_manager import StorylineManager
from data.data_manager import create_save, load_save, save_data

def setup_example():
    """准备示例存档"""
    # 检查存档是否存在
    save_name = "example"
    save_path = Path("save") / "characters" / f"{save_name}.json"
    
    if not save_path.exists():
        # 创建示例存档
        example_data = {
            "id": "example",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "character": {
                "name": "艾里克",
                "title": "魔法师",
                "profession": "学者",
                "background": "来自山区的魔法爱好者"
            },
            "identity_field": "profession",
            "current_era_index": 4,
            "location": "魔法学院图书馆",
            "skills": [
                "火球术",
                "魔法护盾",
                "光照术",
                "元素感知",
                "魔法解析"
            ],
            "active_skill_index": 2,
            "power_level": 3,
            "character_background": "",
            "current_scene": "",
            "option1": "",
            "option2": "",
            "option3": ""
        }
        create_save("character", save_name, example_data)
        print(f"创建示例存档：{save_name}")
    
    return save_name

def explain_template():
    """解释模板的功能和结构"""
    print("\n=== 模板功能说明 ===")
    print("本示例展示了以下高级功能：")
    print("1. 嵌套占位符系统：如 {character.{identity_field}} 允许动态选择字段")
    print("2. 文本数据引用：如 {text;eras;eras[0].name} 直接从data/text文件夹读取数据")
    print("3. 动态数组索引：如 {skills[{active_skill_index}]} 使用变量作为索引")
    
    print("\n模板结构说明：")
    print("- prompt_segments：定义提示词片段，包含各种占位符")
    print("- output_storage：定义输出字段的存储映射")
    print("- prompt_template：定义完整提示词的模板格式")
    
    print("\n占位符示例解析：")
    print("- {character.name} → 访问存档中的character.name字段")
    print("- {character.{identity_field}} → 使用identity_field字段的值作为character对象的字段名")
    print("- {text;eras;eras[{current_era_index}].name} → 从eras.json文件中读取指定索引的纪元名称")
    print("- {skills[{active_skill_index}]} → 获取skills数组中索引为active_skill_index的元素")

def demonstrate_placeholder_resolution():
    """演示占位符解析过程"""
    print("\n=== 占位符解析演示 ===")
    
    # 加载示例存档
    save_name = "example"
    save_data = load_save("character", save_name)
    
    if not save_data:
        print("存档加载失败")
        return False
    
    # 演示嵌套占位符解析
    print("\n嵌套占位符解析示例：")
    identity_field = save_data.get("identity_field", "")
    character = save_data.get("character", {})
    
    print(f"原始数据：identity_field = '{identity_field}', character = {character}")
    print(f"解析 {{character.{{identity_field}}}} 的过程：")
    print(f"1. 先解析内部占位符 {{identity_field}} → '{identity_field}'")
    print(f"2. 得到新的占位符 {{character.{identity_field}}}")
    print(f"3. 解析 {{character.{identity_field}}} → '{character.get(identity_field, '')}'")
    
    # 演示文本数据引用解析
    print("\n文本数据引用解析示例：")
    current_era_index = save_data.get("current_era_index", 0)
    
    print(f"原始数据：current_era_index = {current_era_index}")
    print(f"解析 {{text;eras;eras[{{current_era_index}}].name}} 的过程：")
    print(f"1. 先解析内部占位符 {{current_era_index}} → {current_era_index}")
    print(f"2. 得到新的占位符 {{text;eras;eras[{current_era_index}].name}}")
    print(f"3. 从 data/text/eras.json 中读取 eras[{current_era_index}].name")
    
    # 获取实际的纪元名称
    try:
        eras_path = Path("data") / "text" / "eras.json"
        with open(eras_path, 'r', encoding='utf-8') as f:
            eras_data = json.load(f)
        
        if "eras" in eras_data and len(eras_data["eras"]) > current_era_index:
            era_name = eras_data["eras"][current_era_index].get("name", "未知纪元")
            print(f"4. 解析结果 → '{era_name}'")
        else:
            print("4. 解析失败，索引超出范围或数据结构不匹配")
    except Exception as e:
        print(f"4. 解析异常：{str(e)}")
    
    # 演示数组索引解析
    print("\n数组索引解析示例：")
    skills = save_data.get("skills", [])
    active_skill_index = save_data.get("active_skill_index", 0)
    
    print(f"原始数据：skills = {skills}, active_skill_index = {active_skill_index}")
    print(f"解析 {{skills[{{active_skill_index}}]}} 的过程：")
    print(f"1. 先解析内部占位符 {{active_skill_index}} → {active_skill_index}")
    print(f"2. 得到新的占位符 {{skills[{active_skill_index}]}}")
    if 0 <= active_skill_index < len(skills):
        print(f"3. 解析 {{skills[{active_skill_index}]}} → '{skills[active_skill_index]}'")
    else:
        print(f"3. 解析失败，索引超出范围")
    
    return True

def run_example_generation():
    """运行示例生成"""
    print("\n=== 运行示例生成 ===")
    
    # 初始化故事线管理器
    manager = StorylineManager()
    
    # 获取示例存档名称
    save_name = "example"
    
    # 生成故事
    print(f"正在使用模板 'example' 生成内容...")
    success = manager.generate_story(save_name, "example")
    
    if success:
        # 加载更新后的存档
        updated_save = load_save("character", save_name)
        
        # 显示生成的内容
        print("\n== 生成的角色背景 ==")
        print(updated_save.get("character_background", "生成失败"))
        
        print("\n== 生成的当前场景 ==")
        print(updated_save.get("current_scene", "生成失败"))
        
        print("\n== 生成的选项 ==")
        print(f"选项1: {updated_save.get('option1', '生成失败')}")
        print(f"选项2: {updated_save.get('option2', '生成失败')}")
        print(f"选项3: {updated_save.get('option3', '生成失败')}")
        
        return True
    else:
        print("生成失败")
        return False

def main():
    """主函数"""
    print("===== 高级功能演示 =====")
    
    # 设置示例存档
    save_name = setup_example()
    print(f"使用存档：{save_name}")
    
    # 解释模板功能
    explain_template()
    
    # 演示占位符解析
    demonstrate_placeholder_resolution()
    
    # 询问是否生成内容
    while True:
        choice = input("\n是否运行内容生成？(y/n): ")
        if choice.lower() == 'y':
            run_example_generation()
            break
        elif choice.lower() == 'n':
            print("跳过内容生成")
            break
        else:
            print("无效的选择，请输入y或n")
    
    print("\n===== 演示完成 =====")

if __name__ == "__main__":
    main() 