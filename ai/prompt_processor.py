"""
提示词处理模块，用于组合和构建提示词
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import config
from data.data_manager import load_save, get_nested_save_value

class PromptProcessor:
    """提示词处理器，用于构建和处理提示词"""
    
    def __init__(self, template: Optional[str] = None):
        """
        初始化提示词处理器
        
        Args:
            template: 可选，自定义提示词模板，默认使用配置中的模板
        """
        self.template = template if template else config.DEFAULT_PROMPT_TEMPLATE
    
    def _get_nested_value(self, data: Dict[str, Any], path: str, default=None):
        """
        从嵌套字典中获取指定路径的值
        
        Args:
            data: 嵌套字典数据
            path: 点分隔的路径，如'a.b.c'
            default: 默认值，如果路径不存在则返回此值
        
        Returns:
            路径指定的值或默认值
        """
        keys = path.split('.')
        result = data
        
        for key in keys:
            # 处理数组索引，如items[0]
            array_match = re.match(r'([^\[]+)\[(\d+)\]', key)
            if array_match:
                array_key = array_match.group(1)
                index = int(array_match.group(2))
                
                if isinstance(result, dict) and array_key in result:
                    array_value = result[array_key]
                    if isinstance(array_value, list) and 0 <= index < len(array_value):
                        result = array_value[index]
                    else:
                        return default
                else:
                    return default
            # 处理普通键
            elif isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return default
        
        return result
    
    def parse_segments(self, segments: List[str]) -> Dict[str, Any]:
        """
        解析输入片段，按类型分类
        
        Args:
            segments: 提示词片段列表
            
        Returns:
            按类型分类的提示词字典
        """
        result = {
            "info": [],      # () 包围的信息类提示词
            "content": [],   # <> 包围的输出内容类提示词
            "format": [],    # [] 包围的输出格式类提示词
            "pairs": []      # 按顺序配对的<内容>和[格式]
        }
        
        # 先按类型分类所有片段
        for segment in segments:
            segment = segment.strip()
            if segment.startswith("(") and segment.endswith(")"):
                # 信息类提示词
                result["info"].append(segment[1:-1])
            elif segment.startswith("<") and segment.endswith(">"):
                # 输出内容类提示词
                result["content"].append(segment[1:-1])
            elif segment.startswith("[") and segment.endswith("]"):
                # 输出格式类提示词
                result["format"].append(segment[1:-1])
        
        # 匹配内容和格式的配对
        content_formats = []
        i = 0
        while i < len(segments) - 1:
            current = segments[i].strip()
            next_seg = segments[i + 1].strip()
            
            if current.startswith("<") and current.endswith(">") and next_seg.startswith("[") and next_seg.endswith("]"):
                # 找到一对配对的内容和格式
                content = current[1:-1]
                format_str = next_seg[1:-1]
                
                # 提取字段名和类型: [field="type"] -> field, type
                field_types = {}
                for match in re.finditer(r'([^=,\s]+)=["\'"]([^"\']+)["\']', format_str):
                    field_name = match.group(1)
                    field_type = match.group(2)
                    field_types[field_name] = field_type
                
                content_formats.append({
                    "content": content,
                    "format": format_str,
                    "field_types": field_types
                })
                i += 2  # 跳过已配对的两个片段
            else:
                i += 1  # 没找到配对，继续下一个
        
        result["pairs"] = content_formats
        return result
    
    def _build_json_template(self, fields_content: Dict[str, Tuple[str, str]]) -> str:
        """
        构建包含类型和三引号描述的JSON模板
        
        Args:
            fields_content: 字段名到(类型,内容)元组的映射
            
        Returns:
            JSON格式的模板字符串，包含三引号描述
        """
        lines = ["{"]
        
        fields = list(fields_content.keys())
        for i, field in enumerate(fields):
            field_type, content = fields_content[field]
            
            # 添加字段和类型
            lines.append(f'  "{field}": "{field_type}"')
            
            # 添加三引号描述
            if content:
                lines.append(f'  """{content}"""')
            
            # 添加逗号（除了最后一个字段）
            if i < len(fields) - 1:
                lines[-1] += ','
        
        lines.append("}")
        return "\n".join(lines)
    
    def _apply_template(self, template: str, replacements: Dict[str, str]) -> str:
        """
        应用模板替换
        
        Args:
            template: 模板字符串
            replacements: 替换映射
            
        Returns:
            替换后的字符串
        """
        result = template
        for key, value in replacements.items():
            if f"{{{key}}}" in result:
                result = result.replace(f"{{{key}}}", value)
        return result
    
    def _replace_placeholders(self, text: str, save_data: Dict[str, Any]) -> str:
        """
        替换字符串中的占位符
        
        支持以下格式的占位符:
        1. {key} 或 {key.subkey} - 从save_data中提取数据
        2. {text;file;path} - 从data/text目录下的file.json文件中提取path指定的数据
        3. {key.{nested}} 或 {text;file;path[{index}]} - 嵌套占位符，递归处理
        
        Args:
            text: 包含占位符的文本
            save_data: 存档数据
            
        Returns:
            替换后的文本
        """
        # 如果没有占位符，直接返回
        if '{' not in text:
            return text
        
        # 最多循环20次，避免可能的无限递归
        for i in range(20):
            # 记录之前的文本，用于检测是否有变化
            previous_text = text
            
            # 查找所有占位符，优先处理没有嵌套的占位符
            # 这个正则表达式会匹配不包含{的占位符，即最内层的占位符
            simple_pattern = r'\{([^{]+?)\}'
            matches = list(re.finditer(simple_pattern, text))
            
            # 如果没有找到简单占位符，但文本中仍有占位符，可能是嵌套结构不完整
            if not matches and '{' in text:
                # 尝试匹配所有占位符，可能包含嵌套结构
                all_pattern = r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
                matches = list(re.finditer(all_pattern, text))
            
            if not matches:
                break  # 没有找到任何占位符，结束循环
                
            # 处理找到的每个占位符
            for match in matches:
                placeholder = match.group(0)  # 完整的占位符，如{character.name}
                content = match.group(1)      # 占位符内容，如character.name
                
                replaced_value = None  # 存储替换的值
                
                # 处理text格式的占位符 {text;file;path}
                if content.startswith('text;'):
                    parts = content.split(';', 2)
                    if len(parts) == 3:
                        file_name = parts[1]
                        path = parts[2]
                        
                        try:
                            # 加载指定的文本数据文件
                            file_data = load_save('text', file_name)
                            if file_data:
                                # 从文件中提取指定路径的数据
                                value = self._get_nested_value(file_data, path)
                                if value is not None:
                                    replaced_value = str(value)
                                else:
                                    replaced_value = f"未找到数据: {path}"
                            else:
                                replaced_value = f"文件不存在: {file_name}"
                        except Exception as e:
                            replaced_value = f"错误: {str(e)}"
                
                # 处理嵌套路径格式 {key.subkey}
                elif '.' in content:
                    parts = content.split('.', 1)
                    key = parts[0]
                    subpath = parts[1]
                    
                    # 从save_data中提取数据
                    if key in save_data:
                        # 处理嵌套字典
                        if isinstance(save_data[key], dict):
                            value = self._get_nested_value(save_data[key], subpath)
                            if value is not None:
                                replaced_value = str(value)
                        # 处理嵌套列表
                        elif isinstance(save_data[key], list):
                            # 尝试处理数组索引，如skills[0]
                            array_match = re.match(r'([^\[]+)\[(\d+)\]', subpath)
                            if array_match:
                                array_key = array_match.group(1)
                                if array_key == '':  # 直接使用数组索引
                                    index = int(array_match.group(2))
                                    if 0 <= index < len(save_data[key]):
                                        replaced_value = str(save_data[key][index])
                            elif subpath:  # 有子路径但不是索引格式
                                replaced_value = str(save_data[key])
                            else:  # 没有子路径，直接返回整个数组
                                replaced_value = str(save_data[key])
                
                # 处理简单格式 {key}
                else:
                    key = content
                    if key in save_data:
                        # 根据类型进行处理
                        value = save_data[key]
                        if isinstance(value, (dict, list)):
                            replaced_value = str(value)
                        else:
                            replaced_value = str(value)
                
                # 如果成功获取了替换值，则替换占位符
                if replaced_value is not None:
                    text = text.replace(placeholder, replaced_value)
            
            # 如果文本没有变化，且没有嵌套占位符，结束循环
            if text == previous_text:
                break
            
            # 打印当前处理结果，便于调试（可选）
            # print(f"迭代 {i+1}: {text}")
        
        return text
    
    def build_prompt(self, segments: List[str], save_data: Dict[str, Any] = None) -> str:
        """
        根据输入片段构建完整提示词，使用自定义模板或默认JSON格式
        
        Args:
            segments: 提示词片段列表
            save_data: 存档数据，用于替换占位符
            
        Returns:
            构建好的完整提示词
        """
        if save_data is None:
            save_data = {}
        
        # 替换片段中的占位符
        processed_segments = []
        for segment in segments:
            processed_segments.append(self._replace_placeholders(segment, save_data))
        
        # 解析处理后的片段
        parsed = self.parse_segments(processed_segments)
        
        # 组合信息类提示词
        input_info = " ".join([f"({info})" for info in parsed["info"]])
        
        # 提取字段和内容
        fields_content = {}
        
        # 从配对中提取
        if parsed["pairs"]:
            for pair in parsed["pairs"]:
                content = pair["content"]
                field_types = pair.get("field_types", {})
                
                for field, field_type in field_types.items():
                    fields_content[field] = (field_type, content)
        
        # 构建JSON模板
        json_template = self._build_json_template(fields_content)
        
        # 如果有自定义模板，尝试使用它
        if self.template:
            try:
                replacements = {
                    "background": "\n".join([f"({info})" for info in parsed["info"]]),
                    "content": "\n".join([f"<{content}>" for content in parsed["content"]]),
                    "format": json_template,
                    "input_info": input_info,
                    "json_format": json_template
                }
                return self._apply_template(self.template, replacements)
            except Exception as e:
                print(f"使用自定义模板失败: {str(e)}，回退到默认模板")
        
        # 使用默认的多字段模板
        multi_field_template = """请严格按照以下JSON格式输出，不要添加任何其他内容或解释。
三引号中的内容是指令，您需要根据指令生成内容：

{json_format}

请确保输出是有效的JSON格式，包含所有指定的字段。
提供给你的信息: {input_info}"""
        
        return self._apply_template(multi_field_template, {
            "json_format": json_template,
            "input_info": input_info
        })
    
    def set_template(self, template: str) -> None:
        """
        设置新的提示词模板
        
        Args:
            template: 新的提示词模板
        """
        self.template = template 