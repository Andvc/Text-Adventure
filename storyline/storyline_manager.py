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
        """应用存储映射（支持多级嵌套、数组、变量路径）"""
        for target_key, source_path in mapping.items():
            value = result.get(target_key)
            if value is None:
                continue
            tokens = self._parse_path_tokens(source_path, current_save)
            self._set_value_by_tokens(current_save, tokens, value)
        save_data("character", save_name, current_save)

    def _parse_path_tokens(self, path_str: str, current_save: dict) -> list:
        """
        解析路径字符串为token列表，支持变量替换与数组索引。
        例如："{type}.arr[1].x" -> ['实际type值', 'arr', 1, 'x']
        """
        import re
        tokens = []
        # 变量替换
        def replace_var(match):
            var_name = match.group(1)
            return str(current_save.get(var_name, var_name))
        path_str = re.sub(r'\{([^{}]+)\}', replace_var, path_str)
        # 分割并处理数组
        pattern = r'([^.\[\]]+)|(\[\d+\])'
        for part in path_str.split('.'):
            # 处理数组索引
            while '[' in part and ']' in part:
                idx1 = part.index('[')
                idx2 = part.index(']')
                if idx1 > 0:
                    tokens.append(part[:idx1])
                tokens.append(int(part[idx1+1:idx2]))
                part = part[idx2+1:]
            if part:
                tokens.append(part)
        return tokens

    def _set_value_by_tokens(self, obj: dict, tokens: list, value):
        """
        根据token列表递归写入value，自动创建字典/数组。
        例如：tokens=['a', 'b', 0, 'c']
        """
        cur = obj
        for i, token in enumerate(tokens):
            is_last = (i == len(tokens) - 1)
            if is_last:
                if isinstance(token, int):
                    # 当前为数组索引
                    if not isinstance(cur, list):
                        cur = []
                    # 扩展数组
                    while len(cur) <= token:
                        cur.append({})
                    cur[token] = value
                else:
                    cur[token] = value
                return
            # 非最后一层
            next_token = tokens[i + 1]
            if isinstance(token, int):
                # 当前为数组索引
                if not isinstance(cur, list):
                    # 替换父对象的引用
                    raise TypeError("父对象不是数组，无法索引")
                # 扩展数组
                while len(cur) <= token:
                    cur.append({})
                if isinstance(next_token, int):
                    if not isinstance(cur[token], list):
                        cur[token] = []
                elif not isinstance(cur[token], dict):
                    cur[token] = {}
                cur = cur[token]
            else:
                if token not in cur or (isinstance(next_token, int) and not isinstance(cur[token], list)):
                    # 下一个是数组索引则新建list，否则新建dict
                    cur[token] = [] if isinstance(next_token, int) else {}
                cur = cur[token]