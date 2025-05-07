#!/usr/bin/env python3
"""
角色创建流程测试

测试角色创建流程的各个功能点
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gameflow.character_creation import CharacterCreationManager

class TestCharacterCreation(unittest.TestCase):
    """角色创建功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = CharacterCreationManager()
        # 模拟StorylineManager
        self.manager.storyline_manager = MagicMock()
        self.manager.storyline_manager.generate_story.return_value = True
    
    def test_select_random_era(self):
        """测试随机选择纪元功能"""
        # 模拟一个测试纪元数据
        test_era = {
            "id": "test_era",
            "name": "测试纪元",
            "era_number": 1,
            "key_features": ["测试特征1", "测试特征2"],
            "dominant_races": ["测试种族1", "测试种族2"],
            "magic_system": "测试魔法体系",
            "technology_level": "测试科技水平",
            "destruction_cause": "测试毁灭原因",
            "era_background": "测试背景"
        }
        
        # 使用patch模拟random.choice总是返回测试纪元
        with patch('random.choice', return_value=test_era):
            result = self.manager.select_random_era()
            
            # 验证结果
            self.assertEqual(result["id"], "test_era")
            self.assertEqual(result["name"], "测试纪元")
            self.assertEqual(self.manager.selected_era, test_era)
    
    def test_show_era_info(self):
        """测试显示纪元信息功能"""
        # 设置测试纪元
        self.manager.selected_era = {
            "id": "test_era",
            "name": "测试纪元",
            "era_number": 1,
            "key_features": ["测试特征1", "测试特征2"],
            "dominant_races": ["测试种族1", "测试种族2"],
            "magic_system": "测试魔法体系",
            "technology_level": "测试科技水平",
            "destruction_cause": "测试毁灭原因",
            "era_background": "测试背景"
        }
        
        # 获取显示信息
        info = self.manager.show_era_info()
        
        # 验证信息包含关键内容
        self.assertIn("测试纪元", info)
        self.assertIn("第1纪元", info)
        self.assertIn("测试特征1", info)
        self.assertIn("测试特征2", info)
        self.assertIn("测试种族1, 测试种族2", info)
        self.assertIn("测试魔法体系", info)
        self.assertIn("测试科技水平", info)
        self.assertIn("测试毁灭原因", info)
        self.assertIn("测试背景", info)
    
    def test_generate_era_history(self):
        """测试生成纪元历史功能"""
        # 设置测试纪元
        self.manager.selected_era = {
            "id": "test_era",
            "name": "测试纪元",
            "era_number": 1,
            "key_features": ["测试特征1", "测试特征2"],
            "dominant_races": ["测试种族1", "测试种族2"],
            "magic_system": "测试魔法体系",
            "technology_level": "测试科技水平",
            "destruction_cause": "测试毁灭原因",
            "era_background": "测试背景"
        }
        
        # 模拟StorylineManager生成结果
        self.manager.storyline_manager.generate_story.return_value = True
        
        # 模拟load_save返回结果
        mock_save_data = {
            "id": self.manager.temp_save_id,
            "era_history": "测试的纪元历史详情"
        }
        with patch('gameflow.character_creation.load_save', return_value=mock_save_data):
            history = self.manager.generate_era_history()
            
            # 验证结果
            self.assertEqual(history, "测试的纪元历史详情")
            self.assertEqual(self.manager.era_history, "测试的纪元历史详情")
            
            # 验证StorylineManager调用
            self.manager.storyline_manager.generate_story.assert_called_once()
    
    def test_generate_character_options(self):
        """测试生成角色选项功能"""
        # 设置测试纪元
        self.manager.selected_era = {
            "id": "test_era",
            "name": "测试纪元",
            "era_number": 1,
            "key_features": ["测试特征1", "测试特征2"],
            "dominant_races": ["测试种族1", "测试种族2"],
            "magic_system": "测试魔法体系",
            "technology_level": "测试科技水平",
            "destruction_cause": "测试毁灭原因",
            "era_background": "测试背景"
        }
        
        # 设置历史
        self.manager.era_history = "测试的纪元历史"
        
        # 模拟StorylineManager生成结果
        self.manager.storyline_manager.generate_story.return_value = True
        
        # 模拟load_save返回结果
        mock_save_data = {
            "id": self.manager.temp_save_id,
            "race_options": [
                {
                    "name": "测试种族1",
                    "description": "测试种族1描述",
                    "magic_affinity": "测试种族1魔法倾向"
                },
                {
                    "name": "测试种族2",
                    "description": "测试种族2描述",
                    "magic_affinity": "测试种族2魔法倾向"
                }
            ],
            "identity_options": {
                "测试种族1": [
                    {
                        "name": "测试身份1",
                        "status": "测试身份1地位",
                        "background": "测试身份1背景"
                    },
                    {
                        "name": "测试身份2",
                        "status": "测试身份2地位",
                        "background": "测试身份2背景"
                    }
                ],
                "测试种族2": [
                    {
                        "name": "测试身份3",
                        "status": "测试身份3地位",
                        "background": "测试身份3背景"
                    },
                    {
                        "name": "测试身份4",
                        "status": "测试身份4地位",
                        "background": "测试身份4背景"
                    }
                ]
            }
        }
        with patch('gameflow.character_creation.load_save', return_value=mock_save_data):
            options = self.manager.generate_character_options()
            
            # 验证结果
            self.assertIn('race_options', options)
            self.assertIn('identity_options', options)
            self.assertEqual(len(options['race_options']), 2)
            self.assertEqual(options['race_options'][0]['name'], "测试种族1")
            self.assertEqual(options['identity_options']['测试种族1'][0]['name'], "测试身份1")
            
            # 验证StorylineManager调用
            self.manager.storyline_manager.generate_story.assert_called_once()
    
    def test_save_character_data(self):
        """测试保存角色数据功能"""
        # 设置测试纪元
        self.manager.selected_era = {
            "id": "test_era",
            "name": "测试纪元",
            "era_number": 1,
            "key_features": ["测试特征1", "测试特征2"],
            "dominant_races": ["测试种族1", "测试种族2"],
            "magic_system": "测试魔法体系",
            "technology_level": "测试科技水平",
            "destruction_cause": "测试毁灭原因",
            "era_background": "测试背景"
        }
        
        # 设置历史
        self.manager.era_history = "测试的纪元历史"
        
        # 测试数据
        character_name = "测试角色"
        selected_race = {
            "name": "测试种族",
            "description": "测试种族描述",
            "magic_affinity": "测试种族魔法倾向"
        }
        selected_identity = {
            "name": "测试身份",
            "status": "测试身份地位",
            "background": "测试身份背景"
        }
        
        # 模拟create_save函数
        with patch('gameflow.character_creation.create_save', return_value=True) as mock_create_save:
            result = self.manager.save_character_data(character_name, selected_race, selected_identity)
            
            # 验证结果
            self.assertTrue(result)
            self.assertIsNotNone(self.manager.current_save_id)
            
            # 验证create_save调用
            mock_create_save.assert_called_once()
            # 验证第一个参数是character
            self.assertEqual(mock_create_save.call_args[0][0], "character")

if __name__ == "__main__":
    unittest.main() 