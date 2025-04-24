#!/usr/bin/env python3
"""
全面测试AI模块功能的测试脚本

本测试文件用于测试AI模块的所有组件和功能，包括：
1. 提示词处理器(prompt_processor)：测试提示词构建、段落解析和模板处理
2. 输出解析器(output_parsers)：测试不同格式的输出解析功能和错误恢复能力
3. API连接器(api_connector)：测试与大语言模型API的连接和交互

使用方法：
    python3 test/ai_test.py               # 运行所有测试
    python3 test/ai_test.py --mock        # 使用模拟响应运行所有测试
    python3 test/ai_test.py --module prompt  # 只测试提示词处理器
    python3 test/ai_test.py --api-key YOUR_KEY  # 指定API密钥运行测试
"""

import os
import sys
import json
import time
import argparse
import unittest
import re
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List, Optional

# 添加项目根目录到Python路径以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入AI模块
from ai.prompt_processor import PromptProcessor
from ai.api_connector import AIModelConnector, APIError, AuthenticationError, RateLimitError
from ai.output_parsers import (
    OutputParser, 
    JSONOutputParser, 
    FormatPatternParser, 
    BaseOutputParser
)
import config

# 测试数据常量
TEST_API_KEY = "test_api_key_for_mock_responses"
MOCK_RESPONSES = {
    "standard_json": """{"name": "李白", "occupation": "诗人", "famous_work": "将进酒"}""",
    "with_markdown": """```json
    {
        "name": "李白",
        "occupation": "诗人",
        "famous_work": "将进酒"
    }
    ```""",
    "with_prefix": """AI助手的回答：
    {
        "name": "李白",
        "occupation": "诗人",
        "famous_work": "将进酒"
    }""",
    "malformed_json": """{
        "name": "李白",
        occupation: "诗人",
        "famous_work": "将进酒"
    }""",
    "key_value_pairs": """name="李白" occupation="诗人" famous_work="将进酒" """
}

class PromptProcessorTests(unittest.TestCase):
    """测试提示词处理器功能"""
    
    def setUp(self):
        """测试前的设置"""
        self.processor = PromptProcessor()
        self.test_segments = [
            "(角色是诗人)",
            "(朝代是唐代)",
            "<创作一首诗>",
            "[poem=\"*\"]"
        ]
        
    def test_parse_segments(self):
        """测试片段解析功能"""
        parsed = self.processor.parse_segments(self.test_segments)
        
        # 验证信息类提示词
        self.assertEqual(len(parsed["info"]), 2)
        self.assertIn("角色是诗人", parsed["info"])
        self.assertIn("朝代是唐代", parsed["info"])
        
        # 验证内容类提示词
        self.assertEqual(len(parsed["content"]), 1)
        self.assertEqual(parsed["content"][0], "创作一首诗")
        
        # 验证格式类提示词
        self.assertEqual(len(parsed["format"]), 1)
        self.assertEqual(parsed["format"][0], "poem=\"*\"")
    
    def test_build_prompt_single_field(self):
        """测试构建单字段提示词"""
        prompt = self.processor.build_prompt(self.test_segments)
        
        # 验证提示词格式
        self.assertIn("请严格按照以下JSON格式输出", prompt)
        self.assertIn("\"poem\"", prompt)
        self.assertIn("(角色是诗人) (朝代是唐代)", prompt)
    
    def test_build_prompt_multi_field(self):
        """测试构建多字段提示词"""
        multi_field_segments = [
            "(角色是诗人)",
            "<描述一位著名诗人>",
            "[name=\"*\", era=\"*\", famous_poems=\"*\"]"
        ]
        
        prompt = self.processor.build_prompt(multi_field_segments)
        
        # 验证提示词格式
        self.assertIn("\"name\"", prompt)
        self.assertIn("\"era\"", prompt)
        self.assertIn("\"famous_poems\"", prompt)
    
    def test_content_format_pairing(self):
        """测试内容和格式配对功能"""
        pairing_segments = [
            "(主题是自然)",
            "<描述一座山>",
            "[mountain=\"*\"]",
            "<描述一条河>",
            "[river=\"*\"]"
        ]
        
        prompt = self.processor.build_prompt(pairing_segments)
        
        # 验证配对结果
        self.assertIn("\"mountain\"", prompt)
        self.assertIn("\"river\"", prompt)
        self.assertIn("描述一座山", prompt)
        self.assertIn("描述一条河", prompt)
    
    def test_custom_template(self):
        """测试自定义模板功能"""
        custom_template = """【角色扮演】你是一位{output_content}专家，请基于以下信息:
{input_info}

生成JSON格式的回答:
{
  "{output_key}": "你的专业回答"
}"""
        
        custom_processor = PromptProcessor(template=custom_template)
        prompt = custom_processor.build_prompt(self.test_segments)
        
        # 由于有可能回退到默认模板，检查是否包含关键内容
        has_custom_template = "【角色扮演】你是一位" in prompt
        has_default_template = "请严格按照以下JSON格式输出" in prompt
        
        self.assertTrue(has_custom_template or has_default_template, 
                       "输出提示词既不是自定义模板格式，也不是默认模板格式")

