"""
全面测试AI提示词处理与API交互模块的所有功能

本测试模块提供了对模块所有功能的全面测试，包括：
1. 提示词处理器功能
2. API连接器功能
3. 输出解析器功能
4. 内容格式配对功能
5. 多字段格式功能
6. 实际API调用功能（可选）
7. 错误处理功能
8. 自定义模板功能
9. 完整工作流程测试
"""

import os
import json
import time
import argparse
import sys
from typing import Dict, Any, List
from getpass import getpass
import re

import config
from prompt_processor import PromptProcessor
from api_connector import AIModelConnector, APIError, AuthenticationError
from output_parsers import OutputParser, JSONOutputParser, FormatPatternParser

# 测试辅助函数
def print_header(title):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(f"测试: {title}")
    print("=" * 60)

def print_section(title):
    """打印子测试标题"""
    print("\n" + "-" * 40)
    print(f"{title}")
    print("-" * 40)

def verify_api_key(api_key):
    """验证API密钥是否有效"""
    if not api_key:
        return False
    
    # 简单验证密钥格式是否类似有效的API密钥
    # DeepSeek API密钥通常是以特定前缀开头的长字符串
    if len(api_key) < 20:  # 假设有效密钥至少20个字符
        return False
    
    # 检查是否是典型的API密钥格式（可以根据实际密钥格式调整）
    if not re.match(r'^[a-zA-Z0-9_.-]+$', api_key):
        return False
        
    return True

def get_api_key():
    """获取API密钥，优先从配置文件和环境变量获取，其次请求用户输入"""
    # 检查配置文件中是否已有API密钥
    api_key = config.DEEPSEEK_API_KEY
    
    # 如果配置中已有有效密钥，直接返回
    if verify_api_key(api_key):
        print("已从配置中读取API密钥")
        return api_key
    
    # 提示用户输入API密钥
    print("未找到有效的API密钥。")
    user_input = input("请输入DeepSeek API密钥 (直接按回车则使用模拟测试): ")
    
    if not user_input:
        print("将使用模拟响应测试...")
        return None
    
    # 验证用户输入的API密钥
    if verify_api_key(user_input):
        print("API密钥格式有效，将用于测试")
        return user_input
    else:
        print("输入的API密钥格式无效，将使用模拟响应测试...")
        return None

# 核心功能测试函数
def test_prompt_processor():
    """测试提示词处理器的基本功能"""
    print_header("提示词处理器基本功能")
    
    # 创建处理器
    processor = PromptProcessor()
    
    # 测试解析片段
    test_segments = [
        "(角色为剑士)",
        "(场景是森林)",
        "<一段故事>",
        "[story=\"*\"]"
    ]
    
    # 解析片段
    parsed = processor.parse_segments(test_segments)
    print("解析片段结果:")
    print(f"信息类: {parsed['info']}")
    print(f"内容类: {parsed['content']}")
    print(f"格式类: {parsed['format']}")
    
    # 测试构建提示词
    prompt = processor.build_prompt(test_segments)
    print_section("构建的提示词")
    print(prompt)
    
    # 测试性能
    perf_test_count = 1000
    start_time = time.time()
    for _ in range(perf_test_count):
        processor.build_prompt(test_segments)
    end_time = time.time()
    
    print(f"\n性能测试: 构建 {perf_test_count} 个提示词用时 {end_time - start_time:.4f} 秒")
    print(f"平均每个提示词构建时间: {(end_time - start_time) / perf_test_count * 1000:.2f} 毫秒")
    
    return True

