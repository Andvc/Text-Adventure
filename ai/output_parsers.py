"""
输出解析器模块，用于解析和提取AI响应中的结构化内容
"""

import re
import json
import asyncio
from typing import Dict, Any, List, Optional, Type, Union, TypeVar, Generic, Callable
from abc import ABC, abstractmethod

T = TypeVar('T')

class BaseOutputParser(ABC, Generic[T]):
    """
    输出解析器基类
    
    负责将AI模型的原始文本输出转换为结构化数据。
    所有自定义解析器都应该继承这个基类。
    """
    
    @abstractmethod
    def parse(self, output: str) -> T:
        """
        解析输出内容
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            解析后的结构化内容
        
        Raises:
            ValueError: 当解析失败且无法恢复时抛出
        """
        pass
    
    async def async_parse(self, output: str) -> T:
        """
        异步解析输出内容
        
        默认实现是在事件循环中运行同步parse方法
        自定义解析器可以覆盖此方法以提供真正的异步实现
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            解析后的结构化内容
        """
        return await asyncio.to_thread(self.parse, output)
    
    @classmethod
    def get_parser_type(cls) -> str:
        """
        获取解析器类型
        
        Returns:
            解析器类型名称
        """
        return cls.__name__.replace("OutputParser", "").lower()

class JSONOutputParser(BaseOutputParser[Dict[str, Any]]):
    """
    JSON格式输出解析器
    
    专门用于解析返回JSON格式的AI响应。具有强大的错误恢复能力，
    可以从多种不规范的JSON格式中提取有效内容。
    """
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        解析JSON格式的输出
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            解析后的JSON对象
            
        Raises:
            ValueError: 当JSON解析完全失败且无法恢复时抛出
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
                    # 尝试修复常见的JSON错误
                    fixed_json = self._attempt_json_repair(json_text)
                    if fixed_json:
                        try:
                            return json.loads(fixed_json)
                        except json.JSONDecodeError:
                            pass
            
            # 如果所有JSON解析方法都失败，尝试使用格式解析器
            format_result = FormatPatternParser().parse(output)
            if format_result:
                return format_result
                
            # 如果都失败了，返回一个错误信息
            error_msg = f"JSON解析失败: {str(e)}\n原始输出: {output[:100]}..."
            print(error_msg)
            return {"error": "无法解析JSON输出", "raw_output": output, "error_details": str(e)}
    
    def _clean_output(self, output: str) -> str:
        """
        清理输出，移除可能的非JSON内容
        
        Args:
            output: 原始输出文本
            
        Returns:
            清理后的可能包含有效JSON的文本
        """
        output = output.strip()
        
        # 移除可能的代码块标记 (多种格式)
        output = re.sub(r'```(?:json|javascript|js)?\s*', '', output)
        output = re.sub(r'```\s*$', '', output)
        
        # 移除开头的可能解释文本，寻找第一个有效的JSON开始字符 ({[)
        json_start = re.search(r'[{[]', output)
        if json_start:
            output = output[json_start.start():]
        
        # 移除结尾的可能解释文本，确保JSON正确闭合
        json_end = None
        # 找到最后一个有效的JSON结束字符 (}])
        for i in range(len(output) - 1, -1, -1):
            if output[i] in '}]':
                matching_char = '{' if output[i] == '}' else '['
                # 简单检查括号是否匹配
                if output.count(matching_char) >= output.count(output[i]):
                    json_end = i
                    break
        
        if json_end is not None and json_end < len(output) - 1:
            output = output[:json_end + 1]
            
        return output
    
    def _extract_json(self, output: str) -> Optional[str]:
        """
        尝试从文本中提取JSON部分
        
        Args:
            output: 原始输出文本
            
        Returns:
            提取的可能包含JSON的文本，如果未找到则返回None
        """
        # 改进的JSON提取模式，支持多层嵌套
        json_patterns = [
            # 标准对象模式
            r'({[^{}]*(?:{[^{}]*(?:{[^{}]*}[^{}]*)*}[^{}]*)*})',
            # 数组模式
            r'(\[[^\[\]]*(?:\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\][^\[\]]*)*\])'
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, output, re.DOTALL)
            if match:
                return match.group(1)
        
        return None
    
    def _attempt_json_repair(self, json_text: str) -> Optional[str]:
        """
        尝试修复常见的JSON错误
        
        Args:
            json_text: 可能包含错误的JSON文本
            
        Returns:
            修复后的JSON文本，如果无法修复则返回None
        """
        # 1. 尝试修复缺失的引号
        json_text = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', json_text)
        
        # 2. 尝试修复尾部逗号
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # 3. 尝试修复缺失的引号在值周围
        json_text = re.sub(r':\s*([a-zA-Z0-9_]+)(\s*[,}])', r': "\1"\2', json_text)
        
        return json_text

