#!/usr/bin/env python3
"""
Simple Loop循环测试

此脚本用于测试simple_loop模板的循环功能:
1. 使用simple_loop存档作为角色数据
2. 使用simple_loop模板生成故事
3. 显示选项并让用户选择
4. 将用户选择存储到"事件选择"属性中
5. 自动开始下一轮循环
"""

import os
import sys
import json
from pathlib import Path
import textwrap

# 修复导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入故事线模块
from storyline.storyline_manager import StorylineManager

# 导入角色模块
from character.character_manager import (
    get_attribute,
    set_attribute,
    get_all_attributes,
    configure_save_system,
    list_saves,
    load_save,
    load_previous_game,
    get_current_save_name
)

class SimpleLoopTester:
    """Simple Loop循环测试器"""
    
    def __init__(self):
        """初始化测试器"""
        # 配置初始存档系统
        configure_save_system()
        
        # 尝试加载上次使用的存档
        self.print_header("存档加载", width=80)
        
        # 获取可用存档列表
        saves = list_saves()
        simple_loop_exists = "simple_loop" in saves
        
        # 检查上次存档
        last_save_loaded = False
        if load_previous_game():
            last_save = get_current_save_name()
            print(f"已自动加载上次使用的存档: {last_save}")
            
            # 让用户确认是否使用该存档
            if input("是否使用此存档继续？(y/n): ").lower() != 'y':
                last_save_loaded = False
            else:
                last_save_loaded = True
                print(f"将使用存档 '{last_save}' 继续")
        
        # 如果没有加载上次存档，则加载simple_loop或创建新存档
        if not last_save_loaded:
            if simple_loop_exists:
                print("找到simple_loop存档，正在加载...")
                load_save("simple_loop")
            else:
                print("未找到simple_loop存档，将配置新的simple_loop存档...")
                configure_save_system(save_file="simple_loop.json")
        
        # 初始化故事线管理器
        self.manager = StorylineManager()
        
        # 循环计数
        self.loop_count = 0
    
    def print_header(self, text, width=80):
        """打印带框的标题"""
        print("\n" + "=" * width)
        print(text.center(width))
        print("=" * width)
    
    def print_section(self, title, text, width=80):
        """打印带子标题的内容部分"""
        print("\n" + "-" * width)
        print(f"| {title} ".ljust(width-1, "-") + "|")
        print("-" * width)
        
        # 自动换行
        wrapped_text = textwrap.fill(text, width=width-2)
        for line in wrapped_text.split('\n'):
            print(f"  {line}")
    
    def print_choices(self, choices):
        """打印可选选项"""
        self.print_section("可选选项", "请选择一个选项：")
        
        for i, choice in enumerate(choices):
            print(f"  [{i+1}] {choice}")
    
    def print_status(self):
        """打印当前状态"""
        self.print_section("当前状态", "角色信息和故事状态：")
        
        # 获取当前存档名称
        current_save = get_current_save_name()
        print(f"  当前存档: {current_save}")
        
        # 获取所有属性
        all_attrs = get_all_attributes()
        
        # 显示关键属性（如果存在）
        basic_info = []
        if "姓名" in all_attrs:
            basic_info.append(f"角色: {all_attrs['姓名']}")
        if "世界" in all_attrs:
            basic_info.append(f"世界: {all_attrs['世界']}")
        if "境界" in all_attrs:
            basic_info.append(f"境界: {all_attrs['境界']}")
        
        # 打印基本信息
        if basic_info:
            print("  " + "  |  ".join(basic_info))
        
        # 打印故事信息
        if "故事梗概" in all_attrs:
            print("\n  【故事梗概】")
            wrapped_summary = textwrap.fill(all_attrs["故事梗概"], width=76)
            for line in wrapped_summary.split('\n'):
                print(f"  {line}")
        
        if "当前事件" in all_attrs:
            print("\n  【当前事件】")
            wrapped_event = textwrap.fill(all_attrs["当前事件"], width=76)
            for line in wrapped_event.split('\n'):
                print(f"  {line}")
        
        if "事件选择" in all_attrs and all_attrs["事件选择"]:
            print("\n  【上次选择】")
            print(f"  {all_attrs['事件选择']}")
    
    def get_choice_options(self):
        """从角色属性中获取选项"""
        all_attrs = get_all_attributes()
        choices = []
        
        # 首先尝试最常见的选项属性命名
        option_names = ["选项1", "选项2", "选项3", "option1", "option2", "option3"]
        
        for name in option_names:
            if name in all_attrs and all_attrs[name]:
                choices.append(all_attrs[name])
        
        # 如果没有找到标准命名的选项，尝试查找其他可能的选项属性
        if not choices:
            # 查找所有包含"选项"、"option"或"choice"的属性
            for name, value in all_attrs.items():
                if (("选项" in name or "option" in name.lower() or "choice" in name.lower()) 
                    and value and isinstance(value, str) 
                    and name not in ["事件选择", "last_choice"]):
                    choices.append(value)
        
        # 如果还是找不到，将所有包含关键词的属性名打印出来，帮助调试
        if not choices:
            print("\n未找到选项属性。正在检查所有属性:")
            for name, value in all_attrs.items():
                print(f"  - {name}: {type(value).__name__}{'，有值' if value else '，无值'}")
            print("\n提示: 请确保模板的output_storage将choice1/choice2/choice3映射到角色属性")
        
        return choices
    
    def run_single_loop(self):
        """运行单次循环"""
        self.loop_count += 1
        
        # 显示循环开始标题
        self.print_header(f"开始第 {self.loop_count} 轮循环")
        
        # 显示当前状态
        self.print_status()
        
        # 生成故事
        try:
            self.print_section("生成故事", "正在使用simple_loop模板生成故事...")
            
            # 生成故事（将会存储到角色属性中）
            _, _, _ = self.manager.generate_story("simple_loop")
            
            # 直接从角色属性中获取当前故事
            current_story = get_attribute("当前事件")
            if not current_story:
                raise ValueError("生成故事失败：未找到'当前事件'属性")
            
            # 显示故事内容
            self.print_section("故事内容", current_story)
            
            # 从角色属性中获取选项
            choices = self.get_choice_options()
            if not choices:
                # 如果没有找到选项，尝试生成一些默认选项
                print("\n警告：未找到选项属性，使用默认选项继续")
                choices = [
                    "继续探索这个神秘空间",
                    "尝试退出这个神秘空间",
                    "思考下一步行动"
                ]
            
            # 显示选项
            self.print_choices(choices)
            
            # 获取用户选择
            while True:
                try:
                    choice = int(input("\n请输入选项编号 (1-{0}): ".format(len(choices))))
                    if 1 <= choice <= len(choices):
                        choice_index = choice - 1
                        break
                    else:
                        print(f"无效选择，请输入1-{len(choices)}之间的数字")
                except ValueError:
                    print("请输入有效的数字")
            
            # 确认用户选择
            selected_choice = choices[choice_index]
            print(f"\n你选择了: {selected_choice}")
            
            # 直接将选择存储到事件选择属性
            set_attribute("事件选择", selected_choice)
            print("\n选择已记录，属性已更新。")
            
            # 显示更新后的状态
            self.print_section("更新后状态", "属性已更新:")
            
            # 直接显示更新后的关键属性
            all_attrs = get_all_attributes()
            if "当前事件" in all_attrs:
                event_preview = all_attrs["当前事件"][:100] + "..." if len(all_attrs["当前事件"]) > 100 else all_attrs["当前事件"]
                print(f"  当前事件: {event_preview}")
            if "事件选择" in all_attrs:
                print(f"  事件选择: {all_attrs['事件选择']}")
            if "故事梗概" in all_attrs:
                summary_preview = all_attrs["故事梗概"][:100] + "..." if len(all_attrs["故事梗概"]) > 100 else all_attrs["故事梗概"]
                print(f"  故事梗概: {summary_preview}")
            
            return True
            
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            return False
    
    def run(self, max_loops=10):
        """运行循环测试
        
        Args:
            max_loops: 最大循环次数，防止无限循环
        """
        self.print_header("Simple Loop循环测试开始")
        
        print("此测试将使用simple_loop模板进行循环测试。")
        print("每轮循环将生成一个故事，让你做出选择，然后进入下一轮。")
        print(f"最大循环次数设置为 {max_loops} 轮。")
        
        # 检查初始状态
        print("\n正在检查初始状态...")
        
        # 确保事件选择有初始值
        if not get_attribute("事件选择"):
            set_attribute("事件选择", "开始故事")
            print("已设置初始事件选择为'开始故事'")
        
        # 运行循环
        for _ in range(max_loops):
            # 运行单次循环
            success = self.run_single_loop()
            if not success:
                break
                
            # 自动继续下一轮循环，不询问用户
            print("\n自动继续下一轮循环...")
        
        # 测试完成
        self.print_header("测试完成")
        print(f"共完成 {self.loop_count} 轮循环")
        
        # 显示最终状态
        self.print_status()

def main():
    """主函数"""
    tester = SimpleLoopTester()
    tester.run()

if __name__ == "__main__":
    main() 