#!/usr/bin/env python3
"""
存档记忆功能测试脚本
"""

import os
import sys
import time

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入存档管理模块
from character import character_manager

def create_test_save():
    """创建测试存档"""
    save_name = f"test_save_{int(time.time())}"
    print(f"创建新存档: {save_name}")
    
    success = character_manager.create_save(save_name, "测试角色", "这是一个用于测试存档记忆功能的存档")
    if success:
        print(f"创建存档 '{save_name}' 成功")
        
        # 添加一些测试属性
        character_manager.create_attribute("姓名", "测试角色")
        character_manager.create_attribute("等级", 1)
        character_manager.create_attribute("生命值", 100)
        
        print("已添加基本属性")
        return save_name
    else:
        print(f"创建存档 '{save_name}' 失败")
        return None

def test_save_memory():
    """测试存档记忆功能"""
    print("\n===== 测试存档记忆功能 =====")
    
    # 1. 列出当前所有存档
    saves = character_manager.list_saves()
    print(f"当前存档列表: {saves}")
    
    # 2. 创建新的测试存档
    new_save = create_test_save()
    if not new_save:
        print("无法创建测试存档，测试终止")
        return
    
    # 3. 确认当前存档
    current_save = character_manager.get_current_save_name()
    print(f"当前活动存档: {current_save}")
    if current_save != new_save:
        print("警告: 当前存档名与创建的测试存档不符")
    
    # 4. 模拟程序重启
    print("\n--- 模拟程序重启 ---")
    
    # 5. 加载上次存档
    print("尝试加载上次使用的存档...")
    success = character_manager.load_previous_game()
    if success:
        loaded_save = character_manager.get_current_save_name()
        print(f"成功加载存档: {loaded_save}")
        
        # 检查是否正确加载了上次的存档
        if loaded_save == new_save:
            print("✅ 测试通过: 成功加载了上次使用的存档")
            
            # 读取属性以验证存档内容
            name = character_manager.get_attribute("姓名")
            level = character_manager.get_attribute("等级")
            hp = character_manager.get_attribute("生命值")
            
            print(f"角色信息: 姓名={name}, 等级={level}, 生命值={hp}")
        else:
            print("❌ 测试失败: 加载的存档与上次使用的不符")
    else:
        print("❌ 测试失败: 无法加载上次存档")

def main():
    """主函数"""
    print("存档记忆功能测试开始\n")
    
    # 运行测试
    test_save_memory()
    
    print("\n存档记忆功能测试结束")

if __name__ == "__main__":
    main() 