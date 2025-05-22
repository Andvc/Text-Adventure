#!/usr/bin/env python3
"""
背景生成管理模块

提供时代背景和家庭背景的生成功能，使用随机种子确保生成结果的多样性
"""

import os
import json
import random
import time
import sys
from typing import Dict, Any

# 确保可以导入上级目录的模块
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from data.data_manager import load_save, save_data, delete_save
from storyline.storyline_manager import StorylineManager

class BackgroundCreationManager:
    """背景生成管理器
    
    负责生成角色的时代背景和家庭背景，使用随机种子确保生成结果的多样性
    """
    
    def __init__(self):
        """初始化背景生成管理器"""
        self.storyline_manager = StorylineManager()
    
    def generate_era_background(self, random_seed: int) -> Dict[str, Any]:
        """生成时代背景
        
        Args:
            random_seed: 随机种子，用于确保生成结果的多样性
            
        Returns:
            Dict[str, Any]: 生成的时代背景，包含名称、特征和历史事件
            
        Raises:
            RuntimeError: 当生成失败时抛出
        """
        # 设置随机种子
        random.seed(random_seed)
        
        # 使用模板生成时代背景
        save_id = f"temp_era_{int(time.time())}"
        save_data_content = {
            "id": save_id,
            "random_seed": random_seed
        }
        
        # 创建临时存档
        save_data("character", save_id, save_data_content)
        
        # 生成时代背景
        generation_success = self.storyline_manager.generate_story(save_id, "era_background_generator")
        if not generation_success:
            raise RuntimeError("生成时代背景失败")
        
        # 重新加载存档以获取生成的内容
        updated_save = load_save("character", save_id)
        
        # 获取生成的时代背景
        era_background = updated_save.get("era", {})
        
        # 删除临时存档
        delete_save("character", save_id)
        
        return era_background
    
    def generate_family_background(self, random_seed: int) -> Dict[str, Any]:
        """生成家庭背景
        
        Args:
            random_seed: 随机种子，用于确保生成结果的多样性
            
        Returns:
            Dict[str, Any]: 生成的家庭背景，包含父母职业、家族地位、财富和家族历史
            
        Raises:
            RuntimeError: 当生成失败时抛出
        """
        # 设置随机种子
        random.seed(random_seed)
        
        # 使用模板生成家庭背景
        save_id = f"temp_family_{int(time.time())}"
        save_data_content = {
            "id": save_id,
            "random_seed": random_seed
        }
        
        # 创建临时存档
        save_data("character", save_id, save_data_content)
        
        # 生成家庭背景
        generation_success = self.storyline_manager.generate_story(save_id, "family_background_generator")
        if not generation_success:
            raise RuntimeError("生成家庭背景失败")
        
        # 重新加载存档以获取生成的内容
        updated_save = load_save("character", save_id)
        
        # 获取生成的家庭背景
        family_background = updated_save.get("family", {})
        
        # 删除临时存档
        delete_save("character", save_id)
        
        return family_background
    
    def run_background_creation_flow(self) -> Dict[str, Any]:
        """运行背景生成流程
        
        生成随机种子，并依次生成时代背景和家庭背景
        
        Returns:
            Dict[str, Any]: 生成结果，包含成功状态和背景信息
        """
        try:
            # 生成随机种子
            random_seed = random.randint(1, 10000)
            
            # 生成时代背景
            era_background = self.generate_era_background(random_seed)
            
            # 生成家庭背景
            family_background = self.generate_family_background(random_seed)
            
            # 创建背景存档
            save_id = f"background_{int(time.time())}"
            background_data = {
                "id": save_id,
                "era": era_background,
                "family": family_background,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
            
            # 保存背景存档
            save_data("character", save_id, background_data)
            
            return {
                "success": True,
                "save_id": save_id,
                "background": background_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 