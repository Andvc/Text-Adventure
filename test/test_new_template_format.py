#!/usr/bin/env python3
"""
测试新的模板格式，以确保PromptProcessor和StorylineManager能够正确处理。
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入需要测试的模块
from ai.prompt_processor import PromptProcessor
from storyline.storyline_manager import StorylineManager

def test_prompt_processor():
    """测试PromptProcessor能否正确处理新格式"""
    print("\n----- 测试PromptProcessor -----")
    
    # 创建测试段落
    test_segments = [
        "(角色名称: 李白)",
        "(角色职业: 诗人)",
        "<描述李白在月光下的情景，突出他的诗意和豪迈>",
        "[scene=\"string\", mood=\"string\"]",
        "<创作一首李白风格的诗歌，表达对月亮的赞美和思乡之情>",
        "[poem=\"string\"]"
    ]
    
    # 创建处理器实例
    processor = PromptProcessor()
    
    # 解析段落
    parsed = processor.parse_segments(test_segments)
    
    # 检查解析结果
    print("\n解析结果:")
    print(f"背景信息数量: {len(parsed['info'])}")
    print(f"内容指令数量: {len(parsed['content'])}")
    print(f"格式指令数量: {len(parsed['format'])}")
    print(f"配对数量: {len(parsed['pairs'])}")
    
    # 检查配对中的字段类型
    for i, pair in enumerate(parsed["pairs"]):
        print(f"\n配对 {i+1}:")
        print(f"  内容: {pair['content']}")
        print(f"  格式: {pair['format']}")
        print(f"  字段类型: {pair.get('field_types', {})}")
    
    # 构建提示词
    prompt = processor.build_prompt(test_segments)
    
    # 检查生成的提示词
    print("\n生成的提示词:")
    print(prompt)
    
    # 检查三引号格式是否正确
    return "\"\"\"" in prompt

def test_storyline_manager():
    """测试StorylineManager与新格式的兼容性"""
    print("\n----- 测试StorylineManager -----")
    
    # 创建临时模板目录
    temp_dir = Path("test_templates")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # 创建测试模板文件
        test_template = {
            "template_id": "test_template",
            "name": "测试模板",
            "description": "用于测试新格式的模板",
            "prompt_segments": [
                "(角色名称: 李白)",
                "(角色职业: 诗人)",
                "<描述李白在月光下的情景，突出他的诗意和豪迈>",
                "[scene=\"string\", mood=\"string\"]",
                "<创作一首李白风格的诗歌，表达对月亮的赞美和思乡之情>",
                "[poem=\"string\"]"
            ],
            "output_storage": {
                "scene": "current_scene",
                "mood": "current_mood",
                "poem": "current_poem"
            }
        }
        
        with open(temp_dir / "test_template.json", "w", encoding="utf-8") as f:
            json.dump(test_template, f, ensure_ascii=False, indent=2)
        
        # 创建StorylineManager实例
        manager = StorylineManager(templates_dir=str(temp_dir))
        
        # 加载模板
        template = manager.load_template("test_template")
        
        # 检查模板是否正确加载
        print("\n加载的模板:")
        print(f"模板ID: {template.get('template_id')}")
        print(f"模板名称: {template.get('name')}")
        print(f"提示片段数量: {len(template.get('prompt_segments', []))}")
        print(f"是否包含output_storage: {'output_storage' in template}")
        
        # 从模板段落中提取字段类型
        field_types = manager._extract_field_types_from_segments(template.get("prompt_segments", []))
        
        # 检查提取的字段类型
        print("\n提取的字段类型:")
        for field, field_type in field_types.items():
            print(f"  {field}: {field_type}")
        
        return len(field_types) > 0
    
    finally:
        # 清理测试目录
        for file in temp_dir.glob("*.json"):
            file.unlink()
        temp_dir.rmdir()

def main():
    """主测试函数"""
    print("===== 测试新的模板格式 =====")
    
    # 测试PromptProcessor
    prompt_processor_success = test_prompt_processor()
    
    # 测试StorylineManager
    storyline_manager_success = test_storyline_manager()
    
    # 输出总结
    print("\n===== 测试结果 =====")
    print(f"PromptProcessor测试: {'通过' if prompt_processor_success else '失败'}")
    print(f"StorylineManager测试: {'通过' if storyline_manager_success else '失败'}")
    
    # 返回总体测试结果
    return prompt_processor_success and storyline_manager_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 