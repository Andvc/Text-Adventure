#!/usr/bin/env python3
"""
角色创建流程管理模块

提供角色创建相关的功能，包括纪元选择、历史生成、种族和身份生成等
"""

import os
import json
import random
import time
import sys
from typing import Dict, List, Optional, Tuple, Union

# 确保可以导入上级目录的模块
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from data.data_manager import load_save, save_data, create_save, delete_save
from storyline.storyline_manager import StorylineManager

class CharacterCreationManager:
    """角色创建流程管理器
    
    负责管理角色创建的整个流程，包括纪元选择、历史生成等
    """
    
    def __init__(self):
        """初始化角色创建管理器"""
        self.storyline_manager = StorylineManager()
        self.selected_era = None
        self.era_history = None
        self.character_options = None
        self.current_save_id = None
        self.temp_save_id = f"temp_character_creation_{int(time.time())}"
    
    def select_random_era(self) -> Dict:
        """随机选择一个纪元
        
        根据权重随机选择一个纪元
        
        Returns:
            Dict: 选中的纪元数据
        """
        try:
            # 加载纪元数据
            era_data_path = os.path.join('data', 'text', 'eras.json')
            with open(era_data_path, 'r', encoding='utf-8') as f:
                era_data = json.load(f)
            
            # 获取权重
            weights = era_data.get('era_selection_weights', {})
            eras = era_data.get('eras', [])
            
            # 如果没有权重，使用均等权重
            if not weights:
                self.selected_era = random.choice(eras)
                return self.selected_era
            
            # 根据权重随机选择
            weighted_eras = []
            for era in eras:
                era_id = era.get('id')
                if era_id in weights:
                    weighted_eras.extend([era] * int(weights[era_id] * 10))
                else:
                    weighted_eras.append(era)
            
            self.selected_era = random.choice(weighted_eras)
            return self.selected_era
            
        except Exception as e:
            print(f"选择纪元时出错: {str(e)}")
            # 如果出错，返回第一个纪元作为默认值
            self.selected_era = {"id": "grand_empire_era", "name": "万象帝国", "era_number": 5}
            return self.selected_era
    
    def show_era_info(self) -> str:
        """显示纪元信息
        
        格式化显示选中纪元的基本信息
        
        Returns:
            str: 格式化的纪元信息文本
        """
        if not self.selected_era:
            return "未选择纪元"
        
        info = [
            f"==== 纪元信息 ====",
            f"名称: {self.selected_era.get('name')}",
            f"编号: 第{self.selected_era.get('era_number')}纪元",
            f"\n主要特征:"
        ]
        
        # 添加关键特征
        for feature in self.selected_era.get('key_features', []):
            info.append(f"  • {feature}")
        
        # 添加主导种族
        races = self.selected_era.get('dominant_races', [])
        if races:
            info.append(f"\n主导种族: {', '.join(races)}")
        
        # 添加魔法系统
        magic = self.selected_era.get('magic_system')
        if magic:
            info.append(f"魔法体系: {magic}")
        
        # 添加技术水平
        tech = self.selected_era.get('technology_level')
        if tech:
            info.append(f"技术水平: {tech}")
        
        # 添加毁灭原因
        destruction = self.selected_era.get('destruction_cause')
        if destruction:
            info.append(f"\n毁灭原因: {destruction}")
        
        # 添加背景简介
        background = self.selected_era.get('era_background')
        if background:
            info.append(f"\n背景简介:\n{background}")
            
        return "\n".join(info)
    
    def generate_era_history(self) -> str:
        """生成纪元详细历史
        
        使用storyline模板生成更详细的纪元历史
        
        Returns:
            str: 生成的历史文本
        """
        if not self.selected_era:
            return "未选择纪元，无法生成历史"
        
        try:
            # 准备临时存档数据，用于生成历史
            temp_save_data = {
                "id": self.temp_save_id,
                "era": {
                    "id": self.selected_era.get('id'),
                    "name": self.selected_era.get('name'),
                    "era_number": self.selected_era.get('era_number'),
                    "key_features_joined": ", ".join(self.selected_era.get('key_features', [])),
                    "dominant_races_joined": ", ".join(self.selected_era.get('dominant_races', [])),
                    "magic_system": self.selected_era.get('magic_system'),
                    "technology_level": self.selected_era.get('technology_level'),
                    "destruction_cause": self.selected_era.get('destruction_cause'),
                    "era_background": self.selected_era.get('era_background')
                }
            }
            
            # 创建或更新临时存档
            create_save("character", self.temp_save_id, temp_save_data)
            
            # 使用模板生成历史
            success = self.storyline_manager.generate_story(self.temp_save_id, "era_history")
            
            if success:
                # 加载生成的历史
                updated_save = load_save("character", self.temp_save_id)
                
                # 调试输出
                print("\n=== 调试信息: 加载的存档内容 ===")
                print(f"存档ID: {updated_save.get('id', 'unknown')}")
                print(f"存档键: {', '.join(updated_save.keys())}")
                if "era_history" in updated_save:
                    print(f"era_history类型: {type(updated_save['era_history'])}")
                    print(f"era_history前100字符: {updated_save['era_history'][:100]}...")
                else:
                    print("存档中不存在era_history键!")
                    print(f"可能的相关键: {[k for k in updated_save.keys() if 'history' in k.lower()]}")
                print("===============================\n")
                
                if updated_save and "era_history" in updated_save:
                    self.era_history = updated_save["era_history"]
                    return self.era_history
            
            # 如果生成失败，返回错误信息
            self.era_history = "历史生成失败，请重试"
            return self.era_history
                
        except Exception as e:
            print(f"生成纪元历史时出错: {str(e)}")
            self.era_history = f"生成历史时遇到错误: {str(e)}"
            return self.era_history
    
    def generate_character_options(self) -> Dict:
        """生成角色选项
        
        使用storyline模板生成可选的种族和职业
        
        Returns:
            Dict: 生成的角色选项，包含种族和职业
        """
        if not self.selected_era:
            return {"error": "未选择纪元"}
        
        try:
            # 准备临时存档数据，用于生成角色选项
            temp_save_data = {
                "id": self.temp_save_id,
                "era": {
                    "id": self.selected_era.get('id'),
                    "name": self.selected_era.get('name'),
                    "era_number": self.selected_era.get('era_number'),
                    "key_features_joined": ", ".join(self.selected_era.get('key_features', [])),
                    "dominant_races_joined": ", ".join(self.selected_era.get('dominant_races', [])),
                    "magic_system": self.selected_era.get('magic_system'),
                    "technology_level": self.selected_era.get('technology_level'),
                    "destruction_cause": self.selected_era.get('destruction_cause')
                },
                "era_history": self.era_history if self.era_history else self.selected_era.get('era_background')
            }
            
            # 创建或更新临时存档
            create_save("character", self.temp_save_id, temp_save_data)
            
            # 使用模板生成角色选项
            success = self.storyline_manager.generate_story(self.temp_save_id, "character_options")
            
            if success:
                # 加载生成的角色选项
                updated_save = load_save("character", self.temp_save_id)
                
                # 调试输出
                print("\n=== 调试信息: 加载的角色选项 ===")
                print(f"存档ID: {updated_save.get('id', 'unknown')}")
                print(f"存档键: {', '.join(updated_save.keys())}")
                
                if "race_options" in updated_save:
                    print(f"race_options类型: {type(updated_save['race_options'])}")
                    if isinstance(updated_save['race_options'], list):
                        print(f"race_options长度: {len(updated_save['race_options'])}")
                        if updated_save['race_options']:
                            print(f"第一个种族的键: {', '.join(updated_save['race_options'][0].keys())}")
                    else:
                        print(f"警告: race_options不是预期的列表类型")
                else:
                    print("存档中不存在race_options键!")
                    print(f"可能的相关键: {[k for k in updated_save.keys() if 'race' in k.lower()]}")
                
                if "career_options" in updated_save:
                    print(f"career_options类型: {type(updated_save['career_options'])}")
                    if isinstance(updated_save['career_options'], list):
                        print(f"career_options长度: {len(updated_save['career_options'])}")
                        if updated_save['career_options']:
                            print(f"第一个职业的键: {', '.join(updated_save['career_options'][0].keys())}")
                    else:
                        print(f"警告: career_options不是预期的列表类型")
                else:
                    print("存档中不存在career_options键!")
                    print(f"可能的相关键: {[k for k in updated_save.keys() if 'career' in k.lower() or 'option' in k.lower()]}")
                print("===============================\n")
                
                if updated_save and "race_options" in updated_save and "career_options" in updated_save:
                    self.character_options = {
                        'race_options': updated_save["race_options"],
                        'career_options': updated_save["career_options"]
                    }
                    return self.character_options
            
            # 如果生成失败，返回错误信息
            return {"error": "生成角色选项失败"}
                
        except Exception as e:
            print(f"生成角色选项时出错: {str(e)}")
            return {"error": f"生成角色选项时出错: {str(e)}"}
    
    def save_character_data(self, character_name: str, selected_race: Dict, selected_career: Dict) -> bool:
        """保存角色数据
        
        将选择的纪元、种族和职业数据保存到存档
        
        Args:
            character_name (str): 角色名称
            selected_race (Dict): 选中的种族
            selected_career (Dict): 选中的职业
            
        Returns:
            bool: 是否成功保存
        """
        try:
            # 创建角色数据
            save_id = f"{character_name.lower().replace(' ', '_')}_{int(time.time())}"
            
            character_data = {
                "id": save_id,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "name": character_name,
                "era": {
                    "id": self.selected_era.get('id'),
                    "name": self.selected_era.get('name'),
                    "era_number": self.selected_era.get('era_number'),
                    "history": self.era_history if self.era_history else self.selected_era.get('era_background')
                },
                "race": selected_race,
                "career": selected_career,
                "stats": {
                    "level": 1,
                    "experience": 0,
                    "health": 100,
                    "energy": 100,
                    "magic": 50
                },
                "inventory": [],
                "journal": [{
                    "entry_id": 1,
                    "title": "开始旅程",
                    "content": f"我的名字是{character_name}，{selected_career.get('description', '').split('.')[0]}",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                }],
                "quests": [],
                "relationships": [],
                "known_locations": [],
                "story_state": {
                    "current_chapter": 1,
                    "chapter_title": "命运的召唤",
                    "plot_points": [],
                    "decisions": []
                }
            }
            
            # 保存数据
            self.current_save_id = save_id
            create_save("character", save_id, character_data)
            
            # 删除临时存档
            try:
                if self.temp_save_id:
                    print(f"清理临时存档 {self.temp_save_id}...")
                    delete_save("character", self.temp_save_id)
            except Exception as e:
                print(f"清理临时存档失败，但不影响角色创建: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"保存角色数据时出错: {str(e)}")
            return False
    
    def run_character_creation_flow(self) -> Dict:
        """运行完整的角色创建流程
        
        引导用户完成整个角色创建过程
        
        Returns:
            Dict: 创建结果信息
        """
        try:
            print("=== 开始角色创建 ===")
            
            # 步骤1: 随机选择纪元
            era_accepted = False
            while not era_accepted:
                self.select_random_era()
                print(self.show_era_info())
                
                choice = input("\n是否接受这个纪元？(y/n): ").strip().lower()
                if choice == 'y':
                    era_accepted = True
            
            # 步骤2: 生成纪元历史
            print("\n=== 生成纪元历史 ===")
            print("正在生成纪元的详细历史...")
            history = self.generate_era_history()
            print(f"\n{history}")
            
            # 步骤3: 生成角色选项
            print("\n=== 生成角色选项 ===")
            print("正在生成角色选项...")
            options = self.generate_character_options()
            
            if "error" in options:
                print(f"错误: {options['error']}")
                # 清理临时存档
                self._cleanup_temp_save()
                return {"success": False, "error": options['error']}
            
            # 显示种族选项
            print("\n可选种族:")
            race_options = options.get('race_options', [])
            
            for i, race in enumerate(race_options, 1):
                print(f"{i}. {race.get('sub_race')} (主种族: {race.get('main_race')})")
                print(f"   描述: {race.get('description')}")
            
            # 获取种族选择
            race_choice = int(input("\n请选择种族 (1-3): "))
            selected_race = race_options[race_choice - 1]
            
            # 显示职业选项
            print("\n可选职业:")
            career_options = options.get('career_options', [])
            
            for i, career in enumerate(career_options, 1):
                print(f"{i}. {career.get('name')}")
                print(f"   描述: {career.get('description')}")
                print(f"   成长路径: {career.get('growth_path')}")
                print(f"   特殊能力: {career.get('special_abilities')}")
            
            # 获取职业选择
            career_choice = int(input("\n请选择职业 (1-3): "))
            selected_career = career_options[career_choice - 1]
            
            # 获取角色名称
            character_name = input("\n请输入角色名称: ")
            
            # 保存角色数据
            print("\n正在保存角色数据...")
            save_result = self.save_character_data(character_name, selected_race, selected_career)
            
            if save_result:
                print(f"\n角色 {character_name} 创建成功!")
                return {
                    "success": True, 
                    "save_id": self.current_save_id,
                    "character_name": character_name,
                    "era": self.selected_era.get('name'),
                    "race": selected_race.get('sub_race'),
                    "career": selected_career.get('name')
                }
            else:
                print("\n角色创建失败，请重试")
                # 确保清理临时存档
                self._cleanup_temp_save()
                return {"success": False, "error": "保存失败"}
                
        except Exception as e:
            print(f"角色创建过程出错: {str(e)}")
            # 在异常情况下也清理临时存档
            self._cleanup_temp_save()
            return {"success": False, "error": str(e)}
    
    def _cleanup_temp_save(self) -> None:
        """清理临时存档文件"""
        try:
            if self.temp_save_id:
                print(f"清理临时存档 {self.temp_save_id}...")
                delete_save("character", self.temp_save_id)
        except Exception as e:
            print(f"清理临时存档失败: {str(e)}") 