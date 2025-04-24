# AI提示词处理与API交互模块

一个轻量级、高度可定制的Python模块，用于构建AI提示词、调用DeepSeek-Chat API并解析JSON格式响应。本模块专注于简化AI大模型交互流程，确保输出为结构化JSON格式。

> **使用指南说明**:
> - 如果您只需要快速上手使用本模块，建议直接阅读 [user_guide.md](user_guide.md) 文件
> - 如果您想了解完整的代码实现细节和架构，请继续阅读本文档

## 目录

- [用户指南](#用户指南)
- [快速开始](#快速开始)
- [完整工作流程](#完整工作流程)
- [核心功能](#核心功能)
- [高级用法](#高级用法)
- [实际应用场景](#实际应用场景)
- [参考](#参考)

## 用户指南

项目提供了一个单独的用户指南文件 [user_guide.md](user_guide.md)，它提供了模块的"黑箱操作"方法，不涉及内部实现细节，专注于如何使用这个模块。用户指南包含：

- 安装与配置方法
- 基本工作流程
- 提示词构建技巧
- 输出解析方法
- 实用场景示例
- 完整可运行示例脚本

如果您只关心如何使用本模块而不需要了解内部工作原理，建议直接阅读用户指南。

## 快速开始

### 安装

```bash
# 克隆仓库
git clone <仓库地址>
cd <项目目录>

# 安装依赖
pip install -r requirements.txt

# 设置API密钥（二选一）
export DEEPSEEK_API_KEY=your_api_key  # 命令行方式
# 或在项目根目录创建.env文件，添加：DEEPSEEK_API_KEY=your_api_key
```

### 基础示例

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

## 完整工作流程

本模块的工作流程分为三个主要步骤：提示词构建、API调用和结果解析。下面是一个完整示例，展示从输入到输出的全过程：

### 1. 提示词构建

首先，使用`PromptProcessor`类来构建结构化的提示词：

```python
from prompt_processor import PromptProcessor

# 创建处理器
processor = PromptProcessor()

# 定义输入片段
segments = [
    "(场景是城堡)",
    "<描述王子的外貌>",        # 对应character字段
    "[character=\"*\"]",
    "<描述王子的性格特点>",    # 对应personality字段
    "[personality=\"*\"]",
    "<描述王子拥有的魔法能力>", # 对应magic_power字段
    "[magic_power=\"*\"]"
]

# 构建提示词
prompt = processor.build_prompt(segments)
print("生成的提示词:")
print(prompt)
```

**输出结果**：
```
生成的提示词:
请严格按照以下JSON格式输出，不要添加任何其他内容或解释：

{
  "pirate_name": "请在这里填入中文-pirate name-描述一位传奇海盗船长",
  "appearance": "请在这里填入中文-appearance-描述一位传奇海盗船长",
  "famous_deeds": "请在这里填入中文-famous deeds-描述一位传奇海盗船长"
}

请确保输出是有效的JSON格式，包含所有指定的字段。
提供给你的信息: (场景是海盗船) (时间是黄金时代)
```

### 2. API调用

接着，使用`AIModelConnector`类调用DeepSeek API：

```python
from api_connector import AIModelConnector

# 创建API连接器
connector = AIModelConnector(api_key="your_api_key")

# 调用API
response = connector.call_api(prompt)
print("\nAPI响应:")
print(response)
```

**输出结果**：
```
API响应:
{
  "pirate_name": "黑胡子爱德华·蒂奇",
  "appearance": "高大魁梧的身材，浓密的黑色胡须几乎覆盖了整个面部，常身着深色长外套，头戴三角帽，腰间别着几把精制手枪和一把弯刀。他眼神凶狠，脸上的伤疤诉说着无数战斗历史。",
  "famous_deeds": "封锁查尔斯顿港口勒索整座城市、率领\"安妮女王复仇号\"击败多艘军舰、在加勒比海域建立海盗王国、掠夺超过40艘商船并积累巨额财富、最后在血战中英勇战死，他的头颅被挂在军舰上作为海盗末路的警示。"
}
```

### 3. 结果解析

最后，使用`OutputParser`类解析响应结果：

```python
from output_parsers import OutputParser

# 解析结果
result = OutputParser.parse(response)
print("\n解析后的结构化数据:")
import json
print(json.dumps(result, indent=2, ensure_ascii=False))

# 使用解析结果
print("\n提取海盗信息:")
print(f"海盗名称: {result['pirate_name']}")
print(f"外貌描述: {result['appearance'][:50]}...")
print(f"著名事迹数量: {len(result['famous_deeds'].split('、'))}")
```

**输出结果**：
```
解析后的结构化数据:
{
  "pirate_name": "黑胡子爱德华·蒂奇",
  "appearance": "高大魁梧的身材，浓密的黑色胡须几乎覆盖了整个面部，常身着深色长外套，头戴三角帽，腰间别着几把精制手枪和一把弯刀。他眼神凶狠，脸上的伤疤诉说着无数战斗历史。",
  "famous_deeds": "封锁查尔斯顿港口勒索整座城市、率领\"安妮女王复仇号\"击败多艘军舰、在加勒比海域建立海盗王国、掠夺超过40艘商船并积累巨额财富、最后在血战中英勇战死，他的头颅被挂在军舰上作为海盗末路的警示。"
}

提取海盗信息:
海盗名称: 黑胡子爱德华·蒂奇
外貌描述: 高大魁梧的身材，浓密的黑色胡须几乎覆盖了整个面部...
著名事迹数量: 5
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
- **格式元素**(方括号): 定义输出的JSON结构

### 内容格式配对

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

**工作原理**:
1. 系统识别相邻的`<内容>`和`[格式]`对
2. 将内容描述与对应字段匹配
3. 生成清晰的提示词指导

**生成的提示词**:
```json
{
  "character": "请在这里填入中文-描述王子的外貌",
  "personality": "请在这里填入中文-描述王子的性格特点",
  "magic_power": "请在这里填入中文-描述王子拥有的魔法能力"
}
```

**预期API响应**:
```json
{
  "character": "金发碧眼，高挑身材，面容姣好，经常身着蓝色王室服装，佩戴镶嵌蓝宝石的金色王冠，举止优雅而又不失亲和力。",
  "personality": "沉稳冷静，富有智慧，对王国充满责任感，但同时也有冒险精神和好奇心，愿意倾听民众声音，善于在压力下做出理性决策。",
  "magic_power": "能够控制冰雪元素，在危险时刻凝结出坚固的冰盾保护自己和他人，也能在节日庆典上创造出美丽的冰花和雪景，为王国带来奇观。"
}
```

### 多字段输出

在一个提示中请求多个相关字段：

```python
segments = [
    "(场景是现代都市)",
    "<设计一个虚构的科技产品>",
    "[product_name=\"*\", product_description=\"*\", target_users=\"*\", pricing=\"*\"]"
]
```

**工作原理**:
1. 系统识别单个内容描述对应多个输出字段
2. 为每个字段提供字段名和内容描述
3. 生成结构化提示词

**生成的提示词**:
```json
{
  "product_name": "请在这里填入中文-product name-设计一个虚构的科技产品",
  "product_description": "请在这里填入中文-product description-设计一个虚构的科技产品",
  "target_users": "请在这里填入中文-target users-设计一个虚构的科技产品",
  "pricing": "请在这里填入中文-pricing-设计一个虚构的科技产品"
}
```

**预期API响应**:
```json
{
  "product_name": "NeuroSync",
  "product_description": "一款可穿戴式脑波同步设备，通过贴在太阳穴的微型传感器捕捉脑电波活动，同步到手机应用。它能够分析使用者的注意力、放松度和创造力水平，并提供实时反馈和个性化建议。",
  "target_users": "知识工作者、创意专业人士、学生、冥想爱好者和任何希望提高专注力与创造力的人群。",
  "pricing": "基础版299美元，高级版499美元（含一年高级数据分析服务）。另提供每月9.99美元的订阅服务，包括高级数据分析和个性化建议。"
}
```

### 混合使用

可以灵活混合使用单字段和多字段格式：

```python
segments = [
    "(游戏设定)",
    "<讲述故事背景>",
    "{background=\"*\"}",
    "<设计主要角色>",
    "{hero_name=\"*\", hero_class=\"*\", hero_skills=\"*\"}",
]
```

**工作原理**:
1. 系统分别处理每对内容-格式配对
2. 对单字段和多字段采用不同的处理方式
3. 合并所有字段生成完整提示词

**生成的提示词**:
```json
{
  "background": "请在这里填入中文-讲述故事背景",
  "hero_name": "请在这里填入中文-hero name-设计主要角色",
  "hero_class": "请在这里填入中文-hero class-设计主要角色",
  "hero_skills": "请在这里填入中文-hero skills-设计主要角色"
}
```

**预期API响应**:
```json
{
  "background": "在远古的埃尔温大陆，魔法与科技并存，人类与各种奇幻生物共同生活。一千年前，黑暗魔王被封印，大陆迎来和平。然而近年来，封印开始松动，黑暗力量逐渐复苏，各地出现神秘事件和怪物袭击。",
  "hero_name": "艾莉亚·风行者",
  "hero_class": "元素猎手",
  "hero_skills": "风之箭（远程攻击）、自然感知（探测隐藏敌人）、元素融合（临时增强武器属性）、风翼术（短距离快速移动）"
}
```

### 自定义模板

可以完全自定义提示词模板：

```python
custom_template = """根据以下信息，生成符合JSON格式的响应：
{{
  "{output_key}": "{output_content}应当包含什么要素？"
}}
背景信息: {input_info}"""

processor = PromptProcessor(template=custom_template)
```

**实例演示**:
```python
custom_template = """【角色扮演】请假装你是一位经验丰富的{output_content}专家，基于以下信息提供专业建议：
{{
  "{output_key}": "请详细解释最佳方案和实施步骤"
}}
用户提供的情境: {input_info}"""

processor = PromptProcessor(template=custom_template)
segments = [
    "(家中有一只1岁的猫咪，经常抓挠家具)",
    "<宠物行为训练>",
    "{solution=\"*\"}"
]

prompt = processor.build_prompt(segments)
print(prompt)
```

**输出结果**:
```
【角色扮演】请假装你是一位经验丰富的宠物行为训练专家，基于以下信息提供专业建议：
{
  "solution": "请详细解释最佳方案和实施步骤"
}
用户提供的情境: (家中有一只1岁的猫咪，经常抓挠家具)
```

## 高级用法

### 响应处理

解析器能够智能处理各种JSON格式响应：

```python
# 标准JSON、代码块内JSON、带前缀文本的JSON都能正确解析
messy_response = """
AI助手的回复：
```json
{
  "answer": "这是答案",
  "confidence": "高"
}
```
希望对您有帮助！
"""

result = OutputParser.parse(messy_response)  # {'answer': '这是答案', 'confidence': '高'}
```

**解析能力演示**:

| 输入类型 | 示例 | 解析结果 |
|---------|------|---------|
| 标准JSON | `{"name": "张三", "age": 28}` | `{'name': '张三', 'age': 28}` |
| 代码块中的JSON | ```````json\n{"name": "张三"}\n```\n```` | `{'name': '张三'}` |
| 带前缀文本的JSON | `回答如下:\n{"name": "张三"}` | `{'name': '张三'}` |
| 带注释的JSON | `{"name": "张三", // 这是姓名\n"age": 28}` | `{'name': '张三', 'age': 28}` |

### 错误处理

```python
try:
    response = connector.call_api(prompt)
    result = OutputParser.parse(response)
except Exception as e:
    print(f"处理过程中出错: {str(e)}")
    
    # 可以尝试错误恢复
    if "API" in str(e):
        print("API调用失败，使用备用响应")
        result = {"error": str(e), "fallback_response": "备用内容"}
    elif "解析" in str(e):
        print("解析失败，尝试备用解析方法")
        from output_parsers import FormatPatternParser
        result = FormatPatternParser().parse(response)
```

## 实际应用场景

### 交互式故事生成

```python
segments = [
    "(世界观是奇幻中世纪)",
    "<创建一个故事开头>",
    "{story_intro=\"*\"}",
    "<提供三个可能的故事发展选项>",
    "{option1=\"*\", option2=\"*\", option3=\"*\"}"
]
```

**完整流程演示**:
```python
# 1. 构建提示词
prompt = processor.build_prompt(segments)

# 2. 调用API
response = connector.call_api(prompt)

# 3. 解析结果
result = OutputParser.parse(response)

# 4. 展示故事
print(result["story_intro"])
print("\n选择下一步:")
print(f"1. {result['option1']}")
print(f"2. {result['option2']}")
print(f"3. {result['option3']}")

# 5. 获取用户选择
choice = int(input("请选择(1-3): "))
selected_option = result[f"option{choice}"]

# 6. 继续故事
next_segments = [
    f"(已有故事: {result['story_intro']})",
    f"(用户选择: {selected_option})",
    "<根据用户选择继续故事>",
    "{story_continuation=\"*\"}",
    "<提供新的选择>",
    "{new_option1=\"*\", new_option2=\"*\"}"
]
```

### 结构化信息提取

```python
segments = [
    "(输入文本：周杰伦，1979年1月18日出生于台湾省新北市，祖籍福建省泉州市永春县，华语流行乐男歌手、音乐人、演员、导演、编剧等)",
    "<从文本中提取人物信息>",
    "{name=\"*\", birth_date=\"*\", birth_place=\"*\", occupation=\"*\"}"
]
```

**预期结果**:
```json
{
  "name": "周杰伦",
  "birth_date": "1979年1月18日",
  "birth_place": "台湾省新北市",
  "occupation": "华语流行乐男歌手、音乐人、演员、导演、编剧"
}
```

### 多轮对话管理

```python
# 第一轮对话
initial_segments = [
    "(用户是初学者)",
    "<解释Python基础概念>",
    "{explanation=\"*\", code_example=\"*\", practice_suggestion=\"*\"}"
]

prompt = processor.build_prompt(initial_segments)
response = connector.call_api(prompt)
result = OutputParser.parse(response)

# 存储对话历史
conversation_history = [
    {"role": "assistant", "content": json.dumps(result, ensure_ascii=False)}
]

# 第二轮对话
user_question = "如何使用循环？"
follow_up_segments = [
    f"(对话历史: {json.dumps(conversation_history, ensure_ascii=False)})",
    f"(用户问题: {user_question})",
    "<回答用户关于Python循环的问题>",
    "{explanation=\"*\", code_example=\"*\", practice_suggestion=\"*\"}"
]
```

## 参考

### 组件说明

- **PromptProcessor**: 提示词处理和构建
  - 解析输入片段
  - 配对内容和格式
  - 生成结构化提示词
  
- **AIModelConnector**: API连接和调用
  - 管理API密钥
  - 构建请求头和负载
  - 处理API错误和重试
  
- **OutputParser**: 响应解析和结构化
  - 智能识别JSON
  - 清洁非标准输出
  - 提取结构化数据

### 配置选项

在`config.py`中可配置：
- `DEEPSEEK_API_KEY`: API密钥
- `DEFAULT_DEEPSEEK_MODEL`: 默认使用的模型
- `DEFAULT_PROMPT_TEMPLATE`: 默认提示词模板
- `API_TIMEOUT`: API请求超时时间(默认30秒)
- `MAX_RETRIES`: 最大重试次数(默认3次)
- `RETRY_DELAY`: 重试间隔时间(默认2秒)

## 文件结构

- `prompt_processor.py`: 提示词处理核心类
- `api_connector.py`: API连接器
- `output_parsers.py`: 输出解析器
- `config.py`: 配置文件
- `comprehensive_test.py`: 完整测试模块
- `user_guide.md`: 用户使用指南，不涉及内部实现细节，专注于如何使用这个模块

## 测试模块

项目包含一个全面的测试模块 `comprehensive_test.py`，用于测试所有功能：

```bash
# 运行所有测试（默认使用真实API，会检测配置文件中的API密钥或提示输入）
python3 comprehensive_test.py

# 使用模拟响应进行测试（不调用真实API）
python3 comprehensive_test.py --mock

# 指定API密钥运行测试
python3 comprehensive_test.py --api-key YOUR_API_KEY

# 运行特定测试
python3 comprehensive_test.py --tests prompt parser pairing
```

### API密钥处理流程

测试模块会按以下顺序查找API密钥：
1. 命令行参数 `--api-key` 指定的密钥
2. 配置文件 `config.py` 或环境变量中的 `DEEPSEEK_API_KEY`
3. 提示用户手动输入（若以上两种方式未找到有效密钥）

如果最终未能获取有效的API密钥，将自动回退到模拟测试模式。

### 可用的测试类型

- `prompt`: 提示词处理器功能
- `api`: API连接器功能
- `parser`: 输出解析器功能  
- `pairing`: 内容格式配对功能
- `custom`: 自定义模板功能
- `complete`: 完整处理流程
- `error`: 错误处理功能
- `real`: 真实大模型调用 (需要API密钥)
- `examples`: README示例测试

## 贡献与支持

欢迎贡献代码或提出建议！如有问题，请提交Issue或联系维护者。 