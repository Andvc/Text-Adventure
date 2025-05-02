# 文字冒险游戏引擎

这是一个基于Python的文字冒险游戏引擎，通过AI驱动故事生成，提供沉浸式的文字冒险体验。本文档将以`simple_loop`为例，说明各模块如何协同工作。

## 项目结构

```
Text Adventure/
├── ai/                # AI模块 - 提示词处理与API交互
├── data/              # 数据模块 - 游戏数据管理
├── storyline/         # 故事线模块 - 故事模板与剧情生成
├── save/              # 游戏存档目录
├── test/              # 测试文件目录
└── main.py            # 游戏主入口
```

## 模块协同示例：simple_loop

`simple_loop`是一个简单的循环故事生成示例，展示了各模块如何协同工作：

### 1. 数据模块：管理游戏状态

```python
# 创建存档数据
save_data = {
    "id": "test_save",
    "character": {
        "name": "李逍遥",
        "level": "炼气期"
    },
    "world": "奇幻大陆",
    "summary": "少年李逍遥无意间获得一本古老的功法，开始了修仙之路。",
    "story": "李逍遥来到了一座神秘的洞穴前，传说里面藏有珍贵的宝物。",
    "selected_choice": "探索洞穴"
}

# 保存到文件
save_data("test_save", "character", save_data)
```

数据模块负责：
- 管理存档数据的创建、读取和更新
- 提供统一的数据访问接口
- 处理数据持久化

### 2. 故事线模块：定义故事结构

```json
// storyline/templates/simple_loop.json
{
  "template_id": "simple_loop",
  "prompt_segments": [
    "## 角色信息",
    "(主角名称：{character.name})",
    "(主角身份：{character.level})",
    "(所处世界：{world})",
    "",
    "## 故事背景",
    "(故事概要：{summary})",
    "",
    "## 当前情况",
    "(当前事件：{story})",
    "(玩家选择了：{selected_choice})",
    "",
    "## 生成要求",
    "<基于玩家的选择 '{selected_choice}'，描述接下来发生的新事件...>",
    "[story=\"*\"]",
    "",
    "<根据新发生的事件，生成三个不同的选择...>",
    "[choice1=\"*\",choice2=\"*\",choice3=\"*\"]",
    "",
    "<根据新的事件发展，更新故事梗概...>",
    "[summary=\"*\"]"
  ],
  "output_storage": {
    "story": "story",
    "summary": "summary",
    "choice1": "choice1",
    "choice2": "choice2",
    "choice3": "choice3"
  }
}
```

故事线模块负责：
- 定义故事模板的结构
- 管理提示片段和输出格式
- 处理存储映射

### 3. AI模块：生成故事内容

```python
# 初始化提示词处理器
prompt_processor = PromptProcessor()

# 构建提示词
segments = [
    "(主角名称：{character.name})",
    "(主角身份：{character.level})",
    "(所处世界：{world})",
    "(故事概要：{summary})",
    "(当前事件：{story})",
    "(玩家选择了：{selected_choice})",
    "<基于玩家的选择 '{selected_choice}'，描述接下来发生的新事件...>",
    "[story=\"*\"]",
    "<根据新发生的事件，生成三个不同的选择...>",
    "[choice1=\"*\",choice2=\"*\",choice3=\"*\"]",
    "<根据新的事件发展，更新故事梗概...>",
    "[summary=\"*\"]"
]

# 生成提示词
prompt = prompt_processor.build_prompt(segments)

# 调用AI生成内容
response = api_connector.generate(prompt)
```

AI模块负责：
- 处理提示词片段
- 构建完整的提示词
- 调用AI API生成内容
- 解析AI响应

### 4. 完整流程示例

```python
# 1. 初始化管理器
manager = StorylineManager()

# 2. 加载存档
save_data = load_save("test_save", "character")

# 3. 生成新故事
success = manager.generate_story("test_save", "simple_loop")

if success:
    # 4. 获取生成的内容
    story = get_save_value("story", save_data)
    choices = [
        get_save_value("choice1", save_data),
        get_save_value("choice2", save_data),
        get_save_value("choice3", save_data)
    ]
    
    # 5. 显示故事和选择
    print(f"故事内容: {story}")
    print(f"选项1: {choices[0]}")
    print(f"选项2: {choices[1]}")
    print(f"选项3: {choices[2]}")
    
    # 6. 更新选择
    save_data["selected_choice"] = choices[0]
    save_data("test_save", "character", save_data)
```

## 模块职责

### 数据模块 (data/)
- 管理游戏状态和存档数据
- 提供统一的数据访问接口
- 处理数据持久化
- 支持嵌套数据结构和数组

### 故事线模块 (storyline/)
- 定义和管理故事模板
- 处理提示片段和输出格式
- 管理存储映射
- 生成故事内容

### AI模块 (ai/)
- 处理提示词构建
- 管理AI API调用
- 解析AI响应
- 提供错误处理

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置API密钥
```bash
echo "DEEPSEEK_API_KEY=your_api_key" > .env
```

3. 运行测试示例
```bash
python test/test_simple_loop_cycle.py
```

## 最佳实践

1. **数据管理**
   - 使用有意义的字段名
   - 保持数据结构的一致性
   - 及时保存更新

2. **模板设计**
   - 使用清晰的标题和分组
   - 提供详细的背景信息
   - 明确指定输出格式

3. **提示词编写**
   - 使用具体的指令和要求
   - 提供足够的上下文信息
   - 添加必要的约束条件

## 注意事项

1. 确保所有占位符存在于存档数据中
2. 存储映射的字段必须与输出格式匹配
3. 生成失败时会返回False，需要检查错误信息
4. 建议在生成前备份存档数据 