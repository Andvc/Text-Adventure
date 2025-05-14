#!/usr/bin/env python3
"""
游戏管理器模块

整合角色创建和能力生成器等功能，提供统一的调用接口
"""

import os
import sys
import time
from typing import Dict, List, Any, Optional, Tuple, Union

# 确保可以导入上级目录的模块
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from gameflow.core import GameFlow
from gameflow.character_creation import CharacterCreationManager
from data.data_manager import load_save, save_data, create_save, delete_save, list_saves

class GameManager:
    """游戏管理器
    
    整合角色创建和能力生成器等核心游戏功能，提供简洁的调用接口
    """
    
    def __init__(self):
        """初始化游戏管理器"""
        self.game_flow = GameFlow()
        self.character_manager = CharacterCreationManager()
        self.current_save_id = None
        
        # 初始化能力生成器
        try:
            from gameflow.power_generator import PowerGenerator
            self.power_generator = PowerGenerator()
        except ImportError:
            print("警告: 能力生成器模块未找到")
            self.power_generator = None
    
    def create_new_character(self) -> Dict:
        """创建新角色的便捷方法
        
        Returns:
            Dict: 创建结果，包含成功状态和角色信息
        """
        result = self.character_manager.run_character_creation_flow()
        if result.get("success"):
            self.current_save_id = result.get("save_id")
        return result
    
    def load_character(self, save_id: str) -> bool:
        """加载角色存档
        
        Args:
            save_id: 存档ID
            
        Returns:
            bool: 是否成功加载
        """
        save_data = load_save("character", save_id)
        if save_data:
            self.current_save_id = save_id
            return True
        return False
    
    def list_available_characters(self) -> List[Dict]:
        """列出所有可用的角色存档
        
        Returns:
            List[Dict]: 角色存档信息列表
        """
        saves = list_saves("character")
        characters = []
        
        for save_id in saves:
            save_data = load_save("character", save_id)
            if save_data and not save_id.startswith("temp_"):
                characters.append({
                    "id": save_id,
                    "name": save_data.get("name", "未命名角色"),
                    "era": save_data.get("era", {}).get("name", "未知纪元"),
                    "race": save_data.get("race", {}).get("sub_race", "未知种族"),
                    "career": save_data.get("career", {}).get("name", "未知职业"),
                    "level": save_data.get("stats", {}).get("level", 1),
                    "created_at": save_data.get("created_at", "未知时间")
                })
        
        return characters
    
    def generate_power_item(self, item_type: str, level: int, detail: str = "") -> Optional[Dict]:
        """生成能力或物品的便捷方法
        
        Args:
            item_type: 物品类型，如'weapon'或'career'
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict: 生成的物品详情，如果失败则返回None
        """
        if not self.power_generator:
            print("错误: 能力生成器模块未找到")
            return None
            
        if not self.current_save_id:
            print("错误: 未选择角色")
            return None
            
        try:
            return self.power_generator.generate_power_item(self.current_save_id, item_type, level, detail)
        except Exception as e:
            print(f"生成{item_type}失败: {str(e)}")
            return None
    
    def get_character_items(self, item_type: str) -> List[Dict]:
        """获取角色的特定类型物品列表
        
        Args:
            item_type: 物品类型，如'weapon'或'career'
            
        Returns:
            List[Dict]: 物品列表，如果没有则返回空列表
        """
        if not self.current_save_id:
            print("错误: 未选择角色")
            return []
            
        character = self.get_current_character()
        if not character:
            return []
            
        # 获取物品数组
        items_array_key = f"{item_type}s"  # 例如：weapons, careers
        return character.get(items_array_key, [])
    
    def get_current_character(self) -> Optional[Dict]:
        """获取当前角色的详细信息
        
        Returns:
            Dict: 角色详细信息，如果未选择角色则返回None
        """
        if not self.current_save_id:
            return None
            
        return load_save("character", self.current_save_id)
    
    def save_current_character(self) -> bool:
        """保存当前角色的状态
        
        Returns:
            bool: 是否成功保存
        """
        if not self.current_save_id:
            print("错误: 未选择角色")
            return False
            
        character_data = load_save("character", self.current_save_id)
        if not character_data:
            print("错误: 无法加载角色数据")
            return False
            
        # 更新最后保存时间
        character_data["last_saved"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        
        return save_data("character", self.current_save_id, character_data) 