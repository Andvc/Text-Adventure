"""
API连接器模块，用于与DeepSeek-Chat API交互
"""

import requests
import json
import time
from typing import Dict, Any, Optional, Union
import config

class APIError(Exception):
    """API调用错误"""
    pass

class AuthenticationError(APIError):
    """认证错误"""
    pass

class RateLimitError(APIError):
    """速率限制错误"""
    pass

class AIModelConnector:
    """DeepSeek-Chat API连接器"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        初始化DeepSeek API连接器
        
        Args:
            api_key: API密钥，如果不提供则从配置文件获取
            model_name: 模型名称，如果不提供则从配置文件获取默认值
        """
        # 设置API密钥
        self.api_key = api_key if api_key else config.DEEPSEEK_API_KEY
        
        # 检查API密钥
        if not self.api_key:
            raise AuthenticationError("DeepSeek API密钥未设置")
        
        # 设置模型名称
        self.model_name = model_name if model_name else config.DEFAULT_DEEPSEEK_MODEL
        
        # 设置API端点
        self.api_endpoint = config.DEEPSEEK_API_ENDPOINT
    
    def _prepare_headers(self) -> Dict[str, str]:
        """
        准备API请求头
        
        Returns:
            请求头字典
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        return headers
    
    def _prepare_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        准备API请求负载
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数，如温度、最大标记数等
            
        Returns:
            请求负载字典
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "请以有效的JSON格式输出响应，不要添加任何额外的文本、解释或前缀/后缀。确保JSON格式正确，可以被JSON解析器直接解析。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "response_format": {"type": "json_object"}  # 如果模型支持，指定JSON响应格式
        }
        
        # 添加其他特定模型的参数
        if kwargs.get("stream", False):
            payload["stream"] = True
        
        return payload
    
    def call_api(self, prompt: str, **kwargs) -> str:
        """
        调用DeepSeek API
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数，如温度、最大标记数等
            
        Returns:
            模型响应文本
            
        Raises:
            APIError: API调用错误
            AuthenticationError: 认证错误
            RateLimitError: 速率限制错误
        """
        headers = self._prepare_headers()
        payload = self._prepare_payload(prompt, **kwargs)
        
        # 重试逻辑
        retries = 0
        while retries <= config.MAX_RETRIES:
            try:
                response = requests.post(
                    self.api_endpoint,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=config.API_TIMEOUT
                )
                
                # 检查响应状态
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                
                # 处理错误
                elif response.status_code == 401:
                    raise AuthenticationError("API密钥无效或已过期")
                elif response.status_code == 429:
                    if retries < config.MAX_RETRIES:
                        retries += 1
                        time.sleep(config.RETRY_DELAY)
                        continue
                    else:
                        raise RateLimitError("API速率限制，请稍后再试")
                else:
                    error_msg = f"API调用失败，状态码: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg += f", 错误: {error_data.get('error', {}).get('message', '未知错误')}"
                    except:
                        pass
                    raise APIError(error_msg)
            
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                if retries < config.MAX_RETRIES:
                    retries += 1
                    time.sleep(config.RETRY_DELAY)
                    continue
                else:
                    raise APIError(f"API请求异常: {str(e)}")
        
        # 如果所有重试都失败
        raise APIError("达到最大重试次数，API调用失败") 