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
            元组 (主要内容, 选项列表, 故事ID)
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
        
        # 生成唯一ID（用于API返回值）
        story_id = str(uuid.uuid4())
        
        # 提取主要内容（从模板配置或默认使用"story"字段）
        main_field = template.get("main_content_field", "story")
        main_content = result.get(main_field, "")
        
        # 收集所有选项
        choices = []
        
        # 从result中找出所有以"choice"开头的字段
        choice_fields = [k for k in result.keys() if k.startswith("choice") and k[6:].isdigit()]
        choice_fields.sort(key=lambda x: int(x[6:]))  # 按数字排序
        
        for i, choice_field in enumerate(choice_fields):
            choice_text = result[choice_field]
            if not choice_text:
                continue
                
            choices.append({
                "id": i,
                "text": choice_text,
                "field": choice_field  # 记录原始字段名，用于后续处理
            })
        
        # 存储输出到角色属性
        if use_template_storage and "output_storage" in template and CHARACTER_MODULE_AVAILABLE:
            self._apply_storage_mapping(result, template["output_storage"])
        
        return main_content, choices, story_id
    
    def _apply_storage_mapping(self, result: Dict[str, Any], mapping: Dict[str, str]) -> None:
        """应用存储映射，将输出存储到角色属性
        
        Args:
            result: AI输出结果
            mapping: 存储映射 {输出字段: 属性名}
        """
        if not CHARACTER_MODULE_AVAILABLE:
            return
            
        for output_field, attr_name in mapping.items():
            # 如果结果中存在映射的字段，则存储到对应属性
            if output_field in result:
                value = result[output_field]
                
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
        """执行选择（简化版本，仅更新事件选择属性）
        
        Args:
            story_id: 故事ID（为兼容旧代码保留此参数，但不再使用）
            choice_index: 选择索引（从0开始）
        """
        # 由于不再使用story_history，只需从角色属性中获取选项并更新事件选择
        if not CHARACTER_MODULE_AVAILABLE:
            print("角色模块不可用，无法更新选择")
            return
            
        # 尝试从属性中获取选项列表
        # 检查常见的选项属性命名
        all_attrs = character_manager.get_all_attributes()
        options = []
        
        # 扫描可能的选项属性
        option_names = ["选项1", "选项2", "选项3", "option1", "option2", "option3"]
        for name in option_names:
            if name in all_attrs and all_attrs[name]:
                options.append(all_attrs[name])
        
        # 验证选择索引
        if not options:
            print("未找到选项属性")
            return
            
        if choice_index < 0 or choice_index >= len(options):
            print(f"无效的选择索引: {choice_index}")
            return
        
        # 更新事件选择属性
        try:
            character_manager.set_attribute("事件选择", options[choice_index])
            print(f"更新事件选择: {options[choice_index]}")
        except Exception as e:
            print(f"设置事件选择失败: {str(e)}")