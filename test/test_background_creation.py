#!/usr/bin/env python3
"""
背景生成管理器测试模块

验证背景生成管理器的各项功能是否正常工作
"""

import unittest
from gameflow.background_creation import BackgroundCreationManager

class TestBackgroundCreation(unittest.TestCase):
    """背景生成管理器测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.background_manager = BackgroundCreationManager()
    
    def test_generate_era_background(self):
        """测试时代背景生成功能"""
        # 使用固定的随机种子以确保测试结果可重现
        random_seed = 42
        era_background = self.background_manager.generate_era_background(random_seed)
        
        # 验证返回值的结构
        self.assertIsNotNone(era_background)
        self.assertIsInstance(era_background, dict)
        
        # 验证必要的字段是否存在
        self.assertIn('name', era_background)
        self.assertIn('feature', era_background)
        self.assertIn('event', era_background)
        
        # 验证字段值的类型
        self.assertIsInstance(era_background['name'], str)
        self.assertIsInstance(era_background['feature'], str)
        self.assertIsInstance(era_background['event'], str)
    
    def test_generate_family_background(self):
        """测试家庭背景生成功能"""
        # 使用固定的随机种子以确保测试结果可重现
        random_seed = 42
        family_background = self.background_manager.generate_family_background(random_seed)
        
        # 验证返回值的结构
        self.assertIsNotNone(family_background)
        self.assertIsInstance(family_background, dict)
        
        # 验证必要的字段是否存在
        self.assertIn('parent_job', family_background)
        self.assertIn('family_status', family_background)
        self.assertIn('wealth', family_background)
        self.assertIn('history', family_background)
        
        # 验证字段值的类型
        self.assertIsInstance(family_background['parent_job'], str)
        self.assertIsInstance(family_background['family_status'], str)
        self.assertIsInstance(family_background['wealth'], str)
        self.assertIsInstance(family_background['history'], str)
    
    def test_run_background_creation_flow(self):
        """测试完整的背景生成流程"""
        result = self.background_manager.run_background_creation_flow()
        
        # 验证返回值的结构
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        
        # 验证成功状态
        self.assertTrue(result['success'])
        
        # 验证必要的字段是否存在
        self.assertIn('save_id', result)
        self.assertIn('background', result)
        
        # 验证背景数据的结构
        background = result['background']
        self.assertIn('era', background)
        self.assertIn('family', background)
        self.assertIn('created_at', background)
        
        # 验证时间戳格式
        self.assertRegex(background['created_at'], r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

if __name__ == '__main__':
    unittest.main() 