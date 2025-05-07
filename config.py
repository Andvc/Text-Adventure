"""
配置文件，用于存储API密钥和其他全局设置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件中的环境变量
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# API密钥（优先从环境变量获取）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# 模型配置
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"

# API端点
DEEPSEEK_API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

# 提示词模板 - 带有三引号描述的JSON格式
# 注意：这里使用了双大括号 {{ 和 }} 来在格式化字符串中表示单个大括号
DEFAULT_PROMPT_TEMPLATE = """请严格按照以下JSON格式输出，不要添加任何其他内容或解释。
三引号中的内容是指令，您需要根据指令生成内容：

{json_format}

请确保输出是有效的JSON格式，包含所有指定的字段。
提供给你的信息: {input_info}"""

# 超时设置
API_TIMEOUT = 30  # 秒

# 重试设置
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