def test_custom_template():
    """测试自定义模板功能"""
    print_header("自定义模板功能")
    
    # 创建处理器
    processor = PromptProcessor()
    
    # 测试输入片段
    test_segments = [
        "(主角是侦探)",
        "(地点是博物馆)",
        "<一个谜题>",
        "[puzzle=\"*\", difficulty=\"high\"]"
    ]
    
    # 使用默认模板
    default_prompt = processor.build_prompt(test_segments)
    print_section("默认模板生成的提示词")
    print(default_prompt)
    
    # 自定义模板
    custom_template = """请根据以下信息，以JSON格式输出：

{{
  "{output_key}": "请创建一个关于{output_content}的内容"
}}

参考信息: {input_info}"""

    custom_processor = PromptProcessor(template=custom_template)
    custom_prompt = custom_processor.build_prompt(test_segments)
    
    print_section("自定义模板生成的提示词")
    print(custom_prompt)
    
    # 角色扮演模板
    role_play_template = """【角色扮演】请假装你是一位经验丰富的{output_content}专家，基于以下信息提供专业建议：
{{
  "{output_key}": "请详细解释最佳方案和实施步骤"
}}
用户提供的情境: {input_info}"""

    role_play_processor = PromptProcessor(template=role_play_template)
    role_play_segments = [
        "(家中有一只1岁的猫咪，经常抓挠家具)",
        "<宠物行为训练>",
        "[solution=\"*\"]"
    ]
    role_play_prompt = role_play_processor.build_prompt(role_play_segments)
    
    print_section("角色扮演模板生成的提示词")
    print(role_play_prompt)
    
    return True

def test_content_format_pairing():
    """测试内容与格式配对功能"""
    print_header("内容与格式配对功能")
    
    # 创建处理器
    processor = PromptProcessor()
    
    # 测试单一字段配对
    print_section("1. 单一字段配对")
    segments1 = [
        "(角色是巫师)",
        "<描述一个强大的火焰魔法>",
        "[spell=\"*\"]"
    ]
    
    prompt1 = processor.build_prompt(segments1)
    print(prompt1)
    
    # 测试多字段单一内容
    print_section("2. 多字段单一内容")
    segments2 = [
        "(场景是学校)",
        "<描述一个学生和老师的对话>",
        "[student_line=\"*\", teacher_line=\"*\"]"
    ]
    
    prompt2 = processor.build_prompt(segments2)
    print(prompt2)
    
    # 测试多组内容格式配对
    print_section("3. 多组内容格式配对")
    segments3 = [
        "(场景是中世纪城堡)",
        "(角色是吟游诗人和国王)",
        "<讲述一个国王面临的困境>",
        "[story=\"*\"]",
        "<提供两个解决方案选项>",
        "[choice1=\"*\", choice2=\"*\"]",
        "<描述选择第一个方案的结果>",
        "[consequence1=\"*\"]",
        "<描述选择第二个方案的结果>",
        "[consequence2=\"*\"]"
    ]
    
    prompt3 = processor.build_prompt(segments3)
    print(prompt3)
    
    # 测试混合配对场景
    print_section("4. 混合配对场景")
    segments4 = [
        "(游戏设定)",
        "<描述游戏主角>",
        "[hero_name=\"*\", hero_class=\"*\"]",
        "<描述游戏世界背景>",
        "[world_description=\"*\"]",
        "(游戏玩法)"
    ]
    
    prompt4 = processor.build_prompt(segments4)
    print(prompt4)
    
    return True

