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
    configure_save_system
)

class SimpleLoopTester:
    """Simple Loop循环测试器"""
    
    def __init__(self):
        """初始化测试器"""
        # 配置存档为simple_loop
        configure_save_system(save_file="simple_loop.json")
        
        # 初始化故事线管理器
        self.manager = StorylineManager()
        
        # 循环计数
        self.loop_count = 0
        
        # 输出缓存
        self.output_cache = {}
        
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
            print(f"  [{i+1}] {choice['text']}")
    
    def print_status(self):
        """打印当前状态"""
        self.print_section("当前状态", "角色信息和故事状态：")
        
        # 获取关键属性
        name = get_attribute("姓名")
        world = get_attribute("世界")
        level = get_attribute("境界")
        story_summary = get_attribute("故事梗概")
        current_event = get_attribute("当前事件")
        last_choice = get_attribute("事件选择")
        
        # 显示基本信息
        print(f"  角色: {name}  |  世界: {world}  |  境界: {level}")
        
        # 显示故事信息
        print("\n  【故事梗概】")
        wrapped_summary = textwrap.fill(story_summary, width=76)
        for line in wrapped_summary.split('\n'):
            print(f"  {line}")
        
        print("\n  【当前事件】")
        wrapped_event = textwrap.fill(current_event, width=76)
        for line in wrapped_event.split('\n'):
            print(f"  {line}")
        
        if last_choice:
            print("\n  【上次选择】")
            print(f"  {last_choice}")
    
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
            
            story_content, choices, story_id = self.manager.generate_story("simple_loop")
            
            # 缓存输出以备使用
            self.output_cache = {
                "story_content": story_content,
                "choices": choices,
                "story_id": story_id
            }
            
            # 显示生成的故事
            self.print_section("故事内容", story_content)
            
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
            print(f"\n你选择了: {selected_choice['text']}")
            
            # 执行选择（这会自动更新当前事件等属性）
            self.manager.make_choice(story_id, choice_index)
            
            # 确保事件选择字段已更新（以防模板没有做这个更新）
            set_attribute("事件选择", selected_choice['text'])
            
            print("\n选择已记录，属性已更新。")
            
            # 显示更新后的状态
            self.print_section("更新后状态", "属性已更新:")
            print(f"  当前事件: {get_attribute('当前事件')[:100]}...")
            print(f"  事件选择: {get_attribute('事件选择')}")
            print(f"  故事梗概: {get_attribute('故事梗概')[:100]}...")
            
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
                
            # 询问是否继续
            while True:
                answer = input("\n是否继续下一轮循环？(y/n): ").lower()
                if answer in ['y', 'yes', 'n', 'no']:
                    break
                print("请输入y或n")
                
            if answer in ['n', 'no']:
                print("用户选择终止循环")
                break
        
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