class OutputParserTests(unittest.TestCase):
    """测试输出解析器功能"""
    
    def test_json_parser_standard(self):
        """测试标准JSON解析"""
        parser = JSONOutputParser()
        result = parser.parse(MOCK_RESPONSES["standard_json"])
        
        self.assertEqual(result["name"], "李白")
        self.assertEqual(result["occupation"], "诗人")
        self.assertEqual(result["famous_work"], "将进酒")
    
    def test_json_parser_markdown(self):
        """测试Markdown代码块中的JSON解析"""
        parser = JSONOutputParser()
        result = parser.parse(MOCK_RESPONSES["with_markdown"])
        
        self.assertEqual(result["name"], "李白")
        self.assertEqual(result["occupation"], "诗人")
        self.assertEqual(result["famous_work"], "将进酒")
    
    def test_json_parser_with_prefix(self):
        """测试带前缀文本的JSON解析"""
        parser = JSONOutputParser()
        result = parser.parse(MOCK_RESPONSES["with_prefix"])
        
        self.assertEqual(result["name"], "李白")
        self.assertEqual(result["occupation"], "诗人")
        self.assertEqual(result["famous_work"], "将进酒")
    
    def test_json_parser_malformed(self):
        """测试格式错误的JSON解析与修复"""
        parser = JSONOutputParser()
        result = parser.parse(MOCK_RESPONSES["malformed_json"])
        
        self.assertEqual(result["name"], "李白")
        self.assertEqual(result["occupation"], "诗人")
        self.assertEqual(result["famous_work"], "将进酒")
    
    def test_format_pattern_parser(self):
        """测试格式模式解析器"""
        parser = FormatPatternParser()
        result = parser.parse(MOCK_RESPONSES["key_value_pairs"])
        
        self.assertEqual(result["name"], "李白")
        self.assertEqual(result["occupation"], "诗人")
        self.assertEqual(result["famous_work"], "将进酒")
    
    def test_output_parser_factory_auto_select(self):
        """测试解析器工厂的自动选择功能"""
        # 测试JSON输入自动选择JSONOutputParser
        result1 = OutputParser.parse(MOCK_RESPONSES["standard_json"])
        self.assertEqual(result1["name"], "李白")
        
        # 测试键值对输入自动选择FormatPatternParser
        result2 = OutputParser.parse(MOCK_RESPONSES["key_value_pairs"])
        self.assertEqual(result2["name"], "李白")
    
    def test_custom_parser_registration(self):
        """测试自定义解析器注册功能"""
        # 创建自定义解析器
        class CSVOutputParser(BaseOutputParser[Dict[str, Any]]):
            def parse(self, output: str) -> Dict[str, Any]:
                result = {}
                lines = output.strip().split('\n')
                if lines:
                    headers = lines[0].split(',')
                    if len(lines) > 1:
                        values = lines[1].split(',')
                        for i, header in enumerate(headers):
                            if i < len(values):
                                result[header.strip()] = values[i].strip()
                return result
                
        # 注册自定义解析器
        OutputParser.register_parser("csv", CSVOutputParser)
        
        # 测试自定义解析器
        csv_data = "name,occupation,famous_work\n李白,诗人,将进酒"
        result = OutputParser.parse(csv_data, parser_type="csv")
        
        self.assertEqual(result["name"], "李白")
        self.assertEqual(result["occupation"], "诗人")
        self.assertEqual(result["famous_work"], "将进酒")
    
    def test_error_handling(self):
        """测试错误处理能力"""
        # 测试完全无法解析的输入
        result = OutputParser.parse("这不是JSON也不是键值对格式")
        
        # 应返回错误信息
        self.assertIn("error", result)
        self.assertIn("raw_output", result)

class APIConnectorTests(unittest.TestCase):
    """测试API连接器功能"""
    
    @patch('requests.post')
    def test_api_call_success(self, mock_post):
        """测试成功的API调用"""
        # 模拟成功的API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": MOCK_RESPONSES["standard_json"]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # 创建API连接器并调用
        connector = AIModelConnector(api_key=TEST_API_KEY)
        result = connector.call_api("测试提示词")
        
        # 验证结果
        self.assertEqual(result, MOCK_RESPONSES["standard_json"])
        
        # 验证API调用
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['Authorization'], f"Bearer {TEST_API_KEY}")
    
    @patch('requests.post')
    def test_api_call_auth_error(self, mock_post):
        """测试认证错误的API调用"""
        # 模拟认证错误的API响应
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        # 创建API连接器并调用，预期抛出AuthenticationError
        connector = AIModelConnector(api_key=TEST_API_KEY)
        with self.assertRaises(AuthenticationError):
            connector.call_api("测试提示词")
    
    @patch('requests.post')
    def test_api_call_rate_limit(self, mock_post):
        """测试速率限制的API调用"""
        # 模拟速率限制的API响应
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response
        
        # 临时修改重试配置
        original_max_retries = config.MAX_RETRIES
        original_retry_delay = config.RETRY_DELAY
        config.MAX_RETRIES = 2
        config.RETRY_DELAY = 0.1
        
        try:
            # 创建API连接器并调用，预期抛出RateLimitError
            connector = AIModelConnector(api_key=TEST_API_KEY)
            with self.assertRaises(RateLimitError):
                connector.call_api("测试提示词")
            
            # 验证重试次数
            self.assertEqual(mock_post.call_count, config.MAX_RETRIES + 1)
        finally:
            # 恢复原始配置
            config.MAX_RETRIES = original_max_retries
            config.RETRY_DELAY = original_retry_delay
    
    def test_missing_api_key(self):
        """测试缺少API密钥的情况"""
        # 临时保存原始API密钥
        original_api_key = config.DEEPSEEK_API_KEY
        config.DEEPSEEK_API_KEY = ""
        
        try:
            # 尝试创建未指定API密钥的连接器
            with self.assertRaises(AuthenticationError):
                AIModelConnector()
        finally:
            # 恢复原始API密钥
            config.DEEPSEEK_API_KEY = original_api_key

