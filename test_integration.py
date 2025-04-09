"""
AI模块和Character模块集成测试程序

这个脚本测试AI模块和Character模块之间的集成功能：
1. 使用Character模块创建角色属性
2. 使用这些属性构建AI提示词
3. 实际调用API生成故事和选择
4. 更新角色属性
"""

import os
import sys
import json
from pathlib import Path

# 修复导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'ai'))

# 导入AI模块的完整组件
from ai.prompt_processor import PromptProcessor
from ai.api_connector import AIModelConnector
from ai.output_parsers import OutputParser

# 导入Character模块
from character.character_manager import (
    create_attribute,
    get_attribute,
    set_attribute,
    list_attributes,
    get_all_attributes,
    configure_save_system
)

def create_basic_character():
    """创建一个基础角色，包含名称、性别、背景和基础属性"""
    print("========== 创建角色 ==========")
    
    # 配置存档位置为测试存档
    configure_save_system(save_file="test_character.json")
    
    # 创建角色基本信息
    create_attribute("name", "李逍遥")
    create_attribute("gender", "男")
    create_attribute("background", "自小在青青的山野长大，性格乐观开朗，身手敏捷。"
                                  "在一次上山采药时，偶然发现了一本古籍《御剑术》，"
                                  "自此开始修习剑法，并立志成为一名行侠仗义的剑客。")
    
    # 创建角色属性
    create_attribute("strength", 8)      # 力量
    create_attribute("agility", 12)      # 敏捷
    create_attribute("intelligence", 10)  # 智力
    create_attribute("constitution", 9)   # 体质
    create_attribute("charisma", 11)      # 魅力
    
    # 技能和装备
    create_attribute("skills", ["基础剑法", "轻功", "药理知识"])
    create_attribute("equipment", {"weapon": "青锋剑", "armor": "布衣", "accessory": "药草包"})
    
    # 初始化冒险次数
    create_attribute("adventure_count", 0)
    
    # 显示角色信息
    print(f"角色创建完成: {get_attribute('name')}")
    print(f"性别: {get_attribute('gender')}")
    print(f"背景: {get_attribute('background')}")
    print("\n属性:")
    print(f"力量: {get_attribute('strength')}")
    print(f"敏捷: {get_attribute('agility')}")
    print(f"智力: {get_attribute('intelligence')}")
    print(f"体质: {get_attribute('constitution')}")
    print(f"魅力: {get_attribute('charisma')}")
    
    print("\n技能:", get_attribute("skills"))
    print("装备:", get_attribute("equipment"))
    
    return True

def build_story_prompt():
    """使用角色信息构建故事提示"""
    print("\n========== 构建提示词 ==========")
    
    # 获取角色信息
    name = get_attribute("name")
    background = get_attribute("background")
    strength = get_attribute("strength")
    agility = get_attribute("agility")
    intelligence = get_attribute("intelligence")
    charisma = get_attribute("charisma")
    skills = get_attribute("skills")
    equipment = get_attribute("equipment")
    
    # 构建提示片段
    segments = [
        f"(角色名称: {name})",
        f"(角色背景: {background})",
        f"(角色属性: 力量={strength}, 敏捷={agility}, 智力={intelligence}, 魅力={charisma})",
        f"(角色技能: {json.dumps(skills, ensure_ascii=False)})",
        f"(角色装备: {json.dumps(equipment, ensure_ascii=False)})",
        "<讲述一段这个角色的冒险故事>",
        "{story=\"*\"}",
        "<提供三个可能的选择，这些选择将影响角色的发展>",
        "{choice1=\"*\", choice2=\"*\", choice3=\"*\"}",
        "<描述每个选择可能带来的属性变化>",
        "{stat_change1=\"*\", stat_change2=\"*\", stat_change3=\"*\"}"
    ]
    
    return segments

