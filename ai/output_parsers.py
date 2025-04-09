"""
输出解析器模块，用于解析和提取AI响应中的结构化内容
"""

import re
import json
from typing import Dict, Any, List, Optional, Type, Union
from abc import ABC, abstractmethod

class BaseOutputParser(ABC):
    """输出解析器基类"""
    
    @abstractmethod
    def parse(self, output: str) -> Dict[str, Any]:
        """
        解析输出内容
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            解析后的结构化内容
        """
        pass
    
    @classmethod
    def get_parser_type(cls) -> str:
        """
        获取解析器类型
        
        Returns:
            解析器类型名称
        """
        return cls.__name__.replace("OutputParser", "").lower()

class JSONOutputParser(BaseOutputParser):
    """JSON格式输出解析器"""
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        解析JSON格式的输出
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            解析后的JSON对象
        """
        try:
            # 清理输出文本
            cleaned_output = self._clean_output(output)
            # 解析JSON
            return json.loads(cleaned_output)
        except json.JSONDecodeError as e:
            # 尝试提取JSON部分
            json_text = self._extract_json(output)
            if json_text:
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass
            
            # 如果都失败了，返回一个空字典并记录错误
            print(f"JSON解析失败: {str(e)}\n原始输出: {output}")
            return {"error": "无法解析JSON输出", "raw_output": output}
    
    def _clean_output(self, output: str) -> str:
        """清理输出，移除可能的非JSON内容"""
        output = output.strip()
        
        # 移除可能的代码块标记
        output = re.sub(r'```json\s*', '', output)
        output = re.sub(r'```\s*$', '', output)
        
        # 移除开头的可能解释
        if output.find('{') > 0:
            output = output[output.find('{'):]
        
        # 移除结尾的可能解释
        if output.rfind('}') < len(output) - 1:
            output = output[:output.rfind('}')+1]
            
        return output
    
    def _extract_json(self, output: str) -> Optional[str]:
        """尝试从文本中提取JSON部分"""
        # 匹配最外层的{}
        json_pattern = r'({[^{}]*(?:{[^{}]*}[^{}]*)*})'
        match = re.search(json_pattern, output, re.DOTALL)
        if match:
            return match.group(1)
        return None

class FormatPatternParser(BaseOutputParser):
    """根据格式模式解析输出的解析器（作为JSON解析失败时的后备）"""
    
    def __init__(self, pattern: Optional[str] = None):
        """
        初始化格式模式解析器
        
        Args:
            pattern: 可选，自定义正则表达式模式
        """
        self.pattern = pattern if pattern else r'["\']?([^"\'=]+)["\']?\s*[=:]\s*["\']([^"\']*)["\']'
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        使用正则表达式模式解析输出
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            解析后的字典，键为属性名，值为属性值
        """
        result = {}
        matches = re.finditer(self.pattern, output)
        
        for match in matches:
            key = match.group(1).strip()
            value = match.group(2).strip()
            result[key] = value
        
        # 如果没有找到匹配，尝试寻找键值对的其他可能格式
        if not result:
            # 尝试查找 "key": "value" 格式
            alt_pattern = r'["\']([^"\']+)["\']:\s*["\']([^"\']+)["\']'
            matches = re.finditer(alt_pattern, output)
            for match in matches:
                key = match.group(1).strip()
                value = match.group(2).strip()
                result[key] = value
        
        return result

class StoryOutputParser(BaseOutputParser):
    """故事输出解析器，专门用于解析故事内容"""
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        解析故事格式的输出
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            包含故事内容的字典
        """
        # 匹配story="内容"模式
        story_pattern = r'story="([^"]*)"'
        match = re.search(story_pattern, output)
        
        if match:
            return {"story": match.group(1)}
        
        # 如果没有找到精确匹配，回退到更宽松的解析
        return FormatPatternParser().parse(output)

class ChoiceOutputParser(BaseOutputParser):
    """选择输出解析器，专门用于解析选择内容"""
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        解析选择格式的输出
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            包含选择内容的字典
        """
        # 匹配choice="内容"模式
        choice_pattern = r'choice="([^"]*)"'
        match = re.search(choice_pattern, output)
        
        if match:
            return {"choice": match.group(1)}
        
        # 如果没有找到精确匹配，回退到更宽松的解析
        return FormatPatternParser().parse(output)

class OutputParser:
    """输出解析器工厂，用于获取适合特定输出的解析器"""
    
    _parsers: Dict[str, Type[BaseOutputParser]] = {
        "json": JSONOutputParser,
        "format": FormatPatternParser
    }
    
    @classmethod
    def register_parser(cls, name: str, parser_class: Type[BaseOutputParser]) -> None:
        """
        注册新的解析器类型
        
        Args:
            name: 解析器名称
            parser_class: 解析器类
        """
        cls._parsers[name] = parser_class
    
    @classmethod
    def get_parser(cls, parser_type: str) -> BaseOutputParser:
        """
        获取指定类型的解析器实例
        
        Args:
            parser_type: 解析器类型名称
            
        Returns:
            解析器实例
            
        Raises:
            ValueError: 如果指定的解析器类型不存在
        """
        if parser_type not in cls._parsers:
            raise ValueError(f"未知的解析器类型: {parser_type}")
        
        return cls._parsers[parser_type]()
    
    @classmethod
    def get_parser_for_output(cls, output: str) -> BaseOutputParser:
        """
        根据输出内容自动选择合适的解析器，首选JSON解析器
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            最合适的解析器实例
        """
        # 首选使用JSON解析器
        return cls.get_parser("json")
    
    @classmethod
    def parse(cls, output: str) -> Dict[str, Any]:
        """
        直接解析输出，无需手动选择解析器
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            解析后的字典
        """
        parser = cls.get_parser_for_output(output)
        return parser.parse(output) 