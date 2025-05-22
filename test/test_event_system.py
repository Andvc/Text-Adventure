import sys
import os
import unittest
import json
from pathlib import Path

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gameflow.event_selector import EventSelector

class TestEventSystem(unittest.TestCase):
    """事件系统测试类"""
    
    def setUp(self):
        # 创建测试用的事件数据
        self.test_events = [
            {
                "event_id": "test_child_event",
                "name": "测试儿童事件",
                "description": "测试用儿童事件",
                "event_type": "测试",
                "tags": ["测试", "儿童"],
                "age_weights": [
                    {"min_age": 5, "max_age": 10, "weight": 1.0},
                    {"min_age": 11, "max_age": 15, "weight": 0.2},
                    {"min_age": 16, "max_age": 100, "weight": 0.0}
                ],
                "conditions": {
                    "required_attributes": {
                        "intelligence": {"min": 5}
                    },
                    "probability": 1.0
                },
                "options": [
                    {
                        "option_id": "test_option_1",
                        "text": "测试选项1",
                        "results": {
                            "attribute_changes": {
                                "intelligence": 2
                            },
                            "status_add": ["test_status"],
                            "story_text": "测试结果1"
                        }
                    }
                ]
            },
            {
                "event_id": "test_teen_event",
                "name": "测试青少年事件",
                "description": "测试用青少年事件",
                "event_type": "测试",
                "tags": ["测试", "青少年"],
                "age_weights": [
                    {"min_age": 5, "max_age": 10, "weight": 0.1},
                    {"min_age": 11, "max_age": 18, "weight": 1.0},
                    {"min_age": 19, "max_age": 100, "weight": 0.2}
                ],
                "conditions": {
                    "required_attributes": {
                        "strength": {"min": 10}
                    },
                    "probability": 0.8
                },
                "options": [
                    {
                        "option_id": "test_option_1",
                        "text": "测试选项1",
                        "results": {
                            "attribute_changes": {
                                "strength": 3
                            },
                            "status_add": ["teen_status"],
                            "story_text": "测试结果2"
                        }
                    }
                ]
            }
        ]
        
        # 创建事件选择器
        self.event_selector = EventSelector(self.test_events)
        
        # 创建测试用的角色状态
        self.child_character = {
            "age": 8,
            "intelligence": 10,
            "strength": 5,
            "status": [],
            "items": []
        }
        
        self.teen_character = {
            "age": 15,
            "intelligence": 10,
            "strength": 15,
            "status": [],
            "items": []
        }
    
    def test_filter_events_by_age(self):
        """测试按年龄筛选事件"""
        # 测试儿童年龄
        child_events = self.event_selector.filter_events_by_age(8)
        self.assertEqual(len(child_events), 2)
        self.assertEqual(child_events[0]["weight"], 1.0)  # 儿童事件权重高
        self.assertEqual(child_events[1]["weight"], 0.1)  # 青少年事件权重低
        
        # 测试青少年年龄
        teen_events = self.event_selector.filter_events_by_age(15)
        self.assertEqual(len(teen_events), 2)
        self.assertEqual(teen_events[0]["weight"], 0.2)  # 儿童事件权重低
        self.assertEqual(teen_events[1]["weight"], 1.0)  # 青少年事件权重高
        
        # 测试成人年龄
        adult_events = self.event_selector.filter_events_by_age(25)
        self.assertEqual(len(adult_events), 1)
        self.assertEqual(adult_events[0]["weight"], 0.2)  # 只有青少年事件权重不为0
    
    def test_check_event_conditions(self):
        """测试事件条件检查"""
        # 测试儿童事件条件
        child_event = self.test_events[0]
        self.assertTrue(self.event_selector.check_event_conditions(child_event, self.child_character))
        
        # 修改条件不满足的情况
        modified_character = self.child_character.copy()
        modified_character["intelligence"] = 3  # 低于要求的5
        self.assertFalse(self.event_selector.check_event_conditions(child_event, modified_character))
        
        # 测试青少年事件条件
        teen_event = self.test_events[1]
        self.assertFalse(self.event_selector.check_event_conditions(teen_event, self.child_character))  # 力量不足
        self.assertTrue(self.event_selector.check_event_conditions(teen_event, self.teen_character))
    
    def test_select_event(self):
        """测试事件选择"""
        # 儿童角色应该选择儿童事件（权重高且满足条件）
        selected_event = self.event_selector.select_event(self.child_character)
        self.assertEqual(selected_event["event_id"], "test_child_event")
        
        # 青少年角色应该选择青少年事件（权重高且满足条件）
        selected_event = self.event_selector.select_event(self.teen_character)
        self.assertEqual(selected_event["event_id"], "test_teen_event")
        
        # 不满足任何事件条件的情况
        invalid_character = {
            "age": 8,
            "intelligence": 3,  # 低于儿童事件要求
            "strength": 5       # 低于青少年事件要求
        }
        selected_event = self.event_selector.select_event(invalid_character)
        self.assertIsNone(selected_event)
    
    def test_process_event_option(self):
        """测试处理事件选项"""
        # 选择儿童事件的选项
        child_event = self.test_events[0]
        updated_character, result_text, follow_up = self.event_selector.process_event_option(
            child_event, "test_option_1", self.child_character
        )
        
        # 验证属性变化
        self.assertEqual(updated_character["intelligence"], 12)  # 10 + 2
        
        # 验证状态添加
        self.assertIn("test_status", updated_character["status"])
        
        # 验证结果文本
        self.assertEqual(result_text, "测试结果1")

    def test_json_file_loading(self):
        """测试从JSON文件加载事件"""
        # 创建临时JSON文件用于测试
        temp_file = Path("temp_test_events.json")
        test_data = {
            "example_events": self.test_events
        }
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 测试加载
        selector = EventSelector()
        selector.load_events_from_file(temp_file)
        
        self.assertEqual(len(selector.event_library), 2)
        self.assertEqual(selector.event_library[0]["event_id"], "test_child_event")
        
        # 清理
        if temp_file.exists():
            temp_file.unlink()

if __name__ == "__main__":
    unittest.main() 