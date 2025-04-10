"""
故事线管理器 (简化版)

这个模块负责故事模板的管理和故事内容的生成。
它直接使用角色模块的属性，避免不必要的变量转换。
"""

import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# 导入AI模块组件
from ai.prompt_processor import PromptProcessor
from ai.api_connector import AIModelConnector
from ai.output_parsers import OutputParser

# 导入角色模块组件
try:
    from character import character_manager
    CHARACTER_MODULE_AVAILABLE = True
except ImportError:
    CHARACTER_MODULE_AVAILABLE = False
    print("警告：未能导入角色模块，角色属性功能将不可用")

class StorylineManager:
    """故事线管理器，负责模板管理和故事生成
    
    简化版管理器直接使用角色属性，无需内外变量转换
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """初始化故事线管理器
        
        Args:
            templates_dir: 模板目录路径，默认使用模块的templates目录
        """
        # 设置模板目录
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # 使用模块默认目录
            from . import TEMPLATES_PATH
            self.templates_dir = TEMPLATES_PATH
        
        # 确保目录存在
        self.templates_dir.mkdir(exist_ok=True)
        
        # 初始化AI组件
        self.prompt_processor = PromptProcessor()
        self.api_connector = AIModelConnector()
        
        # 加载模板缓存
        self._templates_cache = {}
        self._load_all_templates()
        
        # 当前会话故事记录
        self.story_history = {}
    
    def _load_all_templates(self) -> None:
        """加载所有可用的模板"""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template = json.load(f)
                    
                # 存储到缓存
                template_id = template.get("template_id") or template_file.stem
                self._templates_cache[template_id] = template
                
            except Exception as e:
                print(f"加载模板 {template_file.name} 失败: {str(e)}")
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有可用的模板
        
        Returns:
            模板概要信息列表
        """
        result = []
        for template_id, template in self._templates_cache.items():
            result.append({
                "id": template_id,
                "name": template.get("name", template_id),
                "description": template.get("description", ""),
                "version": template.get("version", "1.0"),
                "tags": template.get("tags", [])
            })
        return result
    
    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """加载特定ID的模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板内容，如果模板不存在则返回None
        """
        # 首先检查缓存
        if template_id in self._templates_cache:
            return self._templates_cache[template_id]
        
        # 尝试从文件加载
        template_path = self.templates_dir / f"{template_id}.json"
        if template_path.exists():
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    template = json.load(f)
                
                # 存储到缓存
                self._templates_cache[template_id] = template
                return template
            except Exception as e:
                print(f"加载模板 {template_id} 失败: {str(e)}")
        
        return None
    
    def save_template(self, template: Dict[str, Any]) -> bool:
        """保存模板
        
        Args:
            template: 模板内容
            
        Returns:
            保存是否成功
        """
        # 确保模板有ID
        template_id = template.get("template_id")
        if not template_id:
            return False
        
        # 保存到文件
        template_path = self.templates_dir / f"{template_id}.json"
        try:
            with open(template_path, "w", encoding="utf-8") as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            
            # 更新缓存
            self._templates_cache[template_id] = template
            return True
        except Exception as e:
            print(f"保存模板 {template_id} 失败: {str(e)}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            删除是否成功
        """
        # 从缓存中移除
        if template_id in self._templates_cache:
            del self._templates_cache[template_id]
        
        # 从文件系统删除
        template_path = self.templates_dir / f"{template_id}.json"
        if template_path.exists():
            try:
                template_path.unlink()
                return True
            except Exception as e:
                print(f"删除模板 {template_id} 失败: {str(e)}")
        
        return False
    
    def _replace_placeholders(self, text: str) -> str:
        """替换文本中的角色属性占位符
        
        Args:
            text: 包含占位符的文本
            
        Returns:
            替换后的文本
        """
        if not CHARACTER_MODULE_AVAILABLE:
            return text
            
        # 获取所有角色属性
        all_attributes = character_manager.get_all_attributes()
        
        # 替换基本属性占位符
        for attr_name, attr_value in all_attributes.items():
            placeholder = "{" + attr_name + "}"
            if placeholder in text:
                text = text.replace(placeholder, str(attr_value))
                
            # 处理character.xxx格式
            character_placeholder = "{character." + attr_name + "}"
            if character_placeholder in text:
                text = text.replace(character_placeholder, str(attr_value))
        
        # 处理装备等复杂结构
        if "equipment" in all_attributes and isinstance(all_attributes["equipment"], dict):
            for item_name, item_value in all_attributes["equipment"].items():
                placeholder = "{equipment." + item_name + "}"
                if placeholder in text:
                    text = text.replace(placeholder, str(item_value))
        
        # 添加一些通用默认值
        if "{world_setting}" in text and "world_setting" not in all_attributes:
            text = text.replace("{world_setting}", "奇幻世界")
            
        if "{location}" in text and "location" not in all_attributes:
            text = text.replace("{location}", "神秘之地")
            
        return text
    
    def _process_template_segments(self, segments: List[str]) -> List[str]:
        """处理模板片段，替换其中的角色属性占位符
        
        Args:
            segments: 模板片段列表
            
        Returns:
            处理后的片段列表
        """
        processed_segments = []
        for segment in segments:
            processed_segments.append(self._replace_placeholders(segment))
        return processed_segments
    
    def generate_story(self, template_id: str, use_template_storage: bool = True) -> Tuple[str, List[Dict[str, Any]], str]:
        """生成故事内容
        
        Args:
            template_id: 模板ID
            use_template_storage: 是否应用模板中定义的存储映射
            
        Returns:
            元组 (故事内容, 选项列表, 故事ID)
        """
        # 加载模板
        template = self.load_template(template_id)
        if not template:
            print(f"模板 {template_id} 不存在")
            return "", [], ""
        
        # 处理提示片段
        prompt_segments = template.get("prompt_segments", [])
        processed_segments = self._process_template_segments(prompt_segments)
        
        # 使用自定义或默认提示词模板
        if "prompt_template" in template:
            custom_template = template["prompt_template"]
            custom_processor = PromptProcessor(custom_template)
            prompt = custom_processor.build_prompt(processed_segments)
        else:
            prompt = self.prompt_processor.build_prompt(processed_segments)
        
        # 调用AI生成内容
        try:
            response = self.api_connector.call_api(prompt)
            result = OutputParser.parse(response)
        except Exception as e:
            print(f"生成故事失败: {str(e)}")
            return "", [], ""
        
        # 提取故事内容
        story_content = result.get("story", "")
        story_id = str(uuid.uuid4())
        
        # 创建选项列表
        choices = []
        choice_details = []
        
        for i in range(1, 10):  # 支持最多9个选择
            choice_key = f"choice{i}"
            outcome_key = f"outcome{i}"
            
            if choice_key not in result:
                break
                
            # 处理属性变化
            stat_changes = {}
            stat_change_key = f"stat_change{i}"
            
            if stat_change_key in result:
                try:
                    stat_text = result[stat_change_key]
                    changes = stat_text.split("，")
                    for change in changes:
                        for attr_name in ["力量", "敏捷", "智力", "体质", "魅力"]:
                            if attr_name in change:
                                parts = change.split(attr_name)
                                if len(parts) > 1:
                                    value_part = parts[1].strip()
                                    if value_part.startswith("+") or value_part.startswith("-"):
                                        try:
                                            value = int(value_part[0:2])
                                            stat_changes[attr_name] = value
                                        except ValueError:
                                            pass
                except Exception as e:
                    print(f"处理属性变化失败: {str(e)}")
            
            # 添加选项
            choices.append({
                "id": i-1,
                "text": result[choice_key],
                "outcome": result.get(outcome_key, "")
            })
            
            choice_details.append({
                "id": choice_key,
                "text": result[choice_key],
                "outcome": result.get(outcome_key, ""),
                "stat_changes": stat_changes
            })
        
        # 存储故事记录
        self.story_history[story_id] = {
            "template_id": template_id,
            "content": story_content,
            "choices": choice_details,
            "raw_result": result,
            "generated_at": time.time()
        }
        
        # 存储输出到角色属性
        if use_template_storage and "output_storage" in template and CHARACTER_MODULE_AVAILABLE:
            self._apply_storage_mapping(result, story_content, template["output_storage"])
        
        return story_content, choices, story_id
    
    def _apply_storage_mapping(self, result: Dict[str, Any], story_content: str, mapping: Dict[str, str]) -> None:
        """应用存储映射，将输出存储到角色属性
        
        Args:
            result: AI输出结果
            story_content: 格式化的故事内容
            mapping: 存储映射 {输出字段: 属性名}
        """
        if not CHARACTER_MODULE_AVAILABLE:
            return
            
        for output_field, attr_name in mapping.items():
            # 处理特殊字段"content"
            if output_field == "content":
                value = story_content
            # 处理普通输出字段
            elif output_field in result:
                value = result[output_field]
            else:
                continue
            
            # 存储或更新属性
            try:
                current_value = character_manager.get_attribute(attr_name)
                if current_value is not None:
                    character_manager.set_attribute(attr_name, value)
                    print(f"更新属性: {attr_name}")
                else:
                    character_manager.create_attribute(attr_name, value)
                    print(f"创建属性: {attr_name}")
            except Exception as e:
                print(f"存储属性失败 {attr_name}: {str(e)}")
    
    def make_choice(self, story_id: str, choice_index: int) -> None:
        """执行选择，应用属性变化
        
        Args:
            story_id: 故事ID
            choice_index: 选择索引（从0开始）
        """
        # 检查故事ID
        if story_id not in self.story_history:
            print(f"故事ID {story_id} 不存在")
            return
            
        # 获取故事记录
        story_data = self.story_history[story_id]
        choices = story_data.get("choices", [])
        
        # 验证选择索引
        if choice_index < 0 or choice_index >= len(choices):
            print(f"无效的选择索引: {choice_index}")
            return
            
        # 获取选择
        choice = choices[choice_index]
        
        # 应用属性变化
        if CHARACTER_MODULE_AVAILABLE and "stat_changes" in choice and choice["stat_changes"]:
            for attr_name, change_value in choice["stat_changes"].items():
                try:
                    current_value = character_manager.get_attribute(attr_name)
                    if isinstance(current_value, (int, float)):
                        character_manager.set_attribute(attr_name, current_value + change_value)
                        print(f"更新属性 {attr_name}: {current_value} -> {current_value + change_value}")
                except Exception as e:
                    print(f"无法更新属性 {attr_name}: {str(e)}")
        
        # 记录选择
        if CHARACTER_MODULE_AVAILABLE:
            character_manager.set_attribute("last_choice", choice["text"])
            character_manager.set_attribute("last_story", story_data["content"])
    
    def get_story(self, story_id: str) -> Optional[Dict[str, Any]]:
        """获取故事记录
        
        Args:
            story_id: 故事ID
            
        Returns:
            故事记录，如果不存在则返回None
        """
        return self.story_history.get(story_id)
        
    def clear_history(self) -> None:
        """清除所有故事历史记录"""
        self.story_history = {}
        print("已清除所有故事历史记录")
    
    def save_history_to_file(self, filepath: str) -> bool:
        """将故事历史记录保存到文件
        
        Args:
            filepath: 保存路径
            
        Returns:
            保存是否成功
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.story_history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存历史记录失败: {str(e)}")
            return False
    
    def load_history_from_file(self, filepath: str) -> bool:
        """从文件加载故事历史记录
        
        Args:
            filepath: 文件路径
            
        Returns:
            加载是否成功
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                history = json.load(f)
            
            self.story_history = history
            return True
        except Exception as e:
            print(f"加载历史记录失败: {str(e)}")
            return False