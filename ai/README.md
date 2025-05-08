# AI提示词处理与API交互模块

一个轻量级、高度可定制的Python模块，用于构建AI提示词、调用大模型API并解析结构化响应。本模块专注于简化AI大模型交互流程，确保输出为结构化格式。

## 目录

- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [API调用](#api调用)
- [响应解析系统](#响应解析系统)
- [错误处理](#错误处理)
- [高级用法](#高级用法)
- [实际应用场景](#实际应用场景)
- [性能优化](#性能优化)
- [文件结构](#文件结构)
- [占位符系统](#占位符系统)
- [变更日志](#变更日志)
- [测试与贡献](#测试与贡献)

## 快速开始

### 安装

```bash
# 克隆仓库
git clone <仓库地址>
cd <项目目录>

# 安装依赖
pip install -r requirements.txt

# 设置API密钥（二选一）
export API_KEY=your_api_key  # 命令行方式
# 或在项目根目录创建.env文件，添加：API_KEY=your_api_key
```

### 快速开始脚本

以下是一个完整的入门脚本示例，复制后即可运行：

```python
# quick_start.py
from prompt_processor import PromptProcessor
from api_connector import AIModelConnector
from output_parsers import OutputParser

def main():
    # 1. 创建提示词处理器
    processor = PromptProcessor()
    
    # 2. 定义提示片段
    segments = [
        "(场景是古代中国)",
        "<描述一位武侠人物>",
        "[name=\"*\", appearance=\"*\", skills=\"*\", famous_saying=\"*\"]"
    ]
    
    # 3. 构建提示词
    prompt = processor.build_prompt(segments)
    print("生成的提示词:")
    print(prompt)
    
    # 4. 调用API (如果没有API密钥，会提示错误)
    try:
        connector = AIModelConnector()  # 自动读取环境变量或.env文件中的API密钥
        response = connector.call_api(prompt)
        print("\nAPI响应:")
        print(response)
        
        # 5. 解析结果
        result = OutputParser.parse(response)
        print("\n解析后的结构化数据:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 6. 使用数据
        print("\n武侠人物信息:")
        print(f"姓名: {result['name']}")
        print(f"外貌: {result['appearance']}")
        print(f"绝技: {result['skills']}")
        print(f"名言: {result['famous_saying']}")
        
    except Exception as e:
        print(f"\n出错: {str(e)}")
        print("提示: 请确保已设置有效的API密钥，或使用模拟测试模式")

if __name__ == "__main__":
    main()
```

### 基础示例

简化版本的基础用法：

```python
from prompt_processor import PromptProcessor
from api_connector import AIModelConnector
from output_parsers import OutputParser

# 1. 创建提示词
processor = PromptProcessor()
segments = [
    "(角色是探险家)",
    "<描述一段探险经历>",
    "[adventure=\"*\"]"
]
prompt = processor.build_prompt(segments)

# 2. 调用API
connector = AIModelConnector(api_key="your_api_key")  # 或省略api_key使用环境变量
response = connector.call_api(prompt)

# 3. 解析结果
result = OutputParser.parse(response)
print(f"探险故事: {result['adventure']}")
```

## 核心功能

### 提示词构建

提供三种提示词元素，可灵活组合：
- `(信息)` - 提供上下文信息，用括号包围
- `<内容>` - 指定生成内容的类型，用尖括号包围
- `[字段="*"]` - 定义输出格式，用方括号包围

每种元素的作用：
- **信息元素**(括号): 为模型提供背景信息，不直接影响输出结构
- **内容元素**(尖括号): 描述需要生成的内容类型
- **格式元素**(方括号): 定义输出的结构化格式

### 提示词构建详解

#### 1. 单字段输出

```python
segments = [
    "(用户喜欢科幻内容)",
    "<描述一个未来城市>",
    "[city_description=\"*\"]"
]
```

#### 2. 多字段输出

```python
segments = [
    "(场景是现代都市)",
    "<设计一个虚构的科技产品>",
    "[product_name=\"*\", product_description=\"*\", target_users=\"*\", pricing=\"*\"]"
]
```

#### 3. 内容-格式配对

为每个输出字段单独指定内容要求：

```python
segments = [
    "(场景是城堡)",
    "<描述王子的外貌>",        # 对应character字段
    "[character=\"*\"]",
    "<描述王子的性格特点>",    # 对应personality字段
    "[personality=\"*\"]",
    "<描述王子拥有的魔法能力>", # 对应magic_power字段
    "[magic_power=\"*\"]"
]
```

#### 4. 混合使用单字段和多字段

```python
segments = [
    "(游戏设定)",
    "<讲述故事背景>",
    "[background=\"*\"]",
    "<设计主要角色>",
    "[hero_name=\"*\", hero_class=\"*\", hero_skills=\"*\"]",
]
```

#### 5. 自定义模板

如果默认模板不能满足需求，可以自定义模板：

```python
custom_template = """【角色扮演】请假装你是一位经验丰富的{output_content}专家，
基于以下信息提供专业建议：
{{
  "{output_key}": "请在这里填入中文-{output_content}"
}}
用户提供的情境: {input_info}"""

processor = PromptProcessor(template=custom_template)
```

## API调用

### 基本调用

```python
connector = AIModelConnector(api_key="your_api_key")  # 可选，不提供则从环境变量读取
response = connector.call_api(prompt)
```

### 自定义参数

```python
response = connector.call_api(
    prompt,
    temperature=0.7,     # 控制输出随机性
    max_tokens=500,      # 最大输出长度
    top_p=0.9,           # 控制采样范围
    stream=False         # 是否流式输出
)
```

## 响应解析系统

### 强大的解析架构

本模块采用分层设计的解析系统，包含三个主要组件：

1. **基础解析器接口(`BaseOutputParser`)**: 
   - 定义统一的解析接口
   - 支持同步与异步解析方法
   - 提供类型安全的泛型实现

2. **专用解析器实现**:
   - `JSONOutputParser`: 专门处理JSON格式输出，具有强大的错误恢复能力
   - `FormatPatternParser`: 处理键值对格式的文本，作为JSON解析的补充方案

3. **解析器工厂(`OutputParser`)**:
   - 提供统一的解析入口
   - 根据输入内容智能选择合适的解析器
   - 支持注册自定义解析器
   - 内置错误处理和回退机制

### 智能JSON提取与修复

`JSONOutputParser`具有多层级的错误处理能力：

1. **标准JSON解析**: 首先尝试直接解析，处理标准格式的JSON
2. **清理与提取**: 移除非JSON内容，从文本中提取JSON部分
3. **错误修复**: 修复常见的JSON错误，如缺失引号、尾部逗号等
4. **格式回退**: 当JSON解析失败时，尝试使用`FormatPatternParser`解析
5. **错误信息保留**: 始终保留原始输出，便于调试

### 非JSON格式的处理

`FormatPatternParser`可以识别多种非JSON格式的键值对：

- `key=value` 格式
- `key: value` 格式
- 带引号的键值对 `"key"="value"`

同时能够自动将字符串值转换为适当的类型（数字、布尔值、空值）。

### 解析多种输出格式

```python
# 标准JSON
standard_json = '{"name": "张三", "age": 28}'
result = OutputParser.parse(standard_json)  # {'name': '张三', 'age': 28}

# 代码块内的JSON
markdown_json = '''
回复如下：
```json
{"name": "张三", "age": 28}
```
希望对您有帮助！
'''
result = OutputParser.parse(markdown_json)  # {'name': '张三', 'age': 28}

# 带前缀的JSON
prefixed_json = "AI助手的回复:\n{\"name\": \"张三\", \"age\": 28}"
result = OutputParser.parse(prefixed_json)  # {'name': '张三', 'age': 28}

# 错误格式的JSON（缺少引号）
malformed_json = '{"name": "张三", age: 28}'
result = OutputParser.parse(malformed_json)  # {'name': '张三', 'age': 28}

# 非JSON键值对
key_value_pairs = 'name="张三" age=28 is_student=true score=95.5'
result = OutputParser.parse(key_value_pairs)  # {'name': '张三', 'age': 28, 'is_student': True, 'score': 95.5}
```

### 指定解析器类型

```python
# 强制使用JSON解析器
result = OutputParser.parse(response, parser_type="json")

# 强制使用格式模式解析器
result = OutputParser.parse(response, parser_type="format")
```

### 异步解析

```python
# 异步解析输出
async def process_response():
    response = await connector.async_call_api(prompt)
    result = await OutputParser.async_parse(response)
    return result
```

## 错误处理

新的解析系统内置了强大的错误处理能力：

```python
try:
    response = connector.call_api(prompt)
    result = OutputParser.parse(response)
    
    # 检查是否存在错误
    if "error" in result:
        print(f"解析过程中出现错误: {result['error']}")
        print(f"错误详情: {result.get('error_details', '无详情')}")
        print(f"原始输出: {result.get('raw_output', '无原始输出')[:100]}...")
    else:
        # 正常处理结果
        print(f"解析成功: {result}")
except Exception as e:
    print(f"处理过程中出错: {str(e)}")
```

## 高级用法

### 响应处理

解析器能够智能处理各种格式的响应：

| 输入类型 | 示例 | 解析结果 |
|---------|------|---------|
| 标准JSON | `{"name": "张三", "age": 28}` | `{'name': '张三', 'age': 28}` |
| 代码块中的JSON | ```json\n{"name": "张三"}\n``` | `{'name': '张三'}` |
| 带前缀文本的JSON | `回答如下:\n{"name": "张三"}` | `{'name': '张三'}` |
| 格式错误的JSON | `{"name": "张三", age: 28}` | `{'name': '张三', 'age': 28}` |
| 非JSON键值对 | `name="张三" age=28` | `{'name': '张三', 'age': 28}` |

### 自定义解析器

可以创建并注册自定义解析器：

```python
from output_parsers import BaseOutputParser, OutputParser
from typing import Dict, Any

class CSVOutputParser(BaseOutputParser[Dict[str, Any]]):
    def parse(self, output: str) -> Dict[str, Any]:
        # CSV解析逻辑
        result = {}
        
        # 简单的CSV解析实现
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

# 使用自定义解析器
result = OutputParser.parse(response, parser_type="csv")
```

## 实际应用场景

### 1. 内容生成

生成一个产品描述：

```python
segments = [
    "(行业是智能家居)",
    "(目标用户是科技爱好者)",
    "<描述一款创新的智能产品>",
    "[product_name=\"*\", description=\"*\", key_features=\"*\", price_range=\"*\"]"
]
```

### 2. 信息提取

从文本中提取结构化信息：

```python
segments = [
    "(输入文本：周杰伦，1979年1月18日出生于台湾省新北市，祖籍福建省泉州市永春县，华语流行乐男歌手、音乐人、演员、导演、编剧等)",
    "<从文本中提取人物信息>",
    "[name=\"*\", birth_date=\"*\", birth_place=\"*\", occupation=\"*\"]"
]
```

### 3. 交互式对话

创建一个简单的对话系统：

```python
# 存储对话历史
conversation_history = []

# 处理用户输入
while True:
    user_input = input("请输入问题(输入q退出): ")
    if user_input.lower() == 'q':
        break
    
    # 构建提示词
    segments = [
        f"(对话历史: {conversation_history})",
        f"(用户问题: {user_input})",
        "<回答用户问题>",
        "[answer=\"*\"]"
    ]
    
    prompt = processor.build_prompt(segments)
    response = connector.call_api(prompt)
    result = OutputParser.parse(response)
    
    # 显示回答
    print(f"\nAI回答: {result['answer']}\n")
    
    # 更新对话历史
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": result['answer']})
```

### 4. 决策树

创建一个带选择的故事：

```python
segments = [
    "(世界观是奇幻中世纪)",
    "<创建一个故事开头>",
    "[story_intro=\"*\"]",
    "<提供三个可能的故事发展选项>",
    "[option1=\"*\", option2=\"*\", option3=\"*\"]"
]
```

## 性能优化

当需要生成大量提示词时，可以重用同一个处理器实例：

```python
processor = PromptProcessor()
prompts = []

for topic in topics:
    segments = [
        f"(主题是{topic})",
        "<生成内容>",
        "[content=\"*\"]"
    ]
    prompts.append(processor.build_prompt(segments))
```

## 文件结构

- `prompt_processor.py`: 提示词处理核心类
- `api_connector.py`: API连接器
- `output_parsers.py`: 输出解析器
- `config.py`: 配置文件
- `comprehensive_test.py`: 完整测试模块

## 占位符系统

### 占位符功能概述

提示词处理器支持多种占位符格式，用于在提示词中引用数据：

#### 1. 基本占位符

```
{key} - 直接引用存档中的顶级字段
{key.subkey} - 引用嵌套对象中的字段
```

示例：
```python
segments = [
    "(角色名称: {character.name})",
    "(技能: {skills[0]})",
    "<生成角色描述>",
    "[description=\"*\"]"
]
```

#### 2. 嵌套占位符 (新功能)

支持在占位符内部嵌入其他占位符，实现动态引用：

```
{character.{field_name}} - 引用字段名称由变量决定的属性
{{primary_key}.{secondary_key}[{index}]} - 复杂的嵌套引用，包含变量字段和索引
```

示例：
```python
save_data = {
    "active_field": "name",
    "character": {
        "name": "艾里克",
        "title": "魔法师"
    }
}

# 使用嵌套占位符
segments = [
    "(角色属性: {character.{active_field}})",  # 结果为: (角色属性: 艾里克)
    "<生成角色介绍>",
    "[intro=\"*\"]"
]
```

#### 3. 文本数据引用 (新功能)

可以直接引用data/text目录下的JSON文件中的数据：

```
{text;file_name;path} - 从data/text/file_name.json文件中引用指定路径的数据
```

示例：
```python
# 假设data/text/worlds.json包含世界设定数据
segments = [
    "(当前世界: {text;worlds;current_world.name})",
    "(科技水平: {text;worlds;technology_levels[2].name})",
    "<生成世界描述>",
    "[world_description=\"*\"]"
]
```

#### 4. 数组处理 (改进功能)

提供了更强大的数组处理能力：

```
{key.array[0]} - 引用数组的特定索引
{key.array} - 引用整个数组
{key.array[{index}]} - 使用变量作为索引引用数组元素
```

示例：
```python
save_data = {
    "current_skill_index": 1,
    "skills": ["火球术", "冰霜新星", "闪电链"]
}

segments = [
    "(所有技能: {skills})",
    "(主要技能: {skills[0]})",
    "(当前技能: {skills[{current_skill_index}]})",  # 结果为: (当前技能: 冰霜新星)
    "<生成技能描述>",
    "[skill_description=\"*\"]"
]
```

### 占位符使用最佳实践

1. **避免过深嵌套** - 虽然支持嵌套占位符，但过度嵌套会降低可读性
2. **预先验证数据** - 确保引用的路径在数据中存在，避免运行时错误
3. **合理使用文本数据引用** - 将常用配置和设定放在data/text目录，实现数据复用
4. **注意数组边界** - 引用数组元素时确保索引在有效范围内
5. **使用默认值** - 在关键处理逻辑中为可能缺失的数据提供默认值

## 变更日志

### 2024-05-21
- **增强的占位符系统**：
  - 添加嵌套占位符支持，允许在占位符内部使用其他占位符，实现动态引用
  - 添加文本数据引用功能，支持从data/text目录下的JSON文件中读取数据
  - 改进数组处理，支持变量索引和完整数组引用
  - 统一占位符处理逻辑，确保在所有模块中一致的行为
  - 限制嵌套层级最多20层，防止无限递归
- **内部改进**：
  - 重构`_replace_placeholders`方法，提高占位符处理的鲁棒性
  - 添加错误处理和日志记录功能
  - 优化性能，减少不必要的数据处理

## 测试与贡献

本项目包含全面的测试模块：

```bash
# 运行所有测试
python3 comprehensive_test.py

# 使用模拟响应进行测试（不调用真实API）
python3 comprehensive_test.py --mock

# 运行特定测试
python3 comprehensive_test.py --tests prompt parser pairing
```

欢迎贡献代码或提出建议！如有问题，请提交Issue或联系维护者。 