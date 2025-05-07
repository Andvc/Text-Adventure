#!/usr/bin/env python3
"""
角色创建流程主入口

用于启动角色创建流程的独立脚本
"""

import os
import sys

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from gameflow.character_creation import CharacterCreationManager

def main():
    """主函数：启动角色创建流程"""
    try:
        # 创建角色创建管理器
        manager = CharacterCreationManager()
        
        # 运行角色创建流程
        result = manager.run_character_creation_flow()
        
        # 显示结果
        if result.get('success'):
            print("\n===== 角色创建完成 =====")
            print(f"角色: {result.get('character_name')}")
            print(f"纪元: {result.get('era')}")
            print(f"种族: {result.get('race')}")
            print(f"身份: {result.get('identity')}")
            print(f"存档ID: {result.get('save_id')}")
            print("\n您现在可以开始游戏，进入这个纪元的世界。")
        else:
            print(f"\n角色创建失败: {result.get('error')}")
            print("请重新尝试创建角色。")
    
    except KeyboardInterrupt:
        print("\n\n角色创建已取消。")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        print("请重新尝试创建角色。")

if __name__ == "__main__":
    main() 