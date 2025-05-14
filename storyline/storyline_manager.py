"""
故事线管理模块 - 负责管理和生成故事内容

这个模块负责故事模板的管理和故事内容的生成。
它直接使用数据模块的存档数据，避免不必要的变量转换。
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

# 导入数据模块组件
from data.data_manager import (
    get_save_value,
    get_nested_save_value,
    get_indexed_save,
    load_save,
    save_data
)

class StorylineManager:
    """故事线管理器，负责模板管理和故事生成
    
    简化版管理器直接使用存档数据，无需内外变量转换
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
    
    def _replace_placeholders(self, text: str, save_data: Dict[str, Any]) -> str:
        """替换文本中的占位符
        
        此方法现在委托给PromptProcessor的实现，以确保一致的占位符处理逻辑
        
        Args:
            text: 包含占位符的文本
            save_data: 存档数据
            
        Returns:
            替换后的文本
        """
        # 使用PromptProcessor的实现
        from ai.prompt_processor import PromptProcessor
        processor = PromptProcessor()
        return processor._replace_placeholders(text, save_data)
    
    def _process_template_segments(self, segments: List[str], save_data: Dict[str, Any]) -> List[str]:
        """处理模板片段，替换其中的存档数据占位符
        
        Args:
            segments: 模板片段列表
            save_data: 存档数据
            
        Returns:
            处理后的片段列表
        """
        processed_segments = []
        for segment in segments:
            processed_segments.append(self._replace_placeholders(segment, save_data))
        return processed_segments
    
    def generate_story(self, save_name: str, template_id: str, use_template_storage: bool = True) -> bool:
        """生成故事内容
        
        Args:
            save_name: 存档名称
            template_id: 模板ID
            use_template_storage: 是否应用模板中定义的存储映射
            
        Returns:
            bool: 生成是否成功
        """
        # 加载存档数据
        current_save = load_save("character", save_name)
        if current_save is None:
            print(f"存档 '{save_name}' 不存在")
            return False
        
        # 保存原有的selected_choice
        selected_choice = current_save.get('selected_choice', '')
        
        # 加载模板
        template = self.load_template(template_id)
        if not template:
            print(f"模板 {template_id} 不存在")
            return False
        
        try:
            # 处理提示片段
            prompt_segments = template.get("prompt_segments", [])
            processed_segments = self._process_template_segments(prompt_segments, current_save)
            
            print("\n=== 处理后的提示词片段 ===")
            for segment in processed_segments:
                print(segment)
            print("=======================\n")
            
            # 使用自定义或默认提示词模板
            if "prompt_template" in template:
                custom_template = template["prompt_template"]
                custom_processor = PromptProcessor(custom_template)
                prompt = custom_processor.build_prompt(processed_segments, current_save)
            else:
                prompt = self.prompt_processor.build_prompt(processed_segments, current_save)
            
            print("\n=== 最终生成的提示词 ===")
            print(prompt)
            print("=======================\n")
            
            # 调用AI生成内容
            response = self.api_connector.call_api(prompt)
            result = OutputParser.parse(response, parser_type="json")
            
            if not result:
                print("AI生成内容解析失败")
                return False
                
            # 应用存储映射
            if use_template_storage and "output_storage" in template:
                self._apply_storage_mapping(result, template["output_storage"], current_save, save_name)
            
            # 恢复原有的selected_choice
            current_save['selected_choice'] = selected_choice
            
            # 更新存档
            return save_data("character", save_name, current_save)
            
        except Exception as e:
            print(f"生成故事失败: {str(e)}")
            return False
        
    def _apply_storage_mapping(self, result: Dict[str, Any], mapping: Dict[str, str], current_save: Dict[str, Any], save_name: str) -> None:
        """应用存储映射
        
        Args:
            result: 生成的结果数据
            mapping: 存储映射配置
            current_save: 当前存档数据
            save_name: 存档名称
        """
        for target_key, source_path in mapping.items():
            # 从结果中获取值
            value = result.get(target_key)
            if value is None:
                continue
            
            # 处理嵌套路径映射 (例如 "{temp_type}.name")
            if "." in source_path and "{" in source_path and "}" in source_path:
                # 提取变量部分
                start_idx = source_path.find("{")
                end_idx = source_path.find("}")
                if start_idx != -1 and end_idx != -1:
                    var_name = source_path[start_idx+1:end_idx]
                    var_value = current_save.get(var_name)
                    if var_value:
                        # 获取变量后的路径部分
                        path_suffix = source_path[end_idx+1:]
                        if path_suffix.startswith("."):
                            path_suffix = path_suffix[1:]  # 移除前导点
                        
                        # 创建或获取目标对象
                        if var_value not in current_save:
                            current_save[var_value] = {}
                        
                        # 如果目标是嵌套对象，确保所有路径都存在
                        if "." in path_suffix:
                            parts = path_suffix.split(".")
                            current_obj = current_save[var_value]
                            # 处理中间路径
                            for i, part in enumerate(parts[:-1]):
                                if part not in current_obj:
                                    current_obj[part] = {}
                                current_obj = current_obj[part]
                            # 设置最终值
                            current_obj[parts[-1]] = value
                        else:
                            # 简单路径，直接设置
                            if isinstance(current_save[var_value], dict):
                                current_save[var_value][path_suffix] = value
                            else:
                                current_save[var_value] = {path_suffix: value}
                        continue
            
            # 直接存储到顶层
            current_save[target_key] = value
        
        # 保存更新后的存档数据
        save_data("character", save_name, current_save)