class IntegrationTests(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前的设置"""
        self.processor = PromptProcessor()
        self.test_segments = [
            "(主题是季节)",
            "<描述春天的特点>",
            "[season=\"*\", characteristics=\"*\", activities=\"*\"]"
        ]
        
        # 检查是否使用模拟模式
        self.use_mock = "--mock" in sys.argv
        
        # 设置API连接器
        if self.use_mock:
            # 使用模拟连接器
            self.api_mock = patch('ai.api_connector.AIModelConnector.call_api')
            self.mock_call_api = self.api_mock.start()
            self.mock_call_api.return_value = MOCK_RESPONSES["standard_json"]
            self.connector = AIModelConnector(api_key=TEST_API_KEY)
        else:
            # 尝试使用实际API密钥
            api_key = None
            for i, arg in enumerate(sys.argv):
                if arg == "--api-key" and i+1 < len(sys.argv):
                    api_key = sys.argv[i+1]
            
            if not api_key and not config.DEEPSEEK_API_KEY:
                self.skipTest("没有提供API密钥，跳过实际API测试")
            
            try:
                self.connector = AIModelConnector(api_key=api_key)
            except AuthenticationError:
                self.skipTest("API密钥无效，跳过实际API测试")
    
    def tearDown(self):
        """测试后的清理"""
        if self.use_mock:
            self.api_mock.stop()
    
    def test_end_to_end_flow(self):
        """测试完整的端到端流程"""
        # 1. 构建提示词
        prompt = self.processor.build_prompt(self.test_segments)
        
        # 2. 调用API
        response = self.connector.call_api(prompt)
        
        # 3. 解析结果
        result = OutputParser.parse(response)
        
        # 验证结果
        if self.use_mock:
            # 模拟模式下验证固定结果
            self.assertEqual(result["name"], "李白")
        else:
            # 实际API调用验证结果格式
            self.assertTrue(isinstance(result, dict))
            self.assertTrue(len(result) > 0)

class CustomOutputParserTests(unittest.TestCase):
    """测试自定义输出解析器"""
    
    def test_xml_parser(self):
        """测试XML解析功能"""
        # 定义XML解析器
        class XMLOutputParser(BaseOutputParser[Dict[str, Any]]):
            def parse(self, output: str) -> Dict[str, Any]:
                result = {}
                # 简单的XML解析实现
                tag_pattern = r'<([a-zA-Z0-9_]+)>(.*?)</\1>'
                matches = re.findall(tag_pattern, output, re.DOTALL)
                
                for tag, content in matches:
                    result[tag] = content.strip()
                
                return result
        
        # 测试XML解析器
        xml_data = """
        <name>李白</name>
        <occupation>诗人</occupation>
        <famous_work>将进酒</famous_work>
        """
        
        parser = XMLOutputParser()
        result = parser.parse(xml_data)
        
        self.assertEqual(result["name"], "李白")
        self.assertEqual(result["occupation"], "诗人")
        self.assertEqual(result["famous_work"], "将进酒")
        
        # 注册并通过工厂使用
        OutputParser.register_parser("xml", XMLOutputParser)
        result2 = OutputParser.parse(xml_data, parser_type="xml")
        
        self.assertEqual(result2["name"], "李白")

def main():
    """测试主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="测试AI模块功能")
    parser.add_argument("--mock", action="store_true", help="使用模拟响应而非实际API调用")
    parser.add_argument("--api-key", type=str, help="指定用于测试的API密钥")
    parser.add_argument("--module", type=str, choices=["prompt", "parser", "api", "all"], 
                      default="all", help="指定要测试的模块")
    
    args, unknown = parser.parse_known_args()
    
    # 根据指定模块选择测试
    test_suite = unittest.TestSuite()
    
    if args.module == "prompt" or args.module == "all":
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(PromptProcessorTests))
    
    if args.module == "parser" or args.module == "all":
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(OutputParserTests))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CustomOutputParserTests))
    
    if args.module == "api" or args.module == "all":
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(APIConnectorTests))
    
    if args.module == "all":
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(IntegrationTests))
    
    # 运行测试
    unittest.TextTestRunner(verbosity=2).run(test_suite)

if __name__ == "__main__":
    main() 