class FormatPatternParser(BaseOutputParser[Dict[str, Any]]):
    """
    格式模式解析器
    
    当JSON解析失败时的后备解析器，通过正则表达式识别键值对。
    可以识别多种常见的键值对格式。
    """
    
    def __init__(self, pattern: Optional[str] = None):
        """
        初始化格式模式解析器
        
        Args:
            pattern: 可选，自定义正则表达式模式
        """
        # 默认模式匹配 key=value, key: value, "key"="value" 等常见格式
        self.pattern = pattern if pattern else r'["\']?([^"\'=:]+)["\']?\s*[=:]\s*["\']?([^"\',}\]]*)["\']?[,}]?'
    
    def parse(self, output: str) -> Dict[str, Any]:
        """
        使用正则表达式模式解析输出
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            解析后的字典，键为属性名，值为属性值
        """
        result = {}
        # 先清理输出，移除可能的代码块等干扰
        cleaned_output = re.sub(r'```.*?```', '', output, flags=re.DOTALL)
        cleaned_output = cleaned_output.strip()
        
        # 尝试匹配键值对
        matches = re.finditer(self.pattern, cleaned_output)
        
        for match in matches:
            if len(match.groups()) >= 2:
                key = match.group(1).strip()
                value = match.group(2).strip()
                if key and key not in result:  # 避免重复键
                    result[key] = value
        
        # 尝试把值转换为适当的类型
        self._convert_values(result)
        
        return result
    
    def _convert_values(self, data: Dict[str, Any]) -> None:
        """
        尝试将字符串值转换为合适的类型
        
        Args:
            data: 要处理的数据字典
        """
        for key, value in data.items():
            if isinstance(value, str):
                # 尝试转换为数字
                if value.isdigit():
                    data[key] = int(value)
                elif re.match(r'^-?\d+(\.\d+)?$', value):
                    data[key] = float(value)
                # 尝试转换为布尔值
                elif value.lower() in ('true', 'yes'):
                    data[key] = True
                elif value.lower() in ('false', 'no'):
                    data[key] = False
                # 尝试转换为None
                elif value.lower() in ('none', 'null'):
                    data[key] = None

class OutputParser:
    """
    输出解析器工厂
    
    提供统一的接口来选择和使用合适的解析器。
    支持注册自定义解析器和智能解析器选择。
    """
    
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
        根据输出内容自动选择合适的解析器
        
        智能选择最适合处理给定输出的解析器。
        
        Args:
            output: AI模型的原始输出
            
        Returns:
            最合适的解析器实例
        """
        # 检查输出是否看起来像JSON
        if re.search(r'^\s*[{\[]', output) or '{"' in output or '":' in output:
            return cls.get_parser("json")
        # 检查是否看起来像键值对格式
        elif re.search(r'[a-zA-Z_]+\s*[=:]\s*["\']?[^"\']*["\']?', output):
            return cls.get_parser("format")
        # 默认使用JSON解析器
        return cls.get_parser("json")
    
    @classmethod
    def parse(cls, output: str, parser_type: Optional[str] = None) -> Dict[str, Any]:
        """
        直接解析输出
        
        Args:
            output: AI模型的原始输出
            parser_type: 可选，指定使用的解析器类型
            
        Returns:
            解析后的字典
            
        Raises:
            ValueError: 当指定的解析器类型不存在时抛出
        """
        if parser_type:
            parser = cls.get_parser(parser_type)
        else:
            parser = cls.get_parser_for_output(output)
        
        try:
            return parser.parse(output)
        except Exception as e:
            # 如果指定的解析器失败，尝试使用其他解析器
            if parser_type:
                try:
                    # 回退到智能选择
                    fallback_parser = cls.get_parser_for_output(output)
                    if fallback_parser.get_parser_type() != parser.get_parser_type():
                        return fallback_parser.parse(output)
                except Exception:
                    pass
            
            # 如果所有尝试都失败，返回错误信息
            return {"error": "解析失败", "raw_output": output, "error_details": str(e)}
    
    @classmethod
    async def async_parse(cls, output: str, parser_type: Optional[str] = None) -> Dict[str, Any]:
        """
        异步解析输出
        
        Args:
            output: AI模型的原始输出
            parser_type: 可选，指定使用的解析器类型
            
        Returns:
            解析后的字典
        """
        if parser_type:
            parser = cls.get_parser(parser_type)
        else:
            parser = cls.get_parser_for_output(output)
        
        try:
            return await parser.async_parse(output)
        except Exception as e:
            # 如果指定的解析器失败，尝试使用其他解析器
            if parser_type:
                try:
                    # 回退到智能选择
                    fallback_parser = cls.get_parser_for_output(output)
                    if fallback_parser.get_parser_type() != parser.get_parser_type():
                        return await fallback_parser.async_parse(output)
                except Exception:
                    pass
            
            # 如果所有尝试都失败，返回错误信息
            return {"error": "异步解析失败", "raw_output": output, "error_details": str(e)} 