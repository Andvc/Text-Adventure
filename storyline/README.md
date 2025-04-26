# Storyline模块

这个模块负责管理文字冒险游戏的主线剧情。它提供了一系列工具来创建、编辑和管理故事模板，以及生成基于这些模板的游戏故事情节。

## 目录结构

```
storyline/
├── README.md                # 本文档
├── __init__.py              # 模块初始化文件
├── storyline_manager.py     # 故事线管理核心功能
├── templates/               # 存放故事模板的目录
│   ├── simple_loop.json     # 简单循环测试模板
│   ├── adventure_template.json # 冒险类故事模板
│   └── world_setting.json   # 世界背景设定模板
└── tools/                   # 工具集
    ├── template_editor.py   # 图形化模板编辑工具
    └── template_builder.py  # 命令行模板构建工具
```

## 核心概念

在开始之前，让我们了解Storyline模块的几个核心概念：

1. **模板（Template）**：定义了故事的基本结构和输出格式。

2. **提示片段（Prompt Segments）**：构成模板的文本片段，包括背景信息、内容指令和输出格式。

3. **角色属性（Character Attributes）**：由character模块管理的角色数据，可直接在模板中引用。

4. **存储映射（Storage Mapping）**：定义如何将生成的内容存储到角色属性中。

5. **故事记录（Story History）**：生成的故事内容和选择选项的记录。

## 主要功能

### 1. 模板管理

- 提供标准化的故事模板格式
- 支持创建、读取、更新和删除模板
- 模板分类与组织管理

### 2. 故事生成

- 基于模板生成故事内容
- 与AI模块集成，进行动态内容生成
- 直接使用和更新角色属性

### 3. 存储映射

- 自动将生成的内容映射到角色属性
- 通过模板定义输出字段与属性的映射关系
- 直接使用角色模块的API进行属性管理

## 核心API（新版）

### StorylineManager 类

#### 初始化

```python
manager = StorylineManager(templates_dir=None)
```

- `templates_dir`: 模板目录路径（可选），默认使用模块内置templates目录

#### 模板管理

```python
# 列出所有模板
templates = manager.list_templates()

# 加载特定模板
template = manager.load_template("simple_loop")

# 保存模板
manager.save_template(template_data)

# 删除模板
manager.delete_template("old_template")
```

#### 故事生成

```python
# 生成故事（重要更新：现在返回布尔值表示成功与否）
success = manager.generate_story("simple_loop")

# 生成时不应用存储映射
success = manager.generate_story("simple_loop", use_template_storage=False)
```

**重要变更**：`generate_story` 函数现在返回一个布尔值，表示故事生成是否成功，而不是之前的 `(main_content, choices, story_id)` 元组。故事内容和选项会直接保存到角色属性中，可以通过Character模块的API获取。

#### 故事记录管理

```python
# 获取故事记录
story_data = manager.get_story(story_id)

# 清除历史记录
manager.clear_history()

# 保存历史记录到文件
manager.save_history_to_file(filepath)

# 从文件加载历史记录
manager.load_history_from_file(filepath)
```

## 选择处理

**重要变更**：`make_choice` 函数已被移除。现在应该直接使用Character模块的`set_attribute`函数来更新选择：

```python
# 直接更新"事件选择"属性
from character.character_manager import set_attribute
set_attribute("事件选择", choice_text)
```

## 模板格式

模板采用JSON格式，基本结构如下：

```json
{
  "template_id": "simple_loop",
  "name": "简单循环测试模板",
  "description": "单模板循环",
  "version": "1.0",
  "author": "开发者",
  "created_at": "2025-04-11",
  "tags": ["测试"],
  "prompt_segments": [
    "(主角名称：{姓名})",
    "(背景世界:{世界})",
    "<请根据当前事件和事件的选择，生成下一段故事>",
    "[story=\"*\"]",
    "<请生成三个选择>",
    "[choice1=\"*\",choice2=\"*\",choice3=\"*\"]"
  ],
  "output_format": {
    "story": "string",
    "choice1": "string",
    "choice2": "string",
    "choice3": "string"
  },
  "output_storage": {
    "story": "当前事件",
    "choice1": "选项1",
    "choice2": "选项2",
    "choice3": "选项3"
  },
  "prompt_template": "你是一个高级故事生成AI，请根据以下提示创建故事内容。\n\n## 背景信息\n{background}\n\n## 内容要求\n{content}\n\n## 输出格式\n请严格按照以下JSON格式回复：\n{format}"
}
```

### 关键部分解释

1. **prompt_segments**: 提示片段列表，用于构建AI提示词
   - `(...)`: 背景信息，如`(主角名称：{姓名})`
   - `<...>`: 内容指令，如`<请生成故事>`
   - `[key="*"]`: 输出格式声明，如`[story="*"]`

2. **output_format**: 定义期望的输出字段和类型

3. **output_storage**: 定义如何将输出映射到角色属性
   - 键: AI输出中的字段名
   - 值: 角色属性名
   - 特殊字段`content`指完整的故事内容

4. **prompt_template**: 自定义提示词模板（可选）

## 使用模板编辑工具

### 图形界面编辑器

启动方式：

```bash
# 通过模块启动
python -m storyline

# 或直接启动
python -m storyline.tools.template_editor
```

主要功能：
- 创建和编辑模板
- 管理提示片段
- 配置输出格式和存储映射
- 浏览角色属性
- 测试模板和预览JSON结构

### 命令行工具

```bash
# 列出所有模板
python -m storyline.tools.template_builder list

# 显示特定模板
python -m storyline.tools.template_builder show <template_id>

# 创建新模板
python -m storyline.tools.template_builder create

# 删除模板
python -m storyline.tools.template_builder delete <template_id>
```

## 完整使用示例

```python
from storyline.storyline_manager import StorylineManager
from character.character_manager import get_attribute, set_attribute, create_attribute

# 初始化角色属性
create_attribute("姓名", "李逍遥")
create_attribute("世界", "奇幻大陆")
create_attribute("境界", "炼气期")
create_attribute("故事梗概", "少年李逍遥无意间获得一本古老的功法，开始了修仙之路。")
create_attribute("当前事件", "李逍遥来到了一座神秘的洞穴前，传说里面藏有珍贵的宝物。")
create_attribute("事件选择", "探索洞穴")

# 初始化故事线管理器
manager = StorylineManager()

# 生成故事（自动保存到角色属性）
success = manager.generate_story("simple_loop")
if not success:
    print("故事生成失败")

# 从角色属性中获取生成的内容
story = get_attribute("当前事件")
option1 = get_attribute("选项1")
option2 = get_attribute("选项2")
option3 = get_attribute("选项3")

print(f"故事内容: {story}")
print(f"选项1: {option1}")
print(f"选项2: {option2}")
print(f"选项3: {option3}")

# 做出选择（直接更新角色属性）
set_attribute("事件选择", option1)

# 生成下一段故事
success = manager.generate_story("simple_loop")
```

### 调试提示

1. 启用详细日志输出查看内部处理流程
2. 测试时使用`test_adventure_template.py`等示例脚本
3. 检查生成的故事历史记录，了解属性变化情况 