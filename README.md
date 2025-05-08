# 文字冒险游戏引擎

这是一个基于Python的文字冒险游戏引擎，通过AI驱动故事生成，提供沉浸式的文字冒险体验。本文档将展示系统的核心功能和使用方法。

## 项目结构

```
Text Adventure/
├── ai/                # AI模块 - 提示词处理与API交互
├── data/              # 数据模块 - 游戏数据管理
├── storyline/         # 故事线模块 - 故事模板与剧情生成
├── save/              # 游戏存档目录
├── test/              # 测试文件目录
└── editor/            # JSON编辑器 - 配置文件可视化编辑工具（可选）
```

## 高级功能演示

本游戏引擎支持多种高级功能，为创建复杂、动态的文字冒险游戏提供了强大的工具。以下是关键功能的示例：

### 1. 嵌套占位符系统

嵌套占位符允许在占位符内部嵌入其他占位符，实现动态引用：

```json
// 存档数据
{
  "active_field": "name",
  "character": {
    "name": "李白",
    "title": "诗仙"
  },
  "skill_index": 2,
  "skills": ["剑法", "飞行", "饮酒"]
}

// 使用嵌套占位符的模板
"prompt_segments": [
  "(角色属性: {character.{active_field}})",  // 结果: (角色属性: 李白)
  "(选中技能: {skills[{skill_index}]})",  // 结果: (选中技能: 饮酒)
  "<根据角色属性和技能生成描述>"
]
```

嵌套占位符使模板更具灵活性，可以根据游戏状态动态选择要显示的数据。

### 2. 文本数据引用

可以直接从`data/text`目录下的JSON文件中读取数据：

```json
// data/text/eras.json
{
  "eras": [
    {
      "id": "builders_era",
      "name": "建构者文明",
      "era_number": 1,
      "key_features": ["最早掌握维度工程", "建造了连接各界的魔法通道"]
    },
    {
      "id": "star_spirit_era",
      "name": "星灵文明",
      "era_number": 2,
      "key_features": ["将原能凝聚成永恒星体", "创造了'魔法天穹系统'"]
    }
  ]
}

// 使用文本数据引用的模板
"prompt_segments": [
  "(当前纪元: {text;eras;eras[0].name})",  // 结果: (当前纪元: 建构者文明)
  "(纪元编号: 第{text;eras;eras[0].era_number}纪元)",  // 结果: (纪元编号: 第1纪元)
  "(下一个纪元: {text;eras;eras[1].name})",  // 结果: (下一个纪元: 星灵文明)
  "<基于纪元背景生成故事>"
]
```

这允许将游戏世界设定、物品数据等分离到专门的数据文件中，使模板更加清晰和可维护。

### 3. 动态索引与数组处理

系统支持灵活的数组处理和变量索引：

```json
// 存档数据
{
  "current_era_index": 1,
  "player_choice": 2,
  "available_actions": ["探索", "对话", "战斗", "休息"]
}

// 使用动态索引的模板
"prompt_segments": [
  "(当前纪元: {text;eras;eras[{current_era_index}].name})",  // 动态选择纪元
  "(玩家选择的行动: {available_actions[{player_choice}]})",  // 结果: (玩家选择的行动: 战斗)
  "(所有可用行动: {available_actions})",  // 返回整个数组
  "<根据玩家选择的行动生成事件>"
]
```

变量索引使您可以动态引用数组元素，增强了模板的灵活性。

### 4. 完整模板示例

以下是结合多个高级功能的完整模板示例，可在`storyline/templates/example.json`中找到：

