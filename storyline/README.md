# Storyline模块

这个模块负责管理文字冒险游戏的主线剧情。它提供了一系列工具来创建、编辑和管理故事模板，以及生成基于这些模板的游戏故事情节。

## 目录结构

```
storyline/
├── README.md           # 本文档
├── __init__.py         # 模块初始化文件
├── storyline_manager.py # 故事线管理核心功能
├── templates/          # 存放故事模板的目录
│   ├── base_template.json        # 基础模板
│   ├── adventure_template.json   # 冒险类故事模板
│   └── ...                       # 其他模板
└── tools/              # 工具集
    ├── template_editor.py  # 模板编辑工具
    └── template_builder.py # 模板构建工具
```

## 主要功能

### 1. 模板管理

- 提供标准化的故事模板格式
- 支持创建、读取、更新和删除模板
- 模板分类与组织管理

### 2. 故事生成

- 基于模板生成故事内容
- 与AI模块集成，进行动态内容生成
- 故事分支和选择点管理

### 3. 游戏进程跟踪

- 记录玩家在故事中的位置
- 管理故事状态和进度
- 提供游戏存档和加载功能

## 模板编辑工具

模板编辑工具(template_editor.py)提供了一个便捷的界面来创建和编辑故事模板。主要功能包括：

- 创建新模板
- 编辑现有模板
- 验证模板格式
- 预览模板效果
- 导入/导出模板

## 使用方法

### 基本用法

```python
from storyline.storyline_manager import StorylineManager

# 初始化故事线管理器
manager = StorylineManager()

# 加载模板
template = manager.load_template("adventure_template")

# 生成故事
story = manager.generate_story(template, character_attributes)

# 获取故事内容
print(story.content)

# 获取可能的选择
for choice in story.choices:
    print(choice.text)

# 选择一个分支
next_story = manager.choose_branch(story, choice_index=1)
```

### 使用模板编辑工具

```bash
# 启动模板编辑器
python3 -m storyline.tools.template_editor
```

或在Python代码中：

```python
from storyline.tools.template_editor import TemplateEditor

# 启动编辑器
editor = TemplateEditor()
editor.run()

# 或者直接编辑特定模板
editor.edit_template("adventure_template")
```

## 模板格式

模板采用JSON格式，基本结构如下：

```json
{
  "template_id": "adventure_template",
  "name": "冒险故事模板",
  "description": "适用于野外探险类故事",
  "version": "1.0",
  "author": "游戏设计团队",
  "created_at": "2025-04-08",
  "prompt_segments": [
    "(世界设定: 奇幻世界)",
    "(主角职业: {character.profession})",
    "<描述一段在{location}的冒险经历>",
    "[story=\"*\"]",
    "<提供三个可能的选择>",
    "[choice1=\"*\", choice2=\"*\", choice3=\"*\"]",
    "<描述每个选择可能的结果>",
    "[outcome1=\"*\", outcome2=\"*\", outcome3=\"*\"]"
  ],
  "required_inputs": [
    "character.profession",
    "location"
  ],
  "output_format": {
    "story": "string",
    "choice1": "string",
    "choice2": "string", 
    "choice3": "string",
    "outcome1": "string",
    "outcome2": "string",
    "outcome3": "string"
  },
  "tags": ["冒险", "探索", "奇幻"],
  "next_templates": {
    "choice1": ["combat_template", "puzzle_template"],
    "choice2": ["npc_encounter_template"],
    "choice3": ["rest_template", "travel_template"]
  }
}
``` 