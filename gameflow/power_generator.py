#!/usr/bin/env python3
"""
能力生成器模块

提供生成武器、职业等能力和物品的功能
"""

import os
import sys
import time
import json
from typing import Dict, Any, List, Optional, Tuple, Union

# 确保可以导入上级目录的模块
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from data.data_manager import load_save, save_data
from storyline.storyline_manager import StorylineManager

class PowerGenerator:
    """能力生成器
    
    负责生成武器、职业等能力和物品
    """
    
    def __init__(self):
        """初始化能力生成器"""
        self.storyline_manager = StorylineManager()
        # 预加载能力等级数据
        self._load_power_levels()
    
    def _load_power_levels(self):
        """加载能力等级数据"""
        try:
            # 从data/text目录加载power_levels.json
            power_levels_path = os.path.join(current_dir, "data", "text", "power_levels.json")
            with open(power_levels_path, "r", encoding="utf-8") as f:
                self.power_levels_data = json.load(f)
        except Exception as e:
            print(f"加载能力等级数据失败: {str(e)}")
            self.power_levels_data = None
    
    def generate_power_item(self, save_id: str, item_type: str, level: int, detail: str = "") -> Dict[str, Any]:
        """生成能力或物品
        
        Args:
            save_id: 存档ID
            item_type: 物品类型，如'weapon'或'career'
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict[str, Any]: 生成的结果，包含物品详情
        """
        # 验证参数
        if level < 1 or level > 7:
            raise ValueError("能力等级必须在1-7之间")
        
        # 加载存档
        save_data_content = load_save("character", save_id)
        if not save_data_content:
            raise ValueError(f"无法加载存档: {save_id}")
        
        # 添加临时参数
        save_data_content["temp_level"] = level
        save_data_content["temp_level_index"] = level - 1  # 添加预计算的索引
        save_data_content["temp_type"] = item_type
        save_data_content["temp_detail"] = detail
        
        # 创建物品ID（使用当前时间戳和随机数作为唯一标识）
        import uuid
        item_id = f"{item_type}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        save_data_content["temp_item_id"] = item_id
        
        # 保存更新后的存档
        success = save_data("character", save_id, save_data_content)
        if not success:
            raise RuntimeError(f"更新存档失败: {save_id}")
        
        # 使用模板生成内容
        generation_success = self.storyline_manager.generate_story(save_id, "power_item_generator")
        if not generation_success:
            raise RuntimeError("生成能力或物品失败")
        
        # 重新加载存档以获取生成的内容
        updated_save = load_save("character", save_id)
        
        # 获取生成的物品
        generated_item = {}
        if item_type in updated_save:
            generated_item = updated_save[item_type]
        else:
            raise RuntimeError(f"生成成功但无法找到类型: {item_type}")
        
        # 将生成的物品转换为数组项
        generated_item["id"] = item_id
        generated_item["level"] = level
        generated_item["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # 在存档中创建或更新物品数组
        items_array_key = f"{item_type}s"  # 例如：weapons, careers
        if items_array_key not in updated_save:
            updated_save[items_array_key] = []
        
        # 将新物品添加到数组
        updated_save[items_array_key].append(generated_item)
        
        # 删除临时参数和单个物品存储
        if "temp_level" in updated_save:
            del updated_save["temp_level"]
        if "temp_level_index" in updated_save:
            del updated_save["temp_level_index"]
        if "temp_type" in updated_save:
            del updated_save["temp_type"]
        if "temp_detail" in updated_save:
            del updated_save["temp_detail"]
        if "temp_item_id" in updated_save:
            del updated_save["temp_item_id"]
        if item_type in updated_save:
            del updated_save[item_type]
        
        # 保存清理后的存档
        save_data("character", save_id, updated_save)
        
        # 返回生成的物品结果
        return generated_item
    
    def _get_level_description(self, level: int) -> Dict[str, Any]:
        """获取等级的通用描述（内部方法）
        
        Args:
            level: 能力等级（1-7）
            
        Returns:
            Dict[str, Any]: 等级描述信息
        """
        # 验证参数
        if level < 1 or level > 7:
            raise ValueError("能力等级必须在1-7之间")
        
        # 确保能力等级数据已加载
        if not self.power_levels_data:
            self._load_power_levels()
            if not self.power_levels_data:
                raise RuntimeError("无法加载能力等级数据")
        
        # 直接从加载的数据中获取
        level_index = level - 1  # 转换为0-based索引
        
        # 获取等级数据
        try:
            level_data = self.power_levels_data["levels"][level_index]
            
            return {
                "level": level,
                "name": level_data.get("name", f"等级{level}"),
                "description": level_data.get("universal_description", ""),
                "power_range": level_data.get("power_range", ""),
                "examples": level_data.get("examples", {})
            }
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"获取等级{level}数据失败: {str(e)}")
    
    def explain_power_level(self, level: int) -> str:
        """解释能力等级
        
        Args:
            level: 能力等级（1-7）
            
        Returns:
            str: 格式化的等级解释
        """
        try:
            level_info = self._get_level_description(level)
            
            explanation = [
                f"等级 {level} - {level_info['name']}",
                f"\n描述: {level_info['description']}",
                f"\n能力范围: {level_info['power_range']}",
                f"\n示例:",
                f"  能力: {level_info['examples'].get('ability', '无')}",
                f"  物品: {level_info['examples'].get('item', '无')}",
                f"  魔法: {level_info['examples'].get('magic', '无')}"
            ]
            
            return "\n".join(explanation)
        except Exception as e:
            return f"无法获取等级{level}的信息: {str(e)}" 