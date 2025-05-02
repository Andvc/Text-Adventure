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
from data import data_manager

def create_test_save():
    """创建测试存档"""
    save_name = f"test_save_{int(time.time())}"
    print(f"创建新存档: {save_name}")
    
    success = data_manager.create_save(save_name, "测试角色", "这是一个用于测试存档记忆功能的存档")
    if success:
        print(f"创建存档 '{save_name}' 成功")
        
        # 添加一些测试属性
        data_manager.create_attribute("姓名", "测试角色")
        data_manager.create_attribute("等级", 1)
        data_manager.create_attribute("生命值", 100)
        
        print("已添加基本属性")
        return save_name
    else:
        print(f"创建存档 '{save_name}' 失败")
        return None

def test_save_memory():
    """测试存档记忆功能"""
    save_name = "test_save"
    
    # 创建新存档
    print("\n创建新存档...")
    success = data_manager.create_save(save_name, "测试角色", "这是一个用于测试存档记忆功能的存档")
    if not success:
        print("创建存档失败")
        return
    
    # 创建一些属性
    print("\n创建属性...")
    data_manager.create_attribute("姓名", "测试角色")
    data_manager.create_attribute("等级", 1)
    data_manager.create_attribute("生命值", 100)
    
    # 打印当前存档信息
    print("\n当前存档信息:")
    print_save_info()
    
    # 创建第二个存档
    print("\n创建第二个存档...")
    data_manager.create_save("test_save2", "测试角色2", "第二个测试存档")
    
    # 打印所有存档
    print("\n所有存档:")
    saves = data_manager.list_saves()
    for save in saves:
        print(f"- {save}")
        
    # 获取当前存档名称
    print("\n当前存档名称:")
    current_save = data_manager.get_current_save_name()
    print(f"当前存档: {current_save}")
    
    # 加载上一次的存档
    print("\n加载上一次的存档...")
    success = data_manager.load_previous_game()
    if success:
        print("成功加载上一次的存档")
        loaded_save = data_manager.get_current_save_name()
        print(f"加载的存档: {loaded_save}")
        
        # 验证属性值
        print("\n验证属性值:")
        name = data_manager.get_attribute("姓名")
        level = data_manager.get_attribute("等级")
        hp = data_manager.get_attribute("生命值")
        print(f"姓名: {name}")
        print(f"等级: {level}")
        print(f"生命值: {hp}")
    else:
        print("加载上一次的存档失败")

def main():
    """主函数"""
    print("存档记忆功能测试开始\n")
    
    # 运行测试
    test_save_memory()
    
    print("\n存档记忆功能测试结束")

if __name__ == "__main__":
    main() 