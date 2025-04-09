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
            "format": [],    # {} 包围的输出格式类提示词
            "pairs": []      # 按顺序配对的<内容>和{格式}
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
            elif segment.startswith("{") and segment.endswith("}"):
                # 输出格式类提示词
                result["format"].append(segment[1:-1])
        
        # 匹配内容和格式的配对
        content_formats = []
        i = 0
        while i < len(segments) - 1:
            current = segments[i].strip()
            next_seg = segments[i + 1].strip()
            
            if current.startswith("<") and current.endswith(">") and next_seg.startswith("{") and next_seg.endswith("}"):
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
    
    def build_prompt(self, segments: List[str]) -> str:
        """
        根据输入片段构建完整提示词，使用JSON格式
        
        Args:
            segments: 提示词片段列表
            
        Returns:
            构建好的完整提示词
        """
        parsed = self.parse_segments(segments)
        
        # 组合信息类提示词
        input_info = " ".join([f"({info})" for info in parsed["info"]])
        
        # 检查是否存在内容-格式配对
        if parsed["pairs"]:
            # 提取所有字段和它们对应的内容
            fields_content = {}
            content_map = {}  # 存储格式到内容的映射
            
            for pair in parsed["pairs"]:
                content = pair["content"]
                format_str = pair["format"]
                content_map[format_str] = content
                
                # 从格式中提取字段
                fields = re.findall(r'([^=,\s]+)=', format_str)
                
                # 处理字段与内容的对应关系
                if len(fields) == 1:
                    # 单一字段，使用完整内容描述
                    fields_content[fields[0]] = content
                else:
                    # 多字段，包含字段名和内容描述
                    for field in fields:
                        fields_content[field] = f"{field.replace('_', ' ')}-{content}"
            
            # 构建JSON模板
            json_template = "{\n"
            for field, content in fields_content.items():
                json_template += f'  "{field}": "请在这里填入中文-{content}",\n'
            
            # 移除最后一个逗号
            json_template = json_template.rstrip(",\n") + "\n}"
            
            # 创建适应多字段的模板
            multi_field_template = """请严格按照以下JSON格式输出，不要添加任何其他内容或解释：

{json_format}

请确保输出是有效的JSON格式，包含所有指定的字段。
提供给你的信息: {input_info}"""
            
            # 应用模板
            prompt = multi_field_template.format(
                json_format=json_template,
                input_info=input_info
            )
            return prompt
        
        # 如果没有配对，尝试使用标准方法
        # 获取输出内容和格式
        output_content = parsed["content"][0] if parsed["content"] else "内容"
        output_format = parsed["format"][0] if parsed["format"] else ""
        
        # 处理输出格式
        if output_format:
            # 检查是否是多字段格式
            fields = re.findall(r'([^=,\s]+)=', output_format)
            
            if len(fields) > 1:
                # 多字段格式，显示字段名和内容描述
                json_template = "{\n"
                for field in fields:
                    field_name = field.replace("_", " ")
                    json_template += f'  "{field}": "请在这里填入中文-{field_name}-{output_content}",\n'
                # 移除最后一个逗号
                json_template = json_template.rstrip(",\n") + "\n}"
                
                # 创建一个临时模板来适应多字段
                multi_field_template = """请严格按照以下JSON格式输出，不要添加任何其他内容或解释：

{json_format}

请确保输出是有效的JSON格式，包含所有指定的字段。
提供给你的信息: {input_info}"""
                
                # 应用临时模板
                prompt = multi_field_template.format(
                    json_format=json_template,
                    input_info=input_info
                )
                return prompt
        
        # 单字段格式或无格式，使用默认模板
        output_key = "content"  # 默认键名
        if output_format:
            key_match = re.search(r'([^=]+)=', output_format)
            if key_match:
                output_key = key_match.group(1).strip()
        
        # 修改模板以添加破折号
        modified_template = self.template.replace(
            '"{output_key}": "在这里填入{output_content}"',
            '"{output_key}": "请在这里填入中文-{output_content}"'
        )
        
        # 应用模板
        prompt = modified_template.format(
            input_info=input_info,
            output_content=output_content,
            output_key=output_key
        )
        
        return prompt
    
    def set_template(self, template: str) -> None:
        """
        设置新的提示词模板
        
        Args:
            template: 新的提示词模板
        """
        self.template = template 