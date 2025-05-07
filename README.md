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
└── editor/            # JSON编辑器 - 配置文件可视化编辑工具（可选）
```

## 模块协同示例：simple_loop

`simple_loop`是一个简单的循环故事生成示例，展示了各模块如何协同工作：

### 1. 数据模块：管理游戏状态

```python
# 创建存档数据
save_data = {
    "id": "test_save",
    "era": {
        "name": "魔法纪元",
        "era_number": 3,
        "key_features": ["魔法", "冒险", "神秘"],
        "dominant_races": ["人类", "精灵", "矮人"],
        "magic_system": "元素魔法",
        "technology_level": "中世纪"
    },
    "character_info": {
        "name": "李逍遥",
        "race": "人类",
        "identity": "见习法师"
    },
    "current_location": "魔法学院",
    "current_state": "正在学习基础魔法"
}

# 保存到文件
save_data("test_save", save_data)
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
  "name": "简单循环",
  "description": "生成基本的游戏循环内容，包括场景描述和选项",
  "version": "1.0",
  "author": "系统",
  "created_at": "2024-05-05",
  "tags": [
    "游戏循环",
    "场景",
    "选项"
  ],
  "prompt_segments": [
    "(纪元名称: {era.name})",
    "(纪元编号: 第{era.era_number}纪元)",
    "(主要特征: {era.key_features_joined})",
    "(主导种族: {era.dominant_races_joined})",
    "(魔法体系: {era.magic_system})",
    "(技术水平: {era.technology_level})",
    "(角色信息: {character_info})",
    "(当前位置: {current_location})",
    "(当前状态: {current_state})",
    "<根据以上信息，生成一个游戏场景。场景应该：\n1. 符合纪元背景和设定\n2. 考虑角色的种族和身份特点\n3. 与当前位置和状态相关\n4. 包含环境描述和互动元素\n\n场景描述应包含：\n- 环境细节\n- 可交互对象\n- 潜在危险或机遇\n- 氛围营造>",
    "[scene_description=\"string\"]",
    "<基于场景描述，生成三个不同的选项。每个选项应该：\n1. 提供不同的行动方向\n2. 与场景元素相关\n3. 可能带来不同的结果\n4. 符合角色特点\n\n每个选项对象必须包含：\n- text：选项文本\n- type：选项类型（探索/战斗/对话/其他）\n- risk_level：风险等级（低/中/高）\n- potential_outcome：可能的结果>",
    "[options=\"array\"]"
  ],
  "output_storage": {
    "scene_description": "current_scene",
    "options": "current_options"
  },
  "prompt_template": "你是一位专业的游戏设计师。请根据以下信息，创建一个引人入胜的游戏场景和相应的选项。\n\n## 背景信息\n{input_info}\n\n## 输出格式\n请严格按照以下JSON格式回复，注意三引号中的内容是指令，你需要根据指令生成内容：\n{format}"
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
    "(纪元名称: {era.name})",
    "(纪元编号: 第{era.era_number}纪元)",
    "(主要特征: {era.key_features_joined})",
    "(主导种族: {era.dominant_races_joined})",
    "(魔法体系: {era.magic_system})",
    "(技术水平: {era.technology_level})",
    "(角色信息: {character_info})",
    "(当前位置: {current_location})",
    "(当前状态: {current_state})",
    "<根据以上信息，生成一个游戏场景...>",
    "[scene_description=\"string\"]",
    "<基于场景描述，生成三个不同的选项...>",
    "[options=\"array\"]"
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
save_data = load_save("test_save")

# 3. 生成新故事
success = manager.generate_story("test_save", "simple_loop")

if success:
    # 4. 获取生成的内容
    scene = get_save_value("current_scene", save_data)
    options = get_save_value("current_options", save_data)
    
    # 5. 显示场景和选项
    print(f"场景描述: {scene}")
    for i, option in enumerate(options, 1):
        print(f"选项{i}: {option['text']}")
        print(f"类型: {option['type']}")
        print(f"风险等级: {option['risk_level']}")
        print(f"可能结果: {option['potential_outcome']}")
        print()
    
    # 6. 更新选择
    selected_option = options[0]
    save_data["selected_option"] = selected_option
    save_data("test_save", save_data)
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

4. 使用JSON编辑器（可选）
```bash
python3 -m editor
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