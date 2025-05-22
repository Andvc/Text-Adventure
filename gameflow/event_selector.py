import random
import json
import os
from pathlib import Path

class EventSelector:
    """
    事件选择器类，负责根据角色状态选择合适的事件
    """
    
    def __init__(self, event_library=None):
        """
        初始化事件选择器
        
        Args:
            event_library: 事件库，可以是事件列表或JSON文件路径
        """
        self.event_library = []
        
        if event_library:
            if isinstance(event_library, list):
                self.event_library = event_library
            elif isinstance(event_library, (str, Path)) and os.path.exists(event_library):
                with open(event_library, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.event_library = data.get("example_events", [])
    
    def load_events_from_file(self, file_path):
        """
        从JSON文件加载事件库
        
        Args:
            file_path: 事件库JSON文件路径
        """
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.event_library = data.get("example_events", [])
    
    def add_event(self, event):
        """
        添加单个事件到事件库
        
        Args:
            event: 事件字典
        """
        self.event_library.append(event)
    
    def filter_events_by_age(self, age):
        """
        筛选符合年龄段的事件并计算权重
        
        Args:
            age: 角色年龄
            
        Returns:
            list: 符合年龄的事件列表，每项包含事件和权重
        """
        valid_events = []
        
        for event in self.event_library:
            for age_range in event.get("age_weights", []):
                if age_range["min_age"] <= age <= age_range["max_age"]:
                    if age_range["weight"] > 0:
                        # 添加事件及其对应权重
                        valid_events.append({
                            "event": event,
                            "weight": age_range["weight"]
                        })
                    break
        
        return valid_events
    
    def check_attribute_condition(self, required, character_value):
        """
        检查属性条件是否满足
        
        Args:
            required: 属性要求字典，包含min和max
            character_value: 角色属性值
            
        Returns:
            bool: 是否满足条件
        """
        if "min" in required and character_value < required["min"]:
            return False
        if "max" in required and character_value > required["max"]:
            return False
        return True
    
    def check_event_conditions(self, event, character):
        """
        检查事件条件是否满足
        
        Args:
            event: 事件字典
            character: 角色状态字典
            
        Returns:
            bool: 是否满足所有条件
        """
        conditions = event.get("conditions", {})
        
        # 检查属性要求
        for attr_name, attr_range in conditions.get("required_attributes", {}).items():
            char_value = character.get(attr_name, 0)
            if not self.check_attribute_condition(attr_range, char_value):
                return False
        
        # 检查状态要求
        char_status = character.get("status", [])
        for required in conditions.get("required_status", []):
            if required not in char_status:
                return False
        
        # 检查禁止状态
        for forbidden in conditions.get("forbidden_status", []):
            if forbidden in char_status:
                return False
        
        # 检查物品要求
        char_items = character.get("items", [])
        for required_item in conditions.get("required_items", []):
            if required_item not in char_items:
                return False
        
        # 检查关系要求
        char_relationships = character.get("relationships", {})
        for rel_name, rel_range in conditions.get("required_relationships", {}).items():
            rel_value = char_relationships.get(rel_name, 0)
            if not self.check_attribute_condition(rel_range, rel_value):
                return False
        
        # 检查地点要求
        if "location_requirements" in conditions:
            if character.get("location") not in conditions["location_requirements"]:
                return False
        
        return True
    
    def select_event(self, character):
        """
        根据角色状态选择合适的事件
        
        Args:
            character: 角色状态字典
            
        Returns:
            dict: 选中的事件，如果没有则返回None
        """
        age = character.get("age", 0)
        
        # 筛选符合年龄的事件
        age_filtered_events = self.filter_events_by_age(age)
        
        valid_events = []
        for event_data in age_filtered_events:
            event = event_data["event"]
            base_weight = event_data["weight"]
            
            # 检查事件条件
            if self.check_event_conditions(event, character):
                # 计算最终权重 = 年龄权重 * 基础概率
                final_weight = base_weight * event.get("conditions", {}).get("probability", 1.0)
                valid_events.append({
                    "event": event,
                    "weight": final_weight
                })
        
        # 没有符合条件的事件
        if not valid_events:
            return None
        
        # 按权重随机选择
        weights = [e["weight"] for e in valid_events]
        total = sum(weights)
        
        if total <= 0:
            return None
            
        rand_val = random.uniform(0, total)
        current = 0
        
        for i, event_data in enumerate(valid_events):
            current += event_data["weight"]
            if rand_val <= current:
                return valid_events[i]["event"]
        
        return valid_events[-1]["event"]  # 保险起见
    
    def process_event_option(self, event, option_id, character):
        """
        处理事件选项结果
        
        Args:
            event: 事件字典
            option_id: 选项ID
            character: 角色状态字典
            
        Returns:
            tuple: (更新后的角色状态, 结果文本, 后续事件列表)
        """
        # 复制角色状态，避免直接修改
        updated_character = character.copy()
        result_text = ""
        
        # 查找对应选项
        selected_option = None
        for option in event.get("options", []):
            if option.get("option_id") == option_id:
                selected_option = option
                break
        
        # 如果找不到选项，使用默认结果
        if not selected_option:
            results = event.get("default_result", {})
            result_text = results.get("story_text", "")
        else:
            results = selected_option.get("results", {})
            result_text = results.get("story_text", "")
        
        # 应用属性变化
        for attr, change in results.get("attribute_changes", {}).items():
            updated_character[attr] = updated_character.get(attr, 0) + change
        
        # 添加状态
        char_status = updated_character.get("status", [])
        for status in results.get("status_add", []):
            if status not in char_status:
                char_status.append(status)
        
        # 移除状态
        for status in results.get("status_remove", []):
            if status in char_status:
                char_status.remove(status)
        
        updated_character["status"] = char_status
        
        # 添加物品
        char_items = updated_character.get("items", [])
        for item in results.get("item_add", []):
            char_items.append(item)
        
        # 移除物品
        for item in results.get("item_remove", []):
            if item in char_items:
                char_items.remove(item)
        
        updated_character["items"] = char_items
        
        # 更新关系
        char_relationships = updated_character.get("relationships", {})
        for rel, change in results.get("relationship_changes", {}).items():
            char_relationships[rel] = char_relationships.get(rel, 0) + change
        
        updated_character["relationships"] = char_relationships
        
        # 返回更新后的角色状态、结果文本和后续事件
        return updated_character, result_text, results.get("follow_up_events", []) 