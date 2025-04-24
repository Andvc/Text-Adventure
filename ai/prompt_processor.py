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
        
        # 提取内容和格式信息，用于替换模板
        if parsed["content"]:
            output_content = parsed["content"][0]
        else:
            output_content = "内容"
            
        # 检查是否有自定义模板，如果有则尝试使用它
        # 首先检查模板中是否包含必要的占位符
        has_custom_template = False
        custom_template_usable = False
        
        if self.template != config.DEFAULT_PROMPT_TEMPLATE:
            has_custom_template = True
            # 检查模板是否包含必要的占位符
            if "{input_info}" in self.template:
                custom_template_usable = True
        
        # 处理配对和格式信息
        if parsed["pairs"] or (parsed["format"] and len(re.findall(r'([^=,\s]+)=', parsed["format"][0])) > 1):
            # 有配对或多字段格式，需要构建JSON结构
            
            # 提取字段和内容
            fields_content = {}
            
            # 从配对中提取
            if parsed["pairs"]:
                for pair in parsed["pairs"]:
                    content = pair["content"]
                    format_str = pair["format"]
                    
                    # 从格式中提取字段
                    fields = re.findall(r'([^=,\s]+)=', format_str)
                    
                    # 处理字段与内容的对应关系
                    if len(fields) == 1:
                        # 单一字段
                        fields_content[fields[0]] = content
                    else:
                        # 多字段
                        for field in fields:
                            fields_content[field] = f"{field.replace('_', ' ')}-{content}"
            # 从单独的格式中提取多字段
            elif parsed["format"]:
                format_str = parsed["format"][0]
                fields = re.findall(r'([^=,\s]+)=', format_str)
                
                if len(fields) > 1:
                    for field in fields:
                        field_name = field.replace("_", " ")
                        fields_content[field] = f"{field_name}-{output_content}"
            
            # 构建JSON模板
            json_template = "{\n"
            for field, content in fields_content.items():
                json_template += f'  "{field}": "请在这里填入中文-{content}",\n'
            
            # 移除最后一个逗号
            json_template = json_template.rstrip(",\n") + "\n}"
            
            # 如果有可用的自定义模板，尝试使用它
            if custom_template_usable:
                try:
                    # 替换背景、内容和格式占位符
                    prompt = self.template
                    if "{background}" in prompt or "{content}" in prompt or "{format}" in prompt:
                        # 收集各类型片段
                        background_parts = [f"({info})" for info in parsed["info"]]
                        content_parts = [f"<{content}>" for content in parsed["content"]]
                        format_parts = [json_template]
                        
                        # 替换占位符
                        if "{background}" in prompt:
                            prompt = prompt.replace("{background}", "\n".join(background_parts))
                        if "{content}" in prompt:
                            prompt = prompt.replace("{content}", "\n".join(content_parts))
                        if "{format}" in prompt:
                            prompt = prompt.replace("{format}", "\n".join(format_parts))
                    else:
                        # 使用标准占位符
                        prompt = self.template.format(
                            input_info=input_info,
                            json_format=json_template
                        )
                    return prompt
                except Exception as e:
                    print(f"使用自定义模板失败: {str(e)}，回退到默认模板")
            
            # 使用默认的多字段模板
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
        
        # 单字段格式或无格式的情况
        output_key = "content"  # A默认键名
        if parsed["format"]:
            output_format = parsed["format"][0]
            key_match = re.search(r'([^=]+)=', output_format)
            if key_match:
                output_key = key_match.group(1).strip()
        
        # 如果有可用的自定义模板，尝试使用它
        if custom_template_usable:
            try:
                # 替换背景、内容和格式占位符
                prompt = self.template
                if "{background}" in prompt or "{content}" in prompt or "{format}" in prompt:
                    # 收集各类型片段
                    background_parts = [f"({info})" for info in parsed["info"]]
                    content_parts = [f"<{content}>" for content in parsed["content"]]
                    format_template = f'{{"\\"{output_key}\\": "请在这里填入中文-{output_content}"}}'
                    
                    # 替换占位符
                    if "{background}" in prompt:
                        prompt = prompt.replace("{background}", "\n".join(background_parts))
                    if "{content}" in prompt:
                        prompt = prompt.replace("{content}", "\n".join(content_parts))
                    if "{format}" in prompt:
                        prompt = prompt.replace("{format}", format_template)
                else:
                    # 使用标准占位符
                    prompt = self.template.format(
                        input_info=input_info,
                        output_content=output_content,
                        output_key=output_key
                    )
                return prompt
            except Exception as e:
                print(f"使用自定义模板失败: {str(e)}，回退到默认模板")
        
        # 使用默认模板
        modified_template = config.DEFAULT_PROMPT_TEMPLATE.replace(
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