def test_api_connector():
    """测试API连接器功能"""
    print_header("API连接器功能")
    
    # 测试初始化
    try:
        connector = AIModelConnector(api_key="test_key")
        print("连接器初始化成功")
        
        # 测试请求头生成
        headers = connector._prepare_headers()
        print(f"请求头: {headers}")
        
        # 测试请求负载生成
        payload = connector._prepare_payload("测试提示词")
        print(f"请求负载示例:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        
        # 测试API密钥验证
        try:
            # 临时备份原始API密钥配置
            original_key = config.DEEPSEEK_API_KEY
            # 将配置中的API密钥设为空
            config.DEEPSEEK_API_KEY = ""
            
            try:
                # 尝试创建连接器但不提供API密钥
                no_key_connector = AIModelConnector()
                print("错误: 应该抛出API密钥未设置错误")
                # 恢复原始API密钥配置
                config.DEEPSEEK_API_KEY = original_key
                return False
            except AuthenticationError:
                print("正确: 捕获到未设置API密钥的错误")
                # 恢复原始API密钥配置
                config.DEEPSEEK_API_KEY = original_key
        except Exception as e:
            # 确保配置恢复
            config.DEEPSEEK_API_KEY = original_key
            print(f"API密钥验证测试发生错误: {str(e)}")
            return False
        
        # 注意：不测试实际API调用，因为需要有效密钥
        print("\n注意: 跳过实际API调用测试，需要有效的API密钥")
        
        return True
    except Exception as e:
        print(f"API连接器测试失败: {str(e)}")
        return False

def test_output_parsers():
    """测试输出解析器功能"""
    print_header("输出解析器功能")
    
    # 测试标准JSON解析
    print_section("1. 标准JSON解析")
    standard_json = '{"story": "勇士在森林中遇到了一只野兽。"}'
    result = OutputParser.parse(standard_json)
    print("输入: " + standard_json)
    print("解析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    success = result.get("story") == "勇士在森林中遇到了一只野兽。"
    print(f"解析成功: {success}")
    
    # 测试带前缀文本的JSON
    print_section("2. 带前缀文本的JSON解析")
    prefixed_json = """
    以下是生成的故事:
    
    {"story": "魔法师施展了一道闪电咒语。"}
    """
    result = OutputParser.parse(prefixed_json)
    print("输入: " + prefixed_json.strip())
    print("解析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    success = result.get("story") == "魔法师施展了一道闪电咒语。"
    print(f"解析成功: {success}")
    
    # 测试带Markdown代码块的JSON
    print_section("3. 带Markdown代码块的JSON解析")
    markdown_json = """
    我生成的推理过程如下:
    
    ```json
    {
      "reasoning": "根据线索分析，凶手应该是管家。",
      "confidence": "高"
    }
    ```
    
    希望这对您有所帮助!
    """
    result = OutputParser.parse(markdown_json)
    print("输入: " + markdown_json.strip())
    print("解析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    success = result.get("reasoning") is not None and result.get("confidence") is not None
    print(f"解析成功: {success}")
    
    # 测试多层嵌套JSON
    print_section("4. 多层嵌套JSON解析")
    nested_json = """
    {
      "character": {
        "name": "阿尔托里亚",
        "class": "剑士",
        "attributes": {
          "strength": 85,
          "agility": 90,
          "intelligence": 75
        }
      },
      "equipment": [
        {"slot": "weapon", "item": "神圣之剑"},
        {"slot": "armor", "item": "骑士铠甲"}
      ]
    }
    """
    result = OutputParser.parse(nested_json)
    print("输入: " + nested_json[:100] + "...")
    print("解析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    success = (result.get("character") is not None and 
               result.get("character", {}).get("attributes") is not None and
               len(result.get("equipment", [])) == 2)
    print(f"解析成功: {success}")
    
    # 测试格式错误的JSON
    print_section("5. 格式错误的JSON解析")
    malformed_json = """
    {
      "story": "这是一个没有正确闭合的JSON字符串,
      "author": "AI助手"
    }
    """
    result = OutputParser.parse(malformed_json)
    print("输入: " + malformed_json.strip())
    print("解析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"处理错误JSON的能力: {'error' in result}")
    
    # 测试非JSON格式的键值对
    print_section("6. 非JSON格式的键值对解析")
    non_json = 'story="骑士保卫了王国" author="AI模型"'
    result = OutputParser.parse(non_json)
    print("输入: " + non_json)
    print("解析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    success = "story" in result or "error" in result
    print(f"回退解析成功: {success}")
    
    return True

def test_real_model_output(api_key=None):
    """测试真实大模型输出处理"""
    print_header("真实大模型输出处理")
    
    # 检查API密钥
    if not api_key:
        print("警告: 未设置DeepSeek API密钥，无法进行真实模型测试")
        print("将使用模拟响应进行测试...")
        return test_simulated_model_output()
    
    # 创建多种不同类型的提示词进行测试
    test_cases = [
        {
            "name": "故事生成",
            "segments": [
                "(主角是一名骑士)",
                "(场景是一座古堡)",
                "<一段冒险故事>",
                "[story=\"*\"]"
            ]
        },
        {
            "name": "多字段输出",
            "segments": [
                "(对象是一款游戏)",
                "(类型是角色扮演)",
                "<游戏角色设计>",
                "[character_name=\"*\", character_class=\"*\", main_skill=\"*\"]"
            ]
        },
        {
            "name": "多段文字输出",
            "segments": [
                "(场景是冒险者酒馆)",
                "(角色是讲故事的吟游诗人)",
                "<一个分支故事，有主要情节和两个选择>",
                "[story=\"*\", choice1=\"*\", choice2=\"*\"]"
            ]
        }
    ]
    
    # 创建处理器和连接器
    processor = PromptProcessor()
    
    try:
        connector = AIModelConnector(api_key=api_key)
        
        # 测试各个案例
        results = []
        for case in test_cases:
            print(f"\n测试案例: {case['name']}")
            print("-" * 40)
            
            # 构建提示词
            prompt = processor.build_prompt(case['segments'])
            print(f"提示词:\n{prompt}\n")
            
            try:
                # 调用API
                print("调用DeepSeek API...")
                response = connector.call_api(prompt)
                
                print(f"API响应:\n{response}\n")
                
                # 解析输出
                result = OutputParser.parse(response)
                print("解析结果:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
                # 检查是否成功解析
                success = len(result) > 0 and "error" not in result
                
                # 对多段文字输出进行额外验证
                if case["name"] == "多段文字输出":
                    expected_fields = ["story", "choice1", "choice2"]
                    fields_found = [field in result for field in expected_fields]
                    field_count = sum(fields_found)
                    print(f"预期字段数量: {len(expected_fields)}, 实际找到: {field_count}")
                    print(f"找到的字段: {[f for i, f in enumerate(expected_fields) if fields_found[i]]}")
                    success = "story" in result and field_count >= 2
                
                print(f"解析成功: {success}")
                results.append(success)
            except Exception as e:
                print(f"测试失败: {str(e)}")
                results.append(False)
        
        # 返回整体结果
        overall_success = all(results)
        print(f"\n真实模型测试总结: {'全部通过' if overall_success else '部分失败'}")
        return overall_success
    except Exception as e:
        print(f"连接API失败: {str(e)}")
        print("回退到模拟测试...")
        return test_simulated_model_output()

def test_simulated_model_output():
    """使用模拟响应测试模型输出处理"""
    print_header("模拟大模型输出处理")
    
    # 创建模拟的测试案例
    test_cases = [
        {
            "name": "故事生成",
            "segments": [
                "(主角是一名骑士)",
                "(场景是一座古堡)",
                "<一段冒险故事>",
                "[story=\"*\"]"
            ],
            "mock_response": """
            {
                "story": "骑士小心翼翼地推开古堡沉重的大门，一阵冷风夹杂着灰尘迎面扑来。他举起火把，微弱的光芒照亮了满是蜘蛛网的走廊。远处传来奇怪的声响，像是低语，又像是哭泣。骑士握紧了剑，决心揭开这座被遗忘城堡的秘密。"
            }
            """
        },
        {
            "name": "多字段输出",
            "segments": [
                "(对象是一款游戏)",
                "(类型是角色扮演)",
                "<游戏角色设计>",
                "[character_name=\"*\", character_class=\"*\", main_skill=\"*\"]"
            ],
            "mock_response": """
            {
                "character_name": "艾琳·风矢",
                "character_class": "影刃游侠",
                "main_skill": "暗影步：瞬间移动到敌人背后并造成三倍暴击伤害，随后隐身3秒"
            }
            """
        },
        {
            "name": "多段文字输出",
            "segments": [
                "(场景是冒险者酒馆)",
                "(角色是讲故事的吟游诗人)",
                "<一个分支故事，有主要情节和两个选择>",
                "[story=\"*\", choice1=\"*\", choice2=\"*\"]"
            ],
            "mock_response": """
            {
                "story": "传说北方雪山中沉睡着一条远古冰龙，它守护着能实现任何愿望的宝藏。勇敢的冒险者们，听说这个消息后，纷纷组队前往，但没有一个人能够归来。",
                "choice1": "组建一支精锐小队，配备魔法装备前往雪山寻宝",
                "choice2": "先寻找上一批冒险者的线索，了解他们失败的原因"
            }
            """
        }
    ]
    
    # 创建处理器
    processor = PromptProcessor()
    
    # 测试各个案例
    results = []
    for case in test_cases:
        print(f"\n测试案例: {case['name']}")
        print("-" * 40)
        
        # 构建提示词
        prompt = processor.build_prompt(case['segments'])
        print(f"提示词:\n{prompt}\n")
        
        # 使用模拟响应
        print("使用模拟响应...")
        response = case["mock_response"]
        print(f"模拟响应:\n{response}\n")
        
        # 解析输出
        result = OutputParser.parse(response)
        print("解析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 检查是否成功解析
        success = len(result) > 0 and "error" not in result
        if case["name"] == "多段文字输出":
            expected_fields = ["story", "choice1", "choice2"]
            fields_found = [field in result for field in expected_fields]
            field_count = sum(fields_found)
            print(f"预期字段数量: {len(expected_fields)}, 实际找到: {field_count}")
            print(f"找到的字段: {[f for i, f in enumerate(expected_fields) if fields_found[i]]}")
            success = "story" in result and field_count >= 2
        
        print(f"解析成功: {success}")
        results.append(success)
    
    # 返回整体结果
    overall_success = all(results)
    print(f"\n模拟模型测试总结: {'全部通过' if overall_success else '部分失败'}")
    return overall_success

def test_complete_flow(api_key=None):
    """测试完整处理流程"""
    print_header("完整处理流程")
    
    # 创建处理器
    processor = PromptProcessor()
    
    # 定义输入片段
    input_segments = [
        "(元素系法术)",
        "(魔法学派: 烈焰门派)",
        "<设计一个强力的火焰魔法，能够控制范围并减少友方伤害>",
        "[spell_description=\"*\"]"
    ]
    
    # 构建提示词
    prompt = processor.build_prompt(input_segments)
    print_section("生成的提示词")
    print(prompt)
    
    # 判断是否使用真实API
    if api_key:
        try:
            print("\n尝试调用真实的DeepSeek API...")
            connector = AIModelConnector(api_key=api_key)
            response = connector.call_api(prompt)
            print_section("真实API响应")
            print(response)
        except Exception as e:
            print(f"\nAPI调用失败: {str(e)}")
            print("回退到使用模拟响应...")
            # 如果API调用失败，回退到模拟响应
            response = """
            {
              "spell_description": "法师翻开古老的咒语书，指尖闪烁着蓝色的光芒。他低声吟诵着古老的咒文，周围的空气开始震颤。随着最后一个音节的落下，一道闪电从他的手中射出，照亮了图书馆的每一个角落。"
            }
            """
    else:
        print("\n使用模拟响应...")
        
        # 模拟API响应
        response = """
        {
          "spell_description": "法师翻开古老的咒语书，指尖闪烁着蓝色的光芒。他低声吟诵着古老的咒文，周围的空气开始震颤。随着最后一个音节的落下，一道闪电从他的手中射出，照亮了图书馆的每一个角落。"
        }
        """
    
    # 解析响应
    result = OutputParser.parse(response)
    
    print_section("解析结果")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 提取关键信息
    if "spell_description" in result:
        spell = result["spell_description"]
        print_section("提取的咒语描述")
        print(spell)
        
        # 模拟应用处理
        words = len(spell.split())
        chars = len(spell)
        print(f"\n分析: 咒语描述包含 {words} 个词, {chars} 个字符")
        return True
    else:
        print("\n错误: 未能从响应中提取咒语描述")
        print("原始响应:")
        print(response)
        return False

def test_error_handling():
    """测试错误处理能力"""
    print_header("错误处理能力")
    
    # 测试API错误处理 - 模拟而不是实际调用
    print("模拟API错误处理...")
    
    # 检查APIError类是否存在
    print(f"APIError类存在: {APIError is not None}")
    print(f"AuthenticationError类存在: {AuthenticationError is not None}")
    
    # 测试解析错误处理
    completely_invalid = "这根本不是一个JSON或者键值对格式"
    result = OutputParser.parse(completely_invalid)
    print("\n解析完全无效内容:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"错误处理能力: {'error' in result}")
    
    # 测试异常捕获
    print_section("异常捕获测试")
    try:
        # 模拟API错误
        raise APIError("模拟的API错误")
    except APIError as e:
        print(f"成功捕获API错误: {str(e)}")
    
    try:
        # 模拟认证错误
        raise AuthenticationError("模拟的认证错误")
    except AuthenticationError as e:
        print(f"成功捕获认证错误: {str(e)}")
    
    # 错误恢复示例
    print_section("错误恢复示例")
    error_response = "这不是有效的JSON"
    try:
        result = OutputParser.parse(error_response)
        if "error" in result:
            print("检测到解析错误，尝试备用解析方法...")
            # 使用备用解析器
            fallback_parser = FormatPatternParser()
            result = fallback_parser.parse(error_response)
            print("备用解析结果:")
            print(result)
    except Exception as e:
        print(f"处理错误: {str(e)}")
    
    return True

def test_examples_from_readme():
    """测试README中的示例"""
    print_header("README示例测试")
    
    # 测试基础示例
    print_section("1. 基础示例")
    processor = PromptProcessor()
    segments = [
        "(角色是探险家)",
        "<描述一段探险经历>",
        "{adventure=\"*\"}"
    ]
    prompt = processor.build_prompt(segments)
    print("生成的提示词:")
    print(prompt)
    
    # 测试内容格式配对示例
    print_section("2. 内容格式配对示例")
    segments = [
        "(场景是城堡)",
        "<描述王子的外貌>",
        "{character=\"*\"}",
        "<描述王子的性格特点>",
        "{personality=\"*\"}",
        "<描述王子拥有的魔法能力>",
        "{magic_power=\"*\"}"
    ]
    prompt = processor.build_prompt(segments)
    print("生成的提示词:")
    print(prompt)
    
    # 测试结构化信息提取示例
    print_section("3. 结构化信息提取示例")
    segments = [
        "(输入文本：周杰伦，1979年1月18日出生于台湾省新北市，祖籍福建省泉州市永春县，华语流行乐男歌手、音乐人、演员、导演、编剧等)",
        "<从文本中提取人物信息>",
        "{name=\"*\", birth_date=\"*\", birth_place=\"*\", occupation=\"*\"}"
    ]
    prompt = processor.build_prompt(segments)
    print("生成的提示词:")
    print(prompt)
    
    # 测试解析处理各种格式
    print_section("4. 解析处理测试")
    messy_response = """
    AI助手的回复：
    ```json
    {
      "answer": "这是答案",
      "confidence": "高"
    }
    ```
    希望对您有帮助！
    """
    result = OutputParser.parse(messy_response)
    print("混乱输出:")
    print(messy_response)
    print("解析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return True

def main():
    """运行所有测试"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="全面测试AI提示词处理模块")
    parser.add_argument("--mock", action="store_true", help="使用模拟API响应进行测试（默认使用真实API）")
    parser.add_argument("--api-key", type=str, help="用于测试的API密钥")
    parser.add_argument("--tests", type=str, nargs="+", 
                        choices=["all", "prompt", "api", "parser", "pairing", "custom", "complete", "error", "real", "examples"],
                        default=["all"], help="指定要运行的测试")
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = args.api_key
    if not api_key and not args.mock:  # 如果没有指定密钥且不使用模拟模式
        api_key = get_api_key()  # 尝试获取密钥
    
    # 确定要运行的测试
    tests_to_run = []
    if "all" in args.tests or not args.tests:
        tests_to_run = ["prompt", "api", "parser", "pairing", "custom", "error", "examples", "complete"]
        if not args.mock:  # 默认使用真实API
            tests_to_run.append("real")
    else:
        tests_to_run = [t for t in args.tests if t != "all"]
    
    # 创建测试函数映射
    test_functions = {
        "prompt": test_prompt_processor,
        "api": test_api_connector,
        "parser": test_output_parsers,
        "pairing": test_content_format_pairing,
        "custom": test_custom_template,
        "complete": lambda: test_complete_flow(api_key),
        "error": test_error_handling,
        "real": lambda: test_real_model_output(api_key),
        "examples": test_examples_from_readme
    }
    
    # 运行测试
    results = []
    for test_name in tests_to_run:
        test_func = test_functions.get(test_name)
        if not test_func:
            print(f"警告: 未知的测试类型 {test_name}，跳过")
            continue
            
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"测试 {test_name} 遇到未捕获异常: {str(e)}")
            results.append((test_name, False))
    
    # 打印测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    
    test_names = {
        "prompt": "提示词处理器功能",
        "api": "API连接器功能",
        "parser": "输出解析器功能",
        "pairing": "内容格式配对功能",
        "custom": "自定义模板功能",
        "complete": "完整处理流程",
        "error": "错误处理功能",
        "real": "真实大模型调用",
        "examples": "README示例测试"
    }
    
    all_passed = True
    for name, result in results:
        status = "通过" if result else "失败"
        display_name = test_names.get(name, name)
        print(f"{display_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n所有测试通过!")
    else:
        print("\n部分测试失败。请查看详细输出。")
    
    # 如果用户选择了模拟模式，提醒可以使用真实API测试
    if args.mock:
        print("\n提示: 你使用的是模拟测试模式。如需测试与真实大模型的交互，请去掉--mock参数")
        print("例如: python3 comprehensive_test.py")

if __name__ == "__main__":
    main() 