```json
{
  "template_id": "example",
  "name": "高级功能演示模板",
  "description": "展示嵌套占位符系统、文本数据引用和数组处理功能",
  "version": "1.0",
  "author": "系统",
  "created_at": "2025-05-08",
  "tags": [
    "示例",
    "嵌套占位符",
    "文本数据引用",
    "数组处理"
  ],
  "prompt_segments": [
    "(角色名称: {character.name})",
    "(角色身份: {character.{identity_field}})",
    "(当前纪元: {text;eras;eras[{current_era_index}].name})",
    "(纪元编号: 第{text;eras;eras[{current_era_index}].era_number}纪元)",
    "(主要特征: {text;eras;eras[{current_era_index}].key_features[0]}, {text;eras;eras[{current_era_index}].key_features[1]})",
    "(当前地点: {location})",
    "(可用技能: {skills})",
    "(选中技能: {skills[{active_skill_index}]})",
    "(能力等级: {text;power_levels;levels[{power_level}].name})",
    "(能力描述: {text;power_levels;levels[{power_level}].universal_description})",
    "<根据以上信息，创建一个角色背景故事。故事应该：\n1. 反映角色在当前纪元的生活和经历\n2. 展示角色的身份和社会地位\n3. 解释角色如何获得当前的能力等级\n4. 描述角色与所处地点的关系\n5. 提及角色掌握的技能，特别是当前选中的技能>",
    "[character_background=\"string\"]",
    "<基于角色背景，描述角色当前面临的场景和挑战。场景应该：\n1. 与当前地点相关\n2. 提供使用角色技能的机会\n3. 反映纪元特征\n4. 包含环境描述和氛围营造>",
    "[current_scene=\"string\"]",
    "<提供三个选项，让角色应对当前场景。每个选项应该：\n1. 提供明显不同的行动方向\n2. 至少有一个选项与选中技能相关\n3. 反映角色能力等级的限制和可能性\n4. 可能带来不同的后果>",
    "[option1=\"string\", option2=\"string\", option3=\"string\"]"
  ],
  "output_storage": {
    "character_background": "character_background",
    "current_scene": "current_scene",
    "option1": "option1",
    "option2": "option2",
    "option3": "option3"
  },
  "prompt_template": "你是一位专业的角色背景与场景设计师，擅长创建符合世界观设定的内容。请根据以下信息，创建引人入胜的角色背景和场景。\n\n## 背景信息\n{input_info}\n\n## 输出格式\n请严格按照以下JSON格式回复，注意三引号中的内容是指令，你需要根据指令生成内容：\n{format}\n\n## 注意事项\n1. 保持内容的一致性和连贯性\n2. 充分利用提供的世界观和角色信息\n3. 确保场景与角色背景相呼应\n4. 创建有趣且多样的选择，引导不同的故事发展方向"
}
```

这个模板使用了多种高级功能：
- 嵌套占位符：`{character.{identity_field}}`
- 文本数据引用：`{text;eras;eras[{current_era_index}].name}`
- 动态数组索引：`{skills[{active_skill_index}]}`
- 完整数组引用：`{skills}`

并且包含了完整的`prompt_template`，定义了AI生成内容的指令和格式。

### 5. 动态故事生成流程

下面是一个完整的动态故事生成流程示例，可通过运行`test/test_example.py`测试：

```python
# 初始化故事线管理器
manager = StorylineManager()

# 加载或创建存档
save_name = "example"
current_save = {
    "id": save_name,
    "character": {
        "name": "艾里克",
        "profession": "学者"
    },
    "identity_field": "profession",
    "current_era_index": 4,  # 对应万象帝国
    "location": "魔法学院图书馆",
    "skills": ["火球术", "魔法护盾", "光照术", "元素感知", "魔法解析"],
    "active_skill_index": 2,
    "power_level": 3
}

# 使用模板生成故事（模板使用嵌套占位符和文本数据引用）
success = manager.generate_story(save_name, "example")

if success:
    # 获取生成的内容
    updated_save = load_save("character", save_name)
    
    # 显示新的故事内容
    print(f"角色背景: {updated_save['character_background']}")
    print(f"当前场景: {updated_save['current_scene']}")
    
    # 显示可用选项
    for i, option in enumerate([updated_save['option1'], updated_save['option2'], updated_save['option3']], 1):
        print(f"选项{i}: {option}")
```

## 模块功能介绍

### 数据模块 (data/)
- 管理游戏状态和存档数据
- 提供统一的数据访问接口
- 处理数据持久化
- 支持嵌套数据结构和数组
- 提供文本数据文件访问功能

### 故事线模块 (storyline/)
- 定义和管理故事模板
- 处理提示片段和输出格式
- 支持嵌套占位符和文本数据引用
- 管理存储映射
- 生成故事内容

### AI模块 (ai/)
- 处理提示词构建
- 支持复杂占位符解析
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

3. 运行示例演示
```bash
python test/test_example.py
```

4. 使用JSON编辑器（可选）
```bash
python3 -m editor
```

## 最佳实践

1. **数据管理**
   - 使用有意义的字段名
   - 将共享数据存储在data/text目录下
   - 保持数据结构的一致性
   - 及时保存更新

2. **模板设计**
   - 使用清晰的标题和分组
   - 利用嵌套占位符实现动态内容
   - 充分利用文本数据引用减少重复
   - 提供详细的背景信息
   - 明确指定输出格式

3. **占位符使用**
   - 嵌套占位符: `{character.{field_name}}` 
   - 文本数据引用: `{text;file_name;path}`
   - 动态数组索引: `{array[{index}]}`
   - 完整数组引用: `{array}`

## 注意事项

1. 确保所有占位符存在于存档数据或文本数据文件中
2. 存储映射的字段必须与输出格式匹配
3. 避免过深的嵌套，以保持模板的可读性
4. 生成失败时会返回False，需要检查错误信息
5. 建议在生成前备份存档数据 