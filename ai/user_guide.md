# AI提示词处理与API交互模块使用指南

这份指南将帮助您快速上手使用AI提示词处理与API交互模块，无需了解内部实现细节。

## 快速开始脚本

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

## 安装与配置

### 1. 安装模块

```bash
# 克隆仓库（或直接下载）
git clone <仓库地址>
cd <项目目录>

# 安装依赖
pip install -r requirements.txt
```

### 2. 设置API密钥（二选一）

```bash
# 方法一：环境变量
export DEEPSEEK_API_KEY=your_api_key

# 方法二：创建.env文件
echo "DEEPSEEK_API_KEY=your_api_key" > .env
```

## 基本用法

### 完整工作流程示例

```python
from prompt_processor import PromptProcessor
from api_connector import AIModelConnector
from output_parsers import OutputParser

# 1. 创建提示词
processor = PromptProcessor()
segments = [
    "(角色是探险家)",
    "<描述一段探险经历>",
    "{adventure=\"*\"}"
]
prompt = processor.build_prompt(segments)

# 2. 调用API
connector = AIModelConnector()  # 会自动从环境变量或.env文件读取API密钥
response = connector.call_api(prompt)

# 3. 解析结果
result = OutputParser.parse(response)
print(f"探险故事: {result['adventure']}")
```

## 提示词构建详解

提示词构建使用三种元素，用不同符号包围：
- `(信息)` - 背景信息，不影响输出结构
- `<内容>` - 需要生成的内容类型
- `[字段="*"]` - 输出的JSON结构

### 1. 单字段输出

```python
segments = [
    "(用户喜欢科幻内容)",
    "<描述一个未来城市>",
    "[city_description=\"*\"]"
]
```

### 2. 多字段输出

```python
segments = [
    "(场景是现代都市)",
    "<设计一个科技产品>",
    "[product_name=\"*\", product_description=\"*\", target_users=\"*\", pricing=\"*\"]"
]
```

### 3. 内容-格式配对（为不同字段指定不同内容）

```python
segments = [
    "(场景是城堡)",
    "<描述王子的外貌>",         # 对应character字段
    "[character=\"*\"]",
    "<描述王子的性格特点>",     # 对应personality字段
    "[personality=\"*\"]",
    "<描述王子拥有的魔法能力>", # 对应magic_power字段
    "[magic_power=\"*\"]"
]
```

### 4. 混合使用单字段和多字段

```python
segments = [
    "(游戏设定)",
    "<讲述故事背景>",
    "[background=\"*\"]",
    "<设计主要角色>",
    "[hero_name=\"*\", hero_class=\"*\", hero_skills=\"*\"]",
]
```

### 5. 自定义模板

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

## 输出解析

解析器能够处理各种JSON格式的输出，包括不规范的输出：

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

## 错误处理

```python
try:
    response = connector.call_api(prompt)
    result = OutputParser.parse(response)
except Exception as e:
    print(f"处理过程中出错: {str(e)}")
    
    # 错误恢复逻辑
    if "API" in str(e):
        print("API调用失败，使用备用方案")
        # 备用逻辑
    elif "解析" in str(e):
        print("解析失败，尝试备用解析")
        # 备用解析逻辑
```

## 实际应用场景示例

### 1. 内容生成

生成一个产品描述：

```python
segments = [
    "(行业是智能家居)",
    "(目标用户是科技爱好者)",
    "<描述一款创新的智能产品>",
    "{product_name=\"*\", description=\"*\", key_features=\"*\", price_range=\"*\"}"
]
```

### 2. 信息提取

从文本中提取结构化信息：

```python
segments = [
    "(输入文本：周杰伦，1979年1月18日出生于台湾省新北市，祖籍福建省泉州市永春县，华语流行乐男歌手、音乐人、演员、导演、编剧等)",
    "<从文本中提取人物信息>",
    "{name=\"*\", birth_date=\"*\", birth_place=\"*\", occupation=\"*\"}"
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
        "{answer=\"*\"}"
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
    "{story_intro=\"*\"}",
    "<提供三个可能的故事发展选项>",
    "{option1=\"*\", option2=\"*\", option3=\"*\"}"
]

# 构建提示词并调用API
prompt = processor.build_prompt(segments)
response = connector.call_api(prompt)
result = OutputParser.parse(response)

# 展示故事
print(result["story_intro"])
print("\n选择下一步:")
print(f"1. {result['option1']}")
print(f"2. {result['option2']}")
print(f"3. {result['option3']}")

# 获取用户选择
choice = int(input("请选择(1-3): "))
selected_option = result[f"option{choice}"]

# 继续故事
next_segments = [
    f"(已有故事: {result['story_intro']})",
    f"(用户选择: {selected_option})",
    "<根据用户选择继续故事>",
    "{story_continuation=\"*\"}",
    "<提供新的选择>",
    "{new_option1=\"*\", new_option2=\"*\"}"
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
        "{content=\"*\"}"
    ]
    prompts.append(processor.build_prompt(segments))
```

## 输出示例

所有字段均会输出中文内容，例如：

```json
{
  "character_name": "影刃",
  "character_class": "刺客",
  "main_skill": "暗影突袭"
}
```

或多字段复杂输出：

```json
{
  "story": "在一个风雨交加的夜晚，冒险者酒馆里挤满了寻求庇护的旅人。吟游诗人坐在壁炉旁，开始讲述一个关于古老宝藏的传说。据说，宝藏被藏在遥远的迷雾山脉中，由一条巨龙守护。许多勇敢的冒险者前去寻找，但无一归来。今晚，酒馆里有两位冒险者对此表现出了浓厚的兴趣。",
  "choice1": "接受吟游诗人的挑战，组织一支队伍前往迷雾山脉寻找宝藏。",
  "choice2": "认为这只是一个传说，不值得冒险，选择继续在酒馆里享受温暖的夜晚。"
}
```

## 注意事项

1. 确保所有输出字段使用双引号，遵循JSON格式
2. API调用可能会产生费用，请合理控制调用频率
3. 处理敏感信息时注意信息安全
4. 大模型输出可能会有不确定性，建议加入适当的内容检查
5. 所有模板中使用了"请在这里填入中文-"的提示，确保模型输出中文内容

## 测试与验证

使用内置的测试模块验证功能：

```bash
# 使用模拟测试（不调用实际API）
python3 comprehensive_test.py --mock

# 测试特定功能
python3 comprehensive_test.py --mock --tests prompt parser
```

