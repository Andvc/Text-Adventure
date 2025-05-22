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
    
    # 定义支持的类型
    SUPPORTED_TYPES = [
        "ability",      # 能力
        "item",         # 物品
        "magic",        # 魔法
        "artifact",     # 法器
        "elixir",       # 丹药
        "technique",    # 功法
        "cultivation_role"  # 修炼角色
    ]
    
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
    
    def _get_level_data(self, level: int) -> Dict[str, Any]:
        """获取等级数据（内部方法）
        
        Args:
            level: 能力等级（0-7）
            
        Returns:
            Dict[str, Any]: 等级数据
        """
        if level < 0 or level > 7:
            raise ValueError("能力等级必须在0-7之间")
        
        if not self.power_levels_data:
            self._load_power_levels()
            if not self.power_levels_data:
                raise RuntimeError("无法加载能力等级数据")
        
        return self.power_levels_data["levels"][level]
    
    def _get_type_examples(self, level: int, item_type: str) -> List[str]:
        """获取指定类型和等级的示例（内部方法）
        
        Args:
            level: 能力等级（1-7）
            item_type: 物品类型
            
        Returns:
            List[str]: 示例列表
        """
        level_data = self._get_level_data(level)
        return level_data["examples"].get(item_type, [])
    
    def _get_type_style_note(self, level: int) -> str:
        """获取指定等级的命名风格说明（内部方法）
        
        Args:
            level: 能力等级（1-7）
            
        Returns:
            str: 命名风格说明
        """
        level_data = self._get_level_data(level)
        return level_data.get("style_note", "")
    
    def _generate_base(self, save_id: str, item_type: str, level: int, detail: str = "") -> Dict[str, Any]:
        """基础生成方法（内部方法）
        
        Args:
            save_id: 存档ID
            item_type: 物品类型
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict[str, Any]: 生成的结果
        """
        # 验证参数
        if item_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"不支持的类型: {item_type}")
        
        if level < 1 or level > 7:
            raise ValueError("能力等级必须在1-7之间")
        
        # 加载存档
        save_data_content = load_save("character", save_id)
        if not save_data_content:
            raise ValueError(f"无法加载存档: {save_id}")
        
        # 添加临时参数
        save_data_content["temp_level"] = level
        save_data_content["temp_level_index"] = level - 1
        save_data_content["temp_type"] = item_type
        save_data_content["temp_detail"] = detail
        
        # 创建物品ID
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
        for key in ["temp_level", "temp_level_index", "temp_type", "temp_detail", "temp_item_id", item_type]:
            if key in updated_save:
                del updated_save[key]
        
        # 保存清理后的存档
        save_data("character", save_id, updated_save)
        
        # 返回生成的物品结果
        return generated_item
    
    def generate_ability(self, save_id: str, level: int, detail: str = "") -> Dict[str, Any]:
        """生成能力
        
        Args:
            save_id: 存档ID
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict[str, Any]: 生成的能力
        """
        return self._generate_base(save_id, "ability", level, detail)
    
    def generate_item(self, save_id: str, level: int, detail: str = "") -> Dict[str, Any]:
        """生成物品
        
        Args:
            save_id: 存档ID
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict[str, Any]: 生成的物品
        """
        return self._generate_base(save_id, "item", level, detail)
    
    def generate_magic(self, save_id: str, level: int, detail: str = "") -> Dict[str, Any]:
        """生成魔法
        
        Args:
            save_id: 存档ID
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict[str, Any]: 生成的魔法
        """
        return self._generate_base(save_id, "magic", level, detail)
    
    def generate_artifact(self, save_id: str, level: int, detail: str = "") -> Dict[str, Any]:
        """生成法器
        
        Args:
            save_id: 存档ID
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict[str, Any]: 生成的法器
        """
        return self._generate_base(save_id, "artifact", level, detail)
    
    def generate_elixir(self, save_id: str, level: int, detail: str = "") -> Dict[str, Any]:
        """生成丹药
        
        Args:
            save_id: 存档ID
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict[str, Any]: 生成的丹药
        """
        return self._generate_base(save_id, "elixir", level, detail)
    
    def generate_technique(self, save_id: str, level: int, detail: str = "") -> Dict[str, Any]:
        """生成功法
        
        Args:
            save_id: 存档ID
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict[str, Any]: 生成的功法
        """
        return self._generate_base(save_id, "technique", level, detail)
    
    def generate_cultivation_role(self, save_id: str, level: int, detail: str = "") -> Dict[str, Any]:
        """生成修炼角色
        
        Args:
            save_id: 存档ID
            level: 能力等级（1-7）
            detail: 可选的详细描述
            
        Returns:
            Dict[str, Any]: 生成的修炼角色
        """
        return self._generate_base(save_id, "cultivation_role", level, detail)
    
    def explain_power_level(self, level: int) -> str:
        """解释能力等级
        
        Args:
            level: 能力等级（1-7）
            
        Returns:
            str: 格式化的等级解释
        """
        try:
            level_data = self._get_level_data(level)
            
            explanation = [
                f"等级 {level} - {level_data['name']}",
                f"\n描述: {level_data['description']}",
                f"\n能力范围: {level_data['power_range']}",
                f"\n命名风格: {level_data['style_note']}",
                f"\n示例:"
            ]
            
            # 添加所有类型的示例
            for type_name in self.SUPPORTED_TYPES:
                examples = level_data["examples"].get(type_name, [])
                if examples:
                    explanation.append(f"\n  {type_name}: {', '.join(examples)}")
            
            return "\n".join(explanation)
        except Exception as e:
            return f"无法获取等级{level}的信息: {str(e)}" 