def generate_adventure_story(segments):
    """使用AI生成冒险故事（实际调用API）"""
    print("\n========== 生成故事（API调用） ==========")
    
    try:
        # 创建提示词处理器
        processor = PromptProcessor()
        
        # 构建提示词
        prompt = processor.build_prompt(segments)
        print("生成的提示词:")
        print(prompt)
        
        # 调用API
        connector = AIModelConnector()
        print("\n正在调用AI API...")
        response = connector.call_api(prompt)
        print("\nAPI响应:")
        print(response)
        
        # 解析结果
        result = OutputParser.parse(response)
        print("\n解析后的结构化数据:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
    
    except Exception as e:
        print(f"\n出错: {str(e)}")
        print("提示: 请确保已设置有效的API密钥。如果需要使用模拟数据进行测试，请运行带有--mock参数的脚本。")
        # 如果API调用失败，返回模拟数据作为备选方案
        print("\n使用模拟数据作为备选...")
        return use_mock_data()

def use_mock_data():
    """使用模拟数据作为备选方案"""
    mock_response = {
        "story": "李逍遥手持青锋剑，轻盈地穿过竹林。他正追踪一伙据说在附近出没的山贼，这些山贼最近频繁骚扰村民。凭借着敏捷的身手和轻功，他很快就发现了山贼的藏身之处——一个隐蔽在山腰的山洞。\n\n借着夜色的掩护，李逍遥悄悄接近山洞。洞口有两名山贼守卫，他们正百无聊赖地打着瞌睡。凭借在山野中锻炼出的敏捷，他轻易地避开了守卫，潜入了山洞深处。\n\n在山洞内部，李逍遥发现了一个出乎意料的场景：一位老者被绑在角落，而山贼头目正对着一本古籍发出狂笑。凭借过人的智力，李逍遥立刻认出那本书正是与他习得的《御剑术》出自同源的《风云剑谱》。这本剑谱若是落入心术不正之人手中，后果不堪设想。",
        "choice1": "直接冲上前去挑战山贼头目，解救老者并夺回剑谱",
        "choice2": "利用药理知识配制迷烟，趁山贼不备放倒他们，神不知鬼不觉地救人夺宝",
        "choice3": "先悄悄退出山洞，去附近村庄寻求支援，再一同剿灭山贼",
        "stat_change1": "力量+2（通过激烈的战斗提升力量），敏捷+1（剑法实战经验），体质-1（受伤消耗）",
        "stat_change2": "智力+2（药理知识实践），敏捷+1（潜行技巧提升），魅力-1（行事隐秘减少声望）",
        "stat_change3": "魅力+2（赢得村民信任），智力+1（策略思考），力量-1（错失单独练习剑法的机会）"
    }
    print("\n模拟的数据:")
    print(json.dumps(mock_response, indent=2, ensure_ascii=False))
    return mock_response

def update_character_with_story(story_data):
    """使用故事数据更新角色属性"""
    print("\n========== 更新角色数据 ==========")
    
    if not story_data:
        print("没有故事数据，无法更新角色")
        return False
    
    # 保存故事和选择
    set_attribute("current_story", story_data["story"])
    set_attribute("current_choices", [
        story_data["choice1"],
        story_data["choice2"],
        story_data["choice3"]
    ])
    set_attribute("potential_stat_changes", [
        story_data["stat_change1"],
        story_data["stat_change2"],
        story_data["stat_change3"]
    ])
    
    print("已将故事和选择保存到角色属性中:")
    print(f"故事: {get_attribute('current_story')[:100]}...")
    print("\n可用选择:")
    for i, choice in enumerate(get_attribute("current_choices")):
        print(f"{i+1}. {choice}")
    
    print("\n潜在属性变化:")
    for i, change in enumerate(get_attribute("potential_stat_changes")):
        print(f"选择{i+1}: {change}")
    
    return True

def simulate_player_choice():
    """模拟玩家做出选择并更新角色属性"""
    print("\n========== 模拟玩家选择 ==========")
    
    # 获取当前选择
    choices = get_attribute("current_choices")
    stat_changes = get_attribute("potential_stat_changes")
    
    print("请选择你要采取的行动 (1-3):")
    for i, choice in enumerate(choices):
        print(f"{i+1}. {choice}")
    
    # 在实际游戏中，这里会获取玩家输入
    # 这里我们模拟玩家选择了选项1
    choice_index = 0
    
    print(f"\n你选择了: {choices[choice_index]}")
    print(f"属性变化: {stat_changes[choice_index]}")
    
    # 设置选择记录
    set_attribute("last_choice", choices[choice_index])
    set_attribute("last_stat_change", stat_changes[choice_index])
    
    # 解析并应用属性变化
    # 这里简单解析了模拟数据中的属性变化描述
    print("\n应用属性变化:")
    
    # 假设格式是"力量+2，敏捷+1，体质-1"这样的
    changes = stat_changes[choice_index].split("，")
    for change in changes:
        if "力量" in change:
            value = int(change.split("力量")[1].strip()[0:2])
            set_attribute("strength", get_attribute("strength") + value)
            print(f"力量 {value:+d} -> {get_attribute('strength')}")
        
        elif "敏捷" in change:
            value = int(change.split("敏捷")[1].strip()[0:2])
            set_attribute("agility", get_attribute("agility") + value)
            print(f"敏捷 {value:+d} -> {get_attribute('agility')}")
        
        elif "智力" in change:
            value = int(change.split("智力")[1].strip()[0:2])
            set_attribute("intelligence", get_attribute("intelligence") + value)
            print(f"智力 {value:+d} -> {get_attribute('intelligence')}")
        
        elif "体质" in change:
            value = int(change.split("体质")[1].strip()[0:2])
            set_attribute("constitution", get_attribute("constitution") + value)
            print(f"体质 {value:+d} -> {get_attribute('constitution')}")
        
        elif "魅力" in change:
            value = int(change.split("魅力")[1].strip()[0:2])
            set_attribute("charisma", get_attribute("charisma") + value)
            print(f"魅力 {value:+d} -> {get_attribute('charisma')}")
    
    # 增加冒险次数
    current_adventure_count = get_attribute("adventure_count")
    set_attribute("adventure_count", current_adventure_count + 1)
    print(f"冒险次数: {get_attribute('adventure_count')}")
    
    return True

def main():
    """主函数，运行整个测试流程"""
    print("开始AI与Character模块集成测试\n")
    
    # 创建基础角色
    create_basic_character()
    
    # 构建故事提示
    segments = build_story_prompt()
    
    # 生成冒险故事（实际调用API）
    story_data = generate_adventure_story(segments)
    
    # 更新角色数据
    if story_data:
        update_character_with_story(story_data)
        
        # 模拟玩家选择
        simulate_player_choice()
        
        print("\n测试完成!")
    else:
        print("\n测试未完成，无法生成故事数据")

if __name__ == "__main__":
    main() 