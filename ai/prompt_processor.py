"""
提示词处理模块，用于组合和构建提示词
"""

import re
from typing import List, Dict, Any, Optional
import config

class PromptProcessor:
    """提示词处理器，用于构建和处理提示词"""
    
    def __init__(self, template: Optional[str] = None):
        """
        初始化提示词处理器
        
        Args:
            template: 可选，自定义提示词模板，默认使用配置中的模板
        """
        self.template = template if template else config.DEFAULT_PROMPT_TEMPLATE
    
    def parse_segments(self, segments: List[str]) -> Dict[str, List[str]]:
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
                content_formats.append({
                    "content": current[1:-1],
                    "format": next_seg[1:-1]
                })
                i += 2  # 跳过已配对的两个片段
            else:
                i += 1  # 没找到配对，继续下一个
        
        result["pairs"] = content_formats
        return result
    
    def _build_json_template(self, fields_content: Dict[str, str]) -> str:
        """
        构建JSON模板
        
        Args:
            fields_content: 字段和内容的映射
            
        Returns:
            JSON格式的模板字符串
        """
        json_template = "{\n"
        for field, content in fields_content.items():
            json_template += f'  "{field}": "请在这里填入中文-{content}",\n'
        return json_template.rstrip(",\n") + "\n}"
    
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
    
    def build_prompt(self, segments: List[str]) -> str:
        """
        根据输入片段构建完整提示词，使用自定义模板或默认JSON格式
        
        Args:
            segments: 提示词片段列表
            
        Returns:
            构建好的完整提示词
        """
        parsed = self.parse_segments(segments)
        
        # 组合信息类提示词
        input_info = " ".join([f"({info})" for info in parsed["info"]])
        
        # 提取字段和内容
        fields_content = {}
        
        # 从配对中提取
        if parsed["pairs"]:
            for pair in parsed["pairs"]:
                content = pair["content"]
                format_str = pair["format"]
                fields = re.findall(r'([^=,\s]+)=', format_str)
                for field in fields:
                    fields_content[field] = content
        
        # 从单独的格式中提取多字段
        elif parsed["format"]:
            format_str = parsed["format"][0]
            fields = re.findall(r'([^=,\s]+)=', format_str)
            for field in fields:
                field_name = field.replace("_", " ")
                fields_content[field] = f"{field_name}-内容"
        
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
        multi_field_template = """请严格按照以下JSON格式输出，不要添加任何其他内容